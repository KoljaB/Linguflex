from lingu import State, cfg
import json


language = cfg('language')


class MimicState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "🎭"
        self.chars = []
        self.char_index = -1


state = MimicState()
