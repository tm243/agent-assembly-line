"""
Agent-Assembly-Line
"""
import yaml

class Config:

   def __init__(self, config_file):
      self.load_conf_file(config_file)
   
   def load_conf_file(self, datasource_path):
      if not datasource_path.endswith("/"):
         datasource_path += "/"

      config_file = datasource_path + "/config.yaml"
      with open(config_file, "r") as f:
         config = yaml.safe_load(f)
         self.name            = config["name"]
         self.description     = config["description"]
         self.doc             = datasource_path + config["data"]["file"]
         self.prompt_template = datasource_path + config["prompt"]["template"]
         self.model_name      = config["llm"]["model-name"]
         self.embeddings      = config["llm"]["embeddings"]

