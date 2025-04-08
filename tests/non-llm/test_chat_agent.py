"""
Agent-Assembly-Line
"""

import unittest
import os, shutil, tempfile
from unittest.mock import patch, MagicMock
from agent_assembly_line.chat_agent import ChatAgent

class TestChatAgent(unittest.TestCase):

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

    @patch("agent_assembly_line.decorators.agent_decorators._get_agent_or_fallback")
    def test_chat_agent_run_with_agent_router(self, mock_get_agent_or_fallback):
        """
        Test that ChatAgent uses the decision maker to select an agent and calls its run method.
        """
        # Mock the agent returned by _get_agent_or_fallback
        mock_agent = MagicMock()
        mock_agent.run.return_value = "MockAgent run result"
        mock_get_agent_or_fallback.return_value = mock_agent

        # Now the actual call
        chat_agent = ChatAgent(agent_name="test-agent")
        result = chat_agent.run("test prompt")

        # Assert that it routed to the MockAgent
        self.assertEqual(result, "MockAgent run result")
        mock_get_agent_or_fallback.assert_called_once_with(chat_agent, "test prompt", ["fmi_weather_agent", "website_summary_agent", "diff_details_agent", "diff_sum_agent"])
        mock_agent.run.assert_called_once()

        chat_agent.closeModels()

    @patch("agent_assembly_line.decorators.agent_decorators._get_agent_or_fallback")
    def test_chat_agent_run_fallback_to_original(self, mock_get_agent_or_fallback):
        """
        Test that ChatAgent falls back to the original run method when no agent is selected.
        """
        # No agent will be selected:
        mock_get_agent_or_fallback.return_value = None

        # Mock the original run method
        mock_original_run = MagicMock(return_value="Original run result")
        original_run = ChatAgent.run
        ChatAgent.run = mock_original_run

        # Now the actual call
        chat_agent = ChatAgent("test-agent")
        result = chat_agent.run("test prompt")

        # Assert that the original run method was called
        self.assertEqual(result, "Original run result")
        mock_original_run.assert_called_once_with("test prompt")

        # Restore the original run method, it would affect other test cases
        ChatAgent.run = original_run

        chat_agent.closeModels()

if __name__ == "__main__":
    unittest.main()