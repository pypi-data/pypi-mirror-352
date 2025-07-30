"""
File Purpose: provide convenient methods for the vectors subpackage.
"""

from ..attributors import attributor
from ..abstracts import (
    _equals0, is_constant,
)
from ..basics import (
    get_factors,
)
from ..errors import VectorialityError
from ..tools import (
    equals,
    dichotomize,
)
from ..initializers import INITIALIZERS
from ..defaults import ONE


''' --------------------- Convenience Functions --------------------- '''

@attributor
def is_vector(x):
    '''returns whether x is a vector, by checking x.is_vector().
    if x.is_vector isn't available, return None if x==0, else False.
    '''
    try:
        return x.is_vector()
    except AttributeError:
        if _equals0(x):
            return None
        else:
            return False

def is_unit_vector(x):
    '''returns whether x is a unit vector, i.e. x.is_vector() and x.magnitude()==1.'''
    try:
        return x.is_vector() and equals(x.magnitude(), ONE)
    except AttributeError:
        return False

def is_constant_scalar(x):
    '''returns whether x is a constant scalar, i.e. is_constant(x) and not is_vector(x)'''
    return is_constant(x) and not is_vector(x)

def vectoriality(x):
    '''returns is_vector(x). This is True for vectors, None for 0, False for non-zero non-vectors.'''
    return is_vector(x)

def first_nonzero_vectoriality(*terms):
    '''returns vectoriality of first nonzero term.
    iterates through terms, checking vectoriality:
        if None, continue iterating. otherwise return result.
    if there are no non-None vectorialities, return None.
    '''
    for term in terms:
        result = vectoriality(term)
        if result is not None:
            return result
    return None  # (no non-None vectorialities)

def strictest_vectoriality(*terms):
    '''returns strictest vectoriality of all provided terms, or raises VectorialityError if they are incompatible.
    vectoriality is True for vectors, None for 0, False otherwise.
    strictness determined by True > None, False > None, True incompatible with False.
    for 0 terms, the result will be None.
    '''
    if len(terms) == 0:
        return None
    result = vectoriality(terms[0])
    for t in terms[1:]:
        vralt = vectoriality(t)
        if vralt is None:
            pass  # result unaffected by vralt.
        elif result is None:
            result = vralt
        elif vralt == result:
            pass  # result still compatible with vralt.
        else:
            raise VectorialityError(f'vectorialities incompatible: {vralt}, {result}')
    return result

def any_vectoriality(*terms):
    '''returns True if any term's vectoriality is True,
    else None if all terms' vectorialities are None,
    else False (if at least one term has vectoriality False).
    '''
    result = None
    for term in terms:
        vralt = vectoriality(term)
        if vralt:
            return True
        elif result is None:
            result = vralt
    return result

def same_rank(x, y):
    '''returns whether x and y have the same rank.
    i.e. vectoriality(x) == vectoriality(y) or one of them is None.
    '''
    vralx = vectoriality(x)
    if vralx is None:
        return True
    vraly = vectoriality(y)
    if vraly is None:
        return True
    return vralx == vraly

def get_matching_nonNone_vectoriality(u, v, errmsg=None):
    '''returns vectoriality(u), assuming it equals vectoriality(v) and is non-None.
    raise VectorialityError(errmsg) if this is impossible
    (due to u or v being 0, or vector u and non-vector v, or non-vector u and vector v).
    
    if errmsg is None, use:
        f"Vectorialities do not match! u or v is 0, or is_vector(u)!=is_vector(v). For u={u}, v={v}.".
    '''
    vralu = vectoriality(u)
    vralv = vectoriality(v)
    if (vralu == vralv) and (vralu is not None):
        return vralu
    else:
        if errmsg is None:
            errmsg = f"Vectorialities do not match! u or v is 0, or is_vector(u)!=is_vector(v). For u={u}, v={v}."
        raise VectorialityError(errmsg)

def scalar_vector_get_factors(x, vector_if_None=True):
    '''returns (scalar factors of x, vector factors of x)
    vector_if_None: bool, default True
        whether to treat objects with is_vector(obj) == None as vectors.
        True  --> returns (definitely scalars,  possibly  vectors)
        False --> returns ( possibly  scalars, definitely vectors)'''
    factors = get_factors(x)
    if vector_if_None:
        return dichotomize(factors, lambda u: is_vector(u)==False)
    else:
        return dichotomize(factors, lambda u: is_vector(u)!=True)

def scalar_vector_product_split(x):
    '''returns (product of scalar factors of x, product of vector factors of x).'''
    scalar_factors, vector_factors = scalar_vector_get_factors(x)
    scalar_product = INITIALIZERS.product(*scalar_factors)
    vector_product = INITIALIZERS.product(*vector_factors)  # note: product() might raise error if more than 1 vector.
    return (scalar_product, vector_product)
