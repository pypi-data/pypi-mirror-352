"""
File Purpose: convert AbstractOperations into Polynomial.
[TODO] caching?
"""

from .polynomial import Polynomial
from ..attributors import attributor
from ..abstracts import (
    AbstractOperation, IterableSymbolicObject,
)
from ..basics import (
    Symbol, Sum, Product, Power, Equation, EquationSystem,
    add,
    seems_negative,
)
from ..errors import PolynomialPatternError
from ..tools import (
    equals,
    ProgressUpdater,
    Binding,
)
from ..defaults import DEFAULTS, ZERO, ONE
binding = Binding(locals())


''' --------------------- Convenience --------------------- '''

@attributor
def polynomial(obj, x):
    '''converts obj to a polynomial in x,
    via obj.polynomial(x) if possible,
    else Polynomial.from_degree0(obj).
    '''
    try:
        return obj.polynomial(x)
    except AttributeError:
        return Polynomial.from_degree0(obj)

@attributor
def polynomialize(obj, x, **kw):
    '''makes obj look more like a polynomial / involve more polynomial-looking things,
    via obj.polynomialize(x, **kw) if possible, else just returns obj.
    '''
    try:
        return obj.polynomialize(x, **kw)
    except AttributeError:
        return obj

@attributor
def _first_denominator_appearance(obj, x):
    '''returns first denominator in obj in which x appears,
    via obj._first_denominator_appearance(x) if possible,
    else returns None.
    Note, obj._first_denominator_appearance(x) may return None if x appears in no denominators in obj.
    '''
    try:
        return obj._first_denominator_appearance(x)
    except AttributeError:
        return None


''' --------------------- Convert to Polynomial in x --------------------- '''

with binding.to(AbstractOperation):
    @binding
    def polynomial(self, x):
        '''converts self (an AbstractOperation instance) to a Polynomial in x.
        if self == x, return Polynomial.from_degree1(1, var=x),
        else, return Polynomial.from_degree0(self)

        Note: subclasses should override this method.
        Note: this implementation assumes x is not contained in self (unless self == x, which is handled here).
            the implementation for IterableSymbolicObject should override this, to search via contains_deep.
        '''
        if equals(self, x):
            return Polynomial.from_degree1(1, var=x)
        else:
            return Polynomial.from_degree0(self)

with binding.to(Symbol):
    @binding
    def polynomial(self, x):
        '''converts self (a Symbol instance) to a Polynomial in x.'''
        return AbstractOperation.polynomial(self, x)

with binding.to(IterableSymbolicObject):
    @binding
    def polynomial(self, x):
        '''converts self (an IterableSymbolicObject instance) to a Polynomial in x.
        if self == x, return Polynomial.from_degree1(1, var=x),
        else if self.contains_deep(x) raise PolynomialPatternError
            (if subclass's instance contains x and subclass didn't override this method, then it should crash.
            e.g. DotProduct(x, y).polynomial(x) should crash.)
        else, return Polynomial.from_degree0(self)
            (if subclass's instance doesn't contain x anywhere, can just say it is a 'degree 0 Polynomial in x')
        '''
        if equals(self, x):
            return Polynomial.from_degree1(1, var=x)
        elif self.contains_deep(x):
            errmsg = f'Cannot turn {type(self).__name__} instance containing x into a Polynomial in x; x={x}'
            raise PolynomialPatternError(errmsg)
        else:
            return Polynomial.from_degree0(self)

with binding.to(Sum, Product):
    @binding
    def polynomial(self, x):
        '''converts self (a Sum or Product instance) to a Polynomial in x.'''
        if equals(self, x):
            return Polynomial.from_degree1(1, var=x)
        else:
            term_polys = tuple(polynomial(term, x) for term in self)
            return self.OPERATION(*term_polys)  # add (for sum) or multiply (for product)

with binding.to(Power):
    @binding
    def polynomial(self, x):
        '''converts self (a Power instance) to a Polynomial in x.'''
        if equals(self, x):
            return Polynomial.from_degree1(1, var=x)
        else:
            base_poly = polynomial(self.base, x)
            return base_poly ** self.exp


''' --------------------- AbstractOperation Polynomialize --------------------- '''
# "convert to Polynomial then back to AbstractOperation instance"
# e.g. result in terms of Sum, Product, Power, ..., but looks like a polynomial.

with binding.to(AbstractOperation):
    @binding
    def polynomialize(self, x, descending=True, *, monicize=False, simplify=False, **kw__simplify):
        '''convert self (an AbstractOperation instance) to a Polynomial in x, then "evaluate"
        to convert the polynomial into an AbstractOperation (probably involving Sums and Products).

        descending: bool or None, default True
            whether to sort the result in descending degree order.
            None --> don't sort. (In this case, no particular order can be guaranteed.)
            True --> highest degree first; lowest degree last.
            False --> opposite; i.e. lowest degree first and highest last.
        monicize: bool, default False
            whether to make a monic polynomial, i.e. where the coefficient of the highest-degree term is 1.
        simplify: bool, default False
            whether to simplify result, via result.simplify(poly_priorities=[x], **kw__simplify).

        returned value is based on the monicize kwarg.
        (default) monicize = False
            --> return polynomial-formatted AbstractOperation,
                such that result == self  (mathematically; i.e. even if SymSolver doesn't know that.)
        monicize = True
            --> return (k, monic-polynomial-formatted AbstractOperation),
                such that k * monic-polynomial == self  (in the mathematical sense.)
        '''
        # setup
        if descending is None:
            kw_evaluate = dict(_sorted=False)
        else:
            kw_evaluate = dict(_sorted=True, _descending=descending)
        # evaluate
        poly = self.polynomial(x)
        if monicize:
            k, mpoly = poly.monicize()
            ao_poly = mpoly.evaluate(**kw_evaluate)
            result = (k, ao_poly)
        else:
            ao_poly = poly.evaluate(**kw_evaluate)
            result = ao_poly
        if simplify:
            result = result.simplify(poly_priorities=[x], **kw__simplify)
        return result
    

