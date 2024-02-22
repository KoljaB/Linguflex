from llama_cpp.llama_speculative import LlamaPromptLookupDecoding
from .languagemodelbase import LLM_Base
from lingu import cfg, log, exc, prompt, Prompt
from pydantic import BaseModel, Field, field_validator
from .history import History
import instructor
import llama_cpp
from typing import Annotated
from pydantic.functional_validators import AfterValidator

gpu_layers = int(cfg("local_llm", "gpu_layers", default=17))
model_path = cfg("local_llm", "model_path", default="models/")
model_name = cfg(
    "local_llm", "model_name",
    default="openhermes-2.5-mistral-7b.Q5_K_M.gguf")
max_retries = int(cfg("local_llm", "max_retries", default=3))
max_tokens = int(cfg("local_llm", "max_tokens", default=1024))
repeat_penalty = float(cfg("local_llm", "repeat_penalty", default=1.4))
temperature = float(cfg("local_llm", "temperature", default=1.0))
top_p = float(cfg("local_llm", "top_p", default=1))
top_k = int(cfg("local_llm", "top_k", default=0))
tfs_z = int(cfg("local_llm", "tfs_z", default=1))
mirostat_mode = int(cfg("local_llm", "mirostat_mode", default=0))
mirostat_tau = int(cfg("local_llm", "mirostat_tau", default=5))
mirostat_eta = float(cfg("local_llm", "mirostat_eta", default=0.1))


class ChatAnswer(BaseModel):
    answer: str = Field(
        ..., description="Answer to the user. Must contain at least one word. DO NOT LEAVE BLANK!"
    )


class FunctionName(BaseModel):
    name_of_function_to_call: str = Field(
        ..., description="""Can be "None" if there is no function that can
        help with the user's request."""
    )


class LocalLLMInterface(LLM_Base):
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
        self.model_full_path = f"{model_path}{model_name}"
        self.llama = llama_cpp.Llama(
            model_path=self.model_full_path,
            n_gpu_layers=gpu_layers,
            chat_format="chatml",
            n_ctx=2048,
            draft_model=LlamaPromptLookupDecoding(num_pred_tokens=2),
            logits_all=True,
            verbose=False
        )
        self.create = instructor.patch(
            create=self.llama.create_chat_completion_openai_v1,
            mode=instructor.Mode.JSON_SCHEMA
        )
        log.dbg("  [brain] warm up llm")
        self.warm_up()

    def warm_up(self):
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
            return

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

        extraction_stream = self.create(
            response_model=FunctionName,
            max_retries=max_retries,
            messages=messages_decide,
            max_tokens=100,
        )

        fct_call = extraction_stream.name_of_function_to_call
        fct_call_stripped = fct_call.strip().lower()

        if fct_call_stripped == "none":
            log.inf(f"  [brain] {self.model_name} no function to call")
            return False, None

        log.inf(f"  [brain] {self.model_name} wants to call function {fct_call}")

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

        log.dbg(f"  [brain] {self.model_name} calling tool {fct_call} with messages {messages}")
        try:
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
            "content":
                f"User's request:\n"
                f'"{user_content}"\n'
                f"The function {fct_call} was called to aid in adressing the "
                "user's request.\n"
                f"The function {fct_call} was called with these parameters:\n"
                f'"{extraction_stream}"\n'
                f"The function {fct_call} returned:\n"
                f'"{return_value}"\n'
                f"Your task is to evaluate the return of the function call. "
                "Report it in your own words by answering the user's request."
        }
        messages.append(message_tool_execution)
        self.history.history.append(message_tool_execution)

        return True, return_value

    def generate(self, messages, tools=None):
        log.dbg(f"  [brain] {self.model_name}"
                " generating answer for messages:"
                f" {messages}")

        self.prompt.start()

        self.decide_for_tool_to_call(messages, tools)

        prompt.add(self.prompt.get(), prioritize=True)

        if tools:
            for tool in tools:
                name = tool["function"]["name"]
                description = tool["function"]["description"]

                log.dbg(f"  [brain] {self.model_name} tool name: "
                        f"{name} description: {description}")

        answer = ""

        log.dbg(f"  [brain] {self.model_name} creating extraction stream")
        log.dbg(f"  [brain] Parameters: max_retries={max_retries}, "
                f"messages={messages}, max_tokens={max_tokens}, "
                f"repeat_penalty={repeat_penalty}, temperature={temperature}, "
                f"top_p={top_p}, top_k={top_k}, tfs_z={tfs_z}, "
                f"mirostat_mode={mirostat_mode}, mirostat_tau={mirostat_tau}, "
                f"mirostat_eta={mirostat_eta}")

        extraction_stream = self.create(
            response_model=instructor.Partial[ChatAnswer],
            max_retries=max_retries,
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
            repeat_penalty=repeat_penalty,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            tfs_z=tfs_z,
            mirostat_mode=mirostat_mode,
            mirostat_tau=mirostat_tau,
            mirostat_eta=mirostat_eta,
        )

        log.dbg(f"  [brain] {self.model_name} processing extraction stream")

        for extraction in extraction_stream:
            if not extraction.answer:
                continue

            print(f"\r{extraction.answer}", end="", flush=True)

            # Calculate the length of the new part in the extraction.
            new_part_length = len(extraction.answer) - len(answer)

            # Check if there is a new part in the extraction.
            if new_part_length > 0:
                # Extract the new part from the extraction.
                new_part = extraction.answer[-new_part_length:]

                # Yield the new part.
                yield new_part

            # Update the answer with the current extraction.
            answer = extraction.answer

        log.dbg(f"  [brain] {self.model_name} extraction stream processed")

    def set_temperature(self, temperature):
        log.inf(f"  [brain] setting temperature to {temperature}")
        self.temperature = temperature

    def set_model(self, model_name):
        self.model = model_name
        return self.model
