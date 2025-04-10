"""
Agent-Assembly-Line
"""

import unittest, aiounittest
from unittest.mock import MagicMock, patch
from agent_assembly_line.decorators.agent_decorators import agent_router

# Define a test class with the decorator
@agent_router(allowed_agents=["mock_agent"])
class TestClass:
    _router = None
    _allocated_agents = []
    _inline_text = ""
    def run(self, prompt):
        return f"Original run with prompt: {prompt}" + self._inline_text
    async def arun(self, prompt):
        return f"Original arun with prompt: {prompt}" + self._inline_text
    def add_inline_text(self, text):
        self._inline_text = f" {text}"
        pass

class TestWithDecisionMakerDecorator(aiounittest.AsyncTestCase):
    def setUp(self):
        # Mock agent class to simulate behavior
        class MockAgent:
            def __init__(self, prompt):
                self.prompt = prompt

            def run(self):
                return f"MockAgent run with prompt: {self.prompt}"

            async def arun(self):
                return f"MockAgent arun with prompt: {self.prompt}"

            def add_inline_text(self, text):
                pass

        self.MockAgent = MockAgent

    @patch("agent_assembly_line.decorators.agent_decorators._get_agent_or_fallback")
    def test_run_with_agent_router(self, mock_get_agent_or_fallback):
        """
        Verifies that the decorator correctly calls the mock agent's run method when an agent is selected.
        """
        # Mock the _get_agent_or_fallback to return a mock agent
        mock_get_agent_or_fallback.return_value = self.MockAgent("test prompt")

        # Instantiate the class and call the run method
        instance = TestClass()
        result = instance.run("test prompt")

        # Assert that the mock agent's run method was called
        self.assertEqual(result, "Original run with prompt: test prompt MockAgent run with prompt: test prompt")
        mock_get_agent_or_fallback.assert_called_once_with(instance, "test prompt", ["mock_agent"])

    @patch("agent_assembly_line.decorators.agent_decorators._get_agent_or_fallback")
    def test_run_fallback_to_original(self, mock_get_agent_or_fallback):
        """
        Verifies that the decorator correctly falls back to the original run method when no agent is selected.
        """
        # Mock the _get_agent_or_fallback to return None (fallback to original method)
        mock_get_agent_or_fallback.return_value = None

        # Instantiate the class and call the run method
        instance = TestClass()
        result = instance.run("test prompt")

        # Assert that the original run method was called
        self.assertEqual(result, "Original run with prompt: test prompt")
        mock_get_agent_or_fallback.assert_called_once_with(instance, "test prompt", ["mock_agent"])

    @patch("agent_assembly_line.decorators.agent_decorators._get_agent_or_fallback")
    async def test_arun_with_agent_router(self, mock_get_agent_or_fallback):
        """
        Verifies that the decorator correctly calls the mock agent's arun method when an agent is selected.
        """
        # Mock the _get_agent_or_fallback to return a mock agent
        mock_get_agent_or_fallback.return_value = self.MockAgent("test prompt")

        # Instantiate the class and call the arun method
        instance = TestClass()
        result = await instance.arun("test prompt")

        # Assert that the mock agent's run method was called (agents only do run())
        self.assertEqual(result, "Original arun with prompt: test prompt MockAgent run with prompt: test prompt")
        mock_get_agent_or_fallback.assert_called_once_with(instance, "test prompt", ["mock_agent"])

if __name__ == "__main__":
    unittest.main()