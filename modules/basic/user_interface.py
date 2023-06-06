import sys
sys.path.insert(0, '..')

from linguflex_interfaces import Module_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_message import LinguFlexMessage
from user_interface_helper import UI_Window

class UIModule(Module_IF):   
    def __init__(self) -> None:
        self.ui = UI_Window()
        self.started = False
        self.is_running = True
        self.ui.set_close_notify_method(self.close_notify)

    def close_notify(self) -> None:
        self.is_running = False

    def log(self, 
            dbg_lvl: int, 
            text: str) -> None:
        if DEBUG_LEVEL_MIN >= dbg_lvl and not self.started:
            self.ui.startup(text)
        elif DEBUG_LEVEL_OFF >= dbg_lvl:
            self.ui.system(text)        

    def handle_input(self, 
            message: LinguFlexMessage) -> None: 
        if not message.skip_input:
            self.ui.user(message.input)

    def handle_output(self, 
            message: LinguFlexMessage) -> None: 
        if not message.skip_output:
            self.ui.assistant(message.output_user)

    def shutdown_request(self) -> None:
        return not self.is_running

    def shutdown(self) -> None:
        if self.is_running: 
            self.ui.close()

    def cycle(self, 
            message: LinguFlexMessage) -> None: 
        if not self.started:
            self.ui.startup_ready('system ready')
        self.started = True