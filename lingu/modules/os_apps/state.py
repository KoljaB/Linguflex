from lingu import State


class OS_Apps_State(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "🔧" # 🛠️🔨⚙️


state = OS_Apps_State()
