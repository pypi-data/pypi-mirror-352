"""
Package Purpose: abstract classes for SymSolver.
These classes are all intended to be subclassed, and not instanced directly.

This file:
Imports the main important objects throughout this subpackage.
"""


from .abstract_operations import (
    AbstractOperation,
    _abstract_math,
    # _abstract_add, _abstract_radd,
    # _abstract_mul, _abstract_rmul,
    # _abstract_pow, _abstract_rpow,
)
from .abelian_operations import AbelianOperation
from .associative_operations import (
    AssociativeObject,
    AssociativeOperation,
)
from .commutative_operations import (
    CommutativeObject,                                 
    CommutativeOperation,
)
from .iterable_symbolic_objects import (
    IterableSymbolicObject,
    BinarySymbolicObject,
    get_symbols, get_symbols_in,
    contains_deep, contains_deep_subscript,
    object_counts, object_id_lookup,
    count_nodes,
)
from ._init_modifiers import (
    init_modifier, INIT_MODIFIERS,
)
from .keyed_symbolic_objects import (
    KeyedSymbolicObject,
)
from .operation_containers import (
    OperationContainer,
)
from .simplifiable_objects import (
    SimplifiableObject,
    SIMPLIFY_OPS, EXPAND_OPS,
    SIMPLIFY_OPS_SKIP, EXPAND_OPS_SKIP,
    simplify, expand, simplified,
    simplify_op, expand_op,
    simplify_op_skip_for, expand_op_skip_for,
    simplify_op_DONT_skip, expand_op_DONT_skip, simp_op_DONT_skip,
    simplify_op_DO_skip, expand_op_DO_skip, simp_op_DO_skip,
    restore_simplify_op_skip_defaults, restore_expand_op_skip_defaults, restore_simp_op_skip_defaults,
    _simplyfied,
)
from .substitutions import (
    is_subbable,
    SubbableObject,
    SubstitutionInterface,
    SubTree,
)
from .symbolic_objects import (
    SymbolicObject,
    is_nonsymbolic, is_constant, is_number,
    _equals0,
    symdeplayers,
)

from ._canonical_ordering import (
    canonical_orderer, CanonicalOrderer,
    canonical_sort, canonical_argsort, 
)
from ._complexity import (
    complexity, complexity_infosort, complexity_bins,
    ComplexityBinning, 
)

from . import _compress