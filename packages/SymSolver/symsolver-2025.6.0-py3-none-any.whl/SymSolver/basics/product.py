"""
File Purpose: Product
see also: product
"""
import builtins   # << for unambiguous sum.
from collections import OrderedDict

from ._lites import PowerLite, ProductLite, SumLite
from .sum import Sum
from ..initializers import initializer_for, INITIALIZERS
from ..abstracts import (
    AbelianOperation, SubbableObject,
    AbstractOperation,
    simplify_op, simplify_op_skip_for,
    _equals0,
    _simplyfied,
    _abstract_math,
    ComplexityBinning,
)
from .basics_abstracts import (
    AbstractProduct,
)
from .basics_tools import (
    get_base_and_power, get_factors, get_summands,
    get_common_bases, _adjusted_factor_powers,
    has_minus_sign, seems_negative,
    count_minus_signs_in_factors,
    get_reciprocal, exponent_seems_positive,
    multiply, gcf,
    copy_if_possible,
)
from ..errors import PatternError
from ..tools import (
    equals, find,
    is_integer, int_equals,
    is_real_negative_number,
    alias, caching_attr_simple_if,
    Binding,
)
from ..defaults import DEFAULTS, ZERO, ONE, MINUS_ONE

binding = Binding(locals())


class Product(AbstractProduct, AbelianOperation):
    '''Multiplication operation, e.g. 7*x*y.'''
    IDENTITY = ONE  # == 1

    @property
    def OPERATION(self):
        '''returns the operation which self represents: multiplication.
        I.e. returns a function f(*args) --> args[0] * args[1] * ... * args[-1]
        '''
        return multiply

    def get_factors(self, *, split_minus=False):
        '''returns list of factors for self, i.e. list(self).
        if split_minus, split negative real numbers x into factors (-1, |x|), unless x=-1.'''
        if split_minus:
            return [f for x in self for f in
                            ([MINUS_ONE, -x] if
                            is_real_negative_number(x) and not equals(x, MINUS_ONE)
                            else [x])
                    ]
        else:  # default
            return list(self)

    def gcf(self, b):
        '''return (gcf= the "greatest" common factor of self and b, self/gcf, b/gcf).'''
        if equals(self, b):
            return (self, ONE, ONE)
        gg = Product.IDENTITY
        s_factors = get_factors(self)   # we will store here the gcf'd forms.
        b_factors = get_factors(b)
        for i in range(len(s_factors)):
            for j in range(len(b_factors)):
                # for each factor in self, replace it with s/gcf(s, t) for each factor t in b.
                # (also track gcf and factors in t appropriately during this process.)
                s = s_factors[i]
                t = b_factors[j]
                g, snew, tnew = gcf(s, t)
                gg = gg * g
                s_factors[i] = snew
                b_factors[j] = tnew
        return gg, _simplyfied(self._new(*s_factors)), _simplyfied(self._new(*b_factors))

    without_factor = alias('without_term')

    def negation(self):
        '''returns -self. Handles minus signs nicely.
        provided as separate method from __neg__ for clarity,
        e.g. others may check hasattr(obj, 'negation').
        '''
        if self.count_minus_signs_in_factors() > 0:
            factors = []
            self_factors = iter(self)
            for factor in self_factors: # loop until we have negated one factor.
                if has_minus_sign(factor):
                    neg_factor = -factor # negate factor
                    if equals(neg_factor, Product.IDENTITY):
                        pass  # no need to add 1 to list of factors.
                    else:
                        factors.append(neg_factor)
                    break  # we negated one factor
                else:
                    factors.append(factor)
            for factor in self_factors: # loop through all the remaining factors, don't negate any.
                factors.append(factor)
            return self._new(*factors)
        else:
            return self._new(-1, *self)

    def __neg__(self):
        '''returns -self. Equivalent to self.negation().'''
        return self.negation()

    def _factor_from_negation(self):
        '''(self == -1 * factor) --> factor.
        (returns the other factor when one factor of self equals -1 and self has 2 factors.)
        raises PatternError if that is not possible.
        '''
        if len(self) == 2:
            if equals(self[0], -1):
                return self[1]
            elif equals(self[1], -1):
                return self[0]
            else:
                raise PatternError('neither factor in Product equals -1.')
        else:
            raise PatternError('Product has more than 2 factors.')

    # # # CONSIDERING FRACTIONS # # #
    def get_reciprocal(self):
        return self._new(*(get_reciprocal(factor) for factor in self))

    def fraction_dichotomize(self):
        '''returns (numerator factors, denominator factors) from self.
        (in the result, denominator factors will have positive exponents)'''
        numer_factors, factors_for_denom = self.dichotomize(exponent_seems_positive)
        denom_factors = [get_reciprocal(factor) for factor in factors_for_denom]
        return (numer_factors, denom_factors)

    def fraction_split(self):
        '''returns (numerator, denominator)'''
        numer, product_for_denom = self.split(exponent_seems_positive)
        denom = get_reciprocal(product_for_denom)
        return (numer, denom)

    # # # DIVISION # # #
    def _adjust_base_powers(self, base_power_tuples, *, mode='add', missing_ok=True):
        '''for (base, power) in base_power_tuples, find base in self and add (or subtract) power to its exponent.

        for more help, see help(self._add_base_powers) or help(self._subtract_base_powers).
        returns result of adjusting base powers in self.
        '''
        factors = _adjusted_factor_powers(list(self), base_power_tuples, mode=mode, missing_ok=missing_ok)
        result = tuple(self.power(f[0], f[1]) if ftup else f for (f, ftup) in factors)
        return self._new(*result)

    def _add_base_powers(self, base_power_tuples, *, missing_ok=True):
        '''for (base, power) in base_power_tuples, find base in self and add power to its exponent.
        if base not in self, put a new factor at the end of self like (base ^ power).
        E.g. (x^5 * z)._add_base_powers((x, 2), (y, -1)) --> x^7 * z * y^-1

        missing_ok: bool, default True
            whether it is okay for base to not be found in bases of factors in self.
            False --> raise PatternError if base not found in bases of factors in self.
        '''
        return self._adjust_base_powers(base_power_tuples, mode='add')

    def _subtract_base_powers(self, base_power_tuples, *, missing_ok=True):
        '''for (base, power) in base_power_tuples, find base in self and subtract power from its exponent.
        if base not in self, put a new factor at the end of self like (base ^ -power).
        E.g. (x^5 * z)._subtract_base_powers((x, 2), (y, -1)) --> x^3 * z * y

        missing_ok: bool, default True
            whether it is okay for base to not be found in bases of factors in self.
            False --> raise PatternError if base not found in bases of factors in self.
        '''
        return self._adjust_base_powers(base_power_tuples, mode='subtract')


