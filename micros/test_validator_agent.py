"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class TestValidatorAgent(Agent):
    """
    A small agent that validates strings in tests.
    """

    def __init__(self, mode='local'):
        self.config = Config()

        inline_rag_template = """
        Please tell if the assumption is true about the text.

        ## Context:
        - Today's date: {today}

        ## Instructions
        - answer only with `True` or `False`

        ## Assumption:
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

    def run(self, prompt="Is it true or false?"):
        return super().run(prompt)
