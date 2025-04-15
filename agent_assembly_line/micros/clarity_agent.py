"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class ClarityAgent(Agent):
    """
    A small agent specialized in telling if a text is clear. Chose between local and cloud mode.
    """

    purpose = "Tells if a text is clear, readable, and understandable."

    def __init__(self, text, mode='local'):
        self.config = Config()

        inline_rag_template = """
        You are a helpful AI assistant specialized in analyzing text.

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
            "name": "clarity-agent",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier
            },
        })
        super().__init__(config=self.config)
        self.add_inline_text(text)

    def run(self, prompt="Is the text clear, readble and understandable?"):
        return super().run(prompt)
