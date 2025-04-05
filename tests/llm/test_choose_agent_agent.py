import unittest
import os
from agent_assembly_line.micros.choose_agent_agent import ChooseAgentAgent

class TestChooseAgentAgent(unittest.TestCase):

    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    def test_choose_agent_agent_detect_summary_agent(self):
        examples = [
            "Summarize this document",
            "Can you provide a summary of the text?",
            "Give me a brief overview of this article.",
            "What is the main idea of this passage?",
            "Can you summarize this for me?"
        ]
        for example in examples:
            agent = ChooseAgentAgent(text=example, mode="local")
            result = agent.run()
            self.assertEqual(result, "sum_agent", f"Failed for input: {example}, result: {result}")

    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    def test_choose_agent_agent_detect_weather_agent(self):
        examples = [
            "What's the weather like today?",
            "Tell me the current weather conditions.",
            "Is it going to rain tomorrow?",
            "What is the forecast for next week?",
            "Will it snow today?"
        ]
        for example in examples:
            agent = ChooseAgentAgent(text=example, mode="local")
            result = agent.run()
            self.assertEqual(result, "fmi_weather_agent", f"Failed for input: {example}, result: {result}")

    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    def test_choose_agent_agent_no_match(self):
        examples = [
            "This is an unsupported query",
            "What is the capital of Mars?",
            "Tell me something random that doesn't match any agent.",
            # "How do I bake a cake?"
        ]

        for example in examples:
            agent = ChooseAgentAgent(text=example, mode="local")
            result = agent.run()
            self.assertEqual(result, "None", f"Failed for input: {example}, result: {result}")

    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    def test_diff_sum_agent(self):
        examples = [
            "Can you give me a summary of the changes?",
            "What changed in this commit?",
            "Summarize the diff for me."
        ]
        for example in examples:
            agent = ChooseAgentAgent(text=example)
            result = agent.run()
            self.assertEqual(result, "diff_sum_agent", f"Failed for input: {example}, result: {result}")

    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    def test_diff_details_agent(self):
        examples = [
            "Explain the changes in this commit.",
            "Explain why line 42 was modified.",
            "Can you go into detail about what changed here?",
            "Why did we change this logic in the function?",
            "Walk me through the diff."
        ]
        for example in examples:
            agent = ChooseAgentAgent(text=example)
            result = agent.run()
            self.assertEqual(result, "diff_details_agent", f"Failed for input: {example}, result: {result}")

    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    def test_sentiment_agent(self):
        examples = [
            "I love this product!",
            "This is the worst experience I've ever had.",
            "I'm feeling neutral about this.",
            "The service was excellent."
        ]
        for example in examples:
            agent = ChooseAgentAgent(text=example)
            result = agent.run()
            self.assertIn(result, "sentiment_agent", f"Failed for input: {example}, result: {result}")

    @unittest.skipIf(os.getenv("CIRCLECI") == "true", "Skipping this test on CircleCI")
    def test_website_summary_agent(self):
        examples = [
            "Summarize the content of this website.",
            "Can you provide a summary of the webpage?",
            "Give me a brief overview of this site.",
            "What is the main idea of this website?",
        ]
        for example in examples:
            agent = ChooseAgentAgent(text=example)
            result = agent.run()
            self.assertIn(result, "website_summary_agent", f"Failed for input: {example}, result: {result}")

    # skipping: clarify_agent, yes_no_agent, test_validate_agent, one_word_agent

if __name__ == "__main__":
    unittest.main()