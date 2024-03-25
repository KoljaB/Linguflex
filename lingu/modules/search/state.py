from lingu import State


class SearchState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "🔍"


state = SearchState()
