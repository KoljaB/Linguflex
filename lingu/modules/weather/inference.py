"""
Weather Inference Module

- offers LLMs a way to interact with the weather logic

"""

from lingu import cfg, Populatable
from pydantic import Field
from .logic import logic

default_city = cfg("weather", "city", default="")


class RetrieveWeatherForecast(Populatable):
    """
    Returns current weather forecast data.
    ASK FOR CITY (!) if you don't know it.
    """

    city: str = Field(
        default_city,
        description="City from which the weather gets retrieved. "
                    "ASK (!) if unknown, DO NOT make it up.")

    def on_populated(self):
        return logic.get_weather(self.city)
