import functools


# First part
def union(*args):
    return functools.reduce(lambda x, y: x | y, args, set())


def digits(num):
    if num == 0:
        return [0]
        
    def step(list, cur_num):
        if cur_num == 0:
            return list
        list.append(cur_num % 10)
        return step(list, cur_num // 10)

    return list(reversed(step([], num)))


def lcm(*args):
    def gcd(n, m):
        while n != m:
            if n > m:
                n = n - m
            else:
                m = m - n
        return n

    def lcm_two(n, m):
        return n * m / gcd(n, m)

    return functools.reduce(lambda res, cur: lcm_two(res, cur), args)


def compose(*args):
    def compose_two(f, g):
        return lambda x: g(f(x))
    return functools.reduce(compose_two, reversed(args))


# Second part
def once(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if not inner.called:
            inner.ret_val = func(*args, **kwargs)
            inner.called = True
        return inner.ret_val
    inner.called = False
    return inner


def trace_if(p):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if p(*args, **kwargs):
                print(func.__name__, args, kwargs)
            return func(*args, **kwargs)
        return inner
    return decorator


def n_times(n):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            for i in range(n):
                func(*args, **kwargs)
        return inner
    return decorator


# Third and forth parts
def project():
    def register(func=None, *, depends_on=None):
        depends_on = depends_on or []

        # with brackets
        if func is None:
            return lambda func: register(func, depends_on=depends_on)

        # without brackets
        register.registered.append(func.__name__)
        register.get_all = lambda: register.registered[:]
        register.name_to_func[func.__name__] = func
        func.depends_on = depends_on
        func.get_dependencies = lambda: func.depends_on[:]

        @functools.wraps(func)
        def inner():
            for dep in func.get_dependencies():
                if dep not in register.satisfied_dependencies:
                    register.name_to_func[dep]()
                    register.satisfied_dependencies.add(dep)
            register.satisfied_dependencies.add(func.__name__)
            return func()
        return inner
    register.registered = []
    register.name_to_func = {}
    register.satisfied_dependencies = set()
    return register

# Asserts
assert_msg = "Dont send!!!"

assert union({1, 2, 3}, {10}, {2, 6}) == {1, 2, 3, 6, 10}, assert_msg

assert digits(0) == [0] and digits(1914) == [1, 9, 1, 4], assert_msg

assert lcm(100500, 42) == 703500 and lcm(*range(2, 40, 8)) == 19890, assert_msg

test_f = compose(lambda x: 2 * x, lambda x: x + 1, lambda x: x % 9)
assert test_f(42) == 14, assert_msg


@once
def initialize_settings():
    print("Settings initialized.")
    return {"token": 42}


@trace_if(lambda x, y, **kwargs: kwargs.get("integral"))
def div(x, y, integral=False):
    return x // y if integral else x / y


@n_times(3)
def do_something():
    print("Something is going on!")


register = project()


@register
def do_something():
    print("doing something")


@register(depends_on=["do_something"])
def do_other_thing():
    print("doing other thing")

@register(depends_on=["do_something", "do_other_thing"])
def do_third_thing():
    print("doing third thing")

assert register.get_all() == ["do_something", "do_other_thing", "do_third_thing"], assert_msg
assert do_something.get_dependencies() == [], assert_msg
assert do_other_thing.get_dependencies() == ["do_something"], assert_msg
