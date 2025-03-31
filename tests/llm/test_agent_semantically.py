"""
Agent-Assembly-Line
"""

import unittest
import tempfile
import os
import shutil
from agent_assembly_line import Agent, AgentManager
from unittest.mock import patch, Mock
from agent_assembly_line.middleware.semantic_test_case import SemanticTestCase

class TestAgent(SemanticTestCase):

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
        self.agent_manager = AgentManager()

    def tearDown(self):
        self.agent_manager.cleanup()
        self._deleteSandbox()

    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.add_message', new_callable=Mock)
    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.summarize_memory', new_callable=Mock)
    def test_question_test_agent(self, mock_summarize_memory, mock):
        agent = Agent("test-agent")

        mock_summarize_memory.assert_called_once()

        question = "How many people live in the country? Short answer."
        text = agent.run(question)
        self.assertIn("300,000", text, "Number of citizen")

        mock.assert_called_once_with(question, text)

        text = agent.run(question + " If you don't know the answer, reply only with 'I cannot answer this question'", skip_rag=True)
        self.assertSemanticallyEqual("I cannot answer this question", text)

        question = "What is the name of the country? Short answer."
        text = agent.run(question)
        self.assertIn("Aethelland", text, "Name of country")

        text = agent.run(question + " If you don't know the answer, reply only with 'I cannot answer this question'", skip_rag=True)
        self.assertSemanticallyEqual("I cannot answer this question", text)

        agent.closeModels()

    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.add_message', new_callable=Mock)
    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.summarize_memory', new_callable=Mock)
    def test_question(self, mock_summarize_memory, mock_add_message):
        self.agent_manager.select_agent("test-agent", debug=False)
        mock_summarize_memory.assert_called_once()
        agent = self.agent_manager.get_agent()

        question = "How many people live in the country? Short answer."
        text = agent.run(question)
        self.assertIn("300,000", text, "Number of citizen")
        mock_add_message.assert_called_once_with(question, text)

        text = agent.run(question + " If you don't know the answer, reply only with 'I cannot answer this question'", skip_rag=True)
        self.assertSemanticallyEqual("I cannot answer this question", text, "Number of citizen, without RAG")

        question = "What is the name of the country? Short answer."
        text = agent.run(question)
        self.assertIn("Aethelland", text, "Name of country")

        text = agent.run(question + " If you don't know the answer, reply only with 'I cannot answer this question'", skip_rag=True)
        self.assertSemanticallyEqual("I cannot answer this question", text, "Name of country, without RAG")

        # agent.cleanup()
        agent.closeModels()

if __name__ == '__main__':
    unittest.main()

