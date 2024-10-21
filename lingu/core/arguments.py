import argparse
import sys

class Arguments:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Arguments, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.parser = argparse.ArgumentParser(description="Lingu core application")
        self.args = None
        self._add_arguments()
        self._parse_args()

    def _add_arguments(self):
        self.parser.add_argument("--runtests", action="store_true", help="Run tests")
        self.parser.add_argument("--tests", action="store_true", help="Run tests")
        self.parser.add_argument("--test", action="store_true", help="Run tests")
        self.parser.add_argument("--settings", type=str, help="Path to the settings file")
        # Add more arguments here as needed

    def _parse_args(self):
        if self.args is None:
            self.args = self.parser.parse_args()

    def get_argument(self, arg_name, default=None):
        """
        Check if an argument was submitted and return its value.
        For flags (store_true/store_false arguments), it returns a boolean.
        For arguments with values, it returns the value if provided, else the default.
        """
        if not hasattr(self.args, arg_name):
            return default
        
        value = getattr(self.args, arg_name)
        if isinstance(value, bool):
            return value
        return value if value is not None else default

# Global function to get arguments
def get_argument(arg_name, default=None):
    """
    Check if an argument was submitted and return its value.
    For flags (store_true/store_false arguments), it returns a boolean.
    For arguments with values, it returns the value if provided, else the default.
    """
    return Arguments().get_argument(arg_name, default)