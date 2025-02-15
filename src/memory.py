"""
Agent Assembly Line
"""

from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationSummaryMemory

class MemoryStrategy():

    NO_MEMORY = 0
    SUMMARY   = 1
    HISTORY   = 2

class MemoryAssistant():

    strategy = MemoryStrategy.NO_MEMORY

    def __init__(self, strategy=MemoryStrategy.NO_MEMORY):
        self.strategy = stragety

