from llama_cpp.llama_speculative import LlamaPromptLookupDecoding
from .languagemodelbase import LLM_Base
from lingu import cfg, log, exc, prompt, events, Prompt
from pydantic import BaseModel, Field
from .history import History
import instructor
import llama_cpp
import itertools
import json
import time
import os

gpu_layers = int(cfg("local_llm", "gpu_layers", default=17))
model_path = cfg("local_llm", "model_path", default="models/")
model_name = cfg(
    "local_llm", "model_name",
    default="openhermes-2.5-mistral-7b.Q5_K_M.gguf")
max_retries = int(cfg("local_llm", "max_retries", default=3))
context_length = int(cfg("local_llm", "context_length", default=2048))
max_tokens = int(cfg("local_llm", "max_tokens", default=1024))
repeat_penalty = float(cfg("local_llm", "repeat_penalty", default=1.4))
temperature = float(cfg("local_llm", "temperature", default=1.0))
top_p = float(cfg("local_llm", "top_p", default=1))
top_k = int(cfg("local_llm", "top_k", default=0))
tfs_z = int(cfg("local_llm", "tfs_z", default=1))
mirostat_mode = int(cfg("local_llm", "mirostat_mode", default=0))
mirostat_tau = int(cfg("local_llm", "mirostat_tau", default=5))
mirostat_eta = float(cfg("local_llm", "mirostat_eta", default=0.1))
verbose = bool(cfg("local_llm", "verbose", default=False))
n_threads = int(cfg("local_llm", "threads", default=6))
rope_freq_base = int(cfg("local_llm", "rope_freq_base", default=10000))
rope_freq_scale = float(cfg("local_llm", "rope_freq_scale", default=1.0))


class ChatAnswer(BaseModel):
    answer: str = Field(
        ..., description="Answer to the user. Must contain at least one word."
    )


class FunctionName(BaseModel):
    name_of_function_to_call: str = Field(
        ..., description="""Can be "None" if there is no function that can
        help with the user's request."""
    )


