# MIT License
#
# Copyright (c) 2023 Jason Liu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.




# This class is a modified version of the great work of the brilliant Jason Liu.
# I strongly recommend everyone interested in programming to have a look
# at his amazing work and his concise and really well-written code.
# Can't give enough credit and hope I will someday write code as good as this guy.

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

def _remove_a_key(d, remove_key) -> None:
    """Remove a key from a dictionary recursively"""
    if isinstance(d, dict):
        for key in list(d.keys()):
            if key == remove_key:
                del d[key]
            else:
                _remove_a_key(d[key], remove_key)

class linguflex_function:
    def __init__(self, func: Callable) -> None:
        self.func = func
        self.validate_func = validate_arguments(func)

        parameters = self.validate_func.model.schema()
        parameters["properties"] = {
            k: v
            for k, v in parameters["properties"].items()
            if k not in ("v__duplicate_kwargs", "args", "kwargs")
        }
        parameters["required"] = sorted(
            parameters["properties"]
        )        
        _remove_a_key(parameters, "title")
        _remove_a_key(parameters, "additionalProperties")       


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
   
    def from_function_call(self, function_call, throw_error=True):
        """Execute the function from the response of an openai chat completion"""

        if throw_error:
            assert function_call["name"] == self.openai_schema["name"], "Function name does not match"

        arguments = json.loads(function_call["arguments"])
        return self.validate_func(**arguments)

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
        }
        classes.append(class_dict)

    @classmethod
    def from_function_call(self, function_call, throw_error=True):
        """Execute the function from the response of an openai chat completion"""
        if throw_error:
            assert function_call["name"] == self.openai_schema["name"], "Function name does not match"

        arguments = json.loads(function_call["arguments"])
        return self(**arguments)        

    @classmethod
    @property
    def openai_schema(self):

        schema = self.schema()
        parameters = {
            k: v for k, v in schema.items() if k not in ("title", "description")
        }
        parameters["required"] = sorted(parameters["properties"])
        _remove_a_key(parameters, "title")
        return {
            "name": schema["title"],
            "description": schema["description"] if "description" in schema else "",
            "parameters": parameters,
        }        
    
    def execute(self): return 'success'    