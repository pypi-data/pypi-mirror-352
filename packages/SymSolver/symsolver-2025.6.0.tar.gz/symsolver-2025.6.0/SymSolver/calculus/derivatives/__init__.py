"""
Package Purpose: calculus in SymSolver

This file:
Imports the main important objects throughout this subpackage.
"""

from .derivative import (
    DerivativeSymbol, DerivativeOperator, DerivativeOperation,
    derivative,
)
from .derivatives_tools import (
    is_derivative_operator, is_derivative_operation,
    is_partial_derivative_operator,
    take_derivative,
    _get_dvar, _replace_derivative_operator,
)
from .vector_derivatives import (
    VectorDerivativeSymbol, VectorDerivativeOperator, VectorDerivativeOperation,
)
from .common_vector_derivatives import (
    STORES_NABLA, STORES_TIME, STORES_U,
    grad, div, curl, dpt, dt_advective, dts,
)

# import modules which augment other objects but don't add any new objects:
from . import taking_derivatives
del taking_derivatives

from . import _vector_derivative_operators
del _vector_derivative_operators