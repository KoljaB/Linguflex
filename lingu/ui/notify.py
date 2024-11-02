from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import (
    QObject, Qt, QTimer, pyqtSignal, pyqtSlot, QEvent
)
from PyQt6 import QtGui
from qfluentwidgets import (
    InfoBar,
    setTheme,
    Theme,
    InfoBarPosition,
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont
from PyQt6.QtCore import QSize
import time

timer = None

class NotifyWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.info = None
        self.to_destroy = None
        self.timer = QTimer(self)
        self.last_move = 0
        self.is_displayed = False
        setTheme(Theme.DARK)

    def create_icon_from_emoji(self, emoji, size=64):
        """
        Create a QIcon from a Unicode emoji character.

        Args:
        emoji (str): The emoji character.
        size (int, optional): The size of the icon. Defaults to 64.

        Returns:
        QIcon: The created QIcon object.
        """
        # Create a QPixmap with specified size
        pixmap = QPixmap(QSize(size, size))

        # Fill with a transparent background
        pixmap.fill(QtGui.QColor("transparent"))

        # Create QPainter to draw on QPixmap
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Set font and size
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(size - 10)  # Adjust size to fit in the pixmap
        painter.setFont(font)

        # Draw the emoji on the pixmap
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)

        # End painting
        painter.end()

        # Create and return QIcon from pixmap
        return QIcon(pixmap)

    def notify(
            self,
            title: str = "",
            text: str = "",
            duration: int = 5000,
            type: str = "warn",
            icon: str = "",
            color: str = "",
    ):
        self.running_info = True
        self.to_destroy = None
        self.last_move = 0
        self.updated = False
        self.is_displayed = False

        if self.info is not None:
            self.to_destroy = self.info
            self.close()

        if icon:
            qicon = self.create_icon_from_emoji(icon)

        if type == "warn":
            self.info = InfoBar.warning(
                title=title,
                content=text,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=-1,
                parent=self
            )
        elif type == "error":
            self.info = InfoBar.error(
                title=title,
                content=text,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=-1,
                parent=self
            )
        elif type == "success":
            self.info = InfoBar.success(
                title=title,
                content=text,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=-1,
                parent=self
            )
        elif type == "info":
            self.info = InfoBar.info(
                title=title,
                content=text,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=-1,
                parent=self
            )
        else:
            self.info = InfoBar.new(
                icon=qicon,
                title=title,
                content=text,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=-1,
                parent=self
            )

        if icon:
            self.info.iconWidget.icon = qicon

        if color:
            self.info.setCustomBackgroundColor(
                QtGui.QColor(color),
                QtGui.QColor(color))

        self.info.destroyed.connect(self.on_info_destroyed)

        self.info.installEventFilter(self)
        self.timer.stop()

        if duration > 0:
            self.timer.singleShot(duration, self.hide_info)

        self.infoBarVisibilityTimer = QTimer(self)
        self.infoBarVisibilityTimer.timeout.connect(
            self.checkInfoBarVisibility
        )
        self.infoBarVisibilityTimer.start(50)

    def checkInfoBarVisibility(self):
        if not self.last_move:
            return

        last_move = time.time() - self.last_move
        if last_move > 0.1:
            self.is_displayed = True
            self.infoBarVisibilityTimer.stop()

    def eventFilter(self, obj, event):

        if obj == self.info and event.type() == QEvent.Type.UpdateLater:
            self.updated = True

        if (self.updated
            and obj == self.info
                and event.type() == QEvent.Type.Move):

            self.last_move = time.time()

        return super().eventFilter(obj, event)

    def on_info_destroyed(self, obj):
        """
        Slot to handle the destruction of the info widget.

        Parameters:
        obj (QObject): The destroyed object.
        """
        if self.to_destroy:
            self.to_destroy = None
        elif self.info:
            self.info = None

    def close(self):
        """
        Closes the info window if it exists and is not already destroyed.
        """
        if self.info:
            self.info.close()
        self.info = None

    def hide_info(self):
        if self.info and self.info.isVisible():
            self.info.opacityAni.setDuration(200)
            self.info.opacityAni.setStartValue(1)
            self.info.opacityAni.setEndValue(0)
            self.info.opacityAni.finished.connect(self.close)
            self.info.opacityAni.start()
            return


class NotifyManager(QObject):

    show_signal = pyqtSignal(str, str, int, str, str, str)
    hide_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.create_window()
        self.show_signal.connect(self.show_info)
        self.hide_signal.connect(self.hide_info)

    def request_show_info(self, title, text, duration, type, icon, color):
        self.show_signal.emit(title, text, duration, type, icon, color)

    def request_hide_info(self):
        self.hide_signal.emit()

    @pyqtSlot(str, str, int, str, str, str)
    def show_info(
            self,
            title: str = "",
            text: str = "",
            duration: int = 5000,
            type: str = "warn",
            icon: str = "",
            color: str = "",
    ):
        self.window.show()
        self.window.notify(title, text, duration, type, icon, color)

    @pyqtSlot()
    def hide_info(self):
        self.window.hide_info()

    def create_window(self):
        self.window = NotifyWindow()
        self.window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        window_width = 800
        self.window.setFixedWidth(window_width)
        self.window.setFixedHeight(200)

        self.screen = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        self.window.move(int(self.screen.width() / 2 - window_width / 2), 0)
        self.window.raise_()

    def notification_visible(self):
        return self.window.is_displayed


notify_manager = None


def notify(
        title: str = "",
        text: str = "",
        duration: int = 5000,
        type: str = "custom",
        icon: str = "",
        color: str = "",
):
    global notify_manager
    if not notify_manager:
        notify_manager = NotifyManager()
    notify_manager.request_show_info(title, text, duration, type, icon, color)


def wait_notify(callback=None, interval=50):
    global timer
    """
    Wait for the notification to become visible using a non-blocking approach.

    Parameters:
    - callback: function to call when the notification is visible
    - interval: polling interval in milliseconds
    """

    if callback:
        def check_and_proceed():
            global notify_manager
            if notify_manager.notification_visible():
                timer.stop()  # Stop the timer if the condition is met
                callback()    # Call the callback function
            else:
                pass

        timer = QTimer()

        # Connect the timeout signal to the check function
        timer.timeout.connect(check_and_proceed)
        timer.start(interval)  # Start the timer with the specified interval

    else:
        
        while not notify_manager.notification_visible():
            QApplication.processEvents()  # Process any pending UI events
            time.sleep(0.02)  # Sleep for 20 milliseconds


def denotify():
    global notify_manager
    notify_manager.request_hide_info()
