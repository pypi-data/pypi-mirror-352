"""
File Purpose: canonical ordering for CrossProduct and BoxProduct.
"""
from .cross_product import CrossProduct
from .box_product import BoxProduct
from ..abstracts import simplify_op, canonical_argsort, canonical_orderer

from ..tools import (
    find, equals,
    caching_attr_simple,
    Binding,
)

from ..defaults import DEFAULTS, ONE, MINUS_ONE

binding = Binding(locals())


''' --------------------- canonical ordering stuff --------------------- '''

@simplify_op(CrossProduct, alias='_canonical_order')
def _cross_product_canonical_order(self, **kw__None):
    '''if self not in canonical order, negate & flip. E.g., B x A --> - A x B.'''
    aa = canonical_argsort(self)
    if aa[0] == 0:
        return self  # return self, exactly, to help indicate nothing was changed.
    else:
        return -self._new(self.t2, self.t1)

@simplify_op(BoxProduct, alias='_canonical_order')
def _box_product_canonical_order(self, **kw__None):
    '''if self not in canonical order, cycle and/or negate to get to canonical order.
    Assuming (A, B, C) is the canonical order, the possibilities are:
    (ABC)  A dot (B cross C) --> A dot (B cross C)   (i.e., result unchanged)
    (CAB)  C dot (A cross B) --> A dot (B cross C)
    (BCA)  B dot (C cross A) --> A dot (B cross C)
    (ACB)  A dot (C cross B) --> - A dot (B cross C)
    (BAC)  B dot (A cross C) --> - A dot (B cross C)
    (CBA)  C dot (B cross A) --> - A dot (B cross C)
    '''
    aa = tuple(canonical_argsort(self._ABC))
    return self.cycle(aa)


''' --------------------- hashing --------------------- '''
# implemented here because BoxProducts with different terms orders might have the same hash.

with binding.to(BoxProduct):
    @binding
    @caching_attr_simple
    def __hash__(self):
        aa = canonical_argsort(self._ABC)
        sign, A, B, C = self._cycle_terms(aa)
        return hash((type(self), sign, A, B, C))
