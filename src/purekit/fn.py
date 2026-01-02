__all__ = ("identity", "pipe", "retry_call", "retry")

import functools
import time
from collections.abc import Callable, Iterable
from typing import Any, Literal, TypeVar

import purekit as pk

T = TypeVar("T")


def identity(value: T, /) -> T:
    """Return value unchanged."""
    return value


def pipe(value: T, functions: Iterable[Callable[[Any], Any]]) -> Any:
    """Return the result of applying a sequence of functions to the initial value."""
    result: Any = value
    for function in functions:
        result = function(result)
    return result


def retry_call(
    func: Callable[..., T],
    attempts: int = 3,
    delay: int | float = 1,
    kind: Literal["fixed", "exponential"] = "exponential",
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    *args: Any,
    **kwargs: Any,
) -> T:
    """Return function result, retrying on specified exceptions with delay."""
    if attempts < 1:
        raise ValueError(f"invalid value {attempts!r}; expected >= 1")
    if delay < 0:
        raise ValueError(f"invalid value {delay!r}; expected >= 0")
    choices = {"fixed", "exponential"}
    if kind not in choices:
        raise pk.exceptions.InvalidChoiceError(kind, choices)

    for attempt in range(attempts):
        try:
            return func(*args, **kwargs)
        except exceptions:
            if attempt == attempts - 1:
                raise
            sleep_for = delay * (2**attempt) if kind == "exponential" else delay
            time.sleep(sleep_for)


def retry(
    attempts: int = 3,
    delay: int | float = 1,
    kind: Literal["fixed", "exponential"] = "exponential",
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Return a decorator that retries the wrapped function on specified exceptions."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """Return wrapped function that retries on the configured exceptions."""

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return retry_call(func, attempts, delay, kind, exceptions, *args, **kwargs)

        return wrapper

    return decorator
