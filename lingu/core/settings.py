from typing import Any, Dict, Optional
from .log import log
import yaml
import sys
import os

settings_file = "lingu/settings.yaml"


class SettingsManager:
    """
    A class to manage application settings loaded from a YAML file.

    Attributes:
        file_path (str): The path to the YAML configuration file.
        settings (Dict[str, Any]): The loaded settings as a nested dictionary.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initializes the SettingsManager with the given file path.
        If a file path was submitted per command line, it will be used instead.

        Args:
            file_path (str): The path to the YAML configuration file.
        """
        self.command_line_path = self.get_command_line_path()
        self.file_path: str = self.command_line_path or file_path
        self.settings: Dict[str, Any] = self.load_settings()
        if not self.settings:
            log.err("No settings loaded.")
            exit(0)

    def get_command_line_path(self) -> Optional[str]:
        """
        Retrieves the file path from the command line arguments.

        Returns:
            Optional[str]: The file path from the command line arguments.
              Returns None if no file path was submitted.
        """
        if len(sys.argv) > 1:
            yaml_file_path = sys.argv[1]
            if __name__ == '__main__':
                log.dbg("  [settings] Using file from command line: "
                        f"{yaml_file_path}")
            return yaml_file_path
        return None

    def load_settings(self) -> Dict[str, Any]:
        """
        Loads the settings from the YAML file.

        Returns:
            Dict[str, Any]: The loaded settings as a nested dictionary.
              Returns an empty dictionary if the file is not found or
              on parsing errors.
        """
        try:
            with open(self.file_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            log.err(f"Configuration file not found: {self.file_path}")
            return {}
        except yaml.YAMLError as exc:
            log.err(f"Error parsing YAML file: {exc}")
            return {}

    def get(self,
            *keys: str,
            env_key: str = "",
            default: Optional[Any] = None,
            debug: bool = False) -> Any:
        """
        Retrieves a setting value based on a sequence of keys.

        Args:
            *keys (str): A sequence of keys to traverse
              the settings dictionary.
            env_key (str, optional): An environment variable key to
              use as a fallback.
            default (Optional[Any], optional): The default value to return if
              the keys are not found and the environment variable is not set.
            debug (bool, optional): Whether to log debug messages.

        Returns:
            Any: The value of the setting or the default value if not found.
        """

        current_level = self.settings
        if debug:
            log.dbg(f"  [settings] Getting: {keys}")
        for key in keys:
            if isinstance(current_level, dict) and key in current_level:
                current_level = current_level[key]
            else:
                if env_key:
                    return os.environ.get(env_key, default)
                else:
                    return default
        return current_level


cfg = SettingsManager(settings_file).get
