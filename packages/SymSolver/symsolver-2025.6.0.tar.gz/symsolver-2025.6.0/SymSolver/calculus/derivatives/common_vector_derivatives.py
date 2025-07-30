"""
File Purpose: commonly used vector derivatives.
"""

from . import vector_derivatives   # imported to ensure INITIALIZERS.derivative_operator is up to date.
from .derivative import derivative
from ...abstracts import AbstractOperation
from ...basics import symbols
from ...errors import VectorialityError
from ...initializers import INITIALIZERS
from ...vectors import is_vector
from ...tools import (
    Binding, alias,
)
binding = Binding(locals())


''' --------------------- Setup --------------------- '''

class _Stores_Nabla():
    '''an empty class; set STORES_NABLA.NABLA = NABLA to enable grad, div, and curl functions.'''
    __slots__ = ['NABLA']
STORES_NABLA = _Stores_Nabla()

class _Stores_t():
    '''an empty class; set STORES_TIME.TIME = TIME to enable dpt function.'''
    __slots__ = ['TIME']
STORES_TIME = _Stores_t()

class _Stores_u():
    '''an empty class; set STORES_U.U = U and STORES_U.U_S = U_S to enable advective derivative functions.'''
    __slots__ = ['U', 'U_S']
STORES_U = _Stores_u()


''' --------------------- Spatial --------------------- '''

# # # AS UNBOUND FUNCTIONS # # #
def grad(self):
    '''return gradient of self.'''
    return STORES_NABLA.NABLA(self)

def div(self):
    '''return divergence of self. self must be a vector.'''
    if not is_vector(self):
        raise VectorialityError('cannot do div(obj) with non-vector obj.')
    return STORES_NABLA.NABLA.dot(self)

def curl(self):
    '''return curl of self. self must be a vector.'''
    if not is_vector(self):
        raise VectorialityError('cannot do curl(obj) with non-vector obj.')
    return STORES_NABLA.NABLA.cross(self)

# # # BOUND TO ABSTRACT OPERATION # # #
with binding.to(AbstractOperation):
    @binding
    def grad(self):
        '''return grad(self)'''
        return grad(self)

    @binding
    def div(self):
        '''return divergence of self. self must be a vector.'''
        return div(self)

    @binding
    def curl(self):
        '''return divergence of self. self must be a vector.'''
        return curl(self)


''' --------------------- Temporal --------------------- '''

# # # AS UNBOUND FUNCTIONS # # #
def dpt(self):
    '''return partial derivative of self with respect to time.'''
    return derivative(self, STORES_TIME.TIME, partial=True)

# # # BOUND TO ABSTRACT OPERATION # # #
with binding.to(AbstractOperation):
    @binding
    def dpt(self):
        '''return dpt(self). I.e., partial derivative of self with respect to time.'''
        return dpt(self)


''' --------------------- Advective --------------------- '''

# # # AS UNBOUND FUNCTIONS # # #
def dt_advective(self, subscript=None):
    '''return advective derivative of self. Uses u if subscript is None, else u_{subscript}.
    (advective derivative)(f) --> partial(f)/partial(t) + (u dot nabla)(f)
    u is stored in STORES_U; either uses STORES_U.U or STORES_U.U_S.ss('s', subscript).
    '''
    if subscript is None:
        u = STORES_U.U
    else:
        u = STORES_U.U_S.ss('s', subscript)
    dpt = INITIALIZERS.derivative_operator(STORES_TIME.TIME, partial=True)
    deriv_op = dpt + u.dot(STORES_NABLA.NABLA)
    return deriv_op(self)

dts = dt_advective  # alias

# # # BOUND TO ABSTRACT OPERATION # # #
with binding.to(AbstractOperation):
    @binding
    def dt_advective(self, subscript=None):
        '''return dt_advective(self). I.e., advective derivative of self.
        Uses u if subscript is None, else u_{subscript}.
        (advective derivative)(f) --> partial(f)/partial(t) + (u dot nabla)(f)
        '''
        return dt_advective(self, subscript=subscript)

    AbstractOperation.dts = alias('dt_advective')
