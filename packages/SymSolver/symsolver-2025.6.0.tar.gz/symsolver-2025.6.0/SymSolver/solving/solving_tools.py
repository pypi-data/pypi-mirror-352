"""
File Purpose: misc. tools for the solving subpackage
"""
#from ..errors import SolvingPatternError  # << commented out because not actually used here.
from ..tools import (
    documented_namedtuple,
    Binding,
)
binding = Binding(locals())


''' --------------------- Patterns Printing --------------------- '''

def _solving_pattern_errmsg(expr, patterns, x, kind='expression', abbrv='expr'):
    '''returns a string to use for verbose SolvingPatternError error messages.
    The string will look like:
        Attempted (but failed) to match these patterns:
          PATTERN_1_NAME : pattern_1.pattern_as_str(x)
          PATTERN_2_NAME : pattern_2.pattern_as_str(x)
          ...
          PATTERN_N_NAME : pattern_N.pattern_as_str(x)
        for the <kind> provided, which looks like:
          >> str(<abbrv>):   <str(expr)>
          >> repr(<abbv>):   <repr(expr)>
    where <x> --> str(x), above. (e.g. for abbrv='expr', '<abbrv>' --> 'expr', above)
    '''
    result = ("\nAttempted (but failed) to match these patterns:\n" +
               '\n'.join(f"  {repr(name)} : {pattern.pattern_as_str(x)}"
                         for name, pattern in patterns.items()) +
               f"\nfor the {kind} provided, which looks like:"
               f"\n  >> str({abbrv}):   {expr}"
               f"\n  >> repr({abbrv}):  {repr(expr)}")
    return result


''' --------------------- Methods Tracking --------------------- '''

SolverMethodInfo = documented_namedtuple('SolverMethodInfo', ['name', 'patterns', 'quickcheck'],
        '''Info about some method related to solving equations, e.g. linsolve, vector_eliminate.''',
        name='''attribute name of method, e.g. "linsolve" for Equation.linsolve()''',
        patterns='''patterns associated with the method, e.g. LINEAR_PATTERNS for Equation.linsolve()''',
        quickcheck='''attribute name of quickcheck method e.g. "_should_attempt_linsolve"''',
        _module=(lambda: None).__module__,
        )

with binding.to(SolverMethodInfo):
    SolverMethodInfo.repr = SolverMethodInfo.__repr__   # << use smi.repr() to get "full" __repr__.
    @binding
    def __repr__(self):
        '''only put self.name, for brevity.'''
        return f'{type(self).__name__}(name={repr(self.name)}, ...)'
