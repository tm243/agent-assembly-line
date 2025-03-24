"""
Agent-Assembly-Line
"""

from agent_assembly_line.config import Config
from agent_assembly_line.data_loaders.diff_loader import GitDiffLoader
from agent_assembly_line.memory_assistant import MemoryAssistant, MemoryStrategy, NoMemory
from agent_assembly_line.data_loaders.data_loader_factory import DataLoaderFactory
from agent_assembly_line.exceptions import DataLoadError, EmptyDataError
from agent_assembly_line.utils.inspectable_runnable import InspectableRunnable
from agent_assembly_line.data_loaders.web_loader import WebLoader

import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import StrOutputParser

from agent_assembly_line.llm_factory import LLMFactory

class Agent:
    """
    Agent
    This class creates an agent based on the configuration provided in a YAML file or a dictionary.
    The agent can add files, URLs, or inline text to its context and run with a given prompt.

    The agent manages data in three ways:
    1. agent_vectorstore: Loaded from the data specified in the configuration.
    2. user_vectorstore: Stores user-uploaded files and URLs.
    3. inline_context: Stores text or diffs added directly, which will be included in the LLM's context
       in full length, limited by the LLM's maximum input length.

    Files and URLs specified in the configuration are added to the agent's vector store.
    Methods:
    - add_file(): Adds files to the user vector store.
    - add_url(): Adds URLs to the user vector store.
    - add_inline_text(): Adds text directly to the context without using a vector store.
    - add_diff(): Adds a git diff to the inline context.
    """

    user_uploaded_files = []
    user_added_urls = []
    memory_assistant = NoMemory()
    inline_context = ""

    def __init__(self, agent_name = None, debug = False, config = None):
        if agent_name:
            self.agent_name = agent_name
        if not config:
            self.config = Config(agent_name, debug)
        else:
            self.config = config
        if not agent_name:
            self.agent_name = self.config.name
        self.debug_mode = debug
        if self.config.prompt_template:
            with open(self.config.prompt_template, "r") as rag_template_file:
                self.RAG_TEMPLATE = rag_template_file.read()
        if self.config.inline_rag_templates:
            self.RAG_TEMPLATE = self.config.inline_rag_templates

        self.model, self.embeddings = LLMFactory.create_llm_and_embeddings(self.config)

        self.agent_vectorstore = self.load_data(self.config)
        self.user_vectorstore = Chroma("uploaded-data",self.embeddings)
        self.memory_strategy = MemoryStrategy.SUMMARY
        if self.config.use_memory:
            self.memory_assistant = MemoryAssistant(strategy=self.memory_strategy, model=self.model, config=self.config)
            self.memory_assistant.load_messages(self.config.memory_path)
        else:
            self.memory_assistant = NoMemory(config=self.config)
        self.stats = {}

    async def cleanup(self):
        await self.memory_assistant.stopSaving()
        self.memory_assistant.cleanup()
        self.config.cleanup()
        self.user_uploaded_files = []
        self.user_added_urls = []

    def closeModels(self):
        self.model._client._client.close()
        self.embeddings._client._client.close()

    async def aCloseModels(self):
        await self.model._async_client._client.aclose()
        await self.embeddings._async_client._client.aclose()

    def load_data(self, config) -> Chroma:
        source_type, source_path = DataLoaderFactory.guess_source_type(config)
        if source_type and source_path:
            loader = DataLoaderFactory.get_loader(source_type)
            data = loader.load_data(source_path)
            if data:
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                all_splits = text_splitter.split_documents(data)

                self.agent_vectorstore = Chroma.from_documents(documents=all_splits, embedding=self.embeddings)
            else:
                self.agent_vectorstore = Chroma("context", self.embeddings)
            return self.agent_vectorstore
        else:
            return Chroma("context", self.embeddings)

    def add_file(self, upload_directory, filename):
        """
        user uploaded file
        """
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
        finally:
            self.user_uploaded_files.append(filename)

    def add_url(self, url, use_inline_context = False, wait_time=10):
        """
        user added url
        """
        if self.config.debug:
            print(f"Adding URL: {url}")
        try:
            source_type = DataLoaderFactory.guess_url_type(url)
            loader = DataLoaderFactory.get_loader(source_type)
            data = loader.load_data(url, wait_time)

            if self.config.debug:
                with open("website_debug.txt", "w") as f:
                    f.write(loader.plain_text)
                with open("website_links.txt", "w") as f:
                    f.write("\n".join(loader.relevant_links))
                with open("website_h_t_pairs.txt", "w") as f:
                    f.write(loader.header_text_pairs)

            if data:
                if use_inline_context:
                    self.inline_context += data[0].page_content + "\n"
                else:
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                    all_splits = text_splitter.split_documents(data)
                    self.user_vectorstore.add_documents(all_splits)
            else:
                raise EmptyDataError(url)
        except Exception as e:
            print("Adding url failed:", e)
            raise DataLoadError(f"Adding **{url}** of type {source_type} failed: {e}")
        finally:
            summary = self.model.invoke(f"Classify the type of website this text comes from. Be short and definitive in your answer. Do not hedge with phrases like 'appears to be' or 'likely.' State the category clearly (e.g., 'This is a technology news website like Heise Online.'). Here is the text: {data[0].page_content}")
            summary = LLMFactory.extract_response(summary, self.config)
            size = len(data[0].page_content)
            self.user_added_urls.append(url)
            print(f"URL added: {url}, {size} characters")
            return summary, size

    def add_diff(self, diff_text):
        """
        Adds a git diff to the inline context
        """
        loader = GitDiffLoader('.')
        documents = loader.load_data(diff_text)
        if documents:
            try:
                for doc in documents:
                    self.inline_context += doc.page_content + "\n"
            except Exception as e:
                print("Adding diff failed:", e)
                raise DataLoadError(f"Adding diff failed: {e}")

    def add_inline_text(self, text):
        """
        Adds inline text to the inline context.
        Use this to add text directly to the context, doesn't use a vector store.
        """
        self.inline_context += text + "\n"

    def replace_inline_text(self, text):
        """
        Replaces inline text to the inline context.
        Use this to add text directly to the context, doesn't use a vector store.
        """
        self.inline_context = text + "\n"

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    timestamp = datetime.datetime.now()
    def _log_time(self, named=""):
        now = datetime.datetime.now()
        timediff = (now - self.timestamp).total_seconds() * 1000
        if self.debug_mode:
            print(f"Time taken: {timediff:.2f} ms, {named}")
        self.timestamp = now

    def run(self, prompt, skip_rag = False):
        text = self.do_chain(prompt, skip_rag, self.run_callback)
        self._log_time("chain invoked")
        self.memory_assistant.add_message(prompt, text)
        self._log_time("Memory handling, done")
        return text

    def run_callback(self, prompt, chain):
        return chain.invoke(prompt)

    async def stream(self, prompt, skip_rag = False):
        collected_responses = ""
        async for response in self.do_chain(prompt, skip_rag, self.stream_callback):
            collected_responses += response
            yield response
        self._log_time("chain invoked")
        self.memory_assistant.add_message(prompt, collected_responses)
        self._log_time("Memory handling, done")

    async def stream_callback(self, prompt, chain):
        try:
            stream = chain.astream(prompt)
            async for result in stream:
                yield result
        except Exception as e:
            print(e)
        finally:
            stream.aclose()


    def _stats_callback(self, stats):
        if self.debug_mode:
            print(f"Prompt size: {stats['prompt_size']} characters")
        self.stats.update(stats)

    def do_chain(self, prompt, skip_rag = False, callback = None):
        self._log_time("do_chain start")
        rag_prompt = ChatPromptTemplate.from_template(self.RAG_TEMPLATE)
        history = "\n".join([message.content for message in self.memory_assistant.messages]) if self.config.use_memory else ""

        """ test without rag, to see the difference """
        if skip_rag:
            response_message = self.model.invoke(prompt)
