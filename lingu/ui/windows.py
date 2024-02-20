from lingu import import_repeat_functions
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import Qt

WINDOW_WIDTH = 800


class Windows:

    def create_instance(self, module):
        window = module["ui"]()

        module["ui_instance"] = window
        if module["ui"].logic:
            window.logic = module["ui"].logic
            window.module_name = module["name"]

        import_repeat_functions(module, window)

        window.init()
        window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint)
        window.setFixedWidth(WINDOW_WIDTH)

    def toggle_window(self, module, position: QPoint):
        if "ui" not in module:
            return

        if "ui_instance" not in module:
            self.create_instance(module)
            rb = module["ui_instance"].buttons_width()
            module["ui_instance"].move(
                position.x() - WINDOW_WIDTH + rb,
                position.y())
            module["ui_instance"]._original_pos = module["ui_instance"].pos()

        ui = module["ui_instance"]
        if ui.isVisible():
            if ui.had_focus_recently():
                ui.hide()
            else:
                ui.showNormal()
                ui.raise_()
                ui.activateWindow()
                ui.setFocus()
        else:
            ui.showNormal()
            ui.raise_()
            ui.activateWindow()
            ui.setFocus()
