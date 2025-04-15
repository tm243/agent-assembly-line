"""
Agent-Assembly-Line
"""

import os
from agent_assembly_line.config import Config

_llm_embeddings_mapping = {
    "ollama": {
        "gemma2": {
            "llm": "gemma2",
            "embeddings": "nomic-embed-text"
        },
        "gemma3": {
            "llm": "gemma3",
            "embeddings": "nomic-embed-text"
        }
    },
    "openai": {
        "gpt-3.5-turbo": {
            "llm": "gpt-3.5-turbo",
            "embeddings": "text-embedding-ada-002"
        },
        "gpt-4o": {
            "llm": "gpt-4o",
            "embeddings": "text-embedding-ada-002"
        }
    },
    # Add more mappings as needed
}

class LLMFactory:
    @staticmethod
    def create_llm_and_embeddings(config: Config):
        llm_type, model_name = config.llm_type, config.model_name
        if llm_type == "ollama":
            from langchain_ollama.llms import OllamaLLM
            from langchain_ollama.embeddings import OllamaEmbeddings
            # do before first run: ollama pull nomic-embed-text
            embeddings = ( config.custom_embeddings or 
                          _llm_embeddings_mapping.get("ollama", {}).get(model_name, {}).get("embeddings", "nomic-embed-text") )
            embeddings = OllamaEmbeddings(model=embeddings)
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

        elif llm_type == "runpod":
            from langchain_runpod.llms import RunpodLLM
            from langchain_runpod.embeddings import RunpodEmbeddings
            api_key = os.getenv("RUNPOD_API_KEY")
            if not api_key:
                raise ValueError("Runpod API key not found in environment variables")

            # Extract the endpoint from the model_name (e.g., "runpod:my_serverless_endpoint")
            if not model_name.startswith("runpod:"):
                raise ValueError("Runpod model_name must start with 'runpod:'")
            endpoint = model_name.split("runpod:")[1]

            llm = RunpodLLM(api_key=api_key, endpoint=endpoint, timeout=config.timeout)
            embeddings = RunpodEmbeddings(api_key=api_key, model=config.embeddings)
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
