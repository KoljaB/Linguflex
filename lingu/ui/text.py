from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QFontMetrics
from PyQt6.QtCore import Qt, QRect, QTimer
from functools import partial


class Text(QWidget):
    """
    A widget to display a text in a frameless window
    with a semi-transparent background.

    Attributes:
        text (str): The text to be displayed.
        color (QColor): The color of the text.
        width (int): The width of the widget.
    """

    def __init__(self, text: str, color: QColor, width: int, x: int, y: int,
                 font_type="Arial", font_size=12, padding=5,
                 background_opacity=176, background_color=QColor(0, 0, 0),
                 distance_top=80, distance_right=50):
        """
        Initializes the TextWidget with text, color, width, and position.

        Args:
            text (str): The text to display.
            color (QColor): The color of the text.
            width (int): The width of the widget.
            x (int): The x-coordinate of the widget.
            y (int): The y-coordinate of the widget.
            font_type (str): Font type for the text.
            font_size (int): Font size for the text.
            padding (int): Padding around the text.
            background_opacity (int): Opacity level for the background.
            background_color (QColor): Color for the background.
            distance_top (int): Distance from the top for positioning.
            distance_right (int): Distance from the right for positioning.
        """
        super().__init__()
        self.text = text
        self.color = color
        self.maxWidth = width
        self.origX = x
        self.font_type = font_type
        self.font_size = font_size
        self.padding = padding
        self.background_opacity = background_opacity
        self.background_color = background_color
        self.distance_top = distance_top
        self.distance_right = distance_right
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
        font = QFont(self.font_type, self.font_size)
        fm = QFontMetrics(font)
        rect = fm.boundingRect(QRect(0, 0, self.maxWidth - 2 * self.padding, 1000), Qt.TextFlag.TextWordWrap, self.text)
        return rect.height() + 2 * self.padding

    def calculateWidth(self) -> int:
        """
        Calculates the width of the widget based on the current text,
        with a maximum limit.

        Returns:
            The calculated or maximum width of the widget.
        """
        font = QFont(self.font_type, self.font_size)
        fm = QFontMetrics(font)
        textWidth = fm.horizontalAdvance(self.text) + 2 * self.padding
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
        painter.fillRect(event.rect(), self.background_color)
        opacity_background = QColor(
            self.background_color.red(), self.background_color.green(),
            self.background_color.blue(), self.background_opacity)
        painter.fillRect(event.rect(), opacity_background)
        painter.setPen(self.color)
        font = QFont(self.font_type, self.font_size)

        # Draw the text
        painter.setFont(font)
        textRect = QRect(self.padding, self.padding, self.width() - 2 * self.padding, event.rect().height() - 2 * self.padding)
        painter.drawText(textRect, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignRight, self.text)

    def setVisibility(self, visible: bool):
        """
        Sets the visibility of the widget.

        Args:
            visible (bool): A boolean indicating whether the widget should be visible.
        """
        if visible:
            QTimer.singleShot(0, self.show)
        else:
            QTimer.singleShot(0, self.hide)

    def updateGeometry(self, y: int = None):
        """
        Updates the geometry of the widget based on the current text and width.
        """
        if y is None:
            y = self.y()
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
        QTimer.singleShot(0, partial(self.updateGeometry, y))
