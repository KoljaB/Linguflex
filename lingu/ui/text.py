from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QFontMetrics
from PyQt6.QtCore import Qt, QRect, QTimer
from functools import partial


class TextConfig:
    """
    Configuration class for TextWidget settings.
    """
    FONT_TYPE = "Arial"
    FONT_SIZE = 12
    PADDING = 5
    BACKGROUND_OPACITY = 176
    DISTANCE_TOP = 80
    DISTANCE_RIGHT = 50


class Text(QWidget):
    """
    A widget to display a text in a frameless window
    with a semi-transparent background.

    Attributes:
        text (str): The text to be displayed.
        color (QColor): The color of the text.
        width (int): The width of the widget.
    """

    def __init__(self, text: str, color: QColor, width: int, x: int, y: int):
        """
        Initializes the TextWidget with text, color, width, and position.

        Args:
            text (str): The text to display.
            color (QColor): The color of the text.
            width (int): The width of the widget.
            x (int): The x-coordinate of the widget.
            y (int): The y-coordinate of the widget.
        """
        super().__init__()
        self.text = text
        self.color = color
        self.maxWidth = width
        self.origX = x
        self.initUI(x, y)
        if not text:
            self.hide()

    def setText(self, text: str):
        """
        Sets the text of the widget quickly, deferring the update of
        the widget's geometry.

        Args:
            text (str): The new text to display.
        """
        self.text = text

        # Deferring is important here to return control to caller asap
        QTimer.singleShot(0, self.updateGeometry)

    def calculateHeight(self) -> int:
        """
        Calculates the height of the widget
        based on the current text and width.

        Returns:
            The height of the widget.
        """
        font = QFont(TextConfig.FONT_TYPE, TextConfig.FONT_SIZE)
        fm = QFontMetrics(font)

        rect = fm.boundingRect(
            QRect(0, 0, self.maxWidth - 2 * TextConfig.PADDING, 1000),
            Qt.TextFlag.TextWordWrap, self.text)

        return rect.height() + 2 * TextConfig.PADDING

    def calculateWidth(self) -> int:
        """
        Calculates the width of the widget based on the current text,
        with a maximum limit.

        Returns:
            The calculated or maximum width of the widget.
        """
        font = QFont(TextConfig.FONT_TYPE, TextConfig.FONT_SIZE)
        fm = QFontMetrics(font)
        textWidth = fm.horizontalAdvance(self.text) \
            + 2 * TextConfig.PADDING

        return min(textWidth, self.maxWidth)

    def initUI(self, x: int, y: int):
        """
        Sets up the UI of the widget, including its geometry and appearance.

        Args:
            x (int): The x-coordinate of the widget.
            y (int): The y-coordinate of the widget.
        """
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool)
        self.updateGeometry(y)
        self.show()

    def paintEvent(self, event):
        """
        Handles the painting event, drawing the text in the widget.

        Args:
            event: The event triggering the paint.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set the semi-transparent background
        painter.fillRect(
            event.rect(),
            QColor(0, 0, 0, TextConfig.BACKGROUND_OPACITY))

        # Draw the text
        painter.setPen(self.color)

        font = QFont(
            TextConfig.FONT_TYPE,
            TextConfig.FONT_SIZE)
        painter.setFont(font)

        textRect = QRect(
            TextConfig.PADDING,
            TextConfig.PADDING,
            self.width() - 2 * TextConfig.PADDING,
            event.rect().height() - 2 * TextConfig.PADDING)
        painter.drawText(
            textRect,
            Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignRight,
            self.text)

    def updateGeometry(self, y: int = None):
        """
        Updates the geometry of the widget based on the current text and width.
        """
        # print(f"updateGeometry y param: {y}")
        if y is None:
            y = self.y()
        # print(f"updateGeometry new y: {y}")
        shifted_x = self.origX - self.calculateWidth()
        self.setGeometry(
            shifted_x,
            y,
            self.calculateWidth(),
            self.calculateHeight())

        self.update()
        self.showNormal()
        self.raise_()

    def set_y(self, y: int):
        """
        Sets the y-coordinate of the widget.

        Args:
            y (int): The y-coordinate of the widget.
        """
        # print(f"set_y: {y}")
        QTimer.singleShot(0, partial(self.updateGeometry, y))
