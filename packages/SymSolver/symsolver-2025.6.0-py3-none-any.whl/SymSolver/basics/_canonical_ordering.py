"""
File Purpose: canonical ordering / methods from basics which rely on canonical ordering.
"""
import builtins  # for unambiguous sum

from .sum import Sum
from .symbols import Symbol, SYMBOLS
from .basics_tools import (
    seems_negative, get_factors, get_summands,
    without_factor
)
from ..abstracts import simplify_op, canonical_argsort, canonical_orderer
from ..numbers import IUNIT
from ..tools import (
    find, equals,
    Binding,
)

from ..defaults import DEFAULTS, ONE, MINUS_ONE

binding = Binding(locals())


''' --------------------- Symbol canonical ordering key --------------------- '''

# put these first (in order of value if values provided)
# if "alphabetical" is not the intuitive order, order can be controlled here.
# for all other terms or in case of matching value here, the default will be alphabetical.
CANONICAL_ORDER_FIRST = {'k': 0, r'\omega': 0, 'E': 1, 'B': 1}
CANONICAL_ORDER_N_DEFAULT = max(CANONICAL_ORDER_FIRST.values()) + 1

with binding.to(Symbol):
    @binding
    def _canonical_ordering_key(self):
        '''returns key to use for canonical ordering of symbols.'''
        contents = self._repr_contents()
        ckey = ', '.join(contents[1:])
        s = self.s
        N = CANONICAL_ORDER_FIRST.get(s, CANONICAL_ORDER_N_DEFAULT)
        return (N, s, ckey)

SYMBOLS.viewsort = canonical_orderer  # when displaying SYMBOLS, use canonical ordering to decide order.


''' --------------------- Sum simplify signs & imaginary unit --------------------- '''

@simplify_op(Sum, alias='_canonical_signs')
def _sum_canonical_signs_and_imag(self, **kw__None):
    '''if summands negative signs and i factors are not "canonical", factor -1 and/or i out of self.

    canonical determined by:
        1) fewer imaginary-seeming terms than real-seeming terms.
            If same number of each, first term has factor of i in it.
        2) fewer negative-seeming terms than other terms.
            If same number of each, first term has factor of -1 in it.
        "first term" determined by canonical sort where factors of i and -1 are ignored.
    '''
    has_i = tuple((IUNIT in get_factors(summand)) for summand in self)
    seeming_negative = tuple(seems_negative(summand) for summand in self)
    count_imag = sum(has_i)
    count_real = len(self) - count_imag
    count_neg = sum(seeming_negative)
    count_pos = len(self) - count_neg
    imag_canonical = (count_imag < count_real)
    sign_canonical = (count_neg < count_pos)
    if imag_canonical and sign_canonical:
        return self  # return self, exactly, to help indicate nothing was changed.
    # we'll definitely use this var (either if unsure, or later to help with factoring):
    summands_without_i = tuple(without_factor(summand, IUNIT) if imag else summand
                            for summand, imag in zip(self, has_i))
    # might be unsure about canonical, if counts are equal.
    imag_unsure_if_canonical = (not imag_canonical) and (count_imag == count_real)
    sign_unsure_if_canonical = (not sign_canonical) and (count_pos == count_neg)
    if imag_unsure_if_canonical or sign_unsure_if_canonical:
        summands_canonical = tuple(without_factor(summand, MINUS_ONE, missing_ok=True) if neg else summand
                                    for summand, neg in zip(summands_without_i, seeming_negative))
        aa = canonical_argsort(summands_canonical)
        if imag_unsure_if_canonical:
            imag_canonical = has_i[aa[0]]
        if sign_unsure_if_canonical:  # check if it's actually canonical, based on sort.
            sign_canonical = seeming_negative[aa[0]]
        # check if both are canonical. If so, don't change self.
        if imag_canonical and sign_canonical:
            return self  # return self, exactly, to help indicate nothing was changed.
    # << if we reach this point, not in canonical order.
    summands = list(self)
    if not imag_canonical:  # factor out i
        summands = [noi if imag else -summand * IUNIT
                    for summand, noi, imag in zip(self, summands_without_i, has_i)]
    if not sign_canonical:  # factor out -1
        summands = [-summand for summand in summands]
    outer = []
    if not sign_canonical: outer.append(MINUS_ONE)
    if not imag_canonical: outer.append(IUNIT)
    return self.product(*outer, self._new(*summands))


@simplify_op(Sum, alias='_simplifying_distribute')
def _sum_distribute_internal_minus_one(self, **kw__None):
    '''z - (x + y) --> z - x - y. Only distributes if ALL internal summands don't seem negative.
    (e.g. x & y both seem not negative in example above.)
    Also, only distributes if it is -1 times a sum, with no other factors.
    '''
    result = []
    any_changes = False
    summands = list(self)
    for summand in summands:
        factors = get_factors(summand)
        if len(factors) != 2:
            result.append(summand)
            continue
        i_minus_one = find(factors, MINUS_ONE, equals=equals)
        if i_minus_one is None:
            result.append(summand)
            continue
        if i_minus_one == 0:
            fsm = get_summands(factors[1])
        else:  # i_minus_one == 1
            fsm = get_summands(factors[0])
        if len(fsm) == 1:
            result.append(summand)
            continue
        new_summands = [-summand_in_factor for summand_in_factor in fsm]
        result = result + new_summands  # list addition
        any_changes = True
    if not any_changes:
        return self  # return self, exactly, to help indicate nothing was changed.
    else:
        return self._new(*result)
