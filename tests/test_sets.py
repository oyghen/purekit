import sys

import pytest

import purekit as pk


class TestTwoSetSummary:
    def test_summarize_str_sets(self):
        set1 = {"a", "c", "b", "g", "h"}
        set2 = {"c", "d", "e", "f", "g"}
        summary = pk.sets.summarize(set1, set2)

        assert isinstance(summary, pk.sets.TwoSetSummary)
        assert isinstance(summary.set1, frozenset)
        assert isinstance(summary.set2, frozenset)
        assert summary.set1 == frozenset(set1)
        assert summary.set2 == frozenset(set2)

        assert summary.union == frozenset({"a", "c", "b", "g", "h", "d", "e", "f"})
        assert summary.intersection == frozenset({"c", "g"})
        assert summary.set1_minus_set2 == frozenset({"a", "b", "h"})
        assert summary.set2_minus_set1 == frozenset({"d", "e", "f"})
        assert summary.sym_diff == frozenset({"a", "b", "h", "d", "e", "f"})

        assert summary.jaccard_score == 0.25
        assert summary.overlap_score == 0.4
        assert summary.dice_score == 0.4

        assert summary.is_equal is False
        assert summary.is_disjoint is False
        assert summary.is_subset is False
        assert summary.is_strict_subset is False

    def test_summarize_int_sets(self):
        set1 = {1, 2, 3}
        set2 = {2, 3, 4, 5}
        summary = pk.sets.summarize(set1, set2)

        assert isinstance(summary, pk.sets.TwoSetSummary)
        assert isinstance(summary.set1, frozenset)
        assert isinstance(summary.set2, frozenset)
        assert summary.set1 == frozenset(set1)
        assert summary.set2 == frozenset(set2)

        assert summary.union == frozenset({1, 2, 3, 4, 5})
        assert summary.intersection == frozenset({2, 3})
        assert summary.set1_minus_set2 == frozenset({1})
        assert summary.set2_minus_set1 == frozenset({4, 5})
        assert summary.sym_diff == frozenset({1, 4, 5})

        assert summary.jaccard_score == pytest.approx(pk.sets.jaccard(set1, set2))
        assert summary.overlap_score == pytest.approx(pk.sets.overlap(set1, set2))
        assert summary.dice_score == pytest.approx(pk.sets.dice(set1, set2))

        assert summary.is_equal is False
        assert summary.is_disjoint is False
        assert summary.is_subset is False
        assert summary.is_strict_subset is False

    @pytest.mark.parametrize(
        "set1, set2, expected_jaccard, expected_overlap, expected_dice",
        [
            (set(), set(), 1.0, 1.0, 1.0),
            ({"a"}, {"a"}, 1.0, 1.0, 1.0),
            ({"a"}, {"b"}, 0.0, 0.0, 0.0),
            ({"a", "b"}, {"b", "c"}, 1 / 3, 1 / 2, 2 / 4),
        ],
        ids=[
            "empty vs empty",
            "identical singletons",
            "disjoint singletons",
            "overlapping sets",
        ],
    )
    def test_metric_values(
        self,
        set1: set[str],
        set2: set[str],
        expected_jaccard: float,
        expected_overlap: float,
        expected_dice: float,
    ):
        # symmetric checks
        assert pk.sets.jaccard(set1, set2) == pytest.approx(expected_jaccard)
        assert pk.sets.jaccard(set2, set1) == pytest.approx(expected_jaccard)

        assert pk.sets.overlap(set1, set2) == pytest.approx(expected_overlap)
        assert pk.sets.overlap(set2, set1) == pytest.approx(expected_overlap)

        assert pk.sets.dice(set1, set2) == pytest.approx(expected_dice)
        assert pk.sets.dice(set2, set1) == pytest.approx(expected_dice)

    def test_iterable_inputs(self):
        some_list = ["x", "y"]
        some_tuple = ("y", "z")
        some_generator = (c for c in ["y", "z"])

        summary1 = pk.sets.summarize(some_list, some_tuple)
        summary2 = pk.sets.summarize(some_list, some_generator)

        assert summary1.intersection == frozenset({"y"})
        assert summary2.intersection == frozenset({"y"})

        assert pk.sets.jaccard(some_list, some_tuple) == pytest.approx(1 / 3)
        assert pk.sets.overlap(some_list, some_tuple) == pytest.approx(1 / 2)
        assert pk.sets.dice(some_list, some_tuple) == pytest.approx(2 / 4)

    def test_strict_subset_and_subset_flags(self):
        set1 = {1, 2}
        set2 = {1, 2, 3}
        summary = pk.sets.summarize(set1, set2)
        assert summary.is_subset is True
        assert summary.is_strict_subset is True
        assert summary.is_equal is False

        summary_rev = pk.sets.summarize(set2, set1)
        assert summary_rev.is_subset is False
        assert summary_rev.is_strict_subset is False

    def test_equal_flag(self):
        set1 = {1, 2}
        set2 = {1, 2}
        summary = pk.sets.summarize(set1, set2)
        assert summary.is_equal is True
        assert summary.is_subset is True
        assert summary.is_strict_subset is False

        summary_rev = pk.sets.summarize(set2, set1)
        assert summary_rev.is_equal is True
        assert summary_rev.is_subset is True
        assert summary_rev.is_strict_subset is False

    def test_floating_point_edge_cases(self):
        set1 = set(range(1000))
        set2 = set(range(500, 1500))
        jaccard_score = pk.sets.jaccard(set1, set2)
        overlap_score = pk.sets.overlap(set1, set2)
        dice_score = pk.sets.dice(set1, set2)

        assert 0.0 <= jaccard_score <= 1.0
        assert 0.0 <= overlap_score <= 1.0
        assert 0.0 <= dice_score <= 1.0

        eps = sys.float_info.epsilon
        assert dice_score >= jaccard_score - eps

    def test_type_and_immutability(self):
        summary = pk.sets.summarize([1, 2], [2, 3])
        with pytest.raises((AttributeError, TypeError)):
            summary.set1 = frozenset()


