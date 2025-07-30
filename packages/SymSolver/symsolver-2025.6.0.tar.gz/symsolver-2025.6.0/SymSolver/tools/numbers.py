"""
File Purpose: tools related to numerical values / value comparisons
"""

import math
import numbers

from ..errors import warn

from ..defaults import ZERO


''' --------------------- Classify --------------------- '''

def is_integer(x):
    '''return whether x is an integer.
    by first checking isinstance(x, int),
    if that's False, check x.is_integer() if it exists,
    else return False.
    '''
    if isinstance(x, int):
        return True
    else:
        try:
            return x.is_integer()
        except AttributeError:
            return False

def is_number(x):
    '''return whether x is a number.
    returns x.is_number() if possible, else True.
    '''
    try:
        x_is_number = x.is_number
    except AttributeError:
        return True
    else:
        return x_is_number()

def is_real_number(x):
    '''returns whether x is a real number.
    by first checking isinstance(x, complex); if so, return x.imag == 0.
    otherwise, return x.is_real_number() if it exists,
    else return False.
    '''
    if isinstance(x, numbers.Complex):  # note: real numbers are subclasses of numbers.Complex, in python.
        return x.imag == ZERO   # we can use '==' because we know x is a Complex number.
    else:
        try:
            x_is_real_number = x.is_real_number
        except AttributeError:
            return False
        else:
            return x_is_real_number()

def is_real_negative_number(x):
    '''returns whether x is a real negative number. Equivalent: is_real_number(x) and x < 0'''
    return is_real_number(x) and x < ZERO


''' --------------------- Infinity --------------------- '''

class _Infinity():
    '''mathematical infinity or negative infinity, in the sense of comparisons.

    compares equal to other _Infinity.

    Rather than initialize using this class, use the infinity() function.
    Or, choose your desired already-initialized infinity: POS_INFINITY or NEG_INFINITY
    '''
    def __init__(self, positive=True):
        self.positive = positive
    def __eq__(self, x):
        return isinstance(x, _Infinity) and x.positive==self.positive
    def __gt__(self, x):
        return (self.positive) and (self != x)
    def __ge__(self, x):
        return (self.positive) or (self == x)
    def __lt__(self, x):
        return (not self.positive) and (self != x)
    def __le__(self, x):
        return (not self.positive) or (self == x)
    def __repr__(self):
        return ('+' if self.positive else '-')+'Infinity'
    def __pos__(self):
        return self
    def __neg__(self):
        return infinity(not self.positive)

    def __hash__(self):
        return hash((type(self), self.positive))

POS_INFINITY = _Infinity(True)
NEG_INFINITY = _Infinity(False)

POS_INF = PLUS_INF = PLUS_INFINITY = INFINITY = INF = POS_INFINITY
NEG_INF = NEG_INF = MINUS_INF = MINUS_INFINITY = NEG_INFINITY

def infinity(positive=True):
    '''return POS_INFINITY if positive else NEG_INFINITY.'''
    return POS_INFINITY if positive else NEG_INFINITY


''' --------------------- Numerical Tricks --------------------- '''

def isqrt(n):
    '''return the integer square root of x, i.e. the largest integer n such that n**2 <= x.
    raise ValueError if n is negative.
    '''
    try:
        math_isqrt = math.isqrt
    except AttributeError:
        warn('math.isqrt not found (Python < 3.8?) falling back to older isqrt implementation.')
        math_isqrt = None
    if math_isqrt is None:
        return int(n**0.5)
    else:
        return math_isqrt(int(n))  # raises ValueError if n is negative.

def isqrt_and_check(n):
    '''return (isqrt(n), whether n**2 == x)
    isqrt(n) is the largest integer n such that n**2 <= x.
    '''
    result = isqrt(n)
    check = (result**2 == n)
    return (result, check)

def isqrt_if_square(n):
    '''return positive x such that x**2 == n, if that is possible. else return None.'''
    if not is_integer(n):
        return None
    try:
        result, check = isqrt_and_check(n)
    except ValueError:  # n is negative.
        return None
    return result if check else None
