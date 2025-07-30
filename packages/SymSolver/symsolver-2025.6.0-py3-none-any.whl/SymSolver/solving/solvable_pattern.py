"""
File Purpose: SolvablePattern
stores a function to generate a pattern,
and the solution to expr_matching_pattern == 0.
"""

from . import predefined_pattern_symbols as pps
from ..abstracts import SymbolicObject
from ..errors import SolvingPatternError
from ..essences import (
    essentialize, essence_pattern_matches,
    subs_pattern_matched,
)
from ..tools import (
    caching_attr_simple_if,
)
from ..defaults import DEFAULTS


''' --------------------- SolvablePattern --------------------- '''

class SolvablePattern(SymbolicObject):
    '''stores a function to generate a pattern, and the solution to expr == 0,
    for expr matching pattern.

    The 'x' in str or repr of self is a "generic" x representing variable for which to solve expr.
    pattern_maker: callable
        pattern_maker(x) should return an object with PatternSymbols and x.
        e.g. (lambda x: PSYM_A0 * x), to match pattern A * x with A anything.
    solution: object
        the solution for (expr == 0) when essentialized(expr, x) matches pattern_maker(x).
        Note: probably will want to use the same PatternSymbols here as in pattern_maker result.
        e.g. pattern_maker = (lambda x: x + PSYM_A0), solution = (-PSYM_A0).
    _verbose_errors: bool, default True
        whether to use verbose error messages, which may involve converting objects to str.
        Internal calculations which catch the error should instead use False for efficiency.
    '''
    def __init__(self, pattern_maker, solution, *, _verbose_errors=True):
        self.pattern_maker = pattern_maker
        self.solution = solution
        self._verbose_errors = _verbose_errors

    # # # DISPLAY # # #
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def _default_pattern_as_str(self):
        '''returns pattern_maker(predefined_pattern_symbols.PSYM_X)'''
        return self.pattern_maker(pps.PSYM_X)

    def pattern_as_str(self, x=None):
        '''returns pattern_maker(x) if x is not None, else self._default_pattern_as_str()'''
        return self.pattern_maker(x) if x is not None else self._default_pattern_as_str()
        
    def __repr__(self, x=None):
        return f'{type(self).__name__}({self.pattern_as_str(x=x)}, {self.solution})'

    def __str__(self, x=None):
        return fr'{self.pattern_as_str(x=x)} \Longrightarrow {self.solution}'

    # # # SOLVING # # #
    def get_pattern(self, x):
        '''sets self.pattern = self.pattern_maker(x); returns self.pattern.
        caches up to 1 result at a time;
            if self._cached_pattern_x is x, return self.pattern without recalculating.
        '''
        # caching
        if getattr(self, '_cached_pattern_x', None) is x:
            return self.pattern
        # calculate result
        result = self.pattern_maker(x)
        self.pattern = result
        # caching
        self._cached_pattern_x = x
        # result result
        return result

    def use_to_solve_essentialized(self, essentialized_expr, x):
        '''use self to solve essentialized_expr which was essentialized with target x.
        raise SolvingPatternError if this is not possible
            (probably due to self not being an essence_pattern_match for essentialized_expr).
        '''
        pattern = self.get_pattern(x)
        match = essence_pattern_matches(pattern, essentialized_expr)
        if not match:
            errmsg = 'Pattern did not match essentialized expression.'
            if self._verbose_errors:
                errmsg += f'\nPattern: {pattern}.\nEssentialized expression: {essentialized_expr}'
            raise SolvingPatternError(errmsg)
        else:
            result = subs_pattern_matched(self.solution)
            return result

    def use_to_solve(self, expr, x):
        '''use self to solve expr for x.
        Takes these steps:
            essentialize expr with target x.
            match essentialized_expr to self.get_pattern(x)
                (if they don't match, raise SolvingPatternError).
            result = self.solution, subbed appropriately based on the pattern matching.
            return restore_from_essentialized(result, x)
        '''
        essentialized_expr = essentialize(expr, x)
        result = self.use_to_solve_essentialized(essentialized_expr, x)
        return restore_from_essentialized(result, x)
