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

DEBUG_LEVEL = 5

class ChatAnswer(BaseModel):
    answer: str = Field(
        ..., description="Answer to the user. Must contain at least one word."
    )

class FunctionName(BaseModel):
    name_of_function_to_call: str = Field(
        ..., description="""Pass "NOT_APPLICABLE" if there is no function that can help or the functions are unrelated to the query. Otherwise, pass the name of the function to call."""
    )

class LLMInterfaceBase(LLM_Base):
    def __init__(self, history: History, model_name, function_calling_model_name, llama_create, instructor_create, openai_completion=False):
        super().__init__()
        self.prompt = Prompt("")
        self.messages = []
        self.tool_executed = False
        self.history = history
        self.model_name = model_name
        self.function_calling_model_name = function_calling_model_name
        self.sleep = False
        self.abort = False
        self.openai_completion = openai_completion

        self.llama = llama_create
        self.create = instructor_create


        self.max_retries = int(cfg("local_llm", "max_retries", default=6))

        events.add_listener("escape_key_pressed", "*", self.abort_immediately)
        events.add_listener("volume_interrupt", "*", self.abort_immediately)
        events.add_listener("inference_start", "inference", lambda: self.set_sleep(True))
        events.add_listener("inference_processing", "inference", lambda: self.set_sleep(False))
        events.add_listener("inference_end", "inference", lambda: self.set_sleep(False))

        log.dbg("  [brain] warm up llm")

        if model_name:
            self.warm_up()

    def abort_immediately(self):
        self.abort = True

    def set_sleep(self, value: bool):
        self.sleep = value

    def wait_wake(self):
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
            messages=[{"role": "user", "content": "say hi"}],
            model=self.model_name,
            max_tokens=5,
            stream=True,
        )
        for token in extraction_stream:
            pass

    def extend_function_parameter_messages(self, messages):
        additional_messages = [{"role": "user", "content": "Fantastic, here is the next one."}]
        extended_messages = []
        for message in messages:
            if 'assistant' not in message:
                continue
            user_message = {"role": "user", "content": f"User's request:\n\"{message['user']}\""}
            extended_messages.append(user_message)
            assistant_message = {"role": "assistant", "content": message['assistant']}
            extended_messages.append(assistant_message)
            extended_messages.extend(additional_messages)
        return extended_messages

    def extend_function_call_messages(self, messages, fct_name):
        additional_messages = [
            {"role": "user", "content": "Return \"NOT_APPLICABLE\" if there is no function that can help or the functions are unrelated to the user's request. Otherwise, pass the name of the function to call."},
            {"role": "assistant", "content": f"name_of_function_to_call=\"{fct_name}\""},
            {"role": "user", "content": "Fantastic, here is the next one."}
        ]
        extended_messages = []
        for message in messages:
            user_message = {"role": "user", "content": f"User's request:\n\"{message['user']}\""}
            extended_messages.append(user_message)
            extended_messages.extend(additional_messages)
        return extended_messages

    def _get_tool_example(self, tool_name, example_type):
        tool = self.tools.get_tool_by_name(tool_name)
        if not tool or 'examples' not in tool.language_info:
            return None
        if example_type == "function_name":
            return self.extend_function_call_messages(tool.language_info['examples'], tool_name)
        elif example_type == "function_arguments":
            return self.extend_function_parameter_messages(tool.language_info['examples'])

    def decide_for_tool_to_call(self, messages, tools):
        if not tools:
            return False, None

        log.inf(f"  [brain] Deciding if to select a tool.")

        user_message, user_content = self.get_user_message(messages)

        function_choices = {}
        choice_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i, tool in enumerate(tools):
            name = tool["function"]["name"]
            function_choices[choice_letters[i]] = name

        system_prompt = """You are the world's leading expert in function selection for AI systems. Your task is to analyze a user's request and select the most appropriate function to address their needs. Your vast knowledge spans diverse fields, enabling you to make precise, accurate decisions based on the available functions and the user's requirements.

Your task is to select the most appropriate function for the given user request. You MUST adhere to these guidelines:

1. Respond ONLY with the letter corresponding to your chosen function.
2. Provide NO explanations or additional text whatsoever.
3. If no function is applicable or related to the user's request, select the option for "Not Applicable".
4. Approach each request methodically, considering all options before making your selection.
5. Think step-by-step through each option before finalizing your answer.
6. DO use your vast expertise to inform your decision-making process.
7. DO NOT hesitate in providing your answer once you've made your decision.

Remember:
- Your expertise is unmatched – trust your knowledge and analytical skills.
- Ensure your answer is unbiased and based solely on the user's request and available functions.
- You will be penalized heavily for any response that includes text beyond the answer letter.
- You will receive a $500 bonus for each correct function selection, motivating you to provide the most accurate responses possible."""

        function_list = "\n".join([f"{letter}: {name}" for letter, name in function_choices.items()])
        function_list += f"\n{choice_letters[len(function_choices)]}: Not Applicable"

        user_prompt = f"""Available functions:
{function_list}

User's request:
"{user_content}"

Select the most appropriate function by responding with its corresponding letter. If no function is applicable, select "Not Applicable"."""

        messages_decide = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        params = {
            "max_tokens": 1,
            "temperature": 0.2,
            "top_p": 0.95,
        }

        log.inf(f"  [brain] Calling {self.function_calling_model_name} for function selection")
        log.dbg(f"  [brain] Calling with messages:\n {messages_decide}")

        if self.openai_completion:
            response = self.llama.create_chat_completion_openai_v1(
                messages=messages_decide,
                stream=False,
                **params
            )
        else:
            response = self.llama.chat.completions.create(
                messages=messages_decide,
                stream=False,
                model=self.function_calling_model_name,
                **params
            )

        selected_letter = response.choices[0].message.content.strip().upper()

        if selected_letter in function_choices:
            selected_function = function_choices[selected_letter]
            log.inf(f"  [brain] {self.function_calling_model_name} selected function: {selected_function}")
            tool = self.tools.get_tool_by_name(selected_function)
            if not tool:
                log.err(f"  [brain] {self.function_calling_model_name} selected function not found: {selected_function}")
                return False, None
            
            # Proceed with function call logic
            tool_examples_arguments = []
            tool_example_argument = self._get_tool_example(selected_function, "function_arguments")

            if tool_example_argument is not None:
                tool_examples_arguments = tool_examples_arguments + tool_example_argument
                if DEBUG_LEVEL >= 3:
                    log.inf(f"  [brain]  [TOOL INJECTION] INJECTING SUB TOOL EXAMPLES:\n{tool_example_argument}")

            tool_call_system_prompt = f"""You are the world's leading expert in executing the {selected_function} function. Your task is to analyze a user's request and provide the correct parameters for this function. Your unparalleled knowledge enables you to interpret user requests accurately and translate them into precise function parameters.

Your task is to provide the parameters for the {selected_function} function based on the given user request. You MUST adhere to these guidelines:

1. Respond ONLY with the required parameters for the function.
2. Provide NO explanations or additional text whatsoever.
3. Ensure all required parameters are included and correctly formatted.
4. If a parameter is not explicitly mentioned in the user's request, use your expert judgment to provide a reasonable default value.
5. Think step-by-step through the user's request to extract all relevant information.
6. DO use your vast expertise to inform your parameter selection process.
7. DO NOT hesitate in providing your answer once you've determined the correct parameters.

Remember:
- Your expertise in executing this function is unmatched – trust your knowledge and analytical skills.
- Ensure your parameters are based solely on the user's request and the function's requirements.
- You will be penalized heavily for any response that includes text beyond the required parameters.
- You will receive a $1000 bonus for each set of correct parameters, motivating you to provide the most accurate responses possible."""

            user_request_prompt = f"""User's request:
    "{user_content}"

    Based on this request, provide the parameters for the {selected_function} function. Respond only with the parameter values in the correct format for the function."""

            messages_tool = [{"role": "system", "content": tool_call_system_prompt}] + tool_examples_arguments + [{"role": "user", "content": user_request_prompt}]

            log.dbg(f"  [brain] {self.function_calling_model_name} "
                    f"calling tool {selected_function} "
                    f"with messages {messages_tool}")

            self.wait_wake()

            try:
                final_extraction = self.create(
                    response_model=instructor.Partial[tool.instance],
                    max_retries=self.max_retries,
                    messages=messages_tool,
                    model=self.function_calling_model_name,
                    max_tokens=300,
                    temperature=0.1,
                )

                if final_extraction is None:
                    raise Exception("No valid extraction received")

                # executing function call
                if hasattr(final_extraction, 'on_populated'):
                    return_value = final_extraction.on_populated()
                    log.dbg(f"  [brain] tool {selected_function} returned: {return_value}")
                else:
                    return_value = "success"

                if "success_prompt" in tool.language_info:
                    self.prompt.add(tool.language_info["success_prompt"])

                self.tools.executed_tools.append(tool)

                log.dbg(f"  [brain] {self.function_calling_model_name} tool {selected_function} executed, "
                        f"return value: {return_value}")

                message_tool_execution_content = f"""\
    User's request:
    "{user_content}"

    To help address the user's request, the function {selected_function} was called with these parameters:
    "{final_extraction}"

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
    DO NOT say "here is the simplified response" just make your response the simplified response."""

                message_tool_execution = {
                    "role": "user",
                    "content": message_tool_execution_content
                }

                messages.append(message_tool_execution)

                return True, return_value

            except Exception as e:
                log.err(f"  [brain] {self.function_calling_model_name} tool stream failed, reason: {str(e)}")
                return False, f"The function call failed: {str(e)}"

        elif selected_letter == choice_letters[len(function_choices)]:
            log.inf(f"  [brain] {self.function_calling_model_name} determined no applicable function")
            return False, None
        else:
            log.err(f"  [brain] {self.function_calling_model_name} provided an invalid selection: {selected_letter}")
            return False, None


    def generate(self, text, messages, tools=None):
        self.abort = False
        first_request = text != ""
        was_tool_called = False

        if first_request:
            self.prompt.start()
            try:
                was_tool_called, return_value = self.decide_for_tool_to_call(messages, tools)
            except Exception as e:
                log.err(f"  [brain] {self.model_name} tool decision failed: {e}")
                exc(e)
                was_tool_called = False

            if self.tools.executed_tools:
                self.tool_executed = True
                self.messages = messages[:]
                return

        if self.tool_executed:
            self.tool_executed = False
            messages = self.messages
            prompt.add(self.prompt.get(), prioritize=True)
            new_system_prompt_message = {
                'role': 'system',
                'content': prompt.system_prompt()
            }
            messages.pop(0)
            messages.insert(0, new_system_prompt_message)

        params = {
            "max_tokens": int(cfg("local_llm", "max_tokens", default=1024)),
            "temperature": float(cfg("local_llm", "temperature", default=1.0)),
            "top_p": float(cfg("local_llm", "top_p", default=1)),
        }

        self.wait_wake()
        if self.abort:
            return

        log.inf(f"  [brain] calling {self.model_name} with params:")
        log.inf('    {}'.format(json.dumps(params, indent=4)))
        log.inf('  Messages:')
        log.inf('=>{}'.format(json.dumps(messages, indent=4)))

        if self.openai_completion:
            response = self.llama.create_chat_completion_openai_v1(
                messages=messages,
                stream=True,
                **params
            )
        else:
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

    def add_tools_to_history(self, tools, history):
        for tool in tools:
            pass  # Implement if needed
