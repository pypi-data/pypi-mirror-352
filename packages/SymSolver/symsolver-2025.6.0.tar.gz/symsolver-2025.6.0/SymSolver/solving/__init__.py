"""
Package Purpose: solving in SymSolver.
Methods for solving Equation & EquationSystem.

This file:
Imports the main important objects throughout this subpackage.
"""

from .equation_linsolve import (
    LINEAR_PATTERNS, LINEAR_ELIMINATION_PATTERNS,
    linsolve_essentialized, linsolve_expression,
    LINEAR_SOLVE_METHOD_INFO, LINEAR_ELIMINATE_METHOD_INFO,
)
from .equation_vecsolve import (
    VECTOR_PATTERNS, VECTOR_ELIMINATION_PATTERNS,
    vecsolve_essentialized, vecsolve_expression,
    VECTOR_SOLVE_METHOD_INFO, VECTOR_ELIMINATE_METHOD_INFO,
)
from .equation_solve import (
    SOLVE_METHOD_INFOS, ELIMINATE_METHOD_INFOS,
)
from .predefined_pattern_symbols import (
    PSYMS_ANY, PSYMS_SCALAR, PSYMS_VECTOR,
)
from .solvable_pattern import (
    SolvablePattern,
)
from .solving_tools import (
    SolverMethodInfo,
)
from .system_solver import (
    SystemSolveState, SystemSolver,
    SolveStepInfo,
)