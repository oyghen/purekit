import pytest

import purekit as pk


class TestEnumMixin:
    class SomeEnum(pk.enums.EnumMixin):
        FIRST = 1
        SECOND = 2
        THIRD = "three"

    def test_all_method(self):
        all_members = self.SomeEnum.all()
        assert isinstance(all_members, tuple)
        assert len(all_members) == 3
        assert all(isinstance(mbr, self.SomeEnum) for mbr in all_members)

    def test_names_method(self):
        names = self.SomeEnum.names()
        assert isinstance(names, tuple)
        assert names == ("FIRST", "SECOND", "THIRD")

    def test_values_method(self):
        values = self.SomeEnum.values()
        assert isinstance(values, tuple)
        assert values == (1, 2, "three")

    def test_get_by_name_success(self):
        member = self.SomeEnum.get_by_name("FIRST")
        assert member == self.SomeEnum.FIRST
        assert member.value == 1

    def test_get_by_name_invalid(self):
        with pytest.raises(pk.exceptions.InvalidChoiceError) as excinfo:
            self.SomeEnum.get_by_name("FOURTH")

        # verify exception details
        assert "FOURTH" in str(excinfo.value)
        assert all(name in str(excinfo.value) for name in self.SomeEnum.names())

    def test_get_by_value_success(self):
        member = self.SomeEnum.get_by_value(1)
        assert member == self.SomeEnum.FIRST

        member = self.SomeEnum.get_by_value("three")
        assert member == self.SomeEnum.THIRD

    def test_get_by_value_not_found(self):
        with pytest.raises(ValueError) as excinfo:
            self.SomeEnum.get_by_value(4)

        assert "no SomeEnum member found for value 4" in str(excinfo.value)

    def test_repr(self):
        repr_str = repr(self.SomeEnum.FIRST)
        assert repr_str == "SomeEnum.FIRST (value: 1)"

    @pytest.mark.parametrize(
        "enum_member, expected_name, expected_value",
        [
            (SomeEnum.FIRST, "FIRST", 1),
            (SomeEnum.SECOND, "SECOND", 2),
            (SomeEnum.THIRD, "THIRD", "three"),
        ],
    )
    def test_enum_member_properties(self, enum_member, expected_name, expected_value):
        assert enum_member.name == expected_name
        assert enum_member.value == expected_value

    def test_enum_comparison(self):
        assert self.SomeEnum.FIRST != self.SomeEnum.SECOND
        assert self.SomeEnum.FIRST == self.SomeEnum.FIRST
