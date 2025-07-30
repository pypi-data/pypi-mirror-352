"""
File Purpose: canonical ordering for SymbolicObjects.

Canonical ordering is an implementation detail,
not guaranteed to remain the same as SymSolver updates.
The goal is that equal objects will be treated the same by this ordering, even if not the same object.
E.g. sum1 = symbol('x') * 7; sum2 = symbol('x') * 7;
    sum1 & sum2 are not the same object but sum1==sum2.
    We guarantee: canonical_ordering(*objs, sum1) == canonical_ordering(*objs, sum2).
"""
from ._complexity import complexity
from .commutative_operations import CommutativeObject
from .iterable_symbolic_objects import IterableSymbolicObject
from .simplifiable_objects import simplify_op, simplify_op_skip_for
from .symbolic_objects import SymbolicObject

from ..attributors import attributor
from ..errors import warn
from ..tools import (
    equals,
    caching_attr_simple,
    caching_property_simple, weakref_property_simple,
    Binding,
)

from ..defaults import DEFAULTS, ZERO

binding = Binding(locals())


''' --------------------- Convenience --------------------- '''

@attributor
def canonical_orderer(x):
    '''returns x.canonical_orderer() if avabilable, else CanonicalOrderer(x).'''
    try:
        x_canonical_orderer = x.canonical_orderer
    except AttributeError:
        return CanonicalOrderer(x)
    else:
        return x_canonical_orderer()

def canonical_sort(iterable):
    '''returns args sorted in canonical order.'''
    return sorted(iterable, key=canonical_orderer)

def canonical_argsort(iterable):
    '''returns indices such that [args[i] for i in result] is args sorted in canonical order.'''
    list_ = list(iterable)
    indices = list(range(len(list_)))
    sortkey = (lambda i: canonical_orderer(list_[i]))
    return sorted(indices, key=sortkey)


''' --------------------- CanonicalOrderer --------------------- '''

class CanonicalOrderer():
    '''helps with ordering.
    Assumes obj will not change after being input (i.e. does some caching...)

    provides comparison methods returning results for canonical ordering.

    comparison checks (using first one where comparison is available & not equal results).
        1) complexity(...) for obj and target
        2) str(type(...)) for obj and target
        3) getattr(..., '_canonical_ordering_key')() for obj and target, if available, else None

    also checks:
        4) equals(obj, target)

    for equality comparison, also checks:
        0) obj is target (return True immediately if True)
    '''
    def __init__(self, obj):
        self.obj = obj

    _ATTRS_CMP = ('complexity', 'typestr', 'orderkey')

    # # # PROPERTIES # # #
    obj = weakref_property_simple('_obj', 'obj for which I am a CanonicalOrderer.')

    @caching_property_simple
    def complexity(self):
        '''complexity(self.obj)'''
        return complexity(self.obj)

    @caching_property_simple
    def typestr(self):
        '''str(type(self.obj))'''
        return str(type(self.obj))

    @caching_property_simple
    def orderkey(self):
        '''getattr(self.obj, '_canonical_ordering_key', '')'''
        try:
            cok = self.obj._canonical_ordering_key
        except AttributeError:
            return ''
        else:
            return cok()

    # # # ORDERING # # #
    def _attrs_cmp_lt(self, y):
        '''returns (self < y) or None if (self < y) inconclusive, by comparing self._ATTRS_CMP attrs.
        Assumes y is a CanonicalOrderer.
        '''
        for attr in self._ATTRS_CMP:
            attx = getattr(self, attr)
            atty = getattr(y, attr)
            if attx < atty:
                return True
            elif attx > atty:
                return False
        # all attrs equal --> inconclusive
        return None

    def _equals_y(self, y):
        '''returns whether self.obj is y.obj or equals(self.obj, y.obj).
        Assumes y is a CanonicalOrderer.
        '''
        xobj, yobj = self.obj, y.obj
        return (xobj is yobj) or equals(xobj, yobj)

    def __lt__(self, y):
        '''self < y'''
        if not isinstance(y, CanonicalOrderer): return NotImplemented
        acl = self._attrs_cmp_lt(y)
        if acl is not None:
            return acl
        if self._equals_y(y):
            return False
        try:
            result = self.obj < y.obj  # might fail with TypeError if operation not defined.
            return bool(result)        # might fail with ValueError if numpy array
        except (TypeError, ValueError):
            if DEFAULTS.DEBUG_CANONICAL_ORDER:
                warn(f'canonical order not unique for objects with types: {self.typestr} and {y.typestr}')
            return False

    def __gt__(self, y):
        '''self > y'''
        if not isinstance(y, CanonicalOrderer): return NotImplemented
        acl = self._attrs_cmp_lt(y)
        if acl is not None:
            return (not acl)
        if self._equals_y(y):
            return False
        try:
            result = self.obj > y.obj  # might fail with TypeError if operation not defined.
            return bool(result)        # might fail with ValueError if numpy array
        except (TypeError, ValueError):
            if DEFAULTS.DEBUG_CANONICAL_ORDER:
                warn(f'canonical order not unique for objects with types: {self.typestr} and {y.typestr}')
            return False

    def __le__(self, y):
        '''self <= y'''
        if not isinstance(y, CanonicalOrderer): return NotImplemented
        if self.obj is y.obj:
            return True
        acl = self._attrs_cmp_lt(y)
        if acl is not None:
            return acl
        return equals(self.obj, y.obj)

    def __ge__(self, y):
        '''self >= y'''
        if not isinstance(y, CanonicalOrderer): return NotImplemented
        if self.obj is y.obj:
            return True
        acl = self._attrs_cmp_lt(y)
        if acl is not None:
            return (not acl)
        return equals(self.obj, y.obj)

    def __eq__(self, y):
        '''self == y'''
        if not isinstance(y, CanonicalOrderer): return NotImplemented
        if self.obj is y.obj:
            return True
        acl = self._attrs_cmp_lt(y)
        if acl is not None:
            return False  # deinitively > or <.
        return equals(self.obj, y.obj)

    @caching_attr_simple
    def __hash__(self):
        return hash((type(self), self.obj))


''' --------------------- Canonical Orderer bind to classes --------------------- '''

# canonical_orderer(symbolic_object) --> CanonicalOrderer(symbolic_object), by default.
with binding.to(SymbolicObject):
    @binding
    def canonical_orderer(self):
        '''returns CanonicalOrderer(self). Helps with canonical_sort & argsort'''
        return CanonicalOrderer(self)

# canonical_order_key
with binding.to(IterableSymbolicObject):
    @binding
    def _canonical_ordering_key(self):
        '''returns tuple of (len(self), *(canonical_orderer(term) for term in self))
        Helps with canonical_sort & argsort.
        '''
        return (len(self), *(canonical_orderer(term) for term in self))


''' --------------------- Simplify Ops --------------------- '''

simplify_op_skip_for(CommutativeObject, '_commutative_canonical_reorder')

@simplify_op(CommutativeObject, alias='_canonical_reorder')
def _commutative_canonical_reorder(self, **kw__None):
    '''returns self but rearranged to put terms in the canonical order.'''
    self_terms = list(self)
    result = canonical_argsort(self_terms)
    if all(i==j for i, j in zip(result, range(len(result)))):
        return self  # return self, exactly, to help indicate nothing was changed.
    return self._new(*(self_terms[i] for i in result))
