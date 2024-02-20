from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QGridLayout
)
from PyQt6.QtCore import QTimer, pyqtSlot
from PyQt6.QtGui import QColor
from lingu import UI, Line
from qfluentwidgets import ColorPickerButton, SwitchButton, setTheme, Theme


class HouseUI(UI):
    def __init__(self):
        super().__init__()

        self.bulb_color_picker = {}
        self.bulb_onoff = {}
        self.device_onoff = {}
        # self.device_watts = {}

        label = UI.headerlabel("🏠 House")
        self.header(label, nostyle=True)

        setTheme(Theme.DARK)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(100)

        self.add_ui_listener(self, "states_ready", "house", "on_states_ready")

    def on_timer(self):
        if not self.isVisible():
            return

        self.timer.setInterval(5000)

        self.logic.trigger_states()

    @pyqtSlot()
    def on_states_ready(self):

        for bulb_name in self.logic.get_bulb_names():
            bulb_state = self.logic.bulb_states[bulb_name]
            (r, g, b) = bulb_state["color"]
            self.bulb_color_picker[bulb_name].setColor(
                QColor(r, g, b)
            )

            switchButton = self.bulb_onoff[bulb_name]
            switchButton.blockSignals(True)
            switchButton.setChecked(bulb_state["is_on"])
            switchButton.blockSignals(False)

        for outlet_name in self.logic.get_outlet_names():
            outlet_state = self.logic.outlet_states[outlet_name]

            switchButton = self.device_onoff[outlet_name]
            switchButton.blockSignals(True)
            switchButton.setChecked(outlet_state["is_on"])
            switchButton.blockSignals(False)

            # self.device_watts[outlet_name].setText(
            #     f"{outlet_state['power']} W"
            # )

    def init(self):

        main_widget = QWidget()

        line = Line()
        line.add(main_widget)
        self.add(line)

        i = 0
        self.grid_layout = QGridLayout(main_widget)
        self.grid_layout.setSpacing(0)

        label = UI.label("Bulb")
        label.setStyleSheet("margin-left: 2px; margin-bottom: 1 px; color: #ffffff; font-size: 18px;")
        self.grid_layout.addWidget(label, i, 0)
        label = UI.label("State")
        label.setStyleSheet("margin-left: 0px; margin-bottom: 1 px; color: #ffffff; font-size: 18px;")
        self.grid_layout.addWidget(label, i, 1)
        label = UI.label("Color")
        label.setStyleSheet("margin-left: 37px; margin-bottom: 1 px; color: #ffffff; font-size: 18px;")
        self.grid_layout.addWidget(label, i, 2)
        i += 1

        for bulb_name in self.logic.get_bulb_names():
            label = UI.label(f" {bulb_name}  ", "content")
            self.grid_layout.addWidget(label, i, 0)

            switchButton = SwitchButton(
                parent=self
                )
            switchButton.setText(bulb_name)
            switchButton.checkedChanged.connect(
                lambda checked, bulb_name=bulb_name:
                self.on_bulb_checked_changed(checked, bulb_name)
            )
            self.grid_layout.addWidget(switchButton, i, 1)
            self.bulb_onoff[bulb_name] = switchButton

            switchButtonContainer = QWidget()
            switchButtonLayout = QHBoxLayout(switchButtonContainer)
            switchButtonLayout.setContentsMargins(40, 0, 0, 0)
            colorPicker = ColorPickerButton(
                QColor("#5012aaa2"),
                'Background Color',
                self,
                enableAlpha=False)
            colorPicker.colorChanged.connect(
                lambda color, bulb_name=bulb_name:
                self.on_color_changed(color, bulb_name)
            )
            self.bulb_color_picker[bulb_name] = colorPicker
            switchButtonLayout.addWidget(colorPicker)
            switchButtonContainer.setLayout(switchButtonLayout)
            self.grid_layout.addWidget(switchButtonContainer, i, 2)

            i += 1

        self.grid_layout.addWidget(UI.label(), i, 0)
        i += 1

        label = UI.label("Device")
        label.setStyleSheet("margin-left: 2px; margin-bottom: 1 px; color: #ffffff; font-size: 18px;")
        self.grid_layout.addWidget(label, i, 0)
        label = UI.label("State")
        label.setStyleSheet("margin-left: 0px; margin-bottom: 1 px; color: #ffffff; font-size: 18px;")
        self.grid_layout.addWidget(label, i, 1)
        # label = UI.label(
        #     "W", align="bottomleft", font_size=18,
        #     bright=True
        # )
        # label.setStyleSheet("margin-left: 5px; margin-bottom: 1 px; color: #ffffff; font-size: 18px;")
        # self.grid_layout.addWidget(label, i, 2)
        i += 1

        for outlet_name in self.logic.get_outlet_names():
            label = UI.label(f" {outlet_name}  ", "content")
            self.grid_layout.addWidget(label, i, 0)

            switchButtonContainer = QWidget()
            switchButtonLayout = QHBoxLayout(switchButtonContainer)
            switchButtonLayout.setContentsMargins(0, 5, 0, 5)
            switchButton = SwitchButton(
                parent=self
                )
            switchButton.checkedChanged.connect(
                lambda checked, outlet_name=outlet_name:
                self.on_outlet_checked_changed(checked, outlet_name)
            )            
            self.device_onoff[outlet_name] = switchButton
            switchButtonLayout.addWidget(switchButton)
            switchButtonContainer.setLayout(switchButtonLayout)
            self.grid_layout.addWidget(switchButtonContainer, i, 1)

            # label_watts = UI.label(
            #     "0 W", align="bottomleft", font_size=18, bright=True
            # )
            # self.device_watts[outlet_name] = label_watts
            # self.grid_layout.addWidget(label_watts, i, 2)

            i += 1

    def on_color_changed(self, color, bulb_name):
        self.logic.set_color_hex(bulb_name, color.name())

    def on_bulb_checked_changed(self, checked, bulb_name):
        print(f"trying to set {bulb_name} to {checked}")
        self.logic.set_bulb_on_off(bulb_name, checked)

    def on_outlet_checked_changed(self, checked, outlet_name):
        print(f"trying to set {outlet_name} to {checked}")
        self.logic.set_outlet_on_off(outlet_name, checked)
