"""
Package Purpose: operators in SymSolver, before calculus is introduced.

This sets up the basic architecture for using operators in SymSolver:
    - AbstractOperator allows to define a custom operator, e.g. f such that f(x) = x**2 - 7.
    - operators can be called on other operators to make a composite operator
    - operators can be added to other operators, or multiplied by non-operators
    - operators might have special properties such as linearity or [TODO] even-ness
There also may be some example operators in here already:
    - SummationOperator; see also summation()

The value of using operators becomes even clearer during calculus,
where (hopefully) a nice definition of the "nabla" operator
precludes the need for completely separate definitions of
grad, curl, div, and u dot nabla for some vector u.

This file:
Imports the main important objects throughout this subpackage.
"""

from .abstract_operators import (
    AbstractOperator, CompositeOperator,
    CompositeCallable,
)
from .generic_operations import (
    GenericOperation,
)
from .linear_operations import (
    LinearOperation,
)
from .linear_operators import (
    LinearOperator,
)
from .operation_vector_products import (
    OperationBinaryVectorProduct,
    OperationDotProduct,
    OperationCrossProduct,
    DotOperation,
)
from .operators_tools import (
    is_operator, nonop_yesop_get_factors,
    is_linear_operator,
)
from .summations import (
    summation, SummationSymbol, SummationOperator, SummationOperation,
)

# load some modules which augment objects from other modules, then can be deleted
# (since their functionality gets attached to those other objects.)
from . import _operator_basics  # augment basic objects (e.g. Sum, Product, Power) to handle operators.
del _operator_basics

from . import _operator_vectors  # augment vectors (DotProduct, CrossProduct) to handle operators.
del _operator_vectors

from . import _to_python  # augment operators to handle conversion to python.
del _to_python
