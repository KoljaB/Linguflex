from lingu import StateBase

class HouseState(StateBase):
    def __init__(self):
        super().__init__()
        self.large_symbol = "🏠"
        # self.large_symbol_offset_x = 0
        # self.large_symbol_offset_y = -4

state = HouseState()