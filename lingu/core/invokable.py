from pydantic import validate_arguments
from typing import Any, Callable
from functools import wraps
import inspect
import json
import os


def remove_key(d, key):
    """
    Recursively removes a key from a dictionary and its nested dictionaries.
    """
    if isinstance(d, dict):
        d.pop(key, None)
        for v in d.values():
            remove_key(v, key)


class Invokable:
    """
    Wraps a callable to enable JSON-schema-based validation and invocation.

    This class is used to wrap a function, enabling validation of its arguments
    based on JSON schemas, and to facilitate its invocation in environments
    where JSON is used for argument serialization.
    The main use case is creating a schema for a function so that LLMs like
    openai gpt can call/invoke it.
    """
    def __init__(self, func: Callable) -> None:
        """
        Initializes the Invokable wrapper for a function.

        Args:
            func (Callable): The function to be wrapped by Invokable.
        """
        self.func = func
        self.validate_func = validate_arguments(func)

        parameters = self.validate_func.model.schema()
        parameters["properties"] = {
            key: val
            for key, val in parameters["properties"].items()
            if key not in ("v__duplicate_kwargs", "args", "kwargs")
            and not key.startswith("_")
        }
        parameters["required"] = sorted(
            k for k, v in parameters["properties"].items()
            if "default" not in v and not k.startswith("_")
        )

        remove_key(parameters, "title")
        remove_key(parameters, "additionalProperties")

        self.openai_schema = {
            "name": self.func.__name__,
            "description": self.func.__doc__ if self.func.__doc__ else '',
            "parameters": parameters,
        }

        self.model = self.validate_func.model
        self.caller_filename = self.get_caller_filename()

        function_dict = {
            "name": self.func.__name__,
            "execution": self,
            "function": self.func,
            "description": self.func.__doc__ if self.func.__doc__ else '',
            "schema": self.openai_schema,
            "caller_filename": self.caller_filename,
            "keywords": "",
            "init_prompt": "",
            "success_prompt": "Confirm successful execution.",
            "fail_prompt":
                "Report failed execution including reason of failure.",
        }
        self.info_dict = function_dict

    def get_caller_filename(self):
        """
        Retrieves the filename of the script
        that instantiated the Invokable.

        Returns:
            str: The name of the file without its extension.
        """
        caller_frame = inspect.stack()[2]
        full_file_path = caller_frame.filename
        file_name = os.path.basename(full_file_path)
        file_name_without_extension, _ = os.path.splitext(file_name)
        return file_name_without_extension

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Enables the Invokable instance to be called like a function.

        Args:
            *args (Any): Positional arguments to pass to the wrapped function.
            **kwargs (Any): Keyword arguments to pass to the wrapped function.

        Returns:
            Any: The result of the wrapped function call.
        """
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            return self.validate_func(*args, **kwargs)

        return wrapper(*args, **kwargs)

    def from_arguments(self, arguments):
        """
        Creates an invocation from a JSON string of arguments.

        Args:
            arguments (str): JSON string representing the arguments.

        Returns:
            Any: The result of the function call with the provided arguments.
        """
        return self.validate_func(
            **json.loads(
                arguments,
                strict=False
            )
        )

    def from_function_call(self, function_call):
        """
        Creates an invocation from an openai function call.

        Args:
            function_call: openai function call.

        Returns:
            Any: The result of the function call with the provided arguments.
        """
        return self.validate_func(
            **json.loads(
                function_call["arguments"],
                strict=False
            )
        )
