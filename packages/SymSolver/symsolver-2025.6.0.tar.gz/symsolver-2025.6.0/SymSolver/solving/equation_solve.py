"""
File Purpose: solve equation using the appropriate available method.
"""

from .equation_linsolve import LINEAR_SOLVE_METHOD_INFO, LINEAR_ELIMINATE_METHOD_INFO
from .equation_vecsolve import VECTOR_SOLVE_METHOD_INFO, VECTOR_ELIMINATE_METHOD_INFO
from .solving_tools import _solving_pattern_errmsg
from ..basics import Equation
from ..errors import SolvingPatternError, InputError
from ..essences import (
    essentialize,
)
from ..tools import (
    Binding, format_docstring,
)
from ..defaults import DEFAULTS, ZERO

binding = Binding(locals())


SOLVE_METHOD_INFOS = {
    'linear': LINEAR_SOLVE_METHOD_INFO,
    'vector': VECTOR_SOLVE_METHOD_INFO,
}
SOLVE_METHOD_OPTIONS = tuple(SOLVE_METHOD_INFOS.keys())
ELIMINATE_METHOD_INFOS = {
    'linear': LINEAR_ELIMINATE_METHOD_INFO,
    'vector': VECTOR_ELIMINATE_METHOD_INFO,
}
ELIMINATE_METHOD_OPTIONS = tuple(ELIMINATE_METHOD_INFOS.keys())


''' --------------------- Setup: Pre Essentialize --------------------- '''

with binding.to(Equation):
    @binding
    def _pre_essentialize(self, x, *, _pre_essentialized=False, **kw__essentialize):
        '''returns equation of form (essentialized expression == 0), based on self.
        if _pre_essentialized: instead return self, unchanged.
        '''
        if _pre_essentialized:
            return self
        else:
            self_as_expr = self.subtract_rhs().lhs
            essentialized_expr = essentialize(self_as_expr, x, **kw__essentialize)
            return self._new(essentialized_expr, ZERO)


''' --------------------- Solve --------------------- '''

_kwarg_docs = f'''simplify: bool, None, or dict. default None
            whether return result.simplify() instead of result.
            None --> use DEFAULTS.SOLVING_SIMPLIFY_AFTER (default: {DEFAULTS.SOLVING_SIMPLIFY_AFTER})
            dict --> do result.simplify(**simplify), i.e. "True, & use this as kwargs".
        _verbose_errors: bool, default True
            if False, provide shorter SolvingPatternError error messages.
            [EFF] use False if expecting to catch and not re-raise any SolvingPatternErrors.
        _pre_essentialized: bool, default False
            whether self is already in the form: (essentialized expression == 0).
        '''

with binding.to(Equation):
    @binding
    @format_docstring(method_options=SOLVE_METHOD_OPTIONS, kwargdocs=_kwarg_docs)
    def solve(self, x, *, methods=SOLVE_METHOD_OPTIONS, numerate=True, simplify=None,
              _verbose_errors=True, _pre_essentialized=False, **kw__pre_essentialize):
        '''solve self for x, or raise SolvingPatternError if that is not possible.
        returns Equation like (x == solution).

        E.g. for (A * x + B == 0), returns Equation (x == - B / A).

        methods: tuple of strings
            methods to consider using.
            choose any from: {method_options}
        numerate: bool, default True
            whether to first do self.numerate(x).
            This enables linsolve to work for equations which can be rearranged to a linear form,
                E.g. (A = B / x) is linear in x once you multiply both sides by x.
        {kwargdocs}
        '''
        if numerate:
            self = self.numerate(x)
        # get equation of form (essentialized expression == 0), based on self.
        self = self._pre_essentialize(x, _pre_essentialized=_pre_essentialized, **kw__pre_essentialize)
        # bookkeeping
        _attempted_patterns = {}  # << for error, if all patterns fail
        _attempted_methods = []
        # try to solve
        kw_solve = dict(_verbose_errors=False, _pre_essentialized=False)
        for mkey in methods:
            # get SolverMethodInfo object
            try:
                method = SOLVE_METHOD_INFOS[mkey]
            except KeyError:
                errmsg = f"Invalid method ({repr(mkey)}) entered in 'methods' kwarg. "
                errmsg += f"Valid options: {tuple(SOLVE_METHOD_INFOS.keys())}"
                raise InputError(errmsg) from None
            # use method to try to solve.
            _quickcheck = getattr(self, method.quickcheck)
            if _quickcheck(x):
                _method = getattr(self, method.name)
                try:
                    result = _method(x, **kw_solve)
                except SolvingPatternError:
                    _attempted_patterns.update(method.patterns)
                    _attempted_methods.append(method.name)
                    pass  # ignore error; handled after the 'else' block.
                else:
                    # possibly simplify. Then, return.
                    if simplify is None: simplify = DEFAULTS.SOLVING_SIMPLIFY_AFTER
                    if isinstance(simplify, dict):
                        result = result.simplify(**simplify)
                    elif simplify:
                        result = result.simplify()
                    return result
        # << if we reached this line, we couldn't figure out a solution.
        errmsg = "Essentialized equation does not match any known patterns; cannot solve."
        if _verbose_errors:
            if len(_attempted_methods) == 0:
                errmsg += ("\nDid not have any candidate patterns to try,"
                           f"\nfor equation which looks like:"
                           f"\n  >> str(eqn):   {self}"
                           f"\n  >> repr(eqn):  {repr(self)}")
            else:
                errmsg += _solving_pattern_errmsg(self.lhs, _attempted_patterns, x)
        raise SolvingPatternError(errmsg)


