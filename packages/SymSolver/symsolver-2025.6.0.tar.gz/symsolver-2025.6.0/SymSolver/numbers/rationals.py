"""
File Purpose: Rationals (i.e. fraction of integers)

Notes:
    - Why not utilize python's numbers.Fraction?
        1) we doesn't want to enforce canonical form representation (i.e. reduced fraction)
        2) we want to enable compatibility with custom-typed obj as long as is_integer(obj)
        By making our own class, Rational, we also get more benefits, such as
        control of the __repr__ and __str__ as well as enabling AbstractOperation math
        although those could

[TODO] __str__ should be aware of DEFAULTS.STRINGREP_FRACTION_LAYERS
"""
import functools
import math
import operator

from .abstract_numbers import AbstractNumber
from ..abstracts import (
    SymbolicObject,
    BinarySymbolicObject,
    _equals0,
    simplify_op,
)
from ..initializers import initializer_for, INITIALIZERS
from ..tools import (
    equals,
    is_integer, int_equals,
    operator_from_str,
    alias,
    format_docstring,
)

from ..defaults import DEFAULTS, ZERO, ONE


''' --------------------- Arithmetic Wrapper for Rationals --------------------- '''

def _rational_math(op_attr=None):
    '''return a decorator(f) which returns a function fc(self, b) that may convert self to float before doing f.
    Those checks, right now, are:
        - if b is not a Rational,
            if b is a SymbolicObject,
                return NotImplemented (thus, allowing b to handle this operation)
            elif b is an integer,
                convert it to Rational(b, 1) then do f(self, b)
            elif DEFAULTS.RATIONAL_TO_FLOAT,
                evaluate self (convert to float),
                then do operator.op(evaluated self, b)
            else,
                do super(Rational, self).op(b)

    op_attr: None or str
        if b is not a Rational, use operator with this name.
        None --> use f.__name__.
        example: op_attr = '__add__'
            --> operator.__add__(evaluated self, b)  or  super(Rational, self).__add__(b)
        Note: must be a builtin magic method such as '__add__' or '__rtruediv__'.
    '''
    @format_docstring(doc_opstr='(f.__name__)' if op_attr is None else op_attr)
    def _rational_math_decorator(f):
        '''returns a function fc(self, b) that sometimes provides different behavior if b is not Rational:
            if b is not Rational, instead returns x.{doc_opstr}(b),
            where x=(self as float), or x=super(Rational, self)
        '''
        # get opstr and op_builtin now, while defining the function,
        # instead of re-getting them every time the function is run.
        opstr = f.__name__ if op_attr is None else op_attr
        op_builtin = operator_from_str(opstr)
        # define the function:
        @functools.wraps(f)
        def f_but_different_if_b_not_rational(self, b):
            '''if isinstance(b, Rational), return f(self, b).
            Otherwise, try to do something reasonable (see _rational_math.__doc__ for details).
            '''
            __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
            if isinstance(b, Rational):
                return f(self, b)
            elif isinstance(b, SymbolicObject):
                return NotImplemented
            elif is_integer(b):
                return f(self, Rational.from_integer(int(b)))
            else:
                if DEFAULTS.DEBUG:
                    return 
                if DEFAULTS.RATIONAL_TO_FLOAT:
                    x = self.evaluate()
                    return op_builtin(x, b)
                else:
                    x = super(Rational, self)
                    try:
                        x__op__ = getattr(x, opstr)
                    except AttributeError:
                        return NotImplemented
                    else:
                        return x__op__(b)
        return f_but_different_if_b_not_rational
    return _rational_math_decorator

def _rational_add_results(s, x):
    '''return (numer, denom) for s + x, for Rationals s, x'''
    return (s.numer * x.denom + x.numer * s.denom, s.denom * x.denom)

def _rational_mul_results(s, x):
    '''return (numer, denom) for s * x, for Rationals s, x'''
    return (s.numer * x.numer, s.denom * x.denom)

def _rational_sub_results(s, x):
    '''return (numer, denom) for s - x, for Rationals s, x'''
    return _rational_add_results(s, -x)

def _rational_truediv_results(s, x):
    '''return (numer, denom) for s / x, for Rationals s, x'''
    return _rational_mul_results(s, x.get_reciprocal())

