__all__ = ("PurekitError", "RetryError")

from typing import TypeVar

T = TypeVar("T")


class PurekitError(Exception):
    """Base exception for all errors raised by purekit."""

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = self.__class__.__name__
        self.message: str = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"


class RetryError(PurekitError, RuntimeError):
    """Raised when all retry attempts for an operation are exhausted."""

    pass
