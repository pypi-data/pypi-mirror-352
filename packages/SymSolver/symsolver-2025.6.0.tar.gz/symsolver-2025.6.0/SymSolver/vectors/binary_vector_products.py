"""
File Purpose: BinaryVectorProduct
This is the abstract class which DotProduct and CrossProduct will inherit.

[TODO] more generic "pattern matching" in SymSolver??

[TODO] consider "commutativity" for simplification ops here, e.g. there is an issue when Operators are involved.
"""
import functools

from .vectors_tools import (
    is_vector,
    scalar_vector_get_factors,
)
from ..abstracts import (
    BinarySymbolicObject,
    _abstract_math,
    simplify_op,
)
from ..basics import (
    AbstractProduct, Product,
    Symbol,
)
from ..errors import VectorialityError

from ..defaults import DEFAULTS


class BinaryVectorProduct(AbstractProduct, BinarySymbolicObject):
    '''abstract product of two vectors.
    Not intended for direct use. See e.g. DotProduct or CrossProduct instead.
    '''
    def __init__(self, v1, v2, **kw):
        '''initialize BinaryVectorProduct.
        checks that v1 and v2 are vectors, else raise VectorialityError.
        '''
        if (is_vector(v1)==False) or (is_vector(v2)==False):  # ==False since is_vector(0) --> None.
            raise VectorialityError(f'{type(self).__name__} received one (or two) non-vector input(s).')
        super().__init__(v1, v2, **kw)

    def is_interface_subbable(self):
        '''returns whether self should appear as an option in a SubstitutionInterface.
        returns whether self.t1 and self.t2 are both Symbols.
        '''
        return isinstance(self.t1, Symbol) and isinstance(self.t2, Symbol)


''' --------------------- BinaryVectorProduct custom math --------------------- '''

def _bvp_math(rop_attr=None):
    '''return a decorator which returns a function g(self, b) that first does some small check(s), then does f.
    Those checks, right now, are:
        - do _abstract_math(f)(b)
        - if result is NotImplemented, try b.{rop_attr}(self) if rop_attr is provided.
            - if that is also NotImplemented, raise TypeError.
        - otherwise, return result.
    '''
    def _bvp_math_decorator(f):
        attempt_rop = rop_attr is not None
        abstract_f = _abstract_math(f)
        @functools.wraps(f)
        def f_after_bvp_math_checks(self, b):
            '''if isinstance(b, OperationContainer), returns NotImplemented. Otherwise returns f(self, b).'''
            __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
            result = abstract_f(self, b)
            if attempt_rop and (result is NotImplemented):
                result = getattr(b, rop_attr)(self)
            if result is NotImplemented:  # i.e., if it's STILL NotImplemented
                errmsg = f'unsupported operand type for {type(self).__name__}.{f.__name__}: {type(b).__name__}'
                raise TypeError(errmsg)
            return result
        return f_after_bvp_math_checks
    return _bvp_math_decorator


''' --------------------- BinaryVectorProduct SIMPLIFY_OPS --------------------- '''

@simplify_op(BinaryVectorProduct, alias='_extract_scalars')
def _binary_vector_product_extract_scalars(self, **kw__None):
    '''extracts scalars. E.g. (a u) dot (b v) --> a b (u dot v) for scalars a,b and vectors u,v.'''
    sf_t1, vf_t1 = scalar_vector_get_factors(self.t1)
    sf_t2, vf_t2 = scalar_vector_get_factors(self.t2)
    if (len(sf_t1) == 0) and (len(sf_t2) == 0):  # i.e. both have no scalars; nothing to extract.
        return self  # return self, exactly, to help indicate nothing was changed.
    no_scalars_bvp = self._new(vf_t1[0], vf_t2[0])
    return self.product(*sf_t1, *sf_t2, no_scalars_bvp)
