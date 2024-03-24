from lingu import State


class HouseState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "🏠"


state = HouseState()
