"""
Agent-Assembly-Line
"""

import unittest
import tempfile
import os
import shutil
from agent_assembly_line import Agent, AgentManager
from unittest.mock import patch, Mock, AsyncMock
from agent_assembly_line.middleware.semantic_test_case import AioSemanticTestCase

class TestAgent(AioSemanticTestCase):

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

    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.summarize_memory', new_callable=AsyncMock)
    async def test_question_test_agent(self, mock_summarize_memory):
        agent = Agent("test-agent")
        await agent.startMemoryAssistant()

        mock_summarize_memory.assert_called_once()

        question = "How many people live in the country? Short answer."
        text = agent.run(question)
        self.assertIn("300,000", text, "Number of citizen")

        text = agent.run(question + " If you don't know the answer, reply only with 'I cannot answer this question'", skip_rag=True)
        await self.assertSemanticallyEqual("I cannot answer this question", text)

        question = "What is the name of the country? Short answer."
        text = agent.run(question)
        self.assertIn("Aethelland", text, "Name of country")

        text = agent.run(question + " If you don't know the answer, reply only with 'I cannot answer this question'", skip_rag=True)
        await self.assertSemanticallyEqual("I cannot answer this question", text)

        agent.cleanup()
        await agent.stopMemoryAssistant()

        agent.closeModels()
        await agent.aCloseModels()

    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    async def test_question(self):
        self.agent_manager.select_agent("test-agent", debug=False)
        agent = self.agent_manager.get_agent()

        question = "How many people live in the country? Short answer."
        text = await agent.arun(question)
        self.assertIn("300,000", text, "Number of citizen")

        text = await agent.arun(question + " If you don't know the answer, reply only with 'I cannot answer this question'", skip_rag=True)
        await self.assertSemanticallyEqual("I cannot answer this question", text, "Number of citizen, without RAG")

        question = "What is the name of the country? Short answer."
        text = await agent.arun(question)
        self.assertIn("Aethelland", text, "Name of country")

        text = agent.run(question + " If you don't know the answer, reply only with 'I cannot answer this question'", skip_rag=True)
        await self.assertSemanticallyEqual("I cannot answer this question", text, "Name of country, without RAG")

        agent.cleanup()
        await agent.aCloseModels()


if __name__ == '__main__':
    unittest.main()

