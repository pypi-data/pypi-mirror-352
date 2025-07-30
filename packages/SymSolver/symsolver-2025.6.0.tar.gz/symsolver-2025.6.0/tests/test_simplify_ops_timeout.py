"""
File Purpose: testing that simplify ops don't stall forever.

These are probably not an exhaustive set of possibilities,
    but the idea is to add a test here every time a stalling-scenario is found,
    to ensure that after fixing it, it does not get "un-fixed" later!
"""

import SymSolver as ss
import warnings

ss.load_presets('MISC', 'REQUIRED', dst=locals())
warnings.filterwarnings('error')  # << warnings as errors instead of warnings.

ss.DEFAULTS.TIMEOUT_SECONDS = 0.1  # should be plenty of time for the simplifications here.

def test_nostall_no_evaluate_numbers():
    '''test that there's no stalling when evaluate_numbers=False.'''
    ss.SIMPLIFY_OPS.disable('evaluate_numbers')

    try:
        result = ss.sum(X, 1, 1).simplify(sum_collect_greedy=True, associative_flatten=True)
        # before debugging, this caused the loop:
        #   X + (1 + 1)   # from sum_collect_greedy
        #   X + 1 + 1     # from associative_flatten.  Then back to top.
    except ss.TimeoutWarning as err:
        assert False   # simplify too slow, possibly infinite loop. test fails.
    assert result == X + 2
