"""
File Purpose: simplifying units
"""

from .common_unit_bases import UNIT_BASES
from .units_tools import is_unit
from ..abstracts import (
    simplify_op, CommutativeOperation,
)
from ..basics import (
    Power, AbstractProduct, Product, Sum,
)
from ..initializers import INITIALIZERS
from ..tools import (
    Dict, equals,
    dichotomize,
    caching_attr_simple_if,
    Binding,
)
from ..defaults import DEFAULTS

binding = Binding(locals())


''' --------------------- is_unit --------------------- '''

with binding.to(Power):
    @binding
    def is_unit(self):
        '''returns whether base is a unit, since (unit)^(exponent) is a unit.'''
        return is_unit(self.base)

with binding.to(AbstractProduct):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def is_unit(self):
        '''returns whether all factors are units. Product of units is a unit.'''
        return all(is_unit(factor) for factor in self)


''' --------------------- count units --------------------- '''

with binding.to(Sum):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def _count_units(self):
        '''returns number of summands in self which are units.'''
        return sum((1 if is_unit(summand) else 0) for summand in self)


''' --------------------- Simplify --------------------- '''

@simplify_op(Sum, alias='simplify_units', order=-1)
def _sum_simplify_units(self, **kw__None):
    '''combine units in Sum. Checks for sum of same unit: [x] + [x] --> [x].
    Also checks for adding unit 0: [x] + [0] --> [x].'''
    ucount = self._count_units()
    if ucount == 0:  # if no units, nothing to simplify.
        return self  # return self, exactly, to help indicate nothing was changed.
    U_ZERO = UNIT_BASES.zero
    if ucount == 1:  # if only 1 unit, can only simplify if it is 0.
        result = [summand for summand in self if summand is not U_ZERO]
        if len(result) == len(self):
            return self  # return self, exactly, to help indicate nothing was changed.
        else:
            return self._new(*result)
    # else, more than 1 unit.
    result = []
    any_changes = False
    _already_added_units = Dict(equals=equals)  # "slow dict"; not hashing; use equals for key comparison.
    for summand in self:
        if is_unit(summand):
            if summand is U_ZERO or summand in _already_added_units:  # [0], or [x] with [x] already in result
                any_changes = True
                continue  # this unit already appears in result!
            else:
                result.append(summand)
                _already_added_units[summand] = None  # using Dict as a Set; the value is unimportant.
        else:
            result.append(summand)
    if not any_changes:
        return self  # return self, exactly, to help indicate nothing was changed.
    return self._new(*result)

@simplify_op(AbstractProduct, alias='simplify_units')
def _abstract_product_simplify_units(self, **kw__None):
    '''remove any instances of the identity unit (UNIT_BASES.one) in AbstractProduct.
    Also, if ALL factors are units, return Product of factors instead of AbstractProduct of factors.
    Also, if any factors are the unit 0, return the unit 0.
    '''
    U_ZERO = UNIT_BASES.zero
    for factor in self:
        if factor is U_ZERO:
            return U_ZERO
    U_ONE = UNIT_BASES.one
    factors = [factor for factor in self if factor is not U_ONE]  # remove U_ONE.
    if (not isinstance(self, Product)) and all(is_unit(factor) for factor in factors):
        return INITIALIZERS.product(*factors)
    if len(factors) == len(self):
        return self  # return self, exactly, to help indicate nothing was changed.
    return self._new(*factors)

@simplify_op(Power, alias='simplify_units')
def _power_simplify_units(self, **kw__None):
    '''if self.base is UNIT_BASES.one or UNIT_BASES.zero, return self.base.'''
    base = self.base
    return base if ((base is UNIT_BASES.one) or (base is UNIT_BASES.zero)) else self
