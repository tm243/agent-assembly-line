"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config
from agent_assembly_line.data_loaders.xml_remote_loader import XmlRemoteLoader
from agent_assembly_line.middleware.fmi_forecast_parser import FmiForecastParser

class FmiWeatherAgent(Agent):
    """
    A small agent specialized in Finnish weather. Chose between local and cloud mode.
    """

    def __init__(self, place = "Helsinki", forecast_hours = 6, mode='local'):
        self.config = Config()
        self.loader = XmlRemoteLoader()

        inline_rag_template = """
        You are a helpful AI weather assistant specialized in telling the forecast.

        ## Instructions:
        - give a textual summary, not just numbers
        - do not write bullet points
        - keep it simple and easy to understand

        ## Context:
        - Today's date: {today}

        {question}

        ## Weather data:
        {context}
        """

        if mode not in ['local', 'cloud']:
            raise ValueError("Invalid mode. Valid options are 'local' or 'cloud'.")

        if mode == 'local':
            model_identifier = "ollama:gemma2:latest"
            embeddings = "nomic-embed-text"
        elif mode == 'cloud':
            model_identifier = "openai:gpt-4o"
            embeddings = "text-embedding-ada-002"
        else:
            raise ValueError("Invalid mode. Choose either 'local' or 'cloud'.")

        self.config.load_conf_dict({
            "name": "weather-demo",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier,
                "embeddings": embeddings
            },
        })
        super().__init__(config=self.config)

        handler = FmiForecastParser(place=place, forecast_time=forecast_hours)
        doc = self.loader.load_data(handler.url, handler.params, parser=handler)

        if not doc or not doc[0].page_content:
            print("Failed to fetch weather data.")
            return

        data = doc[0].page_content

        human_string = handler.to_human_string(data)

        if human_string:
            self.add_inline_text(human_string)
        else:
            print("Failed to fetch weather data.")

    def run(self, prompt="What will the weather be like today?"):
        return super().run(prompt)
