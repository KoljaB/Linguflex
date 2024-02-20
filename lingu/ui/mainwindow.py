from PyQt6.QtCore import QTimer
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QMessageBox
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lingu")
        self.setGeometry(100, 100, 280, 80)

        self.setStyleSheet("background: transparent")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.borderless = False

        self.button = QPushButton("Click Me", self)
        self.button.setStyleSheet("background-color: white;")
        self.button.clicked.connect(self.on_button_clicked)
        self.button.resize(200, 40)
        self.button.move(40, 20)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_userinterface)
        fps = 60

        print("Starting UI timer...")
        self.timer.start(1000 // fps)

    def update_userinterface(self):
        pass

    def on_button_clicked(self):
        QMessageBox.information(self, "Hello", "You clicked the button!")
