"""
Agent-Assembly-Line
"""

import os
import yaml
from typing import Optional, Dict, Any

class Config:
    """
    Class to hold the configuration for the agent.
    Configuration can be loaded from a file or a dictionary.
    """

    # data
    doc: str = ""
    url: str = ""
    inline_content: str = ""
    prompt_template: str = ""
    inline_rag_templates: str = ""

    # model
    model_name: str = ""
    model_identifier: str = ""
    embeddings: str = ""

    # memory
    memory_prompt: str = ""

    # misc
    debug: bool = False
    timeout: int = 120
    ollama_keep_alive: bool = False
    llm_type: str = ""

    def __init__(self, load_agent_conf: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None, debug: bool = False):
        self.debug = debug
        if load_agent_conf:
            if self.debug:
                print(f"Loading configuration for agent: {load_agent_conf}")
            self.load_conf_file(load_agent_conf)
        elif config_dict:
            if self.debug:
                print("Loading configuration from dictionary")
            self.load_conf_dict(config_dict)

    def load_conf_file(self, agent_name: str):
        agents_path = self._get_agents_path(agent_name)
        config_file = os.path.join(agents_path, "config.yaml")
        
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        
        self._validate_config(config)
        self._update_config(config, agents_path)

    def load_conf_dict(self, config: Dict[str, Any]):
        self._validate_config(config)
        self._update_config(config)

    def _update_config(self, config: Dict[str, Any], agents_path: Optional[str] = None):
        self.name = config["name"]
        self.description = config.get("description", "")
        if "data" in config.keys():
            self.doc = os.path.join(agents_path, config.get("data", {}).get("file", "")) if agents_path else config.get("data", {}).get("file", "")
            self.url = config.get("data", {}).get("url", "")
            self.inline_content = config.get("data", {}).get("inline", "")
        self.prompt_template = os.path.join(agents_path, config.get("prompt", {}).get("template", "")) if agents_path else config.get("prompt", {}).get("template", "")
        self.inline_rag_templates = config.get("prompt", {}).get("inline_rag_templates", "")  # Set inline RAG templates from prompt section
        self.model_identifier = config["llm"]["model-identifier"]
        self.embeddings = config["llm"]["embeddings"]
        self.memory_prompt = config.get("memory-prompt", "Please summarize the conversation.")
        self.use_memory = config.get("use-memory", False)
        self.timeout = config.get("timeout", 120)
        self.ollama_keep_alive = config.get("ollama-keep-alive", False)

        self.llm_type, self.model_name = Config.parse_model_identifier(self.model_identifier)

    def _get_agents_path(self, agent_name: str) -> str:
        user_agents_path = os.getenv('USER_AGENTS_PATH', os.path.expanduser(f"~/.local/share/agent-assembly-line/agents/{agent_name}"))
        local_agents_path = os.getenv('LOCAL_AGENTS_PATH', f"agents/{agent_name}")

        local_agents_path = os.path.join(os.path.dirname(__file__), local_agents_path)

        if os.path.exists(user_agents_path):
            return user_agents_path
        elif os.path.exists(local_agents_path):
            return local_agents_path
        else:
            raise FileNotFoundError(f"Agent configuration not found for: {agent_name}")

    def _validate_config(self, config: dict):
        required_fields = {
            "name": str,
            "prompt": dict,
            "llm": dict
        }
        for field, field_type in required_fields.items():
            if field not in config or not isinstance(config[field], field_type):
                raise ValueError(f"Missing or invalid required field: {field}")

    @staticmethod
    def parse_model_identifier(model_identifier: str):
        """
        Schema: ollama:gemma2:latest, openai:gpt-3.5-turbo
        """
        parts = model_identifier.split(":")
        if len(parts) < 2:
            raise ValueError(f"Invalid LLM specification: {model_identifier}")
        llm_type = parts[0]
        model_name = ":".join(parts[1:])
        return llm_type, model_name

    @property
    def memory_path(self) -> str:
        """
        Get the path to the memory/history file for the agent.
        @todo standardize memory vs history terminology
        """
        user_memory_path = os.getenv('USER_MEMORY_PATH', os.path.expanduser(f"~/.local/share/agent-assembly-line/agents/{self.name}/history.json"))
        local_memory_path = os.getenv('LOCAL_MEMORY_PATH', f"agents/{self.name}/history.json")

        if os.path.exists(user_memory_path):
            return user_memory_path
        elif os.path.exists(local_memory_path):
            return local_memory_path
        else:
            os.makedirs(os.path.dirname(user_memory_path), exist_ok=True)
            with open(user_memory_path, 'w') as file:
                file.write('[]')
            return user_memory_path

    def cleanup(self):
        self.doc = None
        self.url = None
        self.inline_content = None
        self.inline_rag_templates = None
        self.prompt_template = None
        self.model_name = None
        self.model_identifier = None
        self.embeddings = None
        self.memory_prompt = None
        self.debug = None
        self.name = None
        self.description = None

