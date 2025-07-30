"""
File Purpose: convert AbstractOperations into PolyFraction

[TODO] encapsulate & reuse, rather than copy-paste, code from polnomialize.py.
"""
from .polyfraction import PolyFraction
from ..attributors import attributor
from ..abstracts import (
    AbstractOperation, IterableSymbolicObject,
)
from ..basics import (
    Symbol, Sum, Product, Power, Equation, EquationSystem,
    add,
    seems_negative,
)
from ..errors import PolyFractionPatternError
from ..tools import (
    equals,
    ProgressUpdater,
    Binding, format_docstring,
)
from ..defaults import DEFAULTS, ZERO, ONE
binding = Binding(locals())


''' --------------------- Convenience --------------------- '''

@attributor
def polyfraction(obj, x):
    '''converts obj to a PolyFraction in x,
    via obj.polyfraction(x) if possible,
    else PolyFraction.from_degree0(obj).
    '''
    try:
        return obj.polyfraction(x)
    except AttributeError:
        return PolyFraction.from_degree0(obj)

@attributor
def polyfractionize(obj, x, **kw):
    '''makes obj look more like a ratio of polyfractions / involve more polyfraction-ratio-looking things,
    via obj.polyfractionize(x, **kw) if possible, else just returns obj.
    '''
    try:
        return obj.polyfractionize(x, **kw)
    except AttributeError:
        return obj


''' --------------------- Convert to PolyFraction in x --------------------- '''

with binding.to(AbstractOperation):
    @binding
    def polyfraction(self, x):
        '''converts self (an AbstractOperation instance) to a PolyFraction in x.
        if self == x, return PolyFraction.from_degree1(1, var=x),
        else, return PolyFraction.from_degree0(self)

        Note: subclasses should override this method.
        Note: this implementation assumes x is not contained in self (unless self == x, which is handled here).
            the implementation for IterableSymbolicObject should override this, to search via contains_deep.
        '''
        if equals(self, x):
            return PolyFraction.from_degree1(1, var=x)
        else:
            return PolyFraction.from_degree0(self)

with binding.to(Symbol):
    @binding
    def polyfraction(self, x):
        '''converts self (a Symbol instance) to a PolyFraction in x.'''
        return AbstractOperation.polyfraction(self, x)

with binding.to(IterableSymbolicObject):
    @binding
    def polyfraction(self, x):
        '''converts self (an IterableSymbolicObject instance) to a PolyFraction in x.
        if self == x, return PolyFraction.from_degree1(1, var=x),
        else if self.contains_deep(x) raise NotImplementedError
            (if subclass's instance contains x and subclass didn't override this method, then it should crash.
            e.g. DotProduct(x, y).polyfraction(x) should crash.)
        else, return PolyFraction.from_degree0(self)
            (if subclass's instance doesn't contain x anywhere, can just say it is a 'degree 0 PolyFraction in x')
        '''
        if equals(self, x):
            return PolyFraction.from_degree1(1, var=x)
        elif self.contains_deep(x):
            errmsg = f'{type(self).__name__}.polyfraction(x), for {type(self).__name__} containing x; x={x}'
            raise NotImplementedError(errmsg)
        else:
            return PolyFraction.from_degree0(self)

with binding.to(Sum, Product):
    @binding
    def polyfraction(self, x):
        '''converts self (a Sum or Product instance) to a PolyFraction in x.'''
        if equals(self, x):
            return PolyFraction.from_degree1(1, var=x)
        else:
            term_polys = tuple(polyfraction(term, x) for term in self)
            return self.OPERATION(*term_polys)  # add (for sum) or multiply (for product)

with binding.to(Power):
    @binding
    def polyfraction(self, x):
        '''converts self (a Power instance) to a PolyFraction in x.'''
        if equals(self, x):
            return PolyFraction.from_degree(1, var=x)
        else:
            base_poly = polyfraction(self.base, x)
            return base_poly ** self.exp


''' --------------------- AbstractOperation Polyfractionize --------------------- '''
# "convert to PolyFraction then back to AbstractOperation instance"
# e.g. result in terms of Sum, Product, Power, ..., but looks like a polyfraction.

_polyfractionize_paramdocs = \
    '''shrinkcoef: bool, default False
            whether to run PolyFraction.shrinkcoef() before evaluating the PolyFraction.
        shrinkdegree: bool, default False
            whether to run PolyFraction.shrinkdegree() before evaluating the PolyFraction.
        shrink_fail_ok: bool, default True
            whether to ignore TypeError raised by if shrinkcoef and/or shrinkdegree.
            E.g. if coefs cannot be compared via min(), then shrinkcoef will probably give TypeError.
                in that case, if shrink_fail_ok, just return the result from before shrinkcoef.
                but if not shrink_fail_ok, raise the error.
        simplify: bool or dict, default False
            if not False, return result.simplify(collect_polys=[x], collect_poly_format=True).
            if dict, also pass this as kwargs when doing simplify.'''

with binding.to(AbstractOperation):
    @binding
    @format_docstring(paramdocs=_polyfractionize_paramdocs)
    def polyfractionize(self, x, shrinkcoef=False, shrinkdegree=False, shrink_fail_ok=True, simplify=False):
        '''convert self (an AbstractOperation instance) to a PolyFraction in x, then "evaluate"
        to convert the polyfraction into an AbstractOperation (probably involving Sums, Products, and Powers).

        {paramdocs}
        '''
        p = self.polyfraction(x)
        if shrinkcoef:
            try:
                p = p.shrinkcoef()
            except TypeError:  # (can't determine 'min' or 'max' of coefs. Maybe they contain an AbstractOperation.)
                if not shrink_fail_ok:
                    raise
        if shrinkdegree:
            try:
                p = p.shrinkdegree()
            except TypeError:  # (can't determine 'min' or 'max' of powers. Maybe they contain an AbstractOperation.)
                if not shrink_fail_ok:
                    raise
        result = p.evaluate()
        if simplify:
            kw_simplify = {'collect_polys':[x], 'collect_poly_format':True}
            if isinstance(simplify, dict):
                kw_simplify.update(simplify)
            result = result.simplify(**kw_simplify)
        return result


''' --------------------- Equation/EquationSystem Polyfractionize --------------------- '''
# "convert Equation to an Equation with lhs and rhs polyfractionized"

with binding.to(Equation):
    @binding
    @format_docstring(paramdocs=_polyfractionize_paramdocs)
    def polyfractionize(self, x, shrinkcoef=False, shrinkdegree=False, **kw):
        '''converts self to be an equation between two polyfractionized-in-x objects.

        {paramdocs}
        '''
        kw_polyfractionize = dict(shrinkcoef=shrinkcoef, shrinkdegree=shrinkdegree, **kw)
        lhs = polyfractionize(self.lhs, x, **kw_polyfractionize)
        rhs = polyfractionize(self.rhs, x, **kw_polyfractionize)
        return self._new(lhs, rhs)

with binding.to(EquationSystem):
    @binding
    @format_docstring(paramdocs=_polyfractionize_paramdocs)
    def polyfractionize(self, x, **kw):
        '''converts self to be a system of equations with lhs & rhs each polyfractionized-in-x objects.

        {paramdocs}
        '''
        return self.op(lambda eqn: eqn.polyfractionize(x, **kw), _prevent_new=True)
