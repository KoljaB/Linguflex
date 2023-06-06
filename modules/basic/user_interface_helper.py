import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QScrollArea, QDesktopWidget, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import pyqtSlot, QObject, QTimer, Qt, QMetaObject
import threading
import win32api
import win32con

from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message

set_section('user_interface')

try:
    window_startup_width =  cfg[get_section()].getint('window_startup_width', 450)
    window_startup_height =  cfg[get_section()].getint('window_startup_height', 150)
    window_maximum_height =  cfg[get_section()].getint('window_maximum_height', 400)
except Exception as e:
    raise ValueError(configuration_parsing_error_message + ' ' + str(e))


class AutoCloseWidget(QWidget):
    def mouseDoubleClickEvent(self, event) -> None:
        self.close()

class UI_Window():
    def __init__(self) -> None:
        self.is_running = True
        self.timer_finished = False
        # Get the size of the primary monitor
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        # Get the work area size of the primary monitor (excluding the taskbar)
        work_area = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))['Work']
        # Calculate the height of the taskbar
        taskbar_height = screen_height - work_area[3]
        # Calculate the width of the taskbar
        taskbar_width = screen_width - work_area[2]
        # Calculate the available height for the application
        self.available_height = work_area[3] - work_area[1]
        # Calculate the available width for the application
        self.available_width = work_area[2] - work_area[0]
        log(DEBUG_LEVEL_MAX, f'  [ui] screen size: {screen_width} x {screen_height}, taskbar: {taskbar_width} x {taskbar_height}, available: {self.available_width} x {self.available_height}')
        self.add_labels = []
        self.launch_ui_async()
        self.close_notify = None
        self.bring_to_top_request = False

    def set_close_notify_method(self, func) -> None:
        self.close_notify = func
                
    def line(self) -> None:
        self.add_label("", '#101010', '#303030', 1)

    def darkline(self) -> None:
        self.add_label("", '#101010', '#1A1A1A', 1)

    def blackline(self) -> None:
        self.add_label("", '#101010', '#101010', 3)

    def startup(self, 
            text: str, 
            fontsize = 8) -> None:
        self.add_label(text, '#808080', '#101010', fontsize)

    def startup_ready(self, text, fontsize = 8) -> None:
        self.startup('')
        self.add_label(text, '#E0E0E0', '#101010', fontsize)
        self.startup('')
        self.bring_to_top()

    def system(self, 
            text: str, 
            fontsize = 8) -> None:
        self.add_label(text, '#ffa500', '#101010', fontsize)

    def user(self, 
            text: str, 
            fontsize = 11) -> None:
        self.blackline()
        self.darkline()
        self.add_label(text, '#D0D0D0', '#1A1A1A', fontsize, True)
        self.darkline()
        self.line()
        self.darkline()

    def assistant(self, 
            text: str, 
            fontsize = 13) -> None:
        self.blackline()
        self.add_label(text, '#F0F0F0', '#101010', fontsize)
        self.blackline()
        self.blackline()
        self.bring_to_top()

    def bring_to_top(self) -> None:
        self.bring_to_top_request = True
        
    # Ugly and flickers too. Only solution to bring window to front that worked tho, tried some other stuff but failed
    def perform_bring_to_top(self) -> None:
        if hasattr(self, 'window'):
            self.window.setWindowState(Qt.WindowMinimized)
            self.window.setWindowState(Qt.WindowNoState)

    def add_label(self,
            text: str, 
            text_color: str, 
            text_backgroundcolor: str, 
            font_size=12, 
            align_right=False) -> None:
        self.add_labels.append((text, text_color, text_backgroundcolor, font_size, align_right))

    def launch_ui(self) -> None:
        # Create a new application instance
        self.app = QApplication(sys.argv)
        # Create a new UI window
        self.window = AutoCloseWidget()
        self.window.setWindowTitle('LinguFlex')
        # Position window at the lower right edge of the screen
        self.window.setGeometry(self.available_width - window_startup_width, self.available_height - window_startup_height, window_startup_width, window_startup_height)
        self.window.setWindowFlag(Qt.FramelessWindowHint)
        self.window.setStyleSheet('background-color: #101010;')
        self.window.closeEvent = self.close_event
        # Create a QVBoxLayout for the window
        window_layout = QVBoxLayout(self.window)
        # Create a scroll area
        self.scroll_area = QScrollArea(self.window)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.verticalScrollBar().rangeChanged.connect(self.ResizeScroll)
        # Add scroll area to the window layout
        window_layout.addWidget(self.scroll_area)
        # Create a container for the scroll area
        container = QWidget(self.scroll_area)
        self.scroll_area.setWidget(container)
        # Create a QVBoxLayout to hold labels
        self.layout = QVBoxLayout(container)    
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop) 
        spacer = QSpacerItem(0, 0, QSizePolicy.Maximum, QSizePolicy.Expanding)
        self.layout.addSpacerItem(spacer)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(500)
        # Show the window
        self.window.show()
        # Start the application event loop
        sys.exit(self.app.exec_())   

    def launch_ui_async(self) -> None:
        threading.Thread(target=self.launch_ui).start()

    def close(self) -> None:
        self.is_running = False
        while not self.timer_finished:
            time.sleep(0.1)

    def close_event(self, 
            event) -> None:
        self.timer.stop()
        if self.close_notify is not None:
            self.close_notify()

    def resize_repos(self) -> None:
        container_height = self.layout.sizeHint().height() 
        new_window_height = container_height + 25  
        if new_window_height > window_maximum_height: new_window_height = window_maximum_height
        if new_window_height < window_startup_height: new_window_height = window_startup_height
        if new_window_height - self.window.height() != 0:
            if new_window_height == window_maximum_height:
                self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.window.setGeometry(self.available_width - window_startup_width, self.available_height - new_window_height, window_startup_width, new_window_height)

    def ResizeScroll(self, min: int, maxi: int) -> None:
        self.scroll_area.verticalScrollBar().setValue(maxi)

    def update(self) -> None:
        global add_labels
        self.app.blockSignals(True)  
        self.timer.setInterval(100)            
        labels_to_add = len(self.add_labels) > 0
        while len(self.add_labels) > 0:
            current_label = self.add_labels.pop(0)
            new_label = QLabel(current_label[0])
            new_label.setStyleSheet(f'color: {current_label[1]}; background-color: {current_label[2]}; padding-right: 4px; ')
            font = QFont()
            font.setPointSize(current_label[3])
            if current_label[4]:
                font.setItalic(True)
                new_label.setAlignment(Qt.AlignRight)
            new_label.setFont(font)
            new_label.setWordWrap(True) 
            self.layout.addWidget(new_label)
        self.resize_repos()
        if self.bring_to_top_request:
            self.perform_bring_to_top()
            self.bring_to_top_request = False
        self.app.blockSignals(False)  
        if not self.is_running:
            self.timer.stop()
            self.window.close()
            self.timer_finished = True