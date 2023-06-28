import configparser
import sys
import os
import inspect

CONFIG_SYSTEM_SECTION = 'system'
DEFAULT_CONFIG_FILE_NAME = 'config.txt'

class SingletonMeta(type):
    """
    Metaclass to implement singleton design pattern.
    This ensures that only one instance of the class can be instantiated.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Overriding the __call__ method to control class instantiation.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    """
    Config class to manage configuration parameters.
    This class uses the Singleton design pattern.
    """

    def __init__(self, config_file_path=DEFAULT_CONFIG_FILE_NAME):
        """
        Initialize the Config class.
        :param config_file_path: Path of the configuration file
        """

        # Check if the config_parser attribute exists, create only if it doesn't
        if not hasattr(self, "config_parser"):

            # If sys.argv has at least two arguments, use the second one as the config file path
            self.config_file_path = config_file_path if len(sys.argv) >= 2 else DEFAULT_CONFIG_FILE_NAME

            # Create a configparser object with allow_no_value set to True
            self.config_parser = configparser.ConfigParser(allow_no_value=True)

            # Load the configuration parameters from the config file
            self.load_config()

    def load_config(self):
        """
        Loads the configuration parameters from the config file.
        """

        # Check if the config file exists
        if not os.path.isfile(self.config_file_path):
            # If not, raise an error
            raise ValueError(f"Config file {self.config_file_path} does not exist")
        
        # Read the config file
        self.config_parser.read(self.config_file_path)

    def items(self):
        """
        Returns all items in the config parser
        """
        return self.config_parser.items

    def get_parser(self) -> configparser.ConfigParser:
        """
        Returns the config parser object.
        """
        return self.config_parser
    
    def get_caller_filename_without_extension(self):
        """
        Returns the file name of the caller without the extension.
        """

        # Get the frame record for the caller
        caller_frame = inspect.stack()[2]
        # Extract just the file name
        file_name = os.path.basename(caller_frame.filename)
        # Remove the .py extension if it exists
        file_name_without_extension, _ = os.path.splitext(file_name)
        return file_name_without_extension    

    def get(self, parameter_name: str, registry_name: str = '', default: str = None, section: str = None) -> str:
        """
        Returns the value of the requested parameter.
        """

        # First, check in the environment variables
        if registry_name and (param := os.environ.get(registry_name)):
            return param
        
        # If the section is not provided, get the file name of the caller
        if not section:
            section = self.get_caller_filename_without_extension()

        # If the section or the parameter doesn't exist in the config file
        if not self.config_parser.has_section(section) or not self.config_parser[section].get(parameter_name):

            # If the system section or the parameter doesn't exist in the system section of the config file
            if not self.config_parser.has_section(CONFIG_SYSTEM_SECTION) or not self.config_parser[CONFIG_SYSTEM_SECTION].get(parameter_name):
                return default
            
            # Return whatever we find in the system section (maybe None)
            return self.config_parser[CONFIG_SYSTEM_SECTION].get(parameter_name)

        # If the parameter exists in the requested section, return it
        return self.config_parser[section].get(parameter_name)

cfg = Config().get
parser = Config().get_parser
items = Config().items