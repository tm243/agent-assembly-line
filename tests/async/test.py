"""
Agent-Assembly-Line
"""

import unittest, aiounittest
import tempfile
import os
import shutil
from src.chain import Chain
from src.memory_assistant import MemoryStrategy
from unittest.mock import patch, Mock

class TestChain(aiounittest.AsyncTestCase):

    def _createSandbox(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = self.temp_dir.name
        self.memory_path = os.path.join(self.config_path, "history.json")
        test_agent_path = os.path.join("tests", "test-agent")
        shutil.copytree(test_agent_path, self.config_path, dirs_exist_ok=True)
        os.environ['USER_DATASOURCE_PATH'] = self.config_path
        os.environ['LOCAL_DATASOURCE_PATH'] = self.config_path
        os.environ['USER_MEMORY_PATH'] = self.memory_path
        os.environ['LOCAL_MEMORY_PATH'] = self.memory_path

    def _deleteSandbox(self):
        self.temp_dir.cleanup()
        self.config_path = None
        self.memory_path = None
        self.temp_dir = None
        os.environ.pop('USER_DATASOURCE_PATH', None)
        os.environ.pop('LOCAL_DATASOURCE_PATH', None)
        os.environ.pop('USER_MEMORY_PATH', None)
        os.environ.pop('LOCAL_MEMORY_PATH', None)

    def setUp(self):
        self._createSandbox()

    def tearDown(self):
        self._deleteSandbox()

    @patch('src.memory_assistant.MemoryAssistant.add_message', new_callable=Mock)
    @patch('src.memory_assistant.MemoryAssistant.summarize_memory', new_callable=Mock)
    async def test_question_test_agent(self, mock_summarize_memory, mock):
        chain = Chain("test-agent")

        mock_summarize_memory.assert_called_once()

        question = "How many people live in the country? Short answer."
        text = chain.run(question)
        self.assertIn("300,000", text, "Number of citizen")

        mock.assert_called_once_with(question, text)

        text = chain.run(question + " If you don't know the answer, reply with 'I cannot answer this question", skip_rag=True)
        self.assertIn("I cannot answer this question", text, "Number of citizen, without RAG")

        question = "What is the name of the country? Short answer."
        text = chain.run(question)
        self.assertIn("Aethelland", text, "Name of country")

        text = chain.run(question + " If you don't know the answer, reply with 'I cannot answer this question", skip_rag=True)
        self.assertIn("I cannot answer this question", text, "Name of country, without RAG")

        await chain.cleanup()
        chain.closeModels()

    @patch('src.memory_assistant.MemoryAssistant.add_message', new_callable=Mock)
    @patch('src.memory_assistant.MemoryAssistant.summarize_memory', new_callable=Mock)
    async def test_question_stream(self, mock_summarize_memory, mock_add_messages):
        chain = Chain("test-agent")

        mock_summarize_memory.assert_called_once()

        question = "How many people live in the country? Short answer."
        text = ""
        async for chunk in chain.stream(question):
            text += chunk
        self.assertIn("300,000", text, "Number of citizen")

        mock_add_messages.assert_called_once_with(question, text)

        await chain.cleanup()
        await chain.aCloseModels()
        chain.closeModels()

    @patch('src.memory_assistant.MemoryAssistant.add_message', new_callable=Mock)
    @patch('src.memory_assistant.MemoryAssistant.summarize_memory', new_callable=Mock)
    async def test_memory(self, mock_summarize_memory, mock):
        chain = Chain("test-agent")
        chain.memory_strategy = MemoryStrategy.SUMMARY
        question = "Are dinosaurs in the country? Short answer."

        mock_summarize_memory.assert_called_once()

        text = chain.run(question)
        # chain.save_memory()
        # stored_memory = chain.load_memory()
        # self.assertIn("dinosaurs", stored_memory, "Dinosaurs in country")
        mock.assert_called_once_with(question, text)

        await chain.cleanup()
        chain.closeModels()

    # @todo add test "agent not found"
    # @todo add test "more than 10 documents"

if __name__ == '__main__':
    unittest.main()

