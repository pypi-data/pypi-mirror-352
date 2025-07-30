"""
File Purpose: testing behaviors for various DEFAULTS settings
"""

import SymSolver as ss

def test_symbols_o0_constant():
    '''tests the DEFAULTS.SYMBOLS_o0_CONSTANT setting.'''
    h = ss.symbol('h')
    ss.DEFAULTS.SYMBOLS_o0_CONSTANT = True
    assert ss.is_constant(h.o0)
    ss.DEFAULTS.SYMBOLS_o0_CONSTANT = False
    assert not ss.is_constant(h.o0)
