"""
Agent-Assembly-Line
"""

import aiounittest, unittest
import tempfile
import os
import shutil
from agent_assembly_line.agent_manager import AgentManager
from agent_assembly_line.memory_assistant import MemoryStrategy
from unittest.mock import patch, Mock, AsyncMock

class TestAgentManager(aiounittest.AsyncTestCase):

    def _createSandbox(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = self.temp_dir.name
        self.memory_path = os.path.join(self.config_path, "history.json")
        test_agent_path = os.path.join("tests", "test-agent")
        shutil.copytree(test_agent_path, self.config_path, dirs_exist_ok=True)

        self.env_patcher = patch.dict(os.environ, {
            'USER_AGENTS_PATH': self.config_path,
            'LOCAL_AGENTS_PATH': self.config_path,
            'USER_MEMORY_PATH': self.memory_path,
            'LOCAL_MEMORY_PATH': self.memory_path,
        })
        self.env_patcher.start()

    def _deleteSandbox(self):
        self.temp_dir.cleanup()
        self.config_path = None
        self.memory_path = None
        self.temp_dir = None
        self.env_patcher.stop()

    def setUp(self):
        self._createSandbox()
        self.agent_manager = AgentManager()

    def tearDown(self):
        self.agent_manager.cleanup()
        self._deleteSandbox()

    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.summarize_memory', new_callable=AsyncMock)
    async def test_select_agent(self, mock_summarize_memory):
        agent = self.agent_manager.select_agent("test-agent", debug=False)
        await agent.startMemoryAssistant()

        mock_summarize_memory.assert_called_once()
        self.assertEqual(agent.name, "test-agent")

        await agent.stopMemoryAssistant()
        agent.cleanup()
        agent.closeModels()
        self.agent_manager.cleanup()


    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    async def test_question(self):
        self.agent_manager.select_agent("test-agent", debug=False)
        agent = self.agent_manager.get_agent()

        question = "How many people live in the country? Short answer."
        text = agent.run(question)
        self.assertIn("300,000", text, "Number of citizen")

        question = "What is the name of the country? Short answer."
        text = agent.run(question)
        self.assertIn("Aethelland", text, "Name of country")

        agent.cleanup()
        await agent.aCloseModels()
        self.agent_manager.cleanup()

    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.summarize_memory', new_callable=AsyncMock)
    async def test_memory(self, mock_summarize_memory):
        self.agent_manager.select_agent("test-agent", debug=False)
        agent = self.agent_manager.get_agent()
        await agent.startMemoryAssistant()
        agent.memory_strategy = MemoryStrategy.SUMMARY

        mock_summarize_memory.assert_called_once()

        question = "Are dinosaurs in the country? Short answer."
        text = agent.run(question)
        # agent.save_memory()
        # stored_memory = agent.load_memory()
        # self.assertIn("dinosaurs", stored_memory, "Dinosaurs in country")
        # mock.assert_called_once_with(question, text)
        await agent.stopMemoryAssistant()
        agent.cleanup()
        await agent.aCloseModels()
        self.agent_manager.cleanup()


if __name__ == '__main__':
    aiounittest.main()