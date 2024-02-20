from core import Populatable, Field

symbol = "🌍"

class GetRandomAnimalFact(Populatable):
    "Call immediately when any animal comes up."

    random_animal_fact : str = Field(None, description="An interesting, funny or otherwise entertaining fact about a random animal.")