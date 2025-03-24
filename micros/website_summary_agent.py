"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class WebsiteSummaryAgent(Agent):
    """
    A small agent specialized in summarizing a website. Chose between local and cloud mode.
    """

    def __init__(self, url, mode='local'):
        self.config = Config()

        inline_rag_template = """
        You are a helpful AI assistant specialized in summarizing websites.

        ## Instructions:
        - ignore website header, language choices, footer, impressum, etc.

        ## Context:
        - Today's date: {today}

        {question}

        ## Text:
        {context}
        """

        if mode == 'local':
            model_identifier = "ollama:gemma2:latest"
            embeddings = "nomic-embed-text"
        elif mode == 'cloud':
            model_identifier = "openai:gpt-4o"
            embeddings = "text-embedding-ada-002"
        else:
            raise ValueError("Invalid mode. Choose either 'local' or 'cloud'.")

        self.config.load_conf_dict({
            "name": "diff-demo",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier,
                "embeddings": embeddings
            },
        })
        super().__init__(config=self.config)
        self.add_url(url, use_inline_context=True)

    def run(self, prompt="Summarize the following text from the website in 6-8 sentences, capturing the main idea and key details."):
        return super().run(prompt)
