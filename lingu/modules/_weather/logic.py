from .handlers.weather_handler import get_weather_data
from lingu import cfg, Logic, repeat
from .state import state


class WeatherLogic(Logic):
    def __init__(self):
        super().__init__()
        self.data = []
        self.default_city = cfg("city", default=None)

    @repeat(60 * 15)
    def repeat_get_weather_data(self):
        self.data, text, info, symbol = get_weather_data(self.default_city)
        state.large_symbol = symbol
        state.bottom_info = info + "°"

    def get_weather(self):
        self.data, text, info, symbol = get_weather_data(self.default_city)
        return self.data


logic = WeatherLogic()
