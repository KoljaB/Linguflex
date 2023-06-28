from .linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR

DEFAULT_USER = 'DefaultUser'

class Request():
    def __init__(self) -> None:        
        self.functions = [] # functions sent to openai function call api
        self.function_call = None 
        self.function_name_execute = None 
        self.function_name_answer = None
        self.function_arguments = None
        self.function_content = None

        self.audio = None # path to audio data
        self.include_all_actions = False # set to true if the model should be offered all available actions
        self.exclude_actions = ''
        self.input = None # input text
        self.original_input = None # needed to smuggle through user input in chained messages by modules
        self.no_input_processing = False # request from module to not process next input (LinguFlexMessages raised by modules would not want this)
        self.skip_input = False 
        self.user_id = DEFAULT_USER # user identification for client-individual history etc
        self.prompt = '' # system prompt to instruct llm
        self.llm = '' # preferred llm model to use
        self.prompt_end = '' # information to add at last
        self.ignore_actions = '' # modules to ignore action
        self.character = ''
        self.ignore_character_prompt = False
        self.clone_last_user_input = False
        # self.no_history_input = False
        # self.no_history_output = False
        self.raise_actions = '' # modules to allow actions for llm        
        self.output = None # raw llm output text
        self.output_user = None # output optimized for user
        self.original_output = None # needed to smuggle through assistant output in chained messages by modules
        self.original_output_user = None # needed to smuggle through assistant output in chained messages by modules
        self.no_input_to_history = False # set to true if the user input should not be written to the conversation history 
        self.no_output_to_history = False # set to true if the llm output should not be written to the conversation history 
        self.skip_output = False # request from module to not communicate answer to user
        self.history = '' # conversation history
        self.tts = None # preferred tts
        self.json_strings = [] # detected json string in llm output
        self.json_objects = [] # converted json objects
        self.initialize_request = None # request to raise after processing this one
        self.return_value_success = False

    def new(self, prompt = '', input = ''): 
        request = Request()
        request.tts = self.tts
        request.user_id = self.user_id

        request.input = input or self.input
        request.prompt = prompt or self.prompt
        request.no_history = True
        request.ignore_actions = 'auto_action'
        request.original_input = self.input
        request.original_output = self.output
        request.original_output_user = self.output_user
        request.no_input_to_history = True
        # try:
        #     request.raise_actions = self.name
        # except AttributeError as e:
        #     log(DEBUG_LEVEL_ERR, f'  module has no name defined, please check if super().__init__() was called within the module constructor') 
        #     raise e
             
        request.skip_input = True
        self.initialize_request = request
        return request

    def answer(self, function_name: str, function_content: str): 
        request = self.new()
        request.function_name_answer = function_name
        request.function_content = function_content
        return request     

    def success(self, function_name: str, function_content: str):
        request = self.answer(function_name, function_content)
        request.return_value_success = True
        return request

    def llm_only(self, prompt = '', input = ''):
        request.ignore_actions = ''
        request = self.create(prompt, input)
        request.no_output_to_history = True
        request.no_input_processing = True
        return request

