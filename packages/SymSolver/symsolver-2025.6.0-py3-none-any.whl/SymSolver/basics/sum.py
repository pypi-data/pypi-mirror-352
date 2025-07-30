"""
File Purpose: Sum
See also: sum
"""

from ..initializers import initializer_for, INITIALIZERS
from ..abstracts import (
    AbelianOperation, SubbableObject,
    AbstractOperation,
    simplify_op, simplify_op_skip_for,
    _equals0,
    _abstract_math,
)
from .basics_tools import (
    get_factors_numeric_and_other,
    get_common_bases, get_factors, get_base_and_power, _adjusted_factor_powers,
    _is_negation__from_info,
    add,
    copy_if_possible,
)
from ..tools import (
    apply, equals,
    int_equals,
    min_number,
    caching_attr_simple_if, alias,
    Binding,
)
from ..defaults import DEFAULTS, ZERO

binding = Binding(locals())


class Sum(AbelianOperation, SubbableObject):
    '''Addition operation, e.g. 7+x+y.'''
    IDENTITY = ZERO  # == 0

    @property
    def OPERATION(self):
        '''returns the operation which self represents: addition.
        I.e. returns a function f(*args) --> args[0] + args[1] + ... + args[-1]
        '''
        return add

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def _equals0(self):
        '''returns whether self == 0.'''
        return all(_equals0(t) for t in self)

    def get_summands(self):
        '''returns list of summands for self, i.e. list(self)'''
        return list(self)

    without_summand = alias('without_term')


@initializer_for(Sum)
def sum(*args, **kw):
    '''return sum of the args provided.
    Usually this means return Sum(*args, **kw).
    However, if there are less than 2 arguments, different behavior occurs:
        len(args)==1 --> return args[0]
        len(args)==0 --> return Sum.IDENTITY (i.e. 0)
    '''
    if len(args)>=2:
        return Sum(*args, **kw)
    elif len(args)==1:
        return args[0]
    else:# len(args)==0:
        return Sum.IDENTITY

def summed(*args, **kw):
    '''return sum of the args provided.
    Usually this means return INITIALIZERS.sum(*args, **kw).
    However, if any of the args are Sum.IDENTITY, remove those args first.
    '''
    args_to_use = tuple(arg for arg in args if not int_equals(arg, Sum.IDENTITY))
    return INITIALIZERS.sum(*args_to_use, **kw)


''' --------------------- Arithmetic: Addition --------------------- '''

def _add_quickcheck(self, b):
    '''return (if a check condition was satisfied, result else None)
    if b == Sum.IDENTITY, return (True, copy_if_possible(self))
    else, return (False, None).
    '''
    if equals(b, Sum.IDENTITY):
        return (True, copy_if_possible(self))
    else:
        return (False, None)

with binding.to(Sum):
    @binding
    @_abstract_math
    def __add__(self, b):
        '''return self + b, but a bit nicer than just sum(self, b):
        if b == Sum.IDENTITY, return (True, copy_if_possible(self))
        Otherwise return self._new(*self, b).
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        check, result = _add_quickcheck(self, b)
        return result if check else self._new(*self, b)

    @binding
    @_abstract_math
    def __radd__(self, b):
        '''return b + self, but a bit nicer than just sum(b, self):
        if b == Sum.IDENTITY, return (True, copy_if_possible(self))
        Otherwise return self._new(b, *self).
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        check, result = _add_quickcheck(self, b)
        return result if check else self._new(b, *self)

with binding.to(AbstractOperation):
    @binding
    @_abstract_math
    def __add__(self, b):
        '''return b + self, but a bit nicer than just sum(b, self):
        if b == Sum.IDENTITY, return (True, copy_if_possible(self))
        Otherwise return self.sum(self, b)
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        check, result = _add_quickcheck(self, b)
        return result if check else self.sum(self, b)

    @binding
    @_abstract_math
    def __radd__(self, b):
        '''return b + self, but a bit nicer than just sum(b, self):
        if b == Sum.IDENTITY, return (True, copy_if_possible(self))
        Otherwise return self.sum(b, self)
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        check, result = _add_quickcheck(self, b)
        return result if check else self.sum(b, self)


''' --------------------- Sum SIMPLIFY_OPS --------------------- '''

simplify_op_skip_for(Sum, '_commutative_simplify_id')  # we run this in _sum_simplify_id.

@simplify_op(Sum, alias='_simplify_id')
def _sum_simplify_id(self, _simplify_x_minus_x=False, **kw):
    '''converts 0+x --> x, -x + x --> 0, at top layer of self.

    _simplify_x_minus_x: bool, default False
        whether to handle the case: -x + x --> 0.
        Note that this case also happens to be handled by the more general _sum_collect.
        The check here is slower since it also checks _is_surely_negation for all pairs of terms.
    '''
    # handle the 0 + x --> x.
    self = self._commutative_simplify_id(**kw)
    if not isinstance(self, Sum):
        return self  # self after _commutative_simplify_id is no longer a Sum.
    # handle the -x + x --> 0
    if _simplify_x_minus_x:
        return self._sum_simplify_x_minus_x(**kw)
    else:
        return self

