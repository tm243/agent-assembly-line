"""
Agent Assembly Line
"""

from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationSummaryMemory

class MemoryStrategy():

    NO_MEMORY = 0
    SUMMARY   = 1
    HISTORY   = 2

    buffer_memory = ConversationBufferMemory()
    model = None
    config = None
    summary = None

class MemoryAssistant():

    strategy = MemoryStrategy.NO_MEMORY

    def __init__(self, strategy=MemoryStrategy.NO_MEMORY, model=None, config=None):
        self.config = config
        self.model = model
        self.strategy = strategy
        self.buffer_memory = ConversationBufferMemory()

    def add_message(self, prompt, answer):
        self.buffer_memory.save_context({"question": prompt}, {"answer": answer})

        if self.strategy == MemoryStrategy.SUMMARY:
            history = self.buffer_memory.load_memory_variables({})
            self.summary_memory = self.model.invoke(self.config.memory_prompt + history["history"])
