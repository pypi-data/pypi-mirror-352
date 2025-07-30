"""
File Purpose: Symbol
See also: SYMBOLS, symbol

[TODO]:
    - test efficiency of using SYMBOLS to help ensure symbol equality
      is determined via object equality, i.e. via 'is', by ensuring that
      when creating a symbol, if any previously-made symbol equals the new one,
      the previous one will be returned instead of the new one.
        - (first adjust __eq__ so that it only checks equality via 'is',
           and use the current __eq__ algorithm to check equality during _symbol_create.)
    - use weakrefs in SYMBOLS -- SYMBOLS should not keep any Symbol from being deleted.
    - hashing when available (i.e. when s is hashable)
    - docstrings including info from all symbols modules
"""
from ..abstracts import (
    AbstractOperation, SubbableObject,
    is_subbable,
    get_symbols,
    is_constant,
)
from ..initializers import (
    initializer_for,
    INITIALIZERS,
    initializer,
)
from ..tools import (
    _repr,
    equals,
    caching_attr_simple,
    StoredInstances,
    Binding, format_docstring,
)
from ..defaults import DEFAULTS

binding = Binding(locals())


''' --------------------- Symbol class --------------------- '''

class Symbol(AbstractOperation, SubbableObject):
    '''treated as a single variable by SymSolver.
    E.g. Symbol('x'), Symbol('n', subscipts=['s'])

    not intended for direct instantiation;
    users should use symbol() or symbols() to create new Symbol object or objects.
    for help on parameters, look to those methods, or to self.__init__.

    Symbol objects are intended to be immutable.
    To make a new Symbol similar to self with some attributes changed, see self._new.

    symbol==x iff x is a Symbol with s and subscripts matching symbol.

    Notes on Immutability:
        s, subscripts, and constant are read-only properties to
        discourage accidentally writing their values.
    '''
    # # # CREATION # # #
    def _init_args(self):
        '''returns args to go before entered args during self._new, for self.initializer.
        self._new(*args, **kw) will lead to self.initializer(*self._init_args(), *args, **kw).
        '''
        return (self.s,)

    def as_constant(self):
        '''returns copy of self with constant=True.'''
        return self._new(constant=True)

    def with_constant_unassumed(self):
        '''returns a copy of self with constant=None'''
        return self._new(constant=None)

    # make s, subscripts, and constant be read-only properties to encourage immutability.
    s = property(lambda self: self._s, doc='''what the Symbol represents''')
    subscripts = property(lambda self: self._subscripts, doc='''subscripts associated with the Symbol''')
    constant = property(lambda self: self._constant, doc='''whether to treate the Symbol like a constant''')

    # # # DISPLAY # # #
    @staticmethod
    def _subscripts_to_str(subscripts):
        '''return string for writing subscipts of Symbol.'''
        subs_str = ', '.join([str(s) for s in subscripts])
        if len(subs_str) > 0:
            subs_str = '_{' + subs_str + '}'
        return subs_str

    def _subs_str(self):
        '''return string for self.subscripts.'''
        subscripts = self.subscripts
        if DEFAULTS.DEBUG_CONSTANTS and (self.constant is not None):
            cdebug = '(C)' if self.constant else '(V)'
            subscripts = (*subscripts, cdebug)
        return self._subscripts_to_str(subscripts)

    def __str__(self):
        return str(self.s) + self._subs_str()

    # # # EQUALITY # # #
    # two Symbols are only equal if they match in these attrs:
    _EQ_TEST_ATTRS = ['s', 'constant', 'subscripts']

    def __eq__(self, b):
        '''return self == b'''
        if b is self:
            return True
        if not isinstance(b, type(self)):
            return False
        for attr in self._EQ_TEST_ATTRS:
            if not equals(getattr(self, attr), getattr(b, attr)):
                return False
        return True

    @caching_attr_simple
    def __hash__(self):
        return hash((type(self), *(getattr(self, attr) for attr in self._EQ_TEST_ATTRS)))

    def _equals0(self):
        '''return self == 0  (i.e., always return False).'''
        return False

    def equals_except(self, b, *skip_attrs):
        '''return self == b except SKIP the attrs provided during the equality test.
        See self._EQ_TEST_ATTRS for skip_attrs options.
        '''
        if len(skip_attrs) == 0:
            return self.__eq__(b)
        if b is self:
            return True
        if not isinstance(b, type(self)):
            return False
        for attr in (set(self._EQ_TEST_ATTRS) - set(skip_attrs)):
            if not equals(getattr(self, attr), getattr(b, attr)):
                return False
        return True

    # # # INSPECTION # # #
    def is_constant(self):
        '''returns whether self is a constant.'''
        return self.constant

    def get_symbols(self):
        '''returns symbols in self. I.e.: (self,)'''
        return (self,)

    def get_symbols_in(self, func):
        '''return symbols in self where func holds. I.e.: (self,) if func(self) else ()'''
        return (self,) if func(self) else ()

    _is_symbol = True
    _is_basic_symbol = True

    # # # SUBSTITUTIONS # # #
    def is_interface_subbable(self):
        '''returns True, because self should appear as an option in a SubstitutionInterface.'''
        return True


