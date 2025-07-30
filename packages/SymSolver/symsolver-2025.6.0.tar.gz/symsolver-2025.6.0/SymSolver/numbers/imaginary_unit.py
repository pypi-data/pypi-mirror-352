"""
File Purpose: the imaginary unit, i == 1j == sqrt(-1).
"""

from .abstract_numbers import AbstractNumber
from ..abstracts import (
    simplify_op, expand_op,
)
from ..errors import PatternError
from ..initializers import initializer_for, INITIALIZERS
from ..tools import (
    equals, int_equals,
    is_real_number, is_integer,
    Singleton,
    caching_attr_simple,
    Binding,
)
binding = Binding(locals())

from ..defaults import DEFAULTS, ZERO, ONE, MINUS_ONE


''' --------------------- ImaginaryUnit --------------------- '''

class ImaginaryUnit(AbstractNumber, Singleton):
    '''the imaginary unit, i.'''
    def evaluate(self):
        '''returns 1j, because it is the number which self represents.'''
        return 1j

    def _repr_contents(self):
        '''returns an empty tuple; just represent self as ImaginaryUnit().'''
        return ()

    def __str__(self):
        return DEFAULTS.IMAGINARY_UNIT_STR

    __hash__ = Singleton.__hash__

IUNIT = ImaginaryUnit()

''' --------------------- ImaginaryUnitPower --------------------- '''

class ImaginaryUnitPower(AbstractNumber):
    '''the imaginary unit raised to a power.
    Can be simplified via the rules implied by i**2 == -1.
    '''
    def __init__(self, exponent):
        self.exponent = exponent

    def evaluate(self):
        '''returns (1j)**self.exponent.'''
        return 1j ** self.exponent

    def _repr_contents(self, **kw):
        '''returns contents to put inside 'ImaginaryUnitPower()' in repr for self.'''
        return [f'exponent={self.exponent}']

    def __str__(self):
        i = DEFAULTS.IMAGINARY_UNIT_STR
        ibase = f'{i}' if len(i)==1 else f'{{{i}}}'
        return f'{ibase}^{{{self.exponent}}}'

    def __eq__(self, b):
        '''returns self == b.
        True means self == b, but False could just mean we don't know the answer.
        Does not consider the identity i**2 == -1; use self.apply('simplify_id') first, instead.
        Also does not consider the identity i**1 == i. use self.apply('simplify_id') first, instead.
        '''
        if isinstance(b, type(self)):
            return equals(self.exponent, b.exponent)
        else:
            return False

    @caching_attr_simple
    def __hash__(self):
        return hash((type(self), self.exponent))

    @staticmethod
    def integer_power_id(exponent):
        '''return result of simplifying i**exponent, where exponent is an integer power.
        raise PatternError if that is impossible (due to exponent not being an integer.)
        The rule is i**2 = -1.
        So, i^(4n)=+1, i^(4n+1)=+i, i^(4n+2)=-1, i^(4n+3)=-i, for any integer n.
        '''
        if not is_integer(exponent):
            raise PatternError('integer_power_id(exponent) with exponent not an integer')
        exp_mod4 = exponent % 4   # i**2 == -1 --> i**exp == i**(exp % 4)
        # check simple cases (0,1,2,3) first because they are the most likely:
        if exp_mod4 == ZERO:
            return ONE
        elif exp_mod4 == ONE:
            return IUNIT
        elif exp_mod4 == 2:
            return MINUS_ONE
        elif exp_mod4 == 3:
            return -IUNIT


''' --------------------- SIMPLIFY for ImaginaryUnitPower --------------------- '''

@expand_op(ImaginaryUnitPower, alias='_simplify_id')  # also an expand op so that we can do it during expand.
@simplify_op(ImaginaryUnitPower, alias='_simplify_id')
def _imaginary_unit_power_simplify_id(self, **kw__None):
    '''returns sign * i**N, with N from 0 (inclusive) to 2 (exclusive), and sign may be 1 or -1.
    if is_real_number(N), N must be able to handle operations: N % 4, and maybe N < 2.
    (regular python builtin real numbers work just fine.)
    '''
    exponent = self.exponent
    if is_real_number(exponent):
        try:
            return ImaginaryUnitPower.integer_power_id(exponent)
        except PatternError:  # exponent not an integer.
            pass  # handled below
        # get exp mod 4
        exp_mod4 = exponent % 4   # i**2 == -1 --> i**exp == i**(exp % 4)
        if exp_mod4 < 2:
            if exp_mod4 == exponent:
                return self  # return self, exactly, to help indicate nothing was changed.
            else:
                return self._new(exp_mod4)
        else:
            return -self._new(exp_mod4 - 2)
    return self  # return self, exactly, to help indicate nothing was changed.
