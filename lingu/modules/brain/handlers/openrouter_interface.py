from .llminterfacebase import LLMInterfaceBase
from lingu import cfg
from openai import OpenAI
import os
import instructor

class OpenrouterInterface(LLMInterfaceBase):
    def __init__(self, history, model_path=None, model_name=None, vision_model_name=None):
        model_name = model_name or cfg("local_llm", "model_name", default="openai/gpt-3.5-turbo")

        function_calling_model_name = cfg(
            "local_llm", "function_calling_model_name",
            default=model_name)
        
        openrouter_url = cfg("local_llm", "openrouter_url", default="https://openrouter.ai/api/v1")
        
        llama = OpenAI(base_url=openrouter_url, api_key=os.getenv("OPENROUTER_API_KEY"))
        create = instructor.patch(
            create=llama.chat.completions.create,
            mode=instructor.Mode.MD_JSON
        )
        super().__init__(history, model_name, function_calling_model_name, llama, create)
