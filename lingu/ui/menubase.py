from PyQt6.QtWidgets import QMenu


class MenuBase(QMenu):
    def __init__(self, parent=None):
        super(MenuBase, self).__init__(parent)

        self.initStylesheet()

    def initStylesheet(self):
        """Set the default stylesheet for the menu."""
        stylesheet = """
            QMenu {
                background-color: black;
                color: white;
                border-radius: 10px;
            }
            QMenu::item:checked {
                background-color: #333333;
            }
            QMenu::item:selected {
                background-color: #555555;
            }
        """
        self.setStyleSheet(stylesheet)
