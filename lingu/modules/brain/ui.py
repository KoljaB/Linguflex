from PyQt6.QtWidgets import (
    QSizePolicy,
    QSlider,
    QGroupBox,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt
from lingu import UI, Line, VSpacer, notify
from qfluentwidgets import Slider, ComboBox

models = [
    "gpt-4-0125-preview",
    "gpt-4-turbo-preview",
    "gpt-4-1106-preview",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-16k-0613",
]


class SteppedSlider(Slider):
    def __init__(self, orientation, parent=None, step=100):
        super().__init__(orientation, parent)
        self.step = step

    def mouseReleaseEvent(self, e):
        # Call the original mouse release event
        super().mouseReleaseEvent(e)

        # Adjust the value to the nearest step
        value = self.value()
        adjusted_value = self.round_to_nearest_step(value)
        self.setValue(adjusted_value)

    def round_to_nearest_step(self, value):
        return round(value / self.step) * self.step


class BrainUI(UI):
    def __init__(self):
        super().__init__()

        label = UI.headerlabel("🧠 Brain")
        self.header(label, nostyle=True)

        # OpenAI Model

        self.add(UI.label("OpenAI model"))

        self.select_model = ComboBox()
        self.select_model.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        self.select_model.setContentsMargins(15, 0, 0, 0)

        for model in models:
            self.select_model.addItem(model, userData=model)
        self.add(self.select_model)

        self.select_model.currentIndexChanged.connect(
            self.on_model_changed)

        self.history_groupbox = QGroupBox("Conversation history")
        self.history_layout = QVBoxLayout()
        self.history_groupbox.setLayout(self.history_layout)
        self.add(self.history_groupbox)

        # Max Number of Messages

        line = Line()
        label_max_messages_start = UI.label("Number of messages limit ")
        label_max_messages_start.setWordWrap(False)
        label_max_messages_start.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_max_messages_start)
        self.label_max_messages = UI.label("12", "one_line_content")
        line.add(self.label_max_messages)
        label_max_messages_end = UI.label(" messages")
        label_max_messages_end.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_max_messages_end)
        self.history_layout.addWidget(line)

        self.max_messages = SteppedSlider(
            Qt.Orientation.Horizontal, self, step=10)
        self.max_messages.setMinimum(4)
        self.max_messages.setMaximum(100)
        self.max_messages.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.max_messages.setTickInterval(10)
        self.max_messages.setSingleStep(10)
        self.history_layout.addWidget(self.max_messages)

        self.history_layout.addWidget(VSpacer())

        # Tokens per Message

        line = Line()
        label_tokens_per_msg_start = UI.label("Single message size limit ")
        label_tokens_per_msg_start.setWordWrap(False)
        label_tokens_per_msg_start.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_tokens_per_msg_start)
        self.label_tokens_per_msg = UI.label("500", "one_line_content")
        line.add(self.label_tokens_per_msg)
        label_tokens_per_msg_end = UI.label(" tokens")
        label_tokens_per_msg_end.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_tokens_per_msg_end)
        self.history_layout.addWidget(line)

        self.max_tokens_per_msg = Slider(
            Qt.Orientation.Horizontal,
            self)
        self.max_tokens_per_msg.setMinimum(100)
        self.max_tokens_per_msg.setMaximum(15500)
        self.max_tokens_per_msg.setTickPosition(
            QSlider.TickPosition.TicksBelow)
        self.max_tokens_per_msg.setTickInterval(500)
        self.max_tokens_per_msg.setSingleStep(100)
        self.history_layout.addWidget(self.max_tokens_per_msg)

        self.history_layout.addWidget(VSpacer())

        # Max Tokens for whole History

        line = Line()
        label_history_tokens_start = UI.label("Whole history size limit ")
        label_history_tokens_start.setWordWrap(False)
        label_history_tokens_start.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_history_tokens_start)
        self.label_history_tokens = UI.label("15500", "one_line_content")
        line.add(self.label_history_tokens)
        label_history_tokens_end = UI.label(" tokens")
        label_history_tokens_end.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_history_tokens_end)
        self.history_layout.addWidget(line)

        self.history_tokens = Slider(
            Qt.Orientation.Horizontal,
            self)
        self.history_tokens.setMinimum(500)
        self.history_tokens.setMaximum(31500)
        self.history_tokens.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.history_tokens.setTickInterval(1000)
        self.history_tokens.setSingleStep(100)
        self.history_layout.addWidget(self.history_tokens)

        self.max_tokens_per_msg.valueChanged.connect(
            self.on_max_tokens_per_msg_changed)
        self.max_messages.valueChanged.connect(
            self.on_max_messages_changed)
        self.history_tokens.valueChanged.connect(
            self.on_history_tokens_changed)

        self.update_display()

    def on_max_tokens_per_msg_changed(self, value):
        self.label_tokens_per_msg.setText(f"{value}")
        self.logic.set_max_tokens_per_msg(value)
        self.update_display()

    def on_max_messages_changed(self, value):
        self.label_max_messages.setText(f"{value}")
        self.logic.set_max_messages(value)
        self.update_display()

    def on_history_tokens_changed(self, value):
        self.label_history_tokens.setText(f"{value}")
        self.logic.set_history_tokens(value)
        self.update_display()

    def update_display(self):
        self.max_tokens_per_msg.blockSignals(True)
        self.max_messages.blockSignals(True)
        self.history_tokens.blockSignals(True)

        print("Set value of max tokens per message to "
              f"{self.state.max_tokens_per_msg}")
        self.max_tokens_per_msg.setValue(
            self.state.max_tokens_per_msg)        
        print(f"Set value of max messages to {self.state.max_messages}")
        self.max_messages.setValue(
            self.state.max_messages)
        print(f"Set value of history tokens to {self.state.history_tokens}")
        self.history_tokens.setValue(
               self.state.history_tokens)

        self.max_tokens_per_msg.blockSignals(False)
        self.max_messages.blockSignals(False)
        self.history_tokens.blockSignals(False)

    def on_model_changed(self, index):
        model = self.select_model.currentData()
        self.logic.switch_language_model(model, True)
        notify("Brain", f"Switched model to {model}", -1, "custom", "🛈")
