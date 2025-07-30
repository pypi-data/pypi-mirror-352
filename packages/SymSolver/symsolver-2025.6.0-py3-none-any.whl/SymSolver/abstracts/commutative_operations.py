"""
File Purpose: CommutativeObject, CommutativeOperation,
"""
import collections
from .abstract_operations import AbstractOperation
from .iterable_symbolic_objects import IterableSymbolicObject
from .simplifiable_objects import (
    SimplifiableObject,
    simplify_op,
    expand_op,
)

from .symbolic_objects import (
    is_number, _equals0,
    is_nonsymbolic,
)
from ..tools import (
    apply, dichotomize,
    caching_attr_simple,
    equals, unordered_list_equals,
)


''' --------------------- CommutativeObject --------------------- '''

class CommutativeObject(IterableSymbolicObject, SimplifiableObject):
    '''Iterable and Simplifiable object with the commutative property.'''
    def __eq__(self, b):
        try:
            return super(IterableSymbolicObject, self).__eq__(b)  # skip IterableSymbolicObject's __eq__.
        except NotImplementedError:
            return unordered_list_equals(self, b)

    @caching_attr_simple
    def __hash__(self):
        return hash((type(self), frozenset(collections.Counter(self.terms).items())))
        # IterableSymbolicObject.__hash__ insufficient because it depends on terms order,
        #   so equal objects would have different hashes.
        # Could use set(self.terms), that is fine since unequal objects are allowed to share the same hash,
        #   but it does ignore duplicates in self.terms, which is not ideal.
        # If frozenset(Counter(self.terms).items()) is too slow, could try using set(self.terms) instead.

    def split(self, func):
        '''splits self by func.
        returns ( self._new(terms such that func(term)), self._new(terms such that func(term)) ).
        if all terms in self have func(term) (or all not func(term)),
            uses self, exactly, instead of self._new, to help indicate nothing was changed.
            (Edge case: if len(self) == 0, return (self, self._new()).)
        '''
        ftrue, ffalse = self.dichotomize(func)
        newtrue  = self
        newfalse = self
        if len(ftrue) == len(self):
            newtrue  = self
            newfalse = self._new(*ffalse)
        else:
            newtrue  = self._new(*ftrue)
            newfalse = self if (len(ffalse) == len(self)) else self._new(*ffalse)
        return (newtrue, newfalse)

    def split_numeric_component(self):
        '''returns (numeric component, non-numeric component) of self.
        if there are no is_number(term) terms in self, non-numeric component will be self, exactly.
        if there are only is_number(term) terms in self, numeric component will be self, exactly.
        '''
        return self.split(is_number)


''' --------------------- CommutativeObject SIMPLIFY_OPS --------------------- '''

@simplify_op(CommutativeObject, alias='_simplify_id')
def _commutative_simplify_id(self, **kw__None):
    '''removes any IDENTITY at top level of self.'''
    try:
        IDENTITY = self.IDENTITY
    except AttributeError:
        return self
    else:
        keep_terms = [term for term in self if not equals(term, self.IDENTITY)]
        if len(keep_terms) == len(self):
            return self  # return self, exactly, to help indicate no changes were made.
        else:
            return self._new(*keep_terms)


''' --------------------- CommutativeOperation --------------------- '''

class CommutativeOperation(CommutativeObject, AbstractOperation):
    '''Iterable and Simplifiable operation with the commutative property.'''
    pass


''' --------------------- CommutativeOperation SIMPLIFY_OPS --------------------- '''

@expand_op(CommutativeOperation, alias='_evaluate_numbers')
@simplify_op(CommutativeOperation, alias='_evaluate_numbers', order=1)
def _commutative_evaluate_numbers(self, **kw):
    '''combines numbers in self by doing self.OPERATION on terms which are numbers.
    Uses Commutative property to provide a result in which the numbers are combined as much as possible.
    This is applied during expand AND simplify, by default.
    '''
    OPERATION = getattr(self, 'OPERATION', None)
    if OPERATION is None:
        return self
    # group terms by number / not a number
    numeric, other = dichotomize(self, is_number)
    if len(numeric) < 2:
        return self  # return self, exactly, to help indicate nothing was changed.
    # combine numeric terms
    number = OPERATION(*numeric)
    if isinstance(number, type(self)) and len(number) == len(numeric):  # combined nothing...
        # combine ONLY the non-symbolic terms.
        nonsymb, symb = dichotomize(numeric, is_nonsymbolic)
        if len(nonsymb) < 2:
            return self  # return self, exactly, to help indicate nothing was changed.
        number = OPERATION(*nonsymb)
        return self._new(number, *symb, *other)
    else:
        return self._new(number, *other)
