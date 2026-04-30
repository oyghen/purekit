from enum import Enum

import pytest

from purekit.mixin import EnumMixin


class TestEnumMixin:
    class SomeEnum(EnumMixin, Enum):
        FIRST = 1
        SECOND = 2
        THIRD = "three"

    def test_get_members(self):
        all_members = self.SomeEnum.get_members()
        assert isinstance(all_members, tuple)
        assert len(all_members) == 3
        assert all(isinstance(mbr, self.SomeEnum) for mbr in all_members)

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

        assert name in str(excinfo.value)

    def test_get_member_by_value__success(self):
        member = self.SomeEnum.get_member_by_value(1)
        assert member == self.SomeEnum.FIRST

        member = self.SomeEnum.get_member_by_value("three")
        assert member == self.SomeEnum.THIRD

    def test_get_member_by_value__fail(self):
        with pytest.raises(ValueError) as excinfo:
            self.SomeEnum.get_member_by_value(4)

        expected = (
            "TestEnumMixin.SomeEnum has no member with value 4. "
            "Available values: 1, 2, 'three'"
        )
        assert str(excinfo.value) == expected

    @pytest.mark.parametrize("expected", SomeEnum.get_members())
    def test_member_attrs(self, expected: Enum):
        result = self.SomeEnum.get_member_by_name(expected.name)
        assert result is expected
        assert result.name == expected.name
        assert result.value == expected.value

    def test_enum_comparison(self):
        assert self.SomeEnum.FIRST == self.SomeEnum.FIRST
        assert self.SomeEnum.FIRST != self.SomeEnum.SECOND
