import json
import tiktoken
from core import log, cfg, Request, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from typing import Optional, Union, Dict
from termcolor import colored

minimum_token_window = int(cfg("minimum_token_window", default=200))
completion_token_reserve = int(cfg("completion_token_reserve", default=1000))
message_in_history_max_size_percent = float(cfg("message_in_history_max_size_percent", default=0.25))
function_in_history_max_size_percent = float(cfg("function_in_history_max_size_percent", default=0.25))

class Conversation:
    """
    A class to manage conversation history.
    """

    def __init__(self) -> None:
        """
        Initialize an empty conversation history.
        """
        self.history = []

    def create_message(self, role: str, content: str, function_name: Optional[str] = None, function_call: Optional[Dict[str, str]] = None):
        message = {"role": role}

        if function_name is not None:
            message["name"] = function_name

        if role == 'assistant' and function_call is not None:
            message["function_call"] = function_call
        
        message["content"] = content
        return message


    def add(self, role: str, content: str, function_name: Optional[str] = None, function_call: Optional[Dict[str, str]] = None) -> None:
        """
        Add a new message to the conversation history.
        
        :param role: The role of the message sender.
        :param content: The content of the message.
        :param function_name: Optional name of the function, only used if role is 'function'.
        :param function_call: Optional function call data, only used if role is 'assistant'.
        """
        message = self.create_message(role, content, function_name, function_call)

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

    def trim_to_size(self, request: Request, requested_tokens_for_functions_result = minimum_token_window, model="gpt-3.5-turbo-0613"):

        if requested_tokens_for_functions_result < minimum_token_window:
            log(DEBUG_LEVEL_MAX, f'  [history] {requested_tokens_for_functions_result} < {minimum_token_window}, adjusted')
            requested_tokens_for_functions_result = minimum_token_window

        # context window token optimizing to reserve space for submitting function result
        context_window = ContextWindow.size_of(model)
        log(DEBUG_LEVEL_MAX, f'  [history] {context_window} start size, optimizing context window tokens')

        input_message = self.create_message("user", request.input)
        input_message_tokens = TokenCounter.num_tokens_from_messages([input_message], model=model)
        available_window = context_window - input_message_tokens
        log(DEBUG_LEVEL_MAX, f'  [history] {available_window} size, subtracted user input message tokens: {input_message_tokens}')

        function_tokens = TokenCounter.num_tokens_from_functions(request.functions, model=model)
        available_window = available_window - function_tokens
        log(DEBUG_LEVEL_MAX, f'  [history] {available_window} size, subtracted tokens for functions offered to llm: {function_tokens}')

        # since we can't calculate precisely, mostly due to no function token calculation, we need to preserve space
        reserve_tokens = completion_token_reserve
        available_window_for_history_and_function_result = available_window - reserve_tokens
        log(DEBUG_LEVEL_MAX, f'  [history] {available_window_for_history_and_function_result} size for history and function result, subtracted {reserve_tokens} tokens reserve')

        # now we have the maximal availabe token size for both history and the desired function execution result token reserve
        # so as long as history is bigger th    n this we size it down until either we cant anymore or size is reached
        available_window_for_history = available_window_for_history_and_function_result - requested_tokens_for_functions_result
        log(DEBUG_LEVEL_MAX, f'  [history] {available_window_for_history} max history size, subtracted requested tokens for functions result {requested_tokens_for_functions_result}')

        history_tokens = TokenCounter.num_tokens_from_messages(self.history, model=model)
        if history_tokens > available_window_for_history:
            log(DEBUG_LEVEL_MAX, f'  [history] trimming history => history tokens {history_tokens} > available window for history {available_window_for_history}')
            self.trim_history(
                max_tokens_per_msg = available_window_for_history_and_function_result * message_in_history_max_size_percent,
                max_total_tokens = available_window_for_history,
                max_tokens_per_function = available_window_for_history_and_function_result * function_in_history_max_size_percent,
                model = model)

        history_tokens = TokenCounter.num_tokens_from_messages(self.history, model=model)
        log(DEBUG_LEVEL_MAX, f'  [history] trimmed history tokens {history_tokens}')
        
        available_window_for_function_result = available_window_for_history_and_function_result - history_tokens
        log(DEBUG_LEVEL_MAX, f'  [history] available window for function result {available_window_for_function_result}')
        return available_window_for_function_result



    def trim_history(self, max_tokens_per_msg: int = 800, max_total_tokens: int = 3000, max_tokens_per_function: int = 200, model: str = "gpt-3.5-turbo-0613") -> None:
        """
        Trim entries in the history to keep their token count within a maximum limit.
        """
        # Check function messages and replace if necessary
        for message in self.history:
            if message['role'] == 'function' and message['content'] is not None:
                num_tokens = TokenCounter.num_tokens_from_messages([message], model=model)
                if num_tokens > max_tokens_per_function:
                    # Replace the message content
                    log(DEBUG_LEVEL_MAX, f'  function purged from history, size {num_tokens} > {max_tokens_per_function}')
                    message['content'] = "[removed]"

        # Trim individual messages
        for message in self.history:
            if message['content'] is not None:
                num_tokens = TokenCounter.num_tokens_from_messages([message], model=model)
                message_trimmed = False
                while num_tokens > max_tokens_per_msg:
                    message_trimmed = True
                    # Remove tokens from the end
                    message['content'] = message['content'][:-1]
                    num_tokens = TokenCounter.num_tokens_from_messages([message], model=model)
                if message_trimmed:
                    log(DEBUG_LEVEL_MAX, f'  message content trimmed to {max_tokens_per_msg}')

            # Trim the total history
            num_tokens_total = TokenCounter.num_tokens_from_messages(self.history, model=model)
            while num_tokens_total > max_total_tokens:
                # We will remove messages until we hit a user message
                removed = False
                for i, message in enumerate(self.history):
                    if message['role'] == 'user':
                        if i == 0: 
                            # First message in history is a user message
                            log(DEBUG_LEVEL_MAX, f'  last single message in history total tokens {num_tokens_total} exceeded limit {max_total_tokens}')
                        else:
                            log(DEBUG_LEVEL_MAX, f'  messages removed because total tokens {num_tokens_total} exceeded limit {max_total_tokens}')
                            # Remove messages from the start until the user message
                            self.history = self.history[i:]
                            removed = True
                            break
                # If we didn't remove anything (i.e., there are no user messages), just remove the oldest message
                if not removed:
                    self.history.pop(0)

                # Recalculate the total token count
                num_tokens_total = TokenCounter.num_tokens_from_messages(self.history, model=model)

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

