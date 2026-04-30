__all__ = ["EnumMixin"]

from enum import Enum
from typing import Any, cast


class EnumMixin:
    @classmethod
    def get_members(cls) -> tuple[Enum, ...]:
        """Return a tuple of all members."""
        return tuple(cast(type[Enum], cls))

    @classmethod
    def get_names(cls) -> tuple[str, ...]:
        """Return a tuple of all member names."""
        return tuple(member.name for member in cls.get_members())

    @classmethod
    def get_values(cls) -> tuple[Any, ...]:
        """Return a tuple of all member values."""
        return tuple(member.value for member in cls.get_members())

    @classmethod
    def get_member_by_name(cls, name: str) -> Enum:
        """Return an enum member by its name."""
        try:
            return cast(type[Enum], cls)[name]
        except KeyError as exc:
            available = ", ".join(cls.get_names())
            raise KeyError(
                f"{cls.__qualname__} has no member named {name!r}. "
                f"Available names: {available}"
            ) from exc

    @classmethod
    def get_member_by_value(cls, value: Any) -> Enum:
        """Return an enum member by its value."""
        try:
            return cast(type[Enum], cls)(value)
        except ValueError as exc:
            available = ", ".join(repr(value) for value in cls.get_values())
            raise ValueError(
                f"{cls.__qualname__} has no member with value {value!r}. "
                f"Available values: {available}"
            ) from exc
