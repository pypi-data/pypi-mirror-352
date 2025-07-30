"""
File Purpose: DotProduct
"""

from .binary_vector_products import (
    BinaryVectorProduct,
    _bvp_math,
)
from .vectors_tools import (
    is_vector,
)
from ..initializers import initializer_for, INITIALIZERS
from ..attributors import attributor
from ..abstracts import (
    CommutativeOperation,
    AbstractOperation, OperationContainer,
    simplify_op, simplify_op_skip_for,
)
from ..basics import (
    Symbol, Product,
    Equation, _eqn_math,
)
from ..tools import (
    equals,
    Binding,
)
from ..defaults import DEFAULTS, ONE

binding = Binding(locals())


''' --------------------- Convenience Functions --------------------- '''

@attributor
def vector_magnitude(x):
    '''returns magnitude of x, by returning x.magnitude() if it exists, else x.
    Takes magnitude of all vectors, but leaves scalars untouched.
    (e.g. vector_magnitude(-7 * u) == -7 * u dot u, for vector u.
    [TODO] make a Magnitude class?
    '''
    try:
        return obj.magnitude()
    except AttributeError:
        return obj


''' --------------------- DotProductBase --------------------- '''

class DotProductBase(BinaryVectorProduct):
    '''dot product, e.g. u dot v, without assuming commutativity.
    For dot product between vectors, see DotProduct instead.

    implementaton note: attach DotProduct-related methods relying on commutative property to DotProduct;
        methods not relying on commutative property can attach to DotProductBase instead.
    '''
    def is_vector(self):
        '''returns False, because the dot product of two values is not a vector.
        (Note: we didn't implement tensors yet. If implementing tensors, need to adjust this method.)
        '''
        return False


''' --------------------- DotProduct --------------------- '''

class DotProduct(DotProductBase, CommutativeOperation):
    '''vector dot product operation, i.e. u dot v, for vectors u, v.'''
    pass  # << behavior for DotProduct defined by parents & methods defined later.


@initializer_for(DotProductBase)  # Base because overwritten in other subpackage, e.g. precalc_operators.
def dot_product(v1, v2, **kw):
    '''returns DotProduct representing v1 dot v2.
    just returns DotProduct(v1, v2, **kw)
    '''
    return DotProduct(v1, v2, **kw)


with binding.to(AbstractOperation):
    # # # BIND DOT PRODUCT # # #
    AbstractOperation.dot_product = property(lambda self: INITIALIZERS.dot_product,
                                             doc='''alias to INITIALIZERS.dot_product''')
    @binding
    @_bvp_math(rop_attr='rdot')
    def dot(self, b):
        '''retuns self dot b.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self.dot_product(self, b)

    @binding
    @_bvp_math(rop_attr='dot')
    def rdot(self, b):
        '''retuns b dot self.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self.dot_product(b, self)

    # # # BIND MAGNITUDE # # #
    @binding
    def magnitude(self):
        '''returns vector magnitude of self.
        Takes magnitude of vectors, but leaves scalars untouched.
        (e.g. vector_magnitude(-7 * u) == -7 * u dot u, for vector u.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if is_vector(self):
            return INITIALIZERS.dot_product(self, self)
        else:
            return self


with binding.to(OperationContainer):
    # # # BIND DOT PRODUCT # # #
    @binding
    def dot(self, b):
        '''applies "obj dot b" to each object in self.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self.bop(INITIALIZERS.dot_product, b)

    @binding
    def rdot(self, b):
        '''applies "b dot obj" to each object in self.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self.bop(INITIALIZERS.dot_product, b, reverse=True)

    # # # BIND MAGNITUDE # # #
    @binding
    def magnitude(self):
        '''applies "vector_magnitude(obj)" to each object in self.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self.op(lambda x: vector_magnitude(x))


def _initializers_dot(v1, v2):
    '''returns INITIALIZERS.dot_product(v1, v2)'''
    return INITIALIZERS.dot_product(v1, v2)
def _initializers_rdot(v1, v2):
    '''returns INITIALIZERS.dot_product(v2, v1)'''
    return INITIALIZERS.dot_product(v2, v1)

Equation.dot = _eqn_math('dot', _initializers_dot)
Equation.rdot = _eqn_math('rdot', _initializers_rdot)


''' --------------------- DotProduct SIMPLIFY_OPS --------------------- '''

simplify_op_skip_for(DotProduct, '_dot_product_magnitude_id')  # skip this operation by default
@simplify_op(DotProduct, alias='_magnitude_id')
def _dot_product_magnitude_id(self, **kw__None):
    '''converts x dot x --> |x|**2, x dot xhat --> x, xhat dot xhat --> 1, for Symbol x.
    Note: xhat dot xhat --> 1 is also handled by _dot_product_simplify_hat_id.
    '''
    t1, t2 = self
    if isinstance(t1, Symbol) and isinstance(t2, Symbol) and t1.equals_except(t2, 'hat'):
        if t1.hat or t2.hat:
            if t1.hat and t2.hat:
                return ONE
            else:
                return t1.magnitude()
        else:
            return t1.magnitude() ** 2
    return self  # return self, exactly, to help indicate nothing was changed.

@simplify_op(DotProduct, aliases=('_simplify_id', '_simplify_hat_id'))
def _dot_product_simplify_hat_id(self, **kw__None):
    '''converts xhat dot xhat --> 1, for Symbol xhat.
    compares via 'is', since symbols should all be unique (see SYMBOLS).
    '''
    t1, t2 = self
    if t1 is t2 and isinstance(t1, Symbol) and isinstance(t2, Symbol) and t1.hat:
        return ONE  # if t1.hat, then definitely t2.hat as well.
    else:
        return self  # return self, exactly, to help indicate nothing was changed.
