from PyQt6.QtWidgets import (
    QSlider,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSlot
from lingu import UI, Line 
from .languages import lang_dict
from qfluentwidgets import Slider, setTheme, Theme, ComboBox, ProgressBar


class ListenUI(UI):
    def __init__(self):
        super().__init__()

        setTheme(Theme.DARK)

        label = UI.headerlabel("👂 Listen")
        self.header(label, nostyle=True)

        self.buttons = self.add_buttons({
            "mute":
                ("🔇", self.mute),
        })

        label_language = UI.label("Detection language")
        self.add(label_language)

        self.select_language = ComboBox()
        self.select_language.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        self.select_language.setContentsMargins(15, 0, 0, 0)
        self.select_language.addItem("Auto", userData="Auto")
        for lng_shortcut, lng_name in lang_dict().items():
            self.select_language.addItem(lng_name, userData=lng_shortcut)
        self.add(self.select_language)

        self.add(Line())

        label_start = UI.label("Start Speech Timeout")
        self.add(label_start)

        line = Line()
        label_switchto = UI.label("Switch to wake word mode after ")
        label_switchto.setWordWrap(False)
        label_switchto.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_switchto)
        self.start_seconds = UI.label("15", "one_line_content")
        line.add(self.start_seconds)
        label_startsecsofsilence = UI.label(" seconds of silence")
        label_startsecsofsilence.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_startsecsofsilence)
        self.add(line)

        self.start_timeout = Slider(
            Qt.Orientation.Horizontal,
            self)
        self.start_timeout.setMinimum(0)
        self.start_timeout.setMaximum(300)
        self.start_timeout.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.start_timeout.setTickInterval(1)
        self.add(self.start_timeout)

        self.add(Line())

        label_stop = UI.label("Stop Speech Timeout")
        self.add(label_stop)

        line = Line()
        label_recognize = UI.label("Recognize end of speech after ")
        label_recognize.setWordWrap(False)
        label_recognize.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_recognize)
        self.end_seconds = UI.label("0.7", "one_line_content")
        line.add(self.end_seconds)
        label_endsecsofsilence = UI.label(" seconds of silence")
        label_endsecsofsilence.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_endsecsofsilence)
        self.add(line)

        self.end_timeout = Slider(
            Qt.Orientation.Horizontal,
            self)
        self.end_timeout.setMinimum(0)
        self.end_timeout.setMaximum(30)
        self.end_timeout.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.end_timeout.setTickInterval(1)
        self.add(self.end_timeout)

        self.add(Line())

        self.lbl_interrupt_thresh, self.interrupt_thresh = \
            self.add_slider(
                "Speech Interruption",
                "Interrupt speech if volume is higher than ",
                " volume",
                7000
            )
        self.add(Line())

        line = Line()
        label_cur_vol = UI.label("Current volume: ")
        label_cur_vol.setWordWrap(False)
        label_cur_vol.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_cur_vol)
        self.lbl_cur_vol = UI.label("0", "one_line_content")
        line.add(self.lbl_cur_vol)
        self.add(line)

        self.pegel = ProgressBar(self)
        self.pegel.setOrientation(Qt.Orientation.Horizontal)
        self.pegel.setMinimum(0)
        self.pegel.setMaximum(20000)
        self.pegel.setTextVisible(False)
        self.add(self.pegel)

        self.interrupt_thresh.valueChanged.connect(self.on_interrupt_thresh_changed)
        self.start_timeout.valueChanged.connect(self.on_start_timeout_changed)
        self.end_timeout.valueChanged.connect(self.on_end_timeout_changed)
        self.select_language.currentIndexChanged.connect(
            self.on_language_changed)

        self.add_ui_listener(
            self,
            "recorded_chunk",
            "listen",
            "recorded_chunk")

    @pyqtSlot()
    def recorded_chunk(self):
        self.lbl_cur_vol.setText(str(int(self.state.pegel)))
        current = int(self.state.pegel)
        self.pegel.setValue(current)

    def on_language_changed(self, index):
        lang_shortcut = self.select_language.currentData()
        self.logic.set_lang_shortcut(lang_shortcut)

    def mute(self):
        self.logic.toggle_mute()

    def init(self):
        self.update_display()

    def on_start_timeout_changed(self, value):
        self.start_seconds.setText(f"{value}")
        self.logic.set_start_timeout(value)

    def on_interrupt_thresh_changed(self, value):
        self.state.interrupt_thresh = value
        self.lbl_interrupt_thresh.setText(f"{value}")
        self.state.save()

    def on_end_timeout_changed(self, value):
        self.end_seconds.setText(f"{(value/10):.1f}")
        self.logic.set_end_timeout(value/10)

    def update_display(self):
        self.start_timeout.setValue(
               self.state.wake_word_activation_delay)

        end_timeout = int(10 * self.state.end_of_speech_silence)
        self.end_timeout.setValue(end_timeout)

        self.lbl_interrupt_thresh.setText(f"{self.state.interrupt_thresh}")
        self.interrupt_thresh.blockSignals(True)
        self.interrupt_thresh.setValue(int(self.state.interrupt_thresh))
        self.interrupt_thresh.blockSignals(False)

        self.select_language.blockSignals(True)

        # Find and set the correct language in the ComboBox
        for i in range(self.select_language.count()):

            print(f"Itemdata: {self.select_language.itemData(i)}, "
                  f"state language: {self.state.language}")
            if self.select_language.itemData(i) == self.state.language:
                self.select_language.setCurrentIndex(i)
                break

        self.select_language.blockSignals(False)
