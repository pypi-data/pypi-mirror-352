"""
File Purpose: misc. tools related to numbers

[TODO] sqrt & divisibility for Rational numbers.
    (right now, we just pretend they are never perfect 
"""
from ..abstracts import _equals0
from ..attributors import attributor
from ..tools import (
    isqrt_if_square, is_integer,
    equals,
)
from ..defaults import ONE


@attributor
def sqrt_if_square(x):
    '''return sqrt(x) if we can get exact result without introducing any roots, else None.
    Examples:
        sqrt_if_square(9) --> 3
        sqrt_if_square(16 * Y^2) --> 6 * Y
        sqrt_if_square(7) --> None
        sqrt_if_square(25 * Y) --> None
    returns x.sqrt_if_square() if possible,
    otherwise if is_integer(x) return isqrt_if_square(x),
    else return None
    '''
    try:
        x_sqrt_if_square = x.sqrt_if_square
    except AttributeError:
        if is_integer(x):
            return isqrt_if_square(x)
        else:
            return None
    else:
        return x_sqrt_if_square()

@attributor
def divide_if_divisible(x, divide_by):
    '''return x / divide_by if x is definitely divisible by divide_by, else None.
    returns x.divide_if_divisible(divide_by) if possible,
    otherwise 1 if x == divide_by,
    otherwise result if remainder==0, from (result, remainder) = divmod(x, divide_by), if possible,
    else, return None.
    '''
    try:
        x_divide_if_divisible = x.divide_if_divisible
    except AttributeError:
        pass  # handled after the 'else' block
    else:
        return x_divide_if_divisible(divide_by)
    # << if we reach this line, x doesn't have divide_if_divisible method.
    if equals(x, divide_by):
        return ONE
    try:
        result, remainder = divmod(x, divide_by)
    except TypeError:
        return None
    else:
        if _equals0(remainder):
            return result
        else:
            return None
