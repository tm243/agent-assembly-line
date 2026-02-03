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
    "anthropic": {
        "claude-3-5-sonnet": {
            "llm": "claude-3-5-sonnet-20241022",
            "embeddings": "text-embedding-ada-002"  # Use OpenAI for embeddings
        },
        "claude-3-5-haiku": {
            "llm": "claude-3-5-haiku-20241022",
            "embeddings": "text-embedding-ada-002"
        },
        "claude-3-opus": {
            "llm": "claude-3-opus-20240229",
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
                raise ValueError("OPENAI_API_KEY not found in environment variables.")

            if model_name == "gpt-3.5-turbo":
                llm = OpenAI(api_key=api_key, model=config.model_name, timeout=config.timeout)
            else:
                llm = ChatOpenAI(api_key=api_key, model=config.model_name, timeout=config.timeout)
            embeddings = ( config.custom_embeddings or
                          _llm_embeddings_mapping.get("openai", {}).get(model_name, {}).get("embeddings", "text-embedding-ada-002") )
            embeddings = OpenAIEmbeddings(api_key=api_key, model=embeddings)
            return llm, embeddings

        elif llm_type == "anthropic":
            from langchain_anthropic import ChatAnthropic
            from langchain_openai.embeddings import OpenAIEmbeddings
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")
            
            # Map short names to full model IDs
            model_mapping = {
                "claude-3-5-sonnet": "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku": "claude-3-5-haiku-20241022",
                "claude-3-opus": "claude-3-opus-20240229",
                "claude-3-sonnet": "claude-3-sonnet-20240229",
                "claude-3-haiku": "claude-3-haiku-20240307",
            }
            
            full_model_name = model_mapping.get(model_name, model_name)
            
            llm = ChatAnthropic(
                api_key=api_key,
                model=full_model_name,
                timeout=config.timeout,
                max_tokens=config.max_tokens if hasattr(config, 'max_tokens') else 4096
            )
            
            # Anthropic doesn't provide embeddings, so use OpenAI or custom
            openai_key = os.getenv("OPENAI_API_KEY")
            if config.custom_embeddings:
                embeddings_model = config.custom_embeddings
            else:
                embeddings_model = _llm_embeddings_mapping.get("anthropic", {}).get(model_name, {}).get("embeddings", "text-embedding-ada-002")
            
            if openai_key:
                embeddings = OpenAIEmbeddings(api_key=openai_key, model=embeddings_model)
            else:
                # Fallback to Ollama embeddings if available
                try:
                    from langchain_ollama.embeddings import OllamaEmbeddings
                    embeddings = OllamaEmbeddings(model="nomic-embed-text")
                except ImportError:
                    raise ValueError(
                        "Anthropic does not provide embeddings. "
                        "Please set OPENAI_API_KEY for OpenAI embeddings or install langchain_ollama."
                    )
            
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
        # Handle Anthropic response format
        if hasattr(response, 'content'):
            return response.content
        return response
