from lingu import State


class SeeState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "👁️"


state = SeeState()
