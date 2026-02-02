"""
Agent-Assembly-Line
"""

from langchain_core.runnables import RunnablePassthrough

from typing import Optional, Iterator, AsyncIterator, Any, Callable

class InspectableRunnable(RunnablePassthrough):
    statsCallback: Optional[Callable] = None

    def __init__(self, next_runnable=None, statsCallback=None):
        super().__init__(next_runnable)
        self.statsCallback = statsCallback if statsCallback else lambda: None

    def invoke(self, inputs, config=None, **kwargs):
        prompt_str = str(inputs)
        self.statsCallback({ "prompt_size": len(prompt_str), "prompt_content": prompt_str })
        return super().invoke(inputs, config, **kwargs)

    async def ainvoke(self, inputs, config=None, **kwargs):
        prompt_str = str(inputs)
        self.statsCallback({ "prompt_size": len(prompt_str), "prompt_content": prompt_str })
        return await super().ainvoke(inputs, config, **kwargs)

    def transform(self, input: Iterator[Any], config: Optional[Any] = None, **kwargs: Any) -> Iterator[Any]:
        for result in super().transform(input, config, **kwargs):
            result_str = result.to_string()
            self.statsCallback({ "prompt_size": len(result_str), "prompt_content": result_str })
            yield result

    async def atransform(self, input: AsyncIterator[Any], config: Optional[Any] = None, **kwargs: Any) -> AsyncIterator[Any]:
        async for result in super().atransform(input, config, **kwargs):
            result_str = result.to_string()
            self.statsCallback({ "prompt_size": len(result_str), "prompt_content": result_str })
            yield result
