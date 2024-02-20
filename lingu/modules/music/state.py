from lingu import State


class MusicState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "🎶"


state = MusicState()
