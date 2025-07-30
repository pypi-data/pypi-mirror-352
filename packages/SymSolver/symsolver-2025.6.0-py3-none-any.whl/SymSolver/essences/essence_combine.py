"""
File Purpose: manipulating / combining EssenceSymbols
"""

from .essence_symbols import (
    EssenceSymbol, ESSENCE_SYMBOLS,
    essence_symbol_for,
)
from ..abstracts import (
    simplify_op, SimplifiableObject, IterableSymbolicObject,
    get_symbols,
)
from ..basics import (
    Sum, Product,
)
from ..attributors import attributor
from ..initializers import INITIALIZERS
from ..vectors import (
    BinaryVectorProduct, DotProduct, CrossProduct,
    is_vector,
)
from ..tools import (
    apply,
    dichotomize,
    Binding, caching_attr_simple_if,
)
from ..defaults import DEFAULTS

binding = Binding(locals())

''' --------------------- Convenience Methods --------------------- '''

@attributor
def has_only_essence_symbols(obj):
    '''return whether obj has only Essence Symbols in it.
    returns obj.has_only_essence_symbols() if it exists, else False.
    '''
    try:
        obj_has_only_essence_symbols = obj.has_only_essence_symbols
    except AttributeError:
        return False
    else:
        return obj_has_only_essence_symbols()

@attributor
def has_any_essence_symbols(obj):
    '''return whether obj has any Essence Symbols in it.
    returns obj.has_any_essence_symbols() if it exists, else False.
    '''
    try:
        obj_has_any_essence_symbols = obj.has_any_essence_symbols
    except AttributeError:
        return False
    else:
        return obj_has_any_essence_symbols()

@attributor
def get_first_essence_symbol(obj):
    '''return the first EssenceSymbol found in self.
    returns obj.get_first_essence_symbol() if it exists, else None.
    '''
    try:
        obj_get_first_essence_symbol = obj.get_first_essence_symbol
    except AttributeError:
        return None
    else:
        return obj_get_first_essence_symbol()

@attributor
def _simple_combine_essence_symbols(obj, **kw):
    '''returns obj, or an EssenceSymbol if has_only_essence_symbols(obj).
    returns obj._simple_combine_essence_symbols(**kw) if it exists, else obj.
    '''
    try:
        obj_simple_combine_essence_symbols = obj._simple_combine_essence_symbols
    except AttributeError:
        return obj
    else:
        return obj_simple_combine_essence_symbols(**kw)

@attributor
def _combine_essence_symbols(obj, **kw):
    '''returns obj but with EssenceSymbols combined.
    returns obj._combine_essence_symbols(**kw) if it exists, else obj.
    May do some more intelligent tricks than _simple_combine_essence_symbols.
    E.g. E1 x + E2 x --> E3 x.
    '''
    try:
        obj_combine_essence_symbols = obj._combine_essence_symbols
    except AttributeError:
        return obj
    else:
        return obj_combine_essence_symbols(**kw)


''' --------------------- look for essence symbols --------------------- '''

# # # HAS ONLY ESSENCE SYMBOLS # # #
with binding.to(IterableSymbolicObject):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def has_only_essence_symbols(self):
        '''returns whether, for every term in self, term is an EssenceSymbol OR has_only_essence_symbols(term).'''
        return all(isinstance(term, EssenceSymbol) or has_only_essence_symbols(term) for term in self)

# # # HAS ANY ESSENCE SYMBOLS # # #
with binding.to(IterableSymbolicObject):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def has_any_essence_symbols(self):
        '''returns whether self has any essence symbols in it.'''
        return any(isinstance(term, EssenceSymbol) or has_any_essence_symbols(term) for term in self)

# # # GET FIRST ESSENCE SYMBOL # # #
with binding.to(IterableSymbolicObject):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def get_first_essence_symbol(self):
        '''returns first EssenceSymbol within self, or None if self has no essence symbols.'''
        for term in self:
            if isinstance(term, EssenceSymbol):
                return term
            result = get_first_essence_symbol(term)
            if result is not None:
                return result
        return None


''' --------------------- combine essence symbols --------------------- '''

