# First part
def peel(cls):
    return {attr for attr in dir(cls) if not attr.startswith("_")}


class implements:
    def __init__(self, interface):
        self.interface = interface

    def __call__(self, cls):
        diff = peel(self.interface) - peel(cls)
        assert not diff, "Attributes " + str(diff) + " not implemented"
        return cls


# Second
class Expr:
    def __call__(self, **context):
        pass

    def d(self, wrt):
        pass

    def __repr__(self):
        return str(self)

    def __neg__(self):
        return Product(Const(-1), self)

    def __pos__(self):
        return self

    def __add__(self, other):
        return Sum(self, other)

    def __sub__(self, other):
        return Sum(self, -other)

    def __mul__(self, other):
        return Product(self, other)

    def __truediv__(self, other):
        return Fraction(self, other)

    def __pow__(self, power):
        return Power(self, power)

    @property
    def is_constexpr(self):
        return False

    @property
    def simplified(self):
        return Expr()


class Const(Expr):
    def __init__(self, value):
        self.value = value

    def __call__(self, **context):
        return self.value

    def d(self, wrt):
        return Const(0)

    def __str__(self):
        return str(self.value)

    @property
    def is_constexpr(self):
        return True

    @property
    def simplified(self):
        return self


class Var(Expr):
    def __init__(self, name):
        self.name = name

    def __call__(self, **context):
        return context[self.name]

    def d(self, wrt):
        return Const(1) if self.name == wrt.name else Const(0)

    def __str__(self):
        return self.name

    @property
    def is_constexpr(self):
        return False

    @property
    def simplified(self):
        return self

C = Const
V = Var

class BinOp(Expr):
    sign = None

    def __init__(self, expr1, expr2):
        self.expr1, self.expr2 = expr1, expr2

    def __str__(self):
        return "({} {} {})".format(self.sign, self.expr1, self.expr2)

    @property
    def is_constexpr(self):
        return self.expr1.is_constexpr and self.expr2.is_constexpr

    @property
    def simplified(self):
        if self.expr1.is_constexpr:
            if self.expr2.is_constexpr:
                return C(self())
            else:
                return self.__class__(C(self.expr1()),
                                      self.expr2.simplified)
        else:
            if self.expr2.is_constexpr:
                return self.__class__(self.expr1.simplified,
                                      Const(self.expr2()))
            else:
                return self.__class__(self.expr1.simplified,
                                      self.expr2.simplified)


class Sum(BinOp):
    sign = "+"

    def __call__(self, **context):
        return self.expr1(**context) + self.expr2(**context)

    def d(self, wrt):
        return self.expr1.d(wrt) + self.expr2.d(wrt)


class Product(BinOp):
    sign = "*"

    def __call__(self, **context):
        return self.expr1(**context) * self.expr2(**context)

    def d(self, wrt):
        return self.expr1 * self.expr2.d(wrt) + self.expr1.d(wrt) * self.expr2


class Fraction(BinOp):
    sign = "/"

    def __call__(self, **context):
        return self.expr1(**context) / self.expr2(**context)

    def d(self, wrt):
        num = self.expr1.d(wrt) * self.expr2 - self.expr1 * self.expr2.d(wrt)
        denum = self.expr2 * self.expr2
        return num / denum


class Power(Expr):
    sign = "**"

    def __init__(self, base, exp):
        assert exp.is_constexpr, "Exp '{}' should be const-expr".format(exp)
        self.base = base
        self.exp = exp

    def __call__(self, **context):
        return self.base(**context) ** self.exp()

    def d(self, wrt):
        return self.base.d(wrt) * self.exp * self.base ** (self.exp - C(1))

    def __str__(self):
        return "(** {} {})".format(self.base, self.exp)

    @property
    def is_constexpr(self):
        return self.base.is_constexpr and self.exp.is_constexpr

    @property
    def simplified(self):
        if self.base.is_constexpr:
            return C(self())
        else:
            return self.base.simplified ** self.exp.simplified


# Third part
def newton_raphson(expr, initial, threshold=1e-4):
    prev = initial
    expr_d = expr.d(Var("x"))
    next = prev - expr(x=prev) / expr_d(x=prev)
    while abs(next - prev) > threshold:
        prev = next
        next = prev - expr(x=prev) / expr_d(x=prev)

    return next

# Asserts
assert_msg = "Don't send!!!"


class AbstractBase:
    def some_method(self):
        pass


class Base(AbstractBase):
    def some_other_method(self):
        pass


class Closeable(Base):
    def close(self):
        pass


assert peel(Closeable) == {'close', 'some_method', 'some_other_method'}, \
       assert_msg


class Closeable:
    def close(self):
        pass


@implements(Closeable)
class FileReader:
    def close(self):
        self.file.close()


class Noop:
    pass

####
assert C(42)() == 42, assert_msg
assert C(42).d(V("x"))() == 0, assert_msg
assert V("x")(x=42) == 42, assert_msg
assert V("x").d(V("x"))() == 1, assert_msg
assert V("x").d(V("y"))() == 0, assert_msg

x = V("x")
assert (x + x * x).d(x)(x=42) == 85, assert_msg
assert (x * (x + C(2)))(x=42) == 1848, assert_msg

assert (x * V("y") / (C(42) + x)).d(x)(x=42, y=24) == 0.14285714285714285, \
       assert_msg


assert ((x * V("y")) / (C(42) + x)).d(V("y"))(x=42, y=24) == 0.5, assert_msg

assert ((V("x") / C(4)) ** C(2))(x=42) == 110.25, assert_msg
assert ((V("x") / C(4)) ** C(2)).d(V("x"))(x=42) == 5.25, assert_msg

assert str((x + x * x).d(x)) == "(+ 1 (+ (* x 1) (* 1 x)))", assert_msg
assert str(x * (x + C(2))) == "(* x (+ x 2))", assert_msg
assert str((x / C(4)) ** C(2)) == "(** (/ x 4) 2)", assert_msg

assert str((C(1) - V("x")) ** C(3) + V("x")) == "(+ (** (+ 1 (* -1 x)) 3) x)", assert_msg

expr = (V("x") + C(-1)) ** C(3) + V("x")
zero = newton_raphson(expr, 0.5, threshold=1e-4)
assert str(expr) == "(+ (** (+ x -1) 3) x)", assert_msg
assert (zero, expr(x=zero)) == (0.31767219617165293, -7.855938122247608e-13), assert_msg

assert not (V("x") + C(1)).is_constexpr, assert_msg
assert not (C(1) + C(42) * V("x")).d(V("x")).is_constexpr, assert_msg
assert (C(1) + C(42) * C(2)).is_constexpr, assert_msg

assert str((C(1) + C(42) * C(2)).simplified) == "85", assert_msg

true_res = "(+ (* 1 y) (/ 84 x))"
assert str((C(1) * V("y") + C(42) * C(2) / V("x")).simplified) == true_res, \
       assert_msg