#            print("Without RAG:")
#            print(response_message)
#            print("---")
            return response_message
        today = datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
        agent_info = self.config.name + " using " + self.config.model_name

        # @todo: session id to separate conversations
        chain = (
            RunnablePassthrough.assign(
                    global_store=lambda input: Agent.format_docs(input["global_store"]),
                    session_store=lambda input: Agent.format_docs(input["session_store"]),
                    context=lambda input: self.inline_context,
                    history=lambda input: history,
                    today=lambda input: today,
                    agent=lambda input: agent_info
            )
            | rag_prompt
            | InspectableRunnable(statsCallback=self._stats_callback)
            | self.model
            | StrOutputParser()
        )

        max_docs = len(self.agent_vectorstore.get()['documents']) if self.agent_vectorstore.get() else 10
        max_docs = 10 if max_docs > 10 else max_docs
        max_docs = max_docs if max_docs > 0 else 1
        agent_docs = self.agent_vectorstore.similarity_search(prompt, max_docs)

        max_docs = len(self.user_vectorstore.get()['documents']) if self.user_vectorstore.get() else 10
        max_docs = 10 if max_docs > 10 else max_docs
        max_docs = max_docs if max_docs > 0 else 1
        user_docs = self.user_vectorstore.similarity_search(prompt, max_docs)

        self._log_time("search done")
        if self.config.debug:
            print(f"Agent vector store size: {len(self.agent_vectorstore.get()['documents'])}")
            print(f"User vector store size: {len(self.user_vectorstore.get()['documents'])}")
            print(f"Agent docs: {len(agent_docs)}")
            print(f"User docs: {len(user_docs)}")
            print(f"History: {len(history)}")
            print(f"Agent info: {agent_info}")

        try:
            if callback:
                return callback({"global_store": agent_docs, "session_store": user_docs, "question": prompt}, chain)
        except Exception as e:
            print(e)

    def get_summary_memory(self):
        return self.memory_assistant.summary_memory