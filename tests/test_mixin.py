from enum import Enum

import pytest

from purekit.mixin import EnumMixin


class TestEnumMixin:
    class SomeEnum(EnumMixin, Enum):
        FIRST = 1
        ALIAS = 1  # lookup returns the first defined member, skipping aliases
        SECOND = 2
        THIRD = "three"

    def test_get_members(self):
        all_members = self.SomeEnum.get_members()
        assert isinstance(all_members, tuple)
        assert len(all_members) == 3
        assert all(isinstance(mbr, self.SomeEnum) for mbr in all_members)

    def test_get_count(self):
        assert self.SomeEnum.get_count() == 3

    def test_get_names(self):
        names = self.SomeEnum.get_names()
        assert isinstance(names, tuple)
        assert names == ("FIRST", "SECOND", "THIRD")

    def test_get_values(self):
        values = self.SomeEnum.get_values()
        assert isinstance(values, tuple)
        assert values == (1, 2, "three")

    def test_get_member_by_name__success(self):
        member = self.SomeEnum.get_member_by_name("FIRST")
        assert member == self.SomeEnum.FIRST
        assert member.value == 1

    @pytest.mark.parametrize("name", ["first", "FOURTH"])
    def test_get_member_by_name__fail(self, name: str):
        with pytest.raises(KeyError) as excinfo:
            self.SomeEnum.get_member_by_name(name)

        result = excinfo.value.args[0]
        expected = (
            f"TestEnumMixin.SomeEnum has no member named {name!r}. "
            "Available names (3): 'FIRST', 'SECOND', 'THIRD'"
        )
        assert result == expected

    @pytest.mark.parametrize("name", ["first", "FOURTH"])
    def test_get_member_by_name__preview(self, name: str):
        with pytest.raises(KeyError) as excinfo:
            self.SomeEnum.get_member_by_name(name, preview=2)

        result = excinfo.value.args[0]
        expected = (
            f"TestEnumMixin.SomeEnum has no member named {name!r}. "
            "Available names (3): 'FIRST', 'SECOND', ..."
        )
        assert result == expected

    def test_get_member_by_value__success(self):
        member = self.SomeEnum.get_member_by_value(1)
        assert member == self.SomeEnum.FIRST

        member = self.SomeEnum.get_member_by_value("three")
        assert member == self.SomeEnum.THIRD

    def test_get_member_by_value__fail(self):
        with pytest.raises(ValueError) as excinfo:
            self.SomeEnum.get_member_by_value(4)

        result = excinfo.value.args[0]
        expected = (
            "TestEnumMixin.SomeEnum has no member with value 4. "
            "Available values (3): 1, 2, 'three'"
        )
        assert result == expected

    def test_get_member_by_value__preview(self):
        with pytest.raises(ValueError) as excinfo:
            self.SomeEnum.get_member_by_value(4, preview=2)

        result = excinfo.value.args[0]
        expected = (
            "TestEnumMixin.SomeEnum has no member with value 4. "
            "Available values (3): 1, 2, ..."
        )
        assert result == expected

    def test_get_member_by_value__alias(self):
        assert self.SomeEnum.FIRST is self.SomeEnum.ALIAS
        assert self.SomeEnum.FIRST == self.SomeEnum.ALIAS

        member = self.SomeEnum.get_member_by_value(1)
        assert member is self.SomeEnum.FIRST
        assert member == self.SomeEnum.FIRST

        assert member is self.SomeEnum.ALIAS
        assert member == self.SomeEnum.ALIAS

    @pytest.mark.parametrize("expected", SomeEnum.get_members())
    def test_member_attrs(self, expected: Enum):
        result = self.SomeEnum.get_member_by_name(expected.name)
        assert result == expected
        assert result.name == expected.name
        assert result.value == expected.value

    def test_enum_comparison(self):
        assert self.SomeEnum.FIRST == self.SomeEnum.FIRST
        assert self.SomeEnum.FIRST != self.SomeEnum.SECOND
