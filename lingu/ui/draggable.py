from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt


class DraggableWidget(QWidget):
    """
    A base class for draggable widgets in PyQt6.
    This class implements the necessary mouse event handlers
    to make a QWidget draggable and return to its original
    position on a double-click.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_start_pos = None
        self._original_pos = self.pos()  # Store the original position

    def mousePressEvent(self, event):
        """
        Overrides the mouse press event to initiate dragging.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.globalPosition().toPoint()
            self.raise_()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        Overrides the mouse move event to handle dragging.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if (event.buttons() & Qt.MouseButton.LeftButton
                and self._drag_start_pos is not None):

            current_pos = event.globalPosition().toPoint()
            delta = current_pos - self._drag_start_pos
            self.move(self.pos() + delta)
            self._drag_start_pos = current_pos
            event.accept()

    def mouseReleaseEvent(self, event):
        """
        Overrides the mouse release event to finalize dragging.

        Args:
            event (QMouseEvent): The mouse event.
        """
        self._drag_start_pos = None
        event.accept()

    def mouseDoubleClickEvent(self, event):
        """
        Overrides the mouse double-click event to reset the widget's position.

        Args:
            event (QMouseEvent): The mouse event.
        """
        self.move(self._original_pos)  # Reset position to the original
        event.accept()
