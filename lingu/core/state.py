from .log import log
from .events import events
import json
import os


class State():
    """
    Represents the state of a module in an application.

    This class handles the state of a module, including its activation status,
    disability status, and various informational properties. It provides
    functionality to save and load state from a JSON file.
    """

    def __init__(self):
        """
        Initializes the State with default values.
        """
        self.is_active = False
        self.is_disabled = False
        self.state_file_path = "state.json"
        self.module_name = "Unknown"
        # self.info_text = ""
        # self.large_symbol = "?"
        # self.large_symbol_offset_x = 0
        # self.large_symbol_offset_y = 0
        # self.bottom_info = ""
        # self.bottom_info_offset_x = 0
        # self.bottom_info_offset_y = 0
        # self.top_info = ""
        # self.top_info_offset_x = 0
        # self.top_info_offset_y = 0
        # self.tooltip = "no tooltip provided"

    def set_text(self, text: str):
        """
        Sets the information text of the state.

        Args:
            text (str): The text to set.
        """
        self.info_text = text
        data = {
            "module": self.module_name,
            "text": text
        }
        events.trigger("module_state_text", "brain", data)

    def set_active(self, is_active: bool):
        """
        Sets the active status of the state.

        Args:
            is_active (bool): True to activate the state, False otherwise.
        """
        self.is_active = is_active
        if is_active:
            events.trigger("module_state_active", "brain", self.module_name)
        else:
            events.trigger("module_state_inactive", "brain", self.module_name)

    def set_disabled(self, is_disabled: bool):
        """
        Sets the disabled status of the state.

        Args:
            is_disabled (bool): True to disable the state, False otherwise.
        """
        self.is_disabled = is_disabled
        if is_disabled:
            events.trigger("module_state_disabled", "brain", self.module_name)
        else:
            events.trigger("module_state_enabled", "brain", self.module_name)

    def save(self):
        """
        Saves the state to a JSON file.
        """
        problematic_items = []
        for key, value in self.__dict__.items():
            try:
                json.dumps(value)

            except TypeError:
                problematic_items.append((key, value))

        if problematic_items:
            log.wrn("  [state] found problematic items in state, not saving")
            for key, value in problematic_items:
                log.wrn(f"  [state] key: {key}, value: {value}, "
                        f"type: {type(value).__name__}")
        else:
            data = {
                'class_name': self.__class__.__name__,
                'state_data': self.__dict__
            }

            with open(self.state_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)

            events.trigger("module_state_saved", self.module_name)

    @staticmethod
    def load(filename="state.json", state_instance=None):
        """
        Loads the state from a JSON file.

        Args:
            filename (str): Name of the file to load the state from.
            state_instance (State): An existing instance of State
              to load data into.

        Returns:
            State: The loaded state instance.

        Raises:
            ValueError: If the loaded object is not of type State.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            class_name = data['class_name']
            state_data = data['state_data']
        except Exception as e:
            log.err(f"  [state] error loading state from file {filename}, "
                    f"exception {e}")
            return state_instance

        # Use globals() to get the class by name and create an instance
        if state_instance is None:
            state_class = globals()[class_name]
            state_instance = state_class()

        for key, value in state_data.items():
            setattr(state_instance, key, value)

        if not isinstance(state_instance, State):
            raise ValueError("Loaded object is not of type StateBase, "
                             f"got {type(state_instance)} instead.")

        return state_instance

    @staticmethod
    def is_load_available(filename="state.json"):
        """
        Checks if a state file is available to load.

        Args:
            filename (str): The name of the state file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return os.path.exists(filename)
