from lingu import State


class CalendarState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "📆"


state = CalendarState()
