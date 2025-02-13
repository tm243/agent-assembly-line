"""
Agent-Assembly-Line
"""

from src.config import Config

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

import asyncio

class Chain():

    local_embeddings = None
    RAG_TEMPLATE = None
    vectorstore = None
    embeddings = None

    def __init__(self, datasource_path):
        config = Config(datasource_path)

        rag_template_file = open(config.prompt_template, "r")
        self.RAG_TEMPLATE = rag_template_file.read()
        rag_template_file.close()

        # do before: llama pull nomic-embed-text
        self.embeddings = OllamaEmbeddings(model=config.embeddings)
        self.vectorstore = self.load_data(config.doc)
        self.model = OllamaLLM(model=config.model_name)

    def cleanup(self):
        self.embeddings._client._client.close()
     
    def load_data(self, doc):
        loader = TextLoader(doc)
        data = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        all_splits = text_splitter.split_documents(data)

        self.vectorstore = Chroma.from_documents(documents=all_splits, embedding=self.embeddings)
        return self.vectorstore


    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def do_chain(self, prompt, skip_rag = False):

        rag_prompt = ChatPromptTemplate.from_template(self.RAG_TEMPLATE)

        """ test without rag, to see the difference """
        if skip_rag:
            response_message = self.model.invoke(prompt)
#            print("Without RAG:")
#            print(response_message)
#            print("---")
            return response_message

        chain = (
            RunnablePassthrough.assign(context=lambda input: Chain.format_docs(input["context"]))
            | rag_prompt
            | self.model
            | StrOutputParser()
        )
        docs = self.vectorstore.similarity_search(prompt, 2)
        text = ""
        try:
            text = chain.invoke({"context": docs, "question": prompt})
        except Exception as e:
            print(e)

        return text
