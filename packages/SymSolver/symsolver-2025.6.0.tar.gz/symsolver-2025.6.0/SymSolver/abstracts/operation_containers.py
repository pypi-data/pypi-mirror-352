"""
File Purpose: OperationContainer
(directly subclasses IterableSymbolicObject)
"""

from .iterable_symbolic_objects import IterableSymbolicObject
from ..defaults import DEFAULTS
from ..tools import (
    alias,
    format_docstring,
    BINARY_MATH_OPERATORS,
)

class OperationContainer(IterableSymbolicObject):
    '''contains Symbolic objects, and applies operations to all objects in self.

    E.g. (LHS = RHS) + x --> LHS + x = RHS + x
    '''
    def apply_operation(self, operation, *, _prevent_new=False):
        '''return self with operation applied to objects contained in self.
        if _prevent_new, and all resulting objects are unchanged (via 'is'), return self.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        opped = [operation(t) for t in self]
        if _prevent_new and all(opi is selfi for opi, selfi in zip(opped, self)):
            return self
        else:
            return self._new(*opped)

    op = alias('apply_operation')

    def apply_binary_operation(self, operation, x, *, _prevent_new=False, reverse=False):
        '''return self with operation(obj, x) applied to objs contained in self.
        if _prevent_new, and all resulting objects are unchanged (via 'is'), return self.

        Equivalent: self.op(lambda t: operation(t, x))

        if reverse, apply operation(x, obj) instead.
        (then, equivalent to self.op(lambda t: operation(x, t))
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        opped = [operation(x, t) for t in self] if reverse else [operation(t, x) for t in self]
        if _prevent_new and all(opi is selfi for opi, selfi in zip(opped, self)):
            return self
        else:
            return self._new(*opped)

    bop = alias('apply_binary_operation')

    def apply_binary_operation_elementwise(self, operation, xlist, *, _prevent_new=False):
        '''return self-like object made from operation(obj, x) for (obj, x) in zip(self, xlist).
        if _prevent_new, and all resulting objects are unchanged (via 'is'), return self.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        opped = [operation(t, x) for t, x in zip(self, xlist)]
        if _prevent_new and all(opi is selfi for opi, selfi in zip(opped, self)):
            return self
        else:
            return self._new(*opped)

    bopwise = alias('apply_binary_operation_elementwise')


# # # ARITHMETIC # # #
# e.g. def __add__(self, x): return self.bop(operator.__add__, x)
#   but, uses a loop to do it for all operators in BINARY_MATH_OPERATORS.
def _operation_container_math(op):
    @format_docstring(op=op)
    def do_operation_container_op(self, x):
        '''returns self.bop({op}, x)'''
        return self.bop(op, x)
    return do_operation_container_op

for opstr, op in BINARY_MATH_OPERATORS.items():
    setattr(OperationContainer, opstr, _operation_container_math(op))
