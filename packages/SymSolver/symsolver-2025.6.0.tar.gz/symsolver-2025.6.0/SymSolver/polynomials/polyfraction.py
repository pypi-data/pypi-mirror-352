"""
File Purpose: efficient PolyFraction (ratio of polynomials with arbitrary coefficients).

[TODO] attempt to find gcf() of denoms before adding two PolyFractions.
"""

import functools

from .polynomial import Polynomial
from ..abstracts import (
    SymbolicObject, BinarySymbolicObject,
    SubbableObject, SimplifiableObject,
    _equals0,
)
from ..basics import (
    add,
    seems_negative,
)
from ..errors import PolyFractionPatternError
from ..precalc_operators import (
    AbstractOperator,
)
from ..tools import (
    equals,
    _repr, _str,
    is_integer,
    array_max, array_min,
)
from ..defaults import DEFAULTS, ZERO, ONE


''' --------------------- Arithmetic: PolyFractions --------------------- '''

def _polyfraction_math(f):
    '''decorates f(self, p) so that it does some check(s) beforehand, and sets result.var appropriately.
    Those checks, right now, are:
        - if p is not a PolyFraction, raise TypeError.
            This ensures we aren't accidentally adding non-polyfractions to a PolyFraction.
    '''
    @functools.wraps(f)
    def f_polyfrac_arithmetic_form(self, p):
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        # checks
        if not isinstance(p, PolyFraction):
            raise TypeError(f'PolyFraction can only do math with other PolyFractions, but got {type(p)}.')
        # calculate and return result
        result = f(self, p)
        return result
    return f_polyfrac_arithmetic_form


''' --------------------- PolyFraction (class) --------------------- '''

class PolyFraction(BinarySymbolicObject, SubbableObject, SimplifiableObject):
    '''fraction of two polynomials.
    numer: Polynomial
        numerator
    denom: Polynomial, default Polynomial.MUL_IDENTITY (i.e. the Polynomial representing the number 1)
        denominator
    var: None or object
        if provided, use this as self.var, and fully ignore numer.var & denom.var.
        Otherwise, infer var from self.numer & self.denom.
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, numer, denom=Polynomial.MUL_IDENTITY, *, var=None):
        '''initialize. Ensure numer and denom are both Polynomials and NOT PolyFractions.
        Ensure numer and denom have compatible var.'''
        if not isinstance(numer, Polynomial) or isinstance(numer, PolyFraction):
            raise TypeError(f'expected Polynomial (and non-PolyFraction) numerator but got type {type(numer)}')
        if not isinstance(denom, Polynomial) or isinstance(denom, PolyFraction):
            raise TypeError(f'expected Polynomial (and non-PolyFraction) denominator but got type {type(denom)}')
        if var is None:
            self.var = numer._get_compatible_var(denom)  # << will crash if numer and denom have incompatible var.
        else:
            self.var = var
        BinarySymbolicObject.__init__(self, numer, denom)
        

    numer = property(lambda self: self.t1, doc='''numerator of PolyFraction instance''')
    denom = property(lambda self: self.t2, doc='''denominator of PolyFraction instance''')

    @classmethod
    def from_degree0(cls, degree0_coef, var=None, **kw__init):
        '''create a new PolyFraction with numerator a degree 0 Polynomial, denominator=1,
        given the value for the numerator degree 0 coefficient.
        '''
        return cls(Polynomial.from_degree0(degree0_coef, var=var), **kw__init)

    @classmethod
    def from_degree1(cls, degree1_coef, var=None, **kw__init):
        '''create a new PolyFraction with numerator a degree 1 Polynomial, denominator=1,
        given the value for the numerator degree 1 coefficient.
        '''
        return cls(Polynomial.from_degree1(degree1_coef, var=var), **kw__init)

    def _new_degree0_from_coef(self, degree0_coef):
        '''create a new PolyFraction like self, with numerator a degree 0 Polynomial, denominator=1,
        given the value for the numerator degree 0 coefficient.
        '''
        return self._new(Polynomial.from_degree0(degree0_coef))

    # # # CALLING / EVALUATING # # #
    def __call__(self, x=None):
        '''returns result of evaluating numer and denom at x, or at numer.var and denom.var if x is None.'''
        return self.evaluate(at=x)

    def evaluate(self, at=None, **kw__polynomial_evaluate):
        '''returns numer.evaluate(...) / denom.evaluate(...)

        at: None or value
            plug this value in to each polynomial.
            None --> use numer.var and denom.var
        additional kwargs are passed to numer.evaluate and denom.evaluate.
        '''
        numer = self.numer.evaluate(at=at, **kw__polynomial_evaluate)
        denom = self.denom.evaluate(at=at, **kw__polynomial_evaluate)
        return numer / denom

    # # # DEGREE # # #
    def is_degree0(self):
        '''returns whether numer and denom are both degree 0, i.e. have 0 terms or are like C * x^0.
        [EFF] this is more efficient than checking self.degree == 0.
        '''
        return self.numer.is_degree0() and self.denom.is_degree0()

    def degree(self):
        '''returns (numer.degree(), denom.degree())'''
        return (self.numer.degree(), self.denom.degree())

    # # # DISPLAY # # #
    def _repr_contents(self, **kw):
        '''list of contents to put as comma-separated list into repr of self.'''
        contents = [_repr(self.numer, **kw), _repr(self.denom, **kw)]
        return contents

    def __str__(self, **kw):
        '''string of self.'''
        numer_str = _str(self.numer, **kw)
        denom_str = _str(self.denom, **kw)
        return fr'\frac{{{numer_str}}}{{{denom_str}}}'

    # # # MATH & COMPARISONS # # #
    @_polyfraction_math
    def __add__(self, p):
        '''return self + p'''
        if equals(self.denom, p.denom):
            return self._new(self.numer + p.numer, self.denom)
        else:
            numer = self.numer * p.denom + p.numer * self.denom
            denom = self.denom * p.denom
            return self._new(numer, denom)

    @_polyfraction_math
    def __mul__(self, p):
        '''return self * p
        [TODO][EFF] is it worthwhile to check equality here?
        '''
        eq0 = equals(self.numer, p.denom)
        eq1 = equals(p.numer, self.denom)
        if eq0 and eq1:
            return self._new(Polynomial.MUL_IDENTITY)
        elif eq0:
            return self._new(p.numer, self.denom)
        elif eq1:
            return self._new(self.numer, p.denom)
        else:
            numer = self.numer * p.numer
            denom = self.denom * p.denom
            return self._new(numer, denom)

    def __pow__(self, n):
        '''return self ** n'''
        if seems_negative(n):  # n < 0 --> flip the fraction
            if equals(n, -1):  # n == -1 --> no need to raise top & bottom to power; just switch them.
                numer = self.denom
                denom = self.numer
            else:
                numer = self.denom ** (-n)
                denom = self.numer ** (-n)
        elif _equals0(n):
            return self._new_degree0_from_coef(1)
        else:
            numer = self.numer ** n
            denom = self.denom ** n
        return self._new(numer, denom)

    def __pos__(self):
        '''return +self'''
        return self

    def __neg__(self):
        '''return -self'''
        numer = -self.numer
        denom = self.denom
        return self._new(numer, denom)

    def __sub__(self, p):
        '''return self - p'''
        return self + -p

    def __truediv__(self, p):
        '''return self / p'''
        return self * (p ** (-1)) 

    # # # CONVENIENT MANIPULATIONS # # #
    def rescaled(self, value):
        '''multiplies numerator and denominator by value

        value: Polynomial or "degree 0 coefficient for Polynomial" (any expression not involving self.var)
            if not a Polynomial, use value = Polynomial.from_degree0(value).
        '''
        if not isinstance(value, Polynomial):
            value = Polynomial.from_degree0(value)
        numer = self.numer * value
        denom = self.denom * value
        return self._new(numer, denom)

    def _smaller_largest_coef(self):
        '''returns min(largest coef in numer, largest coef in denom),

        where 'largest' is determined by absolute value of the coefficients.
        If the coefficients are arrays (of any shape), the result will be an array,
            with each element the answer for the corresponding set of coefficients,
            e.g. result[i] = min(largest coef[i] in numer, largest coef[i] in denom)
        '''
        cnumer = array_max(list(self.numer.values()), key=abs)
        cdenom = array_max(list(self.denom.values()), key=abs)
        result = array_min([cnumer, cdenom], key=abs)
        return result

    def shrinkcoef(self):
        '''divide numerator and denominator by min(largest coef in numer, largest coef in denom).

        'largest' is determined by absolute value of the coeffients.
        '''
        divideby = self._smaller_largest_coef()
        return self.rescaled(1 / divideby)

    def shrinkdegree(self):
        '''divide numerator and denominator by x^(degree of smallest degree term throughout numer and denom)
        E.g. (x^7 + x^3) / (x^6 + x^5) --> (x^4 + x^0) / (x^3 + x^2)
        '''
        deg = min(self.numer.inv_degree(), self.denom.inv_degree())
        deg_increment = -deg   # increment degree of all terms by this value.
        numer = self.numer.increment_degree(deg_increment)
        denom = self.denom.increment_degree(deg_increment)
        return self._new(numer, denom)


PolyFraction.ADD_IDENTITY = PolyFraction.from_degree0(0)
PolyFraction.MUL_IDENTITY = PolyFraction.from_degree0(1)