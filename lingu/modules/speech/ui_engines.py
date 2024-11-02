from PyQt6.QtWidgets import (
    QWidget,
    QSizePolicy,
    QSlider,
)
from PyQt6.QtCore import Qt
from lingu import UI, Line, cfg
from .logic import logic
from qfluentwidgets import (
    ComboBox,
    Slider,
    TextEdit,
)


class SystemWidget(QWidget):
    """
    A widget for system voice settings
    """
    def __init__(self):
        """
        Initialize the SystemWidget.

        Args:
            logic: The logic layer handling voice operations.
        """
        super(SystemWidget, self).__init__()

        self.layout = UI.layout(self)
        lbl_select_voice = UI.label("Voice")
        lbl_select_voice.setContentsMargins(0, 0, 0, 5)
        self.layout.addWidget(lbl_select_voice)

        voices = logic.voices.get_voices("system")

        self.select_voice = ComboBox()
        self.select_voice.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        for voice in voices:
            self.select_voice.addItem(voice.name, userData=voice)
        self.select_voice.currentIndexChanged.connect(self.handle_voice_change)
        self.layout.addWidget(self.select_voice)

    def handle_voice_change(self, index):
        selected_voice = self.select_voice.currentData()
        logic.engines.set_voice_instance("system", selected_voice)


class AzureWidget(QWidget):
    """
    A widget for azure voice settings
    """
    def __init__(self):
        """
        Initialize the AzureWidget.

        Args:
            logic: The logic layer handling voice operations.
        """
        super(AzureWidget, self).__init__()

        self.layout = UI.layout(self)

        self.voices = logic.voices.get_voices("azure")
        self.languages = ["--- ALL ---"] + sorted(
            set(voice.language for voice in self.voices))

        line = Line(horizontal=False, spacing=15)
        line.left_left.setSpacing(5)
        line.left_right.setSpacing(5)
        lbl_select_voice = UI.label("Voice")
        lbl_select_voice.setContentsMargins(0, 0, 0, 0)
        line.add(lbl_select_voice)
        self.select_voice = ComboBox()
        self.select_voice.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        self.select_voice.setContentsMargins(0, 10, 0, 0)
        for voice in self.voices:
            name = voice.name
            if name.endswith("Neural"):
                name = name[:-7]
            self.select_voice.addItem(voice.name, userData=voice)
        self.select_voice.currentIndexChanged.connect(self.handle_voice_change)
        line.add(self.select_voice)
        lbl_select_language = UI.label("Language")
        lbl_select_language.setContentsMargins(0, 0, 0, 0)
        lbl_select_language.setFixedWidth(150)
        line.add(lbl_select_language, align="leftright")

        self.select_language = ComboBox()
        self.select_language.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        self.select_language.setContentsMargins(10, 10, 0, 0)
        for lang in self.languages:
            self.select_language.addItem(lang)
        self.select_language.currentIndexChanged.connect(
            self.handle_language_change)
        line.add(self.select_language, align="leftright")
        self.layout.addWidget(line)

        self.layout.addWidget(Line())

        line = Line()
        line.add(UI.label("Speed "))
        self.label_speed = UI.label("0", "one_line_content")
        line.add(self.label_speed)
        self.layout.addWidget(line)

        self.voice_rate = Slider(
            Qt.Orientation.Horizontal,
            self)
        self.voice_rate.setMinimum(-50)
        self.voice_rate.setMaximum(50)
        self.voice_rate.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.voice_rate.setTickInterval(1)
        self.layout.addWidget(self.voice_rate)

        self.layout.addWidget(Line())

        line = Line()
        line.add(UI.label("Pitch "))
        self.label_pitch = UI.label("0", "one_line_content")
        line.add(self.label_pitch)
        self.layout.addWidget(line)

        self.voice_pitch = Slider(
            Qt.Orientation.Horizontal,
            self)
        self.voice_pitch.setMinimum(-50)
        self.voice_pitch.setMaximum(50)
        self.voice_pitch.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.voice_pitch.setTickInterval(1)
        self.layout.addWidget(self.voice_pitch)

        self.voice_rate.valueChanged.connect(self.on_voice_rate_changed)
        self.voice_pitch.valueChanged.connect(self.on_voice_pitch_changed)
        self.voice_rate.setValue(0)
        self.voice_pitch.setValue(0)

        preselect_language = cfg("language", default="en")
        self.populate_language_combobox(preselect_language)

    def populate_language_combobox(self, preselect_language):
        if preselect_language in self.languages:
            index = self.select_language.findText(preselect_language)
            self.select_language.setCurrentIndex(index)
            self.handle_language_change(index)

    def handle_voice_change(self, index):
        selected_voice = self.select_voice.currentData()
        logic.engines.set_voice_instance("azure", selected_voice)

    def handle_language_change(self, index):
        selected_lang = self.select_language.currentText()

        self.select_voice.blockSignals(True)
        self.select_voice.clear()
        if selected_lang == "--- ALL ---":
            for voice in self.voices:
                self.select_voice.addItem(voice.name, userData=voice)
        else:
            for voice in self.voices:
                if voice.language == selected_lang:
                    self.select_voice.addItem(voice.name, userData=voice)
        self.select_voice.blockSignals(False)

        self.handle_voice_change(self.select_voice.currentIndex())

    def on_voice_rate_changed(self, value):
        self.label_speed.setText(f"{value}")
        logic.engines.set_voice_parameters(
            "azure",
            rate=self.voice_rate.value(),
            pitch=self.voice_pitch.value())

    def on_voice_pitch_changed(self, value):
        self.label_pitch.setText(f"{value}")
        logic.engines.set_voice_parameters(
            "azure",
            rate=self.voice_rate.value(),
            pitch=self.voice_pitch.value())


