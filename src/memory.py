"""
Agent Assembly Line
"""

# @todo migrate to trim_messages()
# https://python.langchain.com/docs/versions/migrating_memory/conversation_buffer_window_memory/

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")
with warnings.catch_warnings():
    from langchain.memory import ConversationSummaryMemory
    from langchain.memory import ConversationBufferMemory

import asyncio

class MemoryStrategy():

    NO_MEMORY = 0
    SUMMARY   = 1
    HISTORY   = 2

    model = None
    config = None
    summary = None

class MemoryAssistant():

    strategy = MemoryStrategy.NO_MEMORY
    summary_memory = ""
    buffer_memory = ConversationBufferMemory()

    def __init__(self, strategy=MemoryStrategy.NO_MEMORY, model=None, config=None):
        self.config = config
        self.model = model
        self.strategy = strategy

    async def add_message(self, prompt, answer):
        self.buffer_memory.save_context({"question": prompt}, {"answer": answer})

        if self.strategy == MemoryStrategy.SUMMARY:
            history = self.buffer_memory.load_memory_variables({})
            self.summary_memory = await asyncio.to_thread(self.model.invoke, self.config.memory_prompt + history["history"])
            print("MemoryAssistant: Summary memory done")
