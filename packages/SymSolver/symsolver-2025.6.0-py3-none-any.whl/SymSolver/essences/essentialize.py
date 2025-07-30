"""
File Purpose: essentialize
essentialize(self, target) gives an object with the same structure as self,
target kept explicit, but other things replaced by symbols.

E.g. (7 * y * x + x**2 * z + 8 + c).essentialize(x) -->
    Essence(a1 * x + a2 * x**2 + a3, ((a1, 7 * y), (a2, z), (a3, 8 + c)))
"""
import functools

from .essence_symbols import (
    EssenceSymbol,
    essence_symbol_for,
)
from ..attributors import attributor
from ..abstracts import (
    SubbableObject, is_subbable,
    contains_deep,
    IterableSymbolicObject, AssociativeOperation, CommutativeOperation,
    OperationContainer,
)
from ..basics import (
    Sum, Product,
)
from ..errors import (
    EssencePatternError,
    InputMissingError, InputConflictError,
)
from ..vectors import (
    is_vector, BinaryVectorProduct,
)
from ..tools import (
    equals,
    group_by,
    Binding, format_docstring,
)
binding = Binding(locals())

from ..defaults import DEFAULTS


''' --------------------- Convenient Methods --------------------- '''

_essentialize_paramdocs = \
    '''target: None or other object. (must provide target or targets, but not both.)
        if not None, use targets = [target]
    targets: None or iterable. (must provide target or targets, but not both.)
        essentialize with respect to these objects.
        Content in self not containing any of these targets will be replaced by EssenceSymbol object(s).
        Must provide at least 1 target, otherwise raises InputMissingError.
    s: string or None
        string to use as the base for all created EssenceSymbol objects.
        if None, use DEFAULTS.ESSENCES_SYMBOL_STR.
        The EssenceSymbol objects will look like s_0, s_1, s_2, ....
    combine: bool, default True
        whether to potentially apply 'combine_essence_symbols' simplification.
        For "full" essentialize, need to use combine=True.
        Otherwise might end up with something like E1 + E2 * (E3 + x).'''

@attributor
@format_docstring(paramdocs=_essentialize_paramdocs)
def essentialize(obj, target=None, *, targets=None, s=None, combine=True, **kw):
    '''return obj, essentialized with respect to target(s), and simplified by combining essence symbols.
    result = obj.essentialize(...) if available,
        and return result.apply('combine_essence_symbols') if possible, else result.
    else (obj.essentialize not available) returns obj if any target == obj,
    else returns essence_symbol_for(obj, s=s, targets=targets, **kw)

    Note: objects with obj.essentialize probably don't apply('combine_essence_symbols') automatically.
    
    {paramdocs}
    additional kwargs are passed to new_essence_symbol.
    '''
    try:
        obj_essentialize = obj.essentialize
    except AttributeError:
        pass  # handled after the 'else' block.
    else:
        return obj_essentialize(target=target, targets=targets, s=s, combine=combine, **kw)
    # << obj.essentialize not available.
    if any(equals(obj, target) for target in targets):
        return obj
    else:
        return essence_symbol_for(obj, s=s, targets=targets, **kw)

@attributor
def restore_from_essentialized(obj, target=None, *, targets=None, **kw):
    '''returns result of replacing all EssenceSymbols in obj with their original values.
    return obj.restore_from_essentialized(**kw) if available,
    else returns obj.
    '''
    try:
        obj_restore_from_essentialized = obj.restore_from_essentialized
    except AttributeError:
        return obj
    else:
        return obj_restore_from_essentialized(target=target, targets=targets, **kw)


''' --------------------- Essentialize --------------------- '''

