"""
Agent-Assembly-Line
"""
from src.chain import Chain

class AgentManager:
    def __init__(self):
        self.current_agent = Chain("chat-demo")

    def select_agent(self, agent_name, debug=False):
        if self.current_agent is None or self.current_agent.agent_name != agent_name:
            if self.current_agent:
                self.current_agent.cleanup()
            self.current_agent = Chain(agent_name, debug)

    def get_agent(self):
        if self.current_agent is None:
            raise ValueError("No agent selected")
        return self.current_agent

    def cleanup(self):
        if self.current_agent:
            self.current_agent.cleanup()
            self.current_agent = None