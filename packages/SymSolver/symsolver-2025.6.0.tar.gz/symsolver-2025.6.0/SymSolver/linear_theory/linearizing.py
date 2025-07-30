"""
File Purpose: linearizition of AbstractOperation objects.

- Notions of "zeroth order", "first order", "higher order"
- ability to linearize. (replace x with x0 + x1, where x0 is constant and x1 is "small")

[TODO] tell AbstractOperators not to linearize..
[TODO] tell LinearOperation to linearize just the operand.
"""

from .linear_theory_tools import (
    get_o0, get_o1,
    get_order, _order_docs,
    MIXED_ORDER,
)
from ..attributors import attributor
from ..abstracts import (
    AbstractOperation, IterableSymbolicObject, OperationContainer,
    SubbableObject, is_subbable,
    is_constant,
)
from ..basics import (
    Sum, AbstractProduct, Power,
    Symbol, # << for assume_o0_constant. Other Symbol-related definitions in linear_symbols.py
)
from ..errors import LinearizationPatternError, LinearizationNotImplementedError
from ..precalc_operators import (
    GenericOperation, LinearOperation,
    DotOperation,
    is_operator, is_linear_operator,
)
from ..tools import (
    default_sum,
    int_equals,
    alias_to_result_of, caching_attr_simple_if,
    Binding, format_docstring,
)
from ..defaults import DEFAULTS, ZERO, ONE

binding = Binding(locals())


''' --------------------- Aliases --------------------- '''

AbstractOperation.o0 = alias_to_result_of('get_o0', doc='''0th order form of self. (alias to self.get_o0()).''')
AbstractOperation.o1 = alias_to_result_of('get_o1', doc='''1st order form of self. (alias to self.get_o1()).''')
AbstractOperation.order = alias_to_result_of('get_order', doc='''"order" or self. (alias to self.get_order()).''') 


''' --------------------- Convenience Functions --------------------- '''

@attributor
def linearize(x, keep0=False):
    '''return linearized form of x, via x.linearize(keep0=keep0)
    if x.linearize isn't available,
        if keep0=False (default), return x.
        otherwise, return 0.

    keep0: bool, default False
        whether to keep the 0'th order terms.
        x.o1 == x.linearize(keep0=True) - x.o0
    '''
    try:
        x_linearize = x.linearize
    except AttributeError:
        if keep0:
            return x
        else:
            return ZERO
    else:
        return x_linearize()


''' --------------------- LINEARIZE for AbstractOperation, OperationContainer --------------------- '''

with binding.to(AbstractOperation):
    @binding
    def linearize(self, keep0=False):
        '''linearizes self (see: linear_theory). i.e., returns self.get_o1().
        If keep0, returns self.get_o0() + self.get_o1() instead.
        '''
        if keep0:
            return self.get_o0() + self.get_o1()
        else:  # default
            return self.get_o1()

with binding.to(OperationContainer):
    @binding
    def linearize(self, keep0=False):
        '''linearizes self (see: linear_theory) by applying linearize to each object in self.'''
        return self.apply_operation(lambda x: linearize(x, keep0=keep0))


''' --------------------- get_o0, get_o1 --------------------- '''

# # # for SUM: (x+y)_0 --> x0 + y0; (x+y)_1 --> x1 + y1 # # #
with binding.to(Sum):
    @binding
    def get_o0(self):
        '''return Sum of 0th order values of each summand.'''
        return self._new(*(get_o0(summand) for summand in self))

    @binding
    def get_o1(self):
        '''return Sum of 1st order values of each summand.'''
        o1s = (get_o1(summand) for summand in self)
        return self._new(*(o1 for o1 in o1s if o1 is not ZERO))

# # # for ANY PRODUCT: (x*y)_0 --> x0 * y0; (x*y)_1 --> x1 * y0 + x0 * y1 # # #
with binding.to(AbstractProduct):
    @binding
    def get_o0(self):
        '''return new product, of 0th order values of each factor.'''
        return self._new(*(get_o0(factor) for factor in self))

    @binding
    def get_o1(self):
        '''returns the 1st order value which remains after linearizing and subtracting 0th order value from self.
        The rule is: (f*g*h)_1 = f1*g0*h0 + f0*g1*h0 + f0*g0*h1, where '*' is a product.
        '''
        result = []
        factors = list(self)
        for i, f in enumerate(factors):
            f1 = get_o1(f)
            if f1 is not ZERO:
                summand_factors = tuple((f1 if i==j else get_o0(g)) for j, g in enumerate(factors) )
                result.append(self._new(*summand_factors))
        return self.sum(*result)