@initializer_for(Product)
def product(*args, simplify_id=False, **kw):
    '''return product of the args provided.
    Usually this means return Product(*args, **kw).
    However, if there are less than 2 arguments, different behavior occurs:
        len(args)==1 --> return args[0]
        len(args)==0 --> return Product.IDENTITY (i.e. 1)

    simplify_id: bool, default False
        if simplify_id and any arg is 0 or 1, does the appropriate simpliciation:
            x*0 --> 0, x*1 --> x.
    '''
    if simplify_id:
        return producted(*args, **kw)
    if len(args)>=2:
        return Product(*args, **kw)
    elif len(args)==1:
        return args[0]
    else:# len(args)==0:
        return Product.IDENTITY

def producted(*args, **kw):
    '''return product of the args provided.
    Usually this means return INITIALIZERS.product(*args, **kw).
    However, if any of the args are 0 or 1, do the appropriate simplification:
        0*x=0, 1*x=x  (i.e. removes all args equal to 1)
    Only checks integer equality, not complicated equality (e.g. Sum(0,0) won't register as 0 here).
    '''
    if any(int_equals(arg, ZERO) for arg in args):
        return ZERO
    args_to_use = tuple(arg for arg in args if not int_equals(arg, ONE))
    return INITIALIZERS.product(*args_to_use, simplify_id=False, **kw)


''' --------------------- Arithmetic: Multiplication and Negation --------------------- '''

