"""
Brain Module

- responsible for switching and configuring LLMs

"""

from lingu import Populatable
from pydantic import Field
from .logic import logic

chars_list = logic.get_char_names()


class switch_char(Populatable):
    "Switches to the given char (personality) name"
    char_name: str = Field(
        None,
        description="Name of the char to switch to. "
                    f"Must be one of these: {chars_list}.")

    def on_populated(self):
        global chars_list
        if self.char_name not in chars_list:
            return {
                "error":
                "Invalid char name. It must be one of the following: "
                f"{chars_list}"
            }

        logic.set_char(self.char_name)
        return {
            "result":
            "char switched successfully",
            "current char name":
            self.char_name
        }



# """
# Brain Module

# - responsible for switching and configuring LLMs

# """

# from lingu import cfg, log, Populatable
# from pydantic import Field
# from .logic import logic
# import enum
# import json

# server = None

# language = cfg('language')
# current_character = cfg('character')


# class CharsList(str, enum.Enum):
#     "Enumeration representing chars (personalities) available to switch to."


# def load_enum_from_strings(data):
#     enum_class = enum.Enum(
#         "CharsEnum",
#         {name.replace(" ", "_"): name for name in data},
#         type=CharsList
#     )
#     return enum_class


# file_path = f"config/personalities.{language}.json"

# with open(file_path, "r", encoding='utf-8') as file:
#     personalities = json.load(file)

# names = [item["name"] for item in personalities]
# for name in names:
#     if ' ' in name:
#         log.dbg("  [mimic] please remove blank space (\" \") from name "
#                 f"\"{name}\" in personalities.{language}.json")
#         exit(0)

# CharsEnum = load_enum_from_strings(names)

# log.dbg("  [mimic] available chars: "
#         f"{str(list(CharsEnum.__members__.keys()))}")
# log.dbg(f"  [mimic] current char is: {current_character}")


# class switch_char(Populatable):
#     "Switches to the given char (personality) name"
#     char_name: CharsEnum = Field(
#         ...,
#         description="Name of the char to switch to")

#     def on_populated(self):
#         global current_character
#         if self.personality_name.value not in CharsEnum.__members__:
#             return {
#                 "error":
#                 "Invalid char name. It must be one of the following: "
#                 f"{list(CharsEnum.__members__.keys())}"
#             }

#         current_character = self.personality_name.value
#         logic.set_character(current_character)
#         return {
#             "result":
#             "personality switched successfully",
#             "new personality":
#             current_character
#         }
