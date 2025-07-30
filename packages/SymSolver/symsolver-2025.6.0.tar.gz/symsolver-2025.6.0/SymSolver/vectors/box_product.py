"""
File Purpose: BoxProduct
BoxProduct(A, B, C) == A.(BxC) == B.(CxA) == C.(AxB) == -A.(CxB) == -B.(AxC) == -C.(BxA).
    == the (signed) volume of the parallelepiped defined by vectors A, B, C.

[TODO] option to represent it as (BxC).A instead, when converting to string.
"""

from .dot_product import DotProduct
from .cross_product import CrossProduct
from ..abstracts import (
    AbstractOperation, IterableSymbolicObject,
    simplify_op, simplify_op_skip_for,
)
from ..errors import PatternError, VectorPatternError
from ..initializers import initializer_for, INITIALIZERS
from ..tools import (
    equals,
    Binding,
)
from ..defaults import ZERO

binding = Binding(locals())


''' --------------------- BoxProduct --------------------- '''

class BoxProduct(DotProduct):
    '''vector box product operation, i.e. A dot (B cross C) for vectors A, B, C.
    Behaves just like DotProduct, but also has methods for handling the box product identity:
        A.(BxC) == B.(CxA) == C.(AxB) == -A.(CxB) == -B.(AxC) == -C.(BxA)
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, A, B, C, rdot=False, **kw):
        '''initialize BoxProduct.
        rdot: bool, default False
            False --> self.terms = [A, B cross C]
            True --> self.terms = [B cross C, A]

            caution: self.rdot has a different meaning (the "reverse dot" operation).
                the value input here will be stored in self._init_rdot instead.

            implementation note: BoxProduct-related methods should ignore self.terms;
                use self._A, self._B, self._C, self._ABC, and/or self._B_cross_C instead.
        '''
        self._A = A
        self._B = B
        self._C = C
        self._init_rdot = rdot
        self._ABC = (self._A, self._B, self._C)
        self._B_cross_C = self.cross_product(B, C)
        if rdot:
            super().__init__(self._B_cross_C, A, **kw)
        else:
            super().__init__(A, self._B_cross_C, **kw)

    def _new_from_ABC(self, A, B, C, **kw):
        '''make new BoxProduct like self, from A, B, C, rather than from A, B_cross_C.
        implementation note: self._new accepts only 2 args so that self still behaves like a DotProduct,
            during creation/initialization. See also: box_product()
        '''
        init_props = self._init_properties()
        init_props.update(kw)
        result = type(self)(A, B, C, **init_props)
        self._transmit_genes(result)
        return result

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another BoxProduct like self.'''
        kw = super()._init_properties()
        kw['rdot'] = self._init_rdot
        return kw

    # # # EQUALITY AND NEGATION # # #
    def __eq__(self, y):
        try:
            return super(IterableSymbolicObject, self).__eq__(y)  # skip IterableSymbolicObject's __eq__.
        except NotImplementedError:
            pass # that's fine / to be expected. can move on.
        try:
            return self._box_product_equals(y)
        except (AttributeError, VectorPatternError):
            pass # that's fine / to be expected. can move on.
        try:
            y_without_minus_1 = y._factor_from_negation()
        except (AttributeError, PatternError):
            pass # that's fine / to be expected. can move on.
        else:  # was able to calculate y_without_minus_1
            return self._is_surely_negation(y_without_minus_1)
        return False

    def _type_precludes_generic_equality(self, b):
        '''returns whether type(b) prevents self == b, for generic b.
        The implementation here is:
            not isinstance(b, DotProduct)
        because DotProducts can equal self, and also BoxProduct subclasses DotProduct.

        Special objects, e.g. 0, might equal self regardless of type.
        '''
        return not isinstance(b, DotProduct)

    def _box_product_equals(self, y):
        '''returns whether self == y due to box product identity:
        A.(BxC) == B.(CxA) == C.(AxB).
        y: a BoxProduct instance, or something that can be converted into a BoxProduct.
            this method will use y._convert_to_box_product().
        '''
        y = y._convert_to_box_product()
        yA, yB, yC = y._ABC
        sA, sB, sC = self._ABC
        if equals(yA, sA):    # A.(BxC) == A.(BxC)
            return equals(yB, sB) and equals(yC, sC)
        elif equals(yA, sB):  # A.(BxC) == B.(CxA)
            return equals(yB, sC) and equals(yC, sA)
        elif equals(yA, sC):  # A.(BxC) == C.(AxB)
            return equals(yB, sA) and equals(yC, sB)
        else:
            return False

    def _box_product_negates(self, y):
        '''returns whether -y == self due to scalar box product identity:
            A.(BxC) == -A.(CxB) == -B.(AxC) == -C.(BxA)
        y: a BoxProduct instance, or something that can be converted into a BoxProduct.
            this method will use y._convert_to_box_product().
        '''
        y = y._convert_to_box_product()
        yA, yB, yC = y._ABC
        sA, sB, sC = self._ABC
        if equals(yA, sA):    # A.(BxC) == -A.(CxB)
            return equals(yB, sC) and equals(yC, sB)
        elif equals(yA, sB):  # A.(BxC) == -B.(AxC)
            return equals(yB, sA) and equals(yC, sC)
        elif equals(yA, sC):  # A.(BxC) == -C.(BxA)
            return equals(yB, sB) and equals(yC, sA)
        else:
            return False

    def _is_surely_negation(self, y):
        '''True result is sufficient to indicate y == -self, but not necessary.
        Checks vector box product identity:
            A.(BxC) == -A.(CxB) == -B.(AxC) == -C.(BxA)
        E.g. (A.(BxC)).is_surely_negation(B.(AxC)) == True
        '''
        try:
            return self._box_product_negates(y)
        except (AttributeError, VectorPatternError):
            return False

    def _convert_to_box_product(self):
        '''returns self, because self is already a BoxProduct.'''
        return self

    # # # CYCLING / REWRITING # # #
    @staticmethod
    def _is_even_cycle(A, B, C):
        '''returns True iff ABC is (0,1,2), (1,2,0) or (2,0,1).'''
        return (A, B, C) in ((0,1,2), (1,2,0), (2,0,1))

    def cycle(self, cycle):
        '''cycles to a different way to write the same BoxProduct; returns result.
        cycle: tuple of 3 values from 0, 1, 2.
            where to put each of (A, B, C) in the returned BoxProduct object:
                "even cycles":
                "ABC"  (0,1,2) --> self  (unchanged)
                "BCA"  (1,2,0) --> self._new_from_ABC(B, C, A)
                "CAB"  (2,0,1) --> self._new_from_ABC(C, A, B)
                "odd cycles":
                "ACB"  (0,2,1) --> -self._new_from_ABC(A, C, B)
                "BAC"  (1,0,2) --> -self._new_from_ABC(B, A, C)
                "CBA"  (2,1,0) --> -self._new_from_ABC(C, B, A)
        '''
        cycle = tuple(cycle)
        if cycle == (0,1,2):
            return self   # unchanged
        sign, A, B, C = self._cycle_terms(cycle)
        result = self._new_from_ABC(A, B, C)
        return result if sign else -result

    def _cycle_terms(self, cycle):
        '''returns (sign, ABC) for cycle.
        self.cycle(cycle) == (1 if sign else -1) * self._new_from_ABC(A, B, C).
        '''
        ABC = self._ABC
        A, B, C = (ABC[i] for i in cycle)
        sign = self._is_even_cycle(*cycle)
        return sign, A, B, C

    def cycle_ABC(self):
        '''returns self, because self is already in A.(BxC) order.'''
        return self

    def cycle_BCA(self):
        '''returns B.(CxA). this equals self via box product identity. self == A.(BxC).'''
        A, B, C = self._ABC
        return self._new_from_ABC(B, C, A)

    def cycle_CAB(self):
        '''returns C.(AxB). this equals self via box product identity. self == A.(BxC).'''
        A, B, C = self._ABC
        return self._new_from_ABC(C, A, B)

    def cycle_ACB(self):
        '''returns -A.(CxB). this equals self via box product identity. self == A.(BxC).'''
        A, B, C = self._ABC
        return -self._new_from_ABC(A, C, B)

    def cycle_BAC(self):
        '''returns -B.(AxC). this equals self via box product identity. self == A.(BxC).'''
        A, B, C = self._ABC
        return -self._new_from_ABC(B, A, C)

    def cycle_CBA(self):
        '''returns -C.(BxA). this equals self via box product identity. self == A.(BxC).'''
        A, B, C = self._ABC
        return -self._new_from_ABC(C, B, A)

    def _cycle_put_internal(self, internal_if, strict=True):
        '''cycles self to force certain vectors into the cross product.
        Uses the box product identity:
            A.(BxC) == B.(CxA) == C.(AxB)

        internal_if: callable of one input.
            if internal_if(v), put v into the cross product.
        strict: bool, default True
            controls behavior when internal_if(v) for v=A, B, and C.
            True --> in that case, raise VectorPatternError.
            False --> in that case, return self, unchanged.

        raise VectorPatternError if this is impossible.
        '''
        if internal_if(self._A):
            if internal_if(self._B):
                if internal_if(self._C):
                    if strict:
                        raise VectorPatternError('internal_if(v) True for A, B, and C but strict=True.')
                    else:  # A.(BxC)
                        return self  # all 3 satisfy internal_if, and B and C are already on the inside.
                else:  # C.(AxB)
                    return self.cycle_CAB()
            else:  # B.(CxA)
                return self.cycle_BCA()
        else:  # not internal_if(A)
            return self  # B and C are already on the inside --> don't need to cycle anything.

    def _cycle_put_external(self, external_if, strict=True):
        '''cycles self to look like A.(BxC), possibly forcing one vector outside of the cross product.
        Uses the dot cross product identity:
            A.(BxC) == B.(CxA) == C.(AxB)

        external_if: callable of one input.
            if external_if(v), put v outside the cross product.
        strict: bool, default True
            controls behavior when external_if(v) for at least 2 v from A, B, C.
            True --> in that case, raise VectorPatternError.
            False --> in that case... (below using self== Aold.(Bold x Cold))
                if external_if(Aold), return self, unchanged
                else (external_if(Bold) and external_if(Cold)...) put Bold on the outside 

        raise VectorPatternError if this is impossible.
        '''
        if external_if(self._B):
            if strict and external_if(self._C) or external_if(self._A):
                raise VectorPatternError('external_if(v) True for multiple vectors but strict=True.')
            else:  # B.(CxA)
                return self.cycle(BCA)
        elif external_if(self._C):
            if strict and external_if(self._A):
                raise VectorPatternError('external_if(v) True for multiple vectors but strict=True.')
            else:  # C.(AxB)
                return self.cycle(CAB)
        else:  # A.(BxC)
            return self   # A already on the outside --> don't need to cycle anything.