def _mul_quickcheck(self, b):
    '''return (if a check condition was satisfied, result else None)
    if b == Product.IDENTITY, return (True, copy_if_possible(self))
    if b == 0, return (True, 0)
    else, return (False, None).
    '''
    if equals(b, Product.IDENTITY):
        return (True, copy_if_possible(self))
    elif _equals0(b):
        return (True, 0)
    else:
        return (False, None)

def _neg_quickcheck(self, b):
    '''return (if a check condition was satisfied, result else None)
    if b == -1, and self.has_minus_sign(), return (True, self.negation())
    else, return (False, None)
    '''
    if equals(b, -1) and self.has_minus_sign():
        return (True, self.negation())
    else:
        return (False, None)

with binding.to(Product):
    @binding
    @_abstract_math
    def __mul__(self, b):
        '''return self * b, but a bit nicer than just product(self, b):
        If b == Product.IDENTITY, return copy_if_possible(self). If b == 0, return 0.
        If b == -1, and self.has_minus_sign(), return self.negation().
        Otherwise return self._new(*self, b).
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        check, result = _mul_quickcheck(self, b)
        if check:
            return result
        ncheck, nresult = _neg_quickcheck(self, b)
        if ncheck:
            return nresult
        return self._new(*self, b)

    @binding
    @_abstract_math
    def __rmul__(self, b):
        '''return b * self, but a bit nicer than just product(b, self):
        If b == Product.IDENTITY, return copy_if_possible(self). If b == 0, return 0.
        If b == -1, return self.negation().
        Otherwise return self._new(b, *self).
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        check, result = _mul_quickcheck(self, b)
        if check:
            return result
        ncheck, nresult = _neg_quickcheck(self, b)
        if ncheck:
            return nresult
        return self._new(b, *self)

with binding.to(AbstractOperation):
    @binding
    @_abstract_math
    def __mul__(self, b):
        '''return b * self, but a bit nicer than just product(b, self):
        If b == Product.IDENTITY, return copy_if_possible(self). If b == 0, return 0.
        Otherwise return self.product(self, b)
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        check, result = _mul_quickcheck(self, b)
        return result if check else self.product(self, b)

    @binding
    @_abstract_math
    def __rmul__(self, b):
        '''return self * b, but a bit nicer than just product(b, self):
        If b == Product.IDENTITY, return copy_if_possible(self). If b == 0, return 0.
        Otherwise return self.product(b, self)
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        check, result = _mul_quickcheck(self, b)
        return result if check else self.product(b, self)


''' --------------------- Product SIMPLIFY_OPS --------------------- '''

@simplify_op(Product, alias='_collect')
def _product_collect(self, **kw__None):
    '''collects all terms with the same base. E.g. x * x^n --> x^(n+1)'''
    bases_and_powers = [get_base_and_power(t) for t in self]
    # collect like terms - record bases and powers
    result_bases  = []
    result_powers = []
    collected_any = False
    for sbase, spower in bases_and_powers:
        for i, rbase in enumerate(result_bases):
            if equals(rbase, sbase):
                result_powers[i] = result_powers[i] + spower
                collected_any = True
                break
        else: # didn't break
            result_bases.append(sbase)
            result_powers.append(spower)
    if not collected_any:
        return self  # return self, exactly, to help indicate nothing was changed.
    # convert to Power (for all terms with power!=1)
    result_terms = (base if power is ONE else self.power(base, power)
                    for base, power in zip(result_bases, result_powers))
    return self._new(*result_terms)

# note about _product_collect_advanced:
#   wrote it before deciding to make _power_distribute a simplify_op too.
#   when _power_distribute is a simplify_op, there's no need for _product_collect_advanced;
#   it is fully handled by a combination of _product_collect and _power_distribute.
simplify_op_skip_for(Product, '_product_collect_advanced')  # do product_collect instead.