def _essentializer_base(f):
    '''returns a function g(self, target=None, *, targets=None, s=None, **kw) which does some checks then f.
    In particular, this function does:
        - targets = _targets_from_kw(target=target, targets=targets)
        - if len(targets) == 0, raise InputMissingError.
        - if any(equals(self, target) for target in targets), return self.
        - otherwise, return f(self, targets=targets, s=s, **kw)
    Also, formats docstring using paramdocs=_essentialize_paramdocs.
    '''
    @format_docstring(paramdocs=_essentialize_paramdocs)
    @functools.wraps(f)
    def _essentialize_wrapper(self, target=None, *, targets=None, s=None, **kw):
        '''wraps f. See _essentializer for details.
        Note: functools.wraps replaces this docstring with docstring of f.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        targets = _targets_from_kw(target=target, targets=targets)
        if len(targets) == 0:
            raise InputMissingError(f'Must provide at least one target during {f.__name__}()')
        elif any(equals(self, target) for target in targets):
            return self
        else:
            return f(self, targets=targets, s=s, **kw)
    return _essentialize_wrapper

def _targets_from_kw(*, target=None, targets=None):
    '''returns targets. If target provided, return [target] instead.
    target OR targets can be provided, but not both.
    '''
    if target is None:
        return targets
    else:
        if targets is None:
            return [target]
        else:
            raise InputConflictError(f'Provide target or targets but not both! Got target={target}, targets={targets}.')

with binding.to(SubbableObject):
    @binding
    @_essentializer_base   # << includes: put targets=[target] if target provided instead of targets
    def essentialize(self, target=None, *, targets=None, s=None, combine=True, **kw):
        '''return self, essentialized with respect to targets.

        {paramdocs}
        '''
        return essence_symbol_for(self, s=s, targets=targets, **kw)

with binding.to(IterableSymbolicObject):
    @binding
    @_essentializer_base   # << includes: put targets=[target] if target provided instead of targets
    def essentialize(self, target=None, *, targets=None, s=None, combine=True, **kw):
        '''return self, essentialized with respect to targets.

        {paramdocs}
        '''
        if any(self.contains_deep(target) for target in targets):
            essentialized_terms = tuple(essentialize(term, targets=targets, s=s, combine=combine, **kw) for term in self)
            return self._new(*essentialized_terms)
        return essence_symbol_for(self, s=s, targets=targets, **kw)

with binding.to(AssociativeOperation):
    @binding
    @_essentializer_base   # << includes: put targets=[target] if target provided instead of targets
    def essentialize(self, target=None, *, targets=None, s=None, combine=True, **kw):
        '''return self, essentialized with respect to targets.

        {paramdocs}
        '''
        terms = list(self)
        grouper = lambda term: any(contains_deep(term, target) for target in targets)
        grouped = group_by(terms, grouper)  # list of (list of terms, contains_deep(term, target)) tuples
        if (len(grouped) == 0) or ((len(grouped) == 1) and not grouped[0][1]):  # no terms containing target.
            return essence_symbol_for(self, s=s, targets=targets, **kw)
        if isinstance(self, CommutativeOperation):
            # for commutative self, we are free to rearrange the terms however we please.
            # so, rewrite the groups into only 2 groups, one with all the terms containing target.
            terms_with_target = [t for (tlist, c) in grouped if c for t in tlist]
            terms_without_target = [t for (tlist, c) in grouped if not c for t in tlist]
            # put in a pretty order (just aesthetic; order doesn't matter mathematically since it's commutative.)
            if grouped[0][1]:  # first term in self contains target:
                grouped = [(terms_with_target, True), (terms_without_target, False)]
            else:  # first term in self doesn't contain target:
                grouped = [(terms_without_target, False), (terms_with_target, True)]
        result = []
        for tlist, contains_target in grouped:
            if len(tlist) == 0:
                continue   # skip this tlist if there are no terms.
            if contains_target:
                result += [essentialize(term, targets=targets, s=s, combine=combine, **kw) for term in tlist]
            else:
                selftype_from_terms_in_tlist = self._new(*tlist)
                result.append(essence_symbol_for(selftype_from_terms_in_tlist, s=s, targets=targets, **kw))
        return self._new(*result)

with binding.to(Sum):
    @binding
    @format_docstring(paramdocs=_essentialize_paramdocs)  # << not _essentializer_base; func calls essentialize().
    def essentialize(self, target=None, *, targets=None, s=None, combine=True, **kw):
        '''return self, essentialized with respect to targets.

        Combines essence Symbols if appropriate, e.g. E1 x + E2 x --> E3 x

        {paramdocs}
        '''
        targets = _targets_from_kw(target=target, targets=targets)
        result = super(Sum, self).essentialize(targets=targets, s=s, combine=combine, **kw)
        if result is self:
            return result
        if combine and isinstance(result, type(self)):
            return result.apply('combine_essence_symbols', targets=targets)
        else:
            return result

with binding.to(Product):
    @binding
    @format_docstring(paramdocs=_essentialize_paramdocs)  # << not _essentializer_base; func calls essentialize().
    def essentialize(self, target=None, *, targets=None, s=None, combine=True, **kw):
        '''return self, essentialized with respect to targets.

        Combines essence Symbols if appropriate, e.g. E1 * E2 --> E3

        {paramdocs}
        '''
        targets = _targets_from_kw(target=target, targets=targets)
        result = super(Product, self).essentialize(targets=targets, s=s, **kw)
        if result is self:
            return result
        if combine and isinstance(result, type(self)):
            return result.apply('combine_essence_symbols', targets=targets)
        return result

with binding.to(BinaryVectorProduct):
    @binding
    @format_docstring(paramdocs=_essentialize_paramdocs)  # << not _essentializer_base; func calls essentialize().
    def essentialize(self, target=None, *, targets=None, s=None, combine=True, **kw):
        '''return self, essentialized with respect to targets.

        Extracts scalars first.

        {paramdocs}
        '''
        targets = _targets_from_kw(target=target, targets=targets)
        result = self._extract_scalars(**kw)
        if isinstance(result, BinaryVectorProduct):
            ess_result = super(BinaryVectorProduct, result).essentialize(targets=targets, s=s, combine=combine, **kw)
        else:
            ess_result = essentialize(result, targets=targets, s=s, combine=combine, **kw)
        if isinstance(ess_result, Product):
            return ess_result.apply('combine_essence_symbols', targets=targets, **kw)
        else:
            return ess_result

with binding.to(OperationContainer):
    @binding
    @format_docstring(paramdocs=_essentialize_paramdocs)  # << not _essentializer_base; func calls essentialize().
    def essentialize(self, target=None, *, targets=None, s=None, combine=True, **kw):
        '''return self, with each operation essentialized with respect to target.

        {paramdocs}
        '''
        return self.op(lambda y: essentialize(y, target=target, targets=targets, combine=combine, s=s, **kw))


''' --------------------- Restore from essentialized --------------------- '''

with binding.to(EssenceSymbol):
    @binding
    def restore_from_essentialized(self, target=None, *, targets=None, **kw):
        '''returns self.replaced if appropriate & possible.

        targetting... can provide target or targets, but not both.
            target: None or object
                the one and only target in targets.
            targets: list of objects
                the targets to compare with self.targets.
            if provided, check if targets and self.targets represent the same set of targets
            If they match, return self.replaced.
            Otherwise, return self, unchanged.

        Also calls self.replaced.restore_from_essentialized(**kw) if possible,
        in case self.replaced contains EssenceSymbols as well.

        If would return self.replaced but it is None, raise EssencePatternError instead.
        '''
        targets = _targets_from_kw(target=target, targets=targets)
        if targets is not None:
            if not equals(targets, self.targets):
                return self
        if self.replaced is None:
            raise EssencePatternError(f'Cannot restore from essentialized; self.replaced is None. self={self}')
        result = self.replaced
        if is_subbable(result):
            return result.restore_from_essentialized(targets=targets, **kw)
        else:
            return result

with binding.to(SubbableObject):
    @binding
    def restore_from_essentialized(self, target=None, *, targets=None, **kw):
        '''restores original object from essentialized object.
        
        target & targets:
            can provide one but not both.
            If provided, only replace EssenceSymbols that match these targets.
            Otherwise, replace all EssenceSymbols.

        kwargs go to self._iter_substitution_terms.
        '''
        if not is_subbable(self):
            return self
        # loop through subbable terms in self, calling term.restored_from_essentialized(...).
        def restore_from_essentialized_rule(term):
            return term.restore_from_essentialized(target=target, targets=targets, **kw)
        return self._substitution_loop(restore_from_essentialized_rule, **kw)
