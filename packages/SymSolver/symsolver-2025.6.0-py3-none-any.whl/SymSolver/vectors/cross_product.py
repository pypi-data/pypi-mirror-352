"""
File Purpose: CrossProduct

[TODO] _sum_collect needs to allow collection of negations of things.
    Right now, can't simplify e.g. (AxB)+7(BxA)
    [how to...] maybe check for a _non_product_gcf() method which allows objects to decide
    whether they share a factor with other objects, without being exactly equal?
    (The factor-checking from Product should remain the same, though..)
"""

from .binary_vector_products import (
    BinaryVectorProduct,
    _bvp_math,
)
from ..initializers import initializer_for, INITIALIZERS
from ..abstracts import (
    AbstractOperation, OperationContainer,
    IterableSymbolicObject,
    is_subbable,
)
from ..basics import (
    Product,
    Equation, _eqn_math,
)
from ..errors import PatternError, VectorPatternError
from ..tools import (
    equals,
    Binding,
)

binding = Binding(locals())


''' --------------------- CrossProductBase --------------------- '''

class CrossProductBase(BinaryVectorProduct):
    '''cross product, e.g. u cross v, without assuming anticommutativity.
    For cross product between vectors, see CrossProduct instead.

    implementaton note: attach CrossProduct-related methods relying on anticommutative property to CrossProduct;
        methods not relying on anticommutative property can attach to CrossProductBase instead.
    '''
    def is_vector(self):
        '''returns True, because the cross product of two values is a vector.'''
        return True


''' --------------------- CrossProduct --------------------- '''

class CrossProduct(CrossProductBase):
    '''vector cross product operation, i.e. u cross v, for vectors u, v.'''
    def _put_first(self, y):
        '''returns self with y first, or raise VectorPatternError if that's not possible.
        self = y x u --> return self, exactly.
        self = u x y --> return y x (-u).
        '''
        if equals(self.t1, y):
            return self  # return self, exactly, to help indicate nothing was changed.
        elif equals(self.t2, y):
            return self._new(y, -1 * self.t1)
        else:
            raise VectorPatternError(f'cannot put y first; neither factor here equals y. y={y}')

    def _put_second(self, y):
        '''returns self with y second, or raise VectorPatternError if that's not possible.
        self = y x u --> return (-u) x y.
        self = u x y --> return self, exactly.
        '''
        if equals(self.t1, y):
            return self._new(-1 * self.t2, y)
        elif equals(self.t2, y):
            return self  # return self, exactly, to help indicate nothing was changed.
        else:
            raise VectorPatternError(f'cannot put y second; neither factor here equals y. y={y}')

    def _is_surely_negation(self, y):
        '''True result is sufficient to indicate y == -self, but not necessary.
        Checks 'anti-commutativity' of cross product: (AxB) == -(BxA).
        '''
        if not isinstance(y, CrossProduct):
            return False
        return equals(self.t1, y.t2) and equals(y.t1, self.t2)

    def __eq__(self, y):
        '''returns self==y
        checks (in this order, returning True if any condition is met):
            if self==y in the sense of commutative products (super().__eq__(y)),
            if y is a product of -1 and z, and self._is_surely_negation(z).
        and if '''
        if super().__eq__(y):
            return True
        try:
            y_without_minus_1 = y._factor_from_negation()
        except (AttributeError, PatternError):
            pass # handled later. 
        else:
            return self._is_surely_negation(y_without_minus_1)
        return False

    __hash__ = IterableSymbolicObject.__hash__

    def sub(self, old, new, **kw):
        '''returns result of substituting old for new in self.
        returns self exactly (i.e. not a copy) if this substitution had no effect.

        The implementation here (for CrossProduct) considers self == old OR self == -1 * old.
            I.e. A.cross(B).sub(A.cross(B), V) --> V
                 A.cross(B).sub(B.cross(A), V) --> -V
        '''
        if not is_subbable(self):
            return self
        # this function's substitution rule for self:
        if isinstance(old, CrossProduct):
            if equals(self, old):
                return new
            if self._is_surely_negation(old):
                return -new
        # loop through terms in self, if applicable.
        def sub_rule(term):
            return term.sub(old, new, **kw)
        return self._substitution_loop(sub_rule, **kw)


@initializer_for(CrossProductBase)  # Base because overwritten in other subpackage, e.g. precalc_operators.
def cross_product(v1, v2, **kw):
    '''returns CrossProduct representing v1 cross v2.
    just returns CrossProduct(v1, v2, **kw)
    '''
    return CrossProduct(v1, v2, **kw)


with binding.to(AbstractOperation):
    AbstractOperation.cross_product = property(lambda self: INITIALIZERS.cross_product,
                                               doc='''alias to INITIALIZERS.cross_product''')
    @binding
    @_bvp_math(rop_attr='rcross')
    def cross(self, b):
        '''retuns self cross b.'''
        return self.cross_product(self, b)

    @binding
    @_bvp_math(rop_attr='cross')
    def rcross(self, b):
        '''retuns b cross self.'''
        return self.cross_product(b, self)

with binding.to(OperationContainer):
    @binding
    def cross(self, b):
        '''applies "obj cross b" to each object in self.'''
        return self.bop(INITIALIZERS.cross_product, b)

    @binding
    def rcross(self, b):
        '''applies "b cross obj" to each object in self.'''
        return self.bop(INITIALIZERS.cross_product, b, reverse=True)


def _initializers_cross(v1, v2):
    '''returns INITIALIZERS.cross_product(v1, v2)'''
    return INITIALIZERS.cross_product(v1, v2)
def _initializers_rcross(v1, v2):
    '''returns INITIALIZERS.cross_product(v2, v1)'''
    return INITIALIZERS.cross_product(v2, v1)

Equation.cross = _eqn_math('cross', _initializers_cross)
Equation.rcross = _eqn_math('rcross', _initializers_rcross)
