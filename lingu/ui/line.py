from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen


class Line(QWidget):
    """
    A custom QWidget subclass that organizes child widgets into a line
    with optional spacers.

    Attributes:
        left_left (QHBoxLayout): Layout for the top left section.
        left_right (QHBoxLayout): Layout for the bottom left section.
        right_left (QHBoxLayout): Layout for the top right section.
        right_right (QHBoxLayout): Layout for the bottom right section.
    """

    def __init__(
            self,
            spacer=True,
            align=Qt.AlignmentFlag.AlignTop,
            horizontal=True,
            background_color=None,
            is_header=False,
            spacing=0):
        """
        Initialize the Line widget.

        Args:
            spacer (bool): If True, adds a spacer.
            align (Qt.AlignmentFlag, optional): Alignment of the layout.
            horizontal (bool, optional): If True, the layout is horizontal.
            background_color (str, optional): Background color in CSS format
        """
        super().__init__()
        main_horizontal_layout = QHBoxLayout()

        self.background_color = background_color
        self.border_color = "#B0B0B0"

        self.configure_layout(main_horizontal_layout, align)
        if is_header:
            main_horizontal_layout.setContentsMargins(5, 2, 5, 2)
            main_horizontal_layout.setSpacing(0)
        if spacing:
            main_horizontal_layout.setSpacing(spacing)

        self.left_left = QHBoxLayout() if horizontal else QVBoxLayout()
        self.configure_layout(self.left_left, align)
        self.left_right = QHBoxLayout() if horizontal else QVBoxLayout()
        self.configure_layout(self.left_right, align)
        self.right_left = QHBoxLayout() if horizontal else QVBoxLayout()
        self.configure_layout(self.right_left, align)
        self.right_right = QHBoxLayout() if horizontal else QVBoxLayout()
        self.configure_layout(self.right_right, align)

        main_horizontal_layout.addLayout(self.left_left)
        main_horizontal_layout.addLayout(self.left_right)
        if spacer:
            spacer_item = QSpacerItem(
                40,
                20,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum
            )
            main_horizontal_layout.addSpacerItem(spacer_item)
        main_horizontal_layout.addLayout(self.right_left)
        main_horizontal_layout.addLayout(self.right_right)
        self.setLayout(main_horizontal_layout)

    def add(self, widget, align="leftleft"):
        """
        Add a widget to a specified section of the layout.

        Args:
            widget (QWidget): The widget to add.
            align (str): The section where the widget will be added.
                         Options: 'leftleft', 'leftright', 'rightleft',
                           'rightright', 'right'.
        """
        if align == "leftright":
            self.left_right.addWidget(widget)
        elif align == "rightleft":
            self.right_left.addWidget(widget)
        elif align == "rightright" or align == "right":
            self.right_right.addWidget(widget)
        else:
            self.left_left.addWidget(widget)

    @staticmethod
    def configure_layout(layout: QBoxLayout, align=Qt.AlignmentFlag.AlignTop):
        """
        Configure the layout with the specified alignment.

        Args:
            layout (QBoxLayout): The layout to configure.
            align (Qt.AlignmentFlag): The alignment flag to set.
        """
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(align)

    def paintEvent(self, event):
        """
        Paint event to set the background color of the widget
          and draw a border.
        """
        painter = QPainter(self)
        if self.background_color:
            painter.fillRect(self.rect(), QColor(self.background_color))

            pen = QPen(QColor(self.border_color), 2)
            pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            painter.setPen(pen)
            border_rect = self.rect().adjusted(
                1, 1, -pen.width() + 1, -pen.width())
            painter.drawRect(border_rect)

        super().paintEvent(event)


class SimpleLine(QWidget):
    """
    A custom QWidget subclass that organizes child widgets into a line
    with optional spacers.

    Attributes:
        left_left (QHBoxLayout): Layout for the top left section.
        left_right (QHBoxLayout): Layout for the bottom left section.
        right_left (QHBoxLayout): Layout for the top right section.
        right_right (QHBoxLayout): Layout for the bottom right section.
    """

    def __init__(
            self,
            spacer=True,
            align=Qt.AlignmentFlag.AlignTop):
        """
        Initialize the Line widget.

        Args:
            spacer (bool): If True, adds a spacer between left
              and right sections.
        """
        super().__init__()
        self.main_horizontal_layout = QHBoxLayout()
        if spacer:
            spacer_item = QSpacerItem(
                40,
                20,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum
            )
            self.main_horizontal_layout.addSpacerItem(spacer_item)
        self.configure_layout(self.main_horizontal_layout, align)
        self.setLayout(self.main_horizontal_layout)

    def add(self, widget):
        """
        Add a widget to the layout.

        Args:
            widget (QWidget): The widget to add.
        """
        self.main_horizontal_layout.insertWidget(0, widget)

    @staticmethod
    def configure_layout(layout: QBoxLayout, align=Qt.AlignmentFlag.AlignTop):
        """
        Configure layout with zero spacing and margins.

        Args:
            layout (QHBoxLayout): The layout to configure.
        """
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(align)


class StretchLine(QWidget):
    def __init__(self):
        super().__init__()

        # Create the main horizontal layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # First column with QVBoxLayout
        self.left = QVBoxLayout()
        self.left.setContentsMargins(0, 0, 0, 0)
        self.left.setSpacing(0)
        self.left.addStretch()

        # Second column with QVBoxLayout
        self.right = QVBoxLayout()
        self.right.setContentsMargins(0, 0, 0, 0)
        self.right.setSpacing(0)

        # Create a widget to hold the left layout and set its size policy
        left_widget = QWidget()
        left_widget.setContentsMargins(0, 0, 5, 0)
        left_widget.setLayout(self.left)
        left_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred)

        # Create a widget to hold the right layout and set its size policy
        right_widget = QWidget()
        right_widget.setContentsMargins(5, 0, 0, 0)
        right_widget.setLayout(self.right)

        # Add the columns to the main layout
        main_layout.addWidget(left_widget,
                              alignment=Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(right_widget,
                              alignment=Qt.AlignmentFlag.AlignTop)

        # Set the main layout for the widget
        self.setLayout(main_layout)

    def add(self, widget, align="left", subalign="left"):
        """
        Add a widget to a specified section of the layout.
        Args:
            widget (QWidget): The widget to add.
            align (str): The section where the widget will be added.
                         Options: 'left', 'right'.
        """
        if subalign == "left":
            alignment = Qt.AlignmentFlag.AlignTop
        else:
            alignment = Qt.AlignmentFlag.AlignRight

        if align == "left":
            self.left.addWidget(widget, alignment=alignment)
        else:
            self.right.addWidget(widget, alignment=alignment)


class VSpacer(QWidget):
    """
    A custom QWidget subclass that acts as a vertical spacer,
    with a customizable height.

    Attributes:
        height (int): The height of the spacer in pixels.
    """

    def __init__(self, height=5):
        """
        Initialize the VSpacer widget.

        Args:
            height (int, optional): The height of the spacer in pixels.
                                    Defaults to 10.
        """
        super().__init__()

        # Set the height of the spacer
        self.setFixedHeight(height)

        # Set the size policy to be fixed in the vertical direction
        # and minimum in the horizontal direction.
        self.setSizePolicy(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Fixed
        )
