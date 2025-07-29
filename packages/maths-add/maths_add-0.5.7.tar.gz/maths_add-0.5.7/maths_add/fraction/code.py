from fractions import Fraction
from maths_add import factors_and_multiples_numbers, special_numbers
from maths_add.except_error import decorate


def ERROR(args, typeList):
    for arg in args:
        is_valid = False
        for t in typeList:
            if isinstance(arg, t):
                is_valid = True
                break
        if not is_valid:
            raise TypeError("The arg must be one of the following types: " + str(typeList) + ".")


@decorate
class Mixed(object):
    def __init__(self, w, f):
        ERROR(w, [int])
        ERROR(f, [Fraction])
        self.w = w
        self.f = f
        self.value = w + f

    def __del__(self):
        print("对象被销毁")

    def __str__(self):
        return f"Mixed(w={self.w}, f={self.f})"

    def __repr__(self):
        return f"Mixed(w={self.w}, f={self.f})"

    def __pos__(self):
        return Mixed(+self.value)

    def __neg__(self):
        return Mixed(-self.value)

    def __abs__(self):
        return Mixed(abs(self.value))

    def __add__(self, other):
        return Mixed(self.value + other.value)

    def __radd__(self, other):
        return Mixed(self.value + other)

    def __sub__(self, other):
        return Mixed(self.value - other.value)

    def __rsub__(self, other):
        return Mixed(self.value - other)

    def __mul__(self, other):
        return Mixed(self.value * other.value)

    def __rmul__(self, other):
        return Mixed(self.value * other)

    def __truediv__(self, other):
        return Mixed(self.value / other.value)

    def __rtruediv__(self, other):
        return Mixed(self.value / other)

    def __floordiv__(self, other):
        return Mixed(self.value // other.value)

    def __rfloordiv__(self, other):
        return Mixed(self.value // other)

    def __mod__(self, other):
        return Mixed(self.value % other.value)

    def __rmod__(self, other):
        return Mixed(self.value % other)

    def __pow__(self, other):
        return Mixed(self.value ** other.value)

    def __rpow__(self, other):
        return Mixed(self.value ** other)

    def __iadd__(self, other):
        self.value += other.value
        return self

    def __isub__(self, other):
        self.value -= other.value
        return self

    def __imul__(self, other):
        self.value *= other.value
        return self

    def __itruediv__(self, other):
        self.value /= other.value
        return self

    def __ifloordiv__(self, other):
        self.value //= other.value
        return self

    def __imod__(self, other):
        self.value %= other.value
        return self

    def __eq__(self, other):
        return self.w == other.w and self.f == other.f

    def __ne__(self, other):
        return self.w != other.w or self.f != other.f

    def __lt__(self, other):
        if self.w < other.w:
            return True
        elif self.w == other.w:
            if self.f < other.f:
                return True
            else:
                return False
        else:
            return False

    def __gt__(self, other):
        if self.w > other.w:
            return True
        elif self.w == other.w:
            if self.f > other.f:
                return True
            else:
                return False
        else:
            return False

    def get_m(self):
        return str(self.w) + str(self.f)


def __init__(self):
    pass

@decorate
def fzx(self, f):
    ERROR(f,[Fraction])
    x = f.numerator / f.denominator
    return x

@decorate
def xfz(self, x):
    ERROR(x,[float])
    f = Fraction(x)
    return f

Hf = type("Hf", (), {"__init__": __init__, "fzx": fzx, "xfz": xfz})


@decorate
def get_f(a, b):
    ERROR((a, b), [int, float, Fraction])
    if type(a) == float or type(b) == float:
        al = special_numbers.获取小数点后的位数(a)
        bl = special_numbers.获取小数点后的位数(b)
        nl = max(al, bl)
        a *= pow(10, nl)
        b *= pow(10, nl)
    f = Fraction(a, b)
    return f, (f.numerator, f.denominator)


@decorate
def find_a_common_denominator(a, b):
    ERROR((a, b), [Fraction])
    c = factors_and_multiples_numbers.the_Smallest_Same_multiples(a.denominator, b.denominator)
    aList = {"numerator": a.numerator * c / a.denominator, "denominator": c}
    bList = {"numerator": b.numerator * c / b.denominator, "denominator": c}
    return aList, bList


@decorate
def improper_to_mixed(f):
    ERROR(f, [Fraction])
    # 计算整数部分
    whole_part = f.numerator // f.denominator
    # 计算分数部分
    remaining_fraction = f - whole_part
    if remaining_fraction == 0:
        return str(whole_part)
    elif whole_part == 0:
        return str(f)
    else:
        return str(whole_part) + str(remaining_fraction)


@decorate
def mixed_to_improper(whole, f):
    ERROR(whole, [int])
    ERROR(f, [Fraction])
    numerator = f.numerator
    numerator += whole * f.denominator
    fn = Fraction(numerator, f.denominator)
    return fn
