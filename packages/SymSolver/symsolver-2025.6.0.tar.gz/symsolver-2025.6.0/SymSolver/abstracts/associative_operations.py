"""
File Purpose: AssociativeObject, AssociativeOperation

Note, right now this class just adds the _flatten() simplification option.
"""
from .abstract_operations import AbstractOperation
from .iterable_symbolic_objects import IterableSymbolicObject
from .simplifiable_objects import (
    SimplifiableObject,
    simplify_op,
    expand_op,
)


''' --------------------- AssociativeObject --------------------- '''

class AssociativeObject(IterableSymbolicObject, SimplifiableObject):
    '''Iterable and Simplifiable object with the associative property.'''
    pass # no methods in particular to put here, yet.


''' --------------------- AssociativeObject SIMPLIFY_OPS --------------------- '''

@expand_op(AssociativeObject, alias='_flatten')
@simplify_op(AssociativeObject, alias='_flatten')
def _associative_flatten(self, **kw__None):
    '''flattens top layer of self. E.g. Product(x, Product(y, z)) --> Product(x, y, z)
    Only hits top layer, e.g. P(x,P(P(u,v),z)) --> P(x,P(u,v),z)

    [TODO][EFF] faster to use list comprehension?

    Note: this function is in SIMPLIFY_OPS *and* EXPAND_OPS.
        It clearly makes expressions simpler.
        It is just also useful to apply it while expanding things,
            since commonly expand ops may lead to results which could be flattened.
    '''
    terms = []
    flattened_any = False
    for t in self:
        if isinstance(t, type(self)):
            terms += list(t) # t._associative_flatten
            flattened_any = True
        else:
            terms += [t]
    if not flattened_any:
        return self  # return self, exactly, to help indicate no changes were made.
    else:
        return self._new(*terms)


''' --------------------- AssociativeOperation --------------------- '''

class AssociativeOperation(AssociativeObject, AbstractOperation):
    '''AssociativeObject which is also an Operation.
    [TODO] might remove this class and ask subclasses to just subclass AbstractOperation too.'''
    pass   # nothing to do here...