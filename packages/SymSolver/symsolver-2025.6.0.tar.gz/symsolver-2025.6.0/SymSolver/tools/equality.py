"""
File Purpose: check equality between two objects.

equals
    All SymSolver-internally-coded checks for equality between potentially-AbstractOperation objects
        should use equals(x,y), instead of x==y.
    This is because equality of objects is checked OFTEN in SymSolver, and may be time-consuming;
        Putting all these checks inside a function named "equals" allows for the potential to:
            - more easily profile how long it takes to check equality of objects
            - attempt to implement improvements, e.g. via caching some results
            (though, initial testing shows that caching all equals results actually slows the code.)
            - count how many times equality is checked
            - implement a different method named "equals" in a specific module to track the checks in just that module
            - maybe do other fun stuff too.
    Maybe it should be named _equals.
    But I didn't want to look at that underscore throughout the whole code base.

list_equals, set_equals
"""
import collections
import warnings

from .imports import ImportFailed

try:
    import numpy as np
except ImportError as err:
    np = ImportFailed('numpy', err=err)

from .numbers import is_integer
from ..defaults import DEFAULTS


''' --------------------- equals --------------------- '''

if isinstance(np, ImportFailed):
    def equals(x, y):
        '''check if x == y.

        This function is an internal implementation detail of SymSolver.
            SymSolver users can use x==y instead of equals(x,y).
        '''
        return x == y
else:  # numpy imported successfully.
    def equals(x, y):
        '''check if x == y. Returns a boolean value, even if x or y is a numpy array.
        If either is a numpy array, return np.all(x == y) instead of x == y.

        This function is an internal implementation detail of SymSolver.
            SymSolver users can use x==y instead of equals(x,y).
        '''
        result = (x == y)
        try:
            return bool(result)
        except ValueError:   # "The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()"
            return np.all(result)

"""  # to use CACHING_EQ = True, uncomment this section.
def equals(x, y, *more_args):
    '''return whether x == y.'''
    if len(more_args) > 0:
        return equals(x, y) and equals(y, more_args[0], *more_args[1:])
    # check caches.
    if CACHING_EQ:
        from_cache = _eq_cache_get(x, y) or _eq_cache_get(y, x)
        if from_cache is not None:
            return from_cache
    # do the actual work
    result = tools.equals(x, y)
    # put in cache
    if CACHING_EQ:
        _eq_cache_put(x, y, result)
        _eq_cache_put(y, x, result)
    return result

def _eq_cache_get(z, elem):
    '''get value for elem from equals cache of z.
    return True or False (the value for elem from cache) upon success;
    return None upon failure (elem wasn't in the cache).
    '''
    if hasattr(z, '_cache_eq'):
        try:
            return z._cache_eq[id(elem)]
        except KeyError:
            return None
    else:
        return None

def _eq_cache_put(z, elem, value):
    '''put elem:value in cache for equals for z.
    return False if z does not have _cache_eq and z._cache_eq cannot be created.
    return True upon success.
    '''
    if not hasattr(z, '_cache_eq'):
        try:
            setattr(z, '_cache_eq', collections.OrderedDict())
        except AttributeError:
            return False  # leave the function; we can't make a cache for this object.
    # << if we reach this line, z has _cache_eq attribute (because it already did, or we just made it.)
    z._cache_eq[id(elem)] = value
    if len(z._cache_eq) > CACHING_EQ_LEN:
        z._cache_eq.popitem(last=False)  # cache too long; forget the oldest entry.
    return True   # return True to indicate we put something.
"""

def _old_equals(x, y):#, *more_args):
    '''check if x == y.

    But also is smart about numpy arrays;
        if (x==y) returns a numpy array,
        return (x==y).all(), insead of crashing.
    (Use numpy's testing.assert_equal function to handle this elegantly.)

    if more_args exist, also check that they are equal to each other, doing one pair at a time.
    E.g. equals(x,y,z) is like x == y == z.  (compares x and y, then y and z.)

    UPDATE: testing reveals that this function was SLOW.
        So now we only use numpy if x == y gives a ValueError.
        (This occurs during e.g. bool(x == y) if x or y contains a numpy array)
    '''
    #if len(more_args) > 0:
    #    return equals(x, y) and equals(y, more_args[0], *more_args[1:])
    if x is y:
        return True
    try:
        return bool(x == y)
    except ValueError:
        pass            # if we can't do bool(result), assume result is an array.
    # use np.testing.assert_equal.
    #   that func can make visible deprecation warning though, even when
    #   numpy arrays are not involved originally. We suppress that warning.
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
        try:
            np.testing.assert_equal(x, y)
        except AssertionError:
            return False
        else:
            return True

