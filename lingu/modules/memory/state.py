from lingu import State, cfg
import json


class MemoryState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "💭"

state = MemoryState()
