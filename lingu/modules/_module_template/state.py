from lingu import State


class ModuleTemplateState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "🐫"


state = ModuleTemplateState()
