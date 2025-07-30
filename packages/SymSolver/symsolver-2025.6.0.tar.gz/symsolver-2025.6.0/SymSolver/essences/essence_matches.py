"""
File Purpose: whether objects match, in essence.
"""

from .essence_combine import get_first_essence_symbol
from .essence_symbols import EssenceSymbol
from .essentialize import essentialize

from ..basics import Symbol
from ..tools import (
    equals,
    caching_attr_simple,
    Binding,
)
from ..defaults import OnOffSwitch

binding = Binding(locals())


with binding.to(EssenceSymbol):
    # True --> __eq__ tests self.essence_matches(b); False --> it tests super().__eq__(b).
    EssenceSymbol._EQ_ESSENCE_MATCHING = OnOffSwitch(False,
            'Whether EssenceSymbol.__eq__ tests essence_matches. (False --> test Symbol.__eq__ instead.)')

    # if not _EQ_ESSENCE_MATCHING, ignore _EQ_ESSENCE_TRACKING.
    # True --> when self.__eq__(b), set self._essence_matched = b and b._essence_matched = self.
    # False (or not _EQ_ESSENCE_MATCHING) --> __eq__ doesn't touch '_essence_matched' from self or b.
    EssenceSymbol._EQ_ESSENCE_TRACKING = OnOffSwitch(False,
            'Whether EssenceSymbol.__eq__ tracks essence matches, via obj._essence_matched.')

    @binding
    def __eq__(self, b):
        '''if self._EQ_ESSENCE_MATCHING, return self.essence_matches(b); else return super().__eq__(b)'''
        if self._EQ_ESSENCE_MATCHING:
            result = self.essence_matches(b)
            if result and self._EQ_ESSENCE_TRACKING:
                self._essence_matched = b
                if isinstance(b, EssenceSymbol):
                    b._essence_matched = self
            return result
        else:
            return super(EssenceSymbol, self).__eq__(b)

    @binding
    @caching_attr_simple
    def __hash__(self):
        return hash((super(EssenceSymbol, self).__hash__(), self.targets))

    @binding
    def essence_matches(self, b):
        '''return whether self has the same essence as b.
        True iff all of these conditions are satisfied:
            - b is an EssenceSymbol
            - b.targets == self.targets
            - b == self, except possibly for id_.
        '''
        if b is self:
            return True
        if not isinstance(b, EssenceSymbol):
            return False
        for attr in Symbol._EQ_TEST_ATTRS:  # << note, Symbol._EQ_TEST_ATTRS, NOT self._EQ_TEST_ATTRS.
            if not equals(getattr(self, attr), getattr(b, attr)):
                return False
        if not equals(self.targets, b.targets):
            return False
        return True


def essence_matches(obj, b):
    '''return whether obj == b but allowing EssenceSymbols with matching essence to be treated as equal.'''
    with EssenceSymbol._EQ_ESSENCE_MATCHING.enabled():
        return equals(obj, b)

def matching_essence(obj, b, targets=[], **kw):
    '''returns whether essence_matches(essentialized(obj), essentialized(b)), using targets & kw.
    I.e. whether, obj and b have the same form with respect to targets.
    For example, 7 * y * z * x + 9 essentially matches 8 * x + y,
        since they both look like A0 * x + A1, for some A0 and A1 independent of x.
    However, note that x + 9 does not essentially match those, since it looks like x + A1;
        the structure is different since the x is not in a Product.

    [TODO] discard all EssenceSymbols created during this check, since they won't be used ever again.
    OR, return the essentialized obj and essentialized b.
    '''
    essentialized_obj = essentialize(obj, targets=targets, **kw)
    essentialized_b = essentialize(b, targets=targets, **kw)
    return essence_matches(essentialized_obj, essentialized_b)

def essence_match_and_track(obj, b):
    '''return whether essence_matches(obj, b); also save matches in '_essence_matched' of EssenceSymbols.
    Examples:
        obj = A1 * x + A2; b = A3 * x + A4
        --> True, also sets:
            A1._essence_matched = A3
            A3._essence_matched = A1
            A2._essence_matched = A4
            A4._essence_matched = A2
        obj = A1 * x + A2; b = A3 * x
        --> False, also might set _essence_matched for A1 and A3, but not guaranteed to do so.
        obj = A1 * x + A2; b = x + A4
        --> False, also might set _essence_matched for A2 and A4, but not guaranteed to do so.
    '''
    with EssenceSymbol._EQ_ESSENCE_TRACKING.enabled():
        return essence_matches(obj, b)
