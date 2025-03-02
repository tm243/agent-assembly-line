"""
Agent Assembly Line
"""

import asyncio
import json

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
)

class MemoryStrategy():

    NO_MEMORY = 0
    SUMMARY   = 1
    HISTORY   = 2

    model = None
    config = None
    summary = None

    messages = []

class MemoryAssistant():

    strategy = MemoryStrategy.NO_MEMORY
    summary_memory = ""
    max_messages = 50

    def __init__(self, strategy=MemoryStrategy.NO_MEMORY, model=None, config=None):
        self.config = config
        self.model = model
        self.strategy = strategy
        self.messages = []

    async def add_message(self, prompt, answer):
        self.messages.append(HumanMessage(content=prompt))
        self.messages.append(AIMessage(content=answer))
        self.trim_messages_buffer()

        if self.strategy == MemoryStrategy.SUMMARY:
            history = "\n".join([message.content for message in self.messages])
            self.summary_memory = await asyncio.to_thread(self.model.invoke, self.config.memory_prompt + history)
            if self.config.debug:
                print("MemoryAssistant: Summary memory done")

    def trim_messages_buffer(self):
        self.messages = trim_messages(
            self.messages,
            token_counter=len,
            max_tokens=self.max_messages,
            strategy="last",
            start_on="human",
            include_system=True,
            allow_partial=False,
        )

    def save_messages(self, file_path):
        with open(file_path, 'w') as file:
            json.dump([message.__dict__ for message in self.messages], file)

    def load_messages(self, file_path):
        with open(file_path, 'r') as file:
            messages_data = json.load(file)
            self.messages = [self._message_from_dict(data) for data in messages_data]

    def _message_from_dict(self, data):
        if not data or 'type' not in data or 'content' not in data:
            return None
        if data['content'] is None:
            return None
        if data['type'] == 'human':
            return HumanMessage(content=data['content'])
        elif data['type'] == 'ai':
            return AIMessage(content=data['content'])
        elif data['type'] == 'system':
            return SystemMessage(content=data['content'])
        else:
            return BaseMessage(type='base', content=data['content'])
