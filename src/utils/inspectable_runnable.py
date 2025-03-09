"""
Agent-Assembly-Line
"""

from langchain_core.runnables import RunnablePassthrough

from typing import Optional
class InspectableRunnable(RunnablePassthrough):
    debug: Optional[bool] = False
    def __init__(self, next_runnable=None, debug=False):
        super().__init__(next_runnable)
        self.debug = debug
    
    def invoke(self, inputs, config = None, **kwargs):
        if self.debug:
            print(f"Prompt size: {len(inputs.to_string())} characters")
        return inputs