@simplify_op(Product)
def _product_collect_advanced(self, **kw__None):
    '''collects all terms with the same base. E.g. x * x^n --> x^(n+1)
    Also looks inside powers of products, E.g. x * (x * y * z)^n --> x^(n+1) * (y * z)^n.
    Also treats nicely exact matches, E.g. (x * y)^3 * (x * y)^2 --> (x * y)^5  (not x^5 * y^5).
        But note any non-exact match will break this, e.g. multiply that by x, --> x^6 * y^5.
    '''
    result = []  # list of lists like: [base, base factors, power, whether power is a dict]
        # if power is not a dict, it represents the power shared by all base factors,
        #    i.e. just raise base to this power; no need to break into factors.
        # if power is a dict, power[i] is the power for factors[i]
        #    all factors with same power will be put into the product together.
        #    e.g. power = {0: 7, 1: -1, 2: 0, 3: 7} --> (f0 * f3)^7 * f1^-1 * f2^0
    bases_and_powers = [get_base_and_power(t) for t in self]
    base_factors_power = [(base, get_factors(base), power) for base, power in bases_and_powers]
    collected_any = False
    for sbase, sfactors, spower in base_factors_power:
        # check for exact match; sbase==rbase
        found_exact_match = False
        for i, (rbase, rfactors, rpower, rpdbool) in enumerate(result):
            if equals(sbase, rbase):
                collected_any = True
                found_exact_match = True
                if rpdbool:
                    rpower.update({rpkey: rpval+spower for rpkey, rpval in rpower.items()})
                else:
                    result[i][2] = rpower + spower  # [2] <--> power
                break
        if found_exact_match:
            continue
        # check for matching factors; comparing to all factors in all terms in result.
        matched_any_factors = False
        js = 0
        while js < len(sfactors):
            sf = sfactors[js]
            for i, (rbase, rfactors, rpower, rpdbool) in enumerate(result):
                # if sfactors[js] matches any rfactors, pop js, and add its power in result.
                matched_factor_here = False
                for i_rf, rf in enumerate(rfactors):
                    if equals(rf, sf):
                        collected_any = True
                        matched_any_factors = True
                        matched_factor_here = True
                        sfactors.pop(js)
                        # tell result[i] that its i_rf'th factor gets +spower to its exponent.
                        # this requires rpower being a dict, so first convert it to a dict if needed.
                        if not rpdbool:  # << convert rpower to dict.
                            result[i][2] = {j_rf: rpower for j_rf in range(len(rfactors))}
                            rpower = result[i][2]
                            result[i][3] = rpdbool = True
                        rpower[i_rf] = rpower[i_rf] + spower
                        break
                if matched_factor_here:
                    break  # don't check other terms in result; we already matched sf to a factor.
            else:  # didn't break, i.e. didn't match any factors in result
                js += 1
        if len(sfactors) > 0:  # at least one unmatched factor
            if matched_any_factors:
                sbase = self.product(*sfactors)
            result.append([sbase, sfactors, spower, False])  # [base, base factors, power, whether power is a dict]
    # convert result into product.
    if not collected_any:
        return self  # return self, exactly, to help indicate nothing was changed.
    # result is a list of lists like: [base, base factors, power, whether power is a dict]
    #   if power is a dict, power[i] is the power for factors[i].
    # here, convert power dicts so that newpower[p] is the list of indices for factors raised to p.
    for i, (rbase, rfactors, rpower, rpdbool) in enumerate(result):
        if rpdbool:
            newpow = dict()
            for i_rf, p in rpower.items():
                try:
                    pindices = newpow[p]
                except KeyError:
                    newpow[p] = [i_rf]
                else:
                    pindices.append(i_rf)
            result[i][2] = newpow
    # now, convert the result from list of lists format into a single list of factors; then do self._new and return.
    final_result = []
    for rbase, rfactors, rnewpower, rpdbool in result:
        if rpdbool:
            for p, rf_indices in rnewpower.items():
                base = self.product(*(rfactors[i_rf] for i_rf in rf_indices))
                term = base if p is ONE else self.power(base, p)
                final_result.append(term)
        else:
            term = rbase if rnewpower is ONE else self.power(rbase, rnewpower)
            final_result.append(term)
    return self._new(*final_result)

simplify_op_skip_for(Product, '_commutative_simplify_id')  # we run this in _product_simplify_id.