@initializer_for(BoxProduct)
def box_product(A, B_cross_C, rdot=False, **kw):
    '''returns BoxProduct representing A dot (B_cross_C).
    if B_cross_C == B cross C, this just means return BoxProduct(A, B, C).
    otherwise, we instead return DotProduct(A, B_cross_C)

    rdot: bool, default False
        False --> result represents A dot (B_cross_C)
        True --> result represents (B_cross_C) dot A
        if result is a BoxProduct, this value will be stored in result._init_rdot.

    implementation note:
        Since BoxProduct.terms == [A, B_cross_C], this initializer needs to accept 2 args, not 3.
    '''
    if isinstance(B_cross_C, CrossProduct):
        return BoxProduct(A, *B_cross_C, rdot=rdot, **kw)
    else:
        if rdot:
            return DotProduct(B_cross_C, A, **kw)
        else:
            return DotProduct(A, B_cross_C, **kw)


with binding.to(AbstractOperation):
    # # # BIND BOX PRODUCT # # #
    AbstractOperation.box_product = property(lambda self: INITIALIZERS.box_product,
                                             doc='''alias to INITIALIZERS.box_product''')


''' --------------------- SIMPLIFY_OPS for BoxProduct --------------------- '''

@simplify_op(BoxProduct, alias='_simplify_id')
def _box_product_simplify_id(self, **kw__None):
    '''converts A dot (A cross B) --> 0.'''
    if equals(self._A, self._B) or equals(self._A, self._C):
        return ZERO
    else:
        return self  # return self, exactly, to help indicate nothing was changed.