class CoquiWidget(QWidget):
    """
    A widget for coqui voice settings
    """
    def __init__(self):
        """
        Initialize the CoquiWidget.

        Args:
            logic: The logic layer handling voice operations.
        """
        super(CoquiWidget, self).__init__()

        self.layout = UI.layout(self)

        lbl_select_model = UI.label("Model")
        lbl_select_model.setContentsMargins(0, 0, 0, 5)
        self.layout.addWidget(lbl_select_model)

        models = logic.engines.get_coqui_models()

        self.select_model = ComboBox()
        self.select_model.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        for model in models:
            self.select_model.addItem(model, userData=model)
        self.select_model.currentIndexChanged.connect(self.handle_model_change)
        self.layout.addWidget(self.select_model)

        lbl_select_voice = UI.label("Voice")
        lbl_select_voice.setContentsMargins(0, 10, 0, 5)
        self.layout.addWidget(lbl_select_voice)

        voices = logic.voices.get_voices("coqui")

        self.select_voice = ComboBox()
        self.select_voice.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        for voice in voices:
            self.select_voice.addItem(voice.name, userData=voice)
        self.select_voice.currentIndexChanged.connect(self.handle_voice_change)
        self.layout.addWidget(self.select_voice)

        line = Line()
        line.add(UI.label("Speed "))
        self.label_speed = UI.label("0", "one_line_content")
        line.add(self.label_speed)
        self.layout.addWidget(line)

        self.voice_speed = Slider(
            Qt.Orientation.Horizontal,
            self)
        self.voice_speed.setMinimum(-50)
        self.voice_speed.setMaximum(50)
        self.voice_speed.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.voice_speed.setTickInterval(1)
        self.layout.addWidget(self.voice_speed)

        self.voice_speed.valueChanged.connect(self.on_voice_speed_changed)

    def on_voice_speed_changed(self, value):
        self.label_speed.setText(f"{value}")
        speed_value = self.voice_speed.value()

        # map from -50..50 to 0.5..1.5
        speed_value = (speed_value + 50) / 100 + 0.5
        logic.engines.set_coqui_speed(speed_value)

    def handle_model_change(self, index):
        selected_model = self.select_model.currentData()
        logic.engines.set_coqui_model(selected_model)

    def handle_voice_change(self, index):
        selected_voice = self.select_voice.currentData()
        logic.engines.set_voice_instance("coqui", selected_voice)


