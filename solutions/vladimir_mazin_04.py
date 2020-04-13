import gzip
import bz2
import random
from collections import defaultdict


# First part
def capwords(s, sep=None):
    cap_words = map(lambda part: part.capitalize(), s.split(sep))
    join_sep = sep if sep is not None else " "
    return join_sep.join(cap_words)


def cut_suffix(s, suff):
    if not suff:
        return s

    cut_s, _, rest = s.rpartition(suff)
    return cut_s if not rest else s


def boxed(s, fill, pad):
    spaced_s = f" {s} "
    box_width = len(spaced_s) + 2 * pad
    box_border = fill * box_width
    centered_s = spaced_s.center(box_width, fill)
    return "\n".join([box_border, centered_s, box_border])


def find_all(s, sub_s):
    res = []
    found_i = s.find(sub_s, 0)
    while found_i != -1:
        res.append(found_i)
        found_i = s.find(sub_s, found_i + 1)
    return res


def common_prefix(first, second, *args):
    prefix = []
    for chars in zip(first, second, *args):
        if all(map(lambda ch: ch == chars[0], chars)):
            prefix.append(chars[0])
        else:
            return ''.join(prefix)


# Second part
def reader(filename, **kwargs):
    if filename.endswith(".gz"):
        return gzip.open(filename, **kwargs)
    if filename.endswith(".bz2"):
        return bz2.open(filename, **kwargs)
    return open(filename, **kwargs)


def parse_shebang(filename):
    first_line = open(filename).readline()
    if first_line.startswith("#!"):
        return first_line[2:].strip()


# Third part
def words(handle):
    return [w for line in handle for w in line.split(" ")]


def transition_matrix(words_list):
    res = {}
    for i in range(len(words_list) - 2):
        key = words_list[i], words_list[i + 1]
        if key in res:
            res[key].append(words_list[i + 2])
        else:
            res[key] = [words_list[i + 2]]
    return res


def markov_chain(words_list, matrix, n):
    if n == 0:
        return ""

    fst = random.choice(words_list)
    if n == 1:
        return fst
        
    snd = random.choice(words_list)
    res = [fst, snd]

    for _ in range(n - 2):
        fst, snd = snd, random.choice(matrix.get((fst, snd), words_list))
        res.append(snd)

    return " ".join(res)


def snoop_says(filename, n):
    file = open(filename, encoding="utf-8")
    words_list = words(file)
    matrix = transition_matrix(words_list)
    return markov_chain(words_list, matrix, n)


# Asserts
assert_msg = "Dont send!!!"

assert capwords("foo,,bar,", sep=",") == "Foo,,Bar,", assert_msg
assert capwords(" foo \nbar\n") == "Foo Bar", assert_msg

assert cut_suffix("foobar", "bar") == "foo", assert_msg
assert cut_suffix("foobar", "boo") == "foobar", assert_msg

assert find_all("abracadabra", "a") == [0, 3, 5, 7, 10], assert_msg

assert common_prefix("abra", "abracadabra", "abrasive") == "abra", assert_msg
assert common_prefix("abra", "foobar") == "", assert_msg

assert parse_shebang("./example1.txt") == "/bin/sh", assert_msg
assert parse_shebang("./example2.txt") == "/usr/bin/env python -v", assert_msg
