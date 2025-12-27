import copy
from typing import Any
from unittest.mock import Mock

import pytest

import purekit as pk


@pytest.mark.parametrize(
    "value, is_mutable",
    [
        (None, False),
        (5, False),
        ("abc", False),
        ([1, 2, 3], True),
        ((1, 2), False),
        ({"a": 1}, True),
    ],
)
def test_identity(value: Any, is_mutable: bool):
    expected = copy.deepcopy(value)

    result = pk.fn.identity(value)

    assert result is value
    assert result == expected
    if is_mutable:
        assert result is not expected


class TestPipe:
    def test_pipe_single_function(self):
        assert pk.fn.pipe(2, [lambda x: x + 1]) == 3

    def test_pipe_multiple_functions(self):
        assert pk.fn.pipe(2, [lambda x: x + 1, lambda x: x * 3]) == 9

    def test_pipe_heterogeneous_types(self):
        def to_str(x: int) -> str:
            return f"{x=}"

        def to_len(s: str) -> int:
            return len(s)

        assert pk.fn.pipe(5, [to_str, to_len]) == len("x=5")

    def test_pipe_no_functions_returns_input(self):
        assert pk.fn.pipe("data", []) == "data"

    @pytest.mark.parametrize(
        "data, functions, expected",
        [
            (3, [lambda x: x * 2], 6),
            ("4", [int, lambda n: n * n, str], "16"),
            ("5", [int, float, lambda x: x > 0], True),
            ("unchanged", [], "unchanged"),
            ("hello", [lambda x: x, lambda x: x], "hello"),
        ],
        ids=[
            "single function",
            "multiple functions",
            "type transformations",
            "empty pipeline",
            "identity pipeline",
        ],
    )
    def test_pipe(self, data: Any, functions: list, expected: Any):
        assert pk.fn.pipe(data, functions) == expected

    def test_function_raises_error(self):
        def bad_fn(x: Any) -> Any:
            raise ValueError("Oops!")

        with pytest.raises(ValueError):
            pk.fn.pipe(10, [bad_fn])

    def test_pipe_functions_called_in_order(self):
        f1 = Mock(side_effect=lambda x: x + 1)
        f2 = Mock(side_effect=lambda x: x * 2)

        result = pk.fn.pipe(3, [f1, f2])

        assert result == 8
        f1.assert_called_once_with(3)
        f2.assert_called_once_with(4)
