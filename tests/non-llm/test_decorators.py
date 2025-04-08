"""
Agent-Assembly-Line
"""

import unittest
from unittest.mock import MagicMock, patch
from agent_assembly_line.decorators.agent_decorators import agent_router

class TestWithDecisionMakerDecorator(unittest.TestCase):
    def setUp(self):
        # Mock agent class to simulate behavior
        class MockAgent:
            def __init__(self, prompt):
                self.prompt = prompt

            def run(self):
                return f"MockAgent run with prompt: {self.prompt}"

            async def arun(self):
                return f"MockAgent arun with prompt: {self.prompt}"

        self.MockAgent = MockAgent

    @patch("agent_assembly_line.decorators.agent_decorators._get_agent_or_fallback")
    def test_run_with_agent_router(self, mock_get_agent_or_fallback):
        """
        Verifies that the decorator correctly calls the mock agent's run method when an agent is selected.
        """
        # Mock the _get_agent_or_fallback to return a mock agent
        mock_get_agent_or_fallback.return_value = self.MockAgent("test prompt")

        # Define a test class with the decorator
        @agent_router(allowed_agents=["mock_agent"])
        class TestClass:
            def run(self, prompt):
                return f"Original run with prompt: {prompt}"

        # Instantiate the class and call the run method
        instance = TestClass()
        result = instance.run("test prompt")

        # Assert that the mock agent's run method was called
        self.assertEqual(result, "MockAgent run with prompt: test prompt")
        mock_get_agent_or_fallback.assert_called_once_with(instance, "test prompt", ["mock_agent"])

    @patch("agent_assembly_line.decorators.agent_decorators._get_agent_or_fallback")
    def test_run_fallback_to_original(self, mock_get_agent_or_fallback):
        """
        Verifies that the decorator correctly falls back to the original run method when no agent is selected.
        """
        # Mock the _get_agent_or_fallback to return None (fallback to original method)
        mock_get_agent_or_fallback.return_value = None

        # Define a test class with the decorator
        @agent_router(allowed_agents=["mock_agent"])
        class TestClass:
            def run(self, prompt):
                return f"Original run with prompt: {prompt}"

        # Instantiate the class and call the run method
        instance = TestClass()
        result = instance.run("test prompt")

        # Assert that the original run method was called
        self.assertEqual(result, "Original run with prompt: test prompt")
        mock_get_agent_or_fallback.assert_called_once_with(instance, "test prompt", ["mock_agent"])

    @patch("agent_assembly_line.decorators.agent_decorators._get_agent_or_fallback")
    def test_arun_with_agent_router(self, mock_get_agent_or_fallback):
        """
        Verifies that the decorator correctly calls the mock agent's arun method when an agent is selected.
        """
        # Mock the _get_agent_or_fallback to return a mock agent
        mock_get_agent_or_fallback.return_value = self.MockAgent("test prompt")

        # Define a test class with the decorator
        @agent_router(allowed_agents=["mock_agent"])
        class TestClass:
            async def run(self, prompt):
                return f"Original run with prompt: {prompt}"

            async def arun(self, prompt):
                return f"Original arun with prompt: {prompt}"

        # Instantiate the class and call the arun method
        instance = TestClass()
        result = self.run_async(instance.arun("test prompt"))

        # Assert that the mock agent's run method was called (agents only do run())
        self.assertEqual(result, "MockAgent run with prompt: test prompt")
        mock_get_agent_or_fallback.assert_called_once_with(instance, "test prompt", ["mock_agent"])

    def run_async(self, coro):
        """Helper method to run async functions in a synchronous test."""
        import asyncio
        return asyncio.run(coro)

if __name__ == "__main__":
    unittest.main()