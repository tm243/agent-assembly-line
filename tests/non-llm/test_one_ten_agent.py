import unittest
from unittest.mock import patch
from agent_assembly_line.micros.one_ten_agent import OneTenAgent

class TestOneTenAgent(unittest.TestCase):
    def setUp(self):
        self.text = "This is a sample text."
        self.agent = OneTenAgent(self.text, mode='local')

    @patch('agent_assembly_line.agent.Agent.run')
    def test_run_valid_response(self, mock_run):
        mock_run.return_value = "7"
        result = self.agent.run()
        self.assertEqual(result, "7")

    @patch('agent_assembly_line.agent.Agent.run')
    def test_run_invalid_response(self, mock_run):
        mock_run.side_effect = ["invalid", "5"]
        result = self.agent.run()
        self.assertEqual(result, "5")

    @patch('agent_assembly_line.agent.Agent.run')
    def test_run_no_valid_response(self, mock_run):
        mock_run.side_effect = ["invalid", "invalid"]
        result = self.agent.run()
        self.assertIsNone(result)

    def test_toInt_valid(self):
        self.assertEqual(OneTenAgent.toInt("5"), 5)

    def test_toInt_invalid(self):
        self.assertIsNone(OneTenAgent.toInt("invalid"))
        self.assertIsNone(OneTenAgent.toInt(""))

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            OneTenAgent(self.text, mode='invalid_mode')

if __name__ == "__main__":
    unittest.main()