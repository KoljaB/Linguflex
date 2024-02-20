from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
)
from lingu import UI, Line


class WeatherUI(UI):
    def __init__(self):
        super().__init__()

        label = UI.headerlabel("🌤️ Weather")
        self.header(label, nostyle=True)

    def set_label_style(self, label):
        label.setStyleSheet("margin-left: 2px; margin-bottom: 1 px; "
                            "color: #ffffff; font-size: 18px;")

    def init(self):
        line = Line()
        main_widget = QWidget()
        line.add(main_widget)
        self.add(line)

        self.grid_layout = QGridLayout(main_widget)
        self.grid_layout.setSpacing(0)

        # Use this method to set the stretch factor of each column to 0
        # Assuming 4 columns for date, temp, weather, wind
        for column in range(4):
            self.grid_layout.setColumnStretch(column, 0)
            # Set a minimum width if necessary
            self.grid_layout.setColumnMinimumWidth(column, 100)

        # Add header labels
        headers = ["Date", "Temp", "Weather", "Wind"]
        for column, header_text in enumerate(headers):
            label = QLabel(header_text)
            label.setStyleSheet("margin-left: 2px; margin-bottom: 1px; "
                                "color: #ffffff; font-size: 18px;")
            self.grid_layout.addWidget(label, 0, column)

        # Add weather data rows
        i = 1
        for weather_line in self.logic.get_weather()["ui_data"]:
            date, temp, weather, wind = weather_line
            for column, value in enumerate([date, temp, weather, wind]):
                label = QLabel(f" {value}   ")
                self.grid_layout.addWidget(label, i, column)
            i += 1
