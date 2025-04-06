"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.decorators.agent_decorators import agent_router

@agent_router(allowed_agents=["fmi_weather_agent", "website_summary_agent", "diff_details_agent", "diff_sum_agent"])
class ChatAgent(Agent):
    def __init__(self, agent_name = None, debug = False, config = None):
        super().__init__(agent_name, debug, config)
        self.use_agent_router = True