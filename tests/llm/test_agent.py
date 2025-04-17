"""
Agent-Assembly-Line
"""

import unittest, aiounittest
import tempfile
import asyncio
import os
import shutil
from agent_assembly_line.agent import Agent, Config, MemoryAssistant, NoMemory
from agent_assembly_line.memory_assistant import MemoryStrategy
from unittest.mock import patch, AsyncMock

class StubModel():
    prompt = ""
    def invoke(self, prompt):
        self.prompt = prompt
    async def ainvoke(self, prompt):
        self.prompt = prompt

class TestAgent(aiounittest.AsyncTestCase):

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

    def tearDown(self):
        self._deleteSandbox()

    def test_question_test_agent(self):
        agent = Agent("test-agent")

        question = "How many people live in the country? Short answer."
        text = agent.run(question)
        self.assertIn("300,000", text, "Number of citizen")

        question = "What is the name of the country? Short answer."
        text = agent.run(question)
        self.assertIn("Aethelland", text, "Name of country")

        agent.cleanup()
        agent.closeModels()

    async def test_question_stream(self):
        agent = Agent("test-agent")

        question = "How many people live in the country? Short answer."
        text = ""
        async for chunk in agent.stream(question):
            text += chunk

        agent.cleanup()
        await agent.aCloseModels()

    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.add_message', new_callable=AsyncMock)
    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.summarize_memory', new_callable=AsyncMock)
    async def test_memory(self, mock_summarize_memory, mock_add_message):
        agent = Agent("test-agent")
        agent.memory_strategy = MemoryStrategy.SUMMARY
        await agent.startMemoryAssistant()

        question = "Are dinosaurs in the country? Short answer."

        mock_summarize_memory.assert_called_once()

        text = agent.run(question)
        mock_add_message.assert_not_called()

        async for _ in agent.stream(question):
            pass
        mock_add_message.assert_called_once_with(question, text)

        await agent.stopMemoryAssistant()
        agent.cleanup()
        await agent.aCloseModels()

    async def test_agent_initialization(self):
        """Test the initialization of the Agent class."""
        agent = Agent("test-agent")
        self.assertEqual(agent.name, "test-agent", "Agent name should match the initialized value.")
        self.assertIsNotNone(agent.memory_strategy, "Memory strategy should be initialized.")
        self.assertIsInstance(agent.memory_strategy, MemoryStrategy, "Memory strategy should be of type MemoryStrategy.")
        self.assertEqual(agent.memory_strategy, MemoryStrategy.SUMMARY, "Memory strategy should be SUMMARY.")
        self.assertIsInstance(agent.memory_assistant, MemoryAssistant, "Memory assistant should be of type MemoryAssistant.")

        agent.cleanup()
        agent.closeModels()

    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.add_message', new_callable=AsyncMock)
    @patch('agent_assembly_line.memory_assistant.MemoryAssistant.summarize_memory', new_callable=AsyncMock)
    async def test_run_with_no_memory(self, add_message_mock, summarize_memory_mock):
        """Test the Agent.run() method with NoMemory()"""
        config = Config(load_agent_conf="test-agent", debug=False)
        config.use_memory = False
        agent = Agent(config=config)

        self.assertIsInstance(agent.memory_strategy, MemoryStrategy, "Memory strategy should be of type MemoryStrategy.")
        self.assertEqual(agent.memory_strategy, MemoryStrategy.NO_MEMORY, "Memory strategy should be NO_MEMORY.")
        self.assertIsInstance(agent.memory_assistant, NoMemory, "Memory assistant should be of type NoMemory.")

        agent.run("Hello, World!")

        add_message_mock.assert_not_called()
        summarize_memory_mock.assert_not_called()

        agent.cleanup()
        await agent.aCloseModels()

    async def test_run_with_empty_question(self):
        """Test the Agent.run() method with an empty question."""
        agent = Agent("test-agent")

        empty = agent.run("")
        self.assertAlmostEqual(empty, "", "Empty question should return an empty string.")

        agent.cleanup()
        agent.closeModels()

    @patch('agent_assembly_line.agent.Agent.model', new_callable=AsyncMock)
    async def test_stream_with_empty_question(self, mock_model):
        """Test the Agent.stream() method with an empty question."""
        agent = Agent("test-agent")

        async for _ in agent.stream(""):
            pass
        mock_model.astream.assert_not_called()

        with self.assertRaises(TypeError, msg="No question should skip the invoke."):
            async for _ in agent.stream(None):
                pass
        mock_model.astream.assert_not_called()

        agent.cleanup()
        agent.closeModels()

    async def test_cleanup_without_usage(self):
        """Test cleanup when Agent has not been used."""
        agent = Agent("test-agent")
        try:
            agent.cleanup()
        except Exception as e:
            self.fail(f"Agent.cleanup() raised an exception unexpectedly: {e}")

        await agent.aCloseModels()

    async def test_run_with_invalid_question_type(self):
        """Test the Agent.run() method with a non-string question."""
        agent = Agent("test-agent")
        with self.assertRaises(TypeError, msg="Non-string question should raise a TypeError."):
            agent.run(12345)
        agent.cleanup()
        agent.closeModels()

    async def test_stream_with_invalid_question_type(self):
        """Test the Agent.stream() method with a non-string question."""
        agent = Agent("test-agent")
        with self.assertRaises(TypeError, msg="Non-string question should raise a TypeError."):
            async for _ in agent.stream(12345):
                pass
        agent.cleanup()
        agent.closeModels()

    # @todo add test "agent not found"
    # @todo add test "more than 10 documents"

if __name__ == '__main__':
    unittest.main()