def _rational_pow_int_results(s, n):
    '''return (numer, denom) for s ** n, for Rational s and is_integer(n).'''
    if n > 0:
        return (s.numer ** n, s.denom ** n)
    else:
        abs_n = -n
        return (s.denom ** abs_n, s.numer ** abs_n)


''' --------------------- Rational --------------------- '''

class Rational(AbstractNumber, BinarySymbolicObject):
    '''rational number, i.e. fraction of two integers, with denominator non-negative.
    __init__ expects two integers (is_integer(val)==True), else raises TypeError.
    if negative denominator is input, result will negate denominator and numerator,
    i.e. Rational(n, d) with d<0 returns Rational(-n, -d) instead.
    '''
    def __init__(self, numer, denom, **kw):
        '''initialize, after ensuring numer and denom are integers.'''
        if not is_integer(numer):
            raise TypeError(f'numer must be an integer, but it was not! (got is_integer(numer)={is_integer(numer)})')
        if not is_integer(denom):
            raise TypeError(f'denom must be an integer, but it was not! (got is_integer(denom)={is_integer(denom)})')
        if denom < 0:
            numer = -numer
            denom = -denom
        super().__init__(numer, denom, **kw)

    numer = property(lambda self: self.t1, doc='''numerator, from self= numerator / denominator''')
    denom = property(lambda self: self.t2, doc='''denominator, from self= numerator / denominator''')

    numerator = alias('numer')
    denominator = alias('denom')

    @classmethod
    def from_integer(cls, integer, **kw):
        '''returns cls(numer=integer, denom=1, **kw)'''
        return cls(numer=integer, denom=ONE, **kw)

    def get_reciprocal(self):
        '''returns reciprocal of self.'''
        return self._new(self.denom, self.numer)

    def is_integer(self):
        '''returns whether self.denom == 1.'''
        return equals(self.denom, ONE)

    def __int__(self):
        '''returns int from self. Round down if self is not an integer.'''
        if self.is_integer():
            return self.numer
        else:
            return self.numer // self.denom

    # # # EVALUATE # # #
    @property
    def OPERATION(self):
        '''returns the operation which self represents: division.
        I.e. returns a function f(numer, denom) --> numer / denom.
        '''
        return lambda numer, denom: numer / denom

    def evaluate(self):
        '''returns numer / denom, because it is the number which self represents.'''
        return self.numer / self.denom

    # # # DISPLAY # # #
    def _repr_contents(self, **kw):
        '''returns contents to put inside 'ImaginaryUnitPower()' in repr for self.'''
        return [f'{self.numer}', f'{self.denom}']

    def __str__(self):
        return fr'\frac{{{self.numer}}}{{{self.denom}}}'

    def _str_protect_power_base(self):
        '''returns True, because str of self needs protecting if it appears in base of a Power.'''
        return True

    # # # COMPARISON WITH 0 # # #
    def _equals0(self):
        '''return self == 0.'''
        return _equals0(self.numer) and (not _equals0(self.denom))

    def is_positive(self):
        '''returns self > 0. Note: denom > 0 is assumed for Rational, and enforced during __init__.'''
        return self.numer > 0

    def is_negative(self):
        '''returns self < 0. Note: denom > 0 is assumed for Rational, and enforced during __init__.'''
        return self.numer < 0

    def _is_surely_negation(self, y):
        '''True result is sufficient to indicate y == -self, but not necessary.
        If y is an instance of type(self), checks whether -self == y.
        otherwise returns False.
        '''
        if isinstance(y, type(self)):
            return equals(-self, y)
        else:
            return False

    # # # COMPARISONS - GENERAL # # #
    @_rational_math('__gt__')
    def __gt__(self, b):
        '''return self > b. non-Rational b are handled by the _rational_math decorator.'''
        if b._equals0():
            return self.is_positive()
        else:  # (note, denom for Rationals are non-negative.)
            return self.numer * b.denom > b.numer * self.denom
        
    @_rational_math('__lt__')
    def __lt__(self, b):
        '''return self < b. non-Rational b are handled by the _rational_math decorator.'''
        if b._equals0():
            return self.is_negative()
        else:  # (note, denom for Rationals are non-negative.)
            return self.numer * b.denom < b.numer * self.denom

    def __ge__(self, b):
        '''return self >= b, via (self > b) or (self == b)'''
        return (self > b) or equals(self, b)

    def __le__(self, b):
        '''return self <= b, via (self < b) or (self == b)'''
        return (self < b) or equals(self, b)

    # # # ARITHMETIC # # #
    @_rational_math('__add__')
    def __add__(self, b):
        '''return self + b. non-Rational b are handled by the _rational_math decorator.'''
        return self._new(*_rational_add_results(self, b))
    @_rational_math('__radd__')
    def __radd__(self, b):
        '''return b + self. non-Rational b are handled by the _rational_math decorator.'''
        return self._new(*_rational_add_results(b, self))
    @_rational_math('__mul__')
    def __mul__(self, b):
        '''return self * b. non-Rational b are handled by the _rational_math decorator.'''
        return self._new(*_rational_mul_results(self, b))
    @_rational_math('__rmul__')
    def __rmul__(self, b):
        '''return b * self. non-Rational b are handled by the _rational_math decorator.'''
        return self._new(*_rational_mul_results(b, self))
    @_rational_math('__sub__')
    def __sub__(self, b):
        '''return self - b. non-Rational b are handled by the _rational_math decorator.'''
        return self._new(*_rational_sub_results(self, b))
    @_rational_math('__rsub__')
    def __rsub__(self, b):
        '''return b - self. non-Rational b are handled by the _rational_math decorator.'''
        return self._new(*_rational_sub_results(b, self))
    @_rational_math('__truediv__')
    def __truediv__(self, b):
        '''return self / b. non-Rational b are handled by the _rational_math decorator.'''
        return self._new(*_rational_truediv_results(self, b))
    @_rational_math('__rtruediv__')
    def __rtruediv__(self, b):
        '''return b / self. non-Rational b are handled by the _rational_math decorator.'''
        return self._new(*_rational_truediv_results(b, self))

    @_rational_math('__pow__')
    def __pow__(self, b):
        '''return self ** b. non-Rational b are handled by the _rational_math decorator.'''
        if not b.is_integer():
            return super(Rational, self).__pow__(b)
        else:
            n = int(b)
            return self._new(*_rational_pow_int_results(self, n))
    @_rational_math('__rpow__')
    def __rpow__(self, b):
        '''return b ** self. non-Rational b are handled by the _rational_math decorator.'''
        if not self.is_integer():
            return super(Rational, self).__rpow__(b)
        else:
            n = int(self)
            return self._new(*_rational_pow_int_results(b, n))

    def __neg__(self):
        '''return -self.'''
        return self._new(-self.numer, self.denom)

    # # # "INTERESTING" ARITHMETIC # # #
    def __floordiv__(self, b):
        '''return self // b.'''
        return self.evaluate() // b

    def __rfloordiv__(self, b):
        '''return b // self.'''
        return b // self.evaluate()


@initializer_for(Rational)
def rational(numer, denom, **kw):
    '''creates a new rational object (a fraction with is_integer(numer) and is_integer(denom)).
    the implementation here just returns Rational(numer, denom, **kw).
    '''
    return Rational(numer, denom, **kw)


''' --------------------- SIMPLIFY_OPS for Rational --------------------- '''

@simplify_op(Rational, alias='_simplify_id')
def _rational_simplify_id(self, **kw__None):
    '''converts (x/1) --> x, (0/y) --> 0.'''
    if self._equals0():
        return ZERO
    elif equals(self.denom, ONE):
        return self.numer
    else:
        return self  # return self, exactly, to help indicate nothing was changed.

@simplify_op(Rational, alias='_reduce_fractions')
def _rational_reduce_fractions(self, **kw__None):
    '''divides numerator and denominator by gcd(numerator, denominator), if possible.'''
    try:
        n = int(self.numer)
        d = int(self.denom)
    except TypeError:  # self.numer or self.denom cannot be converted to builtin int type.
        return self  # return self, exactly, to help indicate nothing was changed.
    gcd = math.gcd(n, d)
    if gcd == ONE:  # can use '==' since gcd and ONE are definitely integers here.
        return self  # return self, exactly, to help indicate nothing was changed.
    else:
        n_new = type(self.numer)(n // gcd)   # // is for integer division;
        d_new = type(self.denom)(d // gcd)   # type(...) is in case original numer & denom were not builtin ints.
        return self._new(n_new, d_new)
