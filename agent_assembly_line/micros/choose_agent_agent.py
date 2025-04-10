"""
Agent-Assembly-Line
"""

import os
from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class ChooseAgentAgent(Agent):
    """
    A small agent specialized in choosing the right agent for the next action.
    """

    purpose = "Chooses the most suitable agent for a given task based on user intent."

    _cached_agents = {}  # Class-level cache for loaded agents

    def __init__(self, text, mode='local'):
        self.config = Config()

        all_agents = self.get_all_agents()

        inline_rag_template = """
        You are a helpful AI assistant specialized in choosing the right agent for the next action.

        ## Context:
        - Today's date: {today}

        ## Instructions:
        - if there is no good match, say "None"
        - summarize your anser to one single word (the agent name)
        - Match the intent to the most suitable agent based on their purpose.
        - If no agent matches the intent, respond with "None".
        - Always respond with a single word: the agent name or "None".
        - Do not select agents that are irrelevant to the user's request.

        ## Question:
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
            "name": "agent-router",
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
        result = super().run(prompt)
        if result:
            result_agent = result.strip().replace("*", "").replace("`", "").replace("`", "").replace("**", "")
            if self.config.debug:
                print(f"[router] proposed agent: {result_agent}")
            return result_agent
        return ""

    def get_all_agents(self):
        """Looks in micros/ for micro agents and retrieves their purposes."""
        folder_path = "agent_assembly_line/micros/"
        agents = ""
        try:
            for filename in os.listdir(folder_path):
                if filename == "__init__.py" or not filename.endswith(".py"):
                    continue
                filepath = os.path.join(folder_path, filename)
                if os.path.isfile(filepath):
                    module_name = filename.replace(".py", "")
                    class_name = self._to_camel_case(module_name)

                    module = __import__(f"agent_assembly_line.micros.{module_name}", fromlist=[module_name])
                    agent_class = getattr(module, class_name, None)

                    if agent_class and hasattr(agent_class, "purpose"):
                        self._cached_agents[class_name] = agent_class
                        agents += f"- {module_name} with the following purpose: \"{agent_class.purpose}\", \n"
                    else:
                        agents += f"- {module_name}, \n"
            return agents
        except FileNotFoundError:
            raise RuntimeError(f"The folder '{folder_path}' does not exist.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while retrieving agents: {e}")

    def _to_camel_case(self, text):
        """
        Converts a string to camel case.
        """
        return ''.join(word.capitalize() for word in text.split('_'))

    def _to_snake_case(self, text):
        """
        Converts a string to snake case.
        """
        return '_'.join(word.lower() for word in text.split())

    def get_agent(self, agent_name):
        """
        Retrieves an agent class by its name from the cached agents.
        """
        agent_name = self._to_camel_case(agent_name)
        if agent_name in self._cached_agents:
            return self._cached_agents[agent_name]
        return None