simplify_op_skip_for(Sum, '_sum_simplify_x_minus_x')  # we run this in _sum_simplify_id.
def _sum_simplify_x_minus_x(self, **kw__None):
    '''converts -x + x --> 0, at top layer of self.
    This happens to be handled by the more general _sum_collect,
        so there is no need to run this if ALSO running _sum_collect.
        However, the implementation here is faster for this specific case.

    Also allows to handle less obvious cases of x + y --> 0,
    by checking x._is_surely_negation(y), if that method is available.
    E.g. (A cross B) negates (B cross A), and CrossProduct provides _is_surely_negation.

    [TODO] also handle -(x+y) + x + y --> 0.

    [TODO] either make this method MUCH faster, or remove it (or disable it by default)
        (can be disabled by default if setting _simplify_x_minus_x=False in _sum_simplify_id.
        but, need to do some testing to learn if that provides okay results.)
    '''
    # first, allow terms of self to use their _is_surely_negation() method, if they have one.
    # x.is_surely_negation(y) can give false negatives (i.e. sometimes may be False when y == -x),
    # but should never give false positive (i.e. True --> y == -x).
    # This is useful for things like CrossProduct, where e.g. (a cross b).is_surely_negation(b cross a).
    result_terms = []
    for t in self:
        try:
            t_is_surely_negation = t._is_surely_negation
        except AttributeError:
            result_terms.append(t)
        else:
            for i, r in enumerate(result_terms):
                if t_is_surely_negation(r):
                    del result_terms[i]
                    break
            else:  # didn't break
                result_terms.append(t)
    # next, use _is_negation__from_info from basics_tools to efficiently check each remaining term's factors.
    numbers_others_and_t = [(get_factors_numeric_and_other(t), t) for t in result_terms]
    # track stuff we've handled. - if adding -x but x exists, instead just remove x.
    result = []
    simplified_any = False
    for sinfo in numbers_others_and_t:
        # if (s == -r) for any r in result, remove r from result
        # otherwise, put s in result.
        # (could use basics_tools.is_negation, but it's less efficient.)
        for i, rinfo in enumerate(result):
            # [TODO] improve efficiency here a bit, by caching things like snum_val and sf_val.
            # (see _is_negation__from_info. No need to recalculate those things many times...)
            if _is_negation__from_info(sinfo, rinfo):
                # remove r from result; don't add s to result.
                del result[i]
                simplified_any = True
                break
        else: # didn't break
            result.append(sinfo)
    if not simplified_any:
        return self  # return self, exactly, to help indicate nothing was changed.
    # make new Sum with all the non-removed terms.
    result_terms = (torig for ((_, _), torig) in result)
    return self._new(*result_terms)

#simplify_op_skip_for(Sum, '_sum_collect_common_base')   # [TODO] handle simplified() looping this & distribute.
#@simplify_op(Sum, alias='_collect_common_base')
def _sum_collect_common_base(self, **kw__None):
    '''collect common bases. I.e. factor out of all terms in self the lowest-power common bases.
    Examples:
        z * x^7 + x^2 * y --> x^2 * (z * x^5 + y).
        z * x^7 + x^2 * z^3 --> z * x^2 * (x^5 + z^2)
        x^-3 + x --> x^-3 * (1 + x^4)
        x^5 + x^3 + x^2 --> x^2 * (x^3 + x + 1)
        x^5 + x^3 + 1 --> no changes (there are no bases common to all terms).
    '''
    common_bases = get_common_bases(*self, allow_minus_1=False, split_minus=True)
    if len(common_bases) == 0:
        return self  # return self, exactly, to help indicate nothing was changed.
    base_power_tuples = tuple((base, min_number(exps, allow_default=True)) for base, exps in common_bases.items())
    if all(_equals0(power) for (base, power) in base_power_tuples):
        return self  # return self, exactly, to help indicate nothing was changed.
    # outside the sum
    collected_factor = self.product(*(self.power(base, exp, simplify_id=True) for base, exp in base_power_tuples))
    # inside the sum
    new_summands = []
    for summand in self:
        factors = get_factors(summand, split_minus=True)
        adjusted_factors = _adjusted_factor_powers(factors, base_power_tuples, mode='subtract', missing_ok=False)
        new_factors = tuple(self.power(f[0], f[1], simplify_id=True) if ftup else f for (f, ftup) in adjusted_factors)
        new_summand = self.product(*new_factors)
        new_summands.append(new_summand)
    new_sum = self._new(*new_summands)
    return self.product(collected_factor, new_sum)
