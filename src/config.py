"""
Agent-Assembly-Line
"""

import os
import yaml

class Config:

    doc = ""
    url = ""
    wait_class_name = ""
    prompt_template = ""
    model_name = ""
    model_identifier = ""
    embeddings = ""
    memory_prompt = ""
    debug = False

    def __init__(self, agent_name, debug=False):
        self.debug = debug
        if self.debug:
            print(f"Loading configuration for agent: {agent_name}")
        self.load_conf_file(agent_name)

    def load_conf_file(self, agent_name):
        user_agents_path = os.getenv('USER_AGENTS_PATH', os.path.expanduser(f"~/.local/share/agent-assembly-line/agents/{agent_name}"))
        local_agents_path = os.getenv('LOCAL_AGENTS_PATH', f"agents/{agent_name}")

        if os.path.exists(user_agents_path):
            agents_path = user_agents_path
        elif os.path.exists(local_agents_path):
            agents_path = local_agents_path
        else:
            raise FileNotFoundError(f"Agent configuration not found for: {agent_name}")

        if not agents_path.endswith("/"):
            agents_path += "/"

        config_file = agents_path + "config.yaml"
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            self.name            = config["name"]
            self.description     = config["description"]
            if "file" in config["data"]:
                self.doc         = agents_path + config["data"]["file"]
            if "url" in config["data"]:
                self.url         = config["data"]["url"]
            if "wait-class-name" in config["data"]:
                self.wait_class_name = config["data"]["wait-class-name"]

            self.prompt_template = agents_path + config["prompt"]["template"]
            self.model_name      = config["llm"]["model-name"]
            self.model_identifier = config["llm"]["model-identifier"]
            self.embeddings      = config["llm"]["embeddings"]
            self.memory_prompt   = config["memory-prompt"] if "memory-prompt" in config else "Please summarize the conversation."
            self.use_memory      = config["use-memory"] if "use-memory" in config else False

            # Ollama specifics:
            self.timeout         = config["timeout"] if "timeout" in config else 120
            self.ollama_keep_alive = config["ollama-keep-alive"] if "ollama-keep-alive" in config else False

    @property
    def memory_path(self):
        user_memory_path = os.getenv('USER_MEMORY_PATH', os.path.expanduser(f"~/.local/share/agent-assembly-line/agents/{self.name}/history.json"))
        local_memory_path = os.getenv('LOCAL_MEMORY_PATH', f"agents/{self.name}/history.json")

        if os.path.exists(user_memory_path):
            return user_memory_path
        elif os.path.exists(local_memory_path):
            return local_memory_path
        else:
            # Create the file if it doesn't exist
            os.makedirs(os.path.dirname(user_memory_path), exist_ok=True)
            with open(user_memory_path, 'w') as file:
                file.write('[]')
            return user_memory_path

    def cleanup(self):
        self.doc = None
        self.url = None
        self.wait_class_name = None
        self.prompt_template = None
        self.model_name = None
        self.model_identifier = None
        self.embeddings = None
        self.memory_prompt = None
        self.debug = None
        self.name = None
        self.description = None

