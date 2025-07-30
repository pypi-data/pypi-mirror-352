"""
File Purpose: replace things with units
"""

from .common_unit_bases import UNIT_BASES
from ..attributors import attributor
from ..abstracts import SubbableObject, is_number, is_subbable, _equals0
from ..basics import Symbol, Power
from ..tools import (
    Binding,
)
binding = Binding(locals())


''' --------------------- Convenience --------------------- '''

@attributor
def unitize(x, *, numbers=True, **kw):
    '''returns units for x, or x if can't determine units and x is not numeric.
    returns x.unitize(**kw) if available,
    else UNIT_BASES.one if x is a number (i.e. non-SymbolicObject or numeric-only SymbolicObject)
        (if x equals 0, use UNIT_BASES.zero instead)
    else x.

    numbers: bool, default True
        whether to unitize if x is a number; if False return x.
        True --> if is_number(x), return UNITS_BASES.one if x is nonzero, else UNITS_BASES.zero.
    '''
    try:
        x_unitize = x.unitize
    except AttributeError:
        if numbers and is_number(x):
            return _unitize_number(x)
        else:
            return x
    else:
        return x_unitize(numbers=numbers, **kw)

def _unitize_number(x):
    '''units for the number x.
    return UNIT_BASES.zero if x==0, else UNIT_BASES.one.
    '''
    return UNIT_BASES.zero if _equals0(x) else UNIT_BASES.one


''' --------------------- Unitize --------------------- '''

with binding.to(Symbol):
    @binding
    def unitize(self, **kw__None):
        '''returns self.units_base if it isn't None, else self (to indicate failure to unitize).'''
        ub = self.units_base
        return self if ub is None else ub

with binding.to(SubbableObject):
    @binding
    def unitize(self, *, numbers=True, **kw):
        '''returns units for self, or self if can't determine units and self is not numeric.
        numbers: bool, default True
            whether to convert numbers into units.
        '''
        if numbers and is_number(self):
            return _unitize_number(self)
        elif not is_subbable(self):
            return self
        # loop through subbable terms in self, calling term.unitize(**kw)
        _subbable_only = kw.pop('_subbable_only', False)  # << sub to numbers during loop, too.
        def unitize_rule(term):
            return unitize(term, numbers=numbers, **kw)  # << not term.unitize(); term might be non-subbable.
        return self._substitution_loop(unitize_rule, _subbable_only=_subbable_only, numbers=numbers, **kw)

with binding.to(Power):
    @binding
    def unitize(self, *, exponents=False, exp_numbers=False, **kw):
        '''returns units for self.base, raised to the self.exponent (don't convert exp into units).
        exponents: bool, default False
            whether to unitize non-numeric exponents.
            False --> never unitize any exponents.
            True --> unitize exponents only if they are non-numeric, i.e. not is_number(exponent).
        exp_numbers: bool, default False
            value for the 'numbers' kwarg of unitize for the exponent, if unitizing the exponent.
        '''
        ubase = unitize(self.base, exponents=exponents, exp_numbers=exp_numbers, **kw)
        exp = self.exponent
        if exponents and not is_number(exp):
            exp = unitize(exp, exponents=exponents, numbers=exp_numbers, exp_numbers=exp_numbers, **kw)
        return self._new(ubase, exp)
