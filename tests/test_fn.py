import copy
import time
from types import SimpleNamespace
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


class TestRetry:
    def test_retry_call_success_first_try(self):
        def func():
            return 42

        assert pk.fn.retry_call(func) == 42

    @pytest.mark.parametrize(
        "attempts, fail_times",
        [
            (3, 2),
            (5, 4),
            (1, 0),
        ],
    )
    def test_retry_call_retries_and_succeeds(self, attempts: int, fail_times: int):
        state = SimpleNamespace(count=0)

        def func():
            if state.count < fail_times:
                state.count += 1
                raise ValueError("fail")
            return "success"

        result = pk.fn.retry_call(
            func,
            attempts=attempts,
            delay=0,
            exceptions=(ValueError,),
        )
        assert result == "success"
        assert state.count == fail_times

    def test_retry_call_raises_after_max_attempts(self):
        max_attempts = 3
        state = SimpleNamespace(count=0)

        def func():
            state.count += 1
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            pk.fn.retry_call(func, max_attempts, delay=0, exceptions=(RuntimeError,))

        assert state.count == 3

    @pytest.mark.parametrize(
        "attempts, fail_times",
        [
            (3, 2),
            (5, 4),
            (1, 0),
        ],
    )
    def test_retry_decorator_retries_and_succeeds(self, attempts: int, fail_times: int):
        state = SimpleNamespace(count=0)

        @pk.fn.retry(attempts, delay=0, exceptions=(KeyError,))
        def func():
            if state.count < fail_times:
                state.count += 1
                raise KeyError("fail")
            return "success"

        result = func()
        assert result == "success"
        assert state.count == fail_times

    def test_retry_decorator_raises_after_max_attempts(self):
        max_attempts = 3
        state = SimpleNamespace(count=0)

        @pk.fn.retry(max_attempts, delay=0, exceptions=(RuntimeError,))
        def func():
            state.count += 1
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            func()

        assert state.count == 3

    @pytest.mark.parametrize(
        "kind, attempts, delay, expected_sleeps",
        [
            ("fixed", 3, 1, [1, 1]),
            ("exponential", 4, 0.5, [0.5, 1.0, 2.0]),
            ("fixed", 7, 1, [1, 1, 1, 1, 1, 1]),
            ("exponential", 7, 1, [1, 2, 4, 8, 16, 32]),
        ],
    )
    def test_retry_call_sleep_durations(
        self,
        monkeypatch,
        kind: str,
        attempts: int,
        delay: int | float,
        expected_sleeps: list[int | float],
    ):
        state = SimpleNamespace(count=0)
        sleeps = []

        def fake_sleep(duration):
            sleeps.append(duration)

        monkeypatch.setattr(time, "sleep", fake_sleep)

        def func():
            if state.count < attempts - 1:
                state.count += 1
                raise ValueError("fail")
            return "success"

        result = pk.fn.retry_call(
            func,
            attempts=attempts,
            delay=delay,
            kind=kind,
            exceptions=(ValueError,),
        )

        assert result == "success"
        assert state.count == attempts - 1
        assert sleeps == expected_sleeps
