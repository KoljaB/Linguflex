import sys
import json
import os
import importlib
import traceback
import pytz
import re
from .linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from .linguflex_texthelper import trim, name_in_json, extract_json 
from .linguflex_interfaces import BaseModule, InputModule, SpeechRecognitionModule, TextToSpeechModule, TextGeneratorModule, ActionModule
from .linguflex_request import Request
from .linguflex_config import parser
from .linguflex_sound import play_sound
from typing import List, Tuple, Dict
from datetime import datetime

# if an action is offered to the llm, whe llm will have access to it for a while
# the number of following request after the llm loses access is defined in ACTION_REQUEST_DECAY
ACTION_REQUEST_DECAY = 4
ACTION_FINAL_TEXT = f'Du kannst nun folgende Aktionen ausführen, indem du JSON-Schlüssel-Wert-Paare ausgibst, keine Erwähnung des JSON in deiner sonstigen Antwort.'
CONFIG_SYSTEM_SECTION = 'system'
CONFIG_SECTION_NOT_FOUND_ERROR_MESSAGE = f'Configuration section for {CONFIG_SYSTEM_SECTION} not found in config file'
CONFIG_PARSING_ERROR_MESSAGE = f'Error parsing configuration for {CONFIG_SYSTEM_SECTION}.'

if not parser().has_section(CONFIG_SYSTEM_SECTION):
    raise ValueError(CONFIG_SECTION_NOT_FOUND_ERROR_MESSAGE)
try:
    language = parser()[CONFIG_SYSTEM_SECTION].get('language', 'en')
    timezone = parser()[CONFIG_SYSTEM_SECTION].get('timezone', 'Europe/Berlin')
    debugfunctions = parser()[CONFIG_SYSTEM_SECTION].getint('debugfunctions', 0)
except Exception as e:
    raise ValueError(CONFIG_PARSING_ERROR_MESSAGE + ' ' + str(e))


functions = []
classes = []
function_calls = {}
class_calls = {}

time_zone = pytz.timezone(timezone)

class InputHandler:
    def __init__(self, special_modules):
        self.special_modules = special_modules

    def create_input(self, request: Request) -> None:
        self.create_audio_input(request)
        if request.audio:
            self.transcribe_audio_input_to_text(request)
        else:
            self.create_text_input(request)        

    def create_audio_input(self, request: Request) -> None:
        for module_instance in self.special_modules[InputModule].values():
            module_instance.create_audio_input(request)
            if request.audio is not None:
                break

    def create_text_input(self, request: Request) -> None:
        for module_instance in self.special_modules[InputModule].values():
            module_instance.create_text_input(request)
            if request.input is not None:
                break

    def transcribe_audio_input_to_text(self, request: Request) -> None:
        if request.audio is not None:
            for module_instance in self.special_modules[SpeechRecognitionModule].values():
                module_instance.transcribe_audio_input_to_text(request)
                if request.input is not None:
                    request.input = trim(request.input)
                    break

class ActionHandler:
    def __init__(self, special_modules):
        self.special_modules = special_modules

    def report_function_execution(self, request: Request, name: str, type: str, return_value) -> None:
        for module_name, module_instance in self.special_modules[ActionModule].items():
            module_instance.on_function_executed(request, name, type, return_value)

    def execute_entity(self, request: Request, entity, entity_type):
        execution_failed = False
        try:
            log(DEBUG_LEVEL_MIN, f'Executing {entity_type} {entity["name"]}')

            play_sound("function_executing")
            if entity_type == 'function':
                entity_return_value = entity["execution"].from_function_call(request.function_call)
            else:
                class_reference = entity["obj"]
                class_instance = class_reference.from_function_call(request.function_call)
                entity_return_value = class_instance.execute()

            log(DEBUG_LEVEL_MAX, f'  {entity["name"]} returned {str(entity_return_value)}')
        except Exception as e:
            error = str(e)
            log(DEBUG_LEVEL_ERR, f'  error occurred executing {entity_type} {entity["name"]}: {error}')
            traceback.print_exc()
            execution_failed = True

        if not execution_failed:
            if entity_return_value is not None:
                play_sound("function_success")
                request_success = request.function_answer(entity["name"], entity_return_value)
            else:
                log(DEBUG_LEVEL_MAX, f'  {entity_type} {entity["name"]} returned None')
                play_sound("function_success")
                request_success = request.function_answer(entity["name"], "success")
            request_success.add_prompt(entity['success_prompt'])
            self.report_function_execution(request, entity["name"], entity_type, entity_return_value)
        else:
            play_sound("function_fail")
            request_fail = request.function_answer(entity["name"], error)                    
            request_fail.add_prompt(entity['fail_prompt'])


    def execute_function(self, request: Request) -> None:
        global functions
        global classes

        for function in functions:
            if function["name"] == request.function_name_execute:
                self.execute_entity(request, function, 'function')

        for lingu_class in classes:
            if lingu_class["name"] == request.function_name_execute:
                self.execute_entity(request, lingu_class, 'class')

        # remove last called function from the offered request.functions list so we never get in infinite call loops
        if request.function_content is not None and request.function_name_answer is not None:
            for function in request.functions:
                if function["name"] == request.function_name_answer:                    
                    request.functions.remove(function)
                    break  # exit the loop once the function is removed

