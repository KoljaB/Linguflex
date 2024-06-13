from .repeat import import_repeat_functions
from .inference import InferenceManager
from .populatable import Populatable
from .invokable import Invokable
from .settings import cfg
from .state import State
from .logic import Logic
from .log import log
from .exc import exc
from lingu.ui.ui import UI
from typing import List
import importlib
import inspect
import json
import time
import os


language = cfg("language", default="en")
load_start = ['state.py', 'logic.py']
load_delayed = ['inference.py', 'ui.py']
module_path = "lingu/modules"


class InferenceObject():
    """
    Represents an inference object, encapsulating information about
    its creation, module, and type.

    Attributes:
        name (str): The name of the inference object.
        instance (InstanceType): The instance of the object.
        module (dict): The module where the object is defined.
        creation_time (float): Timestamp of object creation.
        language_info (dict): Language-specific information.
        schema (dict): Schema related to the OpenAI API.
        is_internal (bool): Flag indicating if object is internal.
        execute_count (int): Counter for the number of executions.
    """
    def __init__(self, name=None, instance=None, module=None):
        self.name = name
        self.instance = instance
        self.is_invokable = isinstance(instance, Invokable)
        self.is_populatable = not self.is_invokable
        self.creation_time = time.time()
        self.language_info = {}
        self.schema = self.instance.openai_schema
        self.module = module
        self.is_internal = False
        self.execute_count = 0


