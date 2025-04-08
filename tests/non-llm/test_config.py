"""
Agent-Assembly-Line
"""

import unittest
import os
import tempfile
import yaml
from agent_assembly_line.config import Config
from unittest.mock import patch

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.agent_name = "test_agent"
        self.config_dir = os.path.join(self.test_dir.name, self.agent_name)
        os.makedirs(self.config_dir, exist_ok=True)

        self.config_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "data": {
                "file": "data.txt",
                "url": "http://example.com",
                "inline": "This is some inline content"
            },
            "prompt": {
                "template": "prompt_template.txt"
            },
            "llm": {
                "model-name": "test_model",
                "model-identifier": "ollama:test_model",
                "embeddings": "test_embeddings"
            },
            "memory-prompt": "Please summarize the conversation.",
            "use-memory": True,
            "timeout": 100,
            "ollama-keep-alive": True
        }

        try:
            with open(os.path.join(self.config_dir, "config.yaml"), "w") as f:
                yaml.dump(self.config_data, f)
        except Exception as e:
            self.fail(f"Failed to write config file: {e}")

        self.env_patcher = patch.dict(os.environ, {
            'USER_AGENTS_PATH': self.test_dir.name + "/" + self.agent_name
        })
        self.env_patcher.start()

    def tearDown(self):
        self.test_dir.cleanup()
        self.env_patcher.stop()

    def test_load_conf_file(self):
        config = Config(load_agent_conf=self.agent_name)
        self.assertEqual(config.name, self.config_data["name"])
        self.assertEqual(config.description, self.config_data["description"])
        self.assertEqual(config.doc, os.path.join(self.config_dir, self.config_data["data"]["file"]))
        self.assertEqual(config.url, self.config_data["data"]["url"])
        self.assertEqual(config.inline_content, self.config_data["data"]["inline"])
        self.assertEqual(config.prompt_template, os.path.join(self.config_dir, self.config_data["prompt"]["template"]))
        self.assertEqual(config.model_name, self.config_data["llm"]["model-name"])
        self.assertEqual(config.model_identifier, self.config_data["llm"]["model-identifier"])
        self.assertEqual(config.embeddings, self.config_data["llm"]["embeddings"])
        self.assertEqual(config.memory_prompt, self.config_data["memory-prompt"])
        self.assertEqual(config.use_memory, self.config_data["use-memory"])
        self.assertEqual(config.timeout, self.config_data["timeout"])
        self.assertEqual(config.ollama_keep_alive, self.config_data["ollama-keep-alive"])

    def test_missing_name(self):
        del self.config_data["name"]
        with open(os.path.join(self.config_dir, "config.yaml"), "w") as f:
            yaml.dump(self.config_data, f)

        with self.assertRaises(ValueError) as context:
            Config(load_agent_conf=self.agent_name)
        self.assertIn("Missing or invalid required field: name", str(context.exception))

    def test_missing_description(self):
        del self.config_data["description"]
        with open(os.path.join(self.config_dir, "config.yaml"), "w") as f:
            yaml.dump(self.config_data, f)

        config = Config(load_agent_conf=self.agent_name)
        self.assertEqual(config.description, "")

    def test_missing_data(self):
        del self.config_data["data"]
        with open(os.path.join(self.config_dir, "config.yaml"), "w") as f:
            yaml.dump(self.config_data, f)

        config = Config(load_agent_conf=self.agent_name)
        self.assertEqual(config.doc, "")
        self.assertEqual(config.url, "")
        self.assertEqual(config.inline_content, "")

    def test_missing_llm(self):
        del self.config_data["llm"]
        with open(os.path.join(self.config_dir, "config.yaml"), "w") as f:
            yaml.dump(self.config_data, f)

        with self.assertRaises(ValueError) as context:
            Config(load_agent_conf=self.agent_name)
        self.assertIn("Missing or invalid required field: llm", str(context.exception))

    def test_memory_path(self):
        config = Config(load_agent_conf=self.agent_name)
        expected_memory_path = os.path.expanduser(f"~/.local/share/agent-assembly-line/agents/Test Agent/history.json")
        self.assertEqual(config.memory_path, expected_memory_path)

    def test_cleanup(self):
        config = Config(load_agent_conf=self.agent_name)
        config.cleanup()
        self.assertIsNone(config.doc)
        self.assertIsNone(config.url)
        self.assertIsNone(config.inline_content)
        self.assertIsNone(config.prompt_template)
        self.assertIsNone(config.model_name)
        self.assertIsNone(config.model_identifier)
        self.assertIsNone(config.embeddings)
        self.assertIsNone(config.memory_prompt)
        self.assertIsNone(config.debug)
        self.assertIsNone(config.name)
        self.assertIsNone(config.description)

if __name__ == '__main__':
    unittest.main()