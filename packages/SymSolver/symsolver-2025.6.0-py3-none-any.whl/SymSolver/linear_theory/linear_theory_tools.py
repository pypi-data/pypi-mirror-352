"""
File Purpose: provide convenient methods for the linear_theory subpackage.
"""

import math

from ..attributors import attributor
from ..tools import (
    format_docstring,
)
from ..defaults import ZERO

MIXED_ORDER = math.nan   # order will be this value if there are 0th and 1st order terms.


''' --------------------- Convenience Functions --------------------- '''

@attributor
def get_o0(x):
    '''returns 0th order form of x, via x.get_o0().
    if x.get_o0() does not exist, return x.
    '''
    try:
        x_get_o0 = x.get_o0
    except AttributeError:
        return x
    else:
        return x_get_o0()

@attributor
def get_o1(x):
    '''returns 1st order form of x, via x.get_o1().
    if x.get_o1() does not exist, return 0.
    '''
    try:
        x_get_o1 = x.get_o1
    except AttributeError:
        return ZERO
    else:
        return x_get_o1()


_order_docs = \
    '''order should be 0, 1, N with N>1, None, or MIXED_ORDER (probably math.nan).
        0 --> 0th order. The constant, background values.
        1 --> 1st order. The "small", variable values.
        N --> Nth order. Even smaller values... non-linear terms.
        None --> no specified order. E.g. 7 or Symbol('x').
        MIXED_ORDER --> ... e.g. n.o1 + n.o0 has MIXED_ORDER.'''

@attributor
@format_docstring(orderdocs=_order_docs)
def get_order(x):
    '''returns x's order, via x.get_order()
    if x.get_order isn't available, return None.

    {orderdocs}
    '''
    try:
        x_get_order = x.get_order
    except AttributeError:
        return None
    else:
        return x_get_order()

def apply_linear_theory(x, o0_constant=True, *, simplify=True, **kw__simplify):
    '''returns x.linearize().assume_o0_constant().assume_plane_waves().simplify()
    If not o0_constant, don't assume_o0_constant.
    If not simplify, don't simplify.
    '''
    result = x.linearize()
    if o0_constant:
        result = result.assume_o0_constant()
    result = result.assume_plane_waves()
    if simplify:
        result = result.simplify(**kw__simplify)
    return result
