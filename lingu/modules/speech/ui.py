from PyQt6.QtWidgets import (
    QSizePolicy,
    QSlider,
    QGroupBox,
    QVBoxLayout,
)
from .ui_engines import (
    ElevenlabsWidget,
    OpenAIWidget,
    SystemWidget,
    AzureWidget,
    CoquiWidget,
)
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    EditableComboBox,
    ComboBox,
    TextEdit,
    Slider,
    Theme,
    setTheme,
)
from lingu import UI, Line
from .logic import logic


class SpeechUI(UI):
    def __init__(self):
        super().__init__()

        setTheme(Theme.DARK)

        label = UI.headerlabel("👄 Speech")
        self.header(label, nostyle=True)

        self.engine_names = [
            "System",
            "Azure",
            "Elevenlabs",
            "Coqui",
            "OpenAI",
        ]

        self.buttons = self.add_buttons({
            "add":
                ("➕", self.add_voice),
            "save":
                ("💾", self.save_voice),
            "delete":
                ("🗑️", self.delete_voice),
            "prev":
                ("◀", self.previous_voice),
            "next":
                ("▶", self.next_voice),
        })

        self.voice_position = UI.headerlabel("# 0/0 ")
        self.header(self.voice_position, align="right", nostyle=True)

        self.add(UI.label("Voice"))
        self.select_voice = EditableComboBox()
        self.select_voice.currentIndexChanged.connect(self.handle_voice_change)
        self.add(self.select_voice)

        self.test_voice_groupbox = QGroupBox("Test")
        self.test_voice_layout = QVBoxLayout()
        line = Line(spacer=False, align=Qt.AlignmentFlag.AlignTop)
        self.test_voice_button = UI.button("🔊", self.test_voice)
        line.add(self.test_voice_button, align="right")
        self.voice_test = TextEdit(self)
        self.voice_test.setFixedHeight(150)
        self.voice_test.textChanged.connect(self.voice_test_text_changed)
        line.add(self.voice_test)
        self.test_voice_layout.addWidget(line)
        self.test_voice_groupbox.setLayout(self.test_voice_layout)
        self.add(self.test_voice_groupbox)

        self.rvc_groupbox = QGroupBox("RVC")
        self.rvc_groupbox.setCheckable(True)
        self.rvc_groupbox.toggled.connect(self.set_rvc_enabled)
        self.rvc_layout = QVBoxLayout()

        self.rvc_layout.addWidget(UI.label("Model"))

        self.rvc_model = ComboBox()
        self.rvc_model.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        for model in logic.get_rvc_models():
            self.rvc_model.addItem(model)
        self.rvc_model.currentIndexChanged.connect(
            self.handle_rvc_model_change)
        self.rvc_layout.addWidget(self.rvc_model)

        line = Line()
        line.add(UI.label("Pitch "))
        self.label_rvc_pitch = UI.label("0")
        self.label_rvc_pitch.setObjectName("one_line_content")
        line.add(self.label_rvc_pitch)
        self.rvc_layout.addWidget(line)

        self.rvc_pitch = Slider(Qt.Orientation.Horizontal, self)
        self.rvc_pitch.setMinimum(-20)
        self.rvc_pitch.setMaximum(20)
        self.rvc_pitch.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.rvc_pitch.setTickInterval(1)
        self.rvc_pitch.valueChanged.connect(self.on_rvc_pitch_changed)
        self.rvc_layout.addWidget(self.rvc_pitch)
        self.rvc_groupbox.setLayout(self.rvc_layout)
        self.add(self.rvc_groupbox)

        self.engine_groupbox = QGroupBox("Engine")
        self.engine_layout = QVBoxLayout()

        self.engine_layout.addWidget(UI.label("Engine"))
        self.select_engine = ComboBox()
        self.select_engine.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        self.select_engine.currentIndexChanged.connect(
            self.handle_engine_change)
        self.engine_layout.addWidget(self.select_engine)

        self.engine_groupbox.setLayout(self.engine_layout)
        self.add(self.engine_groupbox)

        self.add(Line())

        self.engine_widget = None
        self.update_display()

        self.add_listener("update_ui", "speech", self.update_display)
        self.add_listener(
            "audio_stream_start",
            "speech",
            self.on_audio_stream_start)
        self.add_listener(
            "audio_stream_stop",
            "speech",
            self.on_audio_stream_stop)

    def set_rvc_enabled(self, state):
        logic.set_rvc_enabled(self.rvc_groupbox.isChecked())

    def on_rvc_pitch_changed(self, value):
        self.label_rvc_pitch.setText(str(value))
        logic.set_rvc_pitch(self.rvc_pitch.value())

    def handle_rvc_model_change(self, index):
        logic.set_rvc_model(self.rvc_model.currentText())

    def add_voice(self):
        self.save_voice(-1)
        logic.update_ui()
        self.update_display()

    def delete_voice(self):
        logic.voices.delete_voice(self.state.voice_index)
        logic.update_ui()
        self.update_display()

    def previous_voice(self):
        logic.voices.switch_voice(self.state.voice_index - 1)
        self.update_display()

    def next_voice(self):
        logic.voices.switch_voice(self.state.voice_index + 1)
        self.update_display()

    def save_voice(self, voice_index=-2):
        if self.engine_name == "system":
            voice = {
                "name": self.select_voice.currentText(),
                "engine": "system",
                "voice_name":
                self.engine_widget.select_voice.currentData().name,
                "voice_id": self.engine_widget.select_voice.currentData().id,
            }
        elif self.engine_name == "azure":
            voice = {
                "name": self.select_voice.currentText(),
                "engine": "azure",
                "voice_name":
                self.engine_widget.select_voice.currentData().name,
                "voice_full_name":
                self.engine_widget.select_voice.currentData().full_name,
                "voice_rate": self.engine_widget.voice_rate.value(),
                "voice_pitch": self.engine_widget.voice_pitch.value(),
                "voice_locale":
                self.engine_widget.select_voice.currentData().locale,
                "voice_language":
                self.engine_widget.select_voice.currentData().language,
                "voice_gender":
                self.engine_widget.select_voice.currentData().gender,
            }
        elif self.engine_name == "coqui":
            voice = {
                "name": self.select_voice.currentText(),
                "engine": "coqui",
                "voice_name":
                self.engine_widget.select_voice.currentData().name,
                "model":
                self.engine_widget.select_model.currentData(),
            }
        elif self.engine_name == "openai":
            voice = {
                "name": self.select_voice.currentText(),
                "engine": "openai",
                "voice_name":
                self.engine_widget.select_voice.currentData().name,
            }
        elif self.engine_name == "elevenlabs":
            voice = {
                "name": self.select_voice.currentText(),
                "engine": "elevenlabs",
                "voice_name":
                self.engine_widget.select_voice.currentData().name,
                "voice_id":
                self.engine_widget.select_voice.currentData().voice_id,
                "voice_category":
                self.engine_widget.select_voice.currentData().category,
                "voice_description":
                self.engine_widget.select_voice.currentData().description,
                "voice_labels":
                self.engine_widget.select_voice.currentData().labels,
                "voice_stability": self.engine_widget.stability.value(),
                "voice_clarity": self.engine_widget.clarity.value(),
                "voice_exaggeration": self.engine_widget.exaggeration.value(),
            }
        else:
            return

        voice["rvc_enabled"] = self.rvc_groupbox.isChecked()
        voice["rvc_pitch"] = self.rvc_pitch.value()
        voice["rvc_model"] = self.rvc_model.currentText()

        print(f"voice_index: {voice_index}")
        voice_index = (
            self.state.voice_index
            if voice_index is False or voice_index == -2
            else voice_index
        )
        print(f"self.state.voice_index: {self.state.voice_index}")
        print(f"voice_index: {voice_index}")

        logic.voices.save_voice(voice, voice_index)

        self.update_display()

    def on_audio_stream_start(self):
        self.test_voice_button.setEnabled(False)

    def on_audio_stream_stop(self):
        self.test_voice_button.setEnabled(True)

    def handle_voice_change(self, index):
        self.state.voice_index = index
        self.update_display()

    def update_display(self):
        state = self.state
        if state.voice_index < 0 and len(state.voices) > 0:
            state.voice_index = 0
        if state.voice_index >= len(state.voices):
            state.voice_index = len(state.voices) - 1
        if len(state.voices) == 0:
            state.voice_index = -1

        self.voice_position.setText(
            f"# {state.voice_index + 1}/{len(state.voices)} ")

        self.voice_test.setText(self.state.voice_test_text)

        self.buttons["prev"].setEnabled(
            len(state.voices) > 0 and state.voice_index > 0)
        self.buttons["next"].setEnabled(
            len(state.voices) > 0 and
            state.voice_index < len(state.voices) - 1
        )
        self.buttons["save"].setEnabled(
            len(state.voices) > 0
        )
        self.buttons["delete"].setEnabled(
            len(state.voices) > 0
        )

        rvc_enabled = self.rvc_groupbox.isChecked()
        # rvc_pitch = self.rvc_pitch.value()
        # rvc_model = self.rvc_model.currentText()

        self.select_voice.blockSignals(True)
        self.rvc_groupbox.blockSignals(True)
        self.rvc_pitch.blockSignals(True)
        self.rvc_model.blockSignals(True)
        self.select_voice.clear()

        if len(state.voices) > 0:

            self.voice = state.voices[state.voice_index]

            self.select_voice.addItems(
                [voice["name"] for voice in state.voices])
            self.select_voice.setCurrentText(self.voice["name"])

            # handle rvc
            state.rvc_enabled = self.voice.get("rvc_enabled", False)
            if state.rvc_enabled != rvc_enabled:
                logic.set_rvc_enabled(state.rvc_enabled)
            self.rvc_groupbox.setChecked(state.rvc_enabled)

            if state.rvc_enabled:
                if "rvc_model" in self.voice:
                    logic.set_rvc_model(self.voice["rvc_model"])
                    state.rvc_model = self.voice["rvc_model"]
                    self.rvc_model.setCurrentText(self.voice["rvc_model"])
                if "rvc_pitch" in self.voice:
                    logic.set_rvc_pitch(self.voice["rvc_pitch"])
                    state.rvc_pitch = self.voice["rvc_pitch"]
                    self.rvc_pitch.setValue(self.voice["rvc_pitch"])
                    self.label_rvc_pitch.setText(str(self.voice["rvc_pitch"]))
                else:
                    self.rvc_pitch.setValue(0)
                    self.label_rvc_pitch.setText("0")

            if self.voice["engine"] == "azure":
                # print("switch to azure")
                self.handle_engine_change(1)
                if "voice_language" in self.voice:
                    self.engine_widget.select_language.setCurrentText(
                        self.voice["voice_language"])
                if "voice_name" in self.voice:
                    self.engine_widget.select_voice.setCurrentText(
                        self.voice["voice_name"])
                if "voice_rate" in self.voice:
                    # print(f"set voice rate to {self.voice['voice_rate']}")
                    self.engine_widget.voice_rate.setValue(
                        self.voice["voice_rate"])
                if "voice_pitch" in self.voice:
                    # print(f"set voice pitch to {self.voice['voice_pitch']}")
                    self.engine_widget.voice_pitch.setValue(
                        self.voice["voice_pitch"])
            elif self.voice["engine"] == "elevenlabs":
                # print("switch to elevenlabs")
                self.handle_engine_change(2)
                if "voice_name" in self.voice:
                    self.engine_widget.select_voice.setCurrentText(
                        self.voice["voice_name"])
                if "voice_clarity" in self.voice:
                    # print("set voice clarity to "
                    #       f"{self.voice['voice_clarity']}")
                    self.engine_widget.clarity.setValue(
                        self.voice["voice_clarity"])
                if "voice_stability" in self.voice:
                    # print("set voice stability to "
                    #       f"{self.voice['voice_stability']}")
                    self.engine_widget.stability.setValue(
                        self.voice["voice_stability"])
                if "voice_exaggeration" in self.voice:
                    # print("set voice exaggeration to "
                    #       f"{self.voice['voice_exaggeration']}")
                    self.engine_widget.exaggeration.setValue(
                        self.voice["voice_exaggeration"])
            elif self.voice["engine"] == "coqui":
                if "model" in self.voice:
                    state.coqui_model = self.voice["model"]
                # print("switch to coqui")
                self.handle_engine_change(3)
                if "voice_name" in self.voice:
                    self.engine_widget.select_voice.setCurrentText(
                        self.voice["voice_name"])
                if "model" in self.voice:
                    self.engine_widget.select_model.setCurrentText(
                        self.voice["model"])
                    logic.engines.set_coqui_model(self.voice["model"])
                else:
                    logic.engines.set_coqui_model("v2.0.2")
                logic.voices.set_voice_data()
            elif self.voice["engine"] == "openai":
                # print("switch to openai")
                self.handle_engine_change(4)
                if "voice_name" in self.voice:
                    self.engine_widget.select_voice.setCurrentText(
                        self.voice["voice_name"])
            else:
                # print("switch to system")
                self.handle_engine_change(0)
                if "voice_name" in self.voice:
                    self.engine_widget.select_voice.setCurrentText(
                        self.voice["voice_name"])
        else:
            self.voice = None
            self.handle_engine_change(0)
            self.select_voice.setCurrentText("")
            self.rvc_groupbox.setChecked(False)
            self.rvc_pitch.setValue(0)
            self.label_rvc_pitch.setText("0")
            voices = logic.voices.get_voices("system")
            logic.engines.set_voice_instance("system", voices[0])

        self.rvc_groupbox.blockSignals(False)
        self.rvc_pitch.blockSignals(False)
        self.rvc_model.blockSignals(False)
        self.select_voice.blockSignals(False)

        self.select_engine.blockSignals(True)
        self.select_engine.clear()
        self.select_engine.addItems(self.engine_names)
        self.select_engine.setCurrentIndex(state.engine_index)
        self.select_engine.blockSignals(False)

    def voice_test_text_changed(self):
        self.state.voice_test_text = self.voice_test.toPlainText()
        self.state.save()

    def test_voice(self):
        text = self.voice_test.toPlainText()
        logic.test_voice(text)

    def handle_engine_change(self, index):
        if hasattr(self, "engine_index") and index == self.engine_index:
            return

        # print(f"switch to engine index {index}")

        if self.engine_widget is not None:
            self.engine_layout.removeWidget(self.engine_widget)
            self.engine_widget.hide()
            self.engine_widget.deleteLater()
        if index == 0:
            self.engine_index = 0
            self.engine_name = "system"
            self.engine_widget = SystemWidget()
        elif index == 1:
            self.engine_index = 1
            self.engine_name = "azure"
            self.engine_widget = AzureWidget()
        elif index == 2:
            self.engine_index = 2
            self.engine_name = "elevenlabs"
            self.engine_widget = ElevenlabsWidget()
        elif index == 3:
            self.engine_index = 3
            self.engine_name = "coqui"
            self.engine_widget = CoquiWidget()
        elif index == 4:
            self.engine_index = 4
            self.engine_name = "openai"
            self.engine_widget = OpenAIWidget()
        if index >= 0 and index <= 4:
            self.engine_layout.addWidget(self.engine_widget)
            self.engine_layout.update()
            self.engine_layout.activate()
            self.adjustSize()
            self.update()

        logic.engines.switch_engine(self.engine_name)
