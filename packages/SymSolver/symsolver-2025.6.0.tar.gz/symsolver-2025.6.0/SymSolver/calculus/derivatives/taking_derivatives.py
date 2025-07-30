"""
File Purpose: rules for taking derivatives
i.e. for "evaluating DerivativeOperation objects"
"""

from .derivatives_tools import (
    _operator_from_dvar_or_operator,
    take_derivative,
)
from ...basics import (
    Sum, AbstractProduct, Power,
)
from ...errors import warn_NotImplemented
from ...tools import (
    Binding,
)
from ...defaults import ONE, ZERO

binding = Binding(locals())


''' --------------------- Helper functions --------------------- '''

def _operator_and_simple(self, dvar_or_derivative_operator, **kw):
    '''returns (derivative operator, None or simple result)

    kwargs are passed to INITIALIZERS.derivative_operator.
    '''
    operator = _operator_from_dvar_or_operator(dvar_or_derivative_operator, **kw)
    return (operator, operator._evaluates_simple(self))


''' --------------------- Basic Derivatives --------------------- '''

with binding.to(Sum):
    @binding
    def take_derivative(self, dvar_or_derivative_operator, partial=False, **kw):
        '''takes derivative of self with respect to dvar. d(self)/d(dvar).
        d(f + g)/dx = df/dx + dg/dx
        returns a Sum of derivatives of each summand in self.
        '''
        operator, simple = _operator_and_simple(self, dvar_or_derivative_operator, partial=partial, **kw)
        if simple is not None:
            return simple   # got a simple result. E.g. d(7 + 3)/dx == 0.
        dsummands = tuple(take_derivative(summand, operator, partial=partial, **kw) for summand in self)
        dsummands = tuple(ds for ds in dsummands if ds is not ZERO)  # << exclude obvious 0's here.
        return self._new(*dsummands)

with binding.to(AbstractProduct):
    @binding
    def take_derivative(self, dvar_or_derivative_operator, partial=False, **kw):
        '''takes derivative of self with respect to dvar. d(self)/d(dvar).
        d(f*g*h)/dx = (df/dx)*g*h + f*(dg/dx)*h + f*g*(dh/dx), where '*' is any product.
        '''
        operator, simple = _operator_and_simple(self, dvar_or_derivative_operator, partial=partial, **kw)
        if simple is not None:
            return simple   # got a simple result. E.g. d(7 * 3)/dx == 0.
        result = []
        factors = list(self)
        for i, fi in enumerate(factors):
            dfi = take_derivative(fi, operator, partial=partial, **kw)
            if dfi is ZERO:
                continue  # << exclude obvious 0's here.
            summand_factors = tuple(dfi if j==i else fj for j, fj in enumerate(factors))
            result.append(self._new(*summand_factors))
        return self.sum(*result)

with binding.to(Power):
    @binding
    def take_derivative(self, dvar_or_derivative_operator, partial=False, **kw):
        '''takes derivative of self with respect to dvar. d(self)/d(dvar).
        d(f**N)/dx where (d/dx) treats N as constant --> N f**(N-1) df/dx.
        d(N**f)/dx where (d/dx) doesn't treat f as constant -->
            don't evaluate; return a DerivativeOperation representing d(N**f)/dx.
            Also, use tools.warn_NotImplemented to indicate that nothing was evaluated.
        '''
        operator, simple = _operator_and_simple(self, dvar_or_derivative_operator, partial=partial, **kw)
        if simple is not None:
            return simple   # got a simple result. E.g. d(7 * 3)/dx == 0.
        base, power = self
        if operator.treats_as_constant(power):
            result_factors = [power, self._new(base, power - 1)]
            dfdx = take_derivative(base, operator, partial=partial, **kw)
            if dfdx is not ONE:
                result_factors.append(dfdx)
            return self.product(*result_factors)
        else:
            warnmsg = ("d(N**f)/dx where (d/dx) doesn't treat f as constant. E.g. d(2**x)/dx. "
                       "returning a DerivativeOperation representing d(N**f)/dx, instead of evaluating.")
            warn_NotImplemented(warnmsg)
            return operator(self)
