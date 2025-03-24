"""
Agent-Assembly-Line
"""

import os
from agent_assembly_line.config import Config

class LLMFactory:
    @staticmethod
    def create_llm_and_embeddings(config: Config):
        llm_type, model_name = config.llm_type, config.model_name
        if llm_type == "ollama":
            from langchain_ollama.llms import OllamaLLM
            from langchain_ollama.embeddings import OllamaEmbeddings
            # do before first run: llama pull nomic-embed-text
            embeddings = OllamaEmbeddings(model=config.embeddings)
            llm = OllamaLLM(model=model_name, timeout=config.timeout, ollama_keep_alive=config.ollama_keep_alive)
            return llm, embeddings

        elif llm_type == "openai":
            from langchain_openai.llms import OpenAI
            from langchain_openai import ChatOpenAI
            from langchain_openai.embeddings import OpenAIEmbeddings
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found in environment variables")

            if model_name == "gpt-3.5-turbo":
                llm = OpenAI(api_key=api_key, model=config.model_name, timeout=config.timeout)
            else:
                llm = ChatOpenAI(api_key=api_key, model=config.model_name, timeout=config.timeout)
            embeddings = OpenAIEmbeddings(api_key=api_key, model=config.embeddings)
            return llm, embeddings

        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")

    @staticmethod
    def extract_response(response, config: Config):
        # @todo write tests for this function
        if type(response) == dict:
            if config.model_name == "gpt-3.5-turbo":
                return response["choices"][0]["text"]
        if config.model_name == "gpt-4o":
            return response["choices"][0]["text"]
        return response
