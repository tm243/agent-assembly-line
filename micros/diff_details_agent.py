"""
Agent-Assembly-Line
"""

from src.agent import Agent
from src.config import Config

class DiffDetailsAgent(Agent):
    """
    An agent specialized in providing a textual representation of code changes in text format.
    """

    def __init__(self, diff_text):
        self.config = Config()

        inline_rag_template = """
        You are a helpful AI assistant specialized in summarizing code changes and generating commit messages. 
        Your task is to analyze the provided Git diff.

        ## Context:
        - Today's date: {today}

        ## Instructions:
        If something has been removed, and also added, means it has been changed.

        ## Git Diff:
        {context}

        Now perform:
        {question}

        ### Summary:
        """

        self.config.load_conf_dict({
            "name": "diff-demo",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": "openai:gpt-4o",
                "embeddings": "text-embedding-ada-002"
            },
        })
        super().__init__(config=self.config)
        super().add_diff(diff_text)

    def run(self, prompt="What has been changed in the code? Create a comprehensive, textual summary of the changes. The context is only for the bigger picture."):
        return super().run(prompt)
