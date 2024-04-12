from lingu import State


class InterpreterState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "🖥️"


state = InterpreterState()
