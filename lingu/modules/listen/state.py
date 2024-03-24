from lingu import State


class ListenState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "👂"
        self.large_symbol_offset_x = 1
        self.large_symbol_offset_y = 1
        self.wake_word_activation_delay = 40
        self.end_of_speech_silence = 0.7
        self.is_muted = False
        self.language = "en"
        self.interrupt_thresh = 20000


state = ListenState()