_init_paramdocs = \
    '''ARGUMENTS:
    s: object
        instance of Symbol is a "Symbol of s". Will be displayed using str(s).
        Most users will be satisfied to use string s, e.g. s='x' or 'y'.
    subscripts: iterable, default ()
        subscripts associated with self. Order matters.
        input will be converted to tuple to encourage immutability.

    KEYWORD-ONLY ARGUMENTS:
    constant: bool or None, default None
        whether to treat this Symbol like it represents a constant.
        True --> definitely a constant.
        False --> definitely not a constant.
        None --> unsure.'''

with binding.to(Symbol, keep_local=True):
    # define some things outside of the Symbol class, but keep them in the local namespace.
    # this is so that later packages can call these original functions.
    # e.g. vectors will add kwargs to Symbol's __init__, so it needs to reference the __init__ defined here,
    #     and it can't do that from the Symbol class (since it will be overwriting Symbol's __init__).
    #     So instead, vectors can access this __init__ via SymSolver.basics.symbols.__init__.
    @binding
    @format_docstring(paramdocs=_init_paramdocs)
    def __init__(self, s, subscripts=(), *, constant=None, **kw__None):
        '''initialize Symbol self.

        {paramdocs}
        '''
        self._s = s
        self._subscripts = tuple(subscripts)
        self._constant = constant
        super(Symbol, self).__init__()

    @binding
    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another Symbol like self.'''
        kw = super(Symbol, self)._init_properties()
        kw['subscripts'] = self.subscripts
        kw['constant'] = self.constant
        return kw

    @binding
    def _repr_contents(self, **kw):
        '''returns contents to put inside 'Symbol()' in repr for self.'''
        contents = [_repr(self.s, **kw)]
        if len(self.subscripts) > 0:
            contents.append(f'subscripts={_repr(self.subscripts, **kw)}')
        if self.constant:
            contents.append(f'constant={self.constant}')
        return contents

    _kwargs_like_docs = '''constant = is_constant(obj)'''

    @binding.bind(methodtype=staticmethod)
    @format_docstring(_kwargs_like_docs=_kwargs_like_docs)
    def kwargs_like(obj):
        '''returns dict of kwargs for creating Symbol like obj.
        Those kwargs will be:
            {_kwargs_like_docs}
        '''
        return dict(constant=is_constant(obj))


''' --------------------- Create a Symbol object --------------------- '''
# SYMBOLS stores all the Symbol objects ever created.
# the idea is that when about to creating a new Symbol which equals one in here,
#   instead return the already-existing Symbol from in here.

SYMBOLS = StoredInstances(Symbol)

@initializer_for(Symbol)
@format_docstring(paramdocs=_init_paramdocs)
def symbol(s, subscripts=(), *, constant=None, **kw):
    '''create a new Symbol using the parameters provided.
    Stores created Symbol in SYMBOLS, and ensure no duplicates:
        if the new Symbol equals any previously-created symbol,
        return the previously-created symbol instead of making a new one.

    {paramdocs}
    [TODO] update this docstring to include all the kwarg options.
    '''
    return _symbol_create(s, subscripts=subscripts, constant=constant, **kw)

def _symbol_create(s, *args, **kw):
    '''create new symbol but first ensure no duplicates;
    if duplicate, return previously-created equal symbol.
    Generic args & kwargs --> can be used by subclasses with arbitrary __init__.
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    return SYMBOLS.get_new_or_existing_instance(Symbol, s, *args, **kw)

