from lingu import State


class SpeechState(State):
    def __init__(self):
        super().__init__()
        self.engine_index = 0
        self.engine_name = "system"
        self.large_symbol = "👄"

        self.azure_api_key = ""
        self.azure_region = ""
        self.elevenlabs_api_key = ""

        self.voices = []
        self.voice_index = -1
        self.voice_test_text = "Hey, isn't this a nice voice?"
        self.coqui_model = "v2.0.2"
        self.rvc_enabled = False
        self.rvc_pitch = 0
        self.rvc_model = ""


state = SpeechState()
