"""
Open Interpreter Module

- lets LLMs run code on your computer to complete tasks

"""

from lingu import log, Populatable
from pydantic import Field
from .logic import logic


class RunComputerInterpreterCommand(Populatable):
    """
    Provides a natural-language interface to the computer's general-purpose capabilities:
    - create and edit photos, videos, PDFs
    - perform research
    - plot, clean, and analyze large datasets

    Lets you run code on the users local computer using natural language.
    Retrieves real-time information about current events from the internet.
    Uses google search api.
    """
    interpreter_command: str = Field(
        ...,
        description="Command to run on the computer. Example: What operating system are we on?")

    def on_populated(self):
        return logic.process_interpreter_command(
            self.interpreter_command)
