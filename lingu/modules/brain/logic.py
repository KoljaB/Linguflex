from .handlers.openai_interface import OpenaiInterface
from .handlers.local_llm_interface import LocalLLMInterface
from .handlers.history import History
from lingu import log, cfg, prompt, Logic
from .state import state
import datetime


class BrainLogic(Logic):
    """
    Handles the core logic of the brain interface, including
    managing history and LLM interactions.
    """

    def __init__(self):
        """
        Initializes the BrainLogic with configurations and history management.
        """
        super().__init__()

        self.history = History(int(cfg("max_history_messages")))
        self.use_local_llm = bool(
            cfg("local_llm", "use_local_llm", default=False))

        if self.use_local_llm:
            log.inf("  [brain] using local language model")
            self.llm = LocalLLMInterface(self.history)
        else:
            log.inf("  [brain] using openai language model")
            self.llm = OpenaiInterface()

        self.tools = None
        self.abort = False

        self.add_listener("set_prompt", "mimic", self.set_prompt)
        self.add_listener("set_temperature", "*", self.set_temperature)

        self.add_listener(
            "escape_key_pressed",
            "*",
            self.abort_immediately)
        self.add_listener(
            "volume_interrupt",
            "*",
            self.abort_immediately)

    def abort_immediately(self):
        """
        Aborts the current process immediately.
        """
        self.abort = True

    def set_tools(self, tools):
        """
        Sets the tools available for the logic.

        Args:
            tools: The tools to be used.
        """
        self.tools = tools
        self.llm.set_tools(tools)

    def set_temperature(self, temperature):
        """
        Sets the temperature for the language model.

        Args:
            temperature: The temperature to set.
        """
        log.inf(f"  [brain] setting temperature to {temperature}")
        self.llm.set_temperature(temperature)

    def set_prompt(self, base_prompt):
        """
        Sets the base prompt for the language model.

        Args:
            base_prompt: The base prompt to set.
        """
        log.inf(f"  [brain] setting prompt to {base_prompt}")
        prompt.set_base_prompt(base_prompt)

    def init(self):
        """
        Initializes the BrainLogic, sets logic state to ready.
        """
        self.switch_language_model(state.model, save=False)
        self.ready()

    def set_max_tokens_per_msg(self, value):
        """
        Sets the maximum tokens per message.

        Args:
            value: The maximum number of tokens.
        """
        state.max_tokens_per_msg = value
        self.history.max_tokens_per_msg = value
        state.save()

    def set_max_messages(self, value):
        """
        Sets the maximum number of messages allowed in history.

        Args:
            value: The maximum number of messages.
        """
        state.max_messages = value
        self.history.max_history_messages = value
        state.save()

    def set_history_tokens(self, value):
        """
        Sets the maximum history tokens.

        Args:
            value: The maximum number of history tokens.
        """
        state.history_tokens = value
        self.history.max_history_tokens = value
        state.save()

    def switch_language_model(self,
                              model: str,
                              save=True):
        """
        Switches the language model.

        Args:
            model: The model to switch to.
            save: Whether to save the state after switching.
        """
        state.model = model
        self.llm.set_model(model)
        if save:
            state.save()

    def get_system_prompt(self):
        """
        Constructs and returns the system prompt string with the current date,
        including the day of the week.

        Returns:
            str: The system prompt with the current date
              and day of the week appended.
        """
        # Retrieve the existing prompt content, if any.
        prompt_content = prompt.get() if prompt.get() else ""

        # Append a newline for formatting, if the prompt has content.
        if prompt_content:
            prompt_content += "\n\n"

        # Get the current date and day of the week.
        current_date = datetime.datetime.now().strftime("%A, %Y-%m-%d")

        # Append the current date to the prompt content.
        prompt_content += "Current date: " + current_date

        return prompt_content

    def generate(
            self,
            text,
            tools_for_usertext=None,
            functions=None):
        """
        Generates a response from the language model.

        Args:
            text: The input text.
            tools_for_usertext: Tools for processing user text.
            functions: Additional functions.

        Returns:
            The generated response stream.
        """
        system_prompt_message = {
            'role': 'system',
            'content': prompt.system_prompt()
        }

        self.history.trim_tokens(
            [system_prompt_message],
            functions,
            state.model)

        self.history.user(text)

        log.inf(f"  history: {self.history.history}")

        assistant_response_stream = self.llm.generate(
            [system_prompt_message] + self.history.get(),
            tools_for_usertext)

        return assistant_response_stream

    def generate_image(
            self,
            text,
            image_path):

        """
        Generates an image-based response.

        Args:
            text: The input text.
            image_path: The path of the image to process.

        Returns:
            The generated response stream.
        """
        system_prompt_message = {
            'role': 'system',
            'content': prompt.get()
        }

        self.history.trim_tokens(
            [system_prompt_message],
            None,
            state.model)

        self.history.user(text, image_path)

        system_prompt_message = {
            'role': 'system',
            'content': prompt.get()
        }

        assistant_response_stream = self.llm.generate_image(
            [system_prompt_message] + self.history.get(1))

        return assistant_response_stream

    def create_assistant_answer(self,
                                user_text,
                                tools_for_usertext=None,
                                functions=None):
        """
        Creates an assistant answer for the given user text.

        Args:
            user_text: The user text to process.
            tools_for_usertext: Tools for processing user text.
            functions: Additional functions.
        """
        self.abort = False
        self.state.set_active(True)

        self.trigger("assistant_text_start")

        log.dbg("  [brain] creating assistant answer")
        assistant_response_stream = self.generate(
            user_text,
            tools_for_usertext,
            functions)

        assistant_text = ""
        log.dbg("  [brain] processing assistant answer")
        if not self.abort:
            for chunk in assistant_response_stream:
                if self.abort:
                    break
                assistant_text += chunk
                self.trigger("assistant_text", assistant_text)
                self.trigger("assistant_chunk", chunk)

        if self.abort:
            assistant_text += " (aborted)"

        if assistant_text:
            self.history.assistant(assistant_text)
        else:
            log.err("  [brain] no assistant text generated")

        self.trigger("assistant_text_complete", assistant_text)
        self.state.set_active(False)

    def create_assistant_image_answer(
            self,
            user_text,
            image_to_process):
        """
        Creates an assistant image answer for the given user text.

        Args:
            user_text: The user text to process.
            image_to_process: The image to process.
        """
        self.state.set_active(True)

        self.trigger("assistant_text_start")

        assistant_response_stream = self.generate_image(
            user_text,
            image_to_process)

        assistant_text = ""
        for chunk in assistant_response_stream:
            assistant_text += chunk
            self.trigger("assistant_text", assistant_text)
            self.trigger("assistant_chunk", chunk)

        if assistant_text:
            self.history.assistant(assistant_text)

        self.trigger("assistant_text_complete", assistant_text)
        self.state.set_active(False)

    def add_executed_tools_to_history(self, tools):
        """
        Adds executed tools to the history.

        Args:
            tools: The executed tools.
        """
        self.history.add_executed_tools(
            self.llm.tool_calls_message,
            tools
        )


logic = BrainLogic()
