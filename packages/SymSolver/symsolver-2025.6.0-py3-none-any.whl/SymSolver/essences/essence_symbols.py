"""
File Purpose: EssenceSymbol
essentialize(self, x) gives an object with the same structure as self,
x kept explicit, but other things replaced by symbols.

E.g. (7 * y * x + x**2 * z + 8 + c).essentialize(x) -->
    Essence(a1 * x + a2 * x**2 + a3, [(a1, 7 * y), (a2, z), (a3, 8 + c)])
"""
from ..abstracts import canonical_orderer
from ..basics import (
    Symbol, SYMBOLS,
)
from ..errors import InputMissingError
from ..initializers import initializer_for
from ..tools import (
    _repr,
    assert_values_provided,
    Set,
    Binding, StoredInstances,
)
from ..defaults import DEFAULTS

# just for EssenceSymbol.with_properties_like(); [TODO](maybe) encapsulate elsewhere.
from ..vectors import is_vector, is_basis_vector
from ..linear_theory import get_order


''' --------------------- EssenceSymbol --------------------- '''

class EssenceSymbol(Symbol):
    '''symbol to use during essentialize.
    Note: not intended for direct instantiation; use essence_symbol() instead.

    Replaces non-targetted values (e.g. not x, in essentialize(obj, x)).
    Remembers the replaced value, and the targetted value.
    Stored in a separate list from SYMBOLS to avoid confusion.

    targets: SymbolicObjects
        the target(s) of essentialize() that led to creation of this EssenceSymbol.
        non-optional for objects with type == EssenceSymbol. Optional for subclasses.
    id_: int (not optional, must be provided)
        The integer which identifies this EssenceSymbol,
        to ensure it is unique compared to other Symbols and EssenceSymbols.
        Will be shown as a subscript during str(self).
    replaced: None or object
        if provided, should tell the value which self replaced during essentialize().
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, s=None, subscripts=(), *, targets=None, id_=None, replaced=None, **kw):
        assert_values_provided(id_=id_)
        if type(self) == EssenceSymbol:
            assert_values_provided(targets=targets)
            targets = Set(targets)
        self.targets = targets
        self.replaced = replaced
        self.id_ = id_
        if s is None:
            s = DEFAULTS.ESSENCES_SYMBOL_STR
        if s is None:  # << if STILL None, that's an issue.
            raise InputMissingError("'s' not provided, and default (DEFAULTS.ESSENCES_SYMBOL_STR) is None.")
        super().__init__(s, subscripts=subscripts, **kw)

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another EssenceSymbol like self.'''
        kw = super()._init_properties()
        kw['targets'] = self.targets
        kw['id_'] = self.id_
        kw['replaced'] = self.replaced
        return kw

    @classmethod
    def with_properties_like(cls, x, s=None, keep_subscripts=False, **kw_init):
        '''return an EssenceSymbol with properties like x.
        E.g. if x is a vector, result will be a vector too.
        The properties are (property, func to check property)
            vector: is_vector
            hat: is_basis_vector
            order: get_order
        if keep_subscripts (default False), also include the (property, func to check property):
            subscripts: lambda obj: getattr(obj, 'subscripts', ())
        if any kwargs are provided in kw_init which conflict with the properties determined about x,
            uses kw_init instead. (e.g. if x is a vector but vector=False in kw_init, use vector=False.)
        [TODO] make a function which encapsulates the code for getting these properties.
        '''
        kw = dict()
        # order
        if 'order' not in kw_init:
            kw['order'] = get_order(x)
        # vector stuff
        if 'vector' in kw_init:
            making_vector = kw_init['vector']
        else:
            kw['vector'] = is_vector(x)
            making_vector = kw['vector']
        if 'hat' not in kw_init:
            if making_vector:
                kw['hat'] = is_basis_vector(x)
        # subscripts
        if keep_subscripts:
            if 'subscripts' not in kw_init:
                kw['subscripts'] = getattr(x, 'subscripts', ())
        return cls(s=s, **kw, **kw_init)

    # # # DISPLAY # # #
    def _subs_str(self):
        '''return string for writing subscripts (and id_) of self.'''
        return self._subscripts_to_str((*self.subscripts, self.id_))

    def _repr_contents(self, **kw):
        '''returns contents to put inside 'EssenceSymbol()' in repr for self.'''
        contents = super()._repr_contents()
        contents.append(f'id_={self.id_}')
        contents.append(f'targets={_repr(self.targets, **kw)}')
        return contents

    # # # EQUALITY # # #
    # attrs to add to Symbol._EQ_TEST_ATTRS to determine self._EQ_TEST_ATTRS
    _EQ_TEST_ATTRS_APPEND = ['id_', 'targets']

    @classmethod
    def _CLS_EQ_TEST_ATTRS(cls):
        '''returns list of all _EQ_TEST_ATTRS for cls.'''
        return Symbol._EQ_TEST_ATTRS + cls._EQ_TEST_ATTRS_APPEND

    @property
    def _EQ_TEST_ATTRS(self):
        '''two EssenceSymbols are only equal if they match in these attrs.
        Implementation note: implemented as property instead of as a list attached to class,
            in case the Symbol class's _EQ_TEST_ATTRS is updated after the EssenceSymbol class definition.
        '''
        return self._CLS_EQ_TEST_ATTRS()

    def _equals0(self):
        '''returns whether self.vector is None, since that corresponds to a Symbol with value 0.'''
        return self.vector is None

    # # # MISC # # #
    _DEFAULT_SUM_COLLECT_PRIORITY = None  # << never collect this during _sum_collect
    _is_basic_symbol = False  # << don't treat this as a Symbol for symbol_check in sub().


