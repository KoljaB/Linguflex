import time
import datetime
import os
import importlib
import inspect
import sys

sys.path.insert(0, 'modules')
sys.path.insert(0, 'modules/basic')
sys.path.insert(0, 'modules/full')

from linguflex_log import (
    log,
    DEBUG_LEVEL_OFF,
    DEBUG_LEVEL_MIN,
    DEBUG_LEVEL_MID,
    DEBUG_LEVEL_MAX,
    debug_level,
    set_external_method,
    get_elapsed_time,
)
from linguflex_interfaces import (
    Module_IF,
    InputProviderModule_IF,
    SpeechRecognitionModule_IF,
    TextToSpeechModule_IF,
    LanguageProcessingModule_IF,
    JsonActionProviderModule_IF,
)
from linguflex_config import cfg
from linguflex_message import LinguFlexMessage
from linguflex_server import LinguFlexServer


# Constants
LINGU_FS_SLEEP_MAINCYCLE = 0.01 # don't raise too much or mic recording will fail

# Dictionaries to store module instances
all_modules = {}
special_modules = {
    InputProviderModule_IF: {},
    SpeechRecognitionModule_IF: {},
    TextToSpeechModule_IF: {},
    LanguageProcessingModule_IF: {},
    JsonActionProviderModule_IF: {},
}



# Session logging setup
if not os.path.exists("sessionlog"):
    os.mkdir("sessionlog")
now = datetime.datetime.now()
logfile_name = f"sessionlog/linguflex_sessionlog-{now.strftime('%y%m%d-%H%M%S')}.txt"

last_timestamp = None

def logtofile_and_inform_modules(dbg_lvl: int, text: str, lf=True) -> None:
    global last_timestamp

    # Inform modules of the log message
    for module_instance in all_modules.values():
        if callable(getattr(module_instance, "log", None)):
            module_instance.log(dbg_lvl, text)

    # Log to file with timestamps
    current_timestamp = get_elapsed_time()
    timestamp_to_print = (
        " " * len(current_timestamp) if last_timestamp == current_timestamp else current_timestamp
    )
    last_timestamp = current_timestamp
    with open(logfile_name, "a+", encoding="utf-8") as f:
        f.write(f"{timestamp_to_print}| {text}")
        if lf:
            f.write("\n")

set_external_method(logtofile_and_inform_modules)





log(DEBUG_LEVEL_MIN, "hello lingu")
log(DEBUG_LEVEL_MAX, f"  logging debuglevel is {debug_level}")



# Load modules

def is_interface_name(name) -> bool:
    for interface in special_modules:
        if interface.__name__ == name:
            return True
    return False

for module_path, _ in cfg.items("modules"):
    log(DEBUG_LEVEL_MAX, f'  importing {module_path}')
    module = importlib.import_module(module_path)
    module_function = None
    for name, obj in inspect.getmembers(module):
        for interface, container in special_modules.items():
            if not name == interface.__name__  and inspect.isclass(obj) and issubclass(obj, interface):
                all_modules[module_path] = container[module_path] = obj_instance = obj()
                module_function = interface.__name__
                module_function = module_function.replace('Module_IF', '')
                break
        else:
            if not is_interface_name(name) and not name == "Module_IF" and inspect.isclass(obj) and issubclass(obj, Module_IF):
                all_modules[module_path] = obj()
    log_message = f'{module_path} ready'
    if not module_function is None: log_message += f' ({module_function})'
    log(DEBUG_LEVEL_MIN, log_message)


# Launch server
server = LinguFlexServer(all_modules, special_modules)
log(DEBUG_LEVEL_MIN, "---Server up and ready---")

for module_instance in all_modules.values():
    module_instance.server = server

def main():
    try:
        is_running = True
        message = LinguFlexMessage()

        while is_running:
            # Process modules' main cycle method
            server.cycle(message)

            # Handle input creation, processing, and output generation
            message = server.process_message(message)

            # Check for shutdown request
            if server.shutdown_request():
                is_running = False

            # Sleep to reduce CPU usage when there's no input
            if message.input is None:
                time.sleep(LINGU_FS_SLEEP_MAINCYCLE)

        server.shutdown()            

    except Exception as e:

        # Catch all exceptions
        print(f"An unexpected error occurred while running linguflex: {e}")

        # If you want to also print the traceback
        import traceback
        traceback.print_exc()

        # Ensure server shutdown
        server.shutdown()            

    except KeyboardInterrupt:
        server.shutdown()

if __name__ == "__main__":
    main()
