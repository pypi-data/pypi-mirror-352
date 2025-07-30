"""
File Purpose: solving linear equation

Works with LINEAR_PATTERNS:
    A_X_PLUS_B:  A * x + B == 0  -->  x == - B / A,  (for scalar nonzero A, and any B)
    X_PLUS_B:        x + B == 0  -->  x == - B,      (with any B)
    A_X:         A * x     == 0  -->  x == 0,        (with any nonzero A)
Also provides method:
    linear_eliminate(x):  A * x == 0  -->  A == 0    (with any A)
"""

from .predefined_pattern_symbols import (
    PSYM_A0,
    PSYM_S0,
)
from .solvable_pattern import SolvablePattern
from .solving_tools import (
    _solving_pattern_errmsg,
    SolverMethodInfo,
)
from ..abstracts import (
    _equals0,
)
from ..basics import Equation
from ..errors import SolvingPatternError
from ..essences import (
    essentialize, essence_pattern_matches,
    restore_from_essentialized,
    subs_pattern_matched,
)
from ..tools import (
    Binding,
)
from ..defaults import ZERO

binding = Binding(locals())


''' --------------------- Linear Patterns --------------------- '''
# Solvable linear equations have possible patterns:
#   A_X_PLUS_B:  A * x + B == 0  -->  x == - B / A,  (for scalar nonzero A, and any B)
#   X_PLUS_B:        x + B == 0  -->  x == - B,      (with any B)
#   A_X:         A * x     == 0  -->  x == 0,        (with any nonzero A)
# x-eliminate-able linear equations have possible patterns:
#   ELIM__A_X:   A * x     == 0  -->  A == 0         (with any A)

def _pattern__A_X_PLUS_B(x):
    '''returns AbstractOperation for (A x + B) pattern matching scalar A and any B.'''
    return PSYM_S0 * x + PSYM_A0
_solution__A_X_PLUS_B = -PSYM_A0 / PSYM_S0

PATTERN__A_X_PLUS_B = SolvablePattern(_pattern__A_X_PLUS_B,
                                      _solution__A_X_PLUS_B, _verbose_errors=False)

def _pattern__X_PLUS_B(x):
    '''returns AbstractOperation for (x + B) pattern matching any B.'''
    return x + PSYM_A0
_solution__X_PLUS_B = -PSYM_A0

PATTERN__X_PLUS_B = SolvablePattern(_pattern__X_PLUS_B,
                                    _solution__X_PLUS_B, _verbose_errors=False)

def _pattern__A_X(x):
    '''returns AbstractOperation for (A x) pattern matching any A.'''
    return PSYM_A0 * x
_solution__A_X = ZERO

PATTERN__A_X = SolvablePattern(_pattern__A_X,
                               _solution__A_X, _verbose_errors=False)


def _pattern__ELIM__A_X(x):
    '''returns AbstractOperation for (A x) pattern matching any A.
    CAUTION: solution == 0, not x. (solution is A == 0).
    '''
    return PSYM_A0 * x
_solution__ELIM__A_X = PSYM_A0

PATTERN__ELIM__A_X = SolvablePattern(_pattern__ELIM__A_X,
                                     _solution__ELIM__A_X, _verbose_errors=False)


LINEAR_PATTERNS = {
    'A_X_PLUS_B' : PATTERN__A_X_PLUS_B,
    'X_PLUS_B'   : PATTERN__X_PLUS_B,
    'A_X'        : PATTERN__A_X,
}

LINEAR_ELIMINATION_PATTERNS = {
    'ELIM__A_X'  : PATTERN__ELIM__A_X,
}


''' --------------------- Linsolve --------------------- '''

def linsolve_essentialized(essentialized_expr, x, *, _verbose_errors=True):
    '''returns solution to essentialized expression matching a linear pattern.
    "solution" in the sense of solving "essentialized_expr == 0" for x.
    raise SolvingPatternError if that is impossible.
    '''
    for _name, pattern in LINEAR_PATTERNS.items():
        try:
            result = pattern.use_to_solve_essentialized(essentialized_expr, x)
        except SolvingPatternError:
            pass  # didn't match this pattern. Keep trying.
        else:
            return result
    # if we made it to this line, then we didn't match any of the LINEAR_PATTERNS.
    errmsg = "Essentialized expression doesn't match any linear pattern; cannot linsolve."
    if _verbose_errors:
        errmsg += _solving_pattern_errmsg(essentialized_expr, LINEAR_PATTERNS, x)
    raise SolvingPatternError(errmsg)

