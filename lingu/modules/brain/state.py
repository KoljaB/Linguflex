from lingu import State


class BrainState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "🧠"
        self.model = "gpt-4-turbo-preview"
        self.max_tokens_per_msg = 500
        self.max_messages = 12
        self.history_tokens = 3500


state = BrainState()
