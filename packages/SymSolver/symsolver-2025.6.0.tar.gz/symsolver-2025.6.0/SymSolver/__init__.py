"""Symbolic Solver for systems of linear, differential, vector equations.

[TODO] more details about SymSolver here.
"""
# File Purpose: Imports things from throughout SymSolver.

# This enables them to be used directly from here, without needing to know what subpackage they come from.
# For example:
#     import SymSolver as ss
#     ss.SIMPLIFY_OPS   # SymSolver.abstracts.SIMPLIFY_OPS
#     ss.product        # SymSolver.basics.product
#     ss.dot_product    # SymSolver.vectors.dot_product

# [TODO] put lists of things to import, rather than import *

__version__ = '2025.6.0'  # YYYY.MM.MICRO  # MM not 0M, to match pip normalization.
# For non-release versions, use YYYY.MM.MICRO-dev,
#    to indicate the version has no corresponding release.
# in practical terms, to publish new release:
#    (1) remove '-dev' & update version number. E.g. '2024.12.0'
#    (2) push commit with message like: '[VERSION] 2024.12.0'
#    (3) publish release (e.g. git tag, flit build, flit publish)
#    (4) restore '-dev' but do not alter version number. E.g. '2024.12.0-dev'.
#    (5) push commit with message like: '[VERSION] 2024.12.0-dev'

# version history note: after 1.0.4, next is 2025.6.0.
#    2025.6.0 is first version released on pypi.

from .defaults import DEFAULTS
from .tools import *

from .abstracts import *
from .basics import *
from .calculus import *
from .essences import *
from .errors import *
from .linear_theory import *
from .numbers import *
from .polynomials import *
from .precalc_operators import *
from .solving import *
from .vectors import *
from .units import *

from .presets import *

from .attributors import ATTRIBUTORS
from .initializers import INITIALIZERS

# put initializer functions from INITIALIZERS into this namespace.
# e.g. product = INITIALIZERS['product']; power = INITIALIZERS['power']; etc...
# but do it in a more general way than that.
for _initializer_funcname in INITIALIZERS.keys():
    locals()[_initializer_funcname] = INITIALIZERS[_initializer_funcname]
del _initializer_funcname  # << don't save the loop variable to this namespace.
