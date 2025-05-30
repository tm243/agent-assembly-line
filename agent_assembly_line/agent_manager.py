"""
Agent-Assembly-Line
"""

from agent_assembly_line import ChatAgent

class AgentManager:
    """
    Does not take ownership of the agent, just manages the selection of the agent.
    """
    def __init__(self):
        self.current_agent = None

    def select_agent(self, agent_name, debug=False):
        if self.current_agent is None or self.current_agent.name != agent_name:
            self.current_agent = ChatAgent(agent_name, debug)
        return self.current_agent

    def get_agent(self):
        if self.current_agent is None:
            raise ValueError("No agent selected")
        return self.current_agent

    def cleanup(self):
        self.current_agent = None