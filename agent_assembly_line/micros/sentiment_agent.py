"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config
from distutils.util import strtobool

class SentimentAgent(Agent):
    """
    A small agent specialized in detecting sentiment. Chose between local and cloud mode.
    """

    purpose = "Detects the sentiment of a given text."

    def __init__(self, text, mode='local'):
        """
        Initializes the SentimentAgent with the given text and mode.

        Args:
            text (str): The text to analyze for sentiment.
            mode (str): The mode to use ('local' or 'cloud'). Defaults to 'local'.
        """
        self.config = Config()

        inline_rag_template = """
        You are a helpful AI assistant specialized in detecting sentiment in a text.

        ## Instructions
        - What is the dominant emotional tone conveyed in this text?
        - Be specific about whether it leans towards joy, sadness, anger, fear, or something else.

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
            "name": "sentiment-agent",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier
            },
        })
        super().__init__(config=self.config)
        self.add_inline_text(text)

    def run(self, prompt="Analyze the following text and determine its overall sentiment"):
        return super().run(prompt)

