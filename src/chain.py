"""
Agent-Assembly-Line
"""

from src.config import Config
from src.memory import *
from src.data_loaders.data_loader_factory import DataLoaderFactory
from src.exceptions import DataLoadError, EmptyDataError

import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import StrOutputParser

class Chain:
    def __init__(self, agent_name, debug = False):
        self.agent_name = agent_name
        config = Config(agent_name, debug)
        self.config = config
        self.debug_mode = debug

        with open(config.prompt_template, "r") as rag_template_file:
            self.RAG_TEMPLATE = rag_template_file.read()

        # do before: llama pull nomic-embed-text
        self.embeddings = OllamaEmbeddings(model=config.embeddings)
        self.agent_vectorstore = self.load_data(config)
        self.user_vectorstore = Chroma("uploaded-data",self.embeddings)
        self.model = OllamaLLM(model=config.model_name, timeout=120, ollama_keep_alive=True)
        self.memory_strategy = MemoryStrategy.SUMMARY
        self.memory_assistant = MemoryAssistant(strategy=self.memory_strategy, model=self.model, config=config)
        self.memory_assistant.load_messages(self.config.memory_path)

    def cleanup(self):
        self.embeddings._client._client.close()

    def load_data(self, config) -> Chroma:
        source_type, source_path = DataLoaderFactory.guess_source_type(config)
        loader = DataLoaderFactory.get_loader(source_type)
        data = loader.load_data(source_path)

        if data:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            all_splits = text_splitter.split_documents(data)

            self.agent_vectorstore = Chroma.from_documents(documents=all_splits, embedding=self.embeddings)
        else:
            self.agent_vectorstore = Chroma("context", self.embeddings)
        return self.agent_vectorstore

    def add_data(self, upload_directory, filename):
        try:
            filepath = os.path.join(upload_directory, filename)
            source_type = DataLoaderFactory.guess_file_type(filepath)
            loader = DataLoaderFactory.get_loader(source_type)
            data = loader.load_data(filepath)
            if data:
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                all_splits = text_splitter.split_documents(data)
                self.user_vectorstore.add_documents(all_splits)
                total_text_length = sum(len(doc.page_content) for doc in all_splits)
                return total_text_length
            else:
                raise EmptyDataError(filename)
        except Exception as e:
            print("Adding user data failed:", e)
            raise DataLoadError(f"Adding **{filename}** of type {source_type} failed: {e}")

    def add_url(self, url):
        try:
            from src.data_loaders.web_loader import WebLoader
            source_type = DataLoaderFactory.guess_url_type(url)
            loader = DataLoaderFactory.get_loader(source_type)
            data = loader.load_data(url)
            if data:
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                all_splits = text_splitter.split_documents(data)
                self.user_vectorstore.add_documents(all_splits)
                total_text_length = sum(len(doc.page_content) for doc in all_splits)
                return total_text_length
            else:
                raise EmptyDataError(url)
        except Exception as e:
            print("Adding url failed:", e)
            raise DataLoadError(f"Adding **{url}** of type {source_type} failed: {e}")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    timestamp = datetime.datetime.now()
    def _log_time(self, named=""):
        now = datetime.datetime.now()
        timediff = (now - self.timestamp).total_seconds() * 1000
        if self.debug_mode:
            print(f"Time taken: {timediff:.2f} ms, {named}")
        self.timestamp = now

    async def do_chain(self, prompt, skip_rag = False):
        self._log_time("do_chain start")
        rag_prompt = ChatPromptTemplate.from_template(self.RAG_TEMPLATE)
        history = "\n".join([message.content for message in self.memory_assistant.messages])

        """ test without rag, to see the difference """
        if skip_rag:
            response_message = await self.model.ainvoke(prompt)
#            print("Without RAG:")
#            print(response_message)
#            print("---")
            return response_message
        today = datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
        agent_info = self.config.name

        # @todo: session id to separate conversations
        chain = (
            RunnablePassthrough.assign(
                    context=lambda input: Chain.format_docs(input["context"]),
                    uploaded_data=lambda input: Chain.format_docs(input["uploaded_data"]),
                    history=lambda input: history,
                    today=lambda input: today,
                    agent=lambda input: agent_info
            )
            | rag_prompt
            | self.model
            | StrOutputParser()
        )

        agent_docs = self.agent_vectorstore.similarity_search(prompt, 10)
        user_docs = self.user_vectorstore.similarity_search(prompt, 10)
        self._log_time("search done")

        text = ""
        try:
            text = await chain.ainvoke({"context": agent_docs, "uploaded_data": user_docs, "question": prompt})
        except Exception as e:
            print(e)
        self._log_time("chain invoked")

        await self.memory_assistant.add_message(prompt, text)
        self._log_time("Memory handling, done")

        return text

    def get_summary_memory(self):
        return self.memory_assistant.summary_memory