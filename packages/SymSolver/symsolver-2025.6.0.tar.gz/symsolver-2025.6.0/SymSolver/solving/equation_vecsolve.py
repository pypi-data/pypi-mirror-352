"""
File Purpose: solving vector equation
In particular, patterns where attempting to solve for vector x, but x appears in DotProduct or CrossProduct.
For patterns where x not in DotProduct or CrossProduct, e.g. A x + V == 0, use LINEAR_PATTERNS instead.

Works with VECTOR_PATTERNS (with vector U, V; nonzero scalar A):
    U_CROSS_X_PLUS_A_X_PLUS_V:  U cross x + A x + V == 0  -->  
        --> x == - [(V dot U) U / A + V cross U + A V] / (A**2 + U dot U)
    X_CROSS_U_PLUS_A_X_PLUS_V:  x cross U + A x + V == 0  -->
        --> x == - [(V dot U) U / A - V cross U + A V] / (A**2 + U dot U)
    U_CROSS_X_PLUS_X_PLUS_V:    U cross x +   x + V == 0  --> ... see solution above, use A==1
    X_CROSS_U_PLUS_X_PLUS_V:    x cross U +   x + V == 0  --> ... see solution above, use A==1
    U_CROSS_X_PLUS_A_X:         U cross x + A x     == 0  -->  x == 0  (forces x==0 unless A == 0)
    X_CROSS_U_PLUS_A_X:         x cross U + A x     == 0  -->  x == 0  (forces x==0 unless A == 0)
    U_CROSS_X_PLUS_X:           U cross x +   x     == 0  -->  x == 0  (forces x==0 unless U == 0)
    X_CROSS_U_PLUS_X:           x cross U +   x     == 0  -->  x == 0  (forces x==0 unless U == 0)

    Notes on how to solve U_CROSS_X_PLUS_A_X_PLUS_V:  U cross x + A x + V == 0
        - find (equation cross U);
            apply vector identity for double cross product;
            that provides an equation containing x, x dot U, U cross x
        - find (U cross x) via (equation)
        - find (x dot U) via (equation dot U)
        - plug (U cross x) and (x dot U) into (equation cross U);
            solve using linear pattern.
        Here is code which reproduces the steps above:
            import SymSolver as ss
            A = ss.symbol('A')
            X, U, V = ss.symbols('X U V', vector=True)
            eq = ss.equation(U.cross(X) + A * X + V, 0)
            eqc = eq.cross(U).simplified()   # eq cross U; contains X, (U cross X), and (U dot X)
            eqd = eq.dot(U).simplified()     # eq dot U
            eqsc = eq.linsolve(U.cross(X))   # U cross X == ...
            eqsd = eqd.linsolve(U.dot(X))    # U dot X == ...
            eqfin = eqc.subs(eqsc, eqsd).simplified()
            eqsol = eqfin.linsolve(X)        # X == ...  (the full solution)

Also VECTOR_ELIMINATION_PATTERNS... [TODO] inform user of assumptions:
    X_DOT_U:             (x dot U)         == 0  -->  U == 0   (with vector U)
    X_DOT_U_V:           (x dot U) V       == 0  -->  V == 0   (with vector V)
    X_DOT_U_V_PLUS_A_X:  (x dot U) V + A x == 0  -->  A + V dot U == 0  (with scalar A, vectors U, V)
    X_DOT_U_V_PLUS_X:    (x dot U) V +   x == 0  -->  1 + V dot U == 0  (with vectors U, V)
    
    Note on how to solve X_DOT_U_V_PLUS_A_X:  (x dot U) V + A x == 0
        - dot with U --> (x dot U) (V dot U) + A (x dot U) == 0
        - divide by (x dot U)

[TODO](maybe) encapsulate repeated code between here & linsolve_equation.py
"""

