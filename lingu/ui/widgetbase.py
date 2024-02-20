from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy
)
from PyQt6.QtCore import Qt


class CustomWidget(QWidget):
    """
    A custom widget class based on PyQt6, providing a frameless,
      draggable window with configurable elements.
    """

    def __init__(self):
        super().__init__()
        self.initialize_ui()
        self.setup_draggable_window()
        self.create_layouts()

    def initialize_ui(self):
        """Initializes basic UI properties."""
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setFixedWidth(800)

    def setup_draggable_window(self):
        """Configures the widget to be draggable."""
        self._drag_pos = None
        self._dragged = False

    def create_layouts(self):
        """Creates and configures layouts and widgets."""
        self.outer_layout = QHBoxLayout(self)
        self.setLayout(self.outer_layout)

        self.window_layout = QVBoxLayout()
        self.outer_layout.addLayout(self.window_layout)

        self.window_button_layout = QVBoxLayout()
        self.outer_layout.addLayout(self.window_button_layout)

        self.add_close_button()
        self.add_configure_button()

        self.border_widget = QWidget()
        self.window_layout.addWidget(self.border_widget)
        self.border_widget.setObjectName("borderWidget")
        self.main_border_layout = QVBoxLayout(self.border_widget)
        self.border_widget.setLayout(self.main_border_layout)

    def add_close_button(self):
        """Adds a close button to the window."""
        close_button = self.create_button("❌", self.close_window)
        self.window_button_layout.addWidget(close_button)

    def add_configure_button(self):
        """Adds a configuration button to the window."""
        self.configure_button = self.create_button("🛠️", self.configure_module)
        self.window_button_layout.addWidget(self.configure_button)
        self.configure_button.setEnabled(False)
        self.window_button_layout.addStretch()

    def create_button(self, text, callback):
        """Creates a button with specified text and callback function."""
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setMinimumSize(50, 50)
        button.setMaximumSize(50, 50)
        button.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        button.setStyleSheet('QPushButton { font-size: 21px; }')
        return button

    def close_window(self):
        """Closes the widget."""
        self.hide()

    def configure_module(self):
        """Configures the module (Placeholder for actual functionality)."""
        if hasattr(self, 'on_configure') and self.module:
            self.on_configure(self.module)
