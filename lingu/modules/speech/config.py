from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QScrollArea, QSizePolicy, QLabel, QPushButton, QSpacerItem, QHBoxLayout, QPushButton, QComboBox, QTableWidget, QHeaderView, QTableWidgetItem, QAbstractItemView, QShortcut, QStyledItemDelegate, QSlider
from PyQt5.QtGui import QFont, QKeySequence, QPen, QColor, QPalette
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPoint, QEvent
from lingu import ConfigWindowBase, repeat
from .state import state
from .logic import logic

class SpeechConfig(ConfigWindowBase):
    def __init__(self):
        super().__init__()

        self.header("Text-To-Speech Engines Configuration", bright=True)

        self.save_button = self.header_button("💾", self.save_configuration)



        self.add("Azure", bright=True, font_size=24)
        self.add("", font_size=5)

        self.add("API Key", align="bottomleft", font_size=18, cursive=True)
        self.azure_api_key = QLineEdit(state.azure_api_key)
        self.azure_api_key.setReadOnly(False)
        self.azure_api_key.setEchoMode(QLineEdit.Password)
        self.top_layout.addWidget(self.azure_api_key)
        self.add("Region", align="bottomleft", font_size=18, cursive=True)
        self.azure_region = QLineEdit(state.azure_region)
        self.azure_region.setReadOnly(False)
        self.top_layout.addWidget(self.azure_region)        


        self.add("")


        self.add("Elevenlabs", bright=True, font_size=24)
        self.add("", font_size=5)

        self.add("API Key", align="bottomleft", font_size=18, cursive=True)
        self.elevenlabs_api_key = QLineEdit(state.elevenlabs_api_key)
        self.elevenlabs_api_key.setReadOnly(False)
        self.elevenlabs_api_key.setEchoMode(QLineEdit.Password)
        self.top_layout.addWidget(self.elevenlabs_api_key)

    def save_configuration(self):
        state.azure_api_key = self.azure_api_key.text()
        state.azure_region = self.azure_region.text()
        state.elevenlabs_api_key = self.elevenlabs_api_key.text()
        #logic.set_engine()

        print (f"state.azure_region: {state.azure_region}")
        state.save()