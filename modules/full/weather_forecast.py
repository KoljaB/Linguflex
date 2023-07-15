from core import cfg, log, DEBUG_LEVEL_MAX
from linguflex_functions import linguflex_function, LinguFlexBase, tokens_function, max_tokens_answer, max_tokens_result
from datetime import datetime, timedelta
from pydantic import Field
import requests

api_key = cfg('api_key', env_key='OPENWEATHERMAP_API_KEY')
default_city = cfg('city')

def wind_speed_to_description(wind_speed):
    if wind_speed < 10:
        return 'Calm Breeze'
    elif wind_speed < 20:
        return 'Gentle Breeze'
    elif wind_speed < 30:
        return 'Light Winds'
    elif wind_speed < 40:
        return 'Moderate Winds'
    elif wind_speed < 50:
        return 'Fresh Breeze'
    elif wind_speed < 60:
        return 'Strong Breeze'
    elif wind_speed < 70:
        return 'Near Gale'
    elif wind_speed < 80:
        return 'Gale Winds'
    elif wind_speed < 90:
        return 'Severe Gale'
    elif wind_speed < 100:
        return 'Storm Winds'
    elif wind_speed < 110:
        return 'Violent Storm'
    elif wind_speed < 120:
        return 'Hurricane Winds'
    else:
        return 'Extreme Hurricane'
    
@tokens_function(50)
@max_tokens_answer(200)
@max_tokens_result(1200)
class retrieve_weather_forecast(LinguFlexBase):
    "Returns current weather forecast data; ASK FOR CITY (!) if you don't know it"

    city: str = Field(default_city, description="City from which the weather gets retrieved; ASK (!) if unknown, DO NOT make it up")


    def execute(self):
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={self.city}&appid={api_key}&units=metric"
        log(DEBUG_LEVEL_MAX, f"  [weather] calling api endpoint {url}")

        json_weather_data = requests.get(url).json()

        datapoints = []
        if "list" in json_weather_data: 
            for item in json_weather_data["list"]:
                item_time = datetime.utcfromtimestamp(item["dt"])
                if item_time <= datetime.utcnow() + timedelta(hours=72):
                    temp = int(item['main']['temp'])
                    wind_speed = int(item["wind"]["speed"])
                    wind = wind_speed_to_description(wind_speed)
                    datapoints.append({
                        'time' : item_time.strftime('%d.%m.%Y %H Uhr'),
                        'temp' : temp,
                        'weather' : item["weather"][0]["description"],
                        'wind' : wind,
                    })
                else: break
        return {
            "result" : "success",
            "city" : self.city,
            "raw_weather_data" : datapoints
        }