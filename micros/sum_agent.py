"""
Agent-Assembly-Line
"""

from src.agent import Agent
from src.config import Config

class SumAgent(Agent):
    """
    A small agent specialized in summarizing text. Chose between local and cloud mode.
    """

    def __init__(self, text, mode='local'):
        """
        Initializes the SumAgent with the given text and mode.

        Args:
            text (str): The text to summarize.
            mode (str): The mode to use ('local' or 'cloud'). Defaults to 'local'.
        """
        self.config = Config()

        inline_rag_template = """
        You are a helpful AI assistant specialized in summarizing text.

        ## Context:
        - Today's date: {today}

        {question}

        ## Text:
        {context}
        """

        if mode == 'local':
            model_identifier = "ollama:gemma2:latest"
            embeddings = "nomic-embed-text"
        elif mode == 'cloud':
            model_identifier = "openai:gpt-4o"
            embeddings = "text-embedding-ada-002"
        else:
            raise ValueError("Invalid mode. Choose either 'local' or 'cloud'.")

        self.config.load_conf_dict({
            "name": "diff-demo",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier,
                "embeddings": embeddings
            },
        })
        super().__init__(config=self.config)
        self.add_inline_text(text)

    def run(self, prompt="Summarize the following text in 2-3 sentences, capturing the main idea and key details."):
        return super().run(prompt)
