import functools
import math
import re
from collections.abc import Iterator

import pytest

import purekit as pk


class TestCharDiff:
    @pytest.mark.parametrize(
        "s1, s2, expected",
        [
            ("hello", "hello", "hello\n\nhello"),
            ("hello", "hall", "hello\n |  |\nhall"),
            ("hello", "hallo", "hello\n |   \nhallo"),
            ("hello", "hell", "hello\n    |\nhell"),
            ("hall", "hello", "hall\n |  |\nhello"),
            ("", "", "\n\n"),
            ("", "a", "\n|\na"),
            ("abc", "abd", "abc\n  |\nabd"),
            ("café", "cafe", "café\n   |\ncafe"),
            ("1234", "11342", "1234\n |  |\n11342"),
            ("1234.56", "1234,56", "1234.56\n    |  \n1234,56"),
        ],
    )
    def test_basic(self, s1: str, s2: str, expected: str):
        result = pk.text.char_diff(s1, s2)
        assert result == expected

    @pytest.mark.parametrize(
        "s1, s2",
        [
            ("hello", "hall"),
            ("", "a"),
            ("abc", "abd"),
        ],
    )
    def test_marker_len_equals_max_len_when_different(self, s1: str, s2: str):
        result = pk.text.char_diff(s1, s2)
        _, marker, _ = result.split("\n")
        assert "|" in marker
        assert len(marker) == max(len(s1), len(s2))

    def test_middle_line_empty_when_identical(self):
        result = pk.text.char_diff("same", "same")
        top, marker, bottom = result.split("\n")
        assert marker == ""
        assert top == bottom == "same"

    def test_positional_only_signature(self):
        with pytest.raises(TypeError):
            pk.text.char_diff(string1="a", string2="b")


class TestConcat:
    def test_default(self):
        assert pk.text.concat(["a", "b", "c"]) == "a b c"

    def test_basic_and_empty(self):
        assert pk.text.concat(["a", "b", "c"], sep=",") == "a,b,c"
        assert pk.text.concat([], sep=",") == ""

    def test_iterables_and_none(self):
        assert pk.text.concat(["a", None, ["b", None, 3]], sep=",") == "a,b,3"
        assert pk.text.concat([["a", ["b", None], ("c",)]], sep="-") == "a-b-c"

    def test_atomic_string_behavior(self):
        assert pk.text.concat(["abc"], sep="-") == "abc"

    def test_coercion_and_generators(self):
        assert pk.text.concat([1, ["2", 3]], sep=",") == "1,2,3"
        assert pk.text.concat([(i for i in [4, 5])], sep=",") == "4,5"

    def test_only_none_and_empty_strings(self):
        assert pk.text.concat([None, [None, None]], sep="|") == ""
        assert pk.text.concat(["", "a"], sep="-") == "-a"

    def test_bytes_are_atomic_and_stringified(self):
        assert pk.text.concat([b"bytes", b"more"], sep=":") == "b'bytes':b'more'"

    def test_concat_strings_basic_list(self):
        strings = ["Hello", "World"]
        result = pk.text.concat(strings, " ")
        assert result == "Hello World"

    def test_concat_strings_with_partial(self):
        strings = ["Hello", "World"]
        concat = functools.partial(pk.text.concat, sep=" + ")
        result = concat(strings)
        assert result == "Hello + World"

    def test_concat_strings_with_none_entries(self):
        strings = ["Hello", None, "World", None]
        result = pk.text.concat(strings, sep=" ")
        assert result == "Hello World"

    def test_concat_strings_with_map(self):
        concat = functools.partial(pk.text.concat, sep=" ")
        result = tuple(map(concat, [["Hello", "World"], ["Hi", "there"]]))
        assert result == ("Hello World", "Hi there")


class TestFindall:
    def test_returns_iterator_and_yields_lists(self):
        strings = ["one 1", "two 22", "none"]
        result = pk.text.findall(strings, r"\d+")
        assert isinstance(result, Iterator)
        assert list(result) == [["1"], ["22"], []]

    def test_default_flags_are_ignorecase(self):
        strings = ["Foo", "bar", "FOOfoo"]
        result = list(pk.text.findall(strings, r"foo"))
        assert result == [["Foo"], [], ["FOO", "foo"]]

    def test_explicit_zero_flags_means_case_sensitive(self):
        strings = ["Foo", "foo"]
        result = list(pk.text.findall(strings, r"foo", flags=re.NOFLAG))
        assert result == [[], ["foo"]]

    def test_compiled_pattern_uses_its_own_flags_and_ignores_flags_arg(self):
        compiled = re.compile(r"^a.*b$", re.DOTALL)
        strings = ["a\nb", "acb", "no-match"]
        result = list(pk.text.findall(strings, compiled, flags=re.NOFLAG))
        assert result == [["a\nb"], ["acb"], []]

    def test_no_match_returns_empty_list(self):
        strings = ["alpha", "beta"]
        result = list(pk.text.findall(strings, r"z"))
        assert result == [[], []]

    def test_non_str_item_raises_type_error(self):
        strings = ["ok", 123]
        with pytest.raises(TypeError):
            list(pk.text.findall(strings, r"\d+"))


