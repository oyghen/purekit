from typing import Any

import pytest

import purekit as pk


class TestFlatten:
    @pytest.mark.parametrize(
        "items, expected",
        [
            # simple iterables
            ([1, 2, 3], [1, 2, 3]),
            ((1, 2, 3), [1, 2, 3]),
            (range(1, 7), [1, 2, 3, 4, 5, 6]),
            ([1, [2, 3, 4, 5], 6, []], [1, 2, 3, 4, 5, 6]),
            ([[], [1, 2], [3, 4], [5, 6]], [1, 2, 3, 4, 5, 6]),
            ([[1, 2], [3, 4], [5, 6]], [1, 2, 3, 4, 5, 6]),
            ([[[1, 2]], [3], 4, [[[5]]], [[[[6]]]]], [1, 2, 3, 4, 5, 6]),
            ([[1, 2], [3, 4, 5], 6], [1, 2, 3, 4, 5, 6]),
            (([[1, 2], [3, 4, 5], 6],), [1, 2, 3, 4, 5, 6]),
            ([iter([1, (2, 3)]), 4, [], iter([[[5]], 6])], [1, 2, 3, 4, 5, 6]),
            # iterators / generators
            (map(lambda x: 2 * x, range(1, 7)), [2, 4, 6, 8, 10, 12]),
            ((2 * x for x in range(1, 7)), [2, 4, 6, 8, 10, 12]),
            (tuple(2 * x for x in range(1, 7)), [2, 4, 6, 8, 10, 12]),
            (([-1], 0, range(1, 7)), [-1, 0, 1, 2, 3, 4, 5, 6]),
            (([-1], 0, map(lambda x: 2 * x, range(1, 4))), [-1, 0, 2, 4, 6]),
            (([-1], 0, (2 * x for x in range(1, 4))), [-1, 0, 2, 4, 6]),
            (([-1], 0, tuple(2 * x for x in range(1, 4))), [-1, 0, 2, 4, 6]),
            (([-1], 0, list(2 * x for x in range(1, 4))), [-1, 0, 2, 4, 6]),
            # mixed heterogenous nesting
            ([[1, 2], 3, (4, 5), (6,)], [1, 2, 3, 4, 5, 6]),
            ([1, [2, 3, 4], [[5, 6]]], [1, 2, 3, 4, 5, 6]),
            (filter(lambda x: x % 2 == 0, range(1, 7)), [2, 4, 6]),
            ((-1, filter(lambda x: x % 2 == 0, range(1, 7))), [-1, 2, 4, 6]),
            (([-1], filter(lambda x: x % 2 == 0, range(1, 7))), [-1, 2, 4, 6]),
            (
                [["one", 2], 3, [4, "five"], ["six"]],
                ["one", 2, 3, 4, "five", "six"],
            ),
        ],
    )
    def test_flatten(self, items: Any, expected: list[Any]):
        assert list(pk.seq.flatten(items)) == expected

    def test_no_args(self):
        assert list(pk.seq.flatten([])) == []

    def test_max_depth_behavior(self):
        nested = [[1, 2], [3, [4, 5]]]
        assert list(pk.seq.flatten(nested, max_depth=0)) == [[1, 2], [3, [4, 5]]]
        assert list(pk.seq.flatten(nested, max_depth=1)) == [1, 2, 3, [4, 5]]
        assert list(pk.seq.flatten(nested, max_depth=None)) == [1, 2, 3, 4, 5]

    def test_atomic_types_default_and_custom(self):
        # default atomic types treat strings/bytes as atomic
        result = list(pk.seq.flatten(["one", ["two"], b"bytes"]))
        assert result == ["one", "two", b"bytes"]
        # custom atomic type: treat tuple as atomic
        items = [1, (2, 3), [4]]
        assert list(pk.seq.flatten(items, atomic_types=tuple)) == [1, (2, 3), 4]
        assert list(pk.seq.flatten(items, atomic_types=(tuple,))) == [1, (2, 3), 4]

    def test_iterator_consumption_and_exhaustion(self):
        gen = (x for x in [1, 2, 3])
        assert list(pk.seq.flatten(gen)) == [1, 2, 3]
        # generator is now exhausted
        assert list(pk.seq.flatten(gen)) == []

    def test_dict_iteration_behavior(self):
        d = {"a": 1, "b": 2}
        assert list(pk.seq.flatten(d)) == ["a", "b"]

    def test_bytes_and_bytearray_are_atomic(self):
        result = list(pk.seq.flatten([b"abc", bytearray(b"xyz")]))
        assert result == [b"abc", bytearray(b"xyz")]

    def test_negative_max_depth_raises(self):
        with pytest.raises(ValueError):
            list(pk.seq.flatten([1, 2], max_depth=-1))
