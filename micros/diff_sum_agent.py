"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class DiffSumAgent(Agent):
    """
    A small agent specialized in summarizing code changes and generating commit messages.
    """

    def __init__(self, text):
        """
        Initializes the DiffSumAgent with the given text.

        Args:
            text (str): The Git diff text to analyze.
        """
        self.config = Config()

        inline_rag_template = """
        You are a helpful AI assistant specialized in summarizing code changes and generating commit messages.

        ## Context:
        - Today's date: {today}

        ## Instructions:
        - error handling, imports, outputs etc are only mentioned if nothing else has changed in the code

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
        self.add_inline_text(text)

    def run(self, prompt="Shorten the summary. Prioritize refactoring over cleanup. If something got moved, tell which class or code is affected. Ignore imports, requirements or includes as well as print or log outputs and alike. Emphazise API changes."):
        return super().run(prompt)
