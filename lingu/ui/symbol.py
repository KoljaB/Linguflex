from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QFont, QColor, QPen, QPixmap, QImage
from PyQt6.QtCore import Qt, pyqtSignal
from lingu import events


class SymbolConfig:
    """
    Configuration class for SymbolWidget settings.
    """
    SIZE = 50
    FONT_TYPE = "Arial"
    FONT_SIZE = 30
    DISTANCE_TOP = 40
    DISTANCE_RIGHT = 50
    DISTANCE_BETWEEN_SYMBOLS = 0
    # SYMBOL_OPACITY = 0.7


class Symbol(QWidget):
    """
    A widget to display a single symbol (e.g., emoji) in a frameless window.
    The background color changes to red when the mouse hovers over it.

    Attributes:
        symbol (str): The symbol to be displayed.
    """
    leftClicked = pyqtSignal(object)
    rightClicked = pyqtSignal(object)

    def __init__(self, module, symbol: str, x: int, y: int):
        """
        Initializes the SymbolWidget with a symbol and position.

        Args:
            symbol (str): The symbol (e.g., emoji) to display.
            x (int): The x-coordinate of the widget.
            y (int): The y-coordinate of the widget.
        """
        super().__init__()
        self.module = module
        self.symbol = symbol
        self.is_mouse_over = False
        self.is_active = False
        self.is_disabled = False
        self.state = "not_ready"
        self.initUI(x, y)

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
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool)
        self.setGeometry(
            x,
            y,
            SymbolConfig.SIZE,
            SymbolConfig.SIZE)
        self.show()

    def set_state(self, state: str):
        """
        Sets the state of the symbol and updates the UI.

        Args:
            state (str): The new state to set.
        """
        self.state = state
        self.update()

    def set_active(self, is_active: bool):
        """
        Sets the active state of the symbol and updates the UI.

        Args:
            is_active (bool): The new active state to set.
        """
        self.is_active = is_active
        self.update()

    def set_disabled(self, is_disabled: bool):
        """
        Sets the disabled state of the symbol and updates the UI.

        Args:
            is_active (bool): The new active state to set.
        """
        self.is_disabled = is_disabled
        self.update()

    def paintEvent(self, event):
        """
        Handles the painting event, drawing the symbol and border in the
        widget. Changes background color and adds border based on mouse
        hover state.

        Args:
            event: The event triggering the paint.
        """

        state = self.state
        draw_untinted = True

        if state == "fct_call_start":
            back_color = QColor(255, 255, 0, 40)
            border_color = QColor(255, 255, 0)
            symbol_color = QColor(255, 255, 0)
            symbol_opacity = 0.8
        elif state == "executing":
            back_color = QColor(255, 136, 0, 40)
            border_color = QColor(255, 136, 0)
            symbol_color = QColor(255, 136, 0)
            symbol_opacity = 1.0
        elif state == "unavailable":
            back_color = None
            border_color = None
            symbol_color = QColor(160, 160, 160)
            symbol_opacity = 0.3
        else:
            back_color = None
            border_color = None
            symbol_color = None
            symbol_opacity = 0.7

        if self.is_disabled or state == "not_ready":
            draw_untinted = False
            back_color = None
            border_color = None
            symbol_color = QColor(96, 96, 96)
            symbol_opacity = 0.5

        if self.is_active:
            border_color = QColor(160, 160, 160)
            back_color = QColor(255, 255, 255, 40)
            symbol_color = QColor(255, 0, 0)
            symbol_opacity = 0.7

        if self.is_mouse_over:
            back_color = QColor(0, 0, 0)
            border_color = QColor(192, 192, 192)
            symbol_opacity = 1.0

        # draw background
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if back_color:
            painter.fillRect(event.rect(), back_color)
        else:
            painter.fillRect(event.rect(), QColor(0, 0, 0, 5))
        if border_color:
            # Draw the border
            # painter.setPen(border_color)
            # painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
            # painter.drawRect(1, 1, self.width() - 2, self.height() - 2)

            pen = QPen(border_color, 2)
            pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            painter.setPen(pen)
            adjustedRect = event.rect().adjusted(1, 1, -1, -1)
            painter.drawRect(adjustedRect)

        font = QFont(SymbolConfig.FONT_TYPE, SymbolConfig.FONT_SIZE)

        # Draw untinted symbol onto the widget
        if draw_untinted:
            painter.setOpacity(symbol_opacity)
            painter.setFont(font)
            painter.drawText(
                event.rect(),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
                self.symbol)

        if symbol_color:

            # Create a QPixmap to render the emoji
            pixmap = QPixmap(SymbolConfig.SIZE, SymbolConfig.SIZE)
            pixmap.fill(Qt.GlobalColor.transparent)

            # Render the emoji onto the pixmap
            painter.end()
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.setFont(font)
            painter.drawText(
                pixmap.rect(),
                Qt.AlignmentFlag.AlignCenter,
                self.symbol)
            painter.end()

            # Convert pixmap to QImage for manipulation
            image = pixmap.toImage()

            # Apply tint to symbol pixels
            tinted = self.tint_symbol_pixels(image, symbol_color)

            # Draw the tinted image onto the widget
            painter.begin(self)
            painter.setOpacity(symbol_opacity)
            painter.drawImage(event.rect(), tinted)

        painter.end()

    def tint_symbol_pixels(self, image, color):
        """
        Tint the symbol pixels with the given color.

        Args:
            image (QImage): The image containing the symbol.
            color (QColor): The color to apply to the symbol.

        Returns:
            QImage: The tinted image.
        """
        tinted = QImage(image.size(), QImage.Format.Format_ARGB32)
        tinted.fill(Qt.GlobalColor.transparent)

        for x in range(image.width()):
            for y in range(image.height()):
                pixel = image.pixelColor(x, y)
                # Check if the pixel is part of the symbol
                if pixel.alpha() != 0:
                    # Blend the symbol pixel with the tint color
                    r = (pixel.red() * color.red()) // 255
                    g = (pixel.green() * color.green()) // 255
                    b = (pixel.blue() * color.blue()) // 255
                    tinted.setPixelColor(x, y, QColor(r, g, b, pixel.alpha()))

        return tinted

    def enterEvent(self, event):
        """
        Event handler for when the mouse enters the widget area.
        Sets the is_mouse_over flag to True and updates the widget.

        Args:
            event: The event triggering the mouse enter.
        """
        if self.state == "not_ready":
            return
        events.trigger("symbol_mouse_enter", self.module["name"])
        self.is_mouse_over = True
        self.update()

    def leaveEvent(self, event):
        """
        Event handler for when the mouse leaves the widget area.
        Sets the is_mouse_over flag to False and updates the widget.

        Args:
            event: The event triggering the mouse leave.
        """
        if self.state == "not_ready":
            return
        events.trigger("symbol_mouse_leave", self.module["name"])
        self.is_mouse_over = False
        self.update()

    def mousePressEvent(self, event):
        """
        Event handler for mouse press events.
        Emits the leftClicked or rightClicked signal based
        on the mouse button used.

        Args:
            event: The event triggering the mouse press.
        """
        if self.state == "not_ready":
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftClicked.emit(self)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightClicked.emit(self)
