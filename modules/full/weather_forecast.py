from core import cfg, log, DEBUG_LEVEL_MAX
from linguflex_functions import linguflex_function, LinguFlexBase
from datetime import datetime, timedelta
from pydantic import Field
import requests

api_key = cfg('api_key', 'LINGU_OPENWEATHERMAP_API_KEY')
default_city = cfg('city')

class retrieve_weather_forecast(LinguFlexBase):
    "Returns current weather forecast data; ASK FOR CITY (!) if you don't know it"

    city: str = Field(default=default_city, description="City from which the weather gets retrieved; ASK (!) if unknown, DO NOT make it up")

    def execute(self):
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={self.city}&appid={api_key}&units=metric"
        log(DEBUG_LEVEL_MAX, f"  [weather] calling api endpoint {url}")

        json_weather_data = requests.get(url).json()

        datapoints = []
        if "list" in json_weather_data: 
            for item in json_weather_data["list"]:
                item_time = datetime.utcfromtimestamp(item["dt"])
                if item_time <= datetime.utcnow() + timedelta(hours=72):
                    datapoints.append({
                        'time' : item_time.strftime('%d.%m.%Y %H Uhr'),
                        'temp' : item['main']['temp'],
                        'weather' : item["weather"][0]["description"],
                        'wind' : item["wind"]["speed"],
                    })
                else: break
        return datapoints