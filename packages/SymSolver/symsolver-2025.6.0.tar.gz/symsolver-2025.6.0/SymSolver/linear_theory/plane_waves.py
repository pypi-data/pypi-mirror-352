"""
File Purpose: assuming plane waves
"""

from .linear_theory_tools import (
    get_order, MIXED_ORDER,
    apply_linear_theory,
)
from ..abstracts import SubbableObject, is_subbable
from ..calculus import (
    is_derivative_operator, is_derivative_operation, is_partial_derivative_operator,
    _get_dvar, _replace_derivative_operator,
)
from ..errors import PlaneWavesPatternError, warn
from ..numbers import ImaginaryUnit
from ..precalc_operators import is_operator
from ..initializers import INITIALIZERS
from ..vectors import get_matching_nonNone_vectoriality
from ..tools import (
    equals,
    Binding,
)
from ..defaults import ONE
binding = Binding(locals())


''' --------------------- PW QUANTS defaults storage --------------------- '''

class _StoresPWQuants():
    r'''an empty class; set PWQUANTS.quant = value for default quants in assume_plane_waves.
    settable quants are:
        OMEGA: wave frequency, probably Symbol(r'\omega')
        TIME: time coordinate, probably Symbol('t')
        X: position, can be scalar or vector, probably Symbol('x', vector=True)
        K: wavevector or number; vectoriality must match X, probably Symbol('k', vector=True)
    '''
    __slots__ = ['OMEGA', 'TIME', 'X', 'K']
PWQUANTS = _StoresPWQuants()


''' --------------------- assume_plane_waves --------------------- '''

def _default_if_None__omega_t_k_x(omega, t, k, x):
    '''returns (omega, t, k, x), using value from PWQUANTS for each None input.
    also, ensure is_vector(k)==is_vector(x).
    '''
    if omega is None:
        omega = PWQUANTS.OMEGA
    if t is None:
        t = PWQUANTS.TIME
    if k is None:
        k = PWQUANTS.K
    if x is None:
        x = PWQUANTS.X
    _ = get_matching_nonNone_vectoriality(k, x)  # << crash if is_vector(k) != is_vector(x).
    return (omega, t, k, x)

def _plane_waves_derivative_replace(obj, omega, t, k, x):
    '''helper method for assume_plane_waves; replace derivatives appropriately.
    I.e. substitutes partial derivatives with respect to x and t:
        (partial / partial x) --> i k
        (partial / partial t) --> -i omega
    However, does not check if the derivatives are applied to a 1st-order quantity.
    Also, assumes x and k have the save vectoriality.

    returns obj, or (i k), or (-i omega), or raises PlaneWavesPatternError.
    '''
    if is_derivative_operator(obj):
        dvar = _get_dvar(obj)
        if equals(dvar, x):
            if is_partial_derivative_operator(obj):
                return _replace_derivative_operator(obj, ImaginaryUnit() * k)
            else:
                errmsg = f'Cannot assume plane waves for non-partial d/dx of 1st-order quantity: {obj}'
                raise PlaneWavesPatternError(errmsg)
        elif equals(dvar, t):
            if is_partial_derivative_operator(obj):
                return _replace_derivative_operator(obj, - ImaginaryUnit() * omega)
            else:
                errmsg = f'Cannot assume plane waves for non-partial d/dt of 1st-order quantity: {obj}'
                raise PlaneWavesPatternError(errmsg)
        # else:
        # handled below.
    return obj  # not a derivative operator with dvar x or t.


with binding.to(SubbableObject):
    @binding
    def assume_plane_waves(self, *, omega=None, t=None, k=None, x=None, _internal_call=False, **kw):
        '''assumes first order quantities look like plane waves:
        f^{(1)} --> f^{(1)} exp[i(k x - omega t)]

        Although, rather than making those replacements directly,
        instead jump to the final result assuming self is part of a 1st-order equation.
        I.e. substitutes partial derivatives with respect to x and t:
            (partial / partial x) --> i k
            (partial / partial t) --> -i omega
        wherever those derivatives are applied to a 1st-order quantity.
        
        If self is mixed_order, raise PlaneWavesPatternError.

        omega, t, k, x: None or value
            The corresponding quants in the plane wave assumption:
                f^{(1)} --> f^{(1)} exp[i(k x - omega t)]
            if None, PWQUANTS.attr, where attr is OMEGA, TIME, K, or X, respectively.
        additional kwargs go to self._iter_substitution_terms
        '''
        if not is_subbable(self):
            return self  # return self, exactly, to help indicate nothing was changed.
        # this function's substitution rule for self:
        omega, t, k, x = _default_if_None__omega_t_k_x(omega, t, k, x)
        order = get_order(self)
        if order == MIXED_ORDER:
            errmsg = f'assume plane waves cannot handle obj with MIXED_ORDER; obj={self}'
            raise PlaneWavesPatternError(errmsg)
        if is_derivative_operation(self):
            if get_order(self.operand) != ONE:
                return self  # operand is not order 1, so don't replace the derivative.
            operator = self.operator
            op_subbed = _plane_waves_derivative_replace(operator, omega=omega, t=t, k=k, x=x)
            if op_subbed is operator:
                return self  # return self, exactly, to help indicate nothing was changed.
            # else, op_subbed has been changed.
            # [TODO] maybe operations should provide a "possibly non-operation _new",
            #   which would give the appropriate product if args[0] is not an operator,
            #   rather than TypeError. (That's what the code block here is doing.)
            try:  # if self is an OperationDotProduct or OperationCrossProduct, 
                return self._new(op_subbed, self.operand)   # returns a DotProduct or CrossProduct.
            except TypeError:  # self is not an OperationBinaryVectorProduct; assume it is a scalar product.
                pass  # handled below (in case of error, so that the error traceback will be clearer).
            return INITIALIZERS.product(op_subbed, self.operand)
        # loop through terms in self, if applicable.
        def assume_plane_waves_rule(term):
            return term.assume_plane_waves(omega=omega, t=t, k=k, x=x, _internal_call=True, **kw)
        result = self._substitution_loop(assume_plane_waves_rule, **kw)
        if (not _internal_call) and (result is self) and (order is None):
            warnmsg = ('assume_plane_waves had no effect.\nNote: it only looks for 1st-order quantities.'
                       ' Maybe you forgot to do obj.linearize() (or obj.get_o1() or obj.o1)?')
            warn(warnmsg)
        return result

    @binding
    def apply_linear_theory(self, o0_constant=True, *, simplify=True, **kw__simplify):
        '''returns self.linearize().assume_o0_constant().assume_plane_waves().simplify()
        If not o0_constant, don't assume_o0_constant.
        If not simplify, don't simplify.
        '''
        return apply_linear_theory(self, o0_constant=o0_constant, simplify=simplify, **kw__simplify)
