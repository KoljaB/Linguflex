from core import TextGeneratorModule, Request, cfg, log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from typing import Optional, Dict, List, Union
from termcolor import colored
from tenacity import retry, wait_random_exponential, stop_after_attempt
from openai_generator_helper import Conversation, TokenCounter, ContextWindow
import json
import traceback
import time
import openai

openai.api_key = cfg("api_key", env_key="OPENAI_API_KEY")
init_model = cfg("gpt_model", default="gpt-3.5-turbo-0613")
max_model = cfg("gpt_max_model", default="gpt-3.5-turbo-0613")
llm_temperature = float(cfg("default_temperature"))
max_history_entries  = int(cfg("max_history_entries"))
max_tokens_per_msg = int(cfg("max_tokens_per_msg"))
max_total_tokens = int(cfg("max_total_tokens"))
max_tokens_per_function = int(cfg("max_tokens_per_function"))
retry_attempts = int(cfg("retry_attempts", default=5))
min_timeout = int(cfg("min_timeout", default=4))
timeout_increase = int(cfg("timeout_increase", default=4))
estimated_processing_time_per_token = float(cfg("estimated_processing_time_per_token", default=0.005))
output_message_token_reserve = int(cfg("output_message_token_reserve", default=1500))
security_window_for_miscalculating_tokens = int(cfg("security_window_for_miscalculating_tokens", default=200))

def chat_completion_request(messages, functions=None, model="gpt-3.5-turbo-0613", timeout=10, max_tokens=-1, temperature=-1):
    params = {
        "model": model, 
        "messages": messages
    }
    if max_tokens != -1:
        params.update({"max_tokens": max_tokens})
    if temperature != -1:
        params.update({"max_tokens": temperature})
    if functions is not None and len(functions) > 0:
        params.update({"functions": functions})
    params.update({"request_timeout": timeout})        
    
    log(DEBUG_LEVEL_MAX, '  ->{}'.format(json.dumps(params, indent=4)))
    return openai.ChatCompletion.create(**params) # https://platform.openai.com/docs/api-reference/completions

def reliable_completion_request(messages, functions=None, model="gpt-3.5-turbo-0613", init_timeout = min_timeout):

    for i in range(retry_attempts):
        try:
            return chat_completion_request(messages, functions, model, init_timeout)
        
        # we perform retries for any of these:
        except openai.error.APIError as e:
            log(DEBUG_LEVEL_MIN, f'  [openai] API returned an API Error: {str(e)}')
        except openai.error.Timeout as e:
            log(DEBUG_LEVEL_MIN, f'  [openai] OpenAI API request timed out: {str(e)}')
        except openai.error.ServiceUnavailableError as e:
            log(DEBUG_LEVEL_MIN, f'  [openai] OpenAI API service unavailable: {str(e)}')
        except openai.error.APIConnectionError as e: # (?) not sure about retrying on this one
            log(DEBUG_LEVEL_MIN, f'  [openai] Failed to connect to OpenAI API: {str(e)}') 

        # these as quite fatal so we leave because retry won't change much
        except openai.error.RateLimitError as e:
            log(DEBUG_LEVEL_ERR, f'  [openai] OpenAI API request exceeded rate limit: {str(e)}')
            raise e
        except openai.error.InvalidRequestError as e:
            log(DEBUG_LEVEL_ERR, f'  [openai] Invalid request to OpenAI API: {str(e)}')
            raise e
        except openai.error.AuthenticationError as e:
            log(DEBUG_LEVEL_ERR, f'  [openai] Authentication error with OpenAI API: {str(e)}')
            raise e
        except openai.error.PermissionError as e:
            log(DEBUG_LEVEL_ERR, f'  [openai] API request was not permitted: {str(e)}')
            raise e

        init_timeout += timeout_increase
        log(DEBUG_LEVEL_MIN, f'  [openai] retry {i+1}/{retry_attempts} with timeout {init_timeout} seconds')

    return "OpenAI API currently unavailable"

def dump_json_if_necessary(obj):
    if isinstance(obj, str):
        try:
            json.loads(obj)
            return obj
        except json.JSONDecodeError:
            pass
    return json.dumps(obj)    

