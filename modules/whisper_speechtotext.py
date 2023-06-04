import sys
sys.path.insert(0, '..')
import whisper
import torch

from linguflex_interfaces import SpeechRecognitionModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage

set_section('whisper_speechtotext')

try:
    language = cfg[get_section()].get('language', 'de')
    model_size = cfg[get_section()].get('model_size', 'medium')
except Exception as e:
    raise ValueError(configuration_parsing_error_message + ' ' + str(e))

class WhisperASRModule(SpeechRecognitionModule_IF):
    def __init__(self):
        global model_size
        log(DEBUG_LEVEL_MAX, '  [whisper] initializing speech recognition module')
        log(DEBUG_LEVEL_MAX, f'  [whisper] language: {language}')
        whisperdevice = 'cpu'
        if torch.has_cuda:
            log(DEBUG_LEVEL_MAX, '  [whisper] cuda (gpu) used')
            whisperdevice = "cuda"
        else:
            log(DEBUG_LEVEL_MAX, '  [whisper] no cuda (gpu) support found')
        if language == 'en':
            model_size += '.en'                
        log(DEBUG_LEVEL_MAX, '  [whisper] loading model ' + model_size)                
        self.model = whisper.load_model(model_size, whisperdevice)
        log(DEBUG_LEVEL_MID, '  [whisper] ready')                

    def transcribe_audio_input_to_text(self,
            message: LinguFlexMessage):
        log(DEBUG_LEVEL_MAX, '  [whisper] transcribing')                
        result = self.model.transcribe(message.audio, language=language)
        log(DEBUG_LEVEL_MID, '  [whisper] transcribed text:' + result['text']) 
        message.input = result['text']