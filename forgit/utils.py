from functools import wraps
from typing import Optional, Any, Callable, NoReturn

from forgit.messages import NOT_IMPLEMENTED


def nested_get(dict_: dict, *keys: str) -> Optional[Any]:
    last = None
    for key in keys:
        last = dict_.get(key)
        if last is None:
            return None

    return last


def call_func(given_func: Callable[[Any], Any]) -> Any:
    """
    Calls function specified as an argument with arguments from wrapped function.

    Args:
        given_func: a given function to call with parameters from wrapped function

    Returns:
        Return value of given_func.
    """

    @wraps(given_func)
    def wrap_decorated_func(decorated_func):
        @wraps(decorated_func)
        def call_given_func_with_args_from_decorated_func(*args, **kwargs):
            return given_func(*args, **kwargs)

        return call_given_func_with_args_from_decorated_func

    return wrap_decorated_func


def retryable(retry_limit: int) -> NoReturn:
    """
    Retry function/method when it returns False.

    Wraps only functions/methods which returns bool. The functions/methods have to be
     idempotent (or at least have some mechanism to make them "idempotent"), otherwise
     unexpected things may happen.

    Args:
        retry_limit: max retry limit. Defaults to TODO
    """
    # TODO:
    raise NotImplementedError(NOT_IMPLEMENTED)


class DictObj:
    """
    Object which behaves as dictionary, but to access the dictionary is done via dot
     notation.
    """

    # TODO: good idea? less writing for me, but confusing
    pass