class OutputHandler:
    def __init__(self, all_modules, special_modules):
        self.all_modules = all_modules
        self.special_modules = special_modules
        self.action_handler = ActionHandler(special_modules)

    def create_output(self, request: Request) -> None:
        if request.input and len(request.input) > 0:
            log(DEBUG_LEVEL_MID, f'=>{request.input}')

            if request.function_content is not None:
                play_sound("creating_output")
            else:
                play_sound("creating_output_short")

            for module_instance in self.special_modules[TextGeneratorModule].values():
                module_instance.create_output(request)
                if request.output is not None:
                    break
            request.output = trim(request.output)
            if not request.output is None and len(request.output) > 0:
                log(DEBUG_LEVEL_MID, f'<={request.output}')

    def process_output(self, request: Request) -> None:
        if request.function_name_execute and len(request.function_name_execute) > 0:
            self.action_handler.execute_function(request)

        for module_name, module_instance in self.all_modules.items():
            module_instance.function_execution_completed(request)
            
        if request.output and len(request.output) > 0:
            self.output_reaction(request)
            self.handle_output(request)

            play_sound("before_answer")                
            self.text_to_speech(request)

    def output_reaction(self, request: Request) -> None:
        #request.output_user = trim(request.output_user)
        for module_instance in self.all_modules.values():
            module_instance.output_reaction(request)

    def handle_output(self, request: Request) -> None:
        #request.output_user = trim(request.output_user)
        for module_instance in self.all_modules.values():
            module_instance.handle_output(request)

    def text_to_speech(self, request: Request) -> None:

        # prioritize text to speech module that supports requested voice
        text_to_speech_performed = False
        for text_to_speech_module_name, module_instance in self.special_modules[TextToSpeechModule].items():
            if module_instance.is_voice_available(request):
                text_to_speech_performed = True
                module_instance.perform_text_to_speech(request)
                break

        # found no voice? use first found text to speech module 
        if not text_to_speech_performed:
            for text_to_speech_module_name, module_instance in self.special_modules[TextToSpeechModule].items():
                if hasattr(request, 'tts') and request.tts and request.tts != 'default':
                    if text_to_speech_module_name == request.tts:
                        module_instance.perform_text_to_speech(request)
                        break
                else:
                    module_instance.perform_text_to_speech(request)
                    break
        
