from asyncio import windows_utils
import sys
import time
import threading
import win32api
import win32con
import re
import os
import copy
from core import cfg, log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QScrollArea, QSizePolicy, QLabel, QPushButton, QSpacerItem, QHBoxLayout, QPushButton, QComboBox, QTableWidget, QHeaderView, QTableWidgetItem, QAbstractItemView, QShortcut, QStyledItemDelegate
from PyQt5.QtGui import QFont, QKeySequence, QPen, QColor, QPalette
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPoint, QEvent

from datetime import datetime

WINDOW_STARTUP_WIDTH = int(cfg('window_width', section='user_interface'))
WINDOW_MAXIMUM_HEIGHT = int(cfg('window_height', section='user_interface'))

class BaseWidget(QWidget):
    def __init__(self, parent=None):
        super(BaseWidget, self).__init__(parent)
        self._drag_pos = None
        self._resize_drag = False

    def mousePressEvent(self, event):
        self._drag_pos = event.globalPos()
        if self.rect().bottomRight().x() - 10 <= event.pos().x() <= self.rect().bottomRight().x() and self.rect().bottomRight().y() - 10 <= event.pos().y() <= self.rect().bottomRight().y():
            self._resize_drag = True
        else:
            self._resize_drag = False

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self._resize_drag:
                self.resize(event.globalPos().x() - self.pos().x(), event.globalPos().y() - self.pos().y())
            else:
                if self._drag_pos:
                    self.move(self.pos() + event.globalPos() - self._drag_pos)
            self._drag_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self._resize_drag = False
        self._drag_pos = None


    window_shown = pyqtSignal() 

    def showEvent(self, event): 
        super().showEvent(event)
        self.window_shown.emit()

class BaseButton(QPushButton):
    def __init__(self, content=None, width=46, height=46):
        super(BaseButton, self).__init__(content)
        self.set_button_state()
        self.setFixedWidth(width)  
        self.setFixedHeight(height)

    def set_button_state(self, state = 0, font_size = 32):
        if state == 0:
            self.setStyleSheet("""
                QPushButton {{
                    border-radius: 3px;
                    font-size: {}px;
                    background-color: #222222;
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: #444444;
                }}
            """.format(font_size))  
        elif state == 1:
            self.setStyleSheet("""
                QPushButton {{
                    border-radius: 3px;
                    font-size: {}px;
                    background-color: #60A060;
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: #80C080;
                }}
            """.format(font_size))  
        else:
            self.setStyleSheet("""
                QPushButton {{
                    border-radius: 3px;
                    font-size: {}px;
                    background-color: #AA0000;
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: #CC0000;
                }}
            """.format(font_size))  
            
class CloseableWidget(BaseWidget):
    def __init__(self, add_stretch = True):
        super(CloseableWidget, self).__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setStyleSheet('background-color: #303030;')
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)

        self.title_bar = QHBoxLayout()
        self.title_widget = QWidget()
        self.title_layout = QHBoxLayout(self.title_widget)
        self.title_layout.setAlignment(Qt.AlignBottom)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_layout.setSpacing(0)        

        self.close_button = QPushButton('❌')
        self.close_button.setStyleSheet("""
            QPushButton {
                margin-bottom: 5px;
                margin-left: 5px;
                background-color: #600000;
                font-size: 14px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #802020;
            }
        """)
        self.close_button.setFixedWidth(22)
        self.close_button.clicked.connect(self.close)
        
        if add_stretch: self.title_layout.addStretch() 
        self.title_layout.addWidget(self.close_button, alignment= Qt.AlignTop)
        self.layout.addWidget(self.title_widget)

class CustomHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super(CustomHeader, self).__init__(orientation, parent)
    def sectionSizeFromContents(self, index):
        size = super(CustomHeader, self).sectionSizeFromContents(index)
        size.setHeight(18) 
        return size

