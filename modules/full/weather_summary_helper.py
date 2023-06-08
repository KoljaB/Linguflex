import json
import requests
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from datetime import datetime, timedelta

class WeatherManager:
    """
    Eine Klasse, um Wettervorhersagedaten von OpenWeatherMap abzurufen und 
    die Daten zu vereinfachen, um sie leichter lesbar und verständlich zu machen.
    """

    def __init__(self, city, api_key):
        self.city = city
        self.api_key = api_key

    def get_weather_data(self):
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={self.city}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        return data

    def simplify_and_convert_json(self, json_obj):
        simplified_list = []
        current_time = datetime.utcnow()
        time_limit = current_time + timedelta(hours=72)

        for item in json_obj["list"]:
            item_time = datetime.utcfromtimestamp(item["dt"])

            if item_time <= time_limit:
                compact_entry = [
                    item["main"]["temp"],
                    #item_time.strftime('%Y-%m-%d %Hh'),
                    item_time.strftime('%d.%m.%Y %H Uhr'),
                    item["weather"][0]["description"],
                    item["wind"]["speed"]
                ]
                simplified_list.append(compact_entry)
            else:
                break

        return simplified_list

    def get_simplified_forecast(self):
        log(DEBUG_LEVEL_MAX, '  [weather] calling openweathermap api')                
        raw_data = self.get_weather_data()
        log(DEBUG_LEVEL_MAX, '  [weather] parsing')                
        simplified_forecast = self.simplify_and_convert_json(raw_data)
        log(DEBUG_LEVEL_MID, '  [weather] data ready')                
        return simplified_forecast