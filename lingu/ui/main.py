from .symbol import Symbol, SymbolConfig
from PyQt6.QtCore import QTimer, QPoint
from lingu.core.events import events
from lingu.core.settings import cfg
from .text import Text, TextConfig
from .windows import Windows
from PyQt6 import QtGui
import time

USERTEXT_COLOR = QtGui.QColor(255, 200, 61)
ASSISTANT_COLOR = QtGui.QColor(255, 255, 255)
TEXTS_MAX_WIDTH = 500


class UI:
    """
    Manages the user interface for lingu.

    Attributes:
        app: A reference to the PyQt application instance.
        modules: A list of modules, each containing
          a state with a large symbol.
        symbol_widgets: A list to store the created symbol widgets.
        screen: The available screen geometry.
    """

    def __init__(self, app, modules):
        """
        Initializes the UI with the given application and modules.

        Args:
            app: The application instance of the PyQt application.
            modules: A list of modules for symbol widgets.
        """
        self.app = app
        self.modules = modules
        self.symbol_widgets = {}
        self.windows = Windows()
        self.screen = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        self.assistant_time = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_text_timeout)
        self.timer.start(500)

        self.add_symbols()
        self.add_listeners()
        self.add_texts()

    def check_text_timeout(self):
        """
        Hides texts of user and assistant after timeout.
        """
        if self.modules["speech"]["state"].is_active:
            self.assistant_time = time.time()

        """Check if the assistant's last text was more than 20 seconds ago."""
        if self.assistant_time and time.time() - self.assistant_time > 20:
            self.user_text.hide()
            self.assistant_text.hide()
            self.assistant_time = 0  # Reset assistant_time

    def add_texts(self):
        """
        Adds the text widgets for user and assistant to the UI.
        """
        self.user_text = Text(
            "",
            USERTEXT_COLOR,
            TEXTS_MAX_WIDTH,
            self.screen.width() - TextConfig.DISTANCE_RIGHT,
            TextConfig.DISTANCE_TOP,
        )
        self.assistant_text = Text(
            "",
            ASSISTANT_COLOR,
            TEXTS_MAX_WIDTH,
            self.screen.width() - TextConfig.DISTANCE_RIGHT,
            self.user_text.geometry().bottom(),
        )

    def add_listeners(self):
        """
        Adds the listeners for the UI events.
        """

        events.add_listener(
            "user_text",
            "listen",
            self._on_realtime_transcription
        )
        events.add_listener(
            "user_text_complete",
            "listen",
            self._on_final_text
        )
        events.add_listener(
            "assistant_text",
            "brain",
            self._on_assistant_text
        )
        events.add_listener(
            "function_call_start",
            "brain",
            self._on_function_call_start
        )
        events.add_listener(
            "function_call",
            "brain",
            self._on_function_call
        )
        events.add_listener(
            "function_call_finished",
            "brain",
            self._on_function_call_finished
        )
        events.add_listener(
            "wakeword_start",
            "listen",
            self._on_wake_word_start
        )
        events.add_listener(
            "wakeword_end",
            "listen",
            self._on_wake_word_end
        )
        events.add_listener(
            "module_state_active",
            "brain",
            self._on_module_state_active
        )
        events.add_listener(
            "module_state_inactive",
            "brain",
            self._on_module_state_inactive
        )
        events.add_listener(
            "module_state_disabled",
            "brain",
            self._on_module_state_disabled
        )
        events.add_listener(
            "module_state_enabled",
            "brain",
            self._on_module_state_enabled
        )

    def add_symbols(self):
        """
        Adds the symbol widgets to the UI.
        """
        module_order = cfg('modules')
        modules = self.modules.values()

        if module_order:
            sorted_modules = sorted(
                modules,
                key=lambda m: module_order.index(m["name"])
                if m["name"] in module_order else len(module_order)
            )
        else:
            print("No module order found in settings.yaml")
            sorted_modules = modules

        gap = SymbolConfig.SIZE + \
            SymbolConfig.DISTANCE_BETWEEN_SYMBOLS

        x_offset = self.screen.width() - len(sorted_modules) * gap - \
            SymbolConfig.DISTANCE_RIGHT

        for module_index, module in enumerate(sorted_modules):

            # Create and show the symbol widget
            symbol_widget = Symbol(
                module,
                module["state"].large_symbol,
                x_offset + module_index * gap,
                SymbolConfig.DISTANCE_TOP
            )
            symbol_widget.leftClicked.connect(self._on_symbol_left_clicked)
            symbol_widget.show()
            self.symbol_widgets[module["name"]] = symbol_widget

    def set_symbols_ready(self):
        """
        Sets the state of all symbols to ready.
        """
        for symbol in self.symbol_widgets.values():
            if symbol.state == "not_ready":
                symbol.set_state("normal")

    def _on_symbol_left_clicked(self, symbol_widget: Symbol):
        """
        Called when a symbol is left clicked.
        """
        pos = QPoint(
            symbol_widget.geometry().right(),
            symbol_widget.geometry().bottom() - 1)
        self.windows.toggle_window(symbol_widget.module, pos)

    def _on_realtime_transcription(self, text):
        """
        High frequency updated text.

        Args:
            text: Contains the transcription text.
        """
        self.user_text.setText(text)
        self.assistant_text.setText("")
        self.assistant_text.setVisibility(False)

    def _on_final_text(self, text):
        """
        Final detected full sentence text transcribed
        with high accuracy.

        Args:
            text: Contains the transcription text.
        """
        self.user_text.setText(text)
        self.assistant_text.setVisibility(True)
        self.assistant_text.set_y(self.user_text.geometry().bottom())

    def _on_assistant_text(self, text):
        """
        Assitant answer.

        Args:
            text: Contains the answer text of the assistant.
        """
        self.assistant_time = time.time()
        self.assistant_text.setText(text)

    def _on_function_call_start(self, fct):
        """
        Called when a function call starts.
        """
        fct_name = fct["name"]
        for symbol in self.symbol_widgets.values():
            if fct_name in symbol.module["tool_names"]:
                symbol.set_state("fct_call_start")

    def _on_function_call(self, tool, inf_obj):
        """
        Called when a function call is executed.
        """
        module = inf_obj.module
        symbol = self.symbol_widgets[module["name"]]
        symbol.set_state("executing")

    def _on_function_call_finished(self, tool, inf_obj):
        """
        Called when a function call is finished.
        """
        module = inf_obj.module
        symbol = self.symbol_widgets[module["name"]]
        symbol.set_state("normal")

    def _on_wake_word_start(self):
        """
        Called when the wake word is detected.
        """
        for symbol in self.symbol_widgets.values():
            symbol.set_state("unavailable")

    def _on_wake_word_end(self):
        """
        Called when state returns to normal after wake word was detected.
        """
        for symbol in self.symbol_widgets.values():
            symbol.set_state("normal")

    def _on_module_state_active(self, module_name: str):
        """
        Called when a module becomes active.
        """
        for symbol in self.symbol_widgets.values():
            if symbol.module["name"] == module_name:
                symbol.set_active(True)

    def _on_module_state_inactive(self, module_name: str):
        """
        Called when a module becomes inactive.
        """
        for symbol in self.symbol_widgets.values():
            if symbol.module["name"] == module_name:
                symbol.set_active(False)

    def _on_module_state_disabled(self, module_name: str):
        """
        Called when a module becomes disabled.
        """
        for symbol in self.symbol_widgets.values():
            if symbol.module["name"] == module_name:
                symbol.set_disabled(True)

    def _on_module_state_enabled(self, module_name: str):
        """
        Called when a module becomes enabled.
        """
        for symbol in self.symbol_widgets.values():
            if symbol.module["name"] == module_name:
                symbol.set_disabled(False)