class PlayerWidget(CloseableWidget):
    rowClicked = pyqtSignal(int) 

    def __init__(self):
        super(PlayerWidget, self).__init__(False)
        self.last_playlist = None  
           
        self.audio_name = ClickableLabel("")
        self.audio_name.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.audio_name.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.audio_name.setOpenExternalLinks(True)

        self.audio_name.setFixedHeight(26)  
        self.audio_name.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)  
        self.audio_name.setWordWrap(True)
        self.title_layout.insertWidget(0, self.audio_name, alignment=Qt.AlignTop)


        self.buttons_widget = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_widget) 
        self.buttons_layout.setSpacing(0)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0) 
        self.buttons_widget.setStyleSheet("background-color: #222222; margin: 0px; padding: 0px;") 

        button_font_size = 30
        button_width = 46
        button_height = 50

        self.back_button = BaseButton('⏮️', button_width, button_height)
        self.back_button.set_button_state(font_size=button_font_size)
        self.back_button.clicked.connect(lambda: self.button_clicked('back'))
        self.buttons_layout.addWidget(self.back_button)

        self.forward_button = BaseButton('⏭️', button_width, button_height)
        self.forward_button.set_button_state(font_size=button_font_size)
        self.forward_button.clicked.connect(lambda: self.button_clicked('forward'))
        self.buttons_layout.addWidget(self.forward_button)

        self.pause_button = BaseButton('⏯️', button_width, button_height)
        self.pause_button.set_button_state(font_size=button_font_size)
        self.pause_button.clicked.connect(lambda: self.button_clicked('pause_continue'))
        self.buttons_layout.addWidget(self.pause_button)

        self.stop_button = BaseButton('⏹️', button_width, button_height)
        self.stop_button.set_button_state(font_size=button_font_size)
        self.stop_button.clicked.connect(lambda: self.button_clicked('stop'))
        self.buttons_layout.addWidget(self.stop_button)

        self.volume_down_button = BaseButton('🔉', button_width, button_height)
        self.volume_down_button.set_button_state(font_size=button_font_size)
        self.volume_down_button.clicked.connect(lambda: self.button_clicked('volume_down'))
        self.buttons_layout.addWidget(self.volume_down_button)

        self.volume_up_button = BaseButton('🔊', button_width, button_height)
        self.volume_up_button.set_button_state(font_size=button_font_size)
        self.volume_up_button.clicked.connect(lambda: self.button_clicked('volume_up'))
        self.buttons_layout.addWidget(self.volume_up_button)
        
        self.buttons_layout.addStretch(1)

        self.audio_time = ClickableLabel("0:00")
        self.set_isplaying_styles(False)
        self.buttons_layout.addWidget(self.audio_time)
         
        self.layout.addWidget(self.buttons_widget) 

        self.player_scroll_area = QScrollArea()
        self.player_scroll_area.setWidgetResizable(True)
        self.player_scroll_area.setStyleSheet("border: 0px")  

        self.playlist = QTableWidget()
        self.playlist.setColumnCount(3)  
        self.playlist.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.playlist.verticalHeader().setVisible(False)
        
        # Connect the itemClicked signal to a slot
        self.playlist.itemClicked.connect(self.on_item_clicked)        

        # Adjust the stretch of the columns
        self.playlist.horizontalHeader().setMinimumSectionSize(1)
        self.playlist.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Position column
        self.playlist.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Duration column
        self.playlist.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Title column

        # Set a minimal row height
        self.playlist.verticalHeader().setDefaultSectionSize(26)
        self.playlist.horizontalHeader().setVisible(False)

        # Remove grid lines
        self.playlist.setShowGrid(True)

        # Style the headers, rows, and cells
        header_style = "QHeaderView::section { background-color: #222222; color: #D0D0D0; font-size: 18px; padding: 0px; margin: 0px; }"
        cell_style = "QTableWidget { background-color: #222222; color: #D0D0D0; font-size: 18px; padding: 0px; margin: 0px; }"
        self.playlist.horizontalHeader().setStyleSheet(header_style)
        self.playlist.verticalHeader().setStyleSheet(header_style)
        self.playlist.setStyleSheet(cell_style)

        self.player_scroll_area.setWidget(self.playlist)        

        self.layout.addWidget(self.player_scroll_area)

    def set_isplaying_styles(self, is_playing):
        if is_playing:
            self.audio_name.setStyleSheet("QLabel { background-color: #222222; color: #00F2C1; padding: 2px; font-size: 18px; font-weight: bold;}")
            self.audio_time.setStyleSheet("QLabel { background-color: #222222; color: #00F2C1; padding: 2px; font-size: 20px; font-weight: bold;}")
        else:
            self.audio_name.setStyleSheet("QLabel { background-color: #222222; color: #E0E0E0; padding: 2px; font-size: 18px; }")
            self.audio_time.setStyleSheet("QLabel { background-color: #222222; color: #D0D0D0; padding: 2px; font-size: 20px; }")

    def button_clicked(self, button_name):
        if button_name == "forward":
            self.server.set_event("skip_audio", 1)
        elif button_name == "back":
            self.server.set_event("skip_audio", -1)
        else:
            self.server.set_event(button_name)

    def format_duration(self, seconds):
        # Calculate hours, minutes and seconds
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        s = int(s)
        m = int(m)
        h = int(h)

        if h:
            return f"{h}:{m:02d}:{s:02d}"
        else:
            return f"{m}:{s:02d}"
        
    def on_item_clicked(self, item):
        # Emit the rowClicked signal with the row index
        self.rowClicked.emit(item.row())        

    def display(self, audio_information):
        if not audio_information:
            self.audio_name.setText("")
            self.audio_time.setText("0:00")
        else:
            self.audio_name.setText(audio_information["name"])
            self.audio_time.setText(self.format_duration(audio_information["seconds_left"]))

            self.set_isplaying_styles(audio_information["playing"])

            playlist_changed = self.last_playlist != audio_information["playlist"]

            audio_index_changed = "audio_index" in audio_information and (
                not hasattr(self, 'last_audio_index') or self.last_audio_index != audio_information["audio_index"])

            if playlist_changed or audio_index_changed:
                self.playlist.setRowCount(0)

                for pos, entry in enumerate(audio_information["playlist"]):
                    self.playlist.insertRow(pos)

                    if isinstance(entry, str):
                        self.playlist.setItem(pos, 2, QTableWidgetItem(entry))
                    else:
                        duration = self.format_duration(entry["length"])

                        pos_item = QTableWidgetItem(str(pos + 1) + " ")
                        pos_item.setTextAlignment(Qt.AlignLeft)
                        self.playlist.setItem(pos, 0, pos_item)

                        duration_item = QTableWidgetItem(duration + " ")
                        duration_item.setTextAlignment(Qt.AlignRight)
                        self.playlist.setItem(pos, 1, duration_item)

                        title_item = QTableWidgetItem(entry["title"])
                        title_item.setTextAlignment(Qt.AlignLeft)
                        
                        # If this is the current playing audio, set its font to bold
                        if "audio_index" in audio_information and audio_information["audio_index"] == pos:
                            bold_font = QFont()
                            bold_font.setBold(True)
                            pos_item.setFont(bold_font)
                            duration_item.setFont(bold_font)
                            title_item.setFont(bold_font)
                        
                        self.playlist.setItem(pos, 2, title_item)

                self.last_playlist = copy.deepcopy(audio_information["playlist"])

                if audio_index_changed:
                    self.last_audio_index = audio_information["audio_index"]

class ClickableLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)

    def contextMenuEvent(self, event):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text())

class ReturnAcceptTextEdit(QTextEdit):
    returnPressed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(ReturnAcceptTextEdit, self).__init__(*args, **kwargs)
        self.installEventFilter(self)    

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        if obj == self and event.type() == QEvent.FocusIn:
            self.setStyleSheet("""
                QTextEdit {
                    margin-top: 2px;
                    padding: 2px;
                    font-size: 20px;
                    background-color: #000000;
                    color: white;
                }
            """)
            self.setPlaceholderText("")
        elif obj == self and event.type() == QEvent.FocusOut:
            self.setStyleSheet("""
                QTextEdit {
                    margin-top: 2px;
                    padding: 2px;
                    font-size: 20px;
                    background-color: #1A1A1A;
                    color: white;
                }
                QTextEdit:hover {
                    background-color: #2A2A2A;
                }
            """)
            self.setPlaceholderText("🖋️")
        return super().eventFilter(obj, event)    
class UIWindow:
    def __init__(self) -> None:
        os.environ['QT_LOGGING_RULES'] = '*=false' # '*=false;*.critical=true'        
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
        self.player_window_visible = False
        self.memory_data = None
        self.memory_data_string = None
        self.memory_data_changed = False
        self.audio_information = None
        self.audio_information_string = None
        self.microphone_recording = False
        self.microphone_recording_allowed = True
        self.wakeword_detection_active_changed = False
        self.wakeword_detection_active = True
        self.trigger_display_update = False

        self.launch_ui_async()

    def init_update(self) -> None:
        self.trigger_display_update = True        

    def set_server(self, server) -> None:

        def update_microphone_recording(state): 
            self.microphone_recording = state
            self.init_update()
        def update_microphone_recording_allowed(state):
            self.microphone_recording_allowed = state
            self.init_update()
        def update_wakeword_detection_active(state):
            self.wakeword_detection_active = state
            self.init_update()

        def update_audio_information(audio_information):
            if not str(audio_information) == self.audio_information_string:
                self.audio_information = audio_information
                self.audio_information_string = str(audio_information)
                self.init_update()            

        self.server = server
        self.player_window.server = server

        self.server.register_event("audio_information", update_audio_information)
        self.server.register_event("microphone_recording_allowed_changed", update_microphone_recording_allowed)
        self.server.register_event("microphone_recording_changed", update_microphone_recording)
        self.server.register_event("wakeword_detection_active_changed", update_wakeword_detection_active)
        self.server.register_event("memory_data", self.set_memory_data)

        self.set_ui_state(True)
        self.set_microphone_button_state()
        self.set_wakeword_button_state()

    def set_microphone_button_state(self):
        if self.microphone_recording:
            self.mic_button.set_button_state(2)
        elif self.microphone_recording_allowed:
            self.mic_button.set_button_state(1)
        else:
            self.mic_button.set_button_state()

    def set_wakeword_button_state(self):
        if self.wakeword_detection_active:
            self.wake_word_button.set_button_state(1)
        else:
            self.wake_word_button.set_button_state()

    def mic_clicked(self):
        self.server.set_event("microphone_recording_allowed", not self.microphone_recording_allowed)
       
    def wake_word_clicked(self):
        self.server.set_event("wakeword_detection_active", not self.wakeword_detection_active)
       
    def set_close_notify_method(self, func) -> None:
        self.close_notify = func

    def set_memory_data(self, memory_data):
        if not str(memory_data) == self.memory_data_string:

            self.memory_data = memory_data
            self.memory_data_string = str(memory_data)
            self.memory_data_changed = True

    def update_bool(self, current_value, new_value):
        if current_value != new_value:
            current_value = new_value
        return current_value        

    def add_label(self, text: str, text_color="#F0F0F0", text_backgroundcolor="#101010", font_size=17, align_right=False) -> None:
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
        bubble = ClickableLabel(self.linkify(label["text"]))
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bubble.setTextInteractionFlags(Qt.TextBrowserInteraction)
        bubble.setOpenExternalLinks(True)
        bubble.setWordWrap(True)
        bubble.setStyleSheet(
            "QLabel { background-color: %s; color: %s; border-radius: 3px; padding: 2px; font-size: %dpx; }"  
            % (label["text_backgroundcolor"], label["text_color"], label["font_size"])
        )
        bubble.setAlignment(Qt.AlignRight if label["align_right"] else Qt.AlignLeft)
        self.chat_layout.addWidget(bubble) 


    def launch_ui(self) -> None:
        self.app = QApplication(sys.argv)

        self.player_window = PlayerWidget()
        self.player_window.rowClicked.connect(self.on_row_clicked)


        self.window = CloseableWidget()
        self.window.setWindowTitle('LinguFlex')
        self.window.setGeometry(self.available_width - WINDOW_STARTUP_WIDTH, self.available_height - WINDOW_MAXIMUM_HEIGHT, WINDOW_STARTUP_WIDTH, WINDOW_MAXIMUM_HEIGHT)
        self.window.closeEvent = self.close_event

        self.notebook_title = QComboBox() 
        self.notebook_title.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.notebook_title.setStyleSheet("""
            QComboBox {
                margin: 0px;
                background-color: #222222;
                color: white;
                padding: 4px;
                font-size: 18px;
                border: 0px;
            }
            QComboBox:hover {
                background-color: #333333;
            }
            QComboBox::down-arrow {
                image: url(resources/down_arrow.png);
            }            
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                border: 2px solid darkgray;
                selection-background-color: #333333;
                color: white;
            }
            QComboBox QAbstractItemView::item {
                height: 50px;
                background-color: #333333;
                color: white;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #666666;
            }
        """)
        self.notebook_title.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed) 

        self.notebook_title.currentIndexChanged.connect(self.handle_selection_change)
        self.window.title_layout.insertWidget(0, self.notebook_title, alignment=Qt.AlignBottom)
        
        self.notebook_scroll_area = QScrollArea()
        self.notebook_scroll_area.setWidgetResizable(True)
        self.notebook_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.notebook_scroll_area.setStyleSheet("background-color: #111111; border: 0px;")  
        self.window.layout.addWidget(self.notebook_scroll_area)
        self.notebook_data_widget = QWidget()
        widget_style = """
            QWidget {
                padding: 0px; margin: 0px; border: 0px;
            }
        """
        self.notebook_data_widget.setStyleSheet(widget_style)        
        self.notebook_data_layout = QVBoxLayout()
        self.notebook_data_layout.setContentsMargins(0, 0, 0, 0)
        self.notebook_data_layout.setSpacing(0)        
        self.notebook_data_widget.setLayout(self.notebook_data_layout)
        self.notebook_scroll_area.setWidget(self.notebook_data_widget)
        self.notebook_data_table = QTableWidget()
        self.notebook_data_table.setColumnCount(2)  
        self.notebook_data_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.notebook_data_table.setWordWrap(False)   
        self.notebook_data_table.setColumnWidth(0, 200)
        self.notebook_data_table.setColumnWidth(1, WINDOW_STARTUP_WIDTH)
        self.notebook_data_table.horizontalHeader().setFixedHeight(20)
        self.notebook_data_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.notebook_data_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.notebook_data_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)      
        self.notebook_data_table.setHorizontalHeaderLabels(["📝", "📎"])  
        self.notebook_data_table.verticalHeader().setDefaultSectionSize(25)
        self.notebook_data_table.setShowGrid(False)
        self.notebook_data_table.horizontalHeader().setVisible(False)        
        self.notebook_data_table.verticalHeader().setVisible(False)        

        # Style the headers, rows, and cells
        header_style = "QHeaderView::section { background-color: #222222; color: #D0D0D0; font-size: 18px; padding: 0px; margin: 0px; }"
        cell_style = "QToolTip { color: #E0E0E0; font-size: 20px; background-color: #222222; } QTableWidget { background-color: #222222; color: #D0D0D0; font-size: 18px; padding: 7px; margin: 0px; border: 0px; }"
        corner_button_style = "QTableCornerButton::section { background-color: #222222; }"

        self.notebook_data_table.horizontalHeader().setStyleSheet(header_style)
        self.notebook_data_table.verticalHeader().setStyleSheet(header_style)
        self.notebook_data_table.setStyleSheet(f"{cell_style} {corner_button_style}")
        self.notebook_data_layout.addWidget(self.notebook_data_table)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #111111; border: 0px; margin-top: 10px;")  

        self.scroll_area.verticalScrollBar().rangeChanged.connect(self.resize_scroll)

        self.window.layout.addWidget(self.scroll_area)

        self.chat_area = QWidget()
        widget_style = """
            QWidget {
                padding: 0px; margin: 0px; 
            }
        """

        self.chat_area.setStyleSheet(widget_style)  
        self.chat_area.setMaximumWidth(WINDOW_STARTUP_WIDTH - 42)
        self.chat_layout = QVBoxLayout()
        self.chat_layout.addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))  
        self.chat_area.setLayout(self.chat_layout)

        self.scroll_area.setWidget(self.chat_area)

        self.footer_layout = QHBoxLayout() 
        self.footer_layout.setSpacing(5)

        self.text_input = ReturnAcceptTextEdit()
        self.text_input.setPlaceholderText("🖋️")
        self.text_input.setFixedHeight(66) 
        self.text_input.setStyleSheet("""
            QTextEdit {
                margin-top: 2px;
                padding: 2px;
                font-size: 20px;
                background-color: #1A1A1A;
                color: white;
            }
            QTextEdit:hover {
                background-color: #2A2A2A;
            }
        """) 
        self.text_input.returnPressed.connect(self.user_message)

        self.wake_word_button = BaseButton('👂') 
        self.wake_word_button.setFixedWidth(58)  
        self.wake_word_button.setFixedHeight(58)  
        self.wake_word_button.clicked.connect(self.wake_word_clicked)


        self.mic_button = BaseButton('🎤') 
        self.mic_button.setFixedWidth(58) 
        self.mic_button.setFixedHeight(58)  
        self.mic_button.clicked.connect(self.mic_clicked)
        self.footer_layout.addWidget(self.text_input)
        self.footer_layout.addWidget(self.wake_word_button)
        self.footer_layout.addWidget(self.mic_button)
        self.window.layout.addLayout(self.footer_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.perform_update)
        self.timer.start(500)
        self.show_window = True
        self.set_ui_state(False)
        self.mic_button.set_button_state()
        self.wake_word_button.set_button_state()        
        sys.exit(self.app.exec_())

    def set_ui_state(self, enabled):
        self.notebook_title.setDisabled(not enabled)
        self.text_input.setDisabled(not enabled)
        self.mic_button.setDisabled(not enabled)
        self.wake_word_button.setDisabled(not enabled)
        self.player_window.back_button.setDisabled(not enabled)
        self.player_window.forward_button.setDisabled(not enabled)
        self.player_window.pause_button.setDisabled(not enabled)
        self.player_window.stop_button.setDisabled(not enabled)
        self.player_window.volume_down_button.setDisabled(not enabled)
        self.player_window.volume_up_button.setDisabled(not enabled)
        self.player_window.playlist.setDisabled(not enabled)        

    def on_row_clicked(self, row):
        self.server.set_event("playlist_index", row)

    def update_dropdown_items(self, items):
        self.handle_selection_change_allowed = False
        self.notebook_title.clear()
        self.notebook_title.addItems(items)
        self.notebook_title.setCurrentText(self.memory_data["category"])
        self.handle_selection_change_allowed = True            

    def handle_selection_change(self, index):
        if self.handle_selection_change_allowed:
            self.server.set_event("memory_category_changed", self.notebook_title.currentText())

    def user_message(self):
        print ("CALLED")
        text = self.text_input.toPlainText()

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

    def hide_player_window(self):
        if self.player_window_visible:
            self.player_window_visible = False
            self.player_window.hide()

    def show_player_window(self):
        if not self.player_window_visible:
            self.player_window_visible = True
            geometry = self.window.geometry()
            self.player_window.setGeometry(geometry.x(), geometry.y() - 300, geometry.width(), 300)
            self.player_window.show()

    def perform_update(self) -> None:
        if not self.window.isVisible() and self.show_window:
            self.window.show()
        elif self.window.isVisible() and not self.show_window:
            self.window.hide()
        self.app.blockSignals(True)  
        self.timer.setInterval(100)            
        while len(self.add_labels) > 0:
            current_label = self.add_labels.pop(0)
            self.add_chat_bubble(current_label)
        if self.bring_to_top_request:
            self.perform_bring_to_top()
            self.bring_to_top_request = False
        self.app.blockSignals(False)  
        if not self.is_running:
            self.player_window.close()
            self.timer.stop()
            self.window.close()
            self.timer_finished = True

        if self.memory_data_changed:
            self.memory_data_changed = False
            self.update_dropdown_items(self.memory_data["categories"])
            category = self.memory_data["category"]
            entries_in_category = self.memory_data["list_of_information"]
            self.notebook_data_table.setRowCount(0)

            for pos, entry in enumerate(entries_in_category):
                self.notebook_data_table.insertRow(pos)
                title_item = QTableWidgetItem(entry["content"])
                title_item.setTextAlignment(Qt.AlignLeft | Qt.AlignBottom)
                self.notebook_data_table.setItem(pos, 0, title_item)

                entry_data = ""
                if not entry["data"] is None: 
                    entry_data = str(entry["data"])[:130]

                data_item = QTableWidgetItem(entry_data)
                data_item.setTextAlignment(Qt.AlignLeft | Qt.AlignBottom)
                self.notebook_data_table.setItem(pos, 1, data_item)

            for row in range(self.notebook_data_table.rowCount()):
                content = entries_in_category[row]["content"]
                data = str(entries_in_category[row]["data"])[:2000]

                # Insert a line break every 100 characters
                data_with_line_breaks = "\n".join([data[i:i + 100] for i in range(0, len(data), 100)])

                for column in range(self.notebook_data_table.columnCount()):
                    item = self.notebook_data_table.item(row, column)
                    tooltip_text = f"📝\n{content}\n\n📎\n{data_with_line_breaks}"
                    item.setToolTip(tooltip_text)
                    item.setFlags(item.flags() | Qt.ItemIsEnabled)

        if self.trigger_display_update:
            self.trigger_display_update = False

            if not self.audio_information is None and self.audio_information["playing"]:
                self.show_player_window()
            self.player_window.display(self.audio_information)

            self.set_microphone_button_state()
            self.set_wakeword_button_state()

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