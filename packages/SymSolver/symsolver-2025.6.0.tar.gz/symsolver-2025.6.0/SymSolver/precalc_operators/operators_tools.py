"""
File Purpose: provide convenient methods for the precalc_operators subpackage.
"""

from ..attributors import attributor
from ..basics import (
    get_factors,
)
from ..errors import PatternError
from ..tools import (
    dichotomize,
)


''' --------------------- Convenience Functions --------------------- '''

@attributor
def is_operator(x):
    '''returns whether x is an operator, by returning x.is_operator() if possible else False.'''
    try:
        x_is_operator = x.is_operator
    except AttributeError:
        return False
    else:
        return x_is_operator()

@attributor
def is_linear_operator(x):
    '''returns whether x is a linear operator, by returning x.is_linear_operator() if possible else False.'''
    try:
        x_is_linear_operator = x.is_linear_operator
    except AttributeError:
        return False
    else:
        return x_is_linear_operator()

def nonop_yesop_get_factors(x):
    '''returns (non-operator factors of x, operator factors of x)'''
    factors = get_factors(x)
    return dichotomize(factors, lambda f: not is_operator(f))