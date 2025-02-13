"""
Agent-Assembly-Line
"""

import unittest, os
from src.chain import *
import asyncio

class TestChain(unittest.TestCase):

    def test_question_aethelland(self):
        chain = Chain("datasource/aethelland-demo/")

        question = "How many people live in the country? Short answer."
        text = chain.do_chain(question)
        print(question + ":", text)
        self.assertIn("300,000", text, "Number of citizen")

        text = chain.do_chain(question + " If you don't know the answer, reply with 'I cannot answer this question", skip_rag=True)
        print(question + ":", text)
        self.assertIn("I cannot answer this question", text, "Number of citizen, without RAG")

        question = "What is the name of the country? Short answer."
        text = chain.do_chain(question)
        print(question + ":", text)
        self.assertIn("Aethelland", text, "Name of country")

        text = chain.do_chain(question + " If you don't know the answer, reply with 'I cannot answer this question", skip_rag=True)
        print(question + ":", text)
        self.assertIn("I cannot answer this question", text, "Name of country, without RAG")
        chain.cleanup()

if __name__ == '__main__':
    unittest.main()
