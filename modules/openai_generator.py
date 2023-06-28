from core import TextGeneratorModule, Request, cfg, log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from typing import Optional, Dict, List, Union
from termcolor import colored
from tenacity import retry, wait_random_exponential, stop_after_attempt
# import os
import openai
# import requests
import json
import tiktoken
import traceback


openai.api_key = cfg("api_key", "LINGU_OPENAI_API_KEY")
model = cfg("gpt_model")
llm_temperature = float(cfg("default_temperature"))
max_history_entries  = int(cfg("max_history_entries"))
max_tokens_per_msg = int(cfg("max_tokens_per_msg"))
max_total_tokens = int(cfg("max_total_tokens"))
max_tokens_per_function = int(cfg("max_tokens_per_function"))

RETRY_ATTEMPTS = 4
START_TIMEOUT = 30
TIMEOUT_INCREASE = 10

def chat_completion_request(messages, functions=None, model=model, timeout=10):
    params = {
        "model": model, 
        "messages": messages
    }
    if functions is not None and len(functions) > 0:
        params.update({"functions": functions})
    params.update({"request_timeout": timeout})        
    
    log(DEBUG_LEVEL_MAX, '  ->{}'.format(json.dumps(params, indent=4)))
    return openai.ChatCompletion.create(**params) # https://platform.openai.com/docs/api-reference/completions

def reliable_completion_request(messages, functions=None, model=model):

    timeout = START_TIMEOUT

    for i in range(RETRY_ATTEMPTS):
        try:
            return chat_completion_request(messages, functions, model, timeout)
        
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

        timeout += TIMEOUT_INCREASE
        log(DEBUG_LEVEL_MIN, f'  [openai] retry {i+1}/{RETRY_ATTEMPTS} with timeout {timeout} seconds')

    return "OpenAI API currently unavailable"


class OpenAIModule(TextGeneratorModule):
    def __init__(self) -> None: 
        self.conversations = {}

    def create_output(self,
            request: Request) -> None: 
        
        llm_model = model if len(request.llm) == 0 else request.llm

        if request.user_id not in self.conversations:
            self.conversations[request.user_id] = Conversation()

        if request.function_content is not None:
            self.conversations[request.user_id].add('function', json.dumps(request.function_content), function_name=request.function_name_answer)
        else:
            self.conversations[request.user_id].add('user', request.input)

        input_messages = []
        input_messages = self.conversations[request.user_id].history[:]
        gpt_prompt = request.prompt

        if not gpt_prompt is None and len(gpt_prompt) > 0:
            system_prompt = {'role': 'system', 'content': gpt_prompt}
            input_messages = [system_prompt] + input_messages            


        try:
            if request.function_content is not None and request.return_value_success:
                model_response_dict = reliable_completion_request(input_messages, None, llm_model)
            else:
                model_response_dict = reliable_completion_request(input_messages, request.functions, llm_model)
            
            log(DEBUG_LEVEL_MAX, '  <-{}'.format(str(model_response_dict)))

            model_answer_message = model_response_dict['choices'][0]['message']

            if model_answer_message.get('function_call'):
                request.function_call = model_answer_message['function_call']
                request.function_name_execute = model_answer_message['function_call']['name']
                request.function_arguments = json.loads(model_answer_message['function_call']['arguments'])
                self.conversations[request.user_id].history.append(model_answer_message)

            request.output = ''
            if model_answer_message.get('content'):
                request.output = model_answer_message['content']
                if not request.no_output_to_history:
                    self.conversations[request.user_id].add('assistant', request.output)

        except Exception as e:
            log(DEBUG_LEVEL_MIN, f'  [openai] ERROR while calling chat completion api: {str(e)}')
            traceback.print_exc()
            request.output = 'Error while calling chat completion api: ' + str(e)
            if not request.no_output_to_history:
                self.conversations[request.user_id].add('assistant',f'Error: {e}')

        self.conversations[request.user_id].remove_until_user_message(max_history_entries)
        self.conversations[request.user_id].trim_history(max_tokens_per_msg, max_total_tokens, max_tokens_per_function)

        request.output_user = request.output 


    def limit_string (self, 
            input_string: str,
            max_number_of_character: str) -> str:
        if len(input_string) > max_number_of_character:
            return input_string[:max_number_of_character]
        else:
            return input_string        
        