@simplify_op(Product, alias='_simplify_id')
def _product_simplify_id(self, _simplify_x_over_x=True, **kw):
    '''converts 1*x --> x, x^n * x^-n --> 1, at top layer of self.

    _simplify_x_over_x: bool, default True
        whether to handle the case: x^n * x^-n --> 1.
        Note that this case also happens to be handled by the more general _product_collect,
        however the check for it here is much faster,
        because we first look for equal and opposite exponents instead of equality amongst bases.
        Putting this check here is desireable because this case occurrs often,
            e.g. a user may divide by x to remove it from a product mathematically.
        But since it is a bit slower than just the other checks, _simplify_x_over_x=False can disable it.
    '''
    # handle the 1*x --> x.
    self = self._commutative_simplify_id(**kw)
    if not isinstance(self, Product):
        return self  # self after _commutative_simplify_id is no longer a Product.
    # handle the x^n * x^-n --> 1
    if _simplify_x_over_x:
        return self._product_simplify_x_over_x(**kw)

simplify_op_skip_for(Product, '_product_simplify_x_over_x')  # we run this in _product_simplify_id.
@simplify_op(Product)
def _product_simplify_x_over_x(self, **kw__None):
    '''converts x^n * x^-n --> 1, at top layer of self.
    This happens to be handled by the more general _product_collect,
        so there is no need to run this if ALSO running _product_collect.
        However, the implementation here is faster for this specific case,
        since we look for equal and opposite exponents before checking equality of bases.

    Note: a previous implementation used gcf between bases.
        This was removed since it is slow. You can instead just _power_flatten first.
    '''
    bases_powers_and_t = [(get_base_and_power(t), t) for t in self]
    # track stuff we've handled - if adding x^-n but x^n exists, instead just remove x^n.
    result = []
    simplified_any = False
    for (sbase, spower), storig in bases_powers_and_t:
        # if (s == 1/r) for any r in result, remove r from result
        # otherwise, put s in result.
        # (could use basics_tools.is_reciprocal, but it's less efficient.)
        for i, ((rbase, rpower), torig) in enumerate(result):
            if equals(spower, -1 * rpower):
                if equals(sbase, rbase):
                    del result[i]
                    simplified_any = True
                    break
        else: # didn't break
            result.append(((sbase, spower), storig))
    if not simplified_any:
        return self  # return self, exactly, to help indicate nothing was changed.
    # make new Product with all the non-removed terms.
    result_terms = (torig for ((_, _), torig) in result)
    return self._new(*result_terms)

@simplify_op(Product, alias='_consolidate_signs')
def _product_consolidate_minus_signs(self, **kw__None):
    '''consolidates minus signs in self so that there are only 1 or 0 factors with a minus sign.
    if any factors are -1, prioritizes eliminating those factors when possible.
    '''
    # most of the time, we probably will not simplify anything here.
    # we call count_minus_signs_in_factors() since its value may be cached for efficiency.
    if self.count_minus_signs_in_factors() <= 1:
        return self  # return self, exactly, to help indicate nothing was changed.

    # else, there are at least 2 minus signs. we will probably simplify something.
    # we will move things from minus (or negone) to plus (or one) to indicate which have changed.
    minus = OrderedDict() # (count minus signs in factor, factor) for each factor with minus sign(s).
    negone = OrderedDict() # factors equal to -1.
    for i, factor in enumerate(self):
        icount = count_minus_signs_in_factors(factor)
        if (icount % 2) == 1:
            if equals(factor, -1):
                negone[i] = factor
            else:
                minus[i] = (icount, factor)
    one = OrderedDict()  # factors where 1 appears after turning -1 into 1.
    plus = OrderedDict()  # factors which are now positive but were previously negative.
    _skip = OrderedDict()  # factors where negation doesn't reduce number of negative signs.
    
    def move_and_negate_one():
        '''moves first -1 in `negone` to `one`, and negate its value.'''
        key = next(iter(negone))
        one[key] = -negone.pop(key)

    def attempt_move_and_negate_minus():
        '''attempt to move first item in `minus` to `plus`, and negate its value.
        if negating its value doesn't reduce number of minus signs in it:
            move it to `_skip` instead, and
            try again, with the next item in minus.
        return whether an item was moved to `plus` (even possibly not on the first attempt.)
        '''
        while len(minus) > 0:
            key, (icount, factor) = minus.popitem(last=False)  # pop first item
            negated = -factor
            if count_minus_signs_in_factors(negated) < icount:
                plus[key] = negated
                return True
            else:
                _skip[key] = factor
        return False

    # prioritize factors of -1 first.
    while len(negone) > 0:
        if len(negone) >= 2:  # two or more '-1' factors -- cancel out 2 of them.
            move_and_negate_one()
            move_and_negate_one()  # (this line intentionally appears twice.)
        else:  # precicely one '-1' factor -- cancel it with something from minus.
            if len(minus) == 0:
                break  # only 1 minus factor remaining, and it is -1.
            else: # len(i_minus) > 0
                moved = attempt_move_and_negate_minus()
                if moved:
                    move_and_negate_one()
    # iterate through other factors.
    while len(minus) >= 2:
        moved = attempt_move_and_negate_minus()
        if not moved:
            break
        moved2 = attempt_move_and_negate_minus()
        if not moved2:  # pop last item in plus; didn't find another minus sign to remove.
            _unmove = plus.popitem(last=True)
            break

    if (len(plus) == 0) and (len(one) == 0):
        return self  # return self, exactly, to help indicate nothing was changed.

    # put together the new list of factors.
    new_factors = [factor for factor in self]
    for i, fnew in plus.items():
        new_factors[i] = fnew
    for i in reversed(one.keys()):  # reversed -- remove larger i first. (assumes one.keys() is sorted)
        del new_factors[i]
    # return result
    return self._new(*new_factors)

