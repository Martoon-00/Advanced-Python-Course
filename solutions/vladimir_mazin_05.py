from collections import namedtuple, OrderedDict, defaultdict, Counter
import functools

# First part
Factor = namedtuple("Factor", ["elements", "levels"])


def factor(elements):
    levels = OrderedDict()
    for e in elements:
        if e not in levels:
            levels[e] = len(levels)
    coded_elements = [levels[e] for e in elements]
    return Factor(coded_elements, levels)


def lru_cache(func=None, *, maxsize=64):
    # with braces
    if func is None:
        return lambda func: lru_cache(func, maxsize=maxsize)

    # without braces
    cache = OrderedDict()
    hits = 0
    misses = 0

    cache_info_elements = ["hits", "misses", "maxsize", "currsize"]
    CacheInfo = namedtuple("CacheInfo", cache_info_elements)

    @functools.wraps(func)
    def inner(*args, **kwargs):
        nonlocal hits, misses
        key = args + tuple(sorted(kwargs.items()))
        if key not in cache:
            value = func(*args, **kwargs)
            misses += 1
            if len(cache) == maxsize:
                cache.popitem(last=False)
            cache[key] = value
        else:
            hits += 1
            cache.move_to_end(key)
        return cache[key]

    def cache_info():
        return CacheInfo(hits, misses, maxsize, len(cache))

    def cache_clear():
        nonlocal hits, misses
        cache.clear()
        hits = 0
        misses = 0

    inner.cache_info = cache_info
    inner.cache_clear = cache_clear
    return inner


def group_by(iterable, func):
    d = defaultdict(list)
    for it in iterable:
        d[func(it)].append(it)
    return d


def invert(input_dict):
    d = defaultdict(set)
    for k, v in input_dict.items():
        d[v].add(k)
    return d


# Second part
def export_graph(graph, labels, filename):
    lines = ["graph {\n"]
    visited = set()
    for node in graph:
        lines.append(f'{node} [label="{labels[node]}"]\n')
        for to_node in graph[node]:
            if to_node not in visited:
                lines.append("{} -- {}\n".format(node, to_node))
        visited.add(node)
    lines.append("}")

    open(filename, "w").writelines(lines)


# Asserts
assert_msg = "Don't send!"
assert str(factor(["a", "a", "b"])) == \
       ("Factor"
        "("
        "elements=[0, 0, 1], "
        "levels=OrderedDict([('a', 0), ('b', 1)])"
        ")"), assert_msg

assert str(factor(["a", "b", "c", "b", "a"])) == \
       ("Factor"
        "("
        "elements=[0, 1, 2, 1, 0], "
        "levels=OrderedDict([('a', 0), ('b', 1), ('c', 2)])"
        ")"), assert_msg


@lru_cache
def fib(n):
    return n if n <= 1 else fib(n - 1) + fib(n - 2)


assert fib(10) == 55, assert_msg
assert str(fib.cache_info()) == \
       "CacheInfo(hits=8, misses=11, maxsize=64, currsize=11)", assert_msg

assert dict(group_by(["foo", "boo", "barbra"], len)) == \
       {3: ['foo', 'boo'], 6: ['barbra']}, assert_msg

assert dict(invert({"a": 42, "b": 42, "c": 24})) == \
       {24: {'c'}, 42: {'a', 'b'}}, assert_msg
