from linguflex_message import LinguFlexMessage

class Module_IF:
    def __init__(self): 
        self.server = None

    def cycle(self, 
            message: LinguFlexMessage) -> None: 
         pass    
    
    def handle_input(self, 
            message: LinguFlexMessage) -> None: 
         pass    
    
    def output_reaction(self, 
            message: LinguFlexMessage) -> None: 
         pass    
    
    def handle_output(self, 
            message: LinguFlexMessage) -> None: 
         pass
   
    def finish_message(self, 
            message: LinguFlexMessage) -> None: 
         pass
    
    def shutdown(self) -> None: 
         pass
    
    def shutdown_request(self) -> None: 
         pass
    
class JsonActionProviderModule_IF(Module_IF):
    def __init__(self): 
        self.actions = []

    def on_keywords_in_input(self, 
            message: LinguFlexMessage,
            keywords_in_input: str) -> None: 
         pass    
    
    def perform_action(self, 
            message: LinguFlexMessage,
            json_obj) -> None:
         pass

class InputProviderModule_IF(Module_IF):
    def create_audio_input(self,
            message: LinguFlexMessage) -> None:
         pass
    
    def create_text_input(self,
            message: LinguFlexMessage) -> None: 
         pass
    
class SpeechRecognitionModule_IF(Module_IF):
    def transcribe_audio_input_to_text(self,
            message: LinguFlexMessage) -> None: 
         pass

class TextToSpeechModule_IF(Module_IF):
    def perform_text_to_speech(self,
            message: LinguFlexMessage) -> None: 
         pass

class LanguageProcessingModule_IF(Module_IF):
    def create_output(self,
            message: LinguFlexMessage) -> None: 
         pass