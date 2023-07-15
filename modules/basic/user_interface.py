from core import InputModule, Request, log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX

from user_interface_helper import UIWindow

class UserInterfaceModule(InputModule):   
    def init(self) -> None: 
        self.ui.set_server(self.server)

    def __init__(self) -> None:
        self.ui = UIWindow()
        self.started = False
        self.is_running = True
        self.ui.set_close_notify_method(self.close_notify)

    def user_text(self, text) -> None:
        self.ui.add_label(text, text_color="#FFFFFF", text_backgroundcolor="#222222", align_right=True)

    def answer_text(self, text) -> None:
        self.ui.add_label(text, font_size=19)

    def close_notify(self) -> None:
        self.is_running = False

    def handle_input(self, 
            request: Request) -> None: 
        skip_input = hasattr(request, 'skip_input') and request.skip_input
        if not skip_input:
            self.user_text(request.input)

    def handle_output(self, 
            request: Request) -> None: 
        # if not request.skip_output:
        self.answer_text(request.output)

    def shutdown_request(self) -> None:
        return not self.is_running

    def shutdown(self) -> None:
        if self.is_running: 
            self.ui.close()

    def create_text_input(self,
            request: Request) -> None: 
        potential_input = self.ui.user_input.strip()
        if potential_input:
            request.input = potential_input
            self.ui.user_input = ''