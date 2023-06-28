from typing import List

from .linguflex_request import Request
from .linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR

class BaseModule:
    def __init__(self): 
        self.name = 'Unknown module'
        self.server = None

    def cycle(self, 
            request: Request) -> None: 
         pass    
    
    def handle_input(self, 
            request: Request) -> None: 
         pass    
    
    def output_reaction(self, 
            request: Request) -> None: 
         pass    
    
    def handle_output(self, 
            request: Request) -> None: 
         pass
   
    def finish_request(self, 
            request: Request) -> None: 
         pass
    
    def shutdown(self) -> None: 
         pass
    
    def shutdown_request(self) -> None: 
         pass

class ActionModule(BaseModule):
    def __init__(self): 
        super().__init__()
        self.actions = []

    def on_function_added(self, 
            request: Request,
            name: str,
            type: str) -> None: 
         pass    
    
    def on_function_executed(self, 
            request: Request,
            name: str,
            type: str,
            arguments) -> None: 
         pass    

    def on_keywords_in_input(self, 
            request: Request,
            keywords_in_input: str) -> None: 
         pass    
    
    def perform_action(self, 
            request: Request,
            json_obj) -> None:
         pass
    
    def on_function_called(self, 
            request: Request,
            function_name: str,
            function_arguments) -> None: 
         pass
    
class InputModule(BaseModule):
    def create_audio_input(self,
            request: Request) -> None:
         pass
    
    def create_text_input(self,
            request: Request) -> None: 
         pass
    
class SpeechRecognitionModule(BaseModule):
    def transcribe_audio_input_to_text(self,
            request: Request) -> None: 
         pass

class TextToSpeechModule(BaseModule):
    def perform_text_to_speech(self,
            request: Request) -> None: 
         pass
    def is_voice_available(self,
            request: Request) -> bool: 
         return False

class TextGeneratorModule(BaseModule):
    def create_output(self,
            request: Request) -> None: 
         pass