def linsolve_expression(expression, x, *, _verbose_errors=True, _pre_essentialized=False, **kw__essentialize):
    '''returns solution to expression matching a linear pattern.
    "solution in the sense of solving "expression == 0" for x.
    raise SolvingPatternError if that is impossible.
    
    _pre_essentialized: bool, default False
        whether expression is already the result of essentialize(expr, x).
    '''
    essentialized_expr = expression if _pre_essentialized else essentialize(expression, x, **kw__essentialize)
    result = linsolve_essentialized(essentialized_expr, x, _verbose_errors=_verbose_errors)
    unessentialized_result = restore_from_essentialized(result, x)
    return unessentialized_result

with binding.to(Equation):
    @binding
    def linsolve(self, x, *, _verbose_errors=True, _pre_essentialized=False, **kw__essentialize):
        '''returns Equation with x = result, given self an equation linear in x.
        raise SolvingPatternError if that is impossible.

        _pre_essentialized: bool, default False
            whether self already looks like: essentialized_expr == 0
        '''
        eself = self._pre_essentialize(x, _pre_essentialized=_pre_essentialized, **kw__essentialize)
        self_as_expr = eself.lhs
        result_as_expr = linsolve_expression(self_as_expr, x, _verbose_errors=_verbose_errors,
                                             _pre_essentialized=True)
        return self._new(x, result_as_expr)

    @binding
    def _should_attempt_linsolve(self, x):
        '''returns True. returns whether self.solve should attempt self.linsolve(x).
        [TODO][EFF] improve efficiency by returning False when linsolve obviously won't work.
        '''
        return True


''' --------------------- Linear Eliminate --------------------- '''

with binding.to(Equation):
    @binding
    def linear_eliminate(self, x, *, _verbose_errors=True, _pre_essentialized=False, **kw__essentialize):
        '''returns A == 0, given self like A x == 0.
        raise SolvingPatternError if that is impossible.

        _pre_essentialized: bool, default False
            whether self already looks like: essentialized_expr == 0
        '''
        eself = self._pre_essentialize(x, _pre_essentialized=_pre_essentialized, **kw__essentialize)
        essentialized_expr = eself.lhs
        for _name, pattern in LINEAR_ELIMINATION_PATTERNS.items():
            pattern_x = pattern.get_pattern(x)
            match = essence_pattern_matches(pattern_x, essentialized_expr)
            if match:
                essentialized_result_lhs = subs_pattern_matched(pattern.solution)
                result_lhs = restore_from_essentialized(essentialized_result_lhs, x)
                return self._new(result_lhs, ZERO)
        # << if we reach this line, didn't find a match...
        errmsg = "Essentialized expression doesn't match any of the LINEAR_ELIMINATION_PATTERNS; cannot linear_eliminate."
        if _verbose_errors:
            essentialized_eqn = self._new(essentialized_expr, ZERO)
            errmsg += _solving_pattern_errmsg(essentialized_eqn, LINEAR_ELIMINATION_PATTERNS, x, 'equation', 'eqn')
        raise SolvingPatternError(errmsg)

    @binding
    def _should_attempt_linear_eliminate(self, x):
        '''returns True. returns whether self.eliminate should attempt self.linear_eliminate(x).
        [TODO][EFF] improve efficiency by returning False when linear_eliminate obviously won't work.
        '''
        return True


''' --------------------- Linear Solver Method Info --------------------- '''

LINEAR_SOLVE_METHOD_INFO = SolverMethodInfo('linsolve', LINEAR_PATTERNS,
                                            quickcheck='_should_attempt_linsolve')

LINEAR_ELIMINATE_METHOD_INFO = SolverMethodInfo('linear_eliminate', LINEAR_ELIMINATION_PATTERNS,
                                                quickcheck='_should_attempt_linear_eliminate')
