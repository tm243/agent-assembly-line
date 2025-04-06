"""
Agent-Assembly-Line
"""

from agent_assembly_line.micros.choose_agent_agent import ChooseAgentAgent

def _get_agent_or_fallback(self, prompt, white_list):
    """
    Core logic to get the agent or fallback to the original method.
    """
    if hasattr(self, "use_agent_router") and self.use_agent_router:
        choose_agent = ChooseAgentAgent(prompt)
        selected_agent = choose_agent.run()

        if selected_agent not in white_list:
            return None

        agent_class = choose_agent.get_agent(selected_agent)
        return agent_class(prompt)

    return None


def agent_router(allowed_agents=None):
    """
    Higher-order decorator to add agent_routing logic to the Agent class.
    Allows passing a custom allowed_agents list.

    Note:
    Nested decorator to work around the issue of positional cls argument
    """
    allowed_agents = allowed_agents or []

    def decorator(cls):
        original_run = cls.run
        original_arun = getattr(cls, "arun", None)
        original_stream = getattr(cls, "stream", None)

        def run_with_agent_router(self, prompt):
            agent = _get_agent_or_fallback(self, prompt, allowed_agents)
            if agent:
                return agent.run()
            return original_run(self, prompt)

        async def arun_with_agent_router(self, prompt):
            agent = _get_agent_or_fallback(self, prompt, allowed_agents)
            if agent:
                return await agent.arun()
            if original_arun:
                return await original_arun(self, prompt)
            raise NotImplementedError("arun method is not implemented.")

        async def stream_with_agent_router(self, prompt):
            agent = _get_agent_or_fallback(self, prompt, allowed_agents)
            if agent:
                # no stream() in agents
                yield agent.run()
            elif original_stream:
                async for item in original_stream(self, prompt):
                    yield item
            else:
                raise NotImplementedError("stream method is not implemented.")

        cls.run = run_with_agent_router
        if original_arun:
            cls.arun = arun_with_agent_router
        if original_stream:
            cls.stream = stream_with_agent_router

        return cls

    return decorator