__all__ = ["EnumMixin"]

from enum import Enum
from typing import Any, cast


class EnumMixin:
    @classmethod
    def get_members(cls) -> tuple[Enum, ...]:
        """Return a tuple of all members."""
        enum_cls = cast(type[Enum], cls)
        return tuple(enum_cls)

    @classmethod
    def get_count(cls) -> int:
        """Return the number of enum members."""
        return len(cls.get_members())

    @classmethod
    def get_names(cls) -> tuple[str, ...]:
        """Return a tuple of all member names."""
        return tuple(member.name for member in cls.get_members())

    @classmethod
    def get_values(cls) -> tuple[Any, ...]:
        """Return a tuple of all member values."""
        return tuple(member.value for member in cls.get_members())

    @classmethod
    def get_member_by_name(cls, name: str, preview: int = 3) -> Enum:
        """Return an enum member by its name."""
        enum_cls = cast(type[Enum], cls)
        try:
            return enum_cls[name]
        except KeyError as exc:
            available = cls._format_preview(cls.get_names(), preview)
            raise KeyError(
                f"{cls.__qualname__} has no member named {name!r}. "
                f"Available names ({cls.get_count()}): {available}"
            ) from exc

    @classmethod
    def get_member_by_value(cls, value: Any, preview: int = 3) -> Enum:
        """Return an enum member by its value."""
        enum_cls = cast(type[Enum], cls)
        try:
            return enum_cls(value)
        except ValueError as exc:
            available = cls._format_preview(cls.get_values(), preview)
            raise ValueError(
                f"{cls.__qualname__} has no member with value {value!r}. "
                f"Available values ({cls.get_count()}): {available}"
            ) from exc

    @staticmethod
    def _format_preview(items: tuple[Any, ...], n: int) -> str:
        """Return a formatted preview string of items, truncated after n items."""
        preview = ", ".join(map(repr, items[:n]))
        if len(items) > n:
            preview += ", ..."
        return preview
