"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config
from distutils.util import strtobool

class YesNoAgent(Agent):
    """
    A small agent specialized in reducing a statement to Yes or No. Chose between local and cloud mode.
    """

    def __init__(self, text, mode='local'):
        self.config = Config()

        inline_rag_template = """
        You are a helpful AI assistant specialized in telling if a text is yes or no.

        ## Instructions

        ## Context:
        - Today's date: {today}

        {question}

        ## Text:
        {context}
        """

        if mode not in ['local', 'cloud']:
            raise ValueError("Invalid mode. Valid options are 'local' or 'cloud'.")

        if mode == 'local':
            model_identifier = "ollama:gemma2:latest"
            embeddings = "nomic-embed-text"
        elif mode == 'cloud':
            model_identifier = "openai:gpt-4o"
            embeddings = "text-embedding-ada-002"

        self.config.load_conf_dict({
            "name": "yes-no-agent-demo",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier,
                "embeddings": embeddings
            },
        })
        super().__init__(config=self.config)
        self.add_inline_text(text)

    def run(self, prompt="Please summarize the Text to a simple 'Yes' or 'No'"):
        return super().run(prompt).replace(".", "").strip()

    @classmethod
    def toBool(cls, value):
        try:
            return bool(strtobool(value))
        except Exception as e:
            print(f"Error converting {value} to boolean: {e}")
        return None

