"""
Agent-Assembly-Line
"""

import aiounittest
import tempfile
import os, asyncio
from agent_assembly_line.memory_assistant import MemoryAssistant, MemoryStrategy
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

class StubModel():
    prompt = ""
    def invoke(self, prompt):
        self.prompt = prompt
    async def ainvoke(self, prompt):
        self.prompt = prompt

class StubConfig():
    memory_prompt = "memory-prompt"
    debug = False
    def __init__(self, memory_path=None):
        if memory_path is None:
            self.temp_file = tempfile.NamedTemporaryFile(delete=False)
            self.memory_path = self.temp_file.name
        else:
            self.memory_path = memory_path

    def cleanup(self):
        if hasattr(self, 'temp_file'):
            self.temp_file.close()
            os.remove(self.memory_path)

class TestMemory(aiounittest.AsyncTestCase):

    def setUp(self):
        self.config = StubConfig()

    def tearDown(self):
        self.config.cleanup()

    async def test_add_message(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=self.config)

        await memory.add_message("What day is today?", "Today is Tuesday")

        self.assertEqual(len(memory.messages), 2)
        self.assertEqual(memory.messages[0].content, "What day is today?")
        self.assertEqual(memory.messages[1].content, "Today is Tuesday")

        await memory.stopSaving()

    async def test_save_messages(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=self.config)
        await memory.start_saving()
        await memory.load_messages(self.config.memory_path)

        await memory.add_message("message", "response")

        memory.save_messages(self.config.memory_path)
        memory.messages = []
        await memory.load_messages(self.config.memory_path)
        self.assertEqual(len(memory.messages), 2)
        self.assertEqual(memory.messages[0].content, "message")
        self.assertEqual(memory.messages[1].content, "response")

        await memory.stopSaving()

    async def test_trim_messages(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=self.config)
        memory.max_messages_in_buffer = 6

        for i in range(60):
            await memory.add_message(f"Question {i}", f"Answer {i}")

        self.assertEqual(len(memory.messages), 6)
        self.assertEqual(memory.messages[0].content, "Question 57")
        self.assertEqual(memory.messages[1].content, "Answer 57")

        await memory.stopSaving()

    async def test_trim_messages_buffer(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=self.config)
        memory.max_messages_in_buffer = 6

        # more than 6 messages, trim_messages will only leave 7,8,9 in the list
        for i in range(10):
            memory.messages.append(HumanMessage(content=f"Question {i}"))
            memory.messages.append(AIMessage(content=f"Answer {i}"))

        memory.trim_messages_buffer()

        self.assertEqual(len(memory.messages), 6)
        self.assertEqual(memory.messages[0].content, "Question 7")
        self.assertEqual(memory.messages[1].content, "Answer 7")

        await memory.stopSaving()

    async def test_message_from_dict(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=self.config)

        human_message_dict = {'type': 'human', 'content': 'Hello'}
        ai_message_dict = {'type': 'ai', 'content': 'Hi there!'}
        system_message_dict = {'type': 'system', 'content': 'System message'}
        base_message_dict = {'type': 'base', 'content': 'Base message'}

        human_message = memory._message_from_dict(human_message_dict)
        ai_message = memory._message_from_dict(ai_message_dict)
        system_message = memory._message_from_dict(system_message_dict)
        base_message = memory._message_from_dict(base_message_dict)

        self.assertIsInstance(human_message, HumanMessage)
        self.assertEqual(human_message.content, 'Hello')

        self.assertIsInstance(ai_message, AIMessage)
        self.assertEqual(ai_message.content, 'Hi there!')

        self.assertIsInstance(system_message, SystemMessage)
        self.assertEqual(system_message.content, 'System message')

        self.assertIsInstance(base_message, BaseMessage)
        self.assertEqual(base_message.content, 'Base message')

        await memory.stopSaving()

    async def test_message_from_dict_edge_cases(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=self.config)

        empty_message_dict = {'type': 'human', 'content': ''}
        none_message_dict = {'type': 'ai', 'content': None}
        invalid_type_message_dict = {'type': 'invalid', 'content': 'Invalid type'}

        empty_message = memory._message_from_dict(empty_message_dict)
        none_message = memory._message_from_dict(none_message_dict)
        invalid_type_message = memory._message_from_dict(invalid_type_message_dict)

        self.assertIsInstance(empty_message, HumanMessage)
        self.assertEqual(empty_message.content, '')

        self.assertIsNone(none_message)

        self.assertIsInstance(invalid_type_message, BaseMessage)
        self.assertEqual(invalid_type_message.content, 'Invalid type')

        await memory.stopSaving()

    async def test_auto_save(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=self.config)
        memory.auto_save_interval = 1

        await memory.add_message("Auto-save test", "This should be saved automatically")

        # Wait for the auto-save to trigger
        await asyncio.sleep(2)

        await memory.load_messages(self.config.memory_path)
        self.assertEqual(len(memory.messages), 2)
        self.assertEqual(memory.messages[0].content, "Auto-save test")
        self.assertEqual(memory.messages[1].content, "This should be saved automatically")

        await memory.stopSaving()

    async def test_add_summarize_memory(self):
        """
        add_message() should add messages to the memory buffer and summarize_memory() should summarize the messages.
        """
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=self.config)

        await memory.add_message("What day is today?", "Today is Tuesday")
        await memory.add_message("What time is it?", "It's 3 PM")

        while not memory.model.prompt:
            await asyncio.sleep(0.1)

        self.assertIn("What day is today?", memory.model.prompt)
        self.assertIn("What time is it?", memory.model.prompt)

        await memory.stopSaving()

    async def test_no_summary(self):
        """
        If the memory strategy is set to NO_MEMORY, the model should not be prompted to summarize the memory.
        """
        memory = MemoryAssistant(strategy=MemoryStrategy.NO_MEMORY, model=StubModel(), config=self.config)

        await memory.add_message("What day is today?", "Today is Tuesday")
        await memory.add_message("What time is it?", "It's 3 PM")

        self.assertEqual("", memory.model.prompt)

        await memory.stopSaving()

if __name__ == '__main__':
    aiounittest.main()
