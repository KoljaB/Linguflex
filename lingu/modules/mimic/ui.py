from PyQt6.QtWidgets import (
    QSlider,
    QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSlot
from lingu import UI, Line
from .logic import logic
from qfluentwidgets import (
    EditableComboBox,
    Slider,
    ComboBox,
    TextEdit,
    setTheme,
    Theme
)


class MimicUI(UI):
    def __init__(self):
        super().__init__()

        setTheme(Theme.DARK)

        label = UI.headerlabel("🎭 Characters")
        self.header(label, nostyle=True)

        self.buttons = self.add_buttons({
            "add":
                ("➕", self.add_char),
            "save":
                ("💾", self.save_char),
            "delete":
                ("🗑️", self.delete_char),
            "prev":
                ("◀", self.prev_char),
            "next":
                ("▶", self.next_char),
        })

        self.char_position = UI.headerlabel("# 0/0 ")
        self.header(self.char_position, align="right", nostyle=True)

        self.add(UI.label("Character"))
        self.select_char = EditableComboBox()
        self.select_char.currentIndexChanged.connect(self.handle_char_change)
        self.add(self.select_char)

        self.add(UI.label("Voice"))
        self.select_voice = ComboBox()
        self.select_voice.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        self.update_voices()
        self.add(self.select_voice)

        self.add(UI.label("Personality"))

        self.char_personality = TextEdit(self)
        self.char_personality.setFixedHeight(150)
        self.add(self.char_personality)

        line = Line()
        line.setContentsMargins(0, 15, 0, 0)
        label_creativity = UI.label("Creatitivity: ")
        label_creativity.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_creativity)
        self.label_temperature = UI.label("0.7", "one_line_content")
        line.add(self.label_temperature)
        self.add(line)

        self.creativity = Slider(
            Qt.Orientation.Horizontal,
            self)
        self.creativity.setMinimum(0)
        self.creativity.setValue(7)
        self.creativity.setMaximum(20)
        self.creativity.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.creativity.setTickInterval(1)
        self.add(self.creativity)

        self.creativity.valueChanged.connect(self.on_creativity_changed)

        self.add_listener("voices", "speech", self.update_voices)
        self.add_ui_listener(self, "update_ui", "mimic", "update_display")
        self.update_display()

    def on_creativity_changed(self, value):
        self.label_temperature.setText(f"{(value/10):.1f}")

    def update_voices(self, voices=None):
        self.select_voice.blockSignals(True)
        self.select_voice.clear()
        if logic.voices is not None:
            for voice in logic.voices:
                name = voice["name"]
                self.select_voice.addItem(name, userData=voice)
        self.select_voice.blockSignals(False)

    def handle_char_change(self, index):
        self.state.char_index = index
        logic.switch_char(self.state.char_index)
        self.update_display()

    def add_char(self):
        char = {
            "prompt": "",
            "voice": self.select_voice.currentData(),
        }
        logic.save_char(char, -1)
        logic.set_char_data()
        self.update_display()

    def delete_char(self):
        logic.delete_char(self.state.char_index)
        logic.set_char_data()
        self.update_display()

    def prev_char(self):
        logic.switch_char(self.state.char_index - 1)
        self.update_display()

    def next_char(self):
        logic.switch_char(self.state.char_index + 1)
        self.update_display()

    def save_char(self):
        char = {
            "name": self.select_char.currentText(),
            "prompt": self.char_personality.toPlainText(),
            "voice": self.select_voice.currentData(),
            "temperature": self.creativity.value() / 10,
        }
        logic.save_char(char, self.state.char_index)
        logic.set_char_data()
        self.update_display()

    @pyqtSlot()
    def update_display(self):
        state = self.state

        if state.char_index < 0 and len(state.chars) > 0:
            state.char_index = 0
        if state.char_index >= len(state.chars):
            state.char_index = len(state.chars) - 1
        if len(state.chars) == 0:
            state.char_index = -1

        self.char_position.setText(
            f"# {state.char_index + 1}/{len(state.chars)} ")

        self.buttons["prev"].setEnabled(
            len(state.chars) > 0 and state.char_index > 0)
        self.buttons["next"].setEnabled(
            len(state.chars) > 0 and
            state.char_index < len(state.chars) - 1
        )

        if len(state.chars) > 0:

            self.char = state.chars[state.char_index]

            self.select_char.blockSignals(True)
            self.select_char.clear()
            self.select_char.addItems(
                [char["name"] for char in state.chars])
            self.select_char.setCurrentText(self.char["name"])
            self.select_char.blockSignals(False)

            self.select_voice.blockSignals(True)
            self.select_voice.setCurrentText(self.char["voice"]["name"])
            self.select_voice.blockSignals(False)
            self.char_personality.setText(self.char["prompt"])

            if "temperature" in self.char:
                self.creativity.setValue(int(self.char["temperature"] * 10))
                self.label_temperature.setText(
                    f"{self.char['temperature']:.1f}")
                self.trigger("set_temperature", self.char["temperature"])
            else:
                self.creativity.setValue(7)
                self.label_temperature.setText("0.7")
