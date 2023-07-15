import time
import datetime
import os
import importlib
import inspect
import sys

MODULES_PATHS = ['core', 'modules', 'modules/basic', 'modules/full', 'config']
for path in MODULES_PATHS:
    sys.path.insert(0, path)

from pywinauto import win32api # changes thread mode, so need to import here for edge_texttospeech
from core import (log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, 
                  DEBUG_LEVEL_ERR, debug_level, set_external_method, get_elapsed_time, 
                  Config, items, BaseModule, InputModule, SpeechRecognitionModule, TextToSpeechModule, 
                  TextGeneratorModule, ActionModule, Request, LinguFlexServer)
from linguflex_functions import LinguFlexBase

LOGFILE_DIR = "sessionlog"
SLEEP_TIME = 0.01

class LinguFlex:
    def __init__(self):
        self.last_timestamp = None
        self.openai_function_call_module = importlib.import_module("linguflex_functions")
        self.all_modules = {}
        self.module_instances = []
        self.basic_modules = {
            LinguFlexBase : {}
        }
        self.special_modules = {
            InputModule: {},
            SpeechRecognitionModule: {},
            TextToSpeechModule: {},
            TextGeneratorModule: {},
            ActionModule: {},
        }

        if not os.path.exists(LOGFILE_DIR):
            os.mkdir(LOGFILE_DIR)
        now = datetime.datetime.now()
        self.logfile_name = f"{LOGFILE_DIR}/linguflex_sessionlog-{now.strftime('%y%m%d-%H%M%S')}.txt"

        set_external_method(self.log_to_file_and_inform_modules)

        log(DEBUG_LEVEL_MIN, 'lingu hello')
        log(DEBUG_LEVEL_MAX, f'  Logging debug level is {debug_level}')
        log(DEBUG_LEVEL_MAX, f"  Configuration file: {Config().config_file_path}")

        self.import_modules()
        self.server = LinguFlexServer(self.openai_function_call_module, self.all_modules, self.special_modules)
        self.init_modules()
        
        log(DEBUG_LEVEL_MIN, "")
        log(DEBUG_LEVEL_MIN, "lingu ready")

    def log_to_file_and_inform_modules(self, dbg_lvl: int, text: str, lf=True) -> None:
        for module_instance in self.all_modules.values():
            if callable(getattr(module_instance, "log", None)):
                module_instance.log(dbg_lvl, text)

        current_timestamp = get_elapsed_time()
        timestamp_to_print = (
            " " * len(current_timestamp) if self.last_timestamp == current_timestamp else current_timestamp
        )
        self.last_timestamp = current_timestamp
        with open(self.logfile_name, "a+", encoding="utf-8") as f:
            f.write(f"{timestamp_to_print}| {text}")
            if lf:
                f.write("\n")

    def import_modules(self):
        for module_path, _ in items()('modules'):
            log(DEBUG_LEVEL_MIN, f'Importing {module_path}')
            try:
                module = importlib.import_module(module_path)
                self.process_module_classes(module, module_path)
            except Exception as e:
                log(DEBUG_LEVEL_ERR, f'Linguflex stopped, unhandled exception occured importing module {module_path}: {str(e)}')
                self.handle_exception(e)

    def is_interface_name(self, name):
        for interface in self.special_modules:
            if interface.__name__ == name:
                return True
        return False

    def process_module_classes(self, module, module_path):
        self.module_instances.append(module)
        for name, obj in inspect.getmembers(module):
            for interface, container in self.basic_modules.items():
                if not name == interface.__name__  and inspect.isclass(obj) and issubclass(obj, interface):
                    log(DEBUG_LEVEL_MAX, f'  ├── · class {obj.__name__} imported')
                    obj.register(obj, module_path)
                    container[module_path] = obj
                    break
            else:
                for interface, container in self.special_modules.items():
                    if not name == interface.__name__  and inspect.isclass(obj) and issubclass(obj, interface):
                        log(DEBUG_LEVEL_MAX, f'  ├── {obj.__name__} ({interface.__name__}) imported')
                        self.all_modules[module_path] = container[module_path] = obj()
                        break
                else:
                    if not self.is_interface_name(name) and not name == "BaseModule" and inspect.isclass(obj) and issubclass(obj, BaseModule):
                        log(DEBUG_LEVEL_MAX, f'  ├── {obj.__name__} imported')
                        self.all_modules[module_path] = obj()       

        log_message = f'  {module_path} import complete'
        log(DEBUG_LEVEL_MAX, log_message)

    def init_modules(self):
        for module in self.module_instances:
            module.__dict__['server'] = self.server

        for module_name, module_instance in self.all_modules.items():
            module_instance.server = self.server
            module_instance.name = module_name
            module_instance.init()

    def handle_exception(self, exception):
        import traceback
        tb_str = traceback.format_exc()
        log(DEBUG_LEVEL_MIN, f'Traceback:')
        log(DEBUG_LEVEL_MIN, f'  {tb_str}')
        raise(exception)

    def run(self):
        is_running = True
        request = Request()

        try:
            while is_running:
                self.server.cycle(request)
                request = self.server.process_request(request)
                if self.server.shutdown_request():
                    is_running = False
                if request.input is None:
                    time.sleep(SLEEP_TIME)

            log(DEBUG_LEVEL_MIN, 'Linguflex stopped')
            self.server.shutdown()
        except KeyboardInterrupt:
            log(DEBUG_LEVEL_MIN, 'Linguflex stopped by user keyboard command')
            self.server.shutdown()
        except Exception as e:
            log(DEBUG_LEVEL_ERR, f'Linguflex stopped, unhandled exception occured: {str(e)}')
            self.handle_exception(e)

if __name__ == "__main__":
    lingu_flex = LinguFlex()
    lingu_flex.run()