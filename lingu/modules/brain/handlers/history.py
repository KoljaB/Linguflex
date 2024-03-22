from openai_token_counter import openai_token_counter
from lingu import log
import base64
import json


IMG_PLACEHOLDER = '[Image Placeholder]'


class History:
    """
    Manages a history of messages with a
    limit on the number of stored messages.
    """

    def __init__(
            self,
            max_history_messages: int = 12,
            max_tokens_per_msg: int = 500,
            max_history_tokens: int = 3500
            ):
        """
        Initializes the History object
        with a maximum number of history messages.

        Args:
            max_history_messages (int): The maximum number of messages
              to store. Default is 12.
            max_tokens_per_msg (int): The maximum number of tokens
              per message. Default is 500.
            max_history_tokens (int): The maximum number of tokens
              for the entire history. Default is 3500.
        """
        self.max_history_messages = max_history_messages
        self.max_tokens_per_msg = max_tokens_per_msg
        self.max_history_tokens = max_history_tokens

        self.history = []

    def _dump_json_if_necessary(self, obj):
        if isinstance(obj, str):
            try:
                json.loads(obj)
                return obj
            except json.JSONDecodeError:
                pass
        try:
            return json.dumps(obj)
        except Exception:
            return str(obj)

    def function_call(self, func_name: str, func_args: str) -> None:
        """
        Adds a new function call to the history.

        Args:
            func_name (str): The name of the function.
            func_args (str): The arguments of the function.
        """
        function_call_message = {
            'role': 'assistant',
            'content': None,
            'function_call': {"name": func_name, "arguments": func_args}
            }
        log.dbg(f"  [history] adding function call:\n{function_call_message}")
        self._add(function_call_message)

    def function_answer(self, func_name: str, func_return: str) -> None:
        """
        Adds a new function answer to the history.

        Args:
            func_name (str): The name of the function.
            func_return (str): The return value of the function.
        """
        func_return = self._dump_json_if_necessary(func_return)
        func_return_message = {
            'role': 'function',
            'name': func_name,
            'content': func_return
            }
        log.dbg(f"  [history] adding function answer:\n{func_return_message}")
        self._add(func_return_message)

    def assistant(self, assistant_response: str) -> None:
        """
        Adds a new assistant response to the history.

        Args:
            assistant_response (str): The assistant response to add
              to the history.
        """
        assistant_message = {
            'role': 'assistant', 'content': assistant_response
        }
        log.dbg(f"  [history] adding assistant msg:\n{assistant_message}")
        self._add(assistant_message)

    def encode_image(self, image_path):
        """
        Encodes the image at the given path to a base64 string.

        Args:
            image_path (str): The path to the image file.

        Returns:
            str: The base64 encoded string of the image.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def user(
            self,
            user_text: str,
            image_path: str = None,
    ) -> None:
        """
        Adds a new user text to the history.

        Args:
            user_text (str): The user text to add to the history.
            image_path (str): The path to the image to add to the history.
        """
        if image_path:
            base64_image = self.encode_image(image_path)
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        else:
            user_message = {'role': 'user', 'content': user_text}

        log.dbg(f"  [history] adding user msg:\n{user_message}")
        self._add(user_message)

    def add_executed_tools(self, tools_call_msg, tools) -> None:
        """
        Adds a new tools call message to the history.

        Args:
            tools_call_msg: The tools call message dict to add
              to the history.
        """
        self._add(tools_call_msg)
        log.dbg(f"  [history] adding tool msg:\n{tools_call_msg}")

        for tool in tools:
            message = {
                "tool_call_id": tool["id"],
                "role": "tool",
                "name": tool["name"],
                "content": json.dumps(tool["return_value"])
            }
            log.dbg(f"  [history] adding executed tool:\n{message}")
            self._add(message)

    def _add(self, entry: str) -> None:
        """
        Adds a new entry to the history.

        Args:
            entry (str): The message to add to the history.
        """
        self.history.append(entry)

        # Ensure the history does not exceed the maximum limit
        if len(self.history) > self.max_history_messages:
            self.history.pop(0)

    def get(self, number_of_messages=-1) -> list:
        """
        Retrieves the most recent entries in the history
        up to the maximum limit.

        Returns:
            list: A list of the most recent entries.
        """
        number_of_messages = (
            number_of_messages
            if number_of_messages > 0
            else self.max_history_messages
        )
        messages = self.history[-number_of_messages:]

        # Remove tool message from the history if it is the first message
        # This is because tool needs context
        while (
            len(messages) > 0
            and "role" in messages[0]
            and messages[0]["role"] == "tool"
        ):
            messages = messages[1:]

        return messages

    def get_tokens(self, messages, functions, model="gpt-3.5-turbo"):
        """
        Get the number of tokens in the messages.
        """
        result_no_tools = openai_token_counter(
            messages=messages,
            model=model,
            functions=None,
            function_call="auto"
        )
        tokens_tools_est = 0
        if functions:
            for fct in functions:
                # print(fct)
                tokens_tools_est += len(str(fct))
        tokens_tools_est = int(tokens_tools_est * 0.33)
        # log.dbg(
        #     f"  [history] Estimated tokens for tools: {tokens_tools_est}")
        result = result_no_tools + tokens_tools_est

        return result

        # try:
        #     result = openai_token_counter(
        #         messages=messages,
        #         model=model,
        #         functions=functions,
        #         function_call="auto"
        #     )
        #     return result
        # except Exception as e:
        #     log.err(f"  [history] Error in token counting: {e}")
        #     result_no_tools = openai_token_counter(
        #         messages=messages,
        #         model=model,
        #         functions=None,
        #         function_call="auto"
        #     )
        #     tokens_tools_est = 0
        #     if functions:
        #         for fct in functions:
        #             print(fct)
        #             tokens_tools_est += len(str(fct))
        #     tokens_tools_est = tokens_tools_est * 0.33
        #     log.dbg(
        #         f"  [history] Estimated tokens for tools: {tokens_tools_est}")
        #     result = result_no_tools + tokens_tools_est

        #     return result

    def trim_tokens(
            self,
            system_message: str,
            functions,
            model: str
    ) -> None:
        """
        Trim the history to ensure the maximum number of tokens
        is not exceeded.

        Args:
            system_message (str): The system message
              that will be added to the history.
            functions (module): The module
              containing the token counting function.
            model (str): The model used for token counting.
        """
        # Define maximum iterations to prevent infinite loops
        MAX_ITERATIONS = 5000

        # handle image messages (replace image data with a placeholder)
        for message in self.history:
            if 'content' in message:
                # Check if message contains an image
                if isinstance(message['content'], list):
                    for content_part in message['content']:
                        if content_part.get('type') == 'image_url':
                            # Replace image data with a placeholder
                            content_part['image_url']['url'] = IMG_PLACEHOLDER
                elif isinstance(message['content'], str):
                    message_tokens = self.get_tokens([message], None, model)
                    while message_tokens > self.max_tokens_per_msg:
                        message['content'] = message['content'][:-10]
                        message_tokens = self.get_tokens(
                            [message], None, model)

        # First loop: Trim each message independently
        for message in self.history:
            iteration_count = 0

            # Calculate tokens for the current message
            message_tokens = self.get_tokens([message], functions, model)

            while (message_tokens > self.max_tokens_per_msg
                    and iteration_count < MAX_ITERATIONS):

                # Reduce message content incrementally
                message['content'] = message['content'][:-10]
                message_tokens = self.get_tokens([message], functions, model)
                iteration_count += 1

        # Second loop: Check the total tokens of the entire history
        current_tokens = self.get_tokens(
            system_message + self.get(), functions, model)
        iteration_count = 0

        while (current_tokens > self.max_history_tokens
                and len(self.history) > 0
                and iteration_count < MAX_ITERATIONS):
            # Remove the oldest message
            self.history.pop(0)

            # Recalculate the total number of tokens
            current_tokens = self.get_tokens(
                system_message + self.get(), functions, model)

            log.dbg("  [trim_tokens] New total tokens after removing a "
                    f"message: {current_tokens}")

            iteration_count += 1
