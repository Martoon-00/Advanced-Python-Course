# First part
def compose(f, g):
    return lambda *args, **kwargs: f(g(*args, **kwargs))


def constantly(ret_val):
    return lambda *args, **kwargs: ret_val


def flip(func):
    return lambda *args, **kwargs: func(*reversed(args), **kwargs)


def curry(func, *args_1):
    return lambda *args_2, **kwargs: func(*(args_1 + args_2), **kwargs)


# Second part
def enumerate(xs, start=0):
    nums = range(start, start + len(xs))
    return zip(nums, xs)


def which(predicate, xs):
    return [i for i in range(len(xs)) if predicate(xs[i])]


def all(predicate, xs):
    return len(xs) == len(list(filter(predicate, xs)))


def any(predicate, xs):
    return len(list(filter(predicate, xs))) > 0


# Third part
OK, ERROR = "OK", "ERROR"


def char(ch):
    def inner(input):
        if not input:
            return ERROR, "eof", input
        elif input[0] != ch:
            return ERROR, "expected " + ch + " got " + input[0], input
        else:
            return OK, ch, input[1:]
    return inner


def any_of(s):
    def inner(input):
        if not input:
            return ERROR, "eof", input
        elif input[0] not in s:
            return ERROR, "expected any of " + s + " got " + input[0], input
        else:
            return OK, input[0], input[1:]
    return inner


def chain(*args):
    def inner(input):
        parsed = []
        cur_input = input
        for arg in args:
            tag, res, leftover = arg(cur_input)
            if tag == OK:
                parsed += res
                cur_input = leftover
            else:
                return ERROR, res, input
        return OK, parsed, cur_input
    return inner


def choice(*args):
    def inner(input):
        for arg in args:
            res = arg(input)
            if res[0] == OK:
                return res
        return ERROR, "none matched", input
    return inner


def many(parser, empty=True):
    def inner(input):
        parsed = []
        leftover = input
        while True:
            tag, res, leftover = parser(leftover)
            if tag == OK:
                parsed.append(res)
            elif not parsed and not empty:
                return ERROR, res, input
            else:
                return OK, parsed, leftover
    return inner


def skip(parser):
    def inner(input):
        tag, res, leftover = parser(input)
        return tag, None if tag == OK else res, leftover
    return inner


def transform(p, f):
    def inner(input):
        tag, res, leftover = p(input)
        return tag, f(res) if tag == OK else res, leftover
    return inner


def sep_by(p, sep):
    return chain(p, many(transform(chain(sep, p), lambda xs: xs[1])))


def parse(parser, input):
    tag, res, leftover = parser(input)
    assert tag == OK and not leftover, (res, leftover)
    return res
