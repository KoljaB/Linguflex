import sys
import json
from datetime import datetime
import os
import importlib
import traceback
import pytz

from .linguflex_log import (
    log,
    DEBUG_LEVEL_OFF,
    DEBUG_LEVEL_MIN,
    DEBUG_LEVEL_MID,
    DEBUG_LEVEL_MAX,
    DEBUG_LEVEL_ERR
)
from .linguflex_texthelper import (
    trim,
    name_in_json,
    extract_json
)
from .linguflex_interfaces import BaseModule, InputModule, SpeechRecognitionModule, TextToSpeechModule, TextGeneratorModule, ActionModule
from .linguflex_request import Request
from typing import List, Tuple, Dict
from .linguflex_config import parser

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

    def perform_module_action(self, request: Request, module_name: str, action_json: str) -> None:
        json_obj = json.loads(action_json)        
        if module_name in request.ignore_actions:
            log(DEBUG_LEVEL_MID,f'  {module_name} ignoring module action')
            return
        for action_provider_module_name, module_instance in self.special_modules[ActionModule].items():
            if module_name == action_provider_module_name:
                for action in module_instance.actions:
                    if 'keys' in action and not action['keys'] is None and len(action['keys']) > 0:
                        if name_in_json(json_obj, action['keys'], True):
                            log(DEBUG_LEVEL_MAX, f'  [{module_name}] found key {action["keys"]} in json {action_json}')
                            module_instance.perform_action(request, json_obj)
                            return
                    else:
                        log(DEBUG_LEVEL_MAX, f'  no action keys defined in [{module_name}]')

    def perform_actions(self, request: Request) -> None:
        for module_name, module_instance in self.special_modules[ActionModule].items():
            for json_obj in request.json_objects:
                for action in module_instance.actions:
                    if 'keys' in action and not action['keys'] is None and len(action['keys']) > 0:
                        if name_in_json(json_obj, action['keys'], True):
                            log(DEBUG_LEVEL_MAX, f'keys match')
                            action_json_string = request.json_strings[request.json_objects.index(json_obj)]
                            self.perform_module_action(request, module_name, action_json_string)
                    else:
                        log(DEBUG_LEVEL_MAX, f'  no action keys defined in [{module_name}]')

    def report_function_execution(self, request: Request, name: str, type: str, return_value) -> None:
        for module_name, module_instance in self.special_modules[ActionModule].items():
            module_instance.on_function_executed(request, name, type, return_value)
         

    def execute_function(self, request: Request) -> None:
        global functions
        global classes

        for function in functions:
            if function["name"] == request.function_name_execute:
                execution_failed = False
                try:
                    log(DEBUG_LEVEL_MIN, f'Executing function {function["name"]}')
                    function_return_value = function["execution"].from_function_call(request.function_call)
                    log(DEBUG_LEVEL_MAX, f'  {function["name"]} returned {str(function_return_value)}')
                except Exception as e:
                    error = str(e)
                    log(DEBUG_LEVEL_ERR, f'  error occurred executing function {function["name"]}: {error}')
                    traceback.print_exc()                    
                    execution_failed = True

                if not execution_failed:
                    if not function_return_value is None:
                        request_success = request.success(function["name"], function_return_value)
                        request_success.prompt = function['success_prompt']
                    else:
                        log(DEBUG_LEVEL_MAX, f'  function {function["name"]} returned None')
                        request_success = request.success(function["name"], "success")
                        request_success.prompt = function['success_prompt']
                    self.report_function_execution(request, function["name"], 'function', function_return_value)
                else:
                    request_fail = request.answer(function["name"], error)                    
                    request_fail.prompt = function['fail_prompt']

        for lingu_class in classes:
            if lingu_class["name"] == request.function_name_execute:
                execution_failed = False
                try:
                    log(DEBUG_LEVEL_MIN, f'Executing class {lingu_class["name"]}')
                    class_reference = lingu_class["obj"]
                    class_instance = class_reference.from_function_call(request.function_call)
                    lingu_class_return_value = class_instance.execute()
                    log(DEBUG_LEVEL_MAX, f'  {lingu_class["name"]} returned {str(lingu_class_return_value)}')
                except Exception as e:
                    error = str(e)
                    log(DEBUG_LEVEL_ERR, f'  error occurred executing class {lingu_class["name"]}: {error}')
                    traceback.print_exc()                    
                    execution_failed = True

                if not execution_failed:
                    if not lingu_class_return_value is None:
                        request_success = request.success(lingu_class["name"], lingu_class_return_value)
                        request_success.prompt = lingu_class['success_prompt']
                    else:
                        log(DEBUG_LEVEL_MAX, f'  class {lingu_class["name"]} returned None')
                        request_success = request.success(lingu_class["name"], "success")
                        request_success.prompt = lingu_class['success_prompt']
                    self.report_function_execution(request, lingu_class["name"], 'class', lingu_class_return_value)
                else:
                    request_fail = request.answer(lingu_class["name"], error)                    
                    request_fail.prompt = lingu_class['fail_prompt']