class TokenCounter:

    @staticmethod
    def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages."""

        if not messages or len(messages) == 0: 
            return 0
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            log(DEBUG_LEVEL_MIN, f"  [openai] Warning: model not found. Using cl100k_base encoding.")
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
        elif not model == "gpt-3.5-turbo-0613" and "gpt-3.5-turbo" in model:
            return TokenCounter.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif not model == "gpt-4-0613" and "gpt-4" in model:
            return TokenCounter.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0

        for message in messages:
            num_tokens += tokens_per_message

            if "function_call" in message:
                arguments_json = json.loads(message["function_call"]["arguments"])
                message["function_call"]["arguments"] = json.dumps(arguments_json)

            for key, value in message.items():
                current_message_tokens = len(encoding.encode(str(value)))
                num_tokens += current_message_tokens
                if key == "name":
                    num_tokens -= tokens_per_name
                if key == "function_call":
                    num_tokens -= 7                  

        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens            
    
    @staticmethod
    def num_tokens_from_functions(functions, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of functions."""

        if not functions or len(functions) == 0: return 0

        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            log(DEBUG_LEVEL_MIN, f"  [openai] Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        def count_tokens_from_dict(d):
            tokens = 0
            for key in d:
                tokens += len(encoding.encode(key))
                v = d[key]
                for field in v:
                    if field == 'type':
                        tokens += 2
                        tokens += len(encoding.encode(v['type']))
                    elif field == 'description':
                        tokens += 2
                        tokens += len(encoding.encode(v['description']))
                    elif field == 'enum':
                        tokens -= 3
                        for o in v['enum']:
                            tokens += 3
                            tokens += len(encoding.encode(o))
                    # else:
                    #     log(DEBUG_LEVEL_MIN, f"  [openai] Warning num_tokens_from_functions: not supported field {field}")
            tokens += 11
            return tokens

        num_tokens = 0
        for function in functions:
            function_tokens = len(encoding.encode(function['name']))
            function_tokens += len(encoding.encode(function['description']))

            if 'parameters' in function:
                parameters = function['parameters']
                if 'properties' in parameters:
                    function_tokens += count_tokens_from_dict(parameters['properties'])
                if 'definitions' in parameters:
                    function_tokens += count_tokens_from_dict(parameters['definitions'])
                if 'required' in parameters:
                    for requiredParameter in parameters['properties']:
                        function_tokens += len(encoding.encode(requiredParameter))

            num_tokens += function_tokens

        num_tokens += 12 
        return num_tokens
    
    @staticmethod
    def num_tokens_from_text(text, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a specified text."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            log(DEBUG_LEVEL_MIN, f"  [openai] Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        
        num_tokens = len(encoding.encode(str(text)))
        return num_tokens
    
    @staticmethod
    def reduce_text_to_max_tokens(text, max_tokens=2000, model="gpt-3.5-turbo-0613"):
        while TokenCounter.num_tokens_from_text(text, model) > max_tokens:
            text = text[:-1]
        return text

class ContextWindow:

    @staticmethod
    def size_of(model="gpt-3.5-turbo-0613"):
        # https://platform.openai.com/docs/models/overview
        if model == "gpt-3.5-turbo":
            return 4096
        elif model == "gpt-3.5-turbo-0613":
            return 4096
        elif model == "gpt-4":
            return 8192
        elif model == "gpt-4-0613":
            return 8192
        elif model == "gpt-3.5-turbo-16k":
            return 16384
        elif model == "gpt-3.5-turbo-16k-0613":
            return 16384
        elif model == "gpt-4-32k":
            return 32768
        elif model == "gpt-4-32k-0613":
            return 32768
        
        # unknown: return safety low window
        return 4096