"""
File Purpose: square roots and divisibility
"""
from .power import Power
from .product import Product
from .sum import Sum
from .basics_tools import (
    get_summands, get_factors, get_base_and_power,
)
#from ._lites import SumLite, ProductLite, PowerLite
from ..abstracts import (
    simplify_op, simplify_op_skip_for,
    contains_deep,
)
from ..numbers import (
    sqrt_if_square, divide_if_divisible,
)
from ..tools import (
    equals,
    _list_without_i,
    Binding,
)
from ..defaults import DEFAULTS, ONE

binding = Binding(locals())


''' --------------------- equality with divisibility --------------------- '''

def product_unsimplified_equals(x, y):
    '''returns whether x==y. False negatives are possible, but True always means "definitely equal".
    uses divide_if_divisible to get correct result even if x and y have some numerical & uncombined factors.
    E.g. product_unsimplified_equals(10, product(5, 2)) --> True.
    '''
    divided = divide_if_divisible(x, y)
    return False if divided is None else equals(divided, ONE)


''' --------------------- sqrt_if_square --------------------- '''

with binding.to(Power):
    @binding
    def sqrt_if_square(self):
        '''return sqrt(self) if we can get exact result without introducing any roots, else None.'''
        base, exp = self
        newexp = divide_if_divisible(exp, 2)
        if newexp is None:
            return None
        return base if equals(newexp, ONE) else self._new(base, newexp)

with binding.to(Product):
    @binding
    def sqrt_if_square(self):
        '''return sqrt(self) if we can get exact result without introducing any roots, else None.'''
        result = []
        for factor in self:
            factor_sqrt = sqrt_if_square(factor)
            if factor_sqrt is None:
                return None
            result.append(factor_sqrt)
        return self._new(*result)


''' --------------------- divide_if_divisible --------------------- '''

with binding.to(Power):
    @binding
    def divide_if_divisible(self, divide_by):
        '''return self / divide_by if self is definitely divisible by divide_by, else None.'''
        if equals(self, divide_by):
            return ONE
        base, exp = self
        b2, e2 = get_base_and_power(divide_by)
        if not equals(b2, base):
            return None
        newexp = exp - e2
        return base if equals(newexp, ONE) else self._new(base, newexp)

with binding.to(Product):
    @binding
    def divide_if_divisible(self, divide_by):
        '''return self / divide_by if self is definitely divisible by divide_by, else None.'''
        if equals(self, divide_by):
            return ONE
        factors_result = get_factors(self)
        factors_divide = get_factors(divide_by)
        for fdivide in factors_divide:
            for i, fresult in enumerate(factors_result):
                quotient = divide_if_divisible(fresult, fdivide)
                if quotient is not None:
                    if equals(quotient, ONE):
                        del factors_result[i]
                    else:
                        factors_result[i] = quotient
                    break
            else:  # didn't break, i.e. didn't find any fresult divisible by fdivide
                return None
        return self._new(*factors_result)


''' --------------------- sum collect binomial squared --------------------- '''

@simplify_op(Sum, alias='_collect', order=9)
def _sum_collect_binomial_squared(self, collect_polys=[], collect_poly_format=False, **kw__None):
    '''put expanded binomial squared back into binomial^2 form.
    X^2 + 2 X Y + Y^2 --> (X + Y)^2.
    Also  X^2 + Y (2 X + Y) --> (X + Y)^2

    Only applies any simplifications if the ENTIRE sum in self looks like one of the inputs above.
    E.g., does nothing if the input is 1 + X^2 + 2 X Y + Y^2.

    if collect_poly_format AND self.contains_deep(poly) for any poly in collect_polys, skip this simplification.
    '''
    L = len(self)
    if collect_poly_format and len(collect_polys)>0 and (L==3 or L==2):
        # check if we should skip simplification entirely, due to collect_polys.
        #   (the (L==3 or L==2) is for efficiency, since we can only simplify in that case anyways)
        if any(self.contains_deep(poly) for poly in collect_polys):
            return self  # return self, exactly, to help indicate nothing was changed.
    if L == 3:  # trying to match X^2 + 2 X Y + Y^2
        # look for perfect squares. we need to find at least 2, otherwise can't do anything.
        A, B, C = self
        sqrtA = sqrt_if_square(A)
        sqrtB = sqrt_if_square(B)
        if sqrtA is None and sqrtB is None:  # 2 out of 3 are not perfect squares.
            return self  # return self, exactly, to help indicate nothing was changed.
        sqrtC = sqrt_if_square(C)
        if sqrtC is None and (sqrtA is None or sqrtB is None):  # 2 out of 3 are not perfect squares.
            return self  # return self, exactly, to help indicate nothing was changed.
        if sqrtA is None:
            attempts = [(sqrtB, A, sqrtC)]  # each attempt is possible values for (X, 2 X Y, Z)
        elif sqrtB is None:
            attempts = [(sqrtA, B, sqrtC)]
        elif sqrtC is None:
            attempts = [(sqrtA, C, sqrtB)]
        else:  # A, B, and C are ALL perfect squares, so attempt all combinations
            attempts = [(sqrtB, A, sqrtC), (sqrtA, B, sqrtC), (sqrtA, C, sqrtB)]
        for X, twoXY, Y in attempts:
            if product_unsimplified_equals(twoXY, 2 * X * Y):
                return self.power((X + Y), 2)
    elif L == 2:  # trying to match X^2 + 2 Y (X + Y).
        A, B = self
        sqrtA = sqrt_if_square(A)
        sqrtB = sqrt_if_square(B)
        if sqrtA is None and sqrtB is None:
            return self  # return self, exactly, to help indicate nothing was changed.
        attempts = []
        if sqrtA is not None:
            attempts.append((sqrtA, B))
        if sqrtB is not None:
            attempts.append((sqrtB, A))
        for (X, expr) in attempts:  # trying to match expr to Y (2 X + Y).
            # Y or 2 X or both might appear as sums, products, or numbers,
            # depending on the values of Y and X. So we need to be careful about searching.
            # We do know for sure that 2 X + Y should appear as a Sum.
            expr_factors = get_factors(expr)
            if len(expr_factors) == 1:
                return self  # return self, exactly, to help indicate nothing was changed.
            twoX = 2 * X
            for i, factor in enumerate(expr_factors):
                summands = get_summands(factor)
                if len(summands) > 1:
                    for j, summand in enumerate(summands):
                        if product_unsimplified_equals(twoX, summand):
                            del summands[j]
                            Y = self.sum(*summands)  # we found a candidate Y;
                            # check if the other factors look like Y.
                            factors_without_i = _list_without_i(expr_factors, i)
                            Ytest = self.product(*factors_without_i)
                            if product_unsimplified_equals(Ytest, Y):
                                return self.power((X + Y), 2)
    return self  # return self, exactly, to help indicate nothing was changed.