class TestUnion:
    def test_basic(self):
        a = {1, 2}
        b = {3}
        c = {2, 4}
        assert pk.sets.union([a, b, c]) == {1, 2, 3, 4}

    def test_empty_input(self):
        assert pk.sets.union([]) == set()

    def test_single_set(self):
        s = {42}
        assert pk.sets.union([s]) == {42}

    def test_overlap(self):
        assert pk.sets.union([{1, 2}, {2, 3}, {3, 1}]) == {1, 2, 3}

    def test_no_mutation_of_inputs(self):
        a = {1, 2}
        b = {3}
        orig_a = a.copy()
        orig_b = b.copy()

        u = pk.sets.union([a, b])

        assert a == orig_a
        assert b == orig_b
        assert u == {1, 2, 3}

    def test_type_preservation(self):
        s1: set[str] = {"a", "b"}
        s2: set[str] = {"b", "c"}
        result = pk.sets.union([s1, s2])
        assert result == {"a", "b", "c"}
        assert all(isinstance(x, str) for x in result)

    def test_iterable_input(self):
        iterable = [{1}, {2, 3}, {3, 4}]
        result = pk.sets.union(iterable)
        assert result == {1, 2, 3, 4}

    def test_chain_flatten_and_union(self):
        data = [{1, 2}, [{3}], (4, {5, 6}), [[{7}]], "abc", 99]

        extracted_sets = [
            item
            for item in pk.seq.flatten(data, atomic_types=(str, set))
            if isinstance(item, set)
        ]
        result = pk.sets.union(extracted_sets)

        assert extracted_sets == [{1, 2}, {3}, {5, 6}, {7}]
        assert result == {1, 2, 3, 5, 6, 7}

    def test_pipe_with_flatten_and_union(self):
        data = [{1, 2}, [{3}], (4, {5, 6}), [[[{7}]]], "ignore", 999]

        def extract_sets(data):
            return (
                item
                for item in pk.seq.flatten(data, atomic_types=(str, set))
                if isinstance(item, set)
            )

        result = pk.fn.pipe(data, [extract_sets, pk.sets.union])

        assert result == {1, 2, 3, 5, 6, 7}


class TestIntersect:
    def test_basic(self):
        a = {1, 2, 3}
        b = {2, 3}
        c = {3}

        result = pk.sets.intersect([a, b, c])

        assert result == {3}

    def test_empty_input(self):
        result = pk.sets.intersect([])
        assert result == set()

    def test_single_set(self):
        s = {42}
        result = pk.sets.intersect([s])
        assert result == {42}

    def test_disjoint_sets(self):
        a = {1, 2}
        b = {3, 4}

        result = pk.sets.intersect([a, b])

        assert result == set()

    def test_overlap(self):
        a = {1, 2, 3}
        b = {2, 3, 4}

        result = pk.sets.intersect([a, b])

        assert result == {2, 3}

    def test_no_mutation(self):
        a = {1, 2, 3}
        b = {2, 3, 4}
        orig_a = a.copy()
        orig_b = b.copy()

        result = pk.sets.intersect([a, b])

        assert a == orig_a
        assert b == orig_b
        assert result == {2, 3}

    def test_type_preservation(self):
        s1: set[str] = {"a", "b", "c"}
        s2: set[str] = {"b", "c", "d"}

        result = pk.sets.intersect([s1, s2])

        assert result == {"b", "c"}
        assert all(isinstance(x, str) for x in result)
