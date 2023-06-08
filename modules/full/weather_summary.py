import sys
sys.path.insert(0, '..')
import os

from linguflex_interfaces import JsonActionProviderModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage
from weather_summary_helper import WeatherManager
from datetime import datetime

set_section('weather_summary')

API_KEY_NOT_FOUND_ERROR_MESSAGE = 'OpenWeatherMap API-Key not found. Please define the key in your linguflex config file or set the key in the environment variable LINGU_OPENWEATHERMAP_API_KEY.'

# Import OpenWeatherMap API-Key from either registry (LINGU_OPENWEATHERMAP_API_KEY) or config file jv_weather/openweathermap_api_key
api_key = os.environ.get('LINGU_OPENWEATHERMAP_API_KEY')
if api_key is None:
    try:
        api_key = cfg[get_section()]['openweathermap_api_key']
    except Exception as e:
        raise ValueError(configuration_parsing_error_message + ' ' + str(e))
if api_key is None:
    raise ValueError(API_KEY_NOT_FOUND_ERROR_MESSAGE)

# Read module configuration
try:
    city = cfg[get_section()].get('default_city', 'Dortmund')
except Exception as e:
    raise ValueError(configuration_parsing_error_message + ' ' + str(e))

prompt = '''
Antworte knapp, NUR AUF DEUTSCH (!) und nur mit dem zur Beantwortung der Frage absolut Notwendigen; \
keine Ausschmückungen; keine näheren Erläuterungen, Erklärungen oder Ratschläge, die nicht erbeten wurden. \
Nutze dazu folgenden Kontext, wenn nötig:

Standort ist {}. {} falls benötigt hier die Wetterdaten als JSON-Objekt (fasse disee Daten für einen Menschen angenehm zusammen; gib keine Nachkommastellen an, runde stattdessen auf ganze Zahlen), als eindimensionales Array, in dem jedes Element ein weiteres Array mit vier Elementen ist. Jedes dieser inneren Arrays repräsentiert einen Wettereintrag und enthält folgende Informationen in dieser Reihenfolge:

Temperatur (in Grad Celsius)
Zeitpunkt (als String im Format "JJJJ-MM-TT hh")
Wetterbeschreibung (als String, z.B. "overcast clouds")
Windgeschwindigkeit (in m/s)

{}

Ganz wichtig: denk daran, NUR DEUTSCH (!) zu antworten und alle englischen Ausdrücke wie few clouds oder clear sky ins deutsche zu übersetzen.
'''

get_weather_action = {
    'react_to': ['wetter', 'sonnig', 'sonne', 'regen', 'regnen', 'spazieren', 'draußen', 'Natur', 'Wolken', 'Gewitter'],
}

class JV_Weather(JsonActionProviderModule_IF):
    def __init__(self) -> None:
        weather = WeatherManager(city, api_key)
        self.actions = [get_weather_action]
        cur_date = datetime.now().strftime("%d.%m.%Y")
        cur_time = datetime.now().strftime("%H:%M")
        time_string = f'Das heutige Datum ist {cur_date}, es ist {cur_time} Uhr.'
        self.weather_string = prompt.format(city, time_string, str(weather.get_simplified_forecast()))

    def on_keywords_in_input(self, 
            message: LinguFlexMessage,
            keywords_in_input: str) -> None: 
         message.prompt += self.weather_string