simplify_op_skip_for(Product, '_product_distribute_minus_one')  # incompatible with _sum_canonical_signs.

@simplify_op(Product, aliases=('_distribute_minus_one', '_simplifying_distribute'),
             order=1)   # order=1 --> "after _product_consolidate_minus_signs".
def _product_distribute_minus_one(self, **kw__None):
    '''-1 * (x - y) --> -x + y.
    distribute -1 factor into a Sum factor, if possible, but only if the Sum has a factor of -1 in it.

    [TODO][maybe] decide a "canonical" "whether to distribute -1" when terms negative & some positive;
        write a function to distribute or factor out a -1 in those cases.
        E.g. it would always convert -x + y into -1 * (x - y), but keep x - y unchanged.
    '''
    factors = list(self)
    i_minus_one = find(factors, MINUS_ONE, equals=equals)
    if i_minus_one is None:
        return self  # return self, exactly, to help indicate nothing was changed.
    factor_summands = tuple(get_summands(factor) for factor in factors)
    N_summands = tuple(len(summands) for summands in factor_summands)
    try:
        i_sum_ = next(i for (i, summands) in enumerate(factor_summands)
                      if len(summands)>1
                      and any(equals(factor, MINUS_ONE) for summand in summands for factor in get_factors(summand)))
    except StopIteration:
        return self  # return self, exactly, to help indicate nothing was changed.
    sum_ = factors[i_sum_]
    new_sum_ = sum_._new(*(-summand for summand in sum_))
    result = [new_sum_ if i==i_sum_ else factor
                for i, factor in enumerate(factors) if i!=i_minus_one]
    return self._new(*result)

simplify_op_skip_for(Product, '_product_distribute_common_base')  # handled by _sum_collect_common_base...

