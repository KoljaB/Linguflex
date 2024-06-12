from llama_cpp.llama_speculative import LlamaPromptLookupDecoding
from .languagemodelbase import LLM_Base
from lingu import cfg, log, exc, prompt, events, Prompt
from pydantic import BaseModel, Field
from .history import History
from openai import OpenAI
import instructor
import itertools
import json
import time
import os

SHOW_DEBUG = True

gpu_layers = int(cfg("local_llm", "gpu_layers", default=17))
model_path = cfg("local_llm", "model_path", default="models/")
model_name = cfg(
    "local_llm", "model_name",
    default="gemma:7b")
function_calling_model_name = cfg(
    "local_llm", "function_calling_model_name",
    default="llama2")
max_retries = int(cfg("local_llm", "max_retries", default=6))
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
ollama_url = cfg("local_llm", "ollama_url", default="http://localhost:11434/v1")


class ChatAnswer(BaseModel):
    answer: str = Field(
        ..., description="Answer to the user. Must contain at least one word."
    )


class FunctionName(BaseModel):
    name_of_function_to_call: str = Field(
        ..., description="""Pass "NOT_APPLICABLE" if there is no function that can help or the functions are unrelated to the query. Otherwise, pass the name of the function to call."""
    )


class OllamaInterface(LLM_Base):
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
        self.function_calling_model_name = function_calling_model_name

        self.llama = OpenAI(
            base_url=ollama_url,
            api_key="ollama")

        self.create = instructor.patch(
            create=self.llama.chat.completions.create,
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
            model=self.model_name,
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

    def _get_tool_example(
            self,
            tool_name,
            example_type):

        tool = self.tools.get_tool_by_name(tool_name)
        if not tool:
            return None

        if example_type == "function_name":
            if 'function_name_examples' in tool.language_info:
                return tool.language_info['function_name_examples']
            else:
                return None
        elif example_type == "function_arguments":
            if 'function_arguments_examples' in tool.language_info:
                return tool.language_info['function_arguments_examples']
            else:
                return None

    def decide_for_tool_to_call(self, messages, tools):
        TOOL_CALL_LOOP_MESSAGES_APPENDED = []
        TOOL_CALL_NEXT_LOOP_MESSAGES_APPENDED = []

        TOOL_CALL_LOOP_LATEST_EXTRACTION = None
        TOOL_CALL_NEXT_LOOP_LATEST_EXTRACTION = None

        TOOL_CALL_PASS_INITIAL = False

        if not tools:
            return False, None

        user_message, user_content = self.get_user_message(messages)

        function_names = ""
        tool_examples_name = []
        tool_examples_arguments = []
        for tool in tools:
            name = tool["function"]["name"]
            function_names += f' - \"{name}\"\n'

            tool_example_name = self._get_tool_example(
                name, "function_name")
            tool_example_argument = self._get_tool_example(
                name, "function_arguments")
            if tool_example_name != None:
                tool_examples_name = tool_examples_name + tool_example_name
                log.dbg(f"  [TOOL INJECTION] INJECTING TOOL EXAMPLES: {tool_example_name}")
            if tool_example_argument != None:
                tool_examples_arguments = tool_examples_arguments + tool_example_argument
                log.dbg(f"  [TOOL INJECTION] INJECTING SUB TOOL EXAMPLES: {tool_example_argument}")

        messages_decide_1 = [
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
        ]

        messages_decide_2 = [
            {
                "role": "user",
                "content": f"User's request:\n"
                        f'"{user_content}"',
            },
            {
                "role": "user",
                "content": "Return \"NOT_APPLICABLE\" if there is no function that can help or the functions are unrelated to the query. Otherwise, pass the name of the function to call.",
            },
        ]

        # Set the tool call decision messages to the intial system message, + the examples that could be found on the tool, + the final system message
        messages_decide = messages_decide_1 + tool_examples_name + messages_decide_2

        for i in range(max_retries):
            # The tool call loop will automatically return (essentially ending the loop) if the tool call finishes successfully

            # We don't want to call the "decide what tool to use" function multiple times, so we only call it once
            if not TOOL_CALL_PASS_INITIAL:
                if len(TOOL_CALL_LOOP_MESSAGES_APPENDED) > 0:
                    messages_decide = messages_decide + TOOL_CALL_LOOP_MESSAGES_APPENDED

                log.inf(f"  [brain] {self.function_calling_model_name} creating tool stream for "
                        f"messages {messages}")

                self.wait_wake()

                if SHOW_DEBUG:
                    print("DECISION MESSAGES:" + str(messages_decide))

                try:
                    extraction_stream = self.create(
                        response_model=instructor.Partial[FunctionName],
                        max_retries=max_retries,
                        messages=messages_decide,
                        model=self.function_calling_model_name,
                        max_tokens=500,
                        temperature=0.1,
                        stream=True,
                    )

                    for extraction in extraction_stream:
                        if SHOW_DEBUG:
                            print(extraction)
                        TOOL_CALL_LOOP_LATEST_EXTRACTION = extraction
                        final_extraction = extraction

                    extraction_stream = final_extraction

                    fct_call = extraction_stream.name_of_function_to_call
                    try:
                        fct_call_stripped = fct_call.strip().lower()
                    except:
                        log.err(f"  [brain] {self.function_calling_model_name} tool stream failed, reason: Failed to convert to stripped lowercase.")
                        _LOOP_MESSAGES_APPENDED = [
                            {
                                "role": "assistant",
                                "content": "" + str(TOOL_CALL_LOOP_LATEST_EXTRACTION) + "",
                            },
                            {
                                "role": "user",
                                "content": f"You need to pass a valid function name. Either pass the name of the function you want to call or pass \"NOT_APPLICABLE\" if there is no function that can help or the functions are unrelated to the query."
                            }
                        ]
                        TOOL_CALL_LOOP_MESSAGES_APPENDED = TOOL_CALL_LOOP_MESSAGES_APPENDED + _LOOP_MESSAGES_APPENDED
                        log.dbg(f"  [brain] {self.function_calling_model_name} TS1 stream failed, attempting again")
                        continue

                    if fct_call_stripped == "not_applicable":
                        log.inf(f"  [brain] {self.function_calling_model_name} no function to call")
                        return False, None

                    log.inf(f"  [brain] {self.function_calling_model_name} wants to "
                            f"call function {fct_call}")

                    tool = self.tools.get_tool_by_name(fct_call)

                except Exception as e:
                    log.err(f"  [brain] {self.function_calling_model_name} tool stream failed, reason: {str(e)}")
                    _LOOP_MESSAGES_APPENDED = [
                        {
                            "role": "assistant",
                            "content": "" + str(TOOL_CALL_LOOP_LATEST_EXTRACTION) + "",
                        },
                        {
                            "role": "user",
                            "content": f"There was an error while trying to call the function. Here is the error: {str(e)}\nPlease try again."
                        }
                    ]
                    TOOL_CALL_LOOP_MESSAGES_APPENDED = TOOL_CALL_LOOP_MESSAGES_APPENDED + _LOOP_MESSAGES_APPENDED
                    log.dbg(f"  [brain] {self.function_calling_model_name} Tool stream failed, attempting again")
                    continue

                if not tool:
                    log.err(f"  [brain] {self.function_calling_model_name} tool not found: {fct_call}")
                    _LOOP_MESSAGES_APPENDED = [
                        {
                            "role": "assistant",
                            "content": f"{extraction_stream}"
                        },
                        {
                            "role": "user",
                            "content": f"That is not a valid function. Using the proper format, please choose from the list of available functions: {function_names}"
                        }
                    ]
                    TOOL_CALL_LOOP_MESSAGES_APPENDED = TOOL_CALL_LOOP_MESSAGES_APPENDED + _LOOP_MESSAGES_APPENDED
                    log.dbg(f"  [brain] {self.function_calling_model_name} TS1 stream failed, attempting again")
                    continue

                type_of_tool = type(tool.instance)
                log.dbg(f"  [brain] {self.function_calling_model_name} tool found: {tool}")
                log.dbg(f"  [brain] tool type of instance: {type_of_tool}")

                TOOL_CALL_PASS_INITIAL = True

            # Now that there has been no errors, we can call the tool

            messages_tool_1 = [
                user_message
            ]

            #There is no system message to append so it's just examples, then the user message
            messages_tool = tool_examples_arguments + messages_tool_1

            if len(TOOL_CALL_NEXT_LOOP_MESSAGES_APPENDED) > 0:
                messages_tool = messages_tool + TOOL_CALL_NEXT_LOOP_MESSAGES_APPENDED

            log.dbg(f"  [brain] {self.function_calling_model_name} "
                    f"calling tool {fct_call} "
                    f"with messages {messages}")
            
            self.wait_wake()
            
            try:
                
                if SHOW_DEBUG:
                    print("TOOL CALL MESSAGES:" + str(messages_tool))

                extraction_stream = self.create(
                    response_model=instructor.Partial[tool.instance],
                    max_retries=max_retries,
                    messages=messages_tool,
                    model=self.function_calling_model_name,
                    max_tokens=500,
                    temperature=0.1,
                    stream=True,
                )

                for extraction in extraction_stream:
                    if SHOW_DEBUG:
                        print(extraction)
                    TOOL_CALL_NEXT_LOOP_LATEST_EXTRACTION = extraction
                    final_extraction = extraction

                extraction_stream = final_extraction
                
            except Exception as e:
                log.err(f"  [brain] {self.function_calling_model_name} tool stream failed, reason: {str(e)}")
                _LOOP_MESSAGES_APPENDED = [
                    {
                        "role": "assistant",
                        "content": "" + str(TOOL_CALL_NEXT_LOOP_LATEST_EXTRACTION) + "",
                    },
                    {
                        "role": "user",
                        "content": f"There was an error while trying to call the function. Here is the error: {str(e)}\nPlease try again."
                    }
                ]
                TOOL_CALL_NEXT_LOOP_MESSAGES_APPENDED = TOOL_CALL_NEXT_LOOP_MESSAGES_APPENDED + _LOOP_MESSAGES_APPENDED
                log.dbg(f"  [brain] {self.function_calling_model_name} Tool stream failed, attempting again")
                continue


            # This is from when there is an error with the tool call. This can happen when there are invalid search terms, etc.
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
                log.err(f"  [brain] {self.function_calling_model_name} tool stream failed, reason: {str(e)}")
                _LOOP_MESSAGES_APPENDED = [
                    {
                        "role": "assistant",
                        "content": "" + str(TOOL_CALL_NEXT_LOOP_LATEST_EXTRACTION) + "",
                    },
                    {
                        "role": "user",
                        "content": f"There was an error while trying to call the function. Here is the error: {str(e)}\nPlease try again."
                    }
                ]
                TOOL_CALL_NEXT_LOOP_MESSAGES_APPENDED = TOOL_CALL_NEXT_LOOP_MESSAGES_APPENDED + _LOOP_MESSAGES_APPENDED
                log.dbg(f"  [brain] {self.function_calling_model_name} Tool stream failed, attempting again")
                continue

            log.dbg(f"  [brain] {self.function_calling_model_name} tool {fct_call} executed, "
                    f"return value: {return_value}")
            
            # The info to return to the user

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
Focus on providing a short, concise, and direct response to the user's query, rather than simply reproducing the raw data.
DO NOT include the name of the function in your response.
DO NOT include emojis in your response.
DO NOT say "here is the simplifed response" just make your response the simplified response.\
"""
            }

            messages.append(message_tool_execution)

            return True, return_value

        return False, "The function calling model failed to call a function after multiple retries."

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
            "temperature": temperature,
            "top_p": top_p,
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

        response = self.llama.chat.completions.create(
            messages=messages,
            stream=True,
            model=self.model_name,
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
