"""
File Purpose: testing for the basics module.
"""

import SymSolver as ss

ss.load_presets(dst=locals())

def test_sum():
    '''some basic tests for sum.'''
    # 0 inputs -- return 0
    assert ss.sum() == 0
    # 1 input -- return the input.
    assert ss.sum(X) == X
    assert ss.sum(7) == 7
    # 2 inputs
    assert X + Y == ss.sum(X,Y)
    assert X + Y == ss.sum(Y,X)   # order doesn't matter
    assert X + 7 == ss.sum(X,7)   # works with numbers too
    assert 7 + X == ss.sum(X,7)   # __radd__ defined properly
    assert X + 0 == X             # __add__ ignores 0
    assert len(ss.sum(X, 0)) == 2 # ss.sum() doesn't apply anything immediately
    # >2 inputs
    assert X + Y + Z == ss.sum(X,Y,Z)
    assert X + Y + Z == ss.sum(Y,Z,X)  # order doesn't matter even with 3 inputs
    assert 7 + 8 + X == ss.sum(15, X)  # adds numbers until encoutering SymbolicObject
    assert X + 7 + 8 == ss.sum(X, 7, 8)  # doesn't add numbers after encountering SymbolicObject

def test_product():
    '''some basic tests for product.'''
    # 0 inputs -- return 1
    assert ss.product() == 1
    # 1 input -- return the input.
    assert ss.product(X) == X
    assert ss.product(7) == 7
    # 2 inputs
    assert X * Y == ss.product(X,Y)
    assert X * Y == ss.product(Y,X)  # order doesn't matter
    assert X * 7 == ss.product(X,7)  # works with numbers too
    assert 7 * X == ss.product(X,7)  # __rmul__ defined properly
    assert X * 0 == 0                # __mul__ applies 0 immediately
    assert X * 1 == X                # __mul__ applies 1 immediately
    assert len(ss.product(X, 0)) == 2      # ss.product() doesn't apply anything immediately
    assert len(ss.product(X, 1)) == 2      
    # >2 inputs
    assert X * Y * Z == ss.product(X,Y,Z)
    assert X * Y * Z == ss.product(Y,Z,X)  # order doesn't matter even with 3 inputs
    assert 7 * 8 * X == ss.product(56, X)  # adds numbers until encoutering SymbolicObject
    assert X * 7 * 8 == ss.product(X, 7, 8)  # doesn't add numbers after encountering SymbolicObject
