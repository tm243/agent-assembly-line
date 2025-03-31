"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class TestValidatorAgent(Agent):
    """
    A small agent that validates strings in tests.
    """

    def __init__(self, mode='local', llm="ollama:gemma3:4b", embeddings="nomic-embed-text"):
        self.config = Config()

        inline_rag_template = """
        Please tell if the assumption is true about the text.

        ## Instructions
        - Consider whether the provided statement conveys the same meaning as "\n{context}\n".
        - If the meaning is the same, answer `True`. Otherwise, answer `False`.

        ## Statement:
        {question}
        """

        if mode == 'local':
            model_identifier = llm
            embeddings = embeddings
        elif mode == 'cloud':
            model_identifier = "openai:gpt-4o"
            embeddings = "text-embedding-ada-002"
        else:
            raise ValueError("Invalid mode. Choose either 'local' or 'cloud'.")

        self.config.load_conf_dict({
            "name": "test-validator-agent",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier,
                "embeddings": embeddings
            },
        })
        super().__init__(config=self.config)

    def run(self, prompt="Is it true or false?"):
        return super().run(prompt)
