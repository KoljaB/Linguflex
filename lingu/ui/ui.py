from PyQt6.QtWidgets import (
    QSlider,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QSizePolicy,
    QSpacerItem,
    QApplication
)
from PyQt6.QtCore import QMetaObject, Qt
from PyQt6.QtGui import QTextOption
from PyQt6 import QtCore

from .draggable import DraggableWidget
from qfluentwidgets import Slider

from lingu import events
from .line import Line
import time

FOCUSED_BORDER = "#B0B0B0"
UNFOCUSED_BORDER = "#808080"
FOCUSED_HEADER_BORDER = "#FFFFB0"
UNFOCUSED_HEADER_BORDER = "#B0B0B0"
FOCUSED_HEADER_FONT = "#FFFFC0"
UNFOCUSED_HEADER_FONT = "#C0C0C0"

FOCUSED_THRESHOLD_TIME = 0.1


class UI(DraggableWidget):
    """
    A custom widget class based on PyQt6, providing a frameless,
    draggable window with configurable elements.
    """

    def __init__(self):
        super().__init__()
        self.logic = None
        self.module_name = None
        self.setup_draggable_window()
        self.create_layouts()
        self.set_focused_style(is_focused=True)
        self.focused_time = 0
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        QApplication.instance().focusChanged.connect(self.onFocusChanged)

    def onFocusChanged(self, old, new):
        """Handle global focus change."""
        if self.isAncestorOf(new):
            # Focus moved to a child widget
            self.set_focused_style(is_focused=True)
        elif self.isAncestorOf(old) and not self.isAncestorOf(new):
            # Focus moved outside the widget
            self.set_focused_style(is_focused=False)
            self.focused_time = time.time()

    def init(self):
        pass

    def add_listener(
            self,
            event_name: str,
            trigger_module_name: str,
            callback
    ):
        """Registers a callback for a specified event.

        Args:
            event_name (str): The name of the event to listen for.
            trigger_module_name (str): The name of the module triggering
              the event.
            callback: The function to call when the event is triggered.
        """
        events.add_listener(event_name, trigger_module_name, callback)

    def add_ui_listener(
            self,
            object: QtCore.QObject,
            event_name: str,
            trigger_module_name: str,
            callback_method_name: str
    ):
        """Registers a ui thread invoked callback for a specified event.

        Args:
            object (QObject): The object to invoke the callback on.
            event_name (str): The name of the event to listen for.
            trigger_module_name (str): The name of the module triggering
              the event.
            callback_method_name: The function name to call when the event
            is triggered.
        """
        events.add_listener(
            event_name,
            trigger_module_name,
            lambda: QMetaObject.invokeMethod(
                object,
                callback_method_name,
                Qt.ConnectionType.QueuedConnection))

    def trigger(self, event_name: str, data=None):
        """Triggers an event with optional data.

        Args:
            event_name (str): The name of the event to trigger.
            data: Optional data to pass with the event.

        Returns:
            The result of the event trigger.
        """
        return events.trigger(event_name, self.module_name, data)

    def trigger_with_params(self, event_name: str, **kwargs):
        """Triggers an event with named parameters.

        Args:
            event_name (str): The name of the event to trigger.
            **kwargs: Arbitrary keyword arguments to pass with the event.

        Returns:
            The result of the event trigger.
        """
        return events.trigger_with_params(
            event_name,
            self.module_name,
            **kwargs
        )

    def had_focus_recently(self):
        return time.time() - self.focused_time < FOCUSED_THRESHOLD_TIME

    def setup_draggable_window(self):
        """Configures the widget to be draggable."""
        self._drag_pos = None
        self._dragged = False

    def create_layouts(self):
        """Creates and configures layouts and widgets."""

        self.outer_layout = QHBoxLayout(self)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)
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

        self.header_layout = QVBoxLayout(self.border_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.border_widget.setLayout(self.header_layout)

        self.header_line = Line(
            align=Qt.AlignmentFlag.AlignVCenter,
            background_color="#303030",
            is_header=True)
        self.header_line.setFixedHeight(50)
        self.header_layout.addWidget(self.header_line)

        self.content_widget = QWidget()
        self.content_widget.setContentsMargins(10, 10, 10, 10)
        self.header_layout.addWidget(self.content_widget)

        self.main_border_layout = QVBoxLayout(self.content_widget)
        self.main_border_layout.setContentsMargins(5, 5, 5, 5)

    def add_spacer(self):
        # Add a vertical spacer that pushes everything to the top
        spacer = QSpacerItem(
            1, 1,
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_border_layout.addItem(spacer)

    def add(self, widget):
        self.main_border_layout.addWidget(widget)
        return widget

    def add_slider(
            self,
            label: str,
            descr_val_left: str,
            descr_val_right: str,
            default_val: int
    ):

        self.add(UI.label(label))

        line = Line()
        label_descr_left = UI.label(descr_val_left)
        label_descr_left.setWordWrap(False)
        label_descr_left.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_descr_left)
        label_value = UI.label(
            str(default_val),
            "one_line_content")
        line.add(label_value)
        label_descr_right = UI.label(descr_val_right)
        label_descr_right.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        line.add(label_descr_right)
        self.add(line)

        slider = Slider(
            Qt.Orientation.Horizontal,
            self)
        slider.setMinimum(0)
        slider.setMaximum(10000)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(1)
        self.add(slider)

        return label_value, slider

    def remove(self, widget):
        self.main_border_layout.removeWidget(widget)
        return widget

    def add_close_button(self):
        """Adds a close button to the window."""
        close_button = UI.button("❌", self.close_window)
        self.window_button_layout.addWidget(close_button)

    def add_configure_button(self):
        """Adds a configuration button to the window."""
        self.window_button_layout.addStretch()

    def add_buttons(self, buttons_dict):
        """Adds buttons from a dictionary to the window.

        Args:
            buttons_dict (dict): A dictionary where keys are button names and
                                values are tuples (symbol, callback).

        Returns:
            dict: A dictionary of created buttons with their names.
        """
        created_buttons = {}
        for name, (symbol, callback) in buttons_dict.items():
            btn = self.add_button(symbol, callback)
            created_buttons[name] = btn
        return created_buttons

    def add_button(self, title, callback):
        button = UI.button(title, callback)
        self.header_line.right_right.addWidget(button)
        return button

    def close_window(self):
        """Closes the widget."""
        self.hide()

    def configure_module(self):
        """Configures the module (Placeholder for actual functionality)."""
        if hasattr(self, 'on_configure') and self.module:
            self.on_configure(self.module)

    def buttons_width(self):
        """
        Calculates the distance in pixels between the right border of the
        widget and the right border of the border_widget.

        Returns:
            int: The distance in pixels.
        """
        # can't figure out how to reliably calculate this automatically
        # so just hardcode it for now
        return 45

    def header(
            self,
            item,
            align="leftleft",
            bright=False,
            editable=False,
            nostyle=False):
        """
        Adds an item to the header bar.
        Supports labels and editable text fields.

        Args:
            item (str/QWidget): The item to add. Can be a string or a QWidget.
            align (str): Alignment for the item ('left', 'right', etc.).
            bright (bool): If True, applies a bright style to the item.
            editable (bool): If True, creates an editable QLineEdit
              for the item.
        """
        widget = self.create_header_widget(item, editable)
        UI.align_item(item, align)
        if not nostyle:
            UI.set_style(widget, align=align, bright=bright, font_size=28)
        return self.add_header(widget, align=align)

    def add_header(self, widget, align="leftleft"):
        if "leftleft" in align:
            self.header_line.left_left.addWidget(widget)
        elif "leftright" in align:
            self.header_line.left_right.addWidget(widget)
        elif "rightright" in align:
            self.header_line.right_right.addWidget(widget)
        else:
            self.header_line.right_left.addWidget(widget)
        return widget

    @staticmethod
    def layout(widget):
        layout = QVBoxLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    @staticmethod
    def label(text="",
              object_name="description") -> QLabel:
        label = QLabel(text)
        label.setObjectName(object_name)
        label.setWordWrap(True)
        label.setContentsMargins(0, 0, 0, 0)
        label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        return label

    @staticmethod
    def headerlabel(text):
        label = QLabel(text)
        label.setWordWrap(False)
        label.setObjectName("headerLabel")
        return label

    @staticmethod
    def button(text, callback, size=44):
        """Creates a button with specified text and callback function."""
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setMinimumSize(size, size)
        button.setMaximumSize(size, size)
        button.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed)
        return button

    @staticmethod
    def textedit(text="", callback=None) -> QTextEdit:
        """Create and return a QTextEdit for multi-line text input."""
        input_field = QTextEdit(text)
        input_field.setWordWrapMode(
            QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere
        )
        input_field.setReadOnly(False)
        input_field.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed)
        if callback is not None:
            input_field.textChanged.connect(callback)
        return input_field

    @staticmethod
    def lineedit(text="", callback=None) -> QLineEdit:
        """Create and return a QLineEdit for single-line text input."""
        input_field = QLineEdit(text)
        input_field.setReadOnly(False)
        input_field.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed)
        if callback is not None:
            input_field.textChanged.connect(callback)
        return input_field

    def create_header_widget(self, item, editable):
        """
        Creates a header widget based on the item type.

        Args:
            item (str/QWidget): The item to add.
            editable (bool): If True, creates an editable QLineEdit.

        Returns:
            QWidget: The created header widget.
        """
        if isinstance(item, str):
            return QLineEdit(item) if editable else QLabel(item)
        return item  # Assuming item is already a QWidget

    @staticmethod
    def set_style(
            item,
            align="",
            bright=False,
            font_size=20,
            cursive=False):
        """
        Sets the style for a header item.

        Args:
            item (QWidget): The widget to style.
            align (str): The alignment for the widget.
            bright (bool): If True, applies a bright style.
            font_size (int): Font size for the widget.
            cursive (bool): If True, applies italic font style.
        """
        UI.align_item(item, align)
        color = "#FFFFFF" if bright else "#B0B0B0"
        font_style = "italic" if cursive else "normal"
        item.setStyleSheet(f"color: {color}; font-size: {font_size}px; "
                           f"font-style: {font_style};")

    @staticmethod
    def align_item(item, align=""):
        """
        Aligns an item within its parent layout in PyQt6.

        Args:
            item (QWidget): The widget to align.
            align (str): The alignment string
              ('left', 'center', 'right', etc.).
        """
        if not align:
            return
        alignment_map = {
            "topleft": Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            "top": Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop,
            "topright": (Qt.AlignmentFlag.AlignRight |
                         Qt.AlignmentFlag.AlignTop),
            "left": (Qt.AlignmentFlag.AlignLeft |
                     Qt.AlignmentFlag.AlignVCenter),
            "center": Qt.AlignmentFlag.AlignCenter,
            "right": (Qt.AlignmentFlag.AlignRight |
                      Qt.AlignmentFlag.AlignVCenter),
            "bottomleft": (Qt.AlignmentFlag.AlignLeft |
                           Qt.AlignmentFlag.AlignBottom),
            "bottom": (Qt.AlignmentFlag.AlignCenter |
                       Qt.AlignmentFlag.AlignBottom),
            "bottomright": (Qt.AlignmentFlag.AlignRight |
                            Qt.AlignmentFlag.AlignBottom)
        }

        item.setAlignment(alignment_map.get(align,
                                            Qt.AlignmentFlag.AlignLeft |
                                            Qt.AlignmentFlag.AlignVCenter))

    def set_focused_style(self, is_focused):
        """Sets the style for the widget when it is focused.

        Args:
            is_focused (bool): If True, sets the focused style.
        """
        self.header_line.border_color = (FOCUSED_HEADER_BORDER
                                         if is_focused
                                         else UNFOCUSED_HEADER_BORDER)
        self.header_line.update()
        self.create_style_sheet(
            FOCUSED_BORDER if is_focused else UNFOCUSED_BORDER,
            FOCUSED_HEADER_FONT if is_focused else UNFOCUSED_HEADER_FONT
        )

    def create_style_sheet(
            self,
            window_border,
            header_fontcolor="#C0C0C0"):

        self.setStyleSheet(f"""
            #borderWidget {{
                border: 1px solid {window_border};
                background-color: #181818;
            }}
            #headerLabel {{
                color: {header_fontcolor};
            }}
            QWidget {{
                font-size: 20px;
                color: white;
            }}
            QPushButton {{
                background-color: rgba(0, 0, 0, 0.01);
                color: white;
                padding: 5px;
                border: 0px;
            }}
            QPushButton:hover {{
                background-color: #000000;
                border: 1px solid #B0B0B0;
            }}
            QPushButton:pressed {{
                background-color: #404040;
            }}
            QPushButton:disabled {{
                background-color: rgba(48, 48, 48, 128);
                color: #707070;
                border: 0px;
            }}
            QLabel {{
                color: #B0B0B0;
            }}
            QLineEdit, QTextEdit {{
                background-color: #454545;
                color: white;
                border: 2px solid #5A5A5A;
                padding: 5px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                color: #FFFFFF;
            }}
            QLineEdit:hover, QTextEdit:hover {{
                background-color: #555555;
            }}
            QScrollArea {{
                background-color: #454545;
                border: 2px solid #5A5A5A;
            }}
            QSlider {{
                margin-top: 5px;
                margin-bottom: 5px;
            }}
            QLabel {{
                margin-top: 5px;
                margin-bottom: 5px;
            }}
            #description {{
                margin-top: 5px;
                margin-bottom: 0px;
                color: #B0B0B0;
                font-size: 18;
                font-style: italic;
            }}
            #one_line_content {{
                margin-top: 7px;
                margin-bottom: 3px;
                color: #FFFFFF;
                font-size: 18;
            }}
            #content {{
                margin-top: 0px;
                margin-bottom: 5px;
                color: #FFFFFF;
                font-size: 18;
            }}
            QGroupBox {{
                border: 1px solid #808080;
                margin-top: 58px;
                font-size: 20px;
                font-weight: bold;
                border-top-right-radius: 5px;
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #303030,
                                                stop: 1 #202020);
                border-top-color: #B0B0B0;
                border-bottom-color: #505050;
            }}
            QGroupBox::title {{
                border: 1px solid #808080;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 5px 8px;
                margin-left: 0px;
                margin-top: 20px;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #606060,
                                                stop: 0.1 #404040,
                                                stop: 1 #303030);
                color: rgb(255, 255, 255);
                border-top-color: #B0B0B0;
                border-bottom-color: #505050;
            }}
        """)
