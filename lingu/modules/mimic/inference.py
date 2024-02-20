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


