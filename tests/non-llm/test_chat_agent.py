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
    @patch.object(ChatAgent, "do_chain", return_value=("Mocked do_chain result", MagicMock()))
    def test_chat_agent_run_with_agent_router(self, mock_do_chain, mock_get_agent_or_fallback):
        """
        Test that ChatAgent uses the router to select a special agent and calls its run method.
        """

        # Mock the agent router to return a mock agent
        special_agent_mulder = MagicMock()
        special_agent_mulder.run.return_value = "I want to believe"
        mock_get_agent_or_fallback.return_value = special_agent_mulder

        # Mock the do_chain() method to return a mock runnable to call model.invoke()
        mock_model = mock_do_chain.return_value[1]
        mock_model.invoke.return_value = "What if you’re wrong? I want to believe"

        # Now the actual call
        agent_scully = ChatAgent(name="test-agent")
        result = agent_scully.run("What if you’re wrong?")
        self.assertEqual(result, "What if you’re wrong? I want to believe")

        mock_do_chain.assert_called_once_with("What if you’re wrong?", False)

        # Assert that the router routed to Mulder:
        mock_get_agent_or_fallback.assert_called_once_with(agent_scully, "What if you’re wrong?", ["fmi_weather_agent", "website_summary_agent", "diff_details_agent", "diff_sum_agent"])
        special_agent_mulder.run.assert_called_once()

        agent_scully.closeModels()

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