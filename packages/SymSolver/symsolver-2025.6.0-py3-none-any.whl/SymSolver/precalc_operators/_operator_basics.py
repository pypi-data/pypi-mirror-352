"""
File Purpose: AbstactOperators can be added to each other, or multiplied by non-operators.
E.g. for AbstractOperator objects f, g; non-AbstractOperator-object c:
    f + g is well-defined; it is the operator: (f + g)(x) = f(x) + g(x).
    c * f is well-defined; it is the operator: (c * f)(x) = c * f(x)
    f * g is not well-defined.
    f**2 might be well-defined, but SymSolver doesn't treat it (yet). (Use f(f) instead.)
"""

from .abstract_operators import (
    AbstractOperator, CompositeOperator,
)
from .linear_operators import LinearOperator
from .operators_tools import (
    is_operator, nonop_yesop_get_factors,
    is_linear_operator,
)
from ..abstracts import (
    _equals0,
    init_modifier,
)
from ..basics import (
    Sum, Product, Power,
)
from ..errors import OperatorMathError
from ..tools import (
    equals,
    caching_attr_simple_if,
    is_integer,
    Binding,
)
from ..defaults import DEFAULTS, ONE

binding = Binding(locals())


''' --------------------- IS_OPERATOR --------------------- '''

with binding.to(AbstractOperator):
    @binding
    def is_operator(self):
        '''returns True, because self is an operator.'''
        return True

with binding.to(Sum):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def is_operator(self):
        '''returns whether any summand in self is an operator.'''
        return any(is_operator(summand) for summand in self)

with binding.to(Product):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def is_operator(self):
        '''returns whether any factor in self is an operator.'''
        return any(is_operator(factor) for factor in self)

with binding.to(Power):
    @binding
    def is_operator(self):
        '''returns whether base is an operator (from self = base ** exponent)'''
        return is_operator(self.t1)


''' --------------------- IS_LINEAR_OPERATOR --------------------- '''

with binding.to(LinearOperator):
    @binding
    def is_linear_operator(self):
        '''returns True, because self is a linear operator.'''
        return True

with binding.to(Sum):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def is_linear_operator(self):
        '''returns whether all operator summands in self are linear operators; False if no operators in self.'''
        any_ops = False
        for summand in self:
            if is_operator(summand):
                any_ops = True
                if not is_linear_operator(summand):
                    return False
        return any_ops


''' --------------------- INIT_MODIFIERS --------------------- '''

@init_modifier(Product)
def _init_product_operator_check(self, *terms, **kw):
    '''if more than one term is an operator, raise OperatorMathError.'''
    iter_terms = iter(terms)
    for term in iter_terms:
        if is_operator(term):
            break
    else:  # didn't break
        return
    for term in iter_terms:  # continuing where we left off
        if is_operator(term):
            raise OperatorMathError("Cannot create Product of two or more operators.")

@init_modifier(Power)
def _init_power_operator_check(self, base, exponent, **kw):
    '''if base or exponent is an operator, raise OperatorMathError.'''
    if is_operator(base):
        if not equals(exponent, ONE):
            if is_integer(exponent) and exponent > 0:
                errmsg = ('Repeated operator calls as exponentiation not yet implemented. '
                          'Use f(f(f(...))) notation instead.')
                raise NotImplementedError(errmsg)
            else:
                raise OperatorMathError('Operator raised to a power other than a positive integer.')
    if is_operator(exponent):
        if not _equals0(base):
            raise OperatorMathError('Exponentiation by an operator is not allowed.')


''' --------------------- CALL for Sum, Product, Power --------------------- '''

# # # CALL SUM -- CALL FOR OPERATOR SUMMANDS; MULTIPLY FOR OTHER SUMMANDS # # #
with binding.to(Sum):
    @binding
    def __call__(self, g):
        '''calls self on g.
        operator summands will be called at g.
        non-operator summands will be multiplied by g.
        E.g. with f an operator, (7 + f)(g) --> 7 * g + f(g).

        Note: g might be an operator as well.
        '''
        result = []
        for summand in self:
            if is_operator(summand):
                result.append(summand(g))
            else:
                result.append(summand * g)
        return self._new(*result)

# # # CALL PRODUCT -- CALL OPERATOR FACTOR; MULTIPLY OTHERWISE. # # #
with binding.to(Product):
    @binding
    def __call__(self, g):
        '''calls self on g.
        operator factor will be called at g.
        if no factors are operators, multiply by g instead.

        Note: g might be an operator as well.
        '''
        nonop_factors, yesop_factors = nonop_yesop_get_factors(self)
        if len(yesop_factors) == 1:
            op = yesop_factors[0]
            op_at_g = op(g)
            return self._new(*nonop_factors, op_at_g)
        else:
            return self * g

# # # CALL POWER -- CALL OPERATOR BASE IF POWER == 1; MULTIPLY OTHERWISE. # # #
with binding.to(Power):
    @binding
    def __call__(self, g):
        '''calls self on g.
        if self.exponent == 1, calls base on g.
        otherwise multiplies by g.
        '''
        if equals(self.t2, ONE):
            return self._new(self.t1.__call__(g), self.t2)
        else:
            return self.__mul__(g)