# # # SIMPLE COMBINE ESSENCE SYMBOLS # # #
with binding.to(IterableSymbolicObject):
    @binding
    def _simple_combine_essence_symbols(self, **kw__None):
        '''if self is composed entirely of EssenceSymbol objects, return a single EssenceSymbol replacing self.
        Otherwise, just return self, unchanged.
        Note: if len(self) <= 1, makes no changes to self.
        '''
        if (len(ESSENCE_SYMBOLS) > 0) and has_only_essence_symbols(self) and len(self) > 1:
            esym0 = get_first_essence_symbol(self)
            if esym0 is not None:
                return essence_symbol_for(self, esym_like=esym0)
        return self  # return self, exactly, to help indicate nothing was changed.

@simplify_op(SimplifiableObject, alias='_combine_essence_symbols')
def _simplifiable_object_combine_essence_symbols(self, **kw):
    '''combine EssenceSymbols in self where appropriate. E.g. E1 + E2 --> E3.'''
    return _simple_combine_essence_symbols(self, **kw)

def _associative_commutative_combine_essence_symbols(self, _flatten_during_combine=True, **kw):
    '''combine EssenceSymbols in self. Self should be associative and commutative,
    e.g. inherit from AssociativeOperation and CommutativeOperation.
    E.g. E1 + E2 + x --> E3 + x
    '''
    # if no EssenceSymbols, do nothing.
    if not has_any_essence_symbols(self):
        return self
    # flatten first, e.g. E1 + (E2 + x) --> E1 + E2 + x, so that we can get to E3 + x.
    if _flatten_during_combine:
        self = self._associative_flatten(**kw)
    # combine simple
    simple_combined = _simple_combine_essence_symbols(self, **kw)
    if simple_combined is not self:
        return simple_combined
    # combine EssenceSymbols in self
    es_terms, non_es_terms = dichotomize(self, lambda s: isinstance(s, EssenceSymbol))
    if len(es_terms) > 1:
        esym0 = es_terms[0]
        new_es_replaces = self._new(*es_terms)
        es_combined = essence_symbol_for(new_es_replaces, esym_like=esym0)
        result = self._new(es_combined, *non_es_terms)
    else:
        result = self
    # if result is no longer an instance of type(self), _combine_essence_symbols then return.
    if isinstance(result, type(self)):
        return result
    else:
        return _combine_essence_symbols(result, **kw)

@simplify_op(Sum, alias='_combine_essence_symbols')
def _sum_combine_essence_symbols(self, targets=[], _debug=False, **kw):
    '''combine EssenceSymbols in self where appropriate. E.g. E1 + E2 --> E3.
    Also does _sum_collect, e.g. (E1 x + E2 x) --> (E1 + E2) x --> E3 x.
    '''
    # if no EssenceSymbols, do nothing.
    if not has_any_essence_symbols(self):
        return self
    # "standard" combine (for associative commutative operation)
    result = _associative_commutative_combine_essence_symbols(self, targets=targets, **kw)
    if not isinstance(result, type(self)):
        return result
    # use sum_collect then _combine_essence_symbols on each of the resulting summands
    kw_collect = kw
    kw_collect.update(collect_these=targets, collect_priority_only=True, collect_priority_equal=True)
    collected = result._sum_collect(**kw_collect)
    if collected is result:
        return result  # << sum_collect made no changes, so just return result.
    if not isinstance(collected, type(self)):
        # if isinstance(collected, AbstractProduct):
        #     combined_factors = tuple(_combine_essence_symbols(factor, targets=targets, **kw) for factor in collected)
        #     collected = collected._new(*combined_factors)
        return _combine_essence_symbols(collected, targets=targets, **kw)
    es_combined_summands = tuple(_combine_essence_symbols(summand, targets=targets, **kw) for summand in collected)
    if all(x is y for x, y in zip(collected, es_combined_summands)):
        return result  # << _combine_essence_symbols on summands made no changes, so just return result.
    else:
        return collected._new(*es_combined_summands)