''' --------------------- Eliminate --------------------- '''

with binding.to(Equation):
    @binding
    @format_docstring(method_options=ELIMINATE_METHOD_OPTIONS, kwargdocs=_kwarg_docs)
    def eliminate(self, x, *, methods=ELIMINATE_METHOD_OPTIONS, simplify=None,
                  _verbose_errors=True, _pre_essentialized=False, **kw__pre_essentialize):
        '''eliminate nonzero x from self, or raise SolvingPatternError if that is not possible.
        returns Equation like (solution == 0).

        E.g. for (A * x == 0), returns Equation (A == 0).

        methods: tuple of strings
            methods to consider using.
            choose any from: {method_options}
        {kwargdocs}
        '''
        # get equation of form (essentialized expression == 0), based on self.
        self = self._pre_essentialize(x, _pre_essentialized=_pre_essentialized, **kw__pre_essentialize)
        # bookkeeping
        _attempted_patterns = {}  # << for error, if all patterns fail
        _attempted_methods = []
        # try to solve
        kw_eliminate = dict(_verbose_errors=False, _pre_essentialized=False)
        for mkey in methods:
            # get SolverMethodInfo object
            try:
                method = ELIMINATE_METHOD_INFOS[mkey]
            except KeyError:
                errmsg = f"Invalid method ({repr(mkey)}) entered in 'methods' kwarg. "
                errmsg += f"Valid options: {tuple(ELIMINATE_METHOD_INFOS.keys())}"
                raise InputError(errmsg) from None
            # use method to try to solve.
            _quickcheck = getattr(self, method.quickcheck)
            if _quickcheck(x):
                _method = getattr(self, method.name)
                try:
                    return _method(x, **kw_eliminate)
                except SolvingPatternError:
                    _attempted_patterns.update(method.patterns)
                    _attempted_methods.append(method.name)
                    pass  # ignore error; handled below.
                else:
                    # possibly simplify. Then, return.
                    if simplify is None: simplify = DEFAULTS.SOLVING_SIMPLIFY_AFTER
                    if isinstance(simplify, dict):
                        result = result.simplify(**simplify)
                    elif simplify:
                        result = result.simplify()
                    return result
        # << if we reached this line, we couldn't figure out a solution.
        errmsg = "Essentialized equation does not match any known 'elimination' pattern; cannot solve."
        if _verbose_errors:
            if len(_attempted_methods) == 0:
                errmsg += ("\nDid not have any candidate patterns to try,"
                           f"\nfor equation which looks like:"
                           f"\n  >> str(eqn):   {self}"
                           f"\n  >> repr(eqn):  {repr(self)}")
            else:
                errmsg += _solving_pattern_errmsg(self.lhs, _attempted_patterns, x)
        raise SolvingPatternError(errmsg)
