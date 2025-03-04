import aiounittest
import tempfile
import os
import shutil
from src.agent_manager import AgentManager
from src.config import Config
from src.memory import MemoryStrategy
from unittest.mock import AsyncMock, patch

class TestAgentManager(aiounittest.AsyncTestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = self.temp_dir.name
        self.memory_path = os.path.join(self.config_path, "history.json")

        # Copy test-agent configuration to the temporary directory
        test_agent_path = os.path.join("tests", "test-agent")
        shutil.copytree(test_agent_path, self.config_path, dirs_exist_ok=True)

        # Set environment variables for testing
        os.environ['USER_DATASOURCE_PATH'] = self.config_path
        os.environ['LOCAL_DATASOURCE_PATH'] = self.config_path
        os.environ['USER_MEMORY_PATH'] = self.memory_path
        os.environ['LOCAL_MEMORY_PATH'] = self.memory_path

        self.agent_manager = AgentManager("test-agent")
        self.agent_manager.select_agent("test-agent", debug=True)

    def tearDown(self):
        self.agent_manager.cleanup()
        self.temp_dir.cleanup()

        # Reset environment variables
        del os.environ['USER_DATASOURCE_PATH']
        del os.environ['LOCAL_DATASOURCE_PATH']
        del os.environ['USER_MEMORY_PATH']
        del os.environ['LOCAL_MEMORY_PATH']

    @patch('src.memory.MemoryAssistant.add_message', new_callable=AsyncMock)
    async def test_select_agent(self, mock):
        self.agent_manager.select_agent("new-agent", debug=False)
        agent = self.agent_manager.get_agent()
        self.assertEqual(agent.agent_name, "new-agent")

    @patch('src.memory.MemoryAssistant.add_message', new_callable=AsyncMock)
    async def test_question(self, mock):
        agent = self.agent_manager.get_agent()

        question = "How many people live in the country? Short answer."
        text = await agent.do_chain(question)
        self.assertIn("300,000", text, "Number of citizen")

        mock.assert_called_once_with(question, text)

        text = await agent.do_chain(question + " If you don't know the answer, reply with 'I cannot answer this question", skip_rag=True)
        self.assertIn("I cannot answer this question", text, "Number of citizen, without RAG")

        question = "What is the name of the country? Short answer."
        text = await agent.do_chain(question)
        self.assertIn("Aethelland", text, "Name of country")

        text = await agent.do_chain(question + " If you don't know the answer, reply with 'I cannot answer this question", skip_rag=True)
        self.assertIn("I cannot answer this question", text, "Name of country, without RAG")

    @patch('src.memory.MemoryAssistant.add_message', new_callable=AsyncMock)
    async def test_memory(self, mock):
        agent = self.agent_manager.get_agent()
        agent.memory_strategy = MemoryStrategy.SUMMARY
        question = "Are dinosaurs in the country? Short answer."

        text = await agent.do_chain(question)
        # agent.save_memory()
        # stored_memory = agent.load_memory()
        # self.assertIn("dinosaurs", stored_memory, "Dinosaurs in country")
        # mock.assert_called_once_with(question, text)

if __name__ == '__main__':
    aiounittest.main()