def symbols(strings, *args__symbol, **kw__symbol):
    '''create multiple Symbol objects using the provided args and kwargs.

    strings: list of strings, or a single string.
        if a single string, first split into a list of strings via .split()
        create one Symbol for each string here.
        E.g. symbols(('x', 'y', 'z')) <--> symbol('x'), symbol('y'), symbol('z')
        E.g. symbols('a c', constant=True) <--> symbol('a', constant=True), symbol('c', constant=True)

    implementation detail note:
        by using INITIALIZERS.symbol, we ensure that symbols() will remain appropriate
        even if a later module defines a new function as the initializer for Symbol.
    '''
    if isinstance(strings, str):
        strings = strings.split()
    return tuple(INITIALIZERS.symbol(s, *args__symbol, **kw__symbol) for s in strings)

def _symbol_with_int_subscript(s, subscripts=(), *, constant=None, n=0, **kw):
    '''create symbol with subscripts = (*subscripts, n).
    always makes a new symbol, doesn't check existing symbols.
    For internal use only.
    '''
    return Symbol(s, subscripts=(*subscripts, n), constant=constant, **kw)

@format_docstring(paramdocs=_init_paramdocs)
def new_unique_symbol(s=None, subscripts=(), *, constant=None, n=0, **kw):
    '''create a new unique Symbol using the parameters provided.
    
    if s is not provided (i.e. s is None), use s=DEFAULTS.NEW_SYMBOL_STR.

    {paramdocs}
    n: int, default 0
        append this int to the end of self.subscripts.
        if the result is an already-existing symbol (in SYMBOLS), try again but using n=n+1.

    [TODO] update this docstring to include all the kwarg options.
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    if s is None: s = DEFAULTS.NEW_SYMBOL_STR
    return SYMBOLS.get_new_instance(_symbol_with_int_subscript, s, kw_increment='n', n=n, **kw)

@format_docstring(paramdocs=_init_paramdocs)
def new_symbol_like(obj, s=None, subscripts=(), *, n=0, **kw):
    '''creates a new unique Symbol using obj to determine default kwargs.
    E.g. if is_constant(obj), then constant=True by default.
    defaults can be overridden with the appropriate kwargs in kw.

    if s is not provided (i.e. s is None), use s=DEFAULTS.NEW_SYMBOL_STR.

    {paramdocs}
    n: int, default 0
        append this int to the end of self.subscripts.
        if the result is an already-existing symbol (in SYMBOLS), try again but using n=n+1.

    [TODO] update this docstring to include all the kwarg options.
    '''
    if s is None: s = DEFAULTS.NEW_SYMBOL_STR
    kw_use = Symbol.kwargs_like(obj)
    kw_use.update(kw)
    return new_unique_symbol(s, subscripts=subscripts, n=n, **kw_use)


def clear_s(s=None, *, force=False):
    '''clear Symbols in SYMBOLS with s=s. if s is None, use s=DEFAULTS.NEW_SYMBOL_STR.'''
    if s is None: s = DEFAULTS.NEW_SYMBOL_STR
    return SYMBOLS.clear_if(lambda symbol_: symbol_.s == s, force=force)
SYMBOLS.clear_s = clear_s


''' --------------------- assume_constants --------------------- '''

with binding.to(SubbableObject):
    @binding
    def assume_constants(self, *treat_as_constants, **kw):
        '''replace all x in treat_as_constants with x.as_constant(), throughout self.
        Does not look deeper inside any of the x in treat_as_constants.
        If treat_as_constants is empty, treat ALL SYMBOLS in self as constants.
        kw go to self._substitution_loop.
        '''
        if not is_subbable(self):
            return self
        # this function's subtitution rule for self:
        if len(treat_as_constants) == 0:
            treat_as_constants = tuple(s for s in get_symbols(self) if not s.is_constant())
        if self in treat_as_constants:
            return self.as_constant()
        # loop through terms in self, if applicable.
        def assume_constants_rule(term):
            return term.assume_constants(*treat_as_constants, **kw)
        return self._substitution_loop(assume_constants_rule, **kw)

    @binding
    def unassume_constants(self, *constants_to_unassume, **kw):
        '''replace all x in constants_to_unassume with x.with_constant_unassumed(), throughout self.
        similar functionality to self.assume_constants, but constant=None instead of constant=True.
        '''
        if not is_subbable(self):
            return self
        # this function's subtitution rule for self:
        if len(constants_to_unassume) == 0:
            constants_to_unassume = tuple(s for s in get_symbols(self) if s.is_constant() is not None)
        if self in constants_to_unassume:
            return self.with_constant_unassumed()
        # loop through terms in self, if applicable.
        def unassume_constants_rule(term):
            return term.unassume_constants(*constants_to_unassume, **kw)
        return self._substitution_loop(unassume_constants_rule, **kw)