class OutputHandler:
    def __init__(self, all_modules, special_modules):
        self.all_modules = all_modules
        self.special_modules = special_modules
        self.action_handler = ActionHandler(special_modules)

    def create_output(self, request: Request) -> None:
        if request.input and len(request.input) > 0:
            log(DEBUG_LEVEL_MID, f'=>{request.input}')
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

        if request.output and len(request.output) > 0:
            self.output_reaction(request)
            self.handle_output(request)

            if not request.skip_output:
                self.text_to_speech(request)

    def output_reaction(self, request: Request) -> None:
        request.output_user = trim(request.output_user)
        for module_instance in self.all_modules.values():
            module_instance.output_reaction(request)

    def handle_output(self, request: Request) -> None:
        request.output_user = trim(request.output_user)
        for module_instance in self.all_modules.values():
            module_instance.handle_output(request)

    def text_to_speech(self, request: Request) -> None:

        # prioritize text to speech module that supports requested voice
        text_to_speech_performed = False
        for text_to_speech_module_name, module_instance in self.special_modules[TextToSpeechModule].items():
            if module_instance.is_voice_available(request):
                module_instance.perform_text_to_speech(request)
                text_to_speech_performed = True
                break

        # found no voice? use first found text to speech module 
        if not text_to_speech_performed:
            for text_to_speech_module_name, module_instance in self.special_modules[TextToSpeechModule].items():
                if request.tts and request.tts != 'default':
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
        if not request.no_input_processing: self.process_input(request)
        request.prompt += request.prompt_end
        self.output_handler.create_output(request)
        self.output_handler.process_output(request)
        self.finish_request(request)

        if request.initialize_request:
            new_request = request.initialize_request
            new_request.initialize_request = None
            return new_request
        else:
            return Request()

    def report_add(self, request: Request, name: str, type: str, reason: str) -> None:
        log(DEBUG_LEVEL_MAX, f'  {type} {name} added ({reason})')

        for module_name, module_instance in self.special_modules[ActionModule].items():
            module_instance.on_function_added(request, name, type)
            
    def add_function(self, request: Request, function, reason: str) -> None:
        if function['name'] in request.exclude_actions: return
        request.functions.append(function['schema'])
        request.prompt += function['init_prompt']
        self.report_add(request, function['name'], 'function', reason)

    def add_class(self, request: Request, lingu_class, reason: str) -> None:
        if lingu_class['name'] in request.exclude_actions: return
        request.functions.append(lingu_class['schema'])
        request.prompt += lingu_class['init_prompt']
        self.report_add(request, lingu_class['name'], 'class', reason)

    def process_input(self, request: Request) -> None:
        global functions
        global classes
        global function_calls
        global class_calls

        if request.include_all_actions:
            print (f'include_all_actions: {request.include_all_actions}')

        if request.input and len(request.input) > 0:
            input_lower = request.input.lower()

            # let every module react on input and enrichen both prompt and input
            for module_name, module_instance in self.all_modules.items():
                module_instance.handle_input(request)


            for function in functions:
                reacted_to_keywords = False
                if 'keywords' in function and function['keywords'] and len(function['keywords']) > 0:
                    reacted_to_keywords = [keyword for keyword in function['keywords'] if keyword in input_lower]
                else:
                    self.add_function(request, function, 'always include, no keywords set')
                    continue

                if reacted_to_keywords or request.include_all_actions:
                    if request.include_all_actions:
                        self.add_function(request, function, 'forced include')
                    else:
                        self.add_function(request, function, f'keywords detected {str(reacted_to_keywords)}')
                        function_calls[function["name"]] = ACTION_REQUEST_DECAY

                elif function["name"] in function_calls and function_calls[function["name"]] > 0:
                    calls_left = function_calls[function["name"]] = function_calls[function["name"]] - 1
                    self.add_function(request, function, f'{calls_left} follow requests')

            for lingu_class in classes:
                reacted_to_keywords = False
                if 'keywords' in lingu_class and lingu_class['keywords'] and len(lingu_class['keywords']) > 0:
                    reacted_to_keywords = [keyword for keyword in lingu_class['keywords'] if keyword in input_lower]
                else:
                    self.add_class(request, lingu_class, 'always include, no keywords set')
                    continue

                if reacted_to_keywords or request.include_all_actions:
                    if request.include_all_actions:
                        self.add_class(request, lingu_class, 'forced include')
                        log(DEBUG_LEVEL_MAX, f'  Class {lingu_class["name"]} added (include all actions)')
                    else:
                        self.add_class(request, lingu_class, f'keywords detected {str(reacted_to_keywords)}')
                        class_calls[lingu_class["name"]] = ACTION_REQUEST_DECAY

                elif lingu_class["name"] in class_calls and class_calls[lingu_class["name"]] > 0:
                    calls_left = class_calls[lingu_class["name"]] = class_calls[lingu_class["name"]] - 1
                    self.add_class(request, lingu_class, f'{calls_left} follow requests')


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
        # print("alle module drin, starte server")
        functions = openai_function_call_module.functions 
        classes = openai_function_call_module.classes 
		
        self.special_modules = special_modules
        self.request_handler = RequestHandler(all_modules, special_modules)
        self.all_modules_handler = AllModulesHandler(all_modules)

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
            request.prompt += f"\nLocal time: {local_time.isoformat()}"
            request.local_time_added_to_prompt = True        

    def get_time_string(self) -> str:
        cur_date = datetime.now().strftime("%d.%m.%Y")
        cur_time = datetime.now().strftime("%H:%M")
        return f'Das heutige Datum ist {cur_date}, es ist {cur_time} Uhr. '

    def get_full_action_string(self, request: Request) -> str:
        json_action_row = ''
        for module_name, module_instance in self.special_modules[ActionModule].items():
            for action in module_instance.actions:
                if not action['react_to'] is None and len(action['react_to']) > 0 and 'keys' in action and 'description' in action and 'key_description' in action and 'value_description' in action and 'instructions' in action:
                    json_action_row += ' - {}: Schlüssel {}, Wert {}. {} Beispiel User: \'{}\'. Assistant: \'{}\'\n'.format(action['description'], action['key_description'], action['value_description'], action['instructions'], action['example_user'], action['example_assistant'])
        if not json_action_row is None and len(json_action_row) > 0:
            return json_action_row