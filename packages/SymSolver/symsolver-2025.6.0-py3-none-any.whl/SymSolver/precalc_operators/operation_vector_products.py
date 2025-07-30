"""
File Purpose: OperationBinaryVectorProduct, and DotOperation

OperationBinaryVectorProduct:
    (f dot u) or (f cross u) with f an operator, u not an operator.
DotOperation:
    (g dot f)(u) with f an operator, g anything, u not an operator.
    This is necessary when u is a vector.
    [TODO] make more generic, e.g. for any product?
"""

from .generic_operations import GenericOperation
from .operators_tools import is_operator
from ..vectors import (
    BinaryVectorProduct,
    DotProductBase, 
    CrossProductBase,
    is_vector,
)


class OperationBinaryVectorProduct(BinaryVectorProduct, GenericOperation):
    '''BinaryVectorProduct where the first term is an operator and the second is not.'''
    def __init__(self, v1, v2, **kw):
        '''ensure first term is an operator and the second is not.'''
        if not is_operator(v1):
            raise TypeError(f'expected operator v1 but got non-operator with type={type(v1)}')
        if is_operator(v2):
            raise TypeError(f'expected non-operator v2 but got operator with type={type(v2)}')
        BinaryVectorProduct.__init__(self, v1, v2, **kw)  # (self.t1, self.t2) = (v1, v2)
        GenericOperation.__init__(self, v1, v2, **kw)  # (self.operator, self.operand) = (v1, v2)

    __str__ = BinaryVectorProduct.__str__


class OperationDotProduct(DotProductBase, OperationBinaryVectorProduct):
    '''dot product where the first term is an Operator and the second term is not.'''
    def evaluate(self):
        '''tries to evaluate self.
        returns self.operator.dot_evaluate(self.operand), if possible,
        else self.operator.__dot_call__(self.operand), if that provides a different result than self,
        else self.
        '''
        operator = self.operator
        operand = self.operand
        try:
            return operator.dot_evaluate(operand)
        except AttributeError:
            pass  # that's fine, try something else (see below)
        result = operator.__dot_call__(operand)
        # check if result would be the same as self; return self if so.
        # (note: this check is super fast, thanks to using 'is' instead of '=='.)
        if (type(result)==type(self)) and (result.operator is operator) and (result.operand is operand):
            return self  # return self, exactly, to help indicate nothing was changed.
        else:
            return result


class OperationCrossProduct(CrossProductBase, OperationBinaryVectorProduct):
    '''cross product where the first term is an Operator and the second term is not.'''
    def evaluate(self):
        '''tries to evaluate self.
        returns self.operator.cross_evaluate(self.operand), if possible,
        else self.operator.__cross_call__(self.operand), if that provides a different result than self,
        else self.
        '''
        operator = self.operator
        operand = self.operand
        try:
            return operator.cross_evaluate(operand)
        except AttributeError:
            pass  # that's fine, try something else (see below)
        result = operator.__cross_call__(operand)
        # check if result would be the same as self; return self if so.
        # (note: this check is super fast, thanks to using 'is' instead of '=='.)
        if (type(result)==type(self)) and (result.operator is operator) and (result.operand is operand):
            return self  # return self, exactly, to help indicate nothing was changed.
        else:
            return result


class DotOperation(GenericOperation):
    '''DotProduct where t2 is an operator, called on an operand.
    (u dot f)(g) with f an operator, u not an operator, g anything.
    '''
    def __init__(self, dot_product_object, operand, **kw):
        '''ensure first term is an operator and a DotProduct, and second term is not an operator.'''
        if not is_operator(dot_product_object):
            raise TypeError(f'expected operator but got non-operator with type={type(dot_product_object)}')
        if not isinstance(dot_product_object, DotProductBase):
            raise TypeError(f'expected DotProduct but got object with type={type(dot_product_object)}')
        if is_operator(operand):
            raise TypeError(f'expected non-operator operand but got operator with type={type(operand)}')
        super().__init__(dot_product_object, operand, **kw)

    def is_vector(self):
        '''returns whether self is a vector, i.e. whether self.operand is a vector.'''
        return is_vector(self.operand)
