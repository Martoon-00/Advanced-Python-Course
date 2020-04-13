import functools
import io
import sys
import time
import traceback
from contextlib import redirect_stdout
from enum import Enum
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

# First part


class assert_raises:
    def __init__(self, exc):
        self.exc = exc

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert exc_val, "did not raise {}".format(self.exc.__name__)

        return isinstance(exc_val, self.exc)


class closing:
    def __init__(self, res):
        self.res = res

    def __enter__(self):
        return self.res

    def __exit__(self, *exc_info):
        self.res.close()


class log_exceptions:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            exc_info = exc_type, exc_val, exc_tb
            traceback.print_exception(*exc_info, file=sys.stderr)
        return True


class with_context:
    def __init__(self, context_mgr):
        self.context_mgr = context_mgr

    def __call__(self, func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            with self.context_mgr:
                return func(*args, **kwargs)

        return inner

# Second part


class Op(Enum):
    NEXT = ("Ook.", "Ook?")
    PREV = ("Ook?", "Ook.")
    INC = ("Ook.", "Ook.")
    DEC = ("Ook!", "Ook!")
    PRINT = ("Ook!", "Ook.")
    INPUT = ("Ook.", "Ook!")
    START_LOOP = ("Ook!", "Ook?")
    END_LOOP = ("Ook?", "Ook!")


def ook_tokenize(input):
    parts = input.split(" ")
    return [Op(pair) for pair in zip(parts[::2], parts[1::2])]


def ook_eval(source, *, memory_limit=2**16):
    code = ook_tokenize(source)
    memory = [0] * memory_limit
    mp = 0

    loops_stack = []
    op_i = 0
    while op_i < len(code):
        op = code[op_i]

        if op == Op.NEXT:
            mp += 1
        if op == Op.PREV:
            mp -= 1
        if op == Op.INC:
            memory[mp] += 1
        if op == Op.DEC:
            memory[mp] -= 1
        if op == Op.PRINT:
            sys.stdout.write(chr(memory[mp]))
        if op == Op.INPUT:
            memory[mp] = ord(sys.stdin.read(1))

        if op == Op.START_LOOP:
            if memory[mp] == 0:
                while code[op_i] != Op.END_LOOP:
                    op_i += 1
            else:
                loops_stack.append(op_i)

        if op == Op.END_LOOP:
            if memory[mp] != 0:
                op_i = loops_stack[-1]
            else:
                loops_stack.pop()

        op_i += 1


# Asserts
assert_msg = "Don't send!!!"

# with assert_raises(ValueError):
#     "foobar".split("")

# with assert_raises(ValueError):
#     pass

# with assert_raises(ValueError):
#     raise TypeError

# with closing(open("example.txt")) as handle:
#     copy = handle


def f():
    with log_exceptions():
        {}["foobar"]
    return 42

handle = io.StringIO()


@with_context(redirect_stdout(handle))
def f():
    print("Hello world!")
f()
assert handle.getvalue() == "Hello world!\n", assert_msg


true_res = "[<Op.INPUT: ('Ook.', 'Ook!')>, <Op.PRINT: ('Ook!', 'Ook.')>]"
assert str(ook_tokenize("Ook. Ook! Ook! Ook.")) == true_res, assert_msg

test_str = "\
Ook. Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. \
Ook. Ook. Ook. Ook. Ook! Ook? Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. \
Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook? Ook! Ook! Ook? Ook! Ook? Ook. \
Ook! Ook. Ook. Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. \
Ook. Ook. Ook! Ook? Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook? \
Ook! Ook! Ook? Ook! Ook? Ook. Ook. Ook. Ook! Ook. Ook. Ook. Ook. Ook. Ook. Ook. \
Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook. Ook! Ook. Ook. Ook. Ook. Ook. \
Ook. Ook. Ook! Ook. Ook. Ook? Ook. Ook? Ook. Ook? Ook. Ook. Ook. Ook. Ook. Ook. \
Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook? Ook? Ook. Ook. Ook. \
Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook? Ook! Ook! Ook? Ook! Ook? Ook. Ook! Ook. \
Ook. Ook? Ook. Ook? Ook. Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. \
Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook? Ook? Ook. Ook. Ook. \
Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. \
Ook. Ook? Ook! Ook! Ook? Ook! Ook? Ook. Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook. \
Ook? Ook. Ook? Ook. Ook? Ook. Ook? Ook. Ook! Ook. Ook. Ook. Ook. Ook. Ook. Ook. \
Ook! Ook. Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook. \
Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! \
Ook! Ook. Ook. Ook? Ook. Ook? Ook. Ook. Ook! Ook."

handle = io.StringIO()


@with_context(redirect_stdout(handle))
def g():
    ook_eval(test_str)
g()
assert handle.getvalue() == "Hello World!", assert_msg