@simplify_op(Product, aliases=('_distribute_common_base', '_simplifying_distribute'), order=1)
def _product_distribute_common_base(self, **kw__None):
    '''finds and distributes factors with base appearing in all summands in a Sum factor in self.
    Also potentially a Power factor with Sum base.
    Examples:
        x^3 * y * (x^-1 + x^5 * z) --> y * (x^2 + x^8 * z).
        x * (x^3 + x^7)^-1 --> (x^2 + x^6)^-1
        x^6 * (x^7 + x^-8)^3 --> (x^(7+2) + x^(-8+2))^3, since 6/3 == 2.
        x^7 * (x^7 + x^-8)^3 --> x * (x^(7+2) + x^(-8+2))^3,   see note:
            if the sum exponent doesn't evenly divide the factor's exponent,
            move inside the portion which is evenly divided, and keep outside the rest.
        Also note:
            only move factors into base if base's power is an integer.
            E.g. skip (x^2 + x^3)^(3/2).
    [TODO] deal with common base in two sums.
        E.g. (x * y + x^7 * z) * (x^-3 * B + x^5) --> (y + x^6 * z) * (x^-2 * B + x^6).
        Need to decide which rules to use in that case (i.e. which term should lose the common base?)
    '''
    # bookkeeping
    base_and_powers = {i: get_base_and_power(factor) for i, factor in enumerate(self)}
    unused_factors = {i: factor for i, factor in enumerate(self)}  # << the (i, factor)s we didn't yet distribute.
    unconsidered_factors = unused_factors.copy()  # << the (i, factor)s we didn't yet distribute OR consider in the loop.
    factor_locations = {i: 0 for i in unused_factors.keys()}  # << 0 for unused_factors; 1 for distributed_factors.
    distributed_factors = dict()  # << the (i, factor)s after distributing. i is the location of the sum factor.
    # loop through factors; if factor is a sum with common base(s), look for those base(s) in other factors.
    while len(unused_factors) >= 2:  # << if there's less than unused 2 factors, there's nothing left to distribute.
        # look for base sums with common bases; distribute if any other factors in self have those bases.
        for i, factor in tuple(unconsidered_factors.items()):
            del unconsidered_factors[i]
            base, power = base_and_powers[i]
            # if base not a sum, skip.
            summands = get_summands(base)
            if len(summands) == 1:
                continue
            # if power not an integer, skip.
            if not is_integer(power):
                continue
            # if no common bases, skip.
            common_bases = get_common_bases(*summands)
            if len(common_bases) == 0:
                continue
            # look for factors matching a common base, OR with base matching a common base.
            to_distribute = dict()
            for j, jfactor in tuple(unused_factors.items()):  # tuple(...) in case dict changes during iteration.
                if j == i:
                    continue
                if any(equals(jfactor, cbase) for cbase in common_bases):
                    to_distribute[j] = (jfactor, ONE)
                else:
                    jbase, jpower = base_and_powers[j]
                    if any(equals(jbase, cbase) for cbase in common_bases):
                        to_distribute[j] = (jbase, jpower)
            # if found no factors to distribute, continue.
            if len(to_distribute) == 0:
                continue
            # how much of each factor to actually distribute?
            j_in = dict()  # distribute to ibase (which is the sum, possibly inside a power)
            j_out = dict()  # portion of jfactor to remain outside ibase (only for jfactors which get split.)
            if power is ONE:  # simple answer if ipower==1: distribute the whole jfactor!
                j_in = {j: jbase if jpower is ONE else self.power(jbase, jpower)
                                for j, (jbase, jpower) in to_distribute.items()}
                # j_out = empty dict.
            elif equals(power, MINUS_ONE):
                j_in = {j: self.power(jbase, -jpower)
                                for j, (jbase, jpower) in to_distribute.items()}
                # j_out = empty dict.
            else:
                for jbase, jpower in tuple(to_distribute.items()):
                    if equals(jpower, power):
                        j_in[j] = jbase
                        continue
                    try:  # check whether & how much to distribute.
                        if abs(jpower) < abs(power):
                            raise ValueError('nothing to distribute')  #E.g. x^2 * (x + x^5)^3; 2 < 3
                        jpow_in = jpower // power
                        jpow_out = jpower - power * jpow_in
                    except (TypeError, ValueError):  # TypeError if jpower or power hasn't defined an operation, e.g. //
                        del to_distribute[j]  # << nothing to distribute. 
                    else:
                        j_in[j] = self.power(jbase, jpow_in)
                        if not _equals0(jpow_out, ZERO):
                            j_out[j] = jbase
            # which order to put factors in result? (keep original ordering since it's prettier.)
            in_before  = [jfactor for j, jfactor in j_in.items() if j < i]
            in_after   = [jfactor for j, jfactor in j_in.items() if j > i]
            # distribute to factor
            new_base_summands = tuple(self._new(*in_before, summand, *in_after) for summand in base)
            new_base = base._new(*new_base_summands)
            distributed_factors[i] = new_base if power is ONE else self.power(new_base, power)
            # bookkeeping
            factor_locations[i] = 1  # << 0 for unused_factors; 1 for distributed_factors.
            del unused_factors[i]
            j_fully_distributed = set(j_in.keys()) - set(j_out.keys())
            for j in j_fully_distributed:
                del unused_factors[j]
                del factor_locations[j]
                if j > i:  # (if j < i, unconsidered_factors[j] was already deleted, probably when we considered j.)
                    del unconsidered_factors[j]
            for j, jfactor in j_out.items():
                unused_factors[j] = jfactor
                base_and_powers[j] = get_base_and_power(jfactor)
            # break, since we distributed something.
            break
        else:  # didn't break -- distributed nothing. Stop looping
            break
    if len(distributed_factors) == 0:
        return self  # return self, exactly, to help indicate nothing was changed.
    result = tuple(unused_factors[i] if loc==0 else distributed_factors[i] for i, loc in factor_locations.items())
    return self._new(*result)


