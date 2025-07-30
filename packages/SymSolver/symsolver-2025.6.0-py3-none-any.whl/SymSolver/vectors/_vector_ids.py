"""
File Purpose: simplifications related to vector identities (involving DotProduct and/or CrossProduct)
"""

from .cross_product import CrossProduct
from .dot_product import DotProduct
from .vectors_tools import is_vector

from ..abstracts import (
    simplify_op,
)
from ..tools import (
    equals,
    Binding,
)

binding = Binding(locals())


''' --------------------- CROSS SIMPLE ID: AxA=0 --------------------- '''

@simplify_op(CrossProduct, alias='_simplify_id')
def _cross_product_simplify_id(self, **kw__None):
    '''converts u cross u --> 0, but only if is_vector(u).'''
    if is_vector(self.t1) and equals(self.t1, self.t2):
        return 0
    else:
        return self  # return self, exactly, to help indicate nothing was changed.


''' --------------------- BOX PRODUCT: A.(BxC) --------------------- '''
# DotProducts that look like this are instead handled by BoxProduct; see box_product.py.
# The relevant identities are:
# box product identity:
#     A.(BxC) == B.(CxA) == C.(AxB) == -A.(CxB) == -B.(AxC) == -C.(BxA)
# and a special case of the box product identity:
#     A.(AxC) == A.(CxA) == 0


''' --------------------- DOUBLE CROSS: Ax(BxC) --------------------- '''
# (AxB)xC --> (A.C)B - (B.C)A #

@simplify_op(CrossProduct, alias='_vector_id')
def _cross_product_vector_id(self, **kw__None):
    ''''simplifies the double cross product (AxB)xC:
    (AxB)xC --> (A.C)B - (B.C)A
    Ax(BxC) --> (A.C)B - (A.B)C
    Note: multiple applications of this rule will simplify the triple cross product (AxB)x(BxC).
    '''
    if isinstance(self.t1, CrossProduct):
        A, B, C = (*self.t1, self.t2)
        return A.dot(C)*B - B.dot(C)*A
    elif isinstance(self.t2, CrossProduct):
        A, B, C = (self.t1, *self.t2)
        return A.dot(C)*B - A.dot(B)*C
    else:
        return self  # return self, exactly, to help indicate nothing was changed.

''' --------------------- CROSS DOT CROSS: (AxB).(CxD) --------------------- '''
# (AxB).(CxD) = (A.C)(B.D) - (B.C)(A.D) #

@simplify_op(DotProduct, alias='_vector_id')
def _dot_product_vector_id(self, **kw__None):
    '''simplifies the cross dot cross product (AxB).(CxD):
    (AxB).(CxD) --> (A.C)(B.D) - (B.C)(A.D)
    '''
    if isinstance(self.t1, CrossProduct) and isinstance(self.t2, CrossProduct):
        (A, B) = self.t1
        (C, D) = self.t2
        return A.dot(C) * B.dot(D) - B.dot(C) * A.dot(D)
    else:
        return self  # return self, exactly, to help indicate nothing was changed.
