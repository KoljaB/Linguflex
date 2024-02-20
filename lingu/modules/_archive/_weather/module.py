from lingu import cfg, repeat, log, Level, Populatable, Field 

from .weather_impl import get_weather_data # import our "business logic" (the actual weather implementation)

symbol = "🌤️" # defines our starting module symbol
symbol_y = 2
city = None
default_city = cfg('city', default=None) # retrieve the default city from the config file

@repeat(60 * 15) # repeat every 15 minutes
def update(new_city = default_city):
    global data, text, info, symbol, city
    if not new_city or len(new_city) == 0:
        return None
    city = new_city
    log(Level.Low, f'  [weather] retrieving update for city {new_city}')
    data, text, info, symbol = get_weather_data(new_city)

# define our data module and instruct the AI how to use it
class WeatherForecast(Populatable):
    "Current weather forecast data; ASK FOR CITY (!) if you don't know it"

    # define the fields the AI can use to populate the module
    city: str = Field(default_city, description="City from which the weather gets retrieved; ASK (!) if unknown, DO NOT make it up")

    # the method that gets called after the AI has populated the module
    def on_populated(self):
        global data
        log(Level.Low, f"  [weather] on_populated called")
        if not data or city != self.city:
            log(Level.Low, f"  [weather] no data or new city, calling update()")
            update(self.city)

        log(Level.Low, f"  [weather] on_populated return value: {data}")
        return data