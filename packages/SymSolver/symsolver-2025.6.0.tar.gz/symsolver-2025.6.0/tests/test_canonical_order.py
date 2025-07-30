"""
File Purpose: for testing canonical ordering routines.
"""

import SymSolver as ss
import warnings

ss.load_presets('MISC', 'REQUIRED', dst=locals())
warnings.filterwarnings('error')  # << warnings as errors instead of warnings.

def test_nostall_canonical_signs():
    '''test that canonical_signs and canonical_iunits don't stall.
    [TODO] force the relevant values in DEFAULTS / SIMPLIFY_OPS for these tests.
    '''
    ss.DEFAULTS.TIMEOUT_SECONDS = 0.1  # should be plenty of time for the simplifications here.
    # # two terms # #
    term0 = [-i, i, Y, -Y]
    term1 = [-7, 7, -X, X, i*Z, -i*Z]
    sums2 = [(i0 + i1) for i0 in term0 for i1 in term1]
    # all combinations
    try:
        sums_result = ss.viewlist([sum_.simplify() for sum_ in sums2])
    except ss.TimeoutWarning as err:
        assert False   # simplify too slow, possibly infinite loop. test fails.

    # # three terms # #
    terms = [7, X, Y]
    tests = [i, -1, -i, 1]
    sums3 = [(terms[0] * i0 + terms[1] * i1 + terms[2] * i2) for i0 in tests for i1 in tests for i2 in tests]
    # all combinations of 7 i0 + X i1 + Y i2 where i0, i1, i2 are in [i, -1, -i, +1]
    try:
        sums_result = ss.viewlist([sum_.simplify() for sum_ in sums3])
    except ss.TimeoutWarning as err:
        assert False   # simplify too slow, possibly infinite loop. test fails.

