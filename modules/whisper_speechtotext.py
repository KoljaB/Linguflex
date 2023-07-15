from core import SpeechRecognitionModule, Request, cfg, log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
import whisper
import torch

language = cfg('language')
model_size = cfg('model_size')

class SpeechToText_Whisper(SpeechRecognitionModule):
    def __init__(self):
        global model_size
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

    def transcribe_audio_input_to_text(self, request: Request):
        log(DEBUG_LEVEL_MAX, '  [whisper] transcribing')                
        result = self.model.transcribe(request.audio, language=language)
        log(DEBUG_LEVEL_MID, '  [whisper] transcribed text:' + result['text']) 
        request.input = result['text']

# Size	Parameters	English-only    Multilingual 	Required VRAM	Relative speed
# tiny	39 M	    tiny.en	        tiny	        ~1 GB	        ~32x
# base	74 M	    base.en     	base	        ~1 GB	        ~16x
# small	244 M	    small.en	    small	        ~2 GB	        ~6x
# medium769 M	    medium.en	    medium	        ~5 GB	        ~2x
# large	1550 M	    N/A	            large	        ~10 GB          1x