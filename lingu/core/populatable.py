from pydantic import BaseModel
import json


def remove_key(d, key):
    """
    Recursively removes a key from a dictionary and its nested dictionaries.
    """
    if isinstance(d, dict):
        d.pop(key, None)
        for v in d.values():
            remove_key(v, key)


class Populatable(BaseModel):
    """
    Base class for objects that can be populated and registered with a schema.

    The main use case is creating a sink for LLMs to be filled with data.
    """

    def on_populated(self):
        """
        Hook method to be called after the object is populated.
        """
        pass

    @classmethod
    def register(self, obj, filename):
        """
        Register an object with its OpenAI schema and other metadata.
        """
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
            "success_prompt": "Confirm successful execution.",
            "fail_prompt":
                "Report failed execution including reason of failure.",
        }
        self.info_dict = class_dict

    @classmethod
    def from_arguments(self, arguments):
        return self(**json.loads(arguments, strict=False))

    @classmethod
    def from_function_call(self, function_call):
        return self(**json.loads(function_call["arguments"], strict=False))

    @classmethod
    @property
    def openai_schema(self):
        schema = self.schema()

        parameters = {
            key: val for key, val in schema.items()
            if key not in ("title", "description") and not key.startswith("_")
        }
        parameters["required"] = sorted(
            k for k, v in parameters["properties"].items()
            if "default" not in v and not k.startswith("_")
        )

        remove_key(parameters, "title")

        return {
            "name": schema["title"],
            "description": schema.get("description", ""),
            "parameters": parameters,
        }

    def execute(self): return "success"