''' --------------------- Equation/EquationSystem Polynomialize --------------------- '''
# "convert Equation to an Equation with lhs and rhs polynomialized"

# # # EQUATION -- POLYNOMIALIZE AND NUMERATE # # #
with binding.to(Equation):
    @binding
    def polynomialize(self, x, *, monicize=False, simplify=False, **kw):
        '''convert self (an Equation instance) to an Equation with both sides polynomialized.

        monicize: bool, default False
            if True, instead convert self to an Equation (mp(x) = 0),
            where mp(x) is a monic polynomial in x (i.e. coefficient of highest-degree term is 1)
        simplify: bool, default False
            whether to simplify result, via result.simplify(poly_priorities=[x]).

        other **kw are passed to polynomialize.
        '''
        eqnx = self.numerate(x)  # << equation with x numerated
        if monicize:
            lhs = eqnx.subtract_rhs().lhs
            k, mp = polynomialize(lhs, x, monicize=True, **kw)  # mp = lhs / k. k = leading coefficient.
            result = self._new(mp, ZERO)   # equivalent: "divide" both sides by k.
        else:
            lhs = polynomialize(eqnx.lhs, x, **kw)
            rhs = polynomialize(eqnx.rhs, x, **kw)
            result = self._new(lhs, rhs)
        if simplify:
            result = result.simplify(poly_priorities=[x])
        return result

    @binding
    def numerate(self, x, print_freq=None):
        '''multiply by denominators until x is no longer in any denominators in self.'''
        updater = ProgressUpdater(print_freq=print_freq, wait=True)
        self_prev = None
        i = 0
        while self_prev is not self:
            i+=1
            updater.print(f'beginning numerate step {i}.', print_time=True, end='\r')
            self_prev = self
            self = self._numerate_step(x)
        updater.finalize(process_name='numerate')
        return self

    @binding
    def _numerate_step(self, x):
        '''multiplies self by the first denominator in self which contains x.
        returns self, exactly, if there are no denominator appearances in self containing x.
        [TODO][EFF] more efficient implementation?
        '''
        mul = self._first_denominator_appearance(x)
        if mul is not None:
            result = self * mul
            result = result.apply('_distribute', distribute_sum_if=lambda sum_factor: sum_factor is not mul)
            result = result.apply('_associative_flatten')
            result = result.apply('_product_simplify_id')  # [TODO] _simplify_id should always run before _collect
            return result
        else:
            return self

# # # EQUATION SYSTEM -- POLYNOMIALIZE AND NUMERATE
with binding.to(EquationSystem):
    @binding
    def polynomialize(self, x, **kw):
        '''polynomialize (w.r.t. x) all equations in self. See Equation.polynomialize docs for more details.'''
        return self.op(lambda eqn: eqn.polynomialize(x, **kw), _prevent_new=True)

    @binding
    def numerate(self, x):
        '''numerate x in all equations in self. See Equation.numerate docs for more details.'''
        return self.op(lambda eqn: eqn.numerate(x), _prevent_new=True)


''' --------------------- First Denominator Appearance --------------------- '''
# first denominator in which x appears in self.

with binding.to(Power):
    @binding
    def _first_denominator_appearance(self, x):
        '''returns first denominator in self (a Power instance) in which x appears.
        Or, return None if that is not possible.
        '''
        base, exp = (self.base, self.exp)
        if seems_negative(exp):
            try:
                base_contains_x = base.contains_deep(x)  # x == base or x in base.
            except AttributeError:
                base_contains_x = equals(base, x)
            if base_contains_x:
                return self.get_reciprocal()
            else:
                return None
        else:  # exp doesn't seem negative. Still need to look inside base.
            result = _first_denominator_appearance(base, x)
            if result is None:
                return None   # no denominator appearances of x in base.
            elif equals(exp, ONE):
                return result
            else:
                errmsg = ('Found denominator appearance in base of Power with exponent other than 1.'
                          'This is allowed, mathematically. But the numerate(x) routine may fail in this case,'
                          'e.g. (x^-1 + 7)^2, to numerate x more is required than just multiplying by x.'
                          'This may be implemented at some point, but it is currently not implemented, hence the crash.')
                raise NotImplementedError(errmsg)

with binding.to(IterableSymbolicObject):
    @binding
    def _first_denominator_appearance(self, x):
        '''returns first denominator in self (an IterableSymbolicObject instance) in which x appears.
        Or, return None if that is not possible.
        '''
        for term in self:
            result = _first_denominator_appearance(term, x)
            if result is not None:
                return result
        return None
