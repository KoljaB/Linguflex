from .llminterfacebase import LLMInterfaceBase
from lingu import cfg
from openai import OpenAI
import instructor

class LMStudioInterface(LLMInterfaceBase):
    def __init__(self, history, model_path=None, model_name=None, vision_model_name=None):
        function_calling_model_name = cfg("local_llm", "function_calling_model_name", default="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf")
        lmstudio_url = cfg("local_llm", "lmstudio_url", default="http://localhost:1234/v1")
        
        llama = OpenAI(base_url=lmstudio_url, api_key="dummy")
        create = instructor.patch(
            create=llama.chat.completions.create,
            mode=instructor.Mode.MD_JSON
        )
        super().__init__(history, model_name, function_calling_model_name, llama, create)
