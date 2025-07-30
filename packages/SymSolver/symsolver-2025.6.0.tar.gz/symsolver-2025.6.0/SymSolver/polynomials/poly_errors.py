"""
File Purpose: quantifying the scale for "error" in polynomial operations.
E.g., when evaluating polynomial, want to know if it's "close to zero";
    but what is the scale for "close to zero"?
"""

from ..tools import ImportFailed
try:
    import numpy as np
except ImportError as err:
    np = ImportFailed('numpy', err=err)

from .polynomial import Polynomial
from .polyfraction import PolyFraction
from ..tools import (
    Binding,
)
from ..defaults import DEFAULTS

binding = Binding(locals())


''' --------------------- error scale when evaluating polynomial --------------------- '''

with binding.to(Polynomial):
    @binding
    def with_abs_coefs(self):
        '''return new Polynomial made from np.abs() of coefs in self.
        returns self._new({k: np.abs(v) for k, v in self.items()})
        '''
        return self._new({k: np.abs(v) for k, v in self.items()})

    @binding
    def error_scale(self, at, **kw__evaluate):
        '''return error scales for evaluating self at these points.
        When abs(self(at)) < error_scale, the value is consistent with 0, within machine precision.

        This method assumes machine precision is np.finfo(np.float64).eps. (~2e-16)

        Equivalent: self.with_abs_coefs(np.abs(at)) * eps
        '''
        eps = np.finfo(np.float64).eps
        abs_self = self.with_abs_coefs()
        abs_at = np.abs(at)
        return abs_self(abs_at, **kw__evaluate) * eps

with binding.to(PolyFraction):
    @binding
    def error_scales(self, at, **kw__evaluate):
        '''return (self.numer.error_scale(at), self.denom.error_scale(at))
        see Polynomial.error_scale for details.
        '''
        return self.numer.error_scale(at, **kw__evaluate), self.denom.error_scale(at, **kw__evaluate)