class LLamaCppInterface(LLM_Base):
    def __init__(
            self,
            history: History,
            model_path=model_path,
            model_name=model_name
    ):
        super().__init__()

        self.prompt = Prompt("")
        self.history = history
        self.model_path = model_path
        self.model_name = model_name

        self.model_full_path = os.path.join(
            self.model_path, self.model_name)

        self.llama = llama_cpp.Llama(
            model_path=self.model_full_path,
            n_gpu_layers=gpu_layers,
            chat_format="chatml",
            n_ctx=context_length,
            n_threads=n_threads,
            rope_freq_base=rope_freq_base,
            rope_freq_scale=rope_freq_scale,
            draft_model=LlamaPromptLookupDecoding(num_pred_tokens=2),
            logits_all=True,
            verbose=verbose
        )
        self.create = instructor.patch(
            create=self.llama.create_chat_completion_openai_v1,
            mode=instructor.Mode.JSON_SCHEMA
        )
        self.sleep = False
        self.abort = False
        events.add_listener(
            "escape_key_pressed",
            "*",
            self.abort_immediately)
        events.add_listener(
            "volume_interrupt",
            "*",
            self.abort_immediately)

        events.add_listener(
            "inference_start",
            "inference",
            lambda: self.set_sleep(True))
        events.add_listener(
            "inference_processing",
            "inference",
            lambda: self.set_sleep(False))
        events.add_listener(
            "inference_end",
            "inference",
            lambda: self.set_sleep(False))

        log.dbg("  [brain] warm up llm")
        self.warm_up()

    def abort_immediately(self):
        self.abort = True

    def set_sleep(self, value: bool):
        self.sleep = value

    def wait_wake(self):
        """Waits for wake-up, logging every second."""
        for count in itertools.cycle(range(10)):
            if not count:
                log.inf("  [brain] waiting for wake up")

            if not self.sleep:
                break

            time.sleep(0.1)

    def warm_up(self):
        self.wait_wake()
        extraction_stream = self.create(
            response_model=instructor.Partial[ChatAnswer],
            messages=[
                {
                    "role": "user",
                    "content": "say hi",
                },
            ],
            max_tokens=5,
            stream=True,
        )
        for token in extraction_stream:
            pass

    def generate_image(self, messages):
        unavail_str = "Image processing is not yet available for local models"
        for chunk in unavail_str:
            yield chunk

    def get_arguments_for_tool(self, user_content, fct_call):
        pass

    def decide_for_tool_to_call(self, messages, tools):
        if not tools:
            return False, None

        user_message, user_content = self.get_user_message(messages)

        function_names = ""
        for tool in tools:
            name = tool["function"]["name"]
            function_names += f' - \"{name}\"\n'

        messages_decide = [
            {
                "role": "system",
                "content": """You are a world class function calling algorithm.
                    Your task is to call a function when needed.
                    You need to decide if invoking a specific function
                    aids in successfully addressing a user's request.
                    You will be provided with a list of functions.""",
            },
            {
                "role": "user",
                "content": f"Available functions:\n"
                           f"{function_names}",
            },
            {
                "role": "user",
                "content": f"User's request:\n"
                           f'"{user_content}"',
            },
            {
                "role": "user",
                "content": "Return \"None\" if there is no function that "
                           "can help. Otherwise, return the name of the "
                           "function to call.",
            },
        ]

        log.inf(f"  [brain] {self.model_name} creating tool stream for "
                f"messages {messages}")

        self.wait_wake()
        extraction_stream = self.create(
            response_model=instructor.Partial[FunctionName],
            max_retries=max_retries,
            messages=messages_decide,
            max_tokens=500,
            stream=True,
        )

        for extraction in extraction_stream:
            obj = extraction.model_dump()
            print(obj)
            final_extraction = extraction

        extraction_stream = final_extraction
                
        fct_call = extraction_stream.name_of_function_to_call
        fct_call_stripped = fct_call.strip().lower()

        if fct_call_stripped == "none":
            log.inf(f"  [brain] {self.model_name} no function to call")
            return False, None

        log.inf(f"  [brain] {self.model_name} wants to "
                f"call function {fct_call}")

        tool = self.tools.get_tool_by_name(fct_call)
        if not tool:
            log.err(f"  [brain] {self.model_name} tool not found: {fct_call}")
            return False, None

        type_of_tool = type(tool.instance)
        log.dbg(f"  [brain] {self.model_name} tool found: {tool}")
        log.dbg(f"  [brain] tool type of instance: {type_of_tool}")

        messages_tool = [
            user_message
        ]

        log.dbg(f"  [brain] {self.model_name} "
                f"calling tool {fct_call} "
                f"with messages {messages}")
        try:
            self.wait_wake()
            extraction_stream = self.create(
                response_model=tool.instance,
                max_retries=max_retries,
                messages=messages_tool,
                max_tokens=500,
            )
            print(f"  [brain] tool {fct_call} called, "
                  f"extraction_stream: {extraction_stream}")
        except Exception as e:
            return_value = f"fail, reason: {str(e)}"
            log.hgh(f"  [brain] tool {fct_call} failed, reason: {str(e)}")
            exc(e)

        try:
            # executing function call
            if hasattr(extraction_stream, 'on_populated'):
                return_value = extraction_stream.on_populated()
                log.dbg(f"  [brain] tool {fct_call} returned: {return_value}")
            else:
                return_value = "success"

            if "success_prompt" in tool.language_info:
                self.prompt.add(
                    tool.language_info["success_prompt"]
                )
        except Exception as e:
            return_value = f"fail, reason: {str(e)}"
            if "fail_prompt" in tool.language_info:
                self.prompt.add(
                    tool.language_info["fail_prompt"]
                )
            exc(e)

        log.dbg(f"  [brain] {self.model_name} tool {fct_call} executed, "
                f"return value: {return_value}")

        message_tool_execution = {
            "role": "user",
            "content": f"""\
User's request:
"{user_content}"

To help address the user's request, the function {fct_call} was called with these parameters:
"{extraction_stream}"

The function returned the following data:
"{return_value}"

Your task is to carefully analyze and interpret the returned data.
Translate the returned data into an easily understandable form.
Imagine explaining it to someone without technical knowledge.
If the data is complex, simplify it.
Turn numbers, codes, or technical terms into plain explanations.
Using the function's returned data and your understanding, provide a clear response that addresses the user's request.
Extract the key information relevant to the user's request and present it in clear, easily understandable language.
Focus on providing a short, concise, and direct response to the user's query, rather than simply reproducing the raw data.\
"""
        }

        messages.append(message_tool_execution)
        #self.history.history.append(message_tool_execution)

        return True, return_value

    def generate(self, messages, tools=None):
        self.abort = False

        # log.dbg(f"  [brain] {self.model_name}"
        #         " generating answer for messages:"
        #         f" {messages}")

        self.prompt.start()

        try:
            log.dbg("  [brain] deciding for tool call")

            was_tool_called, return_value = \
                self.decide_for_tool_to_call(messages, tools)
        except Exception as e:
            log.err(f"  [brain] {self.model_name} tool"
                    f" decision failed: {e}")
            exc(e)
            was_tool_called = False

        prompt.add(self.prompt.get(), prioritize=True)

        # if tools:
        #     for tool in tools:
        #         name = tool["function"]["name"]
        #         description = tool["function"]["description"]

        #         log.dbg(f"  [brain] {self.model_name} tool name: "
        #                 f"{name} description: {description}")

        # Define the llm creation parameters in a dictionary
        params = {
            "max_tokens": max_tokens,
            "repeat_penalty": repeat_penalty,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "tfs_z": tfs_z,
            "mirostat_mode": mirostat_mode,
            "mirostat_tau": mirostat_tau,
            "mirostat_eta": mirostat_eta,
        }

        if was_tool_called:
            # rewrite system prompt, because instructions of tool may have been added

            # create new system prompt
            new_system_prompt_message = {
                'role': 'system',
                'content': prompt.system_prompt()
            }
            # remove first message from messages (existing system prompt)
            messages.pop(0)

            # insert system prompt as first message into messages
            messages.insert(0, new_system_prompt_message)

        # log.dbg(f"  [brain] Parameters: {params}")

        # Call the API using the dictionary unpacking
        self.wait_wake()
        if self.abort:
            return

        log.inf(f"  [brain] calling {model_name} with params:")
        log.inf('    {}'.format(json.dumps(params, indent=4)))
        # log.inf('  Tools:')
        # log.inf('=>{}'.format(json.dumps(tools, indent=4)))
        log.inf('  Messages:')
        log.inf('=>{}'.format(json.dumps(messages, indent=4)))

        response = self.llama.create_chat_completion_openai_v1(
            messages=messages,
            stream=True,
            **params
        )

        if not self.abort:
            for chunk in response:
                if self.abort:
                    break
                delta = chunk.choices[0].delta
                content = delta.content

                if content:
                    yield content

    def set_temperature(self, temperature):
        log.inf(f"  [brain] setting temperature to {temperature}")
        self.temperature = temperature

    def set_model(self, model_name):
        self.model = model_name
        return self.model
