"""
File Purpose: AbstractOperators might be vectors, and interact with dot and cross products.

The meanings of dot and cross products involving operators is defined as follows,
    (f dot u) <--> the summation of fi(ui). This is a value. 
    (u dot f) <--> the summation of ui * fi. This is an operator.
                    E.g. (u dot f)(value) --> summation(ui fi(value)).
    (g dot f) <--> the summation of gi(fi). This is an operator.
                    E.g. (g dot f)(value) --> summation(gi(fi(value)))
                        which is equivalent to (g dot f(value))
    (f cross u) <--> (fy(uz) - fz(uy))xhat  +  (fz(ux) - fx(uz))yhat  +  (fx(uy) - fy(ux))zhat. This is a value.
    (u cross f) <--> xhat*uy*fz - xhat*uz*fy + yhat*uz*fx - yhat*ux*fz + zhat*ux*fy - zhat*uy*fx.
                    == Cx fx + Cy fy + Cz fz, where
                    Cx = yhat*uz - zhat*uy,
                    Cy = zhat*ux - xhat*uz,
                    Cz = xhat*uy - yhat*ux. 
                    This is an operator.
                    E.g., (u cross f)(value) --> Cx fx(value) + Cy fy(value) + Cz fz(value)
    (g cross f) <--> xhat*gy(fz) - xhat*gz(fy) + yhat*gz(fx) - yhat*gx(fz) + zhat*gx(fy) - zhat*gy(fx).
                    This is an operator.
                    E.g., (g cross f)(value) --> xhat*(gy(fz(value)) - gz(fy(value)))
                                                + yhat*(gz(fx(value)) - gx(fz(value)))
                                                + zhat*(gx(fy(value)) - gy(fx(value)))
                        which is equivalent to (g cross f(value)).
for operators (which are also vectors) f and g; u (a vector but) not an operator;
summations taken over components i which are entered at time of evaluating dot products;
and (xhat, yhat, zhat) the OrthonormalBasis3D entered when evaluating cross products.

This file provides the code for this behavior by implementing:
    for operator f and non-operator u:
        f.dot(u) --> f.__dot_call__(u) if available, else DotProductBase(f, u)
        f.cross(u) --> f.__cross_call__(u) if available, else CrossProductBase(f, u)
    for operator f and any vector (operator or not) v:
        v.dot(f) --> DotProductBase(v, f)
        v.cross(f) --> CrossProductBase(v, f)
    for AbstractOperator f:
        [TODO] f behaves like Symbol in f.component(...) and f.componentize(...)
"""

from .abstract_operators import AbstractOperator
from .generic_operations import GenericOperation
from .operation_vector_products import (
    OperationBinaryVectorProduct,
    OperationDotProduct,
    OperationCrossProduct,
    DotOperation,
)
from .operators_tools import is_operator, is_linear_operator
from ..initializers import initializer_for
from ..vectors import (
    BinaryVectorProduct,
    DotProductBase, DotProduct,
    CrossProductBase, CrossProduct,
    is_vector,
)
from ..tools import (
    Binding,
)
binding = Binding(locals())


''' --------------------- IS_OPERATOR & IS_LINEAR_OPERATOR --------------------- '''

with binding.to(BinaryVectorProduct):
    @binding
    def is_operator(self):
        '''returns whether self.t2 is an operator.'''
        return is_operator(self.t2)

    @binding
    def is_linear_operator(self):
        '''returns whether self.t2 is a linear operator, and self.t1 is not a non-linear operator.'''
        return is_linear_operator(self.t2) and (is_linear_operator(self.t1) if is_operator(self.t1) else True)


''' --------------------- CALL for DotProduct & CrossProduct --------------------- '''

with binding.to(DotProductBase):
    @binding
    def __call__(self, g):
        '''calls self on g.
        if self.t2 is an operator, and g is not, returns DotOperation(self, g).
            if g is an operator but not a vector, call self.t2 on g.
            if g is an operator and a vector, raise NotImplementedError
        else, returns self * g

        Note: g might be an operator as well.
        '''
        if self.is_operator():
            if is_operator(g):
                if is_vector(g):
                    raise NotImplementedError('[TODO] operator DotProduct called on a vector-valued operator')
                else:
                    return self._new(self.t1, self.t2(g))
            else:
                return DotOperation(self, g)
        else:
            return self * g

