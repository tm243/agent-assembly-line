"""
Agent-Assembly-Line
"""

from agent_assembly_line.micros.choose_agent_agent import ChooseAgentAgent

from agent_assembly_line.agent import Agent

def _get_agent_or_fallback(self, prompt, white_list):
    """
    Core logic to get the agent or fallback to the original method.
    """
    if hasattr(self, "use_agent_router") and self.use_agent_router:
        if not self._router:
            self._router = ChooseAgentAgent(prompt)
        selected_agent = self._router.run()

        if selected_agent not in white_list:
            return None

        agent_class = self._router.get_agent(selected_agent)
        print("[agent router] selected agent:", selected_agent)
        agent = agent_class(prompt)
        self._allocated_agents.append(agent)
        return agent

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
        original_cleanup = getattr(cls, "cleanup", None)
        original_close_models = getattr(cls, "closeModels", None)
        original_aclose_models = getattr(cls, "aCloseModels", None)

        def run_with_agent_router(self, prompt, *args, **kwargs):
            agent = _get_agent_or_fallback(self, prompt, allowed_agents)
            if agent:
                agent_result = agent.run()
                self.add_inline_text(agent_result)
            return original_run(self, prompt, *args, **kwargs)

        async def arun_with_agent_router(self, prompt, *args, **kwargs):
            agent = _get_agent_or_fallback(self, prompt, allowed_agents)
            if agent:
                agent_result = agent.run()
                self.add_inline_text(agent_result)
            if original_arun:
                return await original_arun(self, prompt, *args, **kwargs)
            else:
                raise NotImplementedError("arun method is not implemented.")

        async def stream_with_agent_router(self, prompt, *args, **kwargs):
            agent = _get_agent_or_fallback(self, prompt, allowed_agents)
            if agent:
                agent_result = agent.run()
                self.add_inline_text(agent_result)
            if original_stream:
                async for item in original_stream(self, prompt, *args, **kwargs):
                    yield item
            else:
                raise NotImplementedError("stream method is not implemented.")

        def cleanup_with_router(self, *args, **kwargs):
            if original_cleanup:
                original_cleanup(self, *args, **kwargs)

            if hasattr(self, "_router") and self._router:
                self._router.cleanup()

            for agent in self._allocated_agents:
                agent.cleanup()

        def close_models_with_router(self, *args, **kwargs):
            if original_close_models:
                original_close_models(self, *args, **kwargs)

            if hasattr(self, "_router") and self._router:
                self._router.closeModels()

            for agent in self._allocated_agents:
                agent.closeModels()

        async def aclose_models_with_router(self, *args, **kwargs):
            if original_aclose_models:
                await original_aclose_models(self, *args, **kwargs)

            if hasattr(self, "_router") and self._router:
                await self._router.aCloseModels()

            for agent in self._allocated_agents:
                await agent.aCloseModels()

        cls.run = run_with_agent_router
        if original_arun:
            cls.arun = arun_with_agent_router
        if original_stream:
            cls.stream = stream_with_agent_router
        if original_cleanup:
            cls.cleanup = cleanup_with_router
        if original_close_models:
            cls.closeModels = close_models_with_router
        if original_aclose_models:
            cls.aCloseModels = aclose_models_with_router

        return cls

    return decorator