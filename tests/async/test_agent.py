"""
Agent-Assembly-Line
"""

import unittest, aiounittest
import tempfile
import os
import shutil
from agent_assembly_line.agent import Agent
from agent_assembly_line.memory_assistant import MemoryStrategy
from unittest.mock import patch, Mock

class TestAgent(aiounittest.AsyncTestCase):

    def _createSandbox(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = self.temp_dir.name
        self.memory_path = os.path.join(self.config_path, "history.json")
        test_agent_path = os.path.join("tests", "test-agent")
        shutil.copytree(test_agent_path, self.config_path, dirs_exist_ok=True)
        os.environ['USER_AGENTS_PATH'] = self.config_path
        os.environ['LOCAL_AGENTS_PATH'] = self.config_path
        os.environ['USER_MEMORY_PATH'] = self.memory_path
        os.environ['LOCAL_MEMORY_PATH'] = self.memory_path

    def _deleteSandbox(self):
        self.temp_dir.cleanup()
        self.config_path = None
        self.memory_path = None
        self.temp_dir = None
        os.environ.pop('USER_AGENTS_PATH', None)
        os.environ.pop('LOCAL_AGENTS_PATH', None)
        os.environ.pop('USER_MEMORY_PATH', None)
        os.environ.pop('LOCAL_MEMORY_PATH', None)

    def setUp(self):
        self._createSandbox()

    def tearDown(self):
        self._deleteSandbox()

    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.add_message', new_callable=Mock)
    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.summarize_memory', new_callable=Mock)
    async def test_question_test_agent(self, mock_summarize_memory, mock):
        agent = Agent("test-agent")

        mock_summarize_memory.assert_called_once()

        question = "How many people live in the country? Short answer."
        text = agent.run(question)
        self.assertIn("300,000", text, "Number of citizen")

        mock.assert_called_once_with(question, text)

        text = agent.run(question + " If you don't know the answer, reply with 'I cannot answer this question", skip_rag=True)
        self.assertIn("I cannot answer this question", text, "Number of citizen, without RAG")

        question = "What is the name of the country? Short answer."
        text = agent.run(question)
        self.assertIn("Aethelland", text, "Name of country")

        text = agent.run(question + " If you don't know the answer, reply with 'I cannot answer this question", skip_rag=True)
        self.assertIn("I cannot answer this question", text, "Name of country, without RAG")

        await agent.cleanup()
        agent.closeModels()

    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.add_message', new_callable=Mock)
    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.summarize_memory', new_callable=Mock)
    async def test_question_stream(self, mock_summarize_memory, mock_add_messages):
        agent = Agent("test-agent")

        mock_summarize_memory.assert_called_once()

        question = "How many people live in the country? Short answer."
        text = ""
        async for chunk in agent.stream(question):
            text += chunk
        self.assertIn("300,000", text, "Number of citizen")

        mock_add_messages.assert_called_once_with(question, text)

        await agent.cleanup()
        await agent.aCloseModels()
        agent.closeModels()

    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.add_message', new_callable=Mock)
    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.summarize_memory', new_callable=Mock)
    async def test_memory(self, mock_summarize_memory, mock):
        agent = Agent("test-agent")
        agent.memory_strategy = MemoryStrategy.SUMMARY
        question = "Are dinosaurs in the country? Short answer."

        mock_summarize_memory.assert_called_once()

        text = agent.run(question)
        # agent.save_memory()
        # stored_memory = agent.load_memory()
        # self.assertIn("dinosaurs", stored_memory, "Dinosaurs in country")
        mock.assert_called_once_with(question, text)

        await agent.cleanup()
        agent.closeModels()

    # @todo add test "agent not found"
    # @todo add test "more than 10 documents"

if __name__ == '__main__':
    unittest.main()

