"""
Agent Assembly Line
"""

import datetime as dt
from datetime import datetime
import pytz
from agent_assembly_line.data_loaders.xml_remote_loader import XmlRemoteLoader
from agent_assembly_line.middleware.base_dict_parser import BaseDictParser

WEATHER_PARAMETERS = [
    "temperature",
    "PrecipitationAmount",
    "TotalCloudCover",
    "Humidity",
    "LowCloudCover",
    "MediumCloudCover",
    "Pressure",
    "Cape",
]

class FmiForecastParser(BaseDictParser):
    """
    Weather data fetching and parsing for FMI API.
    """
    def __init__(self, place, forecast_time, timezone="Europe/Helsinki"):
        """
        Initialize the FmiForecastParser with a place, forecast time, and timezone.

        Args:
            place (str): Location for the weather forecast.
            forecast_time (int): Forecast time in hours.
            timezone (str): Timezone for the forecast. Defaults to "Europe/Helsinki".
        """
        if forecast_time <= 0:
            raise ValueError("forecast_time must be a positive integer.")
        self.place = place
        self.forecast_time = forecast_time
        self.local_tz = pytz.timezone(timezone)
        self.start_time = None
        self.end_time = None
        self.url = "https://opendata.fmi.fi/wfs"
        self._set_time_frame()
        self._prepare_params()
        self.loader = XmlRemoteLoader()

    def _set_time_frame(self):
        now = datetime.now(self.local_tz)
        self.start_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.end_time = (now + dt.timedelta(hours=self.forecast_time)).strftime('%Y-%m-%dT%H:%M:%SZ')

        print(f"Time frame: {self.start_time} {self.end_time}, {self.forecast_time} hours")

    def _prepare_params(self):
        self.params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "getFeature",
            "storedquery_id": "fmi::forecast::harmonie::surface::point::timevaluepair",
            "place": self.place,
            "parameters": ",".join(WEATHER_PARAMETERS),
            "starttime": self.start_time,
            "endtime": self.end_time,
        }

    def _parse_weather_data(self, member):
        all_arrays = self._get_all_arrays(member)
        nr_of_data_points = len(all_arrays[0]['om:result']['wml2:MeasurementTimeseries']['wml2:point'])
        combined_data = {}

        for it_data_point in range(nr_of_data_points):
            result_for_time = {}
            time = None
            for array in all_arrays:
                tvp = array['om:result']['wml2:MeasurementTimeseries']['wml2:point'][it_data_point]['wml2:MeasurementTVP']
                time = datetime.strptime(tvp['wml2:time'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M')
                value = tvp['wml2:value']
                feature_name = array['om:result']['wml2:MeasurementTimeseries']['@gml:id'].replace('mts-1-1-', '')
                result_for_time[feature_name] = value

            combined_data[time] = result_for_time

        return combined_data

    def _get_all_arrays(self, member):
        all_arrays = []
        for item in member:
            for key, value in item.items():
                if key == 'omso:PointTimeSeriesObservation':
                    all_arrays.append(value)
        return all_arrays

    @staticmethod
    def get_weather_condition(data):
        precipitation = float(data.get('PrecipitationAmount', 0))
        cloud_cover = float(data.get('TotalCloudCover', 0))

        if precipitation > 10:
            return "Heavy Rain"
        elif precipitation > 2:
            return "Moderate Rain"
        elif precipitation > 0.2:
            return "Light Rain"
        elif precipitation > 0:
            return "Drizzle"
        else:  # No precipitation
            if cloud_cover < 20:
                return "Sunny"
            elif cloud_cover < 60:
                return "Partly Cloudy"
            elif cloud_cover < 90:
                return "Cloudy"
            else:
                return "Overcast"
        return "Unknown"

    @staticmethod
    def translate_value(value, feature_name, wordy=False):
        if feature_name == 'temperature':
            return round(float(value))
        if feature_name in ['PrecipitationAmount', 'TotalCloudCover']:
            return FmiForecastParser.get_weather_condition({feature_name: value})
        return value

    @staticmethod
    def get_unit(value):
        if value == 'temperature':
            return '°C'
        return ''

    def parse(self, raw_dict):
        """
        Implement parse() for the data loader
        Fetch and parse weather data from the FMI API.
        """
        try:
            data = raw_dict
            member = data['wfs:FeatureCollection']['wfs:member']
            weather_data = self._parse_weather_data(member)
            print("Data for", len(weather_data), "hours fetched")
            return weather_data
        except KeyError as e:
            print(f"Missing expected key in raw_dict: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error during parsing: {e}")
            return {}

    def to_human_string(self, weather_data):
        """
        Convert weather data to a string representation.
        """
        result = f"Forecast for {self.place} in {self.forecast_time} hours\n\n"
        for time, data in weather_data.items():
            line = f"{time}:"
            for key, value in data.items():
                line += f" {key}: {FmiForecastParser.translate_value(value, key)} ({value}) {FmiForecastParser.get_unit(key)},"

            result += f"Temperature: {data['temperature']}°C\n"
            result += f"Precipitation: {data['PrecipitationAmount']} mm\n"
            result += f"Cloud cover: {data['TotalCloudCover']}%\n"
            result += f"Estimated weather condition: {FmiForecastParser.get_weather_condition(data)}\n\n"
        return result




