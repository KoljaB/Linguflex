from core import TextToSpeechModule, Request, cfg, log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from distutils.command import clean
import pyttsx3

voice = cfg('voice')

class TextToSpeech_System(TextToSpeechModule):
    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        installed_voices = self.engine.getProperty('voices')
        log(DEBUG_LEVEL_MAX, f'  [pyttsx] available voices:')
        for installed_voice in installed_voices:
            log(DEBUG_LEVEL_MAX, f'    [pyttsx] {installed_voice.name}')
        if not voice is None:
            log(DEBUG_LEVEL_MAX, f'  [pyttsx] voice set to {voice}')
            self.engine.setProperty('voice', voice)

    def perform_text_to_speech(self, 
            request: Request) -> None: 
        log(DEBUG_LEVEL_MAX, f'  [pyttsx] speech synthesized for text [{request.output_user}]')
        self.engine.say(request.output_user)
        self.engine.runAndWait()