class Conversation:
    """
    A class to manage conversation history.
    """

    def __init__(self) -> None:
        """
        Initialize an empty conversation history.
        """
        self.history = []

    def add(self, role: str, content: str, function_name: Optional[str] = None) -> None:
        """
        Add a new message to the conversation history.
        
        :param role: The role of the message sender.
        :param content: The content of the message.
        :param function_name: Optional name of the function, only used if role is 'function'.
        """
        message = {"role": role}

        if function_name is not None:
            message["name"] = function_name

        message["content"] = content

        self.history.append(message)

    def remove_until_user_message(self, num_of_user_messages: int = 1) -> None:
        """
        Remove all messages from the conversation history up to a certain number of user messages.
        
        :param num_of_user_messages: The number of user messages to encounter before stopping.
        """
        count = 0
        for i in range(len(self.history) - 1, -1, -1):
            if self.history[i]['role'] == 'user':
                count += 1
                if count == num_of_user_messages:
                    del self.history[:i]
                    break

    def trim_history(self, max_tokens_per_msg: int = 800, max_total_tokens: int = 3000, max_tokens_per_function: int = 200, model: str = "gpt-3.5-turbo-0613") -> None:
        """
        Trim entries in the history to keep their token count within a maximum limit.
        """
        # Check function messages and replace if necessary
        for message in self.history:
            if message['role'] == 'function' and message['content'] is not None:
                num_tokens = self.num_tokens_from_messages([message], model=model)
                if num_tokens > max_tokens_per_function:
                    # Replace the message content
                    log(DEBUG_LEVEL_MAX, f'  function purged from history, size {num_tokens} > {max_tokens_per_function}')
                    message['content'] = "[removed]"

        # Trim individual messages
        for message in self.history:
            if message['content'] is not None:
                num_tokens = self.num_tokens_from_messages([message], model=model)
                message_trimmed = False
                while num_tokens > max_tokens_per_msg:
                    message_trimmed = True
                    # Remove tokens from the end
                    message['content'] = message['content'][:-1]
                    num_tokens = self.num_tokens_from_messages([message], model=model)
                if message_trimmed:
                    log(DEBUG_LEVEL_MAX, f'  message content trimmed to {max_tokens_per_msg}')
                    #log(DEBUG_LEVEL_MAX, f'  message {message["role"]} content trimmed to {max_tokens_per_msg}')

        # Trim the total history
        num_tokens_total = self.num_tokens_from_messages(self.history, model=model)
        while num_tokens_total > max_total_tokens:
            # We will remove messages until we hit a user message
            removed = False
            for i, message in enumerate(self.history):
                if message['role'] == 'user':
                    log(DEBUG_LEVEL_MAX, f'  messages removed because total tokens {num_tokens_total} exceeded limit {max_total_tokens}')
                    # Remove messages from the start until the user message
                    self.history = self.history[i:]
                    removed = True
                    break
            # If we didn't remove anything (i.e., there are no user messages), just remove the oldest message
            if not removed:
                self.history.pop(0)

            # Recalculate the total token count
            num_tokens_total = self.num_tokens_from_messages(self.history, model=model)

    # def trim_history(self, max_tokens_per_msg: int = 800, max_total_tokens: int = 3000, max_tokens_per_function: int = 200) -> None:
    #     """
    #     Trim entries in the history to keep their token count within a maximum limit. 

    #     ...
    #     """
    #     encoding = tiktoken.get_encoding("cl100k_base")

    #     # Check function messages and replace if necessary
    #     for message in self.history:
    #         if message['role'] == 'function' and message['content'] is not None:
    #             tokens = encoding.encode(str(message['content']))
    #             if len(tokens) > max_tokens_per_function:
    #                 # Replace the message content
    #                 log(DEBUG_LEVEL_MAX, f'  function purged from history, size {len(tokens)} > {max_tokens_per_function}')
    #                 message['content'] = "[removed]"

    #     # Trim individual messages
    #     for message in self.history:
    #         if message['content'] is not None:
    #             tokens = encoding.encode(str(message['content']))
    #             message_trimmed = False
    #             while len(tokens) > max_tokens_per_msg:
    #                 message_trimmed = True
    #                 # Remove tokens from the end
    #                 tokens = tokens[:-1]
    #                 # Update the message content
    #                 message['content'] = encoding.decode(tokens)
    #             if message_trimmed:
    #                 log(DEBUG_LEVEL_MAX, f'  message content trimmed to {max_tokens_per_msg}')
    #                 #log(DEBUG_LEVEL_MAX, f'  message {message["role"]} content trimmed to {max_tokens_per_msg}')

    #     # Trim the total history
    #     tokens_total = sum(len(encoding.encode(str(message['content']))) for message in self.history if message['content'] is not None)
    #     while tokens_total > max_total_tokens:
    #         # We will remove messages until we hit a user message
    #         removed = False
    #         for i, message in enumerate(self.history):
    #             if message['role'] == 'user':
    #                 log(DEBUG_LEVEL_MAX, f'  messages removed because total tokens {tokens_total} exceeded limit {max_total_tokens}')
    #                 # Remove messages from the start until the user message
    #                 self.history = self.history[i:]
    #                 removed = True
    #                 break
    #         # If we didn't remove anything (i.e., there are no user messages), just remove the oldest message
    #         if not removed:
    #             self.history.pop(0)

    #         # Recalculate the total token count
    #         tokens_total = sum(len(encoding.encode(str(message['content']))) for message in self.history if message['content'] is not None)


    def remove_latest(self) -> None:
        """
        Remove the latest message from the conversation history.
        """
        self.history.pop()

    def remove_oldest(self) -> None:
        """
        Remove the oldest message from the conversation history.
        """
        self.history.pop(0)

    def display(self) -> None:
        """
        Print the conversation history in a user-friendly format, with different roles in different colors.
        """
        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }

        for message in self.history:
            print(colored(
                    f"{message['role']}: {message['content']}\n\n",
                    role_to_color[message["role"]],
                )
            )


    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            log(DEBUG_LEVEL_MIN, "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            log(DEBUG_LEVEL_MIN, "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(str(value)))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens            