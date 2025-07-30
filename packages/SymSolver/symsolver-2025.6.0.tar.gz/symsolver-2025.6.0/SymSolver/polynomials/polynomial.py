"""
File Purpose: efficient Polynomial with arbitrary coefficients.

saved as dict (keys are powers e.g. 3 for x^3) for faster comparisons.
"""
import functools

from ..abstracts import (
    SymbolicObject, KeyedSymbolicObject,
    SubbableObject, SimplifiableObject,
    _equals0,
)
from ..basics import (
    add,
)
from ..errors import PolynomialPatternError, InputError
from ..precalc_operators import (
    AbstractOperator,
)
from ..tools import (
    equals,
    _repr, _str,
    is_integer,
    caching_attr_simple_if, alias,
)
from ..defaults import DEFAULTS, ZERO, ONE


''' --------------------- Arithmetic: Polynomials --------------------- '''

def _polynomial_math(f):
    '''decorates f(self, p) so that it does some checks beforehand, and sets result.var appropriately.
    Those checks, right now, are:
        - if p is not a Polynomial, raise TypeError.
            This ensures we aren't accidentally adding non-polynomials to a Polynomial.
        - if self.var and p.var are incompatible, raise PolynomialPatternError.
            Otherwise, set result.var to the var implied by self.var and p.var.
    '''
    @functools.wraps(f)
    def f_poly_arithmetic_form(self, p):
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        # checks
        if not isinstance(p, Polynomial):
            raise TypeError(f'Polynomial can only do math with other Polynomials, but got {type(p)}.')
        var = self._get_compatible_var(p)   # << here is where the PolynomialPatternError may occur.
        # calculate result
        result = f(self, p)
        # finish up, then return result
        result.var = var
        return result
    return f_poly_arithmetic_form


''' --------------------- Polynomial (class) --------------------- '''

class Polynomial(KeyedSymbolicObject, SubbableObject, SimplifiableObject):
    '''efficient polynomial with arbitrary coefficients.
    E.g. x^4 + 3 x^2 + 5 x + 7, represented internally as {4: 1, 2: 3, 1: 5, 0: 7}, var=x.
    Note: negative integers power are allowed, e.g.: x^4 + 3 x^(-2) + 5 x + 7 x^-1.

    power_coef_dict: dict
        dict with (key, value) items: (power, coefficient).
        internally, saved to self.dictionary (for compatibility with KeyedSymbolicObject methods).
    var: None or any object, default None
        var associated with this polynomial, or None (to indicate any var is fine; var not yet decided).
        Meaningful in that polynomial math is only allowed between polynomials with compatible vars.
        see self._get_compatible_var(p) for more info.

    Has methods for doing arithmetic, but only with other Polynomial objects.

    Disambiguation note:
        self.is_constant() returns whether self is constant in the 'SymbolicObject' sense,
            i.e. whether all coefficients and self.var (if provided) are constants.
        self.is_degree0() returns whether self is constant in the 'polynomial' sense,
            i.e. whether self contains no terms with var raised to a nonzero power.
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, power_coef_dict, var=None, **kw__init_keyed):
        KeyedSymbolicObject.__init__(self, power_coef_dict, **kw__init_keyed)  # sets self.dictionary = power_coef_dict.
        self.var = var

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another instance of type(self) to be like self,
        via self._new(*args, **kw). Note these will be overwritten in _new by any **kw entered.
        '''
        kw = super()._init_properties()
        kw['var'] = self.var
        return kw

    @classmethod
    def from_degree0(cls, degree0_coef, var=None, **kw__init_super):
        '''create a new degree 0 Polynomial, given the coefficient for the degree 0 term.'''
        return cls({ZERO: degree0_coef}, var=var, **kw__init_super)

    @classmethod
    def from_degree1(cls, degree1_coef, var=None, **kw__init_super):
        '''create a new degree 1 Polynomial, given the coefficient for the degree 1 term.'''
        return cls({ONE: degree1_coef}, var=var, **kw__init_super)

    def _new_degree0_from_coef(self, degree0_coef):
        '''create a new degree 0 object like self, given the coefficient for the degree 0 term.'''
        return self._new({ZERO: degree0_coef})

    def _new_degree1_from_coef(self, degree1_coef):
        '''create a new degree 1 object like self, given the coefficient for the degree 1 term.'''
        return self._new({ZERO: degree1_coef})

    # # # CALLING / EVALUATING # # #
    def __call__(self, x=None):
        '''returns result of evaluating self at x, or at self.var if x is None.'''
        return self.evaluate(self.var if x is None else x)

    def evaluate(self, at=None, *, _sorted=None, _descending=True):
        '''does the additions, multiplications, and exponentiations implied by self.
        e.g. Polynomial({0:1, 2:3}, var=z) --> 1 + 3 * z**2

        at: None or value
            if not None, evaluate at the value provided. (use that value instead of self.var)
        _sorted: None or bool, default None
            whether to sort terms by degree before adding them together.
            None --> use sorted = isinstance(x, SymbolicObject), where x is 'at' if provided, else self.var.
            True --> always sort.
            False --> never sort.
        _descending: bool, default True
            if sorting terms, whether to sort in descending order of degree.
            (Note: this kwarg only matters if sorting terms.)
            True --> descending. I.e. highest degree first; lowest degree last.
            False --> the opposite order.
        '''
        # special cases: empty self, or self with 1 term with power == 0.
        L = len(self)
        if L == 0:
            return ZERO
        if L == 1:
            (power, coef), = self.items()
            if power == ZERO:
                return coef
        # general -- setup
        dict_copy = self.dictionary.copy()
        x = self.var if (at is None) else at
        if x is None:
            raise PolynomialPatternError("Polynomial.evaluate() requires non-None self.var or to input 'at'.")
        sorting = isinstance(x, SymbolicObject) if _sorted is None else _sorted
        if sorting:
            items = sorted(self.items(), key=lambda item: item[0], reverse=_descending)
        else:
            items = list(self.items())
        # general -- result
        result = add(*(coef * (x ** power) for (power, coef) in items))
        return result

    # # # DEGREE # # #
    def is_degree0(self):
        '''returns whether self is degree 0, i.e. has 0 terms or is like C * x^0.
        [EFF] this is more efficient than checking self.degree == 0.
        '''
        if len(self) >= 2:
            return False
        keys = tuple(self.keys())
        if len(keys) == 0:
            return True
        else: # len(keys) == 1
            return _equals0(keys[0])

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def degree(self):
        '''largest power in self. (0 if self is empty)'''
        keys = self.keys()
        return 0 if (len(keys) == 0) else max(keys)

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def inv_degree(self):
        '''smallest power in self. (0 if self is empty)'''
        keys = self.keys()
        return 0 if (len(keys) == 0) else min(keys)

    # # # DISPLAY # # #
    def _repr_contents(self, **kw):
        '''list of contents to put as comma-separated list into repr of self.'''
        contents = [_repr(self.dictionary, **kw)]
        if self.var is not None:
            contents.append(f'var={_repr(self.var, **kw)}')
        return contents

    def __str__(self, **kw):
        '''string of self.
        [TODO] prettier string:
            - use _string_rep to apply protections required based on self.var.
                E.g. right now, str(Polynomial({2: 7}, var=x+y)) --> '7 x + y^2', is misleading/wrong.
            - use '- term' instead of '+ -term' for negative terms
            - only put parentheses around coefs when necessary
        '''
        var_str = r'( \cdot )' if self.var is None else _str(self.var, **kw)
        if '^' in var_str: var_str = f'{{{var_str}}}'   # wrap var^{*} in {}
        coef_strs = [(power, _str(coef, **kw)) for (power, coef) in self.ordered_items(**kw)]
        term_strs = [fr'\left( {coef} \right) {var_str}^{{{power}}}' for (power, coef) in coef_strs]
        return ' + '.join(term_strs)

    def ordered_items(self, descending=True, **kw__None):
        '''return (power, coef) pairs in self, in descending order of power.'''
        return sorted(self.items(), key=lambda item: item[0], reverse=descending)

    # # # MATH & COMPARISONS # # #
    def _get_compatible_var(p1, p2):
        '''returns the compatible var, or raise PolynomialPatternError if that is impossible.
        
        Usually, this will just return p1.var, if p1.var == p2.var,
            or crash with PolynomialPatternError if p1.var != p2.var.

        However, if either var is None or either polynomial has degree 0, there will be no crash.
            In this case, prioritize which var is returned as follows:
                non-None var > var from nonzero-degree-polynomial > var from p1.
            E.g. if both polynomials are degree 0 and both vars are non-None, return p1.var.
        '''
        var1 = p1.var
        var2 = p2.var
        # special case: var1 is var2.
        if var1 is var2:
            return var1
        # special case: either var is None.
        if var2 is None:
            return var1
        elif var1 is None:
            return var2
        # special case: either polynomial is degree 0.
        if p2.is_degree0():
            return var1
        elif p1.is_degree0():
            return var2
        # general case (neither special case applies)
        if equals(var1, var2):
            return var1
        else:
            raise PolynomialPatternError(f'incompatible vars: {var1}, {var2}')

    def __eq__(self, p):
        '''return self == p'''
        if not super().__eq__(p):
            return False
        try:
            self._get_compatible_var(p)
        except PolynomialPatternError:
            return False
        else:
            return True

    __hash__ = KeyedSymbolicObject.__hash__

    @_polynomial_math
    def __add__(self, p):
        '''return self + p'''
        result = self.dictionary.copy()
        for power, coef in p.items():
            try:
                result[power] = result[power] + coef
            except KeyError:
                result[power] = coef
        return self._new(result)

    @_polynomial_math
    def __mul__(self, p):
        '''return self * p'''
        result = {}
        for ppower, pcoef in p.items():
            for spower, scoef in self.items():
                term_power = ppower + spower
                term_coef  = pcoef * scoef
                try:
                    result[term_power] = result[term_power] + term_coef
                except KeyError:
                    result[term_power] = term_coef
        return self._new(result)

    def __pow__(self, n):
        '''return self ** n, for integer n.
        negative n is allowed only if self is a monomial, i.e. if len(self)==1.
        or raise PolynomialPatternError if n is not a non-negative integer.

        [TODO][EFF] make more efficient. Currently, for non-monomials, just multiplies self n times.
        '''
        if not is_integer(n):
            raise PolynomialPatternError(f'cannot raise Polynomial to non-integer power ({n})')
        if len(self) == 1:
            (power, coef), = self.items()
            result = {power * n: coef ** n}
            return self._new(result)
        if n < 0:
            raise PolynomialPatternError(f'cannot raise Polynomial (with multiple terms) to negative power ({n})')
        elif n == 0:
            return self.MUL_IDENTITY
        elif n == 1:
            return self.copy()
        else: # n >= 2 and is an integer.
            # [TODO][EFF] make more efficient than just multiplying self n times.
            result = self
            for _ in range(n-1):  # '-1' because we start with 1 already, via result=self.
                result = result * self
            return result

    def __pos__(self):
        '''return +self'''
        return self

    def __neg__(self):
        '''return -self'''
        return self._new({power: -coef for (power, coef) in self.items()})

    def __sub__(self, p):
        '''return self - p'''
        return self + -p

    def __truediv__(self, p):
        '''return self / p'''
        return self * (p ** (-1))

    # # # CONVENIENT INSPECTION # # #
    def coef_list(self, *, reverse=None, mode=None, iterable_ok=True):
        '''returns sorted list of coefficients in self.
        whether to order from coef-of-highest-power-term to coef-of-lowest-power-term is determined by:
            reverse: if provided, whether to reverse (i.e. if True, highest-power first)
            mode: if reverse not provided, use reverse=True for mode='mpmath', reverse=False for mode='numpy'.

        result will look like: [cN, ..., c1, c0] OR [c0, c1, ..., cN],
            where self represents the polynomial cN x^n + ... + c1 x + c0.

        see also: self.mpmath_coef_list(), self.numpy_coef_list()

        if any powers in self are negative (or non-integers...) raises PolynomialPatternError.

        reverse: None or bool, default None
            whether to reverse the result.
            None  --> use mode to determine reverse.
            True  --> [cN, ..., c1, c0], where self represents cN x^n + ... + c1 x + c0.
                note: directly compatible with mpmath polynomial routines.
            False --> [c0, c1, ..., cN], where self represents c0 + c1 x + ... + cN x^n.
                note: directly compatible with numpy.polynomial.Polynomial.
        mode: None or str ('mpmath' or 'numpy'), default None
            None --> use DEFAULTS.POLYROOTS_MODE
            'mpmath' or 'mpm' --> use reverse = True. (highest power first)
            'numpy' or 'np' --> use reverse = False. (lowest power first)
        iterable_ok: bool, default True
            whether it is okay for coefficients to be iterables.
            e.g. for self.to_numpy_array(), with result an array of polynomials,
                use iterable_ok=True (since that func will handle array coefficients)
            but for self._to_numpy_single(), with result a single numpy polynomial,
                use array_ok = False (since that func doesn't handle array coefficients)
        '''
        # bookkeeping: what value should we use for reverse?
        if reverse is None:  # use mode to determine reverse
            if mode is None:  # get default mode
                mode = DEFAULTS.POLYROOTS_MODE
            if mode in ('mpmath', 'mpm'):
                reverse = True
            elif mode in ('numpy', 'np'):
                reverse = False
            else:
                raise InputError(f"invalid mode. Expected 'mpmath' or 'numpy'; got mode={repr(mode)}")
        # ensure that powers are ok.
        for power in self.keys():
            if not (is_integer(power) and (power >= 0)):
                # there was a bad power, so crash.
                bad_power_errmsg = ("All powers must be integers >= 0 to convert to numpy polynomial, "
                                    f"but at least one power doesn't follow these rules: {badpower}")
                raise PolynomialPatternError(bad_power_errmsg)
        # create coef list.
        result = [ZERO for i in range(self.degree() + 1)]
        for power, coef in self.items():
            if not iterable_ok:
                try:
                    iter(coef)
                except TypeError:
                    pass  # awesome -- coef is not iterable.
                else:
                    errmsg = (f'got iterable coefficient but iterable_ok=False; coef={coef}.'
                              '\nMaybe you forgot to convert to array first?'
                              ' E.g. obj.to_array() or obj.to_mp_array()')
                    raise PolynomialPatternError(errmsg) from None
            result[power] = coef
        return result[::-1] if reverse else result

    def mpmath_coefs(self, *, iterable_ok=True):
        '''returns [cN, ..., c1, c0], where self represents cN x^n + ... + c1 x + c0.
        iterable_ok: bool, default True
            whether it is okay for coefficients to be iterables (as opposed to, e.g., scalars).
        '''
        return self.coef_list(mode='mpmath', iterable_ok=iterable_ok)

    def numpy_coefs(self, *, iterable_ok=True):
        '''returns [c0, c1, ..., cN], where self represents cN x^n + ... + c1 x + c0.
        iterable_ok: bool, default True
            whether it is okay for coefficients to be iterables (as opposed to, e.g., scalars).
        '''
        return self.coef_list(mode='numpy', iterable_ok=iterable_ok)

    mpm_coefs = alias('mpmath_coefs')
    np_coefs = alias('numpy_coefs')

    # # # CONVENIENT MANIPULATIONS # # #
    def increment_degree(self, increment):
        '''return result of adding increment to degee of all terms in self.'''
        return self._new({power + increment: coef for power, coef in self.items()})

    def monicize(self):
        '''converts self to a polynomial proportional to self but with coefficient = 1 for largest degree term.
        returns (previous coefficient of leading term, resulting monic polynomial).
        (if self was already had leading coefficient equal to 1, uses self, exactly, for resulting monic polynomial.)
        '''
        coef_lead = self[self.degree()]
        if equals(coef_lead, ONE):
            return (coef_lead, self)
        else:
            divide_by = self._new_degree0_from_coef(coef_lead)
            monic_poly = self / divide_by
            return (coef_lead, monic_poly)


Polynomial.ADD_IDENTITY = Polynomial.from_degree0(0)
Polynomial.MUL_IDENTITY = Polynomial.from_degree0(1)
