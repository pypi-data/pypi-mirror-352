import logging as _logging
from functools import wraps
from rich.console import Console


logger = _logging.getLogger("factory SDK")
_logging.basicConfig(level=_logging.INFO)

console = Console()


def print_exceptions(show_locals: bool = True):
    """
    Decorator that catches all exceptions in the wrapped function
    and prints them using Rich's console.print_exception.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                # Print the traceback with local variables
                console.print_exception(show_locals=show_locals)
                # Optionally, re-raise the exception so it can be handled upstream
                # raise

        return wrapper

    return decorator
