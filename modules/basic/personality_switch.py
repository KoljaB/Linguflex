from core import ActionModule, Request, cfg, log, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from linguflex_functions import LinguFlexBase, linguflex_function
from pydantic import Field
import enum
import json
import os

language = cfg('language')
current_character = cfg('character')

class PersonalitiesList(str, enum.Enum):
    "Enumeration representing the different personalities available to switch to."

def load_enum_from_strings(data):
    enum_class = enum.Enum(
        "PersonalitiesList", 
        {name.replace(" ", "_"): name for name in data}, 
        type=PersonalitiesList
    )
    return enum_class

# current_directory = os.path.dirname(os.path.abspath(__file__))
# file_path = os.path.join(current_directory, f"personalities.{language}.json")
file_path = f"config/personalities.{language}.json"

with open(file_path, "r", encoding='utf-8') as file:
    personalities = json.load(file)

names = [item["name"] for item in personalities]
for name in names:
    if ' ' in name:
        log(DEBUG_LEVEL_ERR, f"  [personality] please remove blank space (\" \") from name \"{name}\" in personalities.{language}.json")
        exit(0)

PersonalitiesEnum = load_enum_from_strings(names)

log(DEBUG_LEVEL_MAX, f"  [personality] available personalities: {str(list(PersonalitiesEnum.__members__.keys()))}")

class switch_personality(LinguFlexBase):
    "Switches to the given personality name"
    personality_name: PersonalitiesEnum = Field(..., description="Name of the personality to switch to")

    def execute(self):
        global current_character
        if self.personality_name.value not in PersonalitiesEnum.__members__:
            return {"error": "Invalid personality name. It must be one of the following: {}".format(list(PersonalitiesEnum.__members__.keys()))}

        current_character = self.personality_name.value
        return {"result": "personality switched successfully", "new personality": current_character}

class AddPersonalityPrompt(ActionModule):
    def handle_input(self, 
            request: Request) -> None: 
        
        request.character = current_character
        for personality in personalities:
            if personality["name"] == current_character:
                request.add_prompt(personality["prompt"])
                break