class Modules:
    """
    Manages the modules within the application, including their import,
    initialization, and retrieval of inference objects.

    Attributes:
        all (dict): Dictionary of all modules.
        populatables (list): List of populatable modules.
        invokables (list): List of invokable modules.
        inference_manager (InferenceManager): Manager for inference operations.
    """
    def __init__(self):
        self.all = {}
        self.populatables = []
        self.invokables = []
        self.inference_manager = InferenceManager()

    def import_file(self, py_file: str, folder: str, module: dict):
        """
        Imports a Python file and processes its contents, identifying
        various components like states, logic, UI, and inference objects.

        Args:
            py_file (str): The Python file name to import.
            folder (str): The folder where the file is located.
            module (dict): The module dictionary to populate.
        """
        base_name = os.path.basename(folder)
        py_file_path = f"lingu.modules.{base_name}" \
                       f".{py_file[:-3]}"

        log.inf(f"  + importing file {py_file_path}")
        mod = importlib.import_module(py_file_path)

        for name, obj in inspect.getmembers(mod):

            module["modules"][base_name] = mod

            if inspect.isclass(obj) and issubclass(obj, State) \
                    and obj is not State:

                log.inf(f"    + state found: {obj.__name__}")
                file_state = mod.state if hasattr(mod, 'state') else None
                state_path = os.path.join(folder, f"{base_name}_state.json")
                instance = file_state if file_state else obj()

                if State.is_load_available(state_path):
                    module["state"] = State.load(state_path, instance)
                else:
                    module["state"] = instance
                module["state"].module_name = base_name
                module["state"].state_file_path = state_path
                import_repeat_functions(module, module["state"])

            if inspect.isclass(obj) and issubclass(obj, Logic) \
                    and obj is not Logic:

                log.inf(f"    + logic found: {obj.__name__}")
                module["logic"] = mod.logic if hasattr(mod, 'logic') else obj()
                module["logic"].module_name = base_name
                module["logic"].inference_manager = self.inference_manager
                import_repeat_functions(module, module["logic"])

            if inspect.isclass(obj) and issubclass(obj, UI) and obj is not UI:

                log.inf(f"    + user interface found: {obj.__name__}")
                module["ui"] = obj

            if inspect.isclass(obj) and issubclass(obj, Populatable) \
                    and obj is not Populatable:

                log.inf(f"    + populatable found: {obj.__name__}")
                module_data = InferenceObject(obj.__name__, obj, module)
                obj.register(obj, base_name)
                module_data.info_dict = obj.info_dict
                self.populatables.append(module_data)
                module["tool_names"].append(obj.__name__)
                module["inf_obj"].append(module_data)
                module_data.is_internal = hasattr(obj, 'is_internal')

            if isinstance(obj, Invokable):

                log.inf(f"    + invokable found: {name}")
                module_data = InferenceObject(name, obj, module)
                module_data.info_dict = obj.info_dict
                self.invokables.append(module_data)
                module["tool_names"].append(name)
                module["inf_obj"].append(module_data)

    def create(self):
        """
        Creates module structures by identifying all folders in the module path
        and initializes their respective properties.
        """
        module_order = cfg('modules')        
        module_folders = self.get_module_folders(module_path)

        for folder in module_folders:
            module_name = os.path.basename(folder)
            if module_order and module_name not in module_order:
                continue
            log.inf(f"+ importing {folder}")
            files = [f for f in os.listdir(folder) if f.endswith('.py')]

            module = {}
            module["folder"] = folder
            module["name"] = module_name
            module["inf_obj"] = []
            module["tool_names"] = []
            module["modules"] = {}
            module["files"] = files

            self.all[module_name] = module

    def _load(self, modules):
        """
        Loads the specified modules.

        Args:
            modules (list): A list of module file names to be loaded.
        """
        for module_file in modules:
            for module in self.all.values():
                if module_file in module["files"]:
                    self.import_file(module_file, module["folder"], module)

    def load_start_modules(self):
        """
        Loads the start modules.
        """
        self._load(load_start)

    def load_delayed_modules(self):
        """
        Loads the delayed modules.
        """
        self._load(load_delayed)

    def import_language_files(self):
        """
        Imports language-specific files for each module.
        """
        for module in self.all.values():
            language_file_name = os.path.join(
                module["folder"],
                f"inference.{language}.json")

            self.import_language_file(language_file_name, module)

    def post_process(self):
        """
        Post-processes modules after loading, setting up necessary references
        between different components like UI, logic, and state.
        """
        for module in self.all.values():
            if "logic" in module and "state" in module:
                module["logic"].state = module["state"]
            if "ui" in module and "state" in module:
                module["ui"].state = module["state"]
            if "ui" in module and "logic" in module:
                module["ui"].logic = module["logic"]
            if "logic" in module and "inference" in module["modules"]:
                module["logic"].inference = module["modules"]["inference"]

    def import_language_file(self, language_file_name, module):
        """
        Imports a language file into the specified module.

        Args:
            language_file_name (str): The name of the language file to import.
            module (dict): The module to which the language file belongs.
        """
        if os.path.isfile(language_file_name):
            with open(language_file_name, 'r', encoding='utf-8') as f:
                log.dbg(f"    + language file: {language_file_name}")
                try:
                    module["lang"] = json.load(f)

                    for inf_obj in module["inf_obj"]:
                        if inf_obj.name in module["lang"]:
                            for key in [
                                'keywords',
                                'init_prompt',
                                'success_prompt',
                                'fail_prompt',
                                'function_name_examples',
                                'function_argument_examples'
                            ]:
                                if key in module["lang"][inf_obj.name]:
                                    value = module["lang"][inf_obj.name][key]
                                    inf_obj.language_info[key] = value

                except Exception as e:
                    log.err("error occurred reading module file "
                            f"{language_file_name}: {str(e)}")
                    exc(e)

    def get_inference_objects(self):
        """
        Retrieves all inference objects (both invokable and populatable).

        Returns:
            list: A combined list of invokable and populatable objects.
        """
        return self.invokables + self.populatables

    def get_module_folders(
            self,
            module_path: str,
            ignore_prefix: str = '_'
            ) -> List[str]:
        """
        Get a list of subdirectories in a given module path,
        excluding those that start with a specified prefix.

        Args:
            module_path (str): The path to the module directory.
            ignore_prefix (str): The prefix to ignore. Defaults to '_'.

        Returns:
            List[str]: A list of subdirectory names.
        """
        module_folders = []

        # Print the absolute path of the module_path for debugging
        absolute_path = os.path.abspath(module_path)
        log.inf(f"importing modules from: {absolute_path}")

        try:
            with os.scandir(module_path) as files:

                for file in files:
                    # Add folder to list if it's a directory
                    # and doesn't start with the ignore_prefix
                    if (file.is_dir() and
                            not file.name.startswith(ignore_prefix)):

                        module_folder = os.path.join(absolute_path, file.name)
                        module_folders.append(module_folder)

        except FileNotFoundError:
            log.err(f"Folder '{module_path}' was not found.")
        except PermissionError:
            log.err(f"Permission denied to access folder '{module_path}'.")
        return module_folders

    def init(self):
        """
        Initializes the logic component of each module in the application.
        This method iterates through all modules and calls their `init` method
        if they have a logic component.
        """
        for module in self.all.values():
            if "logic" in module:
                log.inf(f"Initializing logic of module {module['name']}")
                module["logic"].init()

    def init_finished(self):
        """
        Marks the completion of the initialization process for the logic
        components of each module. This method is typically called after all
        modules' logic components have been initialized.
        """
        for module in self.all.values():
            if "logic" in module:
                log.inf("Initializing finished logic of module "
                        f"{module['name']}")
                module["logic"].init_finished()

    def wait_ready(self):
        """
        Waits for logic modules to be ready with a timeout.
        """
        for module in self.all.values():
            if "logic" in module:
                is_ready = False
                while not is_ready:
                    is_ready = module["logic"].ready_event.wait(timeout=1)
                    if not is_ready:
                        log.inf("[modules] waiting for logic of module "
                                f"{module['name']} to be ready")

        log.inf("[modules] all modules ready  🎉🎈🍹🎆🌟")

    def set_ready_event(self):
        """
        Sets the ready event for all logic modules.
        """
        for module in self.all.values():
            if "logic" in module:
                module["logic"].server_ready_event.set()

        self.inference_manager.set_inference_objects(
            self.get_inference_objects())

    def post_init_processing(self):
        """
        Performs post-initialization processing for all modules.
        """
        for module in self.all.values():
            if "logic" in module:
                module["logic"].post_init_processing()
