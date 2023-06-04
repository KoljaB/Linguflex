import json

from linguflex_log import (
    log,
    DEBUG_LEVEL_OFF,
    DEBUG_LEVEL_MIN,
    DEBUG_LEVEL_MID,
    DEBUG_LEVEL_MAX,
)
from linguflex_texthelper import (
    trim,
    name_in_json,
    extract_json
)
from linguflex_interfaces import (
    Module_IF,
    InputProviderModule_IF,
    SpeechRecognitionModule_IF,
    TextToSpeechModule_IF,
    LanguageProcessingModule_IF,
    JsonActionProviderModule_IF,
)
from linguflex_message import LinguFlexMessage
from typing import List, Tuple, Dict

ACTION_FINAL_TEXT = f'Du kannst nun folgende Aktionen ausführen, indem du JSON-Schlüssel-Wert-Paare ausgibst, keine Erwähnung des JSON in deiner sonstigen Antwort.'

class InputHandler:
    def __init__(self, special_modules):
        self.special_modules = special_modules

    def create_input(self, message: LinguFlexMessage) -> None:
        self.create_audio_input(message)
        if message.audio:
            self.transcribe_audio_input_to_text(message)
        else:
            self.create_text_input(message)        

    def create_audio_input(self, message: LinguFlexMessage) -> None:
        for module_instance in self.special_modules[InputProviderModule_IF].values():
            module_instance.create_audio_input(message)
            if message.audio is not None:
                break

    def create_text_input(self, message: LinguFlexMessage) -> None:
        for module_instance in self.special_modules[InputProviderModule_IF].values():
            module_instance.create_text_input(message)
            if message.input is not None:
                break

    def transcribe_audio_input_to_text(self, message: LinguFlexMessage) -> None:
        if message.audio is not None:
            for module_instance in self.special_modules[SpeechRecognitionModule_IF].values():
                module_instance.transcribe_audio_input_to_text(message)
                if message.input is not None:
                    message.input = trim(message.input)
                    break

class ActionHandler:
    def __init__(self, special_modules):
        self.special_modules = special_modules

    def perform_module_action(self, message: LinguFlexMessage, module_name: str, action_json: str) -> None:
        json_obj = json.loads(action_json)        
        if module_name in message.ignore_actions:
            log(DEBUG_LEVEL_MID,f'  {module_name} ignoring module action')
            return
        for action_provider_module_name, module_instance in self.special_modules[JsonActionProviderModule_IF].items():
            if module_name == action_provider_module_name:
                for action in module_instance.actions:
                    if 'keys' in action and not action['keys'] is None and len(action['keys']) > 0:
                        if name_in_json(json_obj, action['keys'], True):
                            log(DEBUG_LEVEL_MAX, f'  [{module_name}] found key {action["keys"]} in json {action_json}')
                            module_instance.perform_action(message, json_obj)
                            return
                    else:
                        log(DEBUG_LEVEL_MAX, f'  no action keys defined in [{module_name}]')

    def perform_actions(self, message: LinguFlexMessage) -> None:
        for module_name, module_instance in self.special_modules[JsonActionProviderModule_IF].items():
            for json_obj in message.json_objects:
                for action in module_instance.actions:
                    if 'keys' in action and not action['keys'] is None and len(action['keys']) > 0:
                        if name_in_json(json_obj, action['keys'], True):
                            log(DEBUG_LEVEL_MAX, f'keys match')
                            action_json_string = message.json_strings[message.json_objects.index(json_obj)]
                            self.perform_module_action(message, module_name, action_json_string)
                    else:
                        log(DEBUG_LEVEL_MAX, f'  no action keys defined in [{module_name}]')

    def get_full_action_string(self, message: LinguFlexMessage) -> str:
        json_action_row = ''
        for module_name, module_instance in self.special_modules[JsonActionProviderModule_IF].items():
            for action in module_instance.actions:
                if not action['react_to'] is None and len(action['react_to']) > 0 and 'keys' in action and 'description' in action and 'key_description' in action and 'value_description' in action and 'instructions' in action:
                    json_action_row += ' - {}: Schlüssel {}, Wert {}. {} Beispiel User: \'{}\'. Assistant: \'{}\'\n'.format(action['description'], action['key_description'], action['value_description'], action['instructions'], action['example_user'], action['example_assistant'])
        if not json_action_row is None and len(json_action_row) > 0:
            return '\n' + ACTION_FINAL_TEXT + '\n' + json_action_row

class OutputHandler:
    def __init__(self, all_modules, special_modules):
        self.all_modules = all_modules
        self.special_modules = special_modules
        self.action_handler = ActionHandler(special_modules)

    def create_output(self, message: LinguFlexMessage) -> None:
        if message.input and len(message.input) > 0:
            log(DEBUG_LEVEL_MIN, f'=>{message.input}')
            for module_instance in self.special_modules[LanguageProcessingModule_IF].values():
                module_instance.create_output(message)
                if message.output is not None:
                    break
            message.output = trim(message.output)
            if not message.output is None and len(message.output) > 0:
                log(DEBUG_LEVEL_MIN, f'<={message.output}')

    def process_output(self, message: LinguFlexMessage) -> None:
        if message.output and len(message.output) > 0:
            extract_json(message)
            self.action_handler.perform_actions(message)
            self.output_reaction(message)
            self.handle_output(message)

            if not message.skip_output:
                self.text_to_speech(message)

    def output_reaction(self, message: LinguFlexMessage) -> None:
        message.output_user = trim(message.output_user)
        for module_instance in self.all_modules.values():
            module_instance.output_reaction(message)

    def handle_output(self, message: LinguFlexMessage) -> None:
        message.output_user = trim(message.output_user)
        for module_instance in self.all_modules.values():
            module_instance.handle_output(message)

    def text_to_speech(self, message: LinguFlexMessage) -> None:
        for text_to_speech_module_name, module_instance in self.special_modules[TextToSpeechModule_IF].items():
            if message.tts and message.tts != 'default':
                if text_to_speech_module_name == message.tts:
                    module_instance.perform_text_to_speech(message)
            else:
                module_instance.perform_text_to_speech(message)