''' --------------------- Create an EssenceSymbol object --------------------- '''
# ESSENCE_SYMBOLS stores all the EssenceSymbol objects ever created.
# the idea is that when about to creating a new EssenceSymbol which equals one in here,
#   instead return the already-existing EssenceSymbol from in here.

ESSENCE_SYMBOLS = StoredInstances(EssenceSymbol, viewsort=canonical_orderer)

@initializer_for(EssenceSymbol)
def essence_symbol(s=None, subscripts=(), *, targets=None, replaced=None, id_=0, **kw):
    '''return an EssenceSymbol using the parameters provided.
    Note: Users should probably not call this method directly, but instead use essentialize().

    If the new EssenceSymbol equals any existing one, return the existing one instead.
    If created a new symbol, stores it in ESSENCE_SYMBOLS.
    '''
    return _essence_symbol_create(s, subscripts, targets=targets, replaced=replaced, id_=id_, **kw) 

def _essence_symbol_create(s=None, *args, **kw):
    '''create new symbol but first ensure no duplicates;
    if duplicate, return previously-created equal symbol.
    Generic args & kwargs --> can be used by subclasses with arbitrary __init__.
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    return ESSENCE_SYMBOLS.get_new_or_existing_instance(EssenceSymbol, s, *args, **kw)

def new_essence_symbol(s=None, subscripts=(), *, targets=None, replaced=None, id_=0, **kw):
    '''create a new EssenceSymbol using the parameters provided.
    
    id_ might be incremented any number of times, until the created essence symbol is new.
        the value of id_ here just indicates the starting value for that incrementing.
    '''
    return ESSENCE_SYMBOLS.get_new_instance(EssenceSymbol, s, subscripts, targets=targets, replaced=replaced,
                                            kw_increment='id_', id_=id_, **kw)

def new_essence_symbol_like(x, s=None, *, targets=None, replaced=None, id_=0,
                            esym_like=None,
                            keep_subscripts=False, **kw):
    '''create a new EssenceSymbol like x, using the parameters provided.

    s, targets, and replaced go directly to EssenceSymbol.__init__.
    id_ goes to EssenceSymbol.__init__ after incrementing enough times
        such that the created essence symbol is new. The value here is the starting point.
    esym_like: None or EssenceSymbol
        if provided, use esym_like to set defaults for s, targets, replaced, and id_.
        (Those defaults can still be overwritten by entering the corresponding kwarg here.)

    keep_subscripts: bool, default False
        whether the created EssenceSymbol should have subscripts like x.
    '''
    _kw_esym = _esym_defaults_from_esym(esym_like=esym_like, s=s, targets=targets, replaced=replaced, id_=id_)
    return ESSENCE_SYMBOLS.get_new_instance(EssenceSymbol.with_properties_like, x,
                                            keep_subscripts=keep_subscripts,
                                            kw_increment='id_', **_kw_esym, **kw)

def _esym_defaults_from_esym(esym_like=None, s=None, targets=None, replaced=None, id_=0):
    '''returns a dict of values for s, targets, replaced, and id_.
    Use values provided, else values from esym_like if provided.
    '''
    if esym_like is not None:
        if s is None:
            s = esym_like.s
        if targets is None:
            targets = esym_like.targets
        if replaced is None:
            replaced = esym_like.replaced
        if esym_like.id_ > id_:
            id_ = esym_like.id_ + 1
    return dict(s=s, targets=targets, replaced=replaced, id_=id_)

def new_essence_symbol_to_replace(x, s=None, *, targets=None, id_=0, esym_like=None, **kw_init):
    '''create a new EssenceSymbol meant to replace x, using the parameters provided.
    NOTE: prefer to use essence_symbol_for(...) instead,
        unless you want to force EssenceSymbol objects to be replaced by new EssenceSymbol objects.

    s and targets go directly to EssenceSymbol.__init__.
    id_ goes to EssenceSymbol.__init__ after incrementing enough times
        such that the created essence symbol is new. The value here is the starting point.
    esym_like: None or EssenceSymbol
        if provided, use esym_like to set defaults for s, targets, and id_.
        (Those defaults can still be overwritten by entering the corresponding kwarg here.)

    keep_subscripts: bool, default False
        whether the created EssenceSymbol should have subscripts like x.
    '''
    return new_essence_symbol_like(x, s=s, targets=targets, id_=id_, replaced=x, esym_like=esym_like, **kw_init)

def essence_symbol_for(x, s=None, *, targets=None, id_=0, esym_like=None, **kw_init):
    '''return an EssenceSymbol for x, using the parameters provided.
    if x is already an EssenceSymbol, return x if targets are a subset of x.targets.

    s and targets go directly to EssenceSymbol.__init__.
    id_ goes to EssenceSymbol.__init__ after incrementing enough times
        such that the created essence symbol is new. The value here is the starting point.
    esym_like: None or EssenceSymbol
        if provided, use esym_like to set defaults for s, targets, and id_.
        (Those defaults can still be overwritten by entering the corresponding kwarg here.)

    keep_subscripts: bool, default False
        whether the created EssenceSymbol should have subscripts like x.
    '''
    _kw_esym = _esym_defaults_from_esym(esym_like=esym_like, s=s, targets=targets, replaced=x, id_=id_)
    if isinstance(x, EssenceSymbol):  # might return x, unchanged.
        targets = _kw_esym['targets']
        if targets is None:
            return x
        elif (x.targets == targets) or all(t in x.targets for t in targets):
            return x
    return new_essence_symbol_like(x, **_kw_esym, **kw_init)
