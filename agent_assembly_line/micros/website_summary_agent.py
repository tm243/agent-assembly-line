"""
Agent-Assembly-Line
"""

import re
from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class WebsiteSummaryAgent(Agent):
    """
    A small agent specialized in summarizing a website. Chose between local and cloud mode.
    """

    purpose = "Summarizes a given website into a concise summary. Use this agent if the user  contains a link, http, https, url."

    def __init__(self, prompt, mode='local'):
        self.config = Config()

        url = self._extract_url(prompt)
        self.add_inline_text(prompt)

        inline_rag_template = """
        You are an AI assistant specialized in summarizing websites.

        ## Instructions:
        - ignore website header, language choices, footer, impressum, etc.
        - do not include phrases like "That's an interesting article" or any subjective commentary
        - start directly with the factual summary without any introductory phrases
        - maintain a neutral, objective tone throughout the summary
        - avoid using evaluative language (interesting, great, exciting, etc.)
        - list the main points in bullet points

        ## Context:
        - Today's date: {today}

        {question}

        ## Text:
        {context}
        """

        if mode == 'local':
            model_identifier = "ollama:gemma2:latest"
        elif mode == 'cloud':
            model_identifier = "openai:gpt-4o"
        else:
            raise ValueError("Invalid mode. Choose either 'local' or 'cloud'.")

        self.config.load_conf_dict({
            "name": "website-summary-agent",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier
            },
        })
        super().__init__(config=self.config)
        self.add_url(url, use_inline_context=True)

    def run(self, prompt="Summarize the following text from the website in 6-8 sentences, capturing the main idea and key details."):
        return super().run(prompt)

    def _extract_url(self, prompt):
        """
        Extracts the URL from the given prompt.
        """
        url_pattern = r'(https?://[^\s]+)'
        match = re.search(url_pattern, prompt)
        if match:
            return match.group(0)
        else:
            raise ValueError("No valid URL found in the prompt.")