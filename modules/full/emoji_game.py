from linguflex_functions import LinguFlexBase
from pydantic import Field

class start_emoji_game(LinguFlexBase):
    "Starts a game: randomly select a movie, book or series. Don't mention the name. Select emojis that are related to this work. Present the emojis."
    name: str = Field(..., description="Name of the movie, book or series; DO NOT MENTION IN YOUR OUTPUT")
    emojis: str = Field(..., description="Emojis describing the movie, book or series concisely. The emojis 🎬, 📖, or 📺 are not allowed, as well as multiple use of the same emoji. Visualize essential features of the work, such as a main character, a central object, or a main location. Take into account the chronological order of the emojis.")

    def execute(self):
        return f"Your output answer should contain only the emojis {self.emojis}, DO NOT MENTION THE NAME."