class RequestHandler:
    def __init__(self, all_modules, special_modules):
        self.all_modules = all_modules
        self.special_modules = special_modules
        self.input_handler = InputHandler(special_modules)
        self.output_handler = OutputHandler(all_modules, special_modules)

    def process_request(self, request: Request) -> Request:
        self.input_handler.create_input(request)
        #if not request.no_function_adding: self.handle_function_adding(request)
        self.handle_function_adding(request)
        #request.add_prompt(request.prompt_end)
        self.output_handler.create_output(request)
        self.output_handler.process_output(request)
        self.finish_request(request)

        if request.initialize_request:
            new_request = request.initialize_request
            new_request.initialize_request = None
            return new_request
        else:
            return Request()

    def report_add(self, request: Request, name: str, caller_filename: str, type: str, reason: str) -> None:
        log(DEBUG_LEVEL_MAX, f'  {type} {name} added ({reason})')

        for module_name, module_instance in self.special_modules[ActionModule].items():
            module_instance.on_function_added(request, name, caller_filename, type)
            
    def add_function(self, request: Request, function, reason: str) -> None:
        #if function['name'] in request.exclude_actions: return
        request.functions.append(function['schema'])
        request.add_prompt(function['init_prompt'])
        self.report_add(request, function['name'], function['caller_filename'], 'function', reason)

    def add_class(self, request: Request, lingu_class, reason: str) -> None:
        #if lingu_class['name'] in request.exclude_actions: return
        request.functions.append(lingu_class['schema'])
        request.add_prompt(lingu_class['init_prompt'])
        self.report_add(request, lingu_class['name'], lingu_class['caller_filename'], 'class', reason)

    def handle_entity_adding(self, request: Request, entities, entity_calls, add_entity_method, entity_type) -> None:
        input_lower = request.input.lower()
        for entity in entities:
            keywords_in_input = False
            if 'keywords' in entity and entity['keywords'] and len(entity['keywords']) > 0:
                keywords_in_input = [keyword for keyword in entity['keywords'] 
                                    if re.search(r'\b' + keyword.lower().replace('*', '.*') + r'\b', input_lower)]
            else:
                add_entity_method(request, entity, f'always include, no keywords set for {entity_type}')
                continue

            include_all_actions = hasattr(request, 'include_all_actions') and request.include_all_actions
            if keywords_in_input or include_all_actions:
                if include_all_actions:
                    add_entity_method(request, entity, f'forced include of {entity_type}')
                else:
                    add_entity_method(request, entity, f'keywords detected {str(keywords_in_input)} for {entity_type}')
                    entity_calls[entity["name"]] = ACTION_REQUEST_DECAY

            elif entity["name"] in entity_calls and entity_calls[entity["name"]] > 0:
                calls_left = entity_calls[entity["name"]] = entity_calls[entity["name"]] - 1
                add_entity_method(request, entity, f'{calls_left} follow requests for {entity_type}')


    def handle_function_adding(self, request: Request) -> None:
        if request.input and len(request.input) > 0:
            input_lower = request.input.lower()

            for module_name, module_instance in self.all_modules.items():
                module_instance.handle_input(request)

            self.handle_entity_adding(request, functions, function_calls, self.add_function, 'function')
            self.handle_entity_adding(request, classes, class_calls, self.add_class, 'class')

    def finish_request(self, request: Request) -> None:
        for module_instance in self.all_modules.values():
            module_instance.finish_request(request)
        
class AllModulesHandler:
    def __init__(self, all_modules):
        self.all_modules = all_modules

    def cycle(self, request: Request) -> None:
        for module_name, module_instance in self.all_modules.items():
            try:
                module_instance.cycle(request)
            except Exception as e:
                log(DEBUG_LEVEL_MIN, f'Error occurred calling cycle method for module "{module_name}": {str(e)}')

    def shutdown_request(self) -> bool:
        shutdown = False
        for module_name, module_instance in reversed(self.all_modules.items()):
            module_shutdown = module_instance.shutdown_request()
            if module_shutdown is not None:
                if module_shutdown:
                    log(DEBUG_LEVEL_MIN, f'shutdown request from {module_name}')
                    shutdown = True
        return shutdown          
    
    def shutdown(self) -> None:
        log(DEBUG_LEVEL_MIN, '---Server shutdown---')
        for module_name, module_instance in reversed(self.all_modules.items()):
            log(DEBUG_LEVEL_MAX, f'  shutting down {module_name}')
            module_instance.shutdown()
            log(DEBUG_LEVEL_MIN, f'{module_name} down')
        log(DEBUG_LEVEL_MIN, 'lingu byebye')

