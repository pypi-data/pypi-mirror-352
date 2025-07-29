# encoding:utf-8
import math
from maths_add.except_error import decorate


class Pi(object):
    def __init__(self):
        pass

    def get_num(self):
        return math.pi


class E(object):
    def __init__(self):
        pass

    def get_num(self):
        return math.e


class Tau(object):
    def __init__(self):
        pass

    def get_num(self):
        return math.tau


class Inf(object):
    def __init__(self):
        pass

    def get_num(self):
        return math.inf


class Nan(object):
    def __init__(self):
        pass

    def get_num(self):
        return math.nan

@decorate
def 获取小数点后的位数(f):
    if type(f) != float:
        raise TypeError("The f must be a float.")
    f = str(f)
    fl = f.split(".")
    return len(fl[1])

@decorate
isTwomNum=lambda x: return x%2==0