"""
Package Purpose: basic classes for SymSolver.
These provide the basic objects to be manipulated by SymSolver users.
(Other packages may attach more rules to these objects or alter them in another way.)
These objects are:
    Symbol, Sum, Product, Equation, EquationSystem.

This file:
Imports the main important objects throughout this subpackage.
"""
# module references - in case other packages require direct access to these modules.
# (Provides unambiguous reference to module, even when there is a same-named function.
#  E.g. "from basics import power" is unclear; does it import the power module or power.power?)
# Note: we discourage directly accessing these modules for non-internal use.
from . import symbols as _symbols_module
from . import sum as _sum_module
from . import product as _product_module
from . import power as _power_module
from . import equation as _equation_module
from . import equation_system as _equation_system_module

# the basic objects
from .symbols import Symbol
from .sum import Sum
from .product import Product
from .power import Power
from .equation import Equation
from .equation_system import EquationSystem

# more things from symbols module:
from .symbols import (
    symbol, symbols, SYMBOLS,
    new_unique_symbol,
    new_symbol_like,
)
# more things from the basic objects modules:
from .sum import summed
from .product import producted
from .power import powered
from .equation import _eqn_math
from .equation_system import eqsys

# basics tools
from .basics_tools import (
    get_base_and_power, get_factors, get_summands,
    without_factor, without_summand,
    is_reciprocal, get_reciprocal,
    get_common_bases,
    get_factors_numeric_and_other,
    count_minus_signs_in_factors, has_minus_sign, seems_negative, seems_positive,
    exponent_seems_positive, exponent_seems_negative,
    is_negation, multiply, _multiply_some_args, add, _add_some_args,
    gcf, _least_common_power, lcm_simple,
    copy_if_possible,
)

# more imports ...
from . import _sum_collect  # we need to load the content of this module, to augment Sum,
del _sum_collect            # but we don't need to be able to reference it.

from . import _sum_collect_greedy
del _sum_collect_greedy

from . import _square_roots
del _square_roots

from . import _numbers
del _numbers

from .basics_abstracts import (
    AbstractProduct,
)

from . import _string_rep   # we need to load the content of this module to setup __str__ for SymbolicObjects.
# We keep the module name here (i.e. don't del _string_rep) because later modules should use it for strings.
# However, the content of this module is an implementation detail subject to change without warning,
# so we leave the things defind in _string_rep out of this namespace.

from . import _canonical_ordering
del _canonical_ordering

from ._cascade import (
    Cascade,
)

from ._lites import (
    PowerLite, ProductLite, SumLite,
)

from ._to_python import (
    to_python, SSPython,
)