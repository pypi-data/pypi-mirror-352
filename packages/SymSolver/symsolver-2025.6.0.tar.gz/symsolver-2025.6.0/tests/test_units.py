"""
File Purpose: testing for the basics module.
"""

import SymSolver as ss

ss.load_presets(dst=locals())

def test_units_em():
    '''some electromagnetism units tests for units'''
    assert (eps0 * mu0).unitize().simplified() == (1/c**2).unitize().simplified()

def test_units_vectors():
    '''test that units behave properly with vector products'''
    unew = ss.symbol('unew', vector=True, units_base=ss.UNI.u)  # not-previously-created 'u' symbol
    Bnew = ss.symbol('Bnew', vector=True, units_base=ss.UNI.B)  # not-previously-created 'B' symbol
    known_units = (ss.UNI.u * ss.UNI.B).simplified()
    assert unew.dot(Bnew).unitize().simplified() == known_units
    assert unew.cross(Bnew).unitize().simplified() == known_units
    assert (unew.mag * Bnew.mag).unitize().simplified() == known_units

def test_unit_simplifications():
    '''test some simplifications for units.'''
    # unit id * other units == other units
    for utest in (UNI.B, UNI.E, UNI.u, UNI.watt):  # some things to test, should work with any.
        assert ss.simplify(UNI.id * utest) == utest
        assert ss.simplify(utest * UNI.id) == utest
    # unit id ** power == unit id
    for ptest in (-3,-1,1,3):   # note -- fails for ptest==0 since obj**0 --> 1, not UNI.id.
        assert ss.simplify(UNI.id ** ptest) == UNI.id
    # any unit + itself == itself
    for utest in (UNI.id, UNI.B, UNI.u, UNI.M):  # some things to test, should work with any.
        assert ss.simplify(utest + utest) == utest
    # unit id + other units != other units (i.e. can't simplify)
    assert ss.simplify(UNI.id + UNI.L) != UNI.L
    # unit zero + other units == other units
    assert ss.simplify(UNI.zero + UNI.L) == UNI.L
    # unit zero * other units == unit zero
    assert ss.simplify(UNI.zero * UNI.B) == UNI.zero
    # unit zero ** power == unit zero
    for ptest in (-3,-1,1,3):   # note -- fails for ptest==0 since obj**0 --> 1, not UNI.zero.
        assert ss.simplify(UNI.zero ** ptest) == UNI.zero