# # # for POWER: (x**N)_0 --> (x0**N); (x**N)_1 --> N * (x0**(N-1)) * x1 # # #
with binding.to(Power):
    @binding
    def get_o0(self):
        '''return new Power, of 0th order values of base and exponent.'''
        return self._new(get_o0(self.base), get_o0(self.exp))

    @binding
    def get_o1(self):
        '''returns the 1st order value which remains after linearizing and subtracting 0th order value from self.
        The rule is: (x^n)_1 --> n x0^(n-1) x1.
        The rule comes from the taylor expansion: x^n ~= x0^n + n*x0^(n-1) x1.
        The rule assumes commutativity between x0 and x1.
        '''
        if not is_constant(self.exp):
            raise LinearizationNotImplementedError(f'{type(self).__name__}.get_o1() for Power with non-constant exponent.')
        x, N = self.base, self.exp
        x0 = get_o0(x)
        x1 = get_o1(x)
        if x1 is ZERO:  # quick check to keep things simple later.
            return ZERO
        x0_pow_N_minus_1 = x0 if int_equals(N, ONE+ONE) else self._new(x0, N - ONE)
        return self.product(N, x0_pow_N_minus_1, x1)

# # # for OPERATION CONTAINER: get_oX --> get_oX for each contained object. (X=0 or 1) # # #
with binding.to(OperationContainer):
    @binding
    def get_o0(self):
        '''returns 0th order (see: linear_theory) form of self by applying get_o0 to each object in self.'''
        return self.apply_operation(get_o0)

    @binding
    def get_o1(self):
        '''returns 1st order (see: linear_theory) form of self by applying get_o1 to each object in self.'''
        return self.apply_operation(get_o1)


# # # for GENERIC OPERATION: f(x)_0 --> f(x0); f(x)_1 --> crash # # #
with binding.to(GenericOperation):
    @binding
    def get_o0(self):
        '''returns the 0th order value of self, e.g. self.operator(get_o0(self.operand)).'''
        return self._new_from_operand(get_o0(self.operand))

    @binding
    def get_o1(self):
        '''raises NotImplementedError because we don't know how to get the first order value for a generic operation.
        subclasses may provide implementations. E.g. LinearOperation provides one implementation example.
        '''
        raise LinearizationNotImplementedError(f'{type(self).__name__}.get_o1()')

# # # for LINEAR OPERATION: f(x)_1 --> f(x1) # # #
with binding.to(LinearOperation):
    @binding
    def get_o1(self):
        '''returns the 1st order value which remains after linearizing and subtracting 0th order value from self.
        Since self is a LinearOperation, the rule is: f(x)_1 --> f(x1).
        '''
        return self._new_from_operand(get_o1(self.operand))

    # note: for get_o0, inherits GenericOperation.get_o0()

# # # for DOT OPERATION (see docs; there are a few cases) # # #
with binding.to(DotOperation):
    @binding
    def get_o0(self):
        '''returns the 0th order value of self'''
        (t1, f), u = self
        if is_operator(t1):
            return super().get_o0()
        else:
            return self._new(self.operator._new(get_o0(t1), f), get_o0(u))

    @binding
    def get_o1(self):
        '''returns the 1st order value which remains after linearizing and subtracting 0th order value from self.
        If self.operator is a linear operator, the rule will be:
            (g dot f)(u) --> (g dot f)(u1),   OR
            (v dot f)(u) --> (v1 dot f)(u0) + (v0 dot f)(u1),
            depending on whether the first term is an operator (g) or not an operator (v).
        otherwise, raise LinearizationNotImplementedError.
        '''
        operator = self.operator
        if is_linear_operator(operator):
            (t1, f), u = self
            if is_operator(t1):
                return LinearOperation.get_o1(self)
            else:
                result0 = self._new(operator._new(get_o1(t1), f), get_o0(u))
                result1 = self._new(operator._new(get_o0(t1), f), get_o1(u))
                return self.sum(result0, result1)
        else:
            errmsg = f'{type(self).__name__}.get_o1(), with is_linear_operator(self.operator)==False.'
            raise LinearizationNotImplementedError(errmsg)