@simplify_op(Product, alias='_combine_essence_symbols')
def _product_combine_essence_symbols(self, **kw):
    '''combine EssenceSymbols in self where appropriate. E.g. E1 * E2 --> E3.
    Also, for cross products, do:
        E1 * (x cross E2) --> x cross E3;  E1 * (E2 cross x) --> E3 cross x.
    Also, for dot products, do a similar thing (being careful about vectoriality...)
        (But not if already did it for cross-products.)
    '''
    # if no EssenceSymbols, do nothing.
    if not has_any_essence_symbols(self):
        return self
    # "standard" combine (for associative commutative operation)
    result = _associative_commutative_combine_essence_symbols(self, **kw)
    if not isinstance(result, type(self)):
        return result
    # use _combine_essence_symbols on any summand factors in self before distributing.
    es_combined_factors = []
    for factor in result:
        if isinstance(factor, Sum):
            esf = factor._combine_essence_symbols(**kw)
            es_combined_factors.append(esf)
        else:
            es_combined_factors.append(factor)
    if not all(x is y for x, y in zip(result, es_combined_factors)):
        result = result._new(*es_combined_factors)
    # distribute if it will help to combine essence symbols.
    def _contains_essence_symbol(x):
        return any(isinstance(sym, EssenceSymbol) for sym in get_symbols(x))
    result = result._distribute(distribute_sum_if=_contains_essence_symbol)
    if not isinstance(result, type(self)):
        return result
    # put scalars into dot or cross products, if possible
    es_factors, non_es_factors = dichotomize(result, lambda s: isinstance(s, EssenceSymbol))
    es_vector_factors, es_scalar_factors = dichotomize(es_factors, lambda factor: is_vector(factor))
    if len(es_scalar_factors) == 0:  # no EssenceSymbol scalar factors; nothing more to simplify.
        return result
    # E1 * (x cross E2) --> x cross E3;  E1 * (E2 cross x) --> E3 cross x.
    cps, non_cps = dichotomize(non_es_factors, lambda s: isinstance(s, CrossProduct))
    if len(cps) > 0:
        if len(cps) >= 2:
            raise NotImplementedError(f'Product of multiple cross products...: {cps}')
        cp = cps[0]  # << the one and only cross product
        if len(es_vector_factors) != 0:
            raise NotImplementedError(f'Product of cross product and vector(s)...: {cp}, {es_vector_factors}')
        cpt1, cpt2 = cp
        found_es_in_cp = False
        if isinstance(cpt1, EssenceSymbol):
            es_cpt = cpt1
            found_es_in_cp = 't1'
            non_es_from_cp = cpt2
        elif isinstance(cpt2, EssenceSymbol):
            es_cpt = cpt2
            found_es_in_cp = 't2'
            non_es_from_cp = cpt1
        if found_es_in_cp:
            es_into_cp = INITIALIZERS.product(es_cpt, *es_scalar_factors)
            new_es_in_cp = essence_symbol_for(es_into_cp, esym_like=es_cpt)
            if found_es_in_cp == 't1':
                new_cp = cp._new(new_es_in_cp, non_es_from_cp)
            else:  # found_es_in_cp == 't2'
                new_cp = cp._new(non_es_from_cp, new_es_in_cp)
            return self._new(*non_cps, new_cp)
    # E1 * (x dot E2) --> x dot E3;  E1 * (E2 dot x) --> E3 dot x.
    dps, non_dps = dichotomize(non_es_factors, lambda s: isinstance(s, DotProduct))
    for dp in dps:
        dpt1, dpt2 = dp
        found_es_in_dp = False
        if isinstance(dpt1, EssenceSymbol):
            es_dpt = dpt1
            found_es_in_dp = 't1'
            non_es_from_dp = dpt2
        elif isinstance(dpt2, EssenceSymbol):
            es_dpt = dpt2
            found_es_in_dp = 't2'
            non_es_from_dp = dpt1
        if found_es_in_dp:
            es_into_dp = INITIALIZERS.product(es_dpt, *es_scalar_factors)
            new_es_in_dp = essence_symbol_for(es_into_dp, esym_like=es_dpt)
            if found_es_in_dp == 't1':
                new_dp = dp._new(new_es_in_dp, non_es_from_dp)
            else:  # found_es_in_cp == 't2'
                new_dp = dp._new(non_es_from_dp, new_es_in_dp)
            return self._new(*non_dps, new_dp, *es_vector_factors)
    # couldn't combine EssenceSymbols into DotProducts or CrossProducts. Just return result.
    return result
