"""
File purpose: for testing vector product stuff.
"""

import SymSolver as ss

U, V, W = ss.symbols('U V W', vector=True)

def test_vector_product_hashing():
    '''test that equal objects have the same hash.

    CAUTION: be careful with the logic here.
        (contrapositive) This is TRUE: different hash implies unequal.
        (negation) This is FALSE: unequal implies different hashes.
        (inverse) This is FALSE: same hash implies equal.
    '''
    # cross products
    assert hash(U.cross(V)) == hash(U.cross(V))  # hash based on terms, not object id
    
    # box products
    h012 = hash(ss.box_product(U, V.cross(W)))
    h201 = hash(ss.box_product(W, U.cross(V)))
    h120 = hash(ss.box_product(V, W.cross(U)))
    assert h012 == h201 == h120
    h021 = hash(ss.box_product(U, W.cross(V)))
    h102 = hash(ss.box_product(V, U.cross(W)))
    h210 = hash(ss.box_product(W, V.cross(U)))
    assert h021 == h102 == h210

    # assert h012 != h021  <-- can't make this assertion; this is the negation, not the contrapositive.
