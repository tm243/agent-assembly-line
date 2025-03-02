import aiounittest
import tempfile
import os, asyncio
from src.memory import MemoryAssistant, MemoryStrategy
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

class StubModel():
    def invoke(self, prompt):
        self.prompt = prompt

class StubConfig():
    memory_prompt = "memory-prompt"
    debug = False

class TestMemory(aiounittest.AsyncTestCase):

    async def test_add_message(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=StubConfig())

        await memory.add_message("What day is today?", "Today is Tuesday")

        self.assertEqual(len(memory.messages), 2)
        self.assertEqual(memory.messages[0].content, "What day is today?")
        self.assertEqual(memory.messages[1].content, "Today is Tuesday")

    async def test_save_messages(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=StubConfig())

        await memory.add_message("message", "response")

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            memory.save_messages(temp_file_path)
            memory.load_messages(temp_file_path)
            self.assertEqual(len(memory.messages), 2)
            self.assertEqual(memory.messages[0].content, "message")
            self.assertEqual(memory.messages[1].content, "response")
        finally:
            os.remove(temp_file_path)

    async def test_trim_messages(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=StubConfig())
        memory.max_messages = 6

        for i in range(60):
            await memory.add_message(f"Question {i}", f"Answer {i}")

        self.assertEqual(len(memory.messages), 6)
        self.assertEqual(memory.messages[0].content, "Question 57")
        self.assertEqual(memory.messages[1].content, "Answer 57")

    def test_trim_messages_buffer(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=StubConfig())
        memory.max_messages = 6

        # more than 6 messages, trim_messages will only leave 7,8,9 in the list
        for i in range(10):
            memory.messages.append(HumanMessage(content=f"Question {i}"))
            memory.messages.append(AIMessage(content=f"Answer {i}"))

        memory.trim_messages_buffer()

        self.assertEqual(len(memory.messages), 6)
        self.assertEqual(memory.messages[0].content, "Question 7")
        self.assertEqual(memory.messages[1].content, "Answer 7")

    def test_message_from_dict(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=StubConfig())

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

    def test_message_from_dict_edge_cases(self):
        memory = MemoryAssistant(strategy=MemoryStrategy.SUMMARY, model=StubModel(), config=StubConfig())

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

if __name__ == '__main__':
    aiounittest.main()
