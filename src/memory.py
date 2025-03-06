"""
Agent Assembly Line
"""

import asyncio
import json
import time
import threading
import os
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
)

class MemoryStrategy():
    NO_MEMORY = 0
    SUMMARY = 1
    HISTORY = 2

class MemoryAssistant():
    strategy = MemoryStrategy.NO_MEMORY
    summary_memory = ""
    max_messages_in_buffer = 10 # affects response time of LLM
    auto_save_interval_sec = 30
    auto_save_message_count = 10  # Auto-save every 10 messages

    def __init__(self, strategy=MemoryStrategy.NO_MEMORY, model=None, config=None):
        self.config = config
        self.model = model
        self.strategy = strategy
        self.messages = []
        self.auto_save_path = config.memory_path
        self.message_count_since_last_save = 0

        self.stop_event = threading.Event()
        self.auto_save_task = threading.Thread(target=self._auto_save_periodically)
        self.auto_save_task.daemon = True
        self.auto_save_task.start()

    def add_message(self, prompt, answer):
        timestamp = time.time()
        self.messages.append(HumanMessage(content=prompt, id=f"human-{timestamp}"))
        self.messages.append(AIMessage(content=answer, id=f"ai-{timestamp}"))
        self.trim_messages_buffer()
        self.message_count_since_last_save += 1

        if self.message_count_since_last_save >= self.auto_save_message_count:
            self.save_messages(self.auto_save_path)
            self.message_count_since_last_save = 0

        if self.strategy == MemoryStrategy.SUMMARY:
            history = "\n".join([message.content for message in self.messages])
            asyncio.create_task(self._invoke_model(history))
            if self.config.debug:
                print("MemoryAssistant: Summary memory task created")

    async def _invoke_model(self, history):
        self.summary_memory = await self.model.ainvoke(self.config.memory_prompt + history)
        if self.config.debug:
            print("MemoryAssistant: Summary memory done")

    def trim_messages_buffer(self):
        self.messages = trim_messages(
            self.messages,
            token_counter=len,
            max_tokens=self.max_messages_in_buffer,
            strategy="last",
            start_on="human",
            include_system=True,
            allow_partial=False,
        )

    def save_messages(self, file_path):
        try:
            if file_path:
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    with open(file_path, 'r') as file:
                        existing_messages = json.load(file)
                else:
                    existing_messages = []

                # Convert existing messages to a set of IDs for quick lookup
                existing_message_ids = {msg['id'] for msg in existing_messages}

                # Append new messages to the existing messages, avoiding duplicates
                new_messages = [message.__dict__ for message in self.messages if message.__dict__['id'] not in existing_message_ids]

                all_messages = existing_messages + new_messages

                with open(file_path, 'w') as file:
                    json.dump(all_messages, file)
                if self.config.debug:
                    print(f"{len(all_messages)} messages saved to {file_path}")
        except Exception as e:
            print("Error saving messages: ", e)

    def load_messages(self, file_path):
        try:
            if os.path.exists(file_path):
                if self.config.debug:
                    print("Loading messages from", file_path, os.path.getsize(file_path))
                if os.path.getsize(file_path) < 2:
                    if self.config.debug:
                        print("File is empty, no messages to load.")
                    return
                with open(file_path, 'r') as file:
                    messages_data = json.load(file)
                    self.messages = [self._message_from_dict(data) for data in messages_data]
                if self.config.debug:
                    print(f"Messages loaded from {file_path}")
        except Exception as e:
            print("Error loading messages: ", e, file_path)

    def _message_from_dict(self, data):
        if not data or 'type' not in data or 'content' not in data:
            return None
        if data['content'] is None:
            return None
        if data['type'] == 'human':
            return HumanMessage(content=data['content'], id=data.get('id'))
        elif data['type'] == 'ai':
            return AIMessage(content=data['content'], id=data.get('id'))
        elif data['type'] == 'system':
            return SystemMessage(content=data['content'], id=data.get('id'))
        else:
            return BaseMessage(type='base', content=data['content'], id=data.get('id'))

    def _auto_save_periodically(self):
        sleep_interval = 1  # Check the stop event every 1 second
        total_sleep_time = 0

        while not self.stop_event.is_set():
            if total_sleep_time >= self.auto_save_interval_sec:
                asyncio.run(self._auto_save())
                total_sleep_time = 0
            else:
                time.sleep(sleep_interval)
                total_sleep_time += sleep_interval

    async def _auto_save(self):
        self.save_messages(self.auto_save_path)

    async def stopSaving(self):
        self.stop_event.set()
        self.auto_save_task.join()
        await asyncio.to_thread(self.save_messages, self.auto_save_path)
        self.messages = []
        self.summary_memory = ""
        if self.config.debug:
            print("MemoryAssistant: Messages saved and cleared")