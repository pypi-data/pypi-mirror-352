"""
File Purpose: LinearOperator

What can a LinearOperator do??
LinearOperation of course can simplify f(ax + by) = a f(x) + b f(y).
But with just operators?
    Maybe notice that linear f and g implies linear f o g
    Is there anything else actually useful...?
"""

from .abstract_operators import AbstractOperator
from ..abstracts import is_constant
from ..vectors import is_vector

class LinearOperator(AbstractOperator):
    '''Operator with linear behavior, i.e. f(ax + by) = a f(x) + b f(y),
    for all variables x, y, and "constants" a, b.

    Note that a, b only need to be values which f "treats as constant".
    For example, a sigma-notation sum like "sum from i=1 to i=10 of x*i*3"
        will actually treat anything without an 'i' in it as constant,
        so the x can be pulled out of the sum.
    By default, whether self "treats c as constant" is just is_constant(c)
    '''
    def treats_as_constant(self, c):
        '''returns whether self treats c as constant.
        (if so, then the LinearOperation self(cx) can be turned into c * self(x).)
        The implementation here just checks is_constant(c), but subclasses may override this method.
        '''
        return is_constant(c)

    def _treats_as_distributable_constant(self, value):
        '''returns whether self treats value as a constant which can be distributed.
        "distribute" meaning f(ax + by) --> a f(x) + b f(y).
        The implementation here returns whether self.treats_as_constant(value) AND value is not a vector.
        '''
        return (not is_vector(value)) and (self.treats_as_constant(value))
