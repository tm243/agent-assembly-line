"""
Agent-Assembly-Line
"""

import unittest, asyncio, aiounittest
from src.chain import *
from src.memory import *
from unittest.mock import AsyncMock, patch, Mock

class TestChain(aiounittest.AsyncTestCase):

    @patch('src.memory.MemoryAssistant.add_message', new_callable=AsyncMock)
    async def test_question_aethelland(self, mock):

        chain = Chain("aethelland-demo")

        question = "How many people live in the country? Short answer."
        text = await chain.do_chain(question)
        self.assertIn("300,000", text, "Number of citizen")

        mock.assert_called_once_with(question, text)

        text = await chain.do_chain(question + " If you don't know the answer, reply with 'I cannot answer this question", skip_rag=True)
        self.assertIn("I cannot answer this question", text, "Number of citizen, without RAG")

        question = "What is the name of the country? Short answer."
        text = await chain.do_chain(question)
        self.assertIn("Aethelland", text, "Name of country")

        text = await chain.do_chain(question + " If you don't know the answer, reply with 'I cannot answer this question", skip_rag=True)
        self.assertIn("I cannot answer this question", text, "Name of country, without RAG")

        chain.cleanup()

    @patch('src.memory.MemoryAssistant.add_message', new_callable=AsyncMock)
    async def test_memory(self, mock):

        chain = Chain("aethelland-demo")
        chain.memory_strategy = MemoryStrategy.SUMMARY
        question = "Are dinosaurs in the country? Short answer."

        # temp. disabled:
        text = await chain.do_chain(question)
        # chain.save_memory()
        # stored_memory = chain.load_memory()
        # self.assertIn("dinosaurs", stored_memory, "Dinosaurs in country")
        # mock.assert_called_once_with(question, text)

        chain.cleanup()

if __name__ == '__main__':
    unittest.main()
