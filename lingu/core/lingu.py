from ..modules.brain.logic import BrainLogic
from .repeat import execute_repeat
from lingu.ui.main import UI
from .modules import Modules
from .events import events
from .prompt import prompt
from lingu import log, notify
from .tools import Tools
import threading
import time


class Lingu:
    """Represents the main application for Lingu.

    This class initializes the Lingu application,
    setting up necessary modules and user interface.

    Attributes:
        app: The main application object.
        modules: An instance of Modules containing all loaded modules.
        ui: The user interface object for the application.
    """

    def __init__(self, app):
        """Initializes the Lingu class with the provided application.

        Args:
            app: The main application object to be used with Lingu.
        """
        self.app = app

        events.add_listener(
            "user_text_complete",
            "listen",
            lambda text: threading.Thread(
                target=self.create_assistant_answer_loop,
                args=(text,)
            ).start()
        )

    def start(self):
        """
        Starts the Lingu application by loading modules
        and initializing the UI.
        """
        self.modules = Modules()
        self.modules.create()
        self.modules.load_start_modules()
        self.ui = UI(self.app, self.modules.all)

        # start in thread so that the UI can be shown
        self.init_thread = threading.Thread(target=self._init)
        self.init_thread.start()

    def _init(self):
        """
        Initializes the Lingu application by loading modules,
        importing language files, and setting the UI ready.
        """

        notify("Start", "Starting modules", -1, "custom", "🚀")

        self.modules.post_process()
        self.modules.init()
        self.modules.load_delayed_modules()
        self.modules.import_language_files()
        self.modules.post_process()
        self.modules.init_finished()
        self.modules.wait_ready()
        self.ui.set_symbols_ready()
        self.modules.set_ready_event()
        self.tools = Tools(self.modules.get_inference_objects())

        self.main_worker = threading.Thread(
            target=self._main_worker
        )
        self.main_worker.daemon = True
        self.main_worker.start()

        self.brainlogic: BrainLogic = self.modules.all["brain"]["logic"]
        self.brainlogic.set_tools(self.tools)

        notify("Ready", "Modules loaded.", 5000, "success", "✅")

    def _main_worker(self):
        """
        Responsible for executing repeatable functions
        """
        while True:
            execute_repeat(self.modules.all.values())
            time.sleep(0.1)

    def create_assistant_answer_loop(self, text):
        """
        Prepares the assistant answer for the given user text.
        Calls tools if necessary.
        Loops tool calls until assistant answer is ready.
        """
        seelogic = None
        if "see" in self.modules.all:
            seelogic = self.modules.all["see"]["logic"]

        tools_for_usertext, functions = self.tools.get_tools(text)
        log.dbg(f"Tools:\n{tools_for_usertext}")

        self.tools.executed_tools = []
        prompt.start()
        self.tools.start_execution()
        self.brainlogic.create_assistant_answer(
            text,
            tools_for_usertext=tools_for_usertext,
            functions=functions
        )

        while self.tools.executed_tools:

            # add executed tools to history
            self.brainlogic.add_executed_tools_to_history(
                self.tools.executed_tools)

            # prepare final answer (or call tools again)
            self.tools.executed_tools = []
            prompt.start()
            if seelogic and seelogic.image_to_process:
                # if executed tool needs vision, call vision
                self.brainlogic.create_assistant_image_answer(
                    text,
                    seelogic.image_to_process
                )
            else:
                tools_for_usertext, functions = self.tools.get_tools(text)
                log.dbg(f"Tools:\n{tools_for_usertext}")

                prompt.add(self.tools.get_prompt(), prioritize=True)
                self.tools.start_execution()
                self.brainlogic.create_assistant_answer(
                    "",
                    tools_for_usertext=tools_for_usertext,
                    functions=functions
                )
