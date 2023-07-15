import json
from functools import wraps
from typing import Any, Callable
from pydantic import validate_arguments, BaseModel
import inspect
import os
from linguflex_log import (
    log,
    DEBUG_LEVEL_OFF,
    DEBUG_LEVEL_MIN,
    DEBUG_LEVEL_MID,
    DEBUG_LEVEL_MAX,
    DEBUG_LEVEL_ERR
)

functions = []
classes = []

def tokens_function(value: int) -> Callable:
    """Decorator to set the function_tokens value"""
    def wrapper(cls):
        if inspect.isclass(cls) and issubclass(cls, LinguFlexBase):
            cls.tokens_function = value
            return cls
        else:
            raise TypeError("Decorator can only be used with subclasses of LinguFlexBase")
    return wrapper

def max_tokens_answer(value: int) -> Callable:
    """Decorator to set the generator_tokens value"""
    def wrapper(cls):
        if inspect.isclass(cls) and issubclass(cls, LinguFlexBase):
            cls.max_tokens_answer = value
            return cls
        else:
            raise TypeError("Decorator can only be used with subclasses of LinguFlexBase")
    return wrapper    

def max_tokens_result(value: int) -> Callable:
    """Decorator to set the generator_tokens value"""
    def wrapper(cls):
        if inspect.isclass(cls) and issubclass(cls, LinguFlexBase):
            cls.max_tokens_result = value
            return cls
        else:
            raise TypeError("Decorator can only be used with subclasses of LinguFlexBase")
    return wrapper    

def remove_key(d, key):
    if isinstance(d, dict):
        d.pop(key, None)
        for v in d.values():
            remove_key(v, key)

class LinguFlexBase(BaseModel):
    @classmethod
    def register(self, obj, filename):
        openai_schema = self.openai_schema
        class_dict = {  
            "name": openai_schema["name"],
            "execution": self,
            "obj": obj,
            "schema": openai_schema,
            "caller_filename": filename,
            "description": openai_schema["description"],
            "keywords": "",
            "init_prompt": "",
            "success_prompt": f'Confirm successful execution.',
            "fail_prompt": f'Report failed execution including reason of failure.',
            "tokens_function": getattr(self, 'tokens_function', None),
            "max_tokens_answer": getattr(self, 'max_tokens_answer', None),
            "max_tokens_result": getattr(self, 'max_tokens_result', None),
        }        

        classes.append(class_dict)

    @classmethod
    def from_function_call(self, function_call):
        return self(**json.loads(function_call["arguments"]))

    @classmethod
    @property
    def openai_schema(self):
        schema = self.schema()

        parameters = {
            key: val for key, val in schema.items() if key not in ("title", "description")
        }        
        parameters["required"] = sorted(
            key for key, val in parameters.get("properties", {}).items() if not "default" in val
        )

        remove_key(parameters, "title")

        return {
            "name": schema["title"],
            "description": schema.get("description", ""),
            "parameters": parameters,
        }        
    
    def execute(self): return 'success'    

class linguflex_function:
    def __init__(self, func: Callable) -> None:
        self.func = func
        self.validate_func = validate_arguments(func)

        parameters = self.validate_func.model.schema()
        parameters["properties"] = {
            key: val
            for key, val in parameters["properties"].items()
            if key not in ("v__duplicate_kwargs", "args", "kwargs")
        }
        parameters["required"] = sorted(
            key for key, val in parameters.get("properties", {}).items() if not "default" in val
        )

        remove_key(parameters, "title")
        remove_key(parameters, "additionalProperties")       

        self.openai_schema = {
            "name": self.func.__name__,
            "description": self.func.__doc__,
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
            "success_prompt": f'Confirm successful execution.',
            "fail_prompt": f'Report failed execution including reason of failure.',
        }
        log(DEBUG_LEVEL_MAX, f'  ├── · function {self.func.__name__} imported')        
        functions.append(function_dict)

    def get_caller_filename(self):
        caller_frame = inspect.stack()[2]
        full_file_path = caller_frame.filename
        file_name = os.path.basename(full_file_path)
        file_name_without_extension, _ = os.path.splitext(file_name)
        return file_name_without_extension
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            return self.validate_func(*args, **kwargs)

        return wrapper(*args, **kwargs)
    
    def from_function_call(self, function_call):
        return self.validate_func(**json.loads(function_call["arguments"]))   