from .handlers.weather_handler import get_weather_data
from lingu import cfg, log, Logic, repeat
from .state import state

api_key = cfg("weather", "api_key", env_key="OPENWEATHERMAP_API_KEY")
no_api_key_msg = \
    "Can't perform that action, OpenWeatherMap API Key is needed."


class WeatherLogic(Logic):
    def init(self):
        if not api_key:
            log.err(
                "[weather] Missing OpenWeatherMap API key.\n"
                "  Create a key at https://openweathermap.org/api.\n"
                "  Write this key into the 'settings.yaml' file or "
                "set 'OPENWEATHERMAP_API_KEY' environment variable."
            )
            self.state.set_disabled(True)
        self.ready()

    def __init__(self):
        super().__init__()
        self.data = []
        self.default_city = cfg("weather", "city", default="")

    @repeat(60 * 15)
    def repeat_get_weather_data(self):
        if state.is_disabled:
            return

        self.data, text, info, symbol = get_weather_data(self.default_city)
        state.large_symbol = symbol
        state.bottom_info = info + "°"

    def get_weather(self, city):
        if not api_key:
            return no_api_key_msg

        self.data, text, info, symbol = get_weather_data(city)
        return self.data

    def get_weather_default_city(self):
        self.data, text, info, symbol = get_weather_data(self.default_city)
        return self.data


logic = WeatherLogic()
