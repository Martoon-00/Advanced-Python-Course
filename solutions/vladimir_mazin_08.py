import collections
import functools
import socket
from contextlib import contextmanager
from itertools import count, islice, tee, groupby, chain, repeat, takewhile, \
                      zip_longest


# First part


def ilen(iterable):
    return sum(1 for _ in iterable)


def find(iterable, p):
    try:
        return next(filter(p, iterable))
    except StopIteration:
        raise ValueError("not found")


def chunked(iterable, n):
    it1, it2 = tee(islice(iterable, n), 2)
    while list(it1):
        yield it2
        it1, it2 = tee(islice(iterable, n), 2)
        

def rle(iterable):
    return ((item, ilen(it)) for (item, it) in groupby(iterable))


# Second part


def intersperse(sep, iterable):
    it = iter(iterable)
    yield next(it)

    for item in it:
        yield sep
        yield item


class peekable:  # todo
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self._is_peek_ok = False

    def __next__(self):
        if not self._is_peek_ok:
            return next(self.iterator)
        else:
            self._is_peek_ok = False
            return self._peek

    def peek(self):
        if not self._is_peek_ok:
            self._peek = next(self.iterator)
            self._is_peek_ok = True
        return self._peek


def padded(iterable, def_elem, n):
    return islice(chain(iter(iterable), repeat(def_elem, n)), n)


def sliding(iterable, n, step):  # todo
    it = iter(iterable)
    item = list(islice(it, step))
    common_part = list(islice(it, n - step))
    while len(item) + len(common_part) == n:
        yield chain(item, common_part)
        item = list(islice(common_part,
                           len(common_part) - (n - step),
                           len(common_part)))
        common_part = list(islice(it, step))


# Asserts
assert_msg = "Don't send!!!"
assert list(intersperse(-42, range(3))) == [0, -42, 1, -42, 2], assert_msg

it = intersperse(-42, count())
assert next(it) == 0, assert_msg
assert next(it) == -42, assert_msg

it = peekable([1, 2, 3])
assert it.peek() == 1, assert_msg
assert it.peek() == 1, assert_msg
assert next(it) == 1, assert_msg
assert it.peek() == 2, assert_msg