class TestGrep:
    def test_returns_iterator_and_yields_matching_texts(self):
        strings = ["one 1", "two 22", "none"]
        result = pk.text.grep(strings, r"\d+")
        assert isinstance(result, Iterator)
        assert list(result) == ["one 1", "two 22"]

    def test_default_flags_are_ignorecase(self):
        strings = ["Foo", "bar", "FOOfoo"]
        result = list(pk.text.grep(strings, r"foo"))
        assert result == ["Foo", "FOOfoo"]

    def test_explicit_zero_flags_is_case_sensitive(self):
        strings = ["Foo", "foo"]
        result = list(pk.text.grep(strings, r"foo", flags=re.NOFLAG))
        assert result == ["foo"]

    def test_compiled_pattern_respects_compiled_flags(self):
        compiled = re.compile(r"^a.*b$", re.DOTALL)
        strings = ["a\nb", "acb", "no-match"]
        result = list(pk.text.grep(strings, compiled, flags=re.NOFLAG))
        assert result == ["a\nb", "acb"]

    def test_empty_iterable_returns_empty(self):
        strings = []
        result = list(pk.text.grep(strings, r".+"))
        assert result == []

    def test_non_str_element_raises_type_error(self):
        strings = ["ok", 123]
        with pytest.raises(TypeError):
            list(pk.text.grep(strings, r"\d+"))


class TestHeadline:
    def test_default_width(self):
        result = pk.text.headline("Hello")
        assert isinstance(result, str)
        assert len(result) == 79
        assert " Hello " in result
        assert result.startswith("-")
        assert result.endswith("-")

    def test_custom_width_centering(self):
        title = "Hello"
        result = pk.text.headline(title, width=20)
        assert len(result) == 20
        inner_title = f" {title} "
        left = result.index(inner_title)
        right = len(result) - (left + len(inner_title))
        assert abs(left - right) <= 1

    def test_width_too_small_default_min_pad(self):
        result = pk.text.headline("Hello", width=2)
        assert result == "--- Hello ---"
        assert len(result) == len("--- Hello ---")

    def test_width_too_small_custom_min_pad(self):
        result = pk.text.headline("Hello", width=2, min_pad=1)
        assert result == "- Hello -"
        assert len(result) == len("- Hello -")

    def test_custom_pad_char(self):
        result = pk.text.headline("Hello", width=20, pad_char="*")
        assert result.startswith("*")
        assert result.endswith("*")
        assert len(result) == 20

    def test_small_width_custom_pad_char_and_min_pad(self):
        result = pk.text.headline("Hello", width=2, pad_char="*", min_pad=4)
        assert result == "**** Hello ****"
        assert len(result) == len("**** Hello ****")

    @pytest.mark.parametrize("pad_char", ["", "##", 5])
    def test_invalid_pad_char_raises(self, pad_char):
        with pytest.raises(TypeError):
            pk.text.headline("Hello", pad_char=pad_char)

    @pytest.mark.parametrize("bad_min", ["x", None, 1.5])
    def test_invalid_min_pad_type_raises(self, bad_min):
        with pytest.raises(TypeError):
            pk.text.headline("Hello", width=2, min_pad=bad_min)


class TestNumstr:
    @pytest.mark.parametrize(
        "value, expected",
        [
            (0, "0"),
            (-0.0, "0"),
            (1, "1"),
            (10, "10"),
            (100, "100"),
            (1000, "1_000"),
            (1000000, "1_000_000"),
            (100000.0, "100_000"),
            (100000.01, "100_000.01"),
            (1234567, "1_234_567"),
            (-1234567, "-1_234_567"),
            (1234.567, "1_234.567"),
            (-1234.567, "-1_234.567"),
            (0.000123, "0.000123"),
            (1.5, "1.5"),
            (0.1 + 0.2, "0.3"),
        ],
    )
    def test_basic_values(self, value, expected):
        """Formatting for integers, negatives, zeros and ordinary floats."""
        assert pk.text.numstr(value) == expected

    def test_nan_and_infinities(self):
        """NaN and infinities are returned via built-in str()."""
        for v in (math.nan, math.inf, -math.inf):
            assert pk.text.numstr(v) == str(v)

    def test_type_error_for_non_number(self):
        """Non-numeric types raise a clear TypeError."""
        with pytest.raises(TypeError) as excinfo:
            pk.text.numstr("123")
        assert "unsupported type" in str(excinfo.value)


@pytest.mark.parametrize(
    "input_string, expected",
    [
        ("no punctuation", "no punctuation"),
        (" string with whitespaces ", " string with whitespaces "),
        ("CAPITAL LETTERS", "CAPITAL LETTERS"),
        ("exclamation mark!", "exclamation mark"),
        ('quotation mark"', "quotation mark"),
        ("hash#", "hash"),
        ("dollar$", "dollar"),
        ("percentage%", "percentage"),
        ("ampersand&", "ampersand"),
        ("apostrophe'", "apostrophe"),
        ("asterisk*", "asterisk"),
        ("plus+", "plus"),
        ("comma,", "comma"),
        ("dash-", "dash"),
        ("period.", "period"),
        ("slash/", "slash"),
        ("colon:", "colon"),
        ("semicolon;", "semicolon"),
        ("less than sign<", "less than sign"),
        ("equal sign=", "equal sign"),
        ("greater than sign>", "greater than sign"),
        ("question mark?", "question mark"),
        ("at sign@", "at sign"),
        ("backslash\\", "backslash"),
        ("caret^", "caret"),
        ("underscore_", "underscore"),
        ("backtick`", "backtick"),
        ("vertical bar symbol|", "vertical bar symbol"),
        ("tilde~", "tilde"),
        ("(round brackets)", "round brackets"),
        ("{curly brackets}", "curly brackets"),
        ("[square brackets]", "square brackets"),
    ],
)
def test_remove_punctuation(input_string: str, expected: str):
    result = pk.text.remove_punctuation(input_string)
    assert result == expected
