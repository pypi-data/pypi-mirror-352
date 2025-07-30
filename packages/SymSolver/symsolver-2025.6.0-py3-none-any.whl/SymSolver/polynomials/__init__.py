"""
Package Purpose: efficient polynomials with arbitrary coefficients.

This file:
Imports the main important objects throughout this subpackage.
"""

from .poly_to_array import PolyMPArray
from .polynomial import (
    Polynomial, _polynomial_math,
)
from .polyfraction import (
    PolyFraction, _polyfraction_math,
)
from .polynomialize import (
    polynomial, polynomialize, _first_denominator_appearance,
)
from .polyfractionize import (
    polyfraction, polyfractionize,
)
from .roots import (
    roots_max_imag, roots_min_imag,
    roots_max_real, roots_min_real,
)

from . import poly_errors