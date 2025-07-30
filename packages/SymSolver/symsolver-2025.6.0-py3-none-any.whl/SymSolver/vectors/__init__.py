"""
Package Purpose: vectors for SymSolver.
Attaches vector-handling rules to basics SymSolver objects,
and provides new objects:
    DotProduct, CrossProduct

This file:
Imports the main important objects throughout this subpackage.
"""

# module references - in case other packages require direct access to these modules.
# Note: we discourage directly accessing these modules for non-internal use.
from . import dot_product as _dot_product_module
from . import cross_product as _cross_product_module
from . import box_product as _box_product_module
from . import basis as _basis_module
from . import vector_symbols as _symbols_module

# vector basic objects
from .dot_product import DotProduct, DotProductBase
from .cross_product import CrossProduct, CrossProductBase
from .box_product import BoxProduct

# basis stuff
from .basis import (
    BASISES,  # << this stores all created Basis objects, for reference.
    Basis, OrthonormalBasis, OrthonormalBasis3D,
    is_basis_vector, is_orthonormal_basis_vector, is_orthonormal_basis_3d_vector,
    get_basis_appearances, get_orthonormal_basis_appearances, get_orthonormal_basis_3d_appearances,
    shared_basis_then_indices, shared_orthonormal_basis_then_indices, shared_orthonormal_basis_3d_then_indices,
)

# componentize stuff.
# Note: to turn on or off "components shorthand", set defaults.DEFAULTS.COMPONENTS_SHORTHAND.
from .componentize import (
    set_default_basis, _default_basis_if_None,
    componentize,
    get_default_ndim, set_default_ndim,
    is_directly_componentizeable,
    components_count,
)

# vector tools
from .vectors_tools import (
    is_vector, is_unit_vector, is_constant_scalar,
    vectoriality, strictest_vectoriality, any_vectoriality, first_nonzero_vectoriality,
    same_rank, get_matching_nonNone_vectoriality,
    scalar_vector_get_factors, scalar_vector_product_split,
)

# more imports ...
from .binary_vector_products import BinaryVectorProduct

from . import _canonical_ordering

from . import _string_rep   # we need to load the content of this module to setup __str__ for SymbolicObjects.
# We keep the module name here (i.e. don't del _string_rep) because later modules should use it for strings.
# However, the content of this module is an implementation detail subject to change without warning,
# so we leave the things defind in _string_rep out of this namespace.

# load some modules which augment objects from other modules, then can be deleted
# (since their functionality gets attached to those other objects.)
from . import _vector_basics  # augment basic objects (e.g. Sum, Product, Power) to handle vectors.
del _vector_basics

from . import _vector_ids  # augment DotProduct and CrossProduct.
del _vector_ids