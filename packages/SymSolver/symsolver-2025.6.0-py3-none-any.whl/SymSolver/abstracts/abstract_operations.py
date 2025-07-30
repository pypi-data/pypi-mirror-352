"""
File Purpose: AbstractOperation
(directly subclasses SymbolicObject)

TODO:
    - can probably improve simplify & distribute by enforcing coefficient outside is positive.
        e.g. somewhere in simplify(), convert -7 * (a - b) --> 7 * (- a + b).
"""

import functools

from .symbolic_objects import SymbolicObject
from .operation_containers import OperationContainer

from ..initializers import INITIALIZERS
from ..defaults import DEFAULTS

from ..tools import alias


''' --------------------- Arithmetic: Abstracts --------------------- '''
# defines the most basic abstract arithmetic, outside of AbstractOperation,
# so that quick checks can refer to these functions.
# E.g. basics.sum overwrites AbstractOperation.__sum__ to first check if 0 is being added.

def _abstract_math(f):
    '''decorator which returns a function fc(self, b) that first does some small check(s), then does f.
    Those checks, right now, are:
        - if b is an OperationContaininer instance, return NotImplemented.
            This allows OperationContainer to handle the arithmetic instead.
    '''
    @functools.wraps(f)
    def f_if_b_not_operation_container(self, b):
        '''if isinstance(b, OperationContainer), returns NotImplemented. Otherwise returns f(self, b).'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if isinstance(b, OperationContainer):
            return NotImplemented
        else:
            return f(self, b)
    return f_if_b_not_operation_container

@_abstract_math
def _abstract_add(self, b):
    return self.sum(self, b)

@_abstract_math
def _abstract_radd(self, b):
    return self.sum(b, self)

@_abstract_math
def _abstract_mul(self, b):
    return self.product(self, b)

@_abstract_math
def _abstract_rmul(self, b):
    return self.product(b, self)

@_abstract_math
def _abstract_pow(self, b):
    return self.power(self, b)

@_abstract_math
def _abstract_rpow(self, b):
    return self.power(b, self)


''' --------------------- AbstractOperation --------------------- '''

class AbstractOperation(SymbolicObject):
    '''SymbolicObject along with rules for math (e.g. addition, multiplication).'''

    # Note: we can't load the sum, product, and power functions directly into this module,
    # because they are defined after the Sum, Product, and Power classes, which subclass AbstractOperation.
    # Instead, after defining each of those classes we attach those functions as attributes of AbstractOperation.
    #   e.g., after defining product (which returns a Product), set AbstractOperation.product = product.

    # # # BASIC ARITHMETIC # # #
    def __add__(self, b):
        '''return self + b'''
        return _abstract_add(self, b)

    def __mul__(self, b):
        '''return self * b'''
        return _abstract_mul(self, b)

    def __pow__(self, b):
        '''return self ** b'''
        return _abstract_pow(self, b)

    # # # "DERIVED" ARITHMETIC # # #
    def __sub__(self, b):
        '''return self - b'''
        return self + -b

    def __truediv__(self, b):
        '''return self / b'''
        return self * b**(-1)

    # # # "UNARY" ARITHMETIC # # #
    def __pos__(self):
        '''return +self'''
        return self

    def __neg__(self):
        '''return -self'''
        return -1 * self

    # # # "REVERSE" ARITHMETIC # # #
    def __radd__(self, b):
        '''return b + self'''
        return _abstract_radd(self, b)

    def __rmul__(self, b):
        '''return b * self'''
        return _abstract_rmul(self, b)

    def __rpow__(self, b):
        '''return b ** self'''
        return _abstract_rpow(self, b)

    def __rsub__(self, b):
        '''return b - self'''
        return b + -self

    def __rtruediv__(self, b):
        '''return b / self'''
        return b * self**(-1)

    # # # INITIALIZERS # # #
    sum     = property(lambda self: INITIALIZERS.sum    , doc='''alias to INITIALIZERS.sum'''    )
    product = property(lambda self: INITIALIZERS.product, doc='''alias to INITIALIZERS.product''')
    power   = property(lambda self: INITIALIZERS.power  , doc='''alias to INITIALIZERS.power'''  )

    # # # ALTERNATE PRODUCT NOTATION -- CALL # # #
    __call__ = alias('__mul__',
        doc='''alias to 'self.__mul__' --> can call instead of '*'. E.g. x(7)(y) == x*7*y.''')