class ElevenlabsWidget(QWidget):
    """
    A widget for elevenlabs voice settings
    """
    def __init__(self):
        """
        Initialize the ElevenlabsWidget.

        Args:
            logic: The logic layer handling voice operations.
        """
        super(ElevenlabsWidget, self).__init__()

        self.layout = UI.layout(self)
        lbl_select_voice = UI.label("Voice")
        lbl_select_voice.setContentsMargins(0, 0, 0, 5)
        self.layout.addWidget(lbl_select_voice)

        voices = logic.voices.get_voices("elevenlabs")

        self.select_voice = ComboBox()
        self.select_voice.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        for voice in voices:
            self.select_voice.addItem(voice.name, userData=voice)
        self.select_voice.currentIndexChanged.connect(self.handle_voice_change)
        self.layout.addWidget(self.select_voice)
        self.layout.addWidget(Line())

        line = Line()
        line.add(UI.label("Stability "))
        self.label_stability = UI.label("0", "one_line_content")
        line.add(self.label_stability)
        self.layout.addWidget(line)

        self.stability = Slider(
            Qt.Orientation.Horizontal,
            self)
        self.stability.setMinimum(0)
        self.stability.setMaximum(100)
        self.stability.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.stability.setTickInterval(1)
        self.layout.addWidget(self.stability)

        self.layout.addWidget(Line())

        line = Line()
        line.add(UI.label("Clarity "))
        self.label_clarity = UI.label("0", "one_line_content")
        line.add(self.label_clarity)
        self.layout.addWidget(line)

        self.clarity = Slider(
            Qt.Orientation.Horizontal,
            self)
        self.clarity.setMinimum(0)
        self.clarity.setMaximum(100)
        self.clarity.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.clarity.setTickInterval(1)
        self.layout.addWidget(self.clarity)

        self.layout.addWidget(Line())

        line = Line()
        line.add(UI.label("Exaggeration "))
        self.label_exaggeration = UI.label("0", "one_line_content")
        line.add(self.label_exaggeration)
        self.layout.addWidget(line)

        self.exaggeration = Slider(
            Qt.Orientation.Horizontal,
            self)
        self.exaggeration.setMinimum(0)
        self.exaggeration.setMaximum(100)
        self.exaggeration.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.exaggeration.setTickInterval(1)
        self.layout.addWidget(self.exaggeration)

        self.stability.valueChanged.connect(self.on_stability_changed)
        self.clarity.valueChanged.connect(self.on_clarity_changed)
        self.exaggeration.valueChanged.connect(self.on_exaggeration_changed)
        self.stability.setValue(50)
        self.clarity.setValue(75)
        self.exaggeration.setValue(0)

    def handle_voice_change(self, index):
        selected_voice = self.select_voice.currentData()
        logic.engines.set_voice_instance("elevenlabs", selected_voice)

    def on_stability_changed(self, value):
        self.label_stability.setText(f"{value}")
        logic.engines.set_voice_parameters(
            "elevenlabs",
            stability=self.stability.value(),
            clarity=self.clarity.value(),
            exaggeration=self.exaggeration.value())

    def on_clarity_changed(self, value):
        self.label_clarity.setText(f"{value}")
        logic.engines.set_voice_parameters(
            "elevenlabs",
            stability=self.stability.value(),
            clarity=self.clarity.value(),
            exaggeration=self.exaggeration.value())

    def on_exaggeration_changed(self, value):
        self.label_exaggeration.setText(f"{value}")
        logic.engines.set_voice_parameters(
            "elevenlabs",
            stability=self.stability.value(),
            clarity=self.clarity.value(),
            exaggeration=self.exaggeration.value())


class OpenAIWidget(QWidget):
    """
    A widget for openai voice settings
    """
    def __init__(self):
        """
        Initialize the OpenAIWidget.

        Args:
            logic: The logic layer handling voice operations.
        """
        super(OpenAIWidget, self).__init__()

        self.layout = UI.layout(self)
        lbl_select_voice = UI.label("Voice")
        lbl_select_voice.setContentsMargins(0, 0, 0, 5)
        self.layout.addWidget(lbl_select_voice)

        voices = logic.voices.get_voices("openai")

        self.select_voice = ComboBox()
        self.select_voice.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        for voice in voices:
            self.select_voice.addItem(voice.name, userData=voice)
        self.select_voice.currentIndexChanged.connect(self.handle_voice_change)
        self.layout.addWidget(self.select_voice)

    def handle_voice_change(self, index):
        selected_voice = self.select_voice.currentData()
        logic.engines.set_voice_instance("openai", selected_voice)


class ParlerWidget(QWidget):
    """
    A widget for system voice settings
    """
    def __init__(self):
        """
        Initialize the SystemWidget.

        Args:
            logic: The logic layer handling voice operations.
        """
        super(ParlerWidget, self).__init__()

        self.layout = UI.layout(self)
        lbl_select_voice = UI.label("Voice")
        lbl_select_voice.setContentsMargins(0, 0, 0, 5)
        self.layout.addWidget(lbl_select_voice)

        self.voice_prompt = TextEdit(self)
        self.voice_prompt.textChanged.connect(self.voice_prompt_text_changed)
        self.layout.addWidget(self.voice_prompt)


    def voice_prompt_text_changed(self):
        voice_prompt = self.voice_prompt.toPlainText()
        logic.engines.set_voice_instance("parler_tts", voice_prompt)