class MessageHandler:
    def __init__(self, all_modules, special_modules):
        self.all_modules = all_modules
        self.special_modules = special_modules
        self.input_handler = InputHandler(special_modules)
        self.output_handler = OutputHandler(all_modules, special_modules)

    def process_message(self, message: LinguFlexMessage) -> LinguFlexMessage:
        self.input_handler.create_input(message)
        self.process_input(message)
        self.output_handler.create_output(message)
        self.output_handler.process_output(message)
        self.finish_message(message)

        if message.initialize_message:
            new_message = message.initialize_message
            new_message.initialize_message = None
            return new_message
        else:
            return LinguFlexMessage()

    def process_input(self, message: LinguFlexMessage) -> None:
        if message.input and len(message.input) > 0:
            input_lower = message.input.lower()
            # let every module react on input and enrichen both prompt and input
            for module_name, module_instance in self.all_modules.items():
                module_instance.handle_input(message)
            # let action module react on keyword in input events
            for module_name, module_instance in self.special_modules[JsonActionProviderModule_IF].items():
                for action in module_instance.actions:                    
                    if not action['react_to'] is None and len(action['react_to']) > 0:
                        reacted_to_keywords = [keyword for keyword in action['react_to'] if keyword in input_lower]
                        if reacted_to_keywords:
                            module_instance.on_keywords_in_input(message, reacted_to_keywords)
            # further enrichen prompt with json
            json_action_row = ''
            for module_name, module_instance in self.special_modules[JsonActionProviderModule_IF].items():
                for action in module_instance.actions:
                    if not action['react_to'] is None and len(action['react_to']) > 0 and 'keys' in action and 'description' in action and 'key_description' in action and 'value_description' in action and 'instructions' in action:
                        found_keywords = [keyword for keyword in action['react_to'] if keyword in input_lower]
                        if found_keywords or module_name in message.raise_actions:
                            if module_name in message.ignore_actions:
                                log(DEBUG_LEVEL_MID,f'  {module_name} ignoring module action')
                            else:
                                if found_keywords:
                                    log(DEBUG_LEVEL_MAX, f'  [{module_name}] allows action "{action["description"]}" ({found_keywords} detected)')
                                else:
                                    log(DEBUG_LEVEL_MAX, f'  [{module_name}] allows action "{action["description"]}" (action raise requested)')
                                json_action_row += ' - {}: Schlüssel {}, Wert {}. {} Beispiel User: \'{}\'. Assistant: \'{}\'\n'.format(action['description'], action['key_description'], action['value_description'], action['instructions'], action['example_user'], action['example_assistant'])
                                #json_action_row += ' - {}: Schlüssel {}, Wert {}. {} Beispiel User: \'{}\'.  Assistant: \'{}\''.format(action['description'], action['key_description'], action['value_description'], action['instructions'], action['example_user'], action['example_assistant'])
            if not json_action_row is None and len(json_action_row) > 0:
                message.prompt += '\n' + ACTION_FINAL_TEXT + '\n' + json_action_row
            message.prompt += message.prompt_end

    def finish_message(self, message: LinguFlexMessage) -> None:
        if message.output and len(message.output) > 0:        
            for module_instance in self.all_modules.values():
                module_instance.finish_message(message)
        
class AllModulesHandler:
    def __init__(self, all_modules):
        self.all_modules = all_modules

    def cycle(self, message: LinguFlexMessage) -> None:
        for module_name, module_instance in self.all_modules.items():
            try:
                module_instance.cycle(message)
            except Exception as e:
                log(DEBUG_LEVEL_MIN, f'Error occurred calling cycle method for module "{module_name}": {str(e)}')

    def shutdown_request(self) -> bool:
        shutdown = False
        for module_name, module_instance in self.all_modules.items():
            module_shutdown = module_instance.shutdown_request()
            if module_shutdown is not None:
                if module_shutdown:
                    log(DEBUG_LEVEL_MIN, f'shutdown request from {module_name}')
                    shutdown = True
        return shutdown          
    
    def shutdown(self) -> None:
        log(DEBUG_LEVEL_MIN, '---Server shutdown---')
        for module_name, module_instance in self.all_modules.items():
            log(DEBUG_LEVEL_MAX, f'  shutting down {module_name}')
            module_instance.shutdown()
            log(DEBUG_LEVEL_MIN, f'{module_name} down')
        log(DEBUG_LEVEL_MIN, 'lingu byebye')

class LinguFlexServer:
    def __init__(self, all_modules, special_modules) -> None:
        self.message_handler = MessageHandler(all_modules, special_modules)
        self.all_modules_handler = AllModulesHandler(all_modules)

    def cycle(self, message: LinguFlexMessage) -> None:
        self.all_modules_handler.cycle(message)

    def process_message(self, message: LinguFlexMessage) -> LinguFlexMessage:
        return self.message_handler.process_message(message)

    def shutdown_request(self) -> bool:
        return self.all_modules_handler.shutdown_request()

    def shutdown(self) -> None:
        self.all_modules_handler.shutdown()