''' --------------------- CONVERT DotProduct to BoxProduct --------------------- '''

with binding.to(DotProduct):
    @binding
    def _convert_to_box_product(self):
        '''returns BoxProduct(A,B,C) assuming self looks like A.(BxC).
        raise VectorPatternError if that is not possible.

        note: if self looks like (A1xA2).(BxC), returns BoxProduct(A1xA2, B, C).
        '''
        crossed1, crossed2 = (isinstance(t, CrossProduct) for t in self)
        if crossed2:
            return self.box_product(self.t1, self.t2)
        elif crossed1:
            return self.box_product(self.t2, self.t1, rdot=True)
        else:
            raise VectorPatternError('self looks like A.B, not A.(BxC)')


simplify_op_skip_for(BoxProduct, '_dot_product_convert_to_box_product')  # don't try to do this for BoxProducts.

@simplify_op(DotProduct, alias='_upcast_to_box_product')
def _dot_product_upcast_to_box_product(self, **kw__None):
    '''handles A.(BxC) --> BoxProduct(A, B, C).
    BoxProduct(A, B, C) represents A dot (B cross C),
        but also has implemented rules to incorporate the box product vector identity:
        A.(BxC) == B.(CxA) == C.(AxB) == -A.(CxB) == -B.(AxC) == -C.(BxA)
    '''
    try:
        return self._convert_to_box_product()
    except VectorPatternError:  # don't need to except AttributeError since self is at least a DotProduct.
        return self  # return self, exactly, to help indicate nothing was changed.