''' --------------------- order --------------------- '''

# # # ORDER FOR SUM # # #
with binding.to(Sum):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    @format_docstring(orderdocs=_order_docs)
    def get_order(self):
        '''returns order of self.
        returns:
            None if all summands are order None;
            0 if at least one summand is order 0, and all summands are order 0 or None;
            N>0 if all summands are order N  (e.g. 1 if all summands are order 1)
            MIXED_ORDER (probably math.nan) if any two summands with non-None order have different order.

        {orderdocs}
        '''
        iter_summands = iter(self)
        result = get_order(next(iter_summands))
        for summand in iter_summands:
            order = get_order(summand)
            if order != result:
                if result is None:
                    result = order
                elif (result == ZERO) and (order is None):  # intentially '==' not 'equals', since order is just an integer.
                    pass  # this case is allowed
                else:
                    return MIXED_ORDER
        return order

# # # ORDER FOR ANY PRODUCT # # #
with binding.to(AbstractProduct):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    @format_docstring(orderdocs=_order_docs)
    def get_order(self):
        '''returns order of self.
        returns:
            None if all factors are order None,
            else: sum of orders of factors, treating order=None as order=0.

        {orderdocs}
        '''
        return default_sum(*(get_order(t) for t in self), default=(None, ZERO))

# # # ORDER FOR POWER # # #
with binding.to(Power):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    @format_docstring(orderdocs=_order_docs)
    def get_order(self):
        '''returns order of self (self == base raised to exponent)
        
        calculated via:
            if exponent has order not equal to 0 or None, raise LinearizationPatternError. Otherwise,
            if order of base is None, return None,
            else return  exponent * (order of base).

        {orderdocs}
        '''
        exponent = self.exp
        if get_order(exponent) not in (None, ZERO):
            raise LinearizationPatternError('order of a Power is only defined when exponent has order 0 or None!')
        order_base = get_order(self.base)
        if order_base is None:
            return None
        else:
            return exponent * order_base

# # # ORDER FOR GENERIC OPERATION # # #
with binding.to(GenericOperation):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    @format_docstring(orderdocs=_order_docs)
    def get_order(self):
        '''returns order of self.
        returns order of self.operand if that is 0 or None, else raise LinearizationNotImplementedError.

        {orderdocs}
        '''
        result = get_order(self.operand)
        if result in (None, ZERO):
            return result
        else:
            raise LinearizationNotImplementedError(f'{type(self).__name__}.get_order() when get_order(self.operand) is not 0 or None.')


with binding.to(LinearOperation):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    @format_docstring(orderdocs=_order_docs)
    def get_order(self):
        '''returns order of self.
        just returns order of self.operand, since self is a LinearOperation.

        {orderdocs}
        '''
        return get_order(self.operand)


with binding.to(DotOperation):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    @format_docstring(orderdocs=_order_docs)
    def get_order(self):
        '''returns order of self.
        if self.operator is not a linear operator, return super().get_order().
        otherwise, check if t1 is an operator (where self == (t1 dot f)(u));
            if it is an operator, return LinearOperation.get_order(self).
            otherwise, check order of t1 and u.

        {orderdocs}
        '''
        if is_linear_operator(self.operator):
            (t1, f), u = self
            if is_operator(t1):
                return LinearOperation.get_order(self)
            else:
                return default_sum(get_order(t1), get_order(u), default=(None, ZERO))
        else:
            return super().get_order()


''' --------------------- ASSUME o0 CONSTANT --------------------- '''

with binding.to(Symbol):
    @binding
    def assume_o0_constant(self):
        '''if self is order 0, return self.as_constant(). else return self.'''
        if self.order == ZERO:
            return self.as_constant()
        else:
            return self

with binding.to(SubbableObject):
    @binding
    def assume_o0_constant(self, **kw):
        '''assumes all 0th order quantities in self are constant.
        I.e., replaces all o0 quantities in self with constant versions of themselves.
        kwargs go to self._iter_substitution_terms.
        '''
        if not is_subbable(self):
            return self
        # loop through subbable terms in self, calling term.assume_o0_constant(...).
        def assume_o0_constant_rule(term):
            return term.assume_o0_constant(**kw)
        return self._substitution_loop(assume_o0_constant_rule, **kw)
