from .languagemodelbase import LLM_Base
from openai import OpenAI
from lingu import log, cfg
from lingu import events
import base64
import json

# gpt-3.5-turbo
# gpt-4
# gpt-3.5-turbo-0613
# gpt-3.5-turbo-16k-0613
# gpt-4-0613
# gpt-4-32k-0613
openai_model = cfg("openai_model", default="gpt-3.5-turbo-1106")
vision_model = cfg("see", "model", default="gpt-4o")
vision_max_tokens = cfg("see", "max_tokens", default=1000)


class OpenaiInterface(LLM_Base):

    def __init__(self, model=openai_model):
        super().__init__()

        self.model = model
        print(f"  [brain] using model {self.model}")
        # import traceback
        # traceback.print_stack()

        self.client = OpenAI()
        self.fct_calls = []
        self.assistant_call = ""
        self.set_temperature(0.7)
        self.abort = False
        events.add_listener(
            "escape_key_pressed",
            "*",
            self.abort_immediately)
        events.add_listener(
            "volume_interrupt",
            "*",
            self.abort_immediately)

    def abort_immediately(self):
        self.abort = True

    def set_temperature(self, temperature):
        log.inf(f"  [brain] setting temperature to {temperature}")
        self.temperature = temperature

    def set_model(self, model_name):
        self.model = model_name
        print(f"  [brain] setting model to {self.model}")
        # import traceback
        # traceback.print_stack()
        return self.model

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

    def generate_image(
            self,
            messages,
            prompt: str,
            image_path: str,
            image_source: str
    ):
        self.abort = False

        base64_image = self.encode_image(image_path)
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        })

        params = {
            "model": vision_model,
            # "temperature": self.temperature,
            "messages": messages,
            "stream": True,
            "max_tokens": vision_max_tokens,
        }

        log.inf("  [brain] calling gpt vision with params:")
        log.inf('    {}'.format(json.dumps(params, indent=4)))
        log.inf('  Messages:')
        log.inf('=>{}'.format(json.dumps(messages, indent=4)))

        response = self.client.chat.completions.create(**params)

        log.inf('  <= stream')

        if not self.abort:
            for chunk in response:
                if self.abort:
                    break
                delta = chunk.choices[0].delta
                content = delta.content
                if content:
                    yield content

    def generate(self, text, messages, tools=None):
        self.abort = False

        def add_fct(fct):
            fct["args"] = json.loads(fct["arguments"])
            self.fct_calls.append(fct)
            events.trigger("function_call_request", "brain", fct)

        print(f"  [brain] generating with model {self.model}")
        params = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": messages,
            # prevent model from constantly saying "but, hey" bcs that sucks
            "logit_bias": {35309: -100, 36661: -100},
            "stream": True,
        }

        if tools and len(tools) > 0:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        log.inf("  [brain] calling openai with params:")
        log.inf('    {}'.format(json.dumps(params, indent=4)))
        log.inf('  Tools:')
        log.inf('=>{}'.format(json.dumps(tools, indent=4)))
        log.inf('  Messages:')
        log.inf('=>{}'.format(json.dumps(messages, indent=4)))

        response = self.client.chat.completions.create(**params)

        log.inf('  <= stream')

        fct = {}
        self.assistant_call = ""

        self.tool_calls_message = {
                         "content": None,
                         "role": "assistant",
                         "tool_calls": []
                       }
        if not self.abort:
            # The following "for chunk in response:" can throw ApiError:
            #   raise APIError(
            #     openai.APIError: An error occurred during streaming
            #   File "D:\Linguflex\Linguflex\lingu\modules\brain\handlers\openai_interface.py", line 130, in generate
            #     for chunk in response:

            for chunk in response:

                if self.abort:
                    break
                delta = chunk.choices[0].delta
                content = delta.content

                if delta.tool_calls:

                    tool = delta.tool_calls[0]

                    if tool.id:

                        if "id" in fct:
                            self.tool_calls_message["tool_calls"].append({
                                "id": fct["id"],
                                "function": {
                                    "arguments": fct["arguments"],
                                    "name": fct["name"]
                                },
                                "type": "function"
                            })
                            add_fct(fct)

                        fct = {
                            "arguments": "",
                            "id": tool.id,
                            "name": tool.function.name
                        }
                        events.trigger("function_call_start", "brain", fct)
                    else:
                        fct["arguments"] += tool.function.arguments
                else:
                    if content:
                        yield content
                    elif chunk.choices[0].finish_reason:
                        if chunk.choices[0].finish_reason == "tool_calls":
                            self.tool_calls_message["tool_calls"].append({
                                "id": fct["id"],
                                "function": {
                                    "arguments": fct["arguments"],
                                    "name": fct["name"]
                                },
                                "type": "function"
                            })
                            add_fct(fct)

        # print(f"Recovered pieces: {self.tool_calls_message}")
        events.trigger("answer_finished", "brain", fct)

    def add_tools_to_history(self, tools, history):
        history.add_executed_tools(self.tool_calls_message, tools)
        # self.history.add_executed_tools(
        #     self.llm.tool_calls_message,
        #     tools
        # )        
