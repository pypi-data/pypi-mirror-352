"""
File Purpose: GenericOperation
instances of GenericOperation track an operator and an operand.

Specifically, this class deals with AbstractOperations where the Operator stores some variable info.
    This is useful when dealing with types of operators which have some parameters to control behavior.
    For example, all MultiSumOperator ("big sigma summation notation") objects behave in a similar way,
        but the exact details of the summation vary depending on the indices and summation variable.
    Another example is the DerivativeOperator (defined in the calculus subpackage),
        because the exact details depend on the "differentiator" (e.g. 'x' in d/dx).
    A non-example is any Operator which returns a result in terms of Sum, Product, and Power.
        E.g. for f: x --> x^2 + 3, there is no need to track the Operator after evaluation;
        f(y) becomes y^2 + 3, and f(10) becomes 103.
"""

from .abstract_operators import (
    AbstractOperator,   # just used for type-hinting about Operator.
)
from ..abstracts import (
    BinarySymbolicObject, SimplifiableObject,
    AbstractOperation, SubbableObject,
    simplify_op, simplify_op_skip_for,
)
from ..errors import PatternError
from ..tools import (
    _str,
)


class GenericOperation(BinarySymbolicObject, SimplifiableObject,
                       AbstractOperation, SubbableObject):
    '''generic operation which tracks operator and operand.
    E.g. f(x) but keep the f and x, rather than evaluating anything.
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, operator: AbstractOperator, operand, **kw):
        super().__init__(operator, operand, **kw)

    operator = property(lambda self: self.t1, doc='''operator, e.g. f in f(x)''')
    operand = property(lambda self: self.t2, doc='''operand, e.g. x in f(x)''')

    def _new_from_operand(self, operand, **kw):
        '''make new instance using self.operator and the operand entered here.
        implementation note: this is different from self._new, because self._new must accept 2 args,
            so that self still behaves like a BinarySymbolicObject during creation/initialization.
        '''
        return self._new(self.operator, operand, **kw)

    # # # EVALUATE # # #
    def evaluate(self):
        '''tries to evaluate self.
        returns self.operator.evaluate(self.operand), if possible,
        else self.operator(self.operand), if that provides a different result than self,
        else self.
        '''
        operator = self.operator
        operand = self.operand
        try:
            return operator.evaluate(operand)
        except AttributeError:
            pass  # that's fine, try something else (see below)
        result = operator(operand)
        # check if result would be the same as self; return self if so.
        # (note: this check is super fast, thanks to using 'is' instead of '=='.)
        if (type(result)==type(self)) and (result.operator is operator) and (result.operand is operand):
            return self  # return self, exactly, to help indicate nothing was changed.
        else:
            return result

    # # # STR # # #
    def __str__(self, **kw):
        '''returns f'{self.operator}({self.operand})'.
        [TODO] option to remove the parentheses?
            Or maybe that option will be accomplished by having subclasses override __str__.
        '''
        str_operator = _str(self.operator, **kw)
        str_operand = _str(self.operand, **kw)
        return f'{str_operator}({str_operand})'


''' --------------------- GenericOperation SIMPLIFY_OPS --------------------- '''

simplify_op_skip_for(GenericOperation, '_generic_operation_evaluate')  # skip by default.
@simplify_op(GenericOperation, alias='_evaluate_operations')
def _generic_operation_evaluate(self, **kw__None):
    '''evaluates GenericOperation instances at top layer of self.
    For example, MultiSumOperations with well-defined indices turn into Sums.
    '''
    self_evaluate = self.evaluate   # (this is a function)
    try:
        return self_evaluate()
    except PatternError:
        return self
