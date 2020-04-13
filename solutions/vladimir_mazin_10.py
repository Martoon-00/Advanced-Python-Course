import functools
import hypothesis.strategies as st
import pytest
import random
import sys
import tempfile

from collections.abc import Iterator
from hypothesis import given
from itertools import islice
from sut import parse_shebang, assert_raises, with_context, sliding, factor, \
                chunked, common_prefix


# First part
class TestParseShebang:
    @pytest.mark.parametrize("input, expected", [
        ("#!abcde\n12345", "abcde"),
        ("abcde\n12345", None),
        ("abcd#! e\n12345", None)
    ])
    def test_parse_shebang_all(self, input, expected):
        with tempfile.NamedTemporaryFile(mode="w") as file:
            file.write(input)
            file.flush()
            if expected is None:
                assert parse_shebang(file.name) is None
            else:
                assert parse_shebang(file.name) == expected


class TestAssertRaises:
    def test_assert_raises_omit_exception(self):
        with assert_raises(ValueError):
            raise ValueError()

    def test_assert_raises_raise_exception(self):
        with pytest.raises(ZeroDivisionError):
            with assert_raises(TypeError):
                x = 1 / 0

    def test_assert_raises_no_exception_raised(self):
        with pytest.raises(AssertionError):
            with assert_raises(NameError):
                nop = "Nothing happens"


class TestWithContext:
    def test_with_context(self):
        @with_context(assert_raises(ZeroDivisionError))
        def test_with_context_helper():
            return 1 / 0

        test_with_context_helper()


class TestSliding:
    def test_sliding_type(self):
        slided = sliding(range(4), 2, 1)
        assert isinstance(slided, Iterator)

    @pytest.mark.parametrize("input_args, expected", [
        ((range(10), 3, 2), [[0, 1, 2], [2, 3, 4], [4, 5, 6], [6, 7, 8]]),
        ((range(0), 2, 1), []),
        ((range(4), 0, 2), [])
    ])
    def test_sliding_examples(self, input_args, expected):
        slided = list(map(list, sliding(*input_args)))
        assert slided == expected

    def test_sliding_must_be_hypothesys_test(self):
        l, n, step = 4, 2, 1
        slided = list(map(list, sliding(range(l), n, step)))

        must_be_len = 1 + (l - n) / step  # 3
        assert len(slided) == must_be_len


# Second part
class TestFactor:
    @given(st.text())
    def test_factor(self, initial):
        coded = factor(initial)
        levels = list(coded.levels)
        decoded = "".join(levels[e] for e in coded.elements)
        assert initial == decoded


iterables = st.one_of(st.tuples(st.integers(0, 50)),
                      st.tuples(st.booleans()),
                      st.lists(st.floats(-50, 50)),
                      st.text(),
                      st.sets(st.integers(0, 50))
                      )


class TestChunked:
    @pytest.mark.parametrize("iterable", [(1, 2), [1, 2], {1, 2}, {1: 2}])
    def test_chunked_not_only_iterators(self, iterable, n=2):
        next(chunked(iterable, n))  # check if exception is not raised

    @given(iterables, st.integers(1, 5))
    def test_chunked_simple(self, iterable, n):
        must_be_iterable = []
        for part in chunked(iterable, n):
            for e in part:
                must_be_iterable.append(e)

        assert must_be_iterable == list(iterable)

    @given(iterables, st.integers(1, 10))
    def test_chunked_compare_with_original(self, iterable, n):
        def chunked_original(iterable, n):
            acc = []
            for item in iterable:
                if len(acc) == n:
                    yield iter(acc[:])
                    acc.clear()
                acc.append(item)
            if acc:
                yield iter(acc)

        part_pairs = zip(chunked(iter(iterable), n),
                         chunked_original(iter(iterable), n))
        for part1, part2 in part_pairs:
            for e1, e2 in zip(part1, part2):
                assert e1 == e2


class TestCommonPrefix:
    @given(st.lists(st.text("abc"), 3))
    def test_common_prefix_really_common(self, iters):
        prefix = common_prefix(*iters)
        for it in iters:
            assert "".join(islice(it, len(prefix))) == prefix

    @given(st.lists(st.text("abc"), 2))
    def test_common_prefix_really_max(self, iters):
        prefix = common_prefix(*iters)
        n = len(prefix)

        def exist_not_equal_first_elements(iters):
            try:
                first_elems = next(zip(*iters))
            except StopIteration:
                return True

            first = first_elems[0]
            return any(first != elem for elem in first_elems)

        iters_without_prefix = map(lambda it: islice(it, n, None), iters)
        assert exist_not_equal_first_elements(iters_without_prefix)

