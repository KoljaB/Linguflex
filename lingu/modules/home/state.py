from lingu import cfg, State

class HomeState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "🏠"

state = HomeState()
