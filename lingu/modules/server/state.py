from lingu import State


class WebserverState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "🌐"


state = WebserverState()
