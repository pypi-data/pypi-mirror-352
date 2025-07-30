"""
File Purpose: LinearOperation

stores operation in GenericOperation format, i.e. tracking opeartor and operand.
also provides linear behavior:
    f(ax + by) = a f(x) + b f(y), for all variables x, y, and "constants" a, b.

[TODO] implement the "reverse" i.e. a f(x) + b f(y) --> f(ax + by)
"""

from .generic_operations import GenericOperation
from .linear_operators import LinearOperator
from ..abstracts import (
    expand_op,
    simplify_op,
)
from ..basics import (
    get_summands, get_factors,
    Product,
)
from ..tools import (
    equals,
    dichotomize,
)


class LinearOperation(GenericOperation):
    '''linear operation which tracks operator and operand.
    E.g. f(x) but keep the f and x, rather than evaluating anything.

    Linear behavior: f(ax + by) = a f(x) + b f(y), for all variables x, y, and "constants" a, b.

    To determine what counts as constant, uses f.treats_as_constant(value)
        (by default, just returns is_constant(value))
    '''
    def __init__(self, linear_operator, operand, **kw):
        '''raise TypeError if linear_operator is not a LinearOperator instance.'''
        if not isinstance(linear_operator, LinearOperator):
            raise TypeError(f'expected LinearOperator but got {type(linear_operator)}')
        super().__init__(linear_operator, operand, **kw)

    def treats_as_constant(self, value):
        '''returns whether self treats value as a constant, in the sense of linearity,
        which allows f(cx) --> c f(x).

        The implementation here just returns self.operator.treats_as_constant(value).
        '''
        return self.operator.treats_as_constant(value)

    def _treats_as_distributable_constant(self, value):
        '''returns whether self treats value as a constant which can be distributed.
        "distribute" meaning f(ax + by) --> a f(x) + b f(y).

        The implementation here just returns self.operator.treats_as_constant(value).
        '''
        return self.operator._treats_as_distributable_constant(value)


''' --------------------- LinearOperation SIMPLIFY AND EXPAND OPS --------------------- '''

@expand_op(LinearOperation, alias='_distribute')
@simplify_op(LinearOperation, alias='_simplifying_distribute')
def _linear_operation_distribute(self, **kw__None):
    '''distributes using linearity: f(ax + by) = a f(x) + b f(y),
    for all variables x, y, and "constants" a, b.

    to determine what counts as "constant", use f._treats_as_distributable_constant(value)
        note: if that is None (to indicate "answer unknown"), do not distribute.
        by default, this is just (f.treats_as_constant(value) and not is_vector(value)).
    '''
    summands = get_summands(self.operand)
    distributed_any = len(summands) > 1

    result = []   # list of (outside_factors, operand), for summands in result.
    for summand in summands:
        # separate into outside_factors, inside_factors. outside will be all scalar constant factors.
        factors = get_factors(summand)
        outside_factors, inside_factors = dichotomize(factors, self._treats_as_distributable_constant)
        # put (outside_factors for this summand, operand for this summand) into result.
        if len(inside_factors) == 0:
            # use Product.IDENTITY for operand. But first check to ensure we don't do f(1) --> 1 * f(1).
            if (len(outside_factors) == 1) and equals(outside_factors[0], Product.IDENTITY):
                # looks like f(1). Don't change anything here; no reason to do 1 * f(1).
                # distributed_any doesn't change, because this summand remains unaffected.
                result.append(((), summand))  # note: summand == Product.IDENTITY, here.
            else:  # len(outside_factors) > 0, since len(factors) >= 1 is guaranteed.
                distributed_any = True
                result.append((outside_factors, Product.IDENTITY))
        elif len(outside_factors) > 0:
            distributed_any = True
            result.append((outside_factors, self.product(*inside_factors)))
        else:
            # distributed_any doesn't change, because this summand remains unaffected.
            result.append(((), summand))

    if not distributed_any:
        return self  # return self, exactly, to help indicate nothing was changed.

    final_result = self.sum(*(self.product(*outside_factors, self._new_from_operand(operand))
                              for outside_factors, operand in result))
    return final_result
