from asyncio import windows_utils
import sys
import time
import threading
import win32api
import win32con
import re
from core import log, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR, cfg
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QScrollArea, QSizePolicy, QLabel, QPushButton, QSpacerItem
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

WINDOW_STARTUP_WIDTH = int(cfg('window_width', section='user_interface'))
WINDOW_MAXIMUM_HEIGHT = int(cfg('window_height', section='user_interface'))

class AutoCloseWidget(QWidget):
    window_shown = pyqtSignal()  # define custom signal

    # def mouseDoubleClickEvent(self, event) -> None:
    #     self.close()

    def showEvent(self, event):  # override showEvent        
        super().showEvent(event)
        self.window_shown.emit()


class ClickableLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)

    def contextMenuEvent(self, event):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text())


class UIWindow:
    def __init__(self) -> None:
        self.is_running = True
        self.timer_finished = False


        work_area = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))['Work']
        self.available_height = work_area[3] - work_area[1]
        self.available_width = work_area[2] - work_area[0]


        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        taskbar_height = screen_height - work_area[3]
        taskbar_width = screen_width - work_area[2]
        log(DEBUG_LEVEL_MAX, f'  [ui] screen size: {screen_width} x {screen_height}, taskbar: {taskbar_width} x {taskbar_height}, available: {self.available_width} x {self.available_height}')
        self.add_labels = []
        self.close_notify = None
        self.bring_to_top_request = False
        self.user_input = ''
        self.notebook_data = None
        self.notebook_data_string = None
        self.notebook_data_changed = False
        self.launch_ui_async()

    def set_close_notify_method(self, func) -> None:
        self.close_notify = func

    def set_notebook_data(self, data):
        if not str(data) == self.notebook_data_string:
            self.notebook_data = data
            self.notebook_data_string = str(data)
            self.notebook_data_changed = True

    def add_label(self, text: str, text_color="#F0F0F0", text_backgroundcolor="#101010", font_size=13, align_right=False) -> None:
        self.show_window = True      
        self.add_labels.append(
            {
                "text": text,
                "text_color": text_color,
                "text_backgroundcolor": text_backgroundcolor,
                "font_size": font_size,
                "align_right": align_right
            })

    def bring_to_top(self) -> None:
        self.bring_to_top_request = True

    def launch_ui_async(self) -> None:
        threading.Thread(target=self.launch_ui).start()

    def add_chat_bubble(self, label):
        # bubble_widget = QWidget()
        # bubble_widget.setStyleSheet("margin: 0px; padding: 0px;")
        # bubble_layout = QVBoxLayout()
        # bubble_layout.setSpacing(0)  # Add this line

        # bubble = ClickableLabel(self.linkify(label["text"]))
        # bubble.setWordWrap(True)
        # bubble.setStyleSheet(
        #     "QLabel { background-color: %s; margin: 0px; color: %s; border-radius: 4px; padding: 2px; font-size: %dpx; }"  # Adjust font size here
        #     % (label["text_backgroundcolor"], label["text_color"], label["font_size"])  # Adjust colors here
        # )
        # bubble.setAlignment(Qt.AlignRight if label["align_right"] else Qt.AlignLeft)
        # bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # bubble.setTextInteractionFlags(Qt.TextBrowserInteraction)
        # bubble.setOpenExternalLinks(True)
        # bubble_layout.setContentsMargins(0, 0, 0, 0)

        # bubble_layout.addWidget(bubble)
        # bubble_widget.setLayout(bubble_layout)
        # bubble_widget.setMaximumWidth(WINDOW_STARTUP_WIDTH - 46)
        # self.chat_layout.addWidget(bubble_widget)        
        bubble = ClickableLabel(self.linkify(label["text"]))
        bubble.setWordWrap(True)
        bubble.setStyleSheet(
            "QLabel { background-color: %s; color: %s; border-radius: 4px; padding: 2px; font-size: %dpx; }"  # Adjust font size here
            % (label["text_backgroundcolor"], label["text_color"], label["font_size"])  # Adjust colors here
        )
        bubble.setAlignment(Qt.AlignRight if label["align_right"] else Qt.AlignLeft)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bubble.setTextInteractionFlags(Qt.TextBrowserInteraction)
        bubble.setOpenExternalLinks(True)
        self.chat_layout.addWidget(bubble) 

    def launch_ui(self) -> None:
        self.app = QApplication(sys.argv)
        self.window = AutoCloseWidget()
        self.window.setWindowTitle('LinguFlex')
        self.window.setGeometry(self.available_width - WINDOW_STARTUP_WIDTH, self.available_height - WINDOW_MAXIMUM_HEIGHT, WINDOW_STARTUP_WIDTH, WINDOW_MAXIMUM_HEIGHT)
        self.window.setWindowFlag(Qt.FramelessWindowHint)
        self.window.setStyleSheet('background-color: #101010;')
        self.window.closeEvent = self.close_event

        self.layout = QVBoxLayout(self.window)
             
        self.notebook_title = ClickableLabel("no notebook loaded")
        self.notebook_title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.notebook_title.setWordWrap(True)
        self.notebook_title.setAlignment(Qt.AlignTop)
        self.notebook_title.setAlignment(Qt.AlignCenter)
        self.notebook_title.setStyleSheet(
            "QLabel { background-color: %s; color: %s; border-radius: 4px; padding: 2px; font-size: %dpx; }"  # Adjust font size here
            % ("#222222", "white", 14)  # Adjust colors here
        )
        self.layout.addWidget(self.notebook_title)

        self.notebook_scroll_area = QScrollArea()
        self.notebook_scroll_area.setWidgetResizable(True)
        self.notebook_scroll_area.setStyleSheet("background-color: #333333;")  # Set dark background color
        self.layout.addWidget(self.notebook_scroll_area)

        # Create a widget and layout to contain the data and add it to the notebook_scroll_area
        self.notebook_data_widget = QWidget()
        self.notebook_data_layout = QVBoxLayout()
        self.notebook_data_widget.setLayout(self.notebook_data_layout)
        self.notebook_scroll_area.setWidget(self.notebook_data_widget)


        self.notebook_label = ClickableLabel("")
        self.notebook_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # Enable link accessibility by mouse
        self.notebook_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        # Enable opening of external links
        self.notebook_label.setOpenExternalLinks(True)

        self.notebook_label.setWordWrap(True)
        self.notebook_label.setAlignment(Qt.AlignTop)
        self.notebook_label.setStyleSheet(
            "QLabel { background-color: %s; color: %s; border-radius: 4px; padding: 2px; font-size: %dpx; }"  # Adjust font size here
            % ("#222222", "white", 17)  # Adjust colors here
        )
        self.notebook_data_layout.addWidget(self.notebook_label)


        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.verticalScrollBar().rangeChanged.connect(self.resize_scroll)
        self.layout.addWidget(self.scroll_area)

        self.chat_area = QWidget()
        self.chat_area.setMaximumWidth(WINDOW_STARTUP_WIDTH - 42)
        self.chat_layout = QVBoxLayout()
        self.chat_layout.addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Add spacer to layout
        self.chat_area.setLayout(self.chat_layout)

        self.scroll_area.setWidget(self.chat_area)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your message...")
        self.text_input.setStyleSheet("border-radius: 4px; padding: 2px; font-size: 16px; background-color: #222222; color: white;")  # Adjust font size and colors here
        self.layout.addWidget(self.text_input)       

        self.text_input.returnPressed.connect(self.user_message) 

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(500)
        self.show_window = True
        sys.exit(self.app.exec_())

    def user_message(self):
        text = self.text_input.text()

        if text:
            self.user_input = text
            self.text_input.clear()

    def close(self) -> None:
        self.is_running = False
        while not self.timer_finished:
            time.sleep(0.1)

    def close_event(self, event) -> None:
        self.timer.stop()
        if self.close_notify is not None:
            self.close_notify()

    def resize_repos(self) -> None:

        current_window_height = self.window.size().height()
        current_window_width = self.window.size().width()

        new_window_height = WINDOW_MAXIMUM_HEIGHT

        if new_window_height > WINDOW_MAXIMUM_HEIGHT:
            new_window_height = WINDOW_MAXIMUM_HEIGHT

        if new_window_height - current_window_height != 0:
            if new_window_height == WINDOW_MAXIMUM_HEIGHT:
                self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            window_width = WINDOW_STARTUP_WIDTH
            window_height = new_window_height
            self.window.resize(window_width, window_height)

            window_height = self.window.frameGeometry().height()
            window_width = self.window.frameGeometry().width()
            self.window.move(self.available_width-window_width, self.available_height-window_height)    

    def resize_scroll(self, min: int, maxi: int) -> None:
        self.scroll_area.verticalScrollBar().setValue(maxi)

    def update(self) -> None:
        if not self.window.isVisible() and self.show_window:
            self.window.show()
        elif self.window.isVisible() and not self.show_window:
            self.window.hide()
        self.app.blockSignals(True)  
        self.timer.setInterval(100)            
        while len(self.add_labels) > 0:
            current_label = self.add_labels.pop(0)
            self.add_chat_bubble(current_label)
        #self.resize_repos()
        if self.bring_to_top_request:
            self.perform_bring_to_top()
            self.bring_to_top_request = False
        self.app.blockSignals(False)  
        if not self.is_running:
            self.timer.stop()
            self.window.close()
            self.timer_finished = True

        if self.notebook_data_changed:
            self.notebook_title.setText(self.notebook_data["name"])
            displayed_string = ''
            for entry in self.notebook_data["entries"]:
                displayed_string += entry["text"] + "\n"

            self.notebook_label.setText(self.linkify(displayed_string))
            self.notebook_data_changed = False

    def linkify(self, text):
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        urls = re.findall(url_pattern, text)
        for url in urls:
            text = text.replace(url, f'<a href="{url}" style="color: #A0A0FF;">↪ {url}</a>')
        return text

    def perform_bring_to_top(self) -> None:
        if hasattr(self, 'window'):
            self.window.setWindowState(Qt.WindowMinimized)
            self.window.setWindowState(Qt.WindowNoState)