"""
Agent-Assembly-Line
"""

import os
from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class ChooseAgentAgent(Agent):
    """
    A small agent specialized in choosing the right agent for the next action. Chose between local and cloud mode.
    """

    def __init__(self, text, mode='local'):
        self.config = Config()

        all_agents = self.get_all_agents()

        inline_rag_template = """
        You are a helpful AI assistant specialized in choosing the right agent for the next action.

        ## Context:
        - Today's date: {today}

        ## Instructions:
        - if there is no good match, say "None"
        - try to summarize your anser to one single word (the agent name)

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
            "name": "clarity-agent-demo",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier,
                "embeddings": embeddings
            },
        })
        super().__init__(config=self.config)
        self.add_inline_text("Intent: " + text)
        self.add_inline_text("Available agents:" + all_agents + "\n")

    def run(self, prompt="The following text tells what the user is intending to do, and a list of available agents. Please choose the matching agent for the intent."):
        return super().run(prompt)

    def get_all_agents(self):
        """Looks in micros/ for micro agents."""
        folder_path = "micros/"
        agents = ""
        try:
            for filename in os.listdir(folder_path):
                if filename == "__init__.py":
                    continue
                filepath = os.path.join(folder_path, filename)
                if os.path.isfile(filepath):
                    agents += filename.replace(".py", "") + ", "
            agents += " command-line-runner, API-executor, Python-runner, search-executor"
            return agents
        except FileNotFoundError:
            raise RuntimeError(f"The folder '{folder_path}' does not exist.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while retrieving agents: {e}")