from .predefined_pattern_symbols import (
    PSYM_A0,
    PSYM_S0,
    PSYM_V0, PSYM_V1,
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
from ..initializers import INITIALIZERS
from ..vectors import is_vector
from ..tools import (
    Binding,
)
from ..defaults import ZERO

binding = Binding(locals())


''' --------------------- Vector Patterns --------------------- '''
# Solvable equations containing x inside cross product or dot product have possible patterns:
#   U_CROSS_X_PLUS_A_X_PLUS_V:  U cross x + A x + V == 0  -->  
#       --> x == - [(V dot U) U / A + V cross U + A V] / (A**2 + U dot U)
#   X_CROSS_U_PLUS_A_X_PLUS_V:  x cross U + A x + V == 0  -->
#       --> x == - [(V dot U) U / A - V cross U + A V] / (A**2 + U dot U)
#   U_CROSS_X_PLUS_X_PLUS_V:    U cross x +   x + V == 0  --> ... see solution above, use A==1
#   X_CROSS_U_PLUS_X_PLUS_V:    x cross U +   x + V == 0  --> ... see solution above, use A==1
#   U_CROSS_X_PLUS_A_X:         U cross x + A x     == 0  -->  x == 0  (forces x==0 unless A == 0)
#   X_CROSS_U_PLUS_A_X:         x cross U + A x     == 0  -->  x == 0  (forces x==0 unless A == 0)
#   U_CROSS_X_PLUS_X:           U cross x +   x     == 0  -->  x == 0  (forces x==0 unless U == 0)
#   X_CROSS_U_PLUS_X:           x cross U +   x     == 0  -->  x == 0  (forces x==0 unless U == 0)
# x-eliminate-able equations containing x inside cross or dot product have possible patterns:
#   ELIM__X_DOT_U:              (x dot U)           == 0  -->  U == 0   (with vector U)
#   ELIM__X_DOT_U_V:            (x dot U) V         == 0  -->  V == 0   (with vector V)
#   ELIM__X_DOT_U_V_PLUS_A_X:   (x dot U) V + A x   == 0  -->  A + V dot U == 0  (with scalar A, vectors U, V)
#   ELIM__X_DOT_U_V_PLUS_X:     (x dot U) V +   x   == 0  -->  1 + V dot U == 0  (with vectors U, V)

# # aliases for predefined symbols # #
A = PSYM_S0
B = PSYM_A0
U = PSYM_V0
V = PSYM_V1

# # patterns # #
def _pattern__U_CROSS_X_PLUS_A_X_PLUS_V(x):
    '''returns AbstractOperation for (U cross x + A x + V) pattern matching scalar A and vectors U, V.'''
    return U.cross(x) + A * x + V
_solution__U_CROSS_X_PLUS_A_X_PLUS_V = - (V.dot(U) * U / A + V.cross(U) + A * V) / (A**2 + U.dot(U))

PATTERN__U_CROSS_X_PLUS_A_X_PLUS_V = SolvablePattern(_pattern__U_CROSS_X_PLUS_A_X_PLUS_V,
                                                     _solution__U_CROSS_X_PLUS_A_X_PLUS_V, _verbose_errors=False)

def _pattern__X_CROSS_U_PLUS_A_X_PLUS_V(x):
    '''returns AbstractOperation for (x cross U + A x + V) pattern matching scalar A and vectors U, V.'''
    return x.cross(U) + A * x + V
_solution__X_CROSS_U_PLUS_A_X_PLUS_V = - (V.dot(U) * U / A - V.cross(U) + A * V) / (A**2 + U.dot(U))

PATTERN__X_CROSS_U_PLUS_A_X_PLUS_V = SolvablePattern(_pattern__X_CROSS_U_PLUS_A_X_PLUS_V,
                                                     _solution__X_CROSS_U_PLUS_A_X_PLUS_V, _verbose_errors=False)


def _pattern__U_CROSS_X_PLUS_X_PLUS_V(x):
    '''returns AbstractOperation for (U cross x + x + V) pattern matching vectors U, V.'''
    return U.cross(x) + x + V
_solution__U_CROSS_X_PLUS_X_PLUS_V = - (V.dot(U) * U + V.cross(U) + V) / (1 + U.dot(U))

PATTERN__U_CROSS_X_PLUS_X_PLUS_V = SolvablePattern(_pattern__U_CROSS_X_PLUS_X_PLUS_V,
                                                   _solution__U_CROSS_X_PLUS_X_PLUS_V, _verbose_errors=False)

def _pattern__X_CROSS_U_PLUS_X_PLUS_V(x):
    '''returns AbstractOperation for (x cross U + x + V) pattern matching vectors U, V.'''
    return x.cross(U) + x + V
_solution__X_CROSS_U_PLUS_X_PLUS_V = - (V.dot(U) * U - V.cross(U) + V) / (1 + U.dot(U))

PATTERN__X_CROSS_U_PLUS_X_PLUS_V = SolvablePattern(_pattern__X_CROSS_U_PLUS_X_PLUS_V,
                                                   _solution__X_CROSS_U_PLUS_X_PLUS_V, _verbose_errors=False)


def _pattern__U_CROSS_X_PLUS_A_X(x):
    '''returns AbstractOperation for (U cross x + A x) pattern matching scalar A, vector U.'''
    return U.cross(x) + A * x
_solution__U_CROSS_X_PLUS_A_X = ZERO

PATTERN__U_CROSS_X_PLUS_A_X = SolvablePattern(_pattern__U_CROSS_X_PLUS_A_X,
                                              _solution__U_CROSS_X_PLUS_A_X, _verbose_errors=False)

def _pattern__X_CROSS_U_PLUS_A_X(x):
    '''returns AbstractOperation for (x cross U + A x) pattern matching scalar A, vector U.'''
    return x.cross(U) + A * x
_solution__X_CROSS_U_PLUS_A_X = ZERO

PATTERN__X_CROSS_U_PLUS_A_X = SolvablePattern(_pattern__X_CROSS_U_PLUS_A_X,
                                              _solution__X_CROSS_U_PLUS_A_X, _verbose_errors=False)


def _pattern__U_CROSS_X_PLUS_X(x):
    '''returns AbstractOperation for (U cross x + x) pattern matching vector U.'''
    return U.cross(x) + x
_solution__U_CROSS_X_PLUS_X = ZERO

PATTERN__U_CROSS_X_PLUS_X = SolvablePattern(_pattern__U_CROSS_X_PLUS_X,
                                            _solution__U_CROSS_X_PLUS_X, _verbose_errors=False)

def _pattern__X_CROSS_U_PLUS_X(x):
    '''returns AbstractOperation for (x cross U + x) pattern matching vector U.'''
    return x.cross(U) + x
_solution__X_CROSS_U_PLUS_X = ZERO

PATTERN__X_CROSS_U_PLUS_X = SolvablePattern(_pattern__X_CROSS_U_PLUS_X,
                                            _solution__X_CROSS_U_PLUS_X, _verbose_errors=False)


def _pattern__ELIM__X_DOT_U(x):
    '''returns AbstractOperation for (x dot U) pattern matching vector U.
    CAUTION: solution == 0, not x. (solution is U == 0).
    [TODO] inform user that our solution is overly strict, unless x is "fully generic".
        U==0 is always sufficient to make x dot U == 0, but not always necessary.
    '''
    return x.dot(U)
_solution__ELIM__X_DOT_U = U

PATTERN__ELIM__X_DOT_U = SolvablePattern(_pattern__ELIM__X_DOT_U,
                                         _solution__ELIM__X_DOT_U, _verbose_errors=False)

def _pattern__ELIM__X_DOT_U_B(x):
    '''returns AbstractOperation for ((x dot U) B) pattern matching vector U, any B.
    CAUTION: solution == 0, not x. (solution is B == 0).
    note: will probably never trigger for scalar B, since it would go into U during essentialize.
    '''
    return x.dot(U) * B
_solution__ELIM__X_DOT_U_B = B

PATTERN__ELIM__X_DOT_U_B = SolvablePattern(_pattern__ELIM__X_DOT_U_B,
                                           _solution__ELIM__X_DOT_U_B, _verbose_errors=False)

def _pattern__ELIM__X_DOT_U_V_PLUS_A_X(x):
    '''returns AbstractOperation for ((x dot U) V + A x) pattern matching scalar A and vectors U, V.
    CAUTION: solution == 0, not x. (solution is A + V dot U == 0).
    '''
    return x.dot(U) * V + A * x
_solution__ELIM__X_DOT_U_V_PLUS_A_X = A + V.dot(U)

PATTERN__ELIM__X_DOT_U_V_PLUS_A_X = SolvablePattern(_pattern__ELIM__X_DOT_U_V_PLUS_A_X,
                                                    _solution__ELIM__X_DOT_U_V_PLUS_A_X, _verbose_errors=False)

def _pattern__ELIM__X_DOT_U_V_PLUS_X(x):
    '''returns AbstractOperation for ((x dot U) V + x) pattern matching vectors U, V.
    CAUTION: solution == 0, not x. (solution is 1 + V dot U == 0).
    '''
    return x.dot(U) * V + x
_solution__ELIM__X_DOT_U_V_PLUS_X = 1 + V.dot(U)

PATTERN__ELIM__X_DOT_U_V_PLUS_X = SolvablePattern(_pattern__ELIM__X_DOT_U_V_PLUS_X,
                                                  _solution__ELIM__X_DOT_U_V_PLUS_X, _verbose_errors=False)


VECTOR_PATTERNS = {
    'U_CROSS_X_PLUS_A_X_PLUS_V' : PATTERN__U_CROSS_X_PLUS_A_X_PLUS_V,
    'X_CROSS_U_PLUS_A_X_PLUS_V' : PATTERN__X_CROSS_U_PLUS_A_X_PLUS_V,
    'U_CROSS_X_PLUS_X_PLUS_V'   : PATTERN__U_CROSS_X_PLUS_X_PLUS_V,
    'X_CROSS_U_PLUS_X_PLUS_V'   : PATTERN__X_CROSS_U_PLUS_X_PLUS_V,
    'U_CROSS_X_PLUS_A_X'        : PATTERN__U_CROSS_X_PLUS_A_X,
    'X_CROSS_U_PLUS_A_X'        : PATTERN__X_CROSS_U_PLUS_A_X,
    'U_CROSS_X_PLUS_X'          : PATTERN__U_CROSS_X_PLUS_X,
    'X_CROSS_U_PLUS_X'          : PATTERN__X_CROSS_U_PLUS_X,
}

VECTOR_ELIMINATION_PATTERNS = {
    'ELIM__X_DOT_U'            : PATTERN__ELIM__X_DOT_U,
    'ELIM__X_DOT_U_B'          : PATTERN__ELIM__X_DOT_U_B,
    'ELIM__X_DOT_U_V_PLUS_A_X' : PATTERN__ELIM__X_DOT_U_V_PLUS_A_X,
    'ELIM__X_DOT_U_V_PLUS_X'   : PATTERN__ELIM__X_DOT_U_V_PLUS_X,
}


''' --------------------- Vecsolve --------------------- '''

def vecsolve_essentialized(essentialized_expr, x, *, _verbose_errors=True):
    '''returns solution to essentialized expression matching a vector pattern.
    "solution" in the sense of solving "essentialized_expr == 0" for x.
    raise SolvingPatternError if that is impossible.
    '''
    for _name, pattern in VECTOR_PATTERNS.items():
        try:
            result = pattern.use_to_solve_essentialized(essentialized_expr, x)
        except SolvingPatternError:
            pass  # didn't match this pattern. Keep trying.
        else:
            return result
    # if we made it to this line, then we didn't match any of the LINEAR_PATTERNS.
    errmsg = "Essentialized expression doesn't match any vector pattern; cannot vecsolve."
    if _verbose_errors:
        errmsg += _solving_pattern_errmsg(essentialized_expr, VECTOR_PATTERNS, x)
    raise SolvingPatternError(errmsg)

def vecsolve_expression(expression, x, *, _verbose_errors=True, _pre_essentialized=False, **kw__essentialize):
    '''returns solution to expression matching a vector pattern.
    "solution in the sense of solving "expression == 0" for x.
    raise SolvingPatternError if that is impossible.

    _pre_essentialized: bool, default False
        whether expression is already the result of essentialize(expr, x).
    '''
    essentialized_expr = expression if _pre_essentialized else essentialize(expression, x, **kw__essentialize)
    result = vecsolve_essentialized(essentialized_expr, x, _verbose_errors=_verbose_errors)
    unessentialized_result = restore_from_essentialized(result, x)
    return unessentialized_result

with binding.to(Equation):
    @binding
    def vecsolve(self, x, *, _verbose_errors=True, _pre_essentialized=False, **kw__essentialize):
        '''returns Equation with x = result, given self a solvable equation with x in dot or cross product.
        raise SolvingPatternError if that is impossible.

        _pre_essentialized: bool, default False
            whether self already looks like: essentialized_expr == 0
        '''
        eself = self._pre_essentialize(x, _pre_essentialized=_pre_essentialized, **kw__essentialize)
        self_as_expr = eself.lhs
        result_as_expr = vecsolve_expression(self_as_expr, x, _verbose_errors=_verbose_errors,
                                             _pre_essentialized=True)
        return self._new(x, result_as_expr)

    @binding
    def _should_attempt_vecsolve(self, x):
        '''returns (is_vector(x) != False). returns whether self.solve should attempt self.vecsolve(x).
        [TODO][EFF] improve efficiency by returning False in other cases when vecsolve obviously won't work.
        '''
        return (is_vector(x) != False)


''' --------------------- Vector Eliminate --------------------- '''

with binding.to(Equation):
    @binding
    def vector_eliminate(self, x, *, _verbose_errors=True, _pre_essentialized=False, **kw__essentialize):
        '''returns an Equation: LHS == 0, where LHS is determined by what self looks like.
        After subtracting RHS from self, return based on what self looks like:
            (x dot U)         == 0   -->   U == 0     [TODO] U==0 is sufficient but maybe not necessary...
            (x dot U) V       == 0   -->   V == 0
            (x dot U) V + A x == 0   -->   A + V dot U == 0
        if self doesn't match either of the patterns above, raise SolvingPatternError.
        (above, A is a scalar

        _pre_essentialized: bool, default False
            whether self already looks like: essentialized_expr == 0
        '''
        eself = self._pre_essentialize(x, _pre_essentialized=_pre_essentialized, **kw__essentialize)
        essentialized_expr = eself.lhs
        for _name, pattern in VECTOR_ELIMINATION_PATTERNS.items():
            pattern_x = pattern.get_pattern(x)
            match = essence_pattern_matches(pattern_x, essentialized_expr)
            if match:
                essentialized_result_lhs = subs_pattern_matched(pattern.solution)
                result_lhs = restore_from_essentialized(essentialized_result_lhs, x)
                return self._new(result_lhs, ZERO)
        # << if we reach this line, didn't find a match...
        errmsg = "Essentialized expression doesn't match any of the VECTOR_ELIMINATION_PATTERNS; cannot vector_eliminate."
        if _verbose_errors:
            essentialized_eqn = self._new(essentialized_expr, ZERO)
            errmsg += _solving_pattern_errmsg(essentialized_eqn, VECTOR_ELIMINATION_PATTERNS, x, 'equation', 'eqn')
        raise SolvingPatternError(errmsg)

    @binding
    def _should_attempt_vector_eliminate(self, x):
        '''returns (is_vector(x) != False). returns whether self.eliminate should attempt self.vector_eliminate(x).
        [TODO][EFF] improve efficiency by returning False in other cases when vector_eliminate obviously won't work.
        '''
        return (is_vector(x) != False)


''' --------------------- Vector Solver Method Info --------------------- '''

VECTOR_SOLVE_METHOD_INFO = SolverMethodInfo('vecsolve', VECTOR_PATTERNS,
                                            quickcheck='_should_attempt_vecsolve')

VECTOR_ELIMINATE_METHOD_INFO = SolverMethodInfo('vector_eliminate', VECTOR_ELIMINATION_PATTERNS,
                                                quickcheck='_should_attempt_vector_eliminate')
