"""
File Purpose: AbstractNumber
"""

from ..abstracts import (
    AbstractOperation,
    SimplifiableObject, simplify_op, simplify_op_skip_for,
)

class AbstractNumber(SimplifiableObject, AbstractOperation):
    '''SymbolicObject representing a number.'''
    def is_number(self):
        '''returns True, because self represents a number.'''
        return True

    def is_constant(self):
        '''returns True, because self represents a number.'''
        return True

    def evaluate(self):
        '''converts self to a numerical value. E.g. Rational(7,5) --> 1.4.
        The implementation here just raises NotImplementedError because subclasses should implement this.
        '''
        raise NotImplementedError(f'{type(self).__name__}.evaluate')


simplify_op_skip_for(AbstractNumber, '_abstract_number_evaluate')
@simplify_op(AbstractNumber, alias='_evaluate_numbers', order=-1)
def _abstract_number_evaluate(self, **kw__None):
    '''calls self.evaluate(). The idea is for this to return a numerical value,
    specifically a non-SymSolver numerical value, e.g. an integer or float.
    '''
    return self.evaluate()
