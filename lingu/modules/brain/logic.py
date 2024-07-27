from .handlers.history import History
from lingu import log, cfg, prompt, Logic
from .state import state
import datetime


max_history_messages = int(cfg("max_history_messages", default=12))
max_tokens_per_msg = int(cfg("max_tokens_per_msg", default=1000))
max_history_tokens = int(cfg("max_history_tokens", default=7000))
use_local_llm = bool(cfg("local_llm", "use_local_llm", default=False))
model_provider = cfg("local_llm", "model_provider", default="llama.cpp")
model_name = cfg(
    "local_llm", "model_name",
    default="openhermes-2.5-mistral-7b.Q5_K_M.gguf")

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

        self.history = History(
            max_history_messages,
            max_tokens_per_msg,
            max_history_tokens
            )

        if use_local_llm:
            if model_provider == "ollama":
                log.inf(f"  [brain] using local language model \"{model_name}\" with ollama provider")
                from .handlers.ollama_interface import OllamaInterface
                self.llm = OllamaInterface(self.history)
            elif model_provider == "lmstudio":
                log.inf(f"  [brain] using local language model \"{model_name}\" with lmstudio provider")
                from .handlers.lmstudio_interface import LMStudioInterface
                self.llm = LMStudioInterface(self.history)
            else:
                log.inf(f"  [brain] using local language model \"{model_name}\" with llama.cpp provider")
                self.llm = LLamaCppInterface(self.history)
                from .handlers.llama_cpp_interface import LLamaCppInterface
        else:
            log.inf("  [brain] using openai language model")
            from .handlers.openai_interface import OpenaiInterface
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
            [system_prompt_message] + self.history.get(purge_images=True),
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
                if not assistant_text and not chunk:
                    continue
                if not assistant_text and chunk:
                    self.trigger("assistant_text_start")

                assistant_text += chunk
                self.trigger("assistant_text", assistant_text)
                self.trigger("assistant_chunk", chunk)

        if self.abort:
            assistant_text += " (aborted)"

        if assistant_text:
            self.history.assistant(assistant_text)
            self.trigger("assistant_text_complete", assistant_text)
        else:
            log.inf("  [brain] no assistant text generated")

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
