"""
Agent-Assembly-Line
"""

import unittest, aiounittest
import json
import os
import tempfile
from unittest.mock import AsyncMock
from agent_assembly_line.memory_assistant import MemoryAssistant, MemoryStrategy
from langchain_core.messages import HumanMessage, AIMessage

class TestMemoryAssistant(aiounittest.AsyncTestCase):
    def setUp(self):
        self.config = AsyncMock()
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.config.memory_path = self.temp_file.name
        self.config.debug = False
        self.config.memory_prompt = "Summarize the following conversation: "
        self.model = AsyncMock()
        self.memory_assistant = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=self.model, config=self.config)

    async def asyncTearDown(self):
        if os.path.exists(self.config.memory_path):
            os.remove(self.config.memory_path)
        self.temp_file.close()

    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    async def test_save_messages_no_duplicates(self):
        """
        @todo use mock
        """
        self.memory_assistant.auto_save_interval_sec = 1
        self.memory_assistant.auto_save_message_count = 1

        await self.memory_assistant.add_message("Hello Message 1", "Hi there! Answer 1")
        await self.memory_assistant.add_message("How are you? Message 2", "I'm good, thanks! Answer 2")

        # Mock existing messages in the file
        existing_messages = [
            {"id": "human-1", "type": "human", "content": "Hello Message 3"},
            {"id": "ai-1", "type": "ai", "content": "Hi there! Answer 3"}
        ]
        with open(self.config.memory_path, 'w') as f:
            json.dump(existing_messages, f, indent=4, sort_keys=True)

        self.memory_assistant.save_messages(self.config.memory_path)

        # Now verify that the new messages were added to the file
        with open(self.config.memory_path, 'r') as f:
            written_data = json.load(f)

        # now we have the 2 existing and 4 new messages in the file
        self.assertEqual(len(written_data), 6)

        expected_messages = [
            {"id": "human-1", "type": "human", "content": "Hello Message 3"},
            {"id": "ai-1", "type": "ai", "content": "Hi there! Answer 3"},
            {"id": "human-2", "type": "human", "content": "Hello Message 1"},
            {"id": "ai-2", "type": "ai", "content": "Hi there! Answer 1"},
            {"id": "human-3", "type": "human", "content": "How are you? Message 2"},
            {"id": "ai-3", "type": "ai", "content": "I'm good, thanks! Answer 2"}
        ]

        for expected_message in expected_messages:
            self.assertTrue(any(
                all(item in message.items() for item in expected_message.items() if item[0] in ["content", "type"])
                for message in written_data
            ), f"Expected message not found: {expected_message}")

    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    async def test_load_messages(self):
        """
        @todo use mock
        """
        existing_messages = [
            {"id": "human-1", "type": "human", "content": "Hello"},
            {"id": "ai-1", "type": "ai", "content": "Hi there!"}
        ]
        with open(self.config.memory_path, 'w') as f:
            json.dump(existing_messages, f)

        await self.memory_assistant.load_messages(self.config.memory_path)

        self.assertEqual(len(self.memory_assistant.messages), 2)
        self.assertEqual(self.memory_assistant.messages[0].content, "Hello")
        self.assertEqual(self.memory_assistant.messages[1].content, "Hi there!")

if __name__ == "__main__":
    unittest.main()