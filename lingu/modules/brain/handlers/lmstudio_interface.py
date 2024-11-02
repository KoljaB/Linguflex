from .llminterfacebase import LLMInterfaceBase
from lingu import cfg
from openai import OpenAI
import instructor

class LMStudioInterface(LLMInterfaceBase):
    def __init__(self, history, model_path=None, model_name=None, vision_model_name=None):
        model_name = model_name or cfg("local_llm", "model_name", default="llama3.1:8b")

        function_calling_model_name = cfg(
            "local_llm", "function_calling_model_name",
            default=model_name)
        
        lmstudio_url = cfg("local_llm", "lmstudio_url", default="http://localhost:1234/v1")

        print(f"Using model: {model_name}")
        print(f"Using function calling model: {function_calling_model_name}")
        print(f"Using LLM Studio URL: {lmstudio_url}")
        
        llama = OpenAI(base_url=lmstudio_url, api_key="dummy")
        create = instructor.patch(
            create=llama.chat.completions.create,
            mode=instructor.Mode.MD_JSON
        )
        super().__init__(history, model_name, function_calling_model_name, llama, create)
