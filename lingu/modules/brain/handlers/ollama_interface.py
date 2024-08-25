from .llminterfacebase import LLMInterfaceBase
from lingu import cfg, log
from openai import OpenAI
import instructor
import ollama
import json

class OllamaInterface(LLMInterfaceBase):
    def __init__(self, history, model_path=None, model_name=None, vision_model_name=None):
        model_name = model_name or cfg("local_llm", "model_name", default="llama3.1:8b")
        vision_model_name = vision_model_name or cfg("see", "model_name", default="llava")
        self.vision_model = vision_model_name
        function_calling_model_name = cfg("local_llm", "function_calling_model_name", default="llama3.1:8b")
        ollama_url = cfg("local_llm", "ollama_url", default="http://localhost:11434/v1")


        llama = OpenAI(base_url=ollama_url, api_key="dummy")
        create = instructor.patch(
            create=llama.chat.completions.create,
            mode=instructor.Mode.JSON_SCHEMA
        )
        super().__init__(history, model_name, function_calling_model_name, llama, create)

    def generate_image(
            self,
            messages,
            prompt: str,
            image_path: str,
            image_source: str
    ):
        self.abort = False
        self.tool_executed = False

        if image_source == "screen":
            image_source = "desktop screenshot"

        full_prompt = f"This image was captured from a {image_source}.\nCarefully check this image to answer the following user request:\n{prompt}"

        messages = [
            {
                'role': 'user',
                'content': full_prompt,
                'images': [image_path]
            }
        ]

        log.inf(f"  [brain] calling ollama vision model {self.vision_model} with messages:")
        log.inf('=>{}'.format(json.dumps(messages, indent=4)))

        try:
            response = ollama.chat(
                model=self.vision_model,
                messages=messages, 
                stream=True
            )

            log.inf('  <= stream')

            if not self.abort:
                for chunk in response:
                    if self.abort:
                        break
                    content = chunk['message']['content']
                    if content:
                        yield content
        except Exception as e:
            log.err(f"  [brain] Error in generate_image: {str(e)}")
            yield f"An error occurred while processing the image: {str(e)}"
