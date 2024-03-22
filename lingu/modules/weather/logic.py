from .handlers.weather_handler import get_weather_data
from lingu import cfg, log, Logic, repeat
from .state import state

api_key = cfg("weather", "api_key", env_key="OPENWEATHERMAP_API_KEY")


class WeatherLogic(Logic):
    def init(self):
        if not api_key:
            log.err(
                "[weather] Missing OpenWeatherMap API key.\n"
                "  Please open the 'settings.yaml' file and "
                "provide the API key.")
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
        self.data, text, info, symbol = get_weather_data(city)
        return self.data

    def get_weather_default_city(self):
        self.data, text, info, symbol = get_weather_data(self.default_city)
        return self.data


logic = WeatherLogic()