_equals = equals  # alias to equals, used in methods below.

''' --------------------- equals for lists, dicts, sets --------------------- '''
# return whether lists, dicts, sets are equal, using equals to check equality instead of ==

def list_equals(x, y, equals=None):
    '''return whether lists x and y are equal.
    if equals is entered, use it to compare all elements.
    otherwise, try using x == y, but use _equals if that makes a ValueError.
        _equals is tools.equals; does '==' usually, but is smart about numpy arrays.
    '''
    if equals is None:
        try:
            return x == y
        except ValueError:  # "The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()"
            equals = _equals
    if len(x) != len(y):
        return False
    return all(equals(x[i], y[i]) for i in range(len(x)))

def dict_equals(x, y, equals=None):
    '''return whether dicts x and y are equal.
    if equals is entered, use it to compare all values.
    otherwise, try using x == y, but use _equals if that makes a ValueError.
        _equals is tools.equals; does '==' usually, but is smart about numpy arrays.
    '''
    if equals is None:
        try:
            return x == y
        except ValueError:  # "The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()"
            equals = _equals
    if x.keys() != y.keys():
        return False
    return all(equals(x[key], y[key]) for key in x)

def unordered_list_equals(x, y, equals=equals):
    '''return whether lists x and y contain the same elements, possibly in different order.
    equal if there exists f such that for all i, x[i] == y[f(i)],
        and f(i1) == f(i2) if and only if i1 == i2.  (i.e. no repeated results)

    CAUTION: this is different from equality of sets, because it considers repeats as well.
        For example, set([1,1,2])==set([1,2,2]), but unordered_list_equals([1,1,2],[1,2,2]) is False.

    equals: callable, default is basically just '==' but instead does np.all for numpy arrays
        how to test for equality. Ignored if all elements in x and y are hashable.
        Also ignored if x and y have different lengths (since then the answer is always False).
    '''
    # quick check - if lengths don't match, definitely not equal.
    if len(x) != len(y):
        return False
    # for efficiency, attempt comparison using hashing.
    try:
        xcounts = collections.Counter(x)  # {elem:count for elem in x} (only works if all hashable)
        ycounts = collections.Counter(y)
    except TypeError:  # unhashable type encountered
        pass  # handled after the 'else' block
    else:  # fully hashable, can just compare as sets
        return xcounts == ycounts
    # hashing comparison failed; loop through elements individually.
    iiy = list(range(len(y)))
    for xi in x:
        for j, iy in enumerate(iiy):
            if equals(xi, y[iy]):
                iiy.pop(j)
                break
        else:  # didn't break
            return False
    return True

def equal_sets(x, y, equals=equals):
    '''returns whether x and y are equal in the sense of sets.
    equal when:
        for i in x, i in y, AND for j in y, j in x.

    result will be equivalent to Set(x) == Set(y), where Set is tools.sets.Set,
    however equal_sets(x, y) is more efficient in terms of speed.

    (not named set_equals to avoid ambiguity... this function doesn't *set* anything.)
    '''
    # loop through terms, pop same terms until all are popped or one is missing.
    y = [t for t in y]
    popped = []
    for term in x:
        j = 0
        found_match = False
        while j < len(y):
            if equals(term, y[j]):
                yjpop = y.pop(j)    # we found a match for y[j]; it is term.
                if not found_match:        # if this is the first match to term, record it,
                    popped.append(yjpop)   # so that later we can compare terms against popped.
                found_match = True
            else:
                j += 1
        if (not found_match) and (not any(equals(term, z) for z in popped)):
            return False
    if len(y) > 0:   # there is at least 1 element in y which was not in x.
        return False
    return True


''' --------------------- equals for integers --------------------- '''

def int_equals(x, y):
    '''return whether x and y are both integers (via is_integer) and x==y.
    This may be helpful e.g. if x or y overwrite __eq__ to return a non-boolean,
    e.g. if x or y are numpy arrays.
    '''
    return is_integer(x) and is_integer(y) and x==y