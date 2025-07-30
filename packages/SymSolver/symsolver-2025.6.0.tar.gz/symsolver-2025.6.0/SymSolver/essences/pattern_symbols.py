"""
File Purpose: PatternSymbol
EssenceSymbol with more convenient methods for pattern matching.

[TODO] remove "pattern matching" from EssenceSymbol (see essence_matches.py).
[TODO] add convenient pattern matching functions (e.g. internally essentialize(obj))
"""

from .essence_symbols import EssenceSymbol

from ..attributors import attributor
from ..abstracts import SubbableObject, is_subbable
from ..errors import InputError, InputMissingError
from ..initializers import initializer_for
from ..tools import (
    equals,
    appended_unique,
    Binding,
    StoredInstances, format_docstring, caching_attr_simple_if,
)
binding = Binding(locals())

from ..defaults import DEFAULTS, OnOffSwitch


''' --------------------- Convenience Methods --------------------- '''

@attributor
def subs_pattern_matched(obj, **kw):
    '''returns obj with PatternSymbols replaced by their _pattern_matched values.
    returns obj.subs_pattern_matched(**kw) if available, else obj.
    '''
    try:
        obj_subs_pattern_matched = obj.subs_pattern_matched
    except AttributeError:
        return obj
    else:
        return obj_subs_pattern_matched(**kw)


''' --------------------- PatternSymbol --------------------- '''

@format_docstring(pattern_match_any=str(DEFAULTS.PATTERN_MATCH_ANY))
class PatternSymbol(EssenceSymbol):
    '''EssenceSymbol with more convenient methods for pattern matching.

    by default, ignore _EQ_TEST_ATTRS which appear in DEFAULTS.PATTERN_MATCH_ANY,
        which, when this class was defined, equaled: {pattern_match_any}.

    match_any: None or list of strings, default []
        list of which additional _EQ_TEST_ATTRS to ignore during __eq__.
        (remove these strings from _EQ_TEST_ATTRS during __eq__.)
        None --> equivalent to entering ALL possible _EQ_TEST_ATTRS.
            i.e. in this case, only match attrs in must_match,
            while ignoring match_any and DEFAULTS.PATTERN_MATCH_ANY.
    must_match: list of strings, default []
        list of which _EQ_TEST_ATTRS in fact must be kept during __eq__.
        (add these strings to _EQ_TEST_ATTRS during __eq__,
        after removing the strings indicated by match_any and DEFAULTS.PATTERN_MATCH_ANY.)

    options for strings in match_any and must_match include:
        's': the Symbol's string
        'subscripts': the subscripts for this Symbol
        'constant': whether the Symbol represents a constant
        'vector': whether the Symbol represents a vector
        'hat': whether the Symbol represents a unit vector
        'order': the Symbol's order; see linear_theory for more details.
        'targets': the EssenceSymbol's targets, from essentialize()
        'id_': the EssenceSymbol's id.
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, s=None, subscripts=(), *, match_any=[], must_match=[], **kw):
        self.match_any = match_any
        self.must_match = must_match
        if s is None:
            s = DEFAULTS.PATTERN_SYMBOL_STR
        if s is None:  # << if STILL None, that's an issue.
            raise InputMissingError("'s' not provided, and default (DEFAULTS.PATTERN_SYMBOL_STR) is None.")
        super().__init__(s, subscripts=subscripts, **kw)

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another PatternSymbol like self.'''
        kw = super()._init_properties()
        kw['match_any'] = self.match_any
        kw['must_match'] = self.must_match
        return kw

    # # # DISPLAY # # #
    def _repr_contents(self, **kw):
        '''returns contents to put inside 'PatternSymbol()' in repr for self.'''
        contents = super()._repr_contents(**kw)
        if (self.match_any is None) or len(self.match_any) > 0:
            contents.append(f'match_any={self.match_any}')
        if len(self.must_match) > 0:
            contents.append(f'must_match={self.must_match}')
        return contents

    # # # EQUALITY # # #
    # if _EQ_PATTERN_MODE, __eq__ matches in the sense of patterns
    #    e.g. can match to an EssenceSymbol, and accounts for self.match_any and self.must_match.
    # otherwise, __eq__ matches in the sense of strict equality,
    #    i.e. "does this PatternSymbol behave in exactly the same way as the other PatternSymbol?"
    _EQ_PATTERN_MODE = OnOffSwitch(True, 'Whether PatternSymbol.__eq__ does essence_pattern_matching.')

    @property
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def _EQ_PATTERN_MODE_TEST_ATTRS(self):
        '''_EQ_TEST_ATTRS to match when _EQ_PATTERN_MODE is enabled.'''
        if self.match_any is None:
            return self.must_match
        else:
            result = set(super()._EQ_TEST_ATTRS)
            result = result - set(DEFAULTS.PATTERN_MATCH_ANY)
            result = result - set(self.match_any)
            result = result.union(self.must_match)
            return result

    @property
    def _EQ_TEST_ATTRS(self):
        '''__eq__ only if matching in these attrs.'''
        if self._EQ_PATTERN_MODE:
            return self._EQ_PATTERN_MODE_TEST_ATTRS
        else:  # strict equality for comparing PatternSymbol behavior.
            return super()._EQ_TEST_ATTRS + ['match_any', 'must_match']

    def __eq__(self, b):
        '''if self._EQ_PATTERN_MODE, return self.essence_pattern_matches(b); else return super().__eq__(b)'''
        if self._EQ_PATTERN_MODE:
            result = self.essence_pattern_matches(b)
            if result:
                self._pattern_matched = b
                if isinstance(b, PatternSymbol):
                    b._pattern_matched = self
            return result
        else:
            return super(PatternSymbol, self).__eq__(b)

    __hash__ = None  # no hashing since PatternSymbols might match other things.

    def essence_pattern_matches(self, b):
        '''return whether self has the same essence pattern as b.'''
        if b is self:
            return True
        if not isinstance(b, EssenceSymbol):  # << can only match any EssenceSymbol (or subclass) instance.
            return False
        for attr in self._EQ_TEST_ATTRS:
            if not equals(getattr(self, attr), getattr(b, attr)):
                return False
        return True

    # # # INSPECTION # # #
    def is_vector(self):
        '''returns self.vector, or None if self.__eq__ doesn't currently care about matching Symbol.vector.'''
        if 'vector' in self._EQ_TEST_ATTRS:
            return super().is_vector()
        else:
            return None


