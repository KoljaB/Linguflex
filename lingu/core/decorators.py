from typing import Callable, Type


def is_internal() -> Callable[[Type], Type]:
    """A decorator for marking a class as internal.

    Args:
        cls: The class to be decorated.

    Returns:
        The decorated class with an `is_internal` attribute set to True.
    """
    def decorator(cls: Type) -> Type:
        cls.is_internal = True
        return cls
    return decorator
