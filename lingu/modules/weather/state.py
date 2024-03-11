from lingu import State


class WeatherState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "🌤️"


state = WeatherState()
