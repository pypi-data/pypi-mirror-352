"""
File Purpose: Power
See also: power
"""
from .sum import Sum
from ..initializers import initializer_for, INITIALIZERS
from ..abstracts import (
    BinarySymbolicObject, AbstractOperation, SimplifiableObject, SubbableObject,
    simplify_op, expand_op,
    _equals0, is_nonsymbolic,
    _simplyfied,
    _abstract_math,
)
from .basics_tools import (
    get_base_and_power, get_factors,
    gcf,
    copy_if_possible,
)
from ..tools import (
    equals,
    dichotomize,
    is_integer,
    apply,
    Binding,
)
from ..defaults import DEFAULTS, ONE, ZERO

binding = Binding(locals())


class Power(BinarySymbolicObject, AbstractOperation,
            SimplifiableObject, SubbableObject):
    '''Exponentiation operation e.g. x**2.'''
    def __init__(self, base, power, **kw):
        super().__init__(base, power, **kw)

    @property
    def OPERATION(self):
        '''returns the operation which self represents: exponentiation.
        I.e. returns a function f(base, exp) --> base ** exp.
        '''
        return lambda base, exp: base ** exp

    base = property(lambda self: self.t1, doc='''base, from self= base ** exp''')
    exp = property(lambda self: self.t2, doc='''exp, from self= base ** exp''')
    expo = exponent = exp

    def _equals0(self):
        '''returns whether self == 0.'''
        return _equals0(self.t1)

    def get_reciprocal(self):
        '''returns reciprocal of self.'''
        new_expo = -self.t2
        if new_expo is ONE:
            return self.t1
        else:
            return self._new(self.t1, new_expo)

    def get_base_and_power(self):
        '''returns base, power for self. I.e. (self[0], self[1])'''
        return self.t1, self.t2

    def gcf(self, b):
        '''return (gcf= the "greatest" common factor of self and b, self/gcf, b/gcf).
        gcf(x**2, x**-3) == (x**-3, x**5, 1)    # if the exponents can be compared (via '<'),
        gcf(x**-3, x**2) == (x**-3, 1, x**2)    #   use the term with the smallest exponent as the gcf.
        gcf(x**y, x**z) == (x**y, 1, x**(z-y))  # if '<' is not supported between the exponents,
        gcf(x**z, x**y) == (x**z, 1, x**(y-z))  #   use the first term as the gcf.
        '''
        if equals(self, b):
            return (self, 1, 1)
                                                         # example corresponds to gcf((x * y)**5, (k * y)**2)
        bbase, bpower = get_base_and_power(b)            # e.g. ((k * y), 2)
        sbase, spower = self.t1, self.t2                 # e.g. ((x * y), 5)
        gbase, sbaserem, bbaserem = gcf(sbase, bbase)    # e.g. (y, x, k)
        if gbase == 1:
            return (1, self, b)   # gcf is 1; we can't do any good simplifications.
        # gcf is not 1. Deal with exponents.
        try:
            gexp = min(spower, bpower)               # e.g. 2
        except TypeError:   # can't evaluate "spower < bpower"
            gexp = spower   # so we just choose spower.
        sexp = spower - gexp                         # e.g. 3
        bexp = bpower - gexp                         # e.g. 0
        gg = gbase ** gexp                           # e.g. y**2
        ss = (sbaserem ** spower) * (gbase ** sexp)  # e.g. x**5 * y**3
        bb = (bbaserem ** bpower) * (gbase ** bexp)  # e.g. k**2 * y**0
        return (gg, ss, bb)                          # e.g. (y**2, x**5 * y**3, k**2)

@initializer_for(Power)
def power(base, exponent, *, simplify_id=False, **kw):
    '''returns Power representing base ** exponent.
    This just means return Power(base, exponent, **kw).

    if simplify_id and base or exponent is 0 or 1, does the appropriate simplification:
        0^x=0, 1^x=1, x^0=1, x^1=x. Doesn't simplify 0^0.
    '''
    if simplify_id:
        return powered(base, exponent, **kw)
    else:
        return Power(base, exponent, **kw)

def powered(base, exponent, **kw):
    '''returns exponentiation of the args provided.
    Usually this just means INITIALIZERS.power(base, exponent, **kw).
    However, if base or exponent is 0 or 1, does the appropriate simplification:
        0^x=0, 1^x=1, x^0=1, x^1=x. Doesn't simplify 0^0.
    '''
    if is_integer(base):
        if base==ONE:
            return ONE
        elif base==ZERO and not _equals0(exponent):
            return ZERO
    if is_integer(exponent):
        if exponent==ONE:
            return base
        elif exponent==ZERO and not _equals0(base):
            return ONE
    return INITIALIZERS.power(base, exponent, simplify_id=False, **kw)


''' --------------------- Arithmetic: Exponentiation --------------------- '''

def _pow_quickcheck(self, b):
    '''return (if a check condition was satisfied, result else None)
    if b == 1, return (True, copy_if_possible(self))
    if b == 0, return 1
    else, return (False, None).
    '''
    if equals(b, 1):
        return (True, copy_if_possible(self))
    elif _equals0(b):
        return (True, 1)
    else:
        return (False, None)

def _rpow_quickcheck(self, b):
    '''return (if a check condition was satisfied, result else None)
    if b == 1, return (True, 1)
    if b == 0, return (True, 0)
    else, return (False, None).
    '''
    if equals(b, 1):
        return (True, 1)
    elif _equals0(b):
        return (True, 0)
    else:
        return (False, None)