@simplify_op(Product, aliases=('_distribute_cancels', '_simplifying_distribute'), order=1)
def _product_distribute_cancels(self, **kw__None):
    '''distributes factors which cancel factors inside a sum. E.g. X * (2 + 3 / X) --> 2 * X + 3.
    only distributes if it wont make new terms with seemingly-negative exponents.

    different behavior depending on sum's exponent.
        exponent of 1 --> searching for a match to negative of the factor's exponent.
        exponent of -1 --> searching for a match to the factor's exponent.
            E.g. X^-2 * (7 + 3 / X^2)^-1 --> (7 * X^2 + 3)^-1
        other exponent --> unaffected.
            [TODO] maybe should be affected..? carefully consider issues.
            e.g. X * sqrt(Y) is not always sqrt(X**2 * Y); fails for X<0.
    '''
    adjusted_any = False
    prodl = ProductLite.from_term(self)
    sums = dict()
    _cbins_sums = ComplexityBinning()  # complexity bins for compressing SumLites.
    for i, powl in prodl.items():  # i <--> i'th factor
        exp = powl.exp
        if isinstance(powl.base, Sum) and (exp is ONE or exp is MINUS_ONE):
            suml = SumLite.from_term(powl.base, compress=False)  # compress below instead.
            _any_compressed = suml.compress(cbins=_cbins_sums)
            _any_collected = suml.products_collect()
            if _any_compressed or _any_collected:
                adjusted_any = True
            bases_and_indices = suml.bases_and_i_to_j()
            sums[i] = (suml, exp, bases_and_indices)  # exp is the exponent for this whole sum.
            powl.base = suml
    for i, powl in tuple(prodl.items()):  # i <--> i'th factor
        base, iexp = powl
        if base is MINUS_ONE:  # let other routines handle factors of -1.
            continue
        minus_iexp = -iexp
        id_ = id(base)
        for j, (suml, sumexp, bases_and_indices) in sums.items():  # j <--> j'th factor (which is a sum)
            if j==i:
                continue
            if sumexp is MINUS_ONE:
                search_exp = iexp
            else:
                search_exp = minus_iexp
            if not seems_negative(search_exp):
                # only distribute if we'd end up canceling terms with negative-seeming exponents.
                # e.g. even though (X^-1 * (7 + X) --> 7 X^-1 + 1) is valid,
                #   it's not the "intuitive" thing to do.
                continue
            try:
                _base, indices = bases_and_indices[id_]
            except KeyError:  # base not found in this sum
                continue
            flag1 = False
            for i1, j1 in indices.items():
                if equals(search_exp, suml[i1][j1].exp):
                    # distribute this powl to this suml!
                    adjusted_any = True
                    if sumexp is MINUS_ONE:
                        suml1 = suml.divide_lite(powl)
                    else:
                        suml1 = suml.multiply_lite(powl)
                    prodl.pop(i)   # removed this factor (i) from prodl; distributed it into suml (j)
                    prodl[j] = PowerLite(suml1, sumexp)
                    sums[j] = (suml1, sumexp, suml1.bases_and_i_to_j())  # recalculate bases and indices after multiplying.
                    flag1 = True
                    break
            if flag1:
                break
    if not adjusted_any:
        return self  # return self, exactly, to help indicate nothing was changed.
    else:
        return prodl.reconstruct(force=True)
