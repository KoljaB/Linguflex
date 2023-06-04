import sys
sys.path.insert(0, '..')
import pyttsx3

from linguflex_interfaces import TextToSpeechModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage
from distutils.command import clean

set_section('system_texttospeech')

try:
    voice = cfg[get_section()].get('voice', 'Microsoft Stefan - German (Germany)')
except Exception as e:
    raise ValueError(configuration_parsing_error_message + ' ' + str(e))
    pass

class TextToSpeechModule_Pyttsx(TextToSpeechModule_IF):
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
            message: LinguFlexMessage) -> None: 
        log(DEBUG_LEVEL_MAX, f'  [pyttsx] speech synthesized for text [{message.output_user}]')
        self.engine.say(message.output_user)
        self.engine.runAndWait()