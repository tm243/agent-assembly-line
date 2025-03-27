"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class IntentAgent(Agent):
    """
    A small agent specialized in detecting intention. Chose between local and cloud mode.
    """

    def __init__(self, text, mode='local'):
        self.config = Config()

        inline_rag_template = """
        You are a helpful AI assistant specialized in detecting intention in a text.

        ## Instructions
        - Please describe the user's desired outcome or action. Text

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
            "name": "yes-no-agent-demo",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier,
                "embeddings": embeddings
            },
        })
        super().__init__(config=self.config)
        self.add_inline_text(text)

    def run(self, prompt="What is the main goal or intention expressed in this text?"):
        return super().run(prompt)

    def get_all_agents(self):
        """
        Retrieves a list of all available agents by scanning the 'micros/' folder.

        Returns:
            str: A comma-separated list of agent names.
        """