with binding.to(Power):
    @binding
    @_abstract_math
    def __pow__(self, b):
        '''return self ** b, but a bit nicer than just power(self, b):
        If b == 1, return copy_if_possible(self). If b == 0, return 1.
        Otherwise return self._new(self[0], self[1]*b).
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        check, result = _pow_quickcheck(self, b)
        return result if check else self._new(self.t1, self.t2 * b)

    @binding
    @_abstract_math
    def __rpow__(self, b):
        '''return b ** self, but a bit nicer than just power(b, self):
        If b == 1, return 1. If b == 0, return 0.
        Otherwise return self._new(b, self).
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        check, result = _rpow_quickcheck(self, b)
        return result if check else self._new(b, self)

with binding.to(AbstractOperation):
    @binding
    @_abstract_math
    def __pow__(self, b):
        '''return self ** b, but a bit nicer than just power(self, b):
        If b == 1, return copy_if_possible(self). If b == 0, return 1.
        Otherwise return self.power(self, b).
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        check, result = _pow_quickcheck(self, b)
        return result if check else self.power(self, b)

    @binding
    @_abstract_math
    def __rpow__(self, b):
        '''return b ** self, but a bit nicer than just power(b, self):
        If b == 1, return 1. If b == 0, return 0.
        Otherwise return self.power(b, self).
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        check, result = _rpow_quickcheck(self, b)
        return result if check else self.power(b, self)


''' --------------------- Power SIMPLIFY_OPS --------------------- '''

@simplify_op(Power, alias='_flatten')
def _power_flatten(self, **kw__None):
    '''flattens, as appropriate. Power(Power(x, y), z) --> Power(x, y * z)'''
    if isinstance(self.t1, Power):                   # {x^y}^{z}
        powerbase = self.t1
        self = self._new(powerbase.t1, powerbase.t2 * self.t2)  # --> x^{y * z}
    return self

@simplify_op(Power, alias='_simplify_id')
def _power_simplify_id(self, **kw__None):
    '''converts 1^x --> 1, x^0 --> 1, x^1 --> x.'''
    if equals(self.t2, 1):
        return self.t1
    elif equals(self.t1, 1) or equals(self.t2, 0):
        return 1
    else:
        return self

@simplify_op(Power, alias='_evaluate_numbers')
def _power_evaluate_numbers(self, **kw__None):
    '''evaluates numbers. i.e. performs self.t1**self.t2 if t1 and t2 are both not SymbolicObjects.'''
    if not is_nonsymbolic(self.t1) or not is_nonsymbolic(self.t2):
        return self   # return self, exactly, to help indicate no changes were made.
    # otherwise, self is made up of 2 non-SymbolicObject objects, so do base**exp.
    result = self.OPERATION(self.t1, self.t2)
    return result


''' --------------------- Power SIMPLIFY AND EXPAND OPS --------------------- '''

@expand_op(Power, alias='_distribute')
@simplify_op(Power, alias='_simplifying_distribute')
def _power_distribute(self, distribute_power_if=None, **kw__None):
    '''distributes at top layer of self. (x y)^n --> x^n y^n
    distribute_power_if: None or callable of two args, default None
        None --> ignore this kwarg.
        else --> only distributes power to factors if distribute_power_if(power, factor).
        Example:
            using distribute_power_if = (lambda exp, factor: factor == x),
            _power_distribute  (x y z)^n  -->  x^n (y z)^n.

    Note: this function is in SIMPLIFY_OPS *and* EXPAND_OPS,
        because it makes the expression simpler in that it is easier to deal with,
        but also helps with expanding things such as, e.g. ((x+2)*(x+5))^3.
    '''
    base = self.base
    factors = get_factors(base)
    if len(factors) <= 1:
        return self  # return self, exactly, to help indicate nothing changed.
    exp = self.exp
    if distribute_power_if is None:  # distribute to all factors.
        result = self.product(*(self._new(factor, exp) for factor in factors))
    else:
        distribute_factor_if = lambda factor: distribute_power_if(exp, factor)
        to_distribute, to_skip = dichotomize(factors, distribute_factor_if)
        if len(to_distribute) == 0:
            return self  # return self, exactly, to help indicate nothing changed.
        distributed = tuple(self._new(factor, exp) for factor in to_distribute)
        if len(to_skip) == 0:
            skipped = []
        else:
            skipped = [self._new(self.product(*to_skip), exp)]
        result = self.product(*distributed, *skipped)
    return result


''' --------------------- Power EXPAND_OPS --------------------- '''

@expand_op(Power, alias='_expand_exponents')
def _power_expand_exponents(self, **kw__None):
    '''applies (integer) exponents at the top layer of self.
    E.g. (x + 1)**2 --> (x+1)*(x+1).
    [TODO] use binomial theorem to get coefficients,
        instead of doing N multiplications and distributing each time...
    '''
    if not isinstance(self.t1, Sum):    # [TODO] need to set up this check...
        return self
    if not is_integer(self.t2):
        return self
    if self.t2 > 0:
        result = self.t1
        for i in range(1, self.t2):
            result = result * self.t1
        return _simplyfied(result)
    elif equals(self.t2, -1):
        return self     # return self, exactly, to help indicate we are making no changes.
    else: #self.t2 < -1
        x = self.t1 ** (-1 * self.t2)
        x = apply(x, '_expand_exponents')
        return x ** -1