''' --------------------- Create an PatternSymbol object --------------------- '''
# PATTERN_SYMBOLS stores all the PatternSymbol objects ever created.
# the idea is that when about to creating a new PatternSymbol which equals one in here,
#   instead return the already-existing PatternSymbol from in here.

PATTERN_SYMBOLS = StoredInstances(PatternSymbol)

@initializer_for(PatternSymbol)
def pattern_symbol(s=None, subscripts=(), *, match_any=[], must_match=[], **kw):
    '''return an PatternSymbol using the parameters provided.

    If the new PatternSymbol equals any existing one, return the existing one instead.
    If created a new symbol, stores it in PATTERN_SYMBOLS.
    '''
    return _pattern_symbol_create(s, subscripts, match_any=match_any, must_match=must_match, **kw)

def _pattern_symbol_create(s=None, *args, **kw):
    '''create new symbol but first ensure no duplicates;
    if duplicate, return previously-created equal symbol.
    Generic args & kwargs --> can be used by subclasses with arbitrary __init__.
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    with PatternSymbol._EQ_PATTERN_MODE.disabled():
        result = PATTERN_SYMBOLS.get_new_or_existing_instance(PatternSymbol, s, *args, **kw)
    return result

def new_pattern_symbol(s=None, subscripts=(), *, match_any=[], must_match=[], id_=0, **kw):
    '''create a new PatternSymbol using the parameters provided.
    Stores created PatternSymbol in PATTERN_SYMBOLS.
    id_ might be incremented any number of times, until the created essence symbol is new.
        the value of id_ here just indicates the starting value for that incrementing.
    '''
    with PatternSymbol._EQ_PATTERN_MODE.disabled():
        result = PATTERN_SYMBOLS.get_new_instance(PatternSymbol, s, subscripts,
                match_any=match_any, must_match=must_match, kw_increment='id_', id_=id_, **kw)
    return result

def new_pattern_symbol_like(x, s=None, *, match_any=[], must_match=[], id_=0, **kw):
    '''create a new PatternSymbol like x, using the parameters provided.
    uses PatternSymbol.with_properties_like(x, **kw) to create the new symbol.
    '''
    with PatternSymbol._EQ_PATTERN_MODE.disabled():
        result = PATTERN_SYMBOLS.get_new_instance(PatternSymbol.with_properties_like, x, s=s,
                match_any=match_any, must_match=must_match, kw_increment='id_', id_=id_, **kw)
    return result

def new_pattern_symbol_matching_only(match_only=[], s=None, *, id_=0, **kw):
    '''create a new PatternSymbol which tests for matches only in the attributes indicated by match_only.
    For a fully list of options, check PatternSymbol._CLS_EQ_TEST_ATTRS().
    Additional kwargs go to PatternSymbol.__init__.
    '''
    if isinstance(match_only, str):
        errmsg = (f'match_only should be an iterable of strings, but not a string itself. '
                  f'(Got match_only={repr(match_only)}.) '
                  f'Options include {PatternSymbol._CLS_EQ_TEST_ATTRS()}')
        raise InputError(errmsg)
    with PatternSymbol._EQ_PATTERN_MODE.disabled():
        result = PATTERN_SYMBOLS.get_new_instance(PatternSymbol, s,
                match_any=None, must_match=match_only, kw_increment='id_', id_=id_, **kw)
    return result


''' --------------------- Pattern Matches --------------------- '''

def essence_pattern_matches(obj, b):
    '''return whether obj == b, with PatternSymbol pattern matching enabled.
    Also saves essence pattern matches in '_pattern_matched' of PatternSymbols.
    Examples (with EssenceSymbols A1 and A2; PatternSymbols C1 and C2):
        obj = C1 * x; b = A1
        --> True, also sets:
            C1._pattern_matched = A1
        obj = A1 * x + A2; b = C1 * x + C2
        --> True, also sets:
            C1._pattern_matched = A1
            C2._pattern_matched = A2
        obj = A1 * x + A2; b = C1 * x
        --> False, also might set _pattern_matched for C1, but not guaranteed to do so.
        obj = A1 * x + A2; b = x + C2
        --> False, also might set _essence_matched for C2, but not guaranteed to do so.
    '''
    with PatternSymbol._EQ_PATTERN_MODE.enabled():
        return equals(obj, b)


''' --------------------- Sub from Pattern Matched --------------------- '''

with binding.to(PatternSymbol):
    @binding
    def subs_pattern_matched(self, **kw__None):
        '''returns self._pattern_matched if it exists, else self.'''
        try:
            return self._pattern_matched
        except AttributeError:
            return self

with binding.to(SubbableObject):
    @binding
    def subs_pattern_matched(self, **kw):
        '''returns self with PatternSymbols replaced by their _pattern_matched values.
        kwargs go to self._iter_substitution_terms.
        '''
        if not is_subbable(self):
            return self
        # loop through subbable terms in self, calling term.subs_pattern_matched(...).
        def subs_pattern_matched_rule(term):
            return term.subs_pattern_matched(**kw)
        return self._substitution_loop(subs_pattern_matched_rule, **kw)