with binding.to(CrossProductBase):
    @binding
    def __call__(self, g):
        '''calls self on g.
        if self is an operator:
            if g is a vector, raise NotImplementedError
            Else, call self.t2 on g.
        else, returns self * g

        Note: g might be an operator as well.
        '''
        if self.is_operator():
            if is_vector(g):
                raise NotImplementedError('[TODO] operator CrossProduct called on a vector operator')
            else:
                return self._new(self.t1, self.t2(g))
        else:
            return self * g


''' --------------------- INITIALIZERS for DotProduct & CrossProduct --------------------- '''

@initializer_for(DotProductBase)
def dot_product(v1, v2, **kw):
    '''returns DotProduct, DotProductBase, or OperationDotProduct, representing v1 dot v2.
    if v1 is an operator, returns v1.__dot_call__(v2) if possible.
    else, if either v1 or v2 is an operator, return DotProductBase(v1, v2, **kw).
    else, return DotProduct(v1, v2, **kw).
    '''
    v1_is_operator = is_operator(v1)
    if v1_is_operator:
        try:
            v1_dot_call = v1.__dot_call__
        except AttributeError:
            pass  # handled below
        else:
            return v1_dot_call(v2)
    if v1_is_operator or is_operator(v2):
        return DotProductBase(v1, v2, **kw)  # DotProduct without the commutative property
    else:
        return DotProduct(v1, v2, **kw)


@initializer_for(CrossProductBase)
def cross_product(v1, v2, **kw):
    '''returns CrossProduct, CrossProductBase, or OperationCrossProduct, representing v1 cross v2.
    if v1 is an operator, returns v1.__cross_call__(v2) if possible.
    else, if either v1 or v2 is an operator, return CrossProductBase(v1, v2, **kw).
    else, return CrossProduct(v1, v2, **kw).
    '''
    v1_is_operator = is_operator(v1)
    if v1_is_operator:
        try:
            v1_cross_call = v1.__cross_call__
        except AttributeError:
            pass  # handled below
        else:
            return v1_cross_call(v2)
    if v1_is_operator or is_operator(v2):
        return CrossProductBase(v1, v2, **kw)  # CrossProduct without the anti-commutative property
    else:
        return CrossProduct(v1, v2, **kw)


''' --------------------- __dot_call__ and __cross_call__ --------------------- '''
# __dot_call__ is called during f.dot(u) where f is an AbstractOperator. By default, returns:
#   DotProductBase(f, u)  if  u is an AbstractOperator too;
#   OperationDotProduct(f, u), otherwise
# __cross_call__ is called during f.cross(u) where f is an AbstractOperator. By default, returns:
#   CrossProductBase(f, u)  if  u is an AbstractOperator too;
#   OperationCrossProduct(f, u), otherwise.

with binding.to(AbstractOperator):
    @binding
    def __dot_call__(self, u):
        '''self.dot(u), for self an AbstractOperator.
        __dot_call__ is called whenever a dot product is initialized properly,
            i.e. via dot_product() or obj.dot(u) (which aliases to dot_product(obj, u)).

        if u is an operator, returns DotProductBase(self, u).
        otherwise, returns OperationDotProduct(self, u).

        Note: this will crash with VectorialityError if not self.is_vector().
        '''
        if is_operator(u):
            return DotProductBase(self, u)   # self.dot(u) is an operator because u is an operator.
        else:
            return OperationDotProduct(self, u)  # self.dot(u) is not an operator.

    @binding
    def __cross_call__(self, u):
        '''self.cross(u), for self an AbstractOperator.
        __cross_call__ is called whenever a cross product is initialized properly,
            i.e. via cross_product() or obj.cross(u) (which aliases to cross_product(obj, u)).

        if u is an operator, returns CrossProductBase(self, u).
        otherwise, returns OperationCrossProduct(self, u).

        Note: this will crash with VectorialityError if not self.is_vector().
        '''
        if is_operator(u):
            return CrossProductBase(self, u)   # self.cross(u) is an operator because u is an operator.
        else:
            return OperationCrossProduct(self, u)  # self.cross(u) is not an operator.


''' --------------------- COMPONENTS --------------------- '''

# [TODO] _dot_product_operator_components_shorthand   # a simplify_op.
# [TODO] AbstractOperator.component(...)
# [TODO] AbstractOperator.componentize(...)