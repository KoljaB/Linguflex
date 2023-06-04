import sys
sys.path.insert(0, '..')
import os
import openai

# TBD: add max_tokens, improve temperature

from linguflex_interfaces import LanguageProcessingModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage

set_section('openai_generator')

API_KEY_NOT_FOUND_ERROR_MESSAGE = 'OpenAI API-Key not found. Please define the key in your linguflex config file or set the key in the environment variable LINGU_OPENAI_API_KEY.'

# Import OpenAI API-Key from either registry (LINGU_OPENAI_API_KEY) or config file llm_openai_chat/openai_api_key
api_key = os.environ.get('LINGU_OPENAI_API_KEY')
if api_key is None:
    try:
        api_key = cfg[get_section()]['openai_api_key']
    except Exception as e:
        raise ValueError(configuration_parsing_error_message + ' ' + str(e))
if api_key is None:
    raise ValueError(API_KEY_NOT_FOUND_ERROR_MESSAGE)
openai.api_key = api_key

# Read module configuration
try:
    history_max_entries = cfg[get_section()].getint('history_max_entries', 2)
    history_max_chars_per_message = cfg[get_section()].getint('history_max_chars_per_message', 500)
    history_max_chars_total = cfg[get_section()].getint('history_max_chars_total', 2000)
    gpt_model = cfg[get_section()].get('gpt_model', 'gpt-3.5-turbo')
    gpt_init_prompt = cfg[get_section()].get('init_prompt', 'Du bist ein hilfreicher Assistent, antworte kurz und präzise auf Fragen und Aufgaben.')
    llm_temperature = cfg[get_section()].getfloat('default_temperature', 0.5)
    error_output = cfg[get_section()].get('api_error_message', 'Fehler beim Aufruf der GPT API.')
except Exception as e:
    raise ValueError(configuration_parsing_error_message + ' ' + str(e))

class LangchainSimpleModule(LanguageProcessingModule_IF):
    def __init__(self) -> None: 
     # contains the full complete history for each user
        self.history = {}
        # contains the trimmed part of history we send to llm for each user
        self.limited_history = {}
        # self.last_user_input = {'role':'user', 'content': ''}

    def create_output(self,
            message: LinguFlexMessage) -> None: 
        
        llm_model = gpt_model if len(message.llm) == 0 else message.llm


        # if message.clone_last_user_input:
        #     log(DEBUG_LEVEL_MAX, '  [openai] clone content {} from last user input {}'.format(str(self.last_user_input), self.last_user_input['content']))
        #     message.input += self.last_user_input['content']
        user_input = {'role':'user', 'content': message.input}
        #self.last_user_input = user_input

        user_input_limited = {'role':'user', 'content': self.limit_string(message.input, history_max_chars_per_message)}

        # Fetch the user's history, or initialize it if it doesn't exist yet
        if message.user_id not in self.history:
            self.history[message.user_id] = []
            self.limited_history[message.user_id] = []            

        llm_history = self.limited_history[message.user_id][:]

        if not message.input == ' ':
            llm_history.append(user_input)            
            self.history[message.user_id].append(user_input_limited)
            self.limited_history[message.user_id].append(user_input_limited)


        # prepare llm_messages object for llm containing prompt and chat history including current request
        if not gpt_init_prompt is None and len(gpt_init_prompt) > 0:
            gpt_prompt = gpt_init_prompt + ' ' + message.prompt
        else:
            gpt_prompt = message.prompt
        llm_messages = []
        if not gpt_prompt is None and len(gpt_prompt) > 0:
            llm_messages.append({'role':'system','content': gpt_prompt})
        while len(str(llm_history)) > history_max_chars_total and len(llm_history) > 1:
            llm_history.pop(0)
            llm_history.pop(0)

        if not message.no_history:
            llm_messages.extend(llm_history) 
        else:
            llm_messages.append(user_input)

        # Call llm completion api
        try:
            log(DEBUG_LEVEL_MAX, '  [openai] model {}: '.format(llm_model) + str(llm_messages))
            completion = openai.ChatCompletion.create(model=llm_model, messages=llm_messages, temperature=llm_temperature)
            output = completion['choices'][0]['message']['content']
            if message.remove_from_history:
                if len(self.history) > 1:
                    self.history.pop()
                    self.history.pop()

            history_assistant_output = output
            # if len(message.character) > 0:
            #     history_assistant_output = "[" + message.character + "] " + history_assistant_output

            llm_output = {'role':'assistant', 'content': history_assistant_output}
            llm_output_limited = {'role':'assistant', 'content': self.limit_string(history_assistant_output, history_max_chars_per_message)}
            
            self.history[message.user_id].append(llm_output_limited)
        except Exception as e:
            log(DEBUG_LEVEL_MIN, '  [openai] ERROR while calling chat completion api: {e}')
            output = error_output
            self.history[message.user_id].append({'role':'system', 'content': f'Error: {e}'})

       # create latest history for llm
        self.limited_history[message.user_id] = self.history[message.user_id][:]
        while len(self.limited_history[message.user_id]) > history_max_entries:
            self.limited_history[message.user_id].pop(0)
            self.limited_history[message.user_id].pop(0)

        message.history = self.history[message.user_id]
        message.output = output            

    def limit_string (self, 
            input_string: str,
            max_number_of_character: str) -> str:
        if len(input_string) > max_number_of_character:
            return input_string[:max_number_of_character]
        else:
            return input_string        