def process_elements(elements, element_type, language, log_details):
    for element in elements:
        language_file_name = element['caller_filename'] + '.' + language + '.json'

        if log_details:
            log(DEBUG_LEVEL_MID, f"  {element['name']} {element_type}")
            log(DEBUG_LEVEL_MAX, f"    description: {element['description']}")
            log(DEBUG_LEVEL_MAX, f"    module: {element['caller_filename']}")
            log(DEBUG_LEVEL_MAX, f"    schema:")
            log(DEBUG_LEVEL_MAX, f"      {json.dumps(element['schema'], indent=4)}")

        for directory in sys.path:
            potential_path = os.path.join(directory, language_file_name)
            if os.path.isfile(potential_path):
                try:
                    if log_details: log(DEBUG_LEVEL_MAX, f"  language file {language_file_name}:")
                    with open(potential_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if element['name'] in data:
                        for key in ['keywords', 'init_prompt', 'success_prompt', 'fail_prompt']:
                            element[key] = data[element['name']][key]                            
                        if log_details:
                            log(DEBUG_LEVEL_MAX, f"    keywords: {element['keywords']}")
                            log(DEBUG_LEVEL_MAX, f"    init prompt: {element['init_prompt']}")
                            log(DEBUG_LEVEL_MAX, f"    success prompt: {element['success_prompt']}")
                            log(DEBUG_LEVEL_MAX, f"    fail prompt: {element['fail_prompt']}")
                            log(DEBUG_LEVEL_MAX, f"")
                    break            
                except Exception as e:
                    log(DEBUG_LEVEL_ERR, f'  error occurred loading language file {language_file_name} for {element_type} {element["name"]}: {str(e)}')
                    exit(0)   

def log_element_details(elements, element_type, log_details):
    if log_details:
        for element in elements:
            log(DEBUG_LEVEL_MID, f"  {element['name']}")
            log(DEBUG_LEVEL_MAX, f"    {element['description']}")
            
class LinguFlexServer:
    def __init__(self, openai_function_call_module, all_modules, special_modules) -> None:
        global functions
        global classes

        functions = openai_function_call_module.functions 
        classes = openai_function_call_module.classes 
		
        self.special_modules = special_modules
        self.request_handler = RequestHandler(all_modules, special_modules)
        self.all_modules_handler = AllModulesHandler(all_modules)
        self.events = {}

        log_details = debugfunctions >= DEBUG_LEVEL_MIN

        if classes and log_details: 
            log(DEBUG_LEVEL_MIN, f"──classes────────────────────")
            process_elements(classes, "class", language, log_details)

        if functions and log_details: 
            log(DEBUG_LEVEL_MIN, f"──functions──────────────────")
            process_elements(functions, "function", language, log_details)        

        if debugfunctions >= DEBUG_LEVEL_MID:
            log(DEBUG_LEVEL_MIN, f"──list─of─all─actions────────")
            log_element_details(classes, "class", log_details)
            log_element_details(functions, "function", log_details)            

        for module_instance in special_modules[TextGeneratorModule].values():
            module_instance.functions = functions
            module_instance.classes = classes


    def cycle(self, request: Request) -> None:
        self.all_modules_handler.cycle(request)

    def process_request(self, request: Request) -> Request:
        return self.request_handler.process_request(request)

    def shutdown_request(self) -> bool:
        return self.all_modules_handler.shutdown_request()

    def shutdown(self) -> None:
        self.all_modules_handler.shutdown()

    def add_time(self, request: Request) -> None:
        if not hasattr(request, 'local_time_added_to_prompt') or not request.local_time_added_to_prompt:
            local_time = datetime.now(time_zone)
            #request.add_prompt(f"\nLocal time: {local_time.isoformat()}")
            formatted_time = local_time.strftime("%d.%m.%Y %H:%M Uhr")

            if "de" in language:
                request.add_prompt(f"Das aktuelle Datum und die Uhrzeit: {formatted_time}.")
            else:
                request.add_prompt(f"The current date and time: {formatted_time}.")

            request.local_time_added_to_prompt = True        

    def get_time_string(self) -> str:
        cur_date = datetime.now().strftime("%d.%m.%Y")
        cur_time = datetime.now().strftime("%H:%M")
        return f'Das heutige Datum ist {cur_date}, es ist {cur_time} Uhr. '

    def register_event(self, name, function):
        # Registers a function that should be called whenever set_event is called.
        if name not in self.events:
            self.events[name] = []
        self.events[name].append(function)

    def set_event(self, name, data=None):
        if name in self.events:
            for function in self.events[name]:
                if data is None:
                    function()  # Call the function without any arguments
                else:
                    function(data)  # Call the function with provided data