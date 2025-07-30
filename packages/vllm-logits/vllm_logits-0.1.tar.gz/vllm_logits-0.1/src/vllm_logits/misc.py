import inspect
import os
import sys
from typing import Any, Callable, Dict, Iterable, List

import dotenv


def infinite_iterator(iterator: Iterable) -> Any:
    """Infinite iterator

    :param iterator: iterator
    :type iterator: iterator
    :yield: item from iterator
    :rtype: Any
    """
    while True:
        for item in iterator:
            yield item


def property_with_cache(func: Callable) -> Callable:
    """Property decorator to cache the result of a property. The result is cached in the attribute of name "_{func.__name__}".

    :param func: function to decorate
    :type func: function
    :return: decorated function
    :rtype: function
    """

    @property
    def decorated_func(*args, **kwargs):
        raise RuntimeError("Deprecated. use functools.cached_property instead.")

    return decorated_func


def to_dict(input_object, exclude_prefixes: List[str] = ["_", "__"]) -> Dict[str, Any]:
    """Transform object to dictionary. Note that all the attributes that starts with "__" or callable are excluded.

    :return: Dictionary that contains all the attributes of the object
    :rtype: Dict
    """
    return {
        key: getattr(input_object, key)
        for key in dir(input_object)
        if all([not key.startswith(prefix) for prefix in exclude_prefixes])
        and not callable(getattr(input_object, key))
    }


def load_dotenv(stack_depth: int = 1):
    """Load dotenv from the order of PYTHONPATH, working directory, and the caller file path.

    :param stack_depth: stack_depth of this function from the target caller, defaults to 1
    :type stack_depth: int, optional
    Example:
        # When the file structure is as follows:
        # .env
        # src/
        #   |
        #   |--test.py

        # We can load dotenv from the test.py as follows (note that the stack_depth is 1)
        load_dotenv(stack_depth=1)

    """
    # Get possible paths
    python_paths = (
        os.environ["PYTHONPATH"].split(":") if "PYTHONPATH" in os.environ else []
    )
    working_dir_path = os.getcwd()
    # TODO: Need to check if this works in all the cases
    caller_file_path = os.path.dirname(
        os.path.abspath(inspect.stack()[stack_depth].filename)
    )
    possible_paths = python_paths + [working_dir_path, caller_file_path]

    # Find and load dotenv
    for path in possible_paths:
        dotenv.load_dotenv(dotenv_path=os.path.join(path, ".env"))
        if "SLACK_ACCESS_TOKEN" in os.environ:
            break


def is_debugger_active() -> bool:
    """Return if the debugger is currently active"""

    gettrace = getattr(sys, "gettrace", None)
    # Check if gettrace is available
    if gettrace is None:
        return False
    # Check trace
    v = gettrace()
    if v is None:
        return False
    else:
        return True
