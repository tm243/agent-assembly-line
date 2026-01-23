"""
Agent-Assembly-Line
"""

import os
from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class TextCleanupAgent(Agent):
    """
    A specialized agent for cleaning up text files with bad umlauts, encoding issues, 
    and other symbols. Processes large files by chunking them automatically.
    """

    purpose = (
        "This agent specializes in cleaning up text files with encoding issues, "
        "bad umlauts, corrupted characters, and other symbol problems. "
        "It should be used when the user needs to fix character encoding issues, "
        "clean up corrupted text, or normalize text with symbol problems."
    )

    def __init__(self, input_file_path, output_file_path=None, mode='local', verbose=True, **kwargs):
        """
        Initializes the TextCleanupAgent with the given file paths and mode.

        Args:
            input_file_path (str): Path to the input text file to clean up.
            output_file_path (str): Path where cleaned text should be saved. If None, 
                                   will create a copy with '_cleaned' suffix.
            mode (str): The mode to use ('local' or 'cloud'). Defaults to 'local'.
            verbose (bool): Whether to print progress messages. Defaults to True.
        """
        self.input_file_path = input_file_path
        self.verbose = verbose

        if output_file_path is None:
            base, ext = os.path.splitext(input_file_path)
            self.output_file_path = f"{base}_cleaned{ext}"
        else:
            self.output_file_path = output_file_path

        cleanup_template = """
You are a text cleanup specialist. Your task is to fix character encoding issues, 
corrupted umlauts, and other symbol problems in the provided text.

## Context:
- Today's date: {today}
- This is part of a larger document that is being processed in chunks
- Maintain the original meaning and structure of the text
- Fix encoding issues while preserving the natural flow

## Common Issues to Fix:
- Bad umlauts: ä→ä, ö→ö, ü→ü, Ä→Ä, Ö→Ö, Ü→Ü
- Corrupted quotes: â€œ→", â€→", â€™→'
- Strange symbols: â€¢→•, â€"→—, â€"→–
- Other encoding artifacts and corrupted characters

## Instructions:
1. Clean up all character encoding issues
2. Fix bad umlauts and special characters
3. Normalize quotes and punctuation
4. Preserve paragraph breaks and structure
5. Do NOT add explanations or comments
6. Return ONLY the cleaned text

## Text to Clean:
{context}

## Cleaned Text:
{question}
"""

        if mode == 'local':
            model_identifier = "ollama:gemma2:latest"
        elif mode == 'cloud':
            model_identifier = "openai:gpt-4o"
        else:
            raise ValueError("Invalid mode. Choose either 'local' or 'cloud'.")

        config = Config()
        config.load_conf_dict({
            "name": kwargs.get("name", "text-cleanup-agent"),
            "description": kwargs.get("description", "Agent for cleaning up text files with encoding issues"),
            "prompt": { "inline_rag_templates": cleanup_template },
            "llm": {
                "model-identifier": model_identifier
            },
        })
        super().__init__(config=config)

    def _log(self, message):
        """Internal logging method that respects the verbose setting."""
        if self.verbose:
            print(message)

    def chunk_text(self, text, chunk_size=1000, overlap=100):
        """
        Chunks the text into smaller pieces for processing.

        Args:
            text (str): The text to chunk
            chunk_size (int): Size of each chunk in characters
            overlap (int): Number of characters to overlap between chunks
        
        Returns:
            list: List of text chunks
        """
        chunks = []
        start = 0

        if not text:
            return [""]

        if len(text) <= chunk_size:
            return [text.strip()]

        actual_overlap = min(overlap, chunk_size - 1)

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at a sentence or paragraph boundary if possible
            if end < len(text):
                # Look for a good breaking point (sentence end)
                for break_char in ['\n\n', '. ', '! ', '? ']:
                    last_break = chunk.rfind(break_char)
                    if last_break > chunk_size * 0.7:  # Don't break too early
                        chunk = chunk[:last_break + len(break_char)]
                        end = start + last_break + len(break_char)
                        break
            
            chunks.append(chunk.strip())

            if end >= len(text):
                break

            next_start = end - actual_overlap

            if next_start <= start and len(chunks) > 0:
                next_start = start + 1

            start = next_start

            # Safety check to prevent infinite loops
            if len(chunks) > len(text):
                break

        return chunks

    def process_file(self):
        """
        Processes the input file by loading it, cleaning each chunk, 
        and saving the results to the output file.
        """
        self._log(f"Loading file: {self.input_file_path}")

        try:
            with open(self.input_file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except UnicodeDecodeError:
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(self.input_file_path, 'r', encoding=encoding) as f:
                        text_content = f.read()
                    self._log(f"Successfully read file using {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"Could not read file {self.input_file_path} with any supported encoding")

        self._log(f"File loaded. Total size: {len(text_content)} characters")

        chunks = self.chunk_text(text_content)
        self._log(f"Created {len(chunks)} chunks for processing")

        cleaned_chunks = []
        for i, chunk in enumerate(chunks):
            self._log(f"Processing chunk {i+1}/{len(chunks)}")

            self.replace_inline_text(chunk)
            cleaned_text = self.run("Clean up this text, fixing all encoding issues and corrupted characters.")
            cleaned_chunks.append(cleaned_text)

        full_cleaned_text = "\n".join(cleaned_chunks)

        self._log(f"Saving cleaned text to: {self.output_file_path}")
        with open(self.output_file_path, 'w', encoding='utf-8') as f:
            f.write(full_cleaned_text)

        self._log(f"Cleanup complete! Cleaned file saved as: {self.output_file_path}")
        return self.output_file_path

    def run(self, prompt="Clean up this text."):
        """
        Runs the cleanup agent with the given prompt.
        """
        return super().run(prompt)