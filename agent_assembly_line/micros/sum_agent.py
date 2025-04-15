"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class SumAgent(Agent):
    """
    A small agent specialized in summarizing text. Chose between local and cloud mode.
    """

    purpose = (
        "This agent specializes in summarizing text into concise summaries. "
        "It should only be chosen when the user explicitly requests a summary, "
        "a short answer, or a concise explanation. Do not use this agent for "
        "general questions, detailed answers, or unrelated tasks."
        "Do not use it when the user wants a long answer, a detailed answer, or a long explanation."
    )

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
        elif mode == 'cloud':
            model_identifier = "openai:gpt-4o"
        else:
            raise ValueError("Invalid mode. Choose either 'local' or 'cloud'.")

        self.config.load_conf_dict({
            "name": "sum-agent",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier
            },
        })
        super().__init__(config=self.config)
        self.add_inline_text(text)

    def run(self, prompt="Summarize the following text in 2-3 sentences, capturing the main idea and key details."):
        return super().run(prompt)
