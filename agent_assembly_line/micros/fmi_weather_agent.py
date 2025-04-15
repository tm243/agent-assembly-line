"""
Agent-Assembly-Line
"""

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config
from agent_assembly_line.data_loaders.xml_remote_loader import XmlRemoteLoader
from agent_assembly_line.middleware.fmi_forecast_parser import FmiForecastParser
from datetime import datetime

class FmiWeatherAgent(Agent):
    """
    A small agent specialized in Finnish weather. Chose between local and cloud mode.
    """

    purpose = "Provides weather forecasts for Finland, specifically Helsinki."

    def __init__(self, prompt="Helsinki", forecast_hours=24, mode='local'):
        self.config = Config()
        self.loader = XmlRemoteLoader()

        inline_rag_template = """
        You are a helpful AI weather assistant specialized in telling the forecast.

        ## Instructions:
        Give a precise and accurate weather forecast for the next hours.

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
        elif mode == 'cloud':
            model_identifier = "openai:gpt-4o"

        self.config.load_conf_dict({
            "name": "weather-agent",
            "prompt": { "inline_rag_templates": inline_rag_template },
            "llm": {
                "model-identifier": model_identifier
            },
        })
        super().__init__(config=self.config)

        place = self._extract_city_name_with_llm(prompt)

        handler = FmiForecastParser(place=place, forecast_time=forecast_hours)
        doc = self.loader.load_data(handler.url, handler.params, parser=handler)

        if not doc or not doc[0].page_content:
            print("Failed to fetch weather data.")
            return

        data = doc[0].page_content

        human_string = handler.to_human_string(data)

        if human_string:
            self.add_inline_text(f"\n\The weather service says: {human_string}")
        else:
            print("Failed to fetch weather data.")

    important_city_names = [
        "Helsinki", "Espoo", "Vantaa", "Tampere", "Oulu", "Turku", "Jyväskylä",
        "Lahti", "Kuopio", "Pori", "Lappeenranta", "Joensuu", "Rovaniemi",
        "Vaasa", "Kotka", "Jyvaskyla", "Hämeenlinna", "Seinäjoki", "Kouvola", "Salo",
        "Porvoo", "Nurmijärvi", "Rauma", "Järvenpää", "Kerava", "Ylöjärvi",
        "Lohja", "Kokkola", "Raisio", "Tampereen", "Kemi", "Mikkeli",
        "Tornio", "Savonlinna", "Kouvola", "Hyvinkää", "Rovaniemi",
        "Kajaani", "Iisalmi", "Imatra", "Kangasala", "Päijät-Häme",
        "Lapinlahti", "Ruokolahti", "Suonenjoki", "Kemiönsaari", "Salla",
        "Ruokolahti", "Kuhmo", "Lieksa", "Ylivieska", "Salla",
        "Rautavaara", "Ruokolahti", "Salla", "Kuhmo", "Lieksa",
        "Ylivieska", "Salla", "Rautavaara", "Ruokolahti", "Kuhmo",
        "Lieksa", "Ylivieska", "Salla", "Rautavaara", "Ruokolahti",
        "Kuhmo", "Lieksa", "Ylivieska", "Salla", "Rautavaara", "Inari"
    ]

    def _extract_city_name_with_llm(self, prompt):
        """
        Uses an LLM to extract the city name or place from the given prompt.
        """

        extraction_prompt = f"""
        Extract the name of the city or place mentioned in the following text.
        If no city or place is mentioned, return "Helsinki".

        Only return the name of the city or place, without any additional text.

        If the name of the city is misspelled, correct it.
        If the name of the city is not in Finnish, translate it to Finnish.

        Text: "{prompt}"
        """

        # This saves us a roundtrip to the model
        for city in self.important_city_names:
            if city.lower() in prompt.lower():
                return city

        # Otherwise we use the LLM to extract the city name (and correct it)
        response = super().run(extraction_prompt)
        city_name = response.strip().replace("**", "").replace('"', '').replace("'", "").strip()
        if not city_name:
            return "Helsinki"
        return city_name

    def run(self, prompt="What will the weather be like?"):
        result = super().run(prompt).strip()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = f"{result} timestamp: {current_time}"
        return result
