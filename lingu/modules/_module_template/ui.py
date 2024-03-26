from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QStackedWidget,
    QSizePolicy
)
from qfluentwidgets import (
    InfoBadge,
    InfoLevel,
    setTheme,
    Theme,
    TextEdit,
    SegmentedWidget
)
from lingu import UI, Line, StretchLine
from PyQt6.QtCore import Qt, QUrl, pyqtSlot
from PyQt6.QtGui import QDesktopServices


class MailUI(UI):
    def __init__(self):
        super().__init__()

        setTheme(Theme.DARK)

        label = UI.headerlabel("🐫 Camel facts")
        self.header(label, nostyle=True)
