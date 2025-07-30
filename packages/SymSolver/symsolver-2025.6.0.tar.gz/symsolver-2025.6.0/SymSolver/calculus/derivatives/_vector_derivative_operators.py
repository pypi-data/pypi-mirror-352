"""
File Purpose: adding some methods to vector operators for compatibility with derivatives.
"""

from .derivatives_tools import (
    is_derivative_operator, is_partial_derivative_operator,
    _get_dvar, _replace_derivative_operator,
)
from ...abstracts import simplify_op
from ...errors import PatternError
from ...precalc_operators import DotOperation
from ...vectors import BinaryVectorProduct
from ...tools import (
    Binding,
)
from ...defaults import DEFAULTS, ZERO
binding = Binding(locals())


''' --------------------- _GET_DVAR and other helper methods --------------------- '''

with binding.to(BinaryVectorProduct):
    @binding
    def is_derivative_operator(self):
        '''returns whether self is a derivative operator, i.e. whether self.t2 is that.'''
        return is_derivative_operator(self.t2)

    @binding
    def is_partial_derivative_operator(self):
        '''returns whether self is a partial derivative operator, i.e. whether self.t2 is that.'''
        return is_partial_derivative_operator(self.t2)

    @binding
    def _get_dvar(self):
        '''returns var with respect to which the derivative is being taken,
        if self.t2 is a derivative operator.
        Else, raises PatternError.
        '''
        if self.is_derivative_operator():
            return _get_dvar(self.t2)
        else:
            raise PatternError(f"({type(self).__name__})._get_dvar() requires obj.t2 to be a derivative.")

    @binding
    def _replace_derivative_operator(self, value):
        '''replace self.t2 with value if self.t2 is a derivative operator.'''
        if self.is_derivative_operator():
            return self._new(self.t1, value)


''' --------------------- SIMPLIFY_ID --------------------- '''

@simplify_op(BinaryVectorProduct, alias='_derivative_simplify_id')
def _binary_vector_product_derivative_simplify_id(self, **kw__None):
    '''simplifies "derivative of constant" --> 0.'''
    if is_derivative_operator(self.t1):
        if self.t1.treats_as_constant(self.t2):
            return ZERO
    return self  # return self, exactly, to help indicate nothing was changed.


@simplify_op(DotOperation, alias='_derivative_simplify_id')
def _dot_operation_derivative_simplify_id(self, **kw__None):
    '''simplifies "derivative of constant" --> 0.'''
    (t1, f), u = self
    if is_derivative_operator(f):
        if f.treats_as_constant(u):
            return ZERO
    return self  # return self, exactly, to help indicate nothing was changed.
