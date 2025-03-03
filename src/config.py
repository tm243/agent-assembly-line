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
    embeddings = ""
    memory_prompt = ""
    debug = False

    def __init__(self, agent_name, debug=False):
        self.debug = debug
        if self.debug:
            print(f"Loading configuration for agent: {agent_name}")
        self.load_conf_file(agent_name)

    def load_conf_file(self, agent_name):
        user_datasource_path = os.path.expanduser(f"~/.local/share/agent-assembly-line/agents/{agent_name}")
        local_datasource_path = f"datasource/{agent_name}"

        if os.path.exists(user_datasource_path):
            datasource_path = user_datasource_path
        elif os.path.exists(local_datasource_path):
            datasource_path = local_datasource_path
        else:
            raise FileNotFoundError(f"Agent configuration not found for: {agent_name}")

        if not datasource_path.endswith("/"):
            datasource_path += "/"

        config_file = datasource_path + "config.yaml"
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            self.name            = config["name"]
            self.description     = config["description"]
            if "file" in config["data"]:
                self.doc         = datasource_path + config["data"]["file"]
            if "url" in config["data"]:
                self.url         = config["data"]["url"]
            if "wait-class-name" in config["data"]:
                self.wait_class_name = config["data"]["wait-class-name"]

            self.prompt_template = datasource_path + config["prompt"]["template"]
            self.model_name      = config["llm"]["model-name"]
            self.embeddings      = config["llm"]["embeddings"]
            self.memory_prompt   = config["memory-prompt"] if "memory-prompt" in config else ""

    @property
    def memory_path(self):
        user_memory_path = os.path.expanduser(f"~/.local/share/agent-assembly-line/agents/{self.name}/history.json")
        local_memory_path = f"datasource/{self.name}/history.json"

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

