"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class OneTenAgent(Agent):
    """
    An agent specialized in giving an estimate from 1-10.
    """

    purpose = "Rates a statement on a scale from 1 to 10."

    def __init__(self, text, mode='local'):
        self.config = Config()

        inline_rag_template = """
        You are a helpful AI assistant specialized in rating a text from 1 to 10 (one to ten).

        ## Instructions
        - Reply with a simple single digit '1' or '2' or '3' or '4' or '5' or '6' or '7' or '8' or '9' or '10'
        - based on the question, rate the Text on a scale with either '1' or '2' or '3' or '4' or '5' or '6' or '7' or '8' or '9' or '10'

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
        elif mode == 'cloud':
            model_identifier = "openai:gpt-4o"

        self.config.load_conf_dict({
            "name": "one-ten-agent",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier
            },
        })
        super().__init__(config=self.config)
        self.add_inline_text(text)

    def run(self, prompt="Please rate the Text on a scale with either '1' or '2' or '3' or '4' or '5' or '6' or '7' or '8' or '9' or '10'"):
        result = super().run(prompt).replace(".", "").strip()
        valid_responses = {str(i) for i in range(1, 11)}
        if result.lower() in valid_responses:
            return result
        else:
            result = super().run(prompt).replace(".", "").strip()
            if result.lower() in valid_responses:
                return result

    @classmethod
    def toInt(cls, value):
        try:
            return int(value)
        except Exception as e:
            return None