class OpenAIModule(TextGeneratorModule):
    def __init__(self) -> None: 
        self.conversations = {}

    def create_output(self,
            request: Request) -> None: 
        
        model = init_model 
        if hasattr(request, 'llm') and len(request.llm) > 0:
            model = request.llm

        if request.user_id not in self.conversations:
            self.conversations[request.user_id] = Conversation()

        # we present a function result to the generator
        # we need to reserve space in the context window for the function result and the generators answer to it
        if request.function_content is not None:

            # get context window of model
            context_window = ContextWindow.size_of(max_model)

            # substract tokens reserved for the answer of the generator
            max_tokens_for_function = context_window - output_message_token_reserve
            function_content_dumped = dump_json_if_necessary(request.function_content)

            # calculate tokens of the function 
            tokens_functions_original = TokenCounter.num_tokens_from_text(function_content_dumped)
            trimmed_function_content = TokenCounter.reduce_text_to_max_tokens(function_content_dumped, max_tokens_for_function, model = model)
            tokens_functions_trimmed = TokenCounter.num_tokens_from_text(trimmed_function_content)
            if tokens_functions_trimmed != tokens_functions_original:
                log(DEBUG_LEVEL_MIN, f'  [openai] Warning: function output has been trimmed from {tokens_functions_original} down to {tokens_functions_trimmed} tokens. This is NOT supposed to happen as it can cut into the integrity of structured JSON.')
            request.function_content = trimmed_function_content

            # reduce conversation history to that exact tokens of function_content will fit into context window
            self.conversations[request.user_id].trim_to_size(request, tokens_functions_trimmed, max_model)
            self.conversations[request.user_id].add('function', function_content_dumped, function_name=request.function_name_answer)
        else:
            # we present an initial user request to the generator
            self.conversations[request.user_id].add('user', request.input)

        input_messages = []
        input_messages = self.conversations[request.user_id].history[:]
        gpt_prompt = request.prompt

        if not gpt_prompt is None and len(gpt_prompt) > 0:
            system_prompt = {'role': 'system', 'content': gpt_prompt}
            input_messages = [system_prompt] + input_messages            

        try:
            message_tokens = TokenCounter.num_tokens_from_messages(input_messages, model=model)
            function_tokens = TokenCounter.num_tokens_from_functions(request.functions, model=model)
            total_tokens = message_tokens+function_tokens

            init_timeout = min_timeout + total_tokens * estimated_processing_time_per_token

            log(DEBUG_LEVEL_MAX, f'  [openai] Calculated tokens (message/function/total): {message_tokens}/{function_tokens}/{total_tokens}')
            log(DEBUG_LEVEL_MAX, f'  [openai] Calculated best fitting initial timeout based on tokens: {init_timeout}')
            if not hasattr(request, 'original_input') or request.original_input is None:
                log(DEBUG_LEVEL_MAX, f'  [openai] Initial request')
            else:
                log(DEBUG_LEVEL_MAX, f'  [openai] Follow request')

            # switch to highest allowed model if necessary
            context_window = ContextWindow.size_of(model)

             # add security window for potentially miscalculated token size (since functions api we dont have a reliable mechanism)
            if total_tokens > context_window - security_window_for_miscalculating_tokens:
                model = max_model

            start_time = time.time()
            model_response_dict = reliable_completion_request(messages=input_messages, functions=request.functions, model=model, init_timeout=init_timeout)
            end_time = time.time()

            log(DEBUG_LEVEL_MAX, '  <-{}'.format(str(model_response_dict)))
            log(DEBUG_LEVEL_MAX, '  [openai] Openai processing time: {:.2f}s'.format(end_time - start_time))

            model_answer_message = model_response_dict['choices'][0]['message']
            prompt_tokens = model_response_dict['usage']['prompt_tokens']
            exact_function_tokens = prompt_tokens - message_tokens
            log(DEBUG_LEVEL_MAX, f'  [openai]   Tokens used for functions: {exact_function_tokens}')

            if model_answer_message.get('function_call'):
                request.function_call = model_answer_message['function_call']
                request.function_name_execute = model_answer_message['function_call']['name']
                request.function_arguments = json.loads(model_answer_message['function_call']['arguments'])
                self.conversations[request.user_id].history.append(model_answer_message)

            request.output = ''
            if model_answer_message.get('content'):
                request.output = model_answer_message['content']
                self.conversations[request.user_id].add('assistant', request.output)

        except Exception as e:
            log(DEBUG_LEVEL_MIN, f'  [openai] ERROR while calling chat completion api: {str(e)}')
            traceback.print_exc()
            request.output = 'Error while calling chat completion api: ' + str(e)

        self.conversations[request.user_id].remove_until_user_message(max_history_entries)
        self.conversations[request.user_id].trim_history(max_tokens_per_msg, max_total_tokens, max_tokens_per_function, model=model)

    def limit_string (self, 
            input_string: str,
            max_number_of_character: str) -> str:
        if len(input_string) > max_number_of_character:
            return input_string[:max_number_of_character]
        else:
            return input_string