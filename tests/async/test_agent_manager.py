import aiounittest
from src.agent_manager import AgentManager
from src.memory import MemoryStrategy
from unittest.mock import AsyncMock, patch

class TestAgentManager(aiounittest.AsyncTestCase):

    def setUp(self):
        self.agent_manager = AgentManager()
        self.agent_manager.select_agent("chat-demo", debug=True)

    def tearDown(self):
        self.agent_manager.cleanup()

    @patch('src.memory.MemoryAssistant.add_message', new_callable=AsyncMock)
    async def test_select_agent(self, mock):
        self.agent_manager.select_agent("chat-demo", debug=True)
        agent = self.agent_manager.get_agent()
        self.assertEqual(agent.agent_name, "chat-demo")

    # @patch('src.memory.MemoryAssistant.add_message', new_callable=AsyncMock)
    # async def test_question(self, mock):
    #     agent = self.agent_manager.get_agent()

    #     question = "How many people live in the country? Short answer."
    #     text = await agent.do_chain(question)
    #     self.assertIn("300,000", text, "Number of citizen")

    #     mock.assert_called_once_with(question, text)

    #     text = await agent.do_chain(question + " If you don't know the answer, reply with 'I cannot answer this question", skip_rag=True)
    #     self.assertIn("I cannot answer this question", text, "Number of citizen, without RAG")

    #     question = "What is the name of the country? Short answer."
    #     text = await agent.do_chain(question)
    #     self.assertIn("Aethelland", text, "Name of country")

    #     text = await agent.do_chain(question + " If you don't know the answer, reply with 'I cannot answer this question", skip_rag=True)
    #     self.assertIn("I cannot answer this question", text, "Name of country, without RAG")

    # @patch('src.memory.MemoryAssistant.add_message', new_callable=AsyncMock)
    # async def test_memory(self, mock):
    #     agent = self.agent_manager.get_agent()
    #     agent.memory_strategy = MemoryStrategy.SUMMARY
    #     question = "Are dinosaurs in the country? Short answer."

    #     text = await agent.do_chain(question)
    #     # agent.save_memory()
    #     # stored_memory = agent.load_memory()
    #     # self.assertIn("dinosaurs", stored_memory, "Dinosaurs in country")
    #     # mock.assert_called_once_with(question, text)

if __name__ == '__main__':
    aiounittest.main()