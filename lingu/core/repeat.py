from typing import Callable
from .log import log
from .exc import exc
import threading
import inspect
import time


def repeat(value: int) -> Callable:
    """
    Decorator to mark a function for repetition at a set interval.

    Args:
        interval (int): The interval (in seconds) for the function to repeat.

    Returns:
        Callable: The wrapped function with an attribute
          indicating the repeat interval.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result
        wrapper.repeat_interval = value
        return wrapper
    return decorator


def execute_single_function(repeat_function):
    """
    Executes a single repeat function and handles exceptions.

    Args:
        repeat_function (RepeatFunction): The repeat function to execute.
    """
    try:
        repeat_function.func()
    except Exception as e:
        log.err("  Error occurred executing repeat function "
                f"{repeat_function.name}")
        exc(e)


def execute_repeat(modules):
    """
    Executes repeat functions in provided modules.

    Args:
        modules (list): List of modules containing repeat functions.
    """
    for module in modules:
        if "repeat_functions" not in module:
            continue
        for fct in module["repeat_functions"]:
            if time.time() - fct.last_execution > fct.interval:
                fct.last_execution = time.time()
                thread = threading.Thread(
                    target=execute_single_function,
                    args=(fct,)
                )
                thread.start()


class RepeatFunction():
    """
    Represents a function set to repeat at specified intervals.

    Attributes:
        func (Callable): The function to be repeated.
        name (str): The name of the function.
        interval (int): The time interval (in seconds) between repetitions.
        last_execution (float): The last execution time in Unix timestamp.
    """
    def __init__(self, func, name, interval):
        self.func = func
        self.name = name
        self.interval = interval
        self.last_execution = 0

    def __str__(self):
        return f"{self.name} ({self.interval}s)"


def import_repeat_functions(module, instance):
    """
    Imports repeat functions from a given module and instance.

    Args:
        module (dict): The module dictionary to add repeat functions to.
        instance (Any): The instance containing methods to be checked.
    """
    if "repeat_functions" not in module:
        module["repeat_functions"] = []

    for method_name, method in inspect.getmembers(
        instance,
        predicate=inspect.ismethod
    ):

        if hasattr(method, 'repeat_interval'):
            repeat_function = RepeatFunction(
                method,
                method_name,
                method.repeat_interval
            )

            log.dbg(f"    + repeats \"{repeat_function.name}\" "
                    f"every {repeat_function.interval}s")

            module["repeat_functions"].append(repeat_function)
