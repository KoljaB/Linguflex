import time
import datetime
import os
import importlib
import inspect
import sys

sys.path.insert(0, 'modules')
sys.path.insert(0, 'modules/basic')
sys.path.insert(0, 'modules/full')
sys.path.insert(0, 'core')

openai_function_call_module = importlib.import_module("linguflex_functions")

from core import (
    log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR, debug_level, set_external_method, get_elapsed_time,
    items,
    BaseModule, InputModule, SpeechRecognitionModule, TextToSpeechModule, TextGeneratorModule, ActionModule,
    Request,
    LinguFlexServer)

# log(DEBUG_LEVEL_MIN, 'Eins, zwei, drei, vier, fünf, sechs, sieben, acht, neun, zehn, elf, zwölf, dreizehn, vierzehn, fünfzehn, sechzehn, siebzehn, achtzehn, neunzehn, zwanzig, einundzwanzig, zweiundzwanzig, dreiundzwanzig, vierundzwanzig, fünfundzwanzig, sechsundzwanzig, siebenundzwanzig, achtundzwanzig, neunundzwanzig, dreißig, einunddreißig, zweiunddreißig, dreiunddreißig, vierunddreißig, fünfunddreißig, sechsunddreißig, siebenunddreißig, achtunddreißig, neununddreißig, vierzig, einundvierzig, zweiundvierzig, dreiundvierzig, vierundvierzig, fünfundvierzig, sechsundvierzig, siebenundvierzig, achtundvierzig, neunundvierzig, fünfzig, einundfünfzig, zweiundfünfzig, dreiundfünfzig, vierundfünfzig, fünfundfünfzig, sechsundfünfzig, siebenundfünfzig, achtundfünfzig, neunundfünfzig, sechzig, einundsechzig, zweiundsechzig, dreiundsechzig, vierundsechzig, fünfundsechzig, sechsundsechzig, siebenundsechzig, achtundsechzig, neunundsechzig, siebzig, einundsiebzig, zweiundsiebzig, dreiundsiebzig, vierundsiebzig, fünfundsiebzig, sechsundsiebzig, siebenundsiebzig, achtundsiebzig, neunundsiebzig, achtzig, einundachtzig, zweiundachtzig, dreiundachtzig, vierundachtzig, fünfundachtzig, sechsundachtzig, siebenundachtzig, achtundachtzig, neunundachtzig, neunzig, einundneunzig, zweiundneunzig, dreiundneunzig, vierundneunzig, fünfundneunzig, sechsundneunzig, siebenundneunzig, achtundneunzig, neunundneunzig, hundert.')
# log(DEBUG_LEVEL_MIN, '')
# log(DEBUG_LEVEL_MIN, 'Test Line Break:')
# log(DEBUG_LEVEL_MIN, 'Direct next line')
# log(DEBUG_LEVEL_MIN, 'Some line break in between \none sentence')
# log(DEBUG_LEVEL_MIN, 'Next line')
# exit(0)

from linguflex_functions import linguflex_function, LinguFlexBase

# Constants
LINGU_FS_SLEEP_MAINCYCLE = 0.01 # don't raise too much or mic recording will fail

# Dictionaries to store module instances
all_modules = {}
function_modules = {
    LinguFlexBase : {}
}
special_modules = {
    InputModule: {},
    SpeechRecognitionModule: {},
    TextToSpeechModule: {},
    TextGeneratorModule: {},
    ActionModule: {},
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





log(DEBUG_LEVEL_MIN, 'lingu hello')
log(DEBUG_LEVEL_MAX, f'  logging debuglevel is {debug_level}')



# Load modules

def is_interface_name(name) -> bool:
    for interface in special_modules:
        if interface.__name__ == name:
            return True
    return False

# import json

# openai_function_call_module = importlib.import_module("openai_function_call")

modules = []
for module_path, _ in items()('modules'):
    log(DEBUG_LEVEL_MIN, f'importing {module_path}')

    try:
        module = importlib.import_module(module_path)
        # log(DEBUG_LEVEL_MAX, f'  importing finished')
        modules.append(module)
    except Exception as e:
        log(DEBUG_LEVEL_ERR, f'{module_path} {str(e)}')
        raise(e)

    # print (f'functions: {openai_function_call_module.functions}')
    # print (f'classes: {openai_function_call_module.classes}')

    module_function = None
    for name, obj in inspect.getmembers(module):
        for interface, container in function_modules.items():
            if not name == interface.__name__  and inspect.isclass(obj) and issubclass(obj, interface):
                log(DEBUG_LEVEL_MAX, f'  ├── · class {obj.__name__} imported')
                #log(DEBUG_LEVEL_MAX, f'  imported function {obj.__name__}')
                obj.register(obj, module_path)
                container[module_path] = obj
                module_function = interface.__name__
                break
        else:
            for interface, container in special_modules.items():
                if not name == interface.__name__  and inspect.isclass(obj) and issubclass(obj, interface):
                    log(DEBUG_LEVEL_MAX, f'  ├── {obj.__name__} ({interface.__name__}) imported')
                    #log(DEBUG_LEVEL_MAX, f'  interface module object {obj.__name__} of {module_path} created for interface {interface.__name__}')

                    all_modules[module_path] = container[module_path] = obj()
                    module_function = interface.__name__
                    module_function = module_function.replace('BaseModule', '')
                    #all_modules[module_path].module_name = module_path
                    break
            else:
                if not is_interface_name(name) and not name == "BaseModule" and inspect.isclass(obj) and issubclass(obj, BaseModule):
                    log(DEBUG_LEVEL_MAX, f'  ├── {obj.__name__} imported')
                    all_modules[module_path] = obj()
    log_message = f'  {module_path} import complete'
    #if not module_function is None: log_message += f' ({module_function})'
    log(DEBUG_LEVEL_MAX, log_message)




# # Convert to pretty printed JSON string
# pretty_json = json.dumps(openai_function_call_module.openai_function_schemas, indent=4)

# # Drucken Sie die Liste "openai_functions"
# print(pretty_json)


#  for module in modules:
#      if hasattr(module, 'openai_function_schemas'):
#          pretty_json = json.dumps(module.openai_function_schemas, indent=4)
#          print(pretty_json)
# # Convert to pretty printed JSON string


# # Drucken Sie die Liste "openai_functions"
# 





# Launch server
server = LinguFlexServer(openai_function_call_module, all_modules, special_modules)
log(DEBUG_LEVEL_MIN, "")
log(DEBUG_LEVEL_MIN, "lingu ready")

for module in modules:
    module.__dict__['server'] = server

for module_instance in all_modules.values():
    module_instance.server = server

def main():
    try:
        is_running = True
        request = Request()

        while is_running:
            # Process modules' main cycle method
            server.cycle(request)

            # Handle input creation, processing, and output generation
            request = server.process_request(request)

            # Check for shutdown request
            if server.shutdown_request():
                is_running = False

            # Sleep to reduce CPU usage when there's no input
            if request.input is None:
                time.sleep(LINGU_FS_SLEEP_MAINCYCLE)

        log(DEBUG_LEVEL_MIN, 'Linguflex stopped')

        server.shutdown()            

    except KeyboardInterrupt:

        log(DEBUG_LEVEL_MIN, 'Linguflex stopped by user keyboard command')

        server.shutdown()

    except Exception as e:

        # Catch all exceptions
        log(DEBUG_LEVEL_MIN, f'Linguflex stopped, unhandled exception occured: {str(e)}')

        # If you want to also print the traceback
        import traceback
        traceback.print_exc()

        # Ensure server shutdown
        server.shutdown()            

if __name__ == "__main__":
    main()
