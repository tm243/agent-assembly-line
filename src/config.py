"""
Agent-Assembly-Line
"""
import os
import yaml

class Config:

    def __init__(self, agent_name):
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
            self.doc             = datasource_path + config["data"]["file"]
            self.prompt_template = datasource_path + config["prompt"]["template"]
            self.model_name      = config["llm"]["model-name"]
            self.embeddings      = config["llm"]["embeddings"]
            self.memory_prompt   = config["memory-prompt"] if "memory-prompt" in config else ""

