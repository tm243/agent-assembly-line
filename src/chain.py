"""
Agent-Assembly-Line
"""

from src.config import Config
from src.memory import *
from src.data_loaders.data_loader_factory import DataLoaderFactory

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

class Chain():

    local_embeddings = None
    RAG_TEMPLATE = None
    vectorstore = None
    embeddings = None
    memory_strategy = MemoryStrategy.NO_MEMORY

    def __init__(self, agent_name):
        config = Config(agent_name)
        self.config = config

        with open(config.prompt_template, "r") as rag_template_file:
            self.RAG_TEMPLATE = rag_template_file.read()

        # do before: llama pull nomic-embed-text
        self.embeddings = OllamaEmbeddings(model=config.embeddings)
        self.vectorstore = self.load_data(config)
        self.model = OllamaLLM(model=config.model_name)
        self.summary_memory = ConversationSummaryMemory(llm=self.model, human_prefix="User", ai_prefix="Agent", return_messages=True)
        self.buffer_memory = ConversationBufferMemory()
        self.memory_strategy = MemoryStrategy.SUMMARY
        self.memory_assistant = MemoryAssistant(strategy=self.memory_strategy, model=self.model, config=config)

    def cleanup(self):
        self.embeddings._client._client.close()

    def load_data(self, config) -> Chroma:
        source_type, source_path = DataLoaderFactory.guess_source_type(config)
        loader = DataLoaderFactory.get_loader(source_type)
        data = loader.load_data(source_path)

        if data:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            all_splits = text_splitter.split_documents(data)

            self.vectorstore = Chroma.from_documents(documents=all_splits, embedding=self.embeddings)
            return self.vectorstore
        else:
            print("Config:", self.config.doc, self.config.url)
            raise ValueError("No data loaded")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def do_chain(self, prompt, skip_rag = False):

        rag_prompt = ChatPromptTemplate.from_template(self.RAG_TEMPLATE)
        messages = self.buffer_memory.load_memory_variables({})

        """ test without rag, to see the difference """
        if skip_rag:
            response_message = self.model.invoke(prompt)
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
                    history=lambda input: messages["history"],
                    today=lambda input: today,
                    agent=lambda input: agent_info
            )
            | rag_prompt
            | self.model
            | StrOutputParser()
        )

        docs = self.vectorstore.similarity_search(prompt, 10)

        text = ""
        try:
            text = chain.invoke({"context": docs, "question": prompt})
        except Exception as e:
            print(e)

        self.memory_assistant.add_message(prompt, text)
        self.buffer_memory.save_context({"question": prompt}, {"answer": text})
        self.summary_memory.save_context({"input": prompt}, {"output": text})

        return text

    def save_memory(self):
        with open("memory_summary.txt", "w") as f:
            sm = self.summary_memory.load_memory_variables({})["history"]
            for s in sm:
                f.write(s.content)

    def load_memory(self):
        with open("memory_summary.txt", "r") as f:
            return f.read()

    def get_summary_memory(self):
        return self.memory_assistant.summary_memory