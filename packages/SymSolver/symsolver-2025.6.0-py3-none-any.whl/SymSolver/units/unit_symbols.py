"""
File Purpose: allow to attach units to symbols.

[TODO] better handling of: make symbol; get symbol.as_vector;
        attach units to symbol; get symbol.as_vector (and have the units transfer to the result too).
"""
from ..basics import (
    Symbol,
)
from ..errors import UnitsPatternError
from ..linear_theory import _symbols_module as _symbols_parent
from ..initializers import initializer_for
from ..tools import (
    alias,
    StoredInstances,
    Binding, format_docstring,
)
from ..defaults import DEFAULTS

binding = Binding(locals())


''' --------------------- SYMBOL CREATION / INITIALIZATION --------------------- '''
# add the "units_base" kwarg / attibute option to initialization

# # # CREATION / INITIALIZATION # # #
_init_paramdocs = \
    fr'''{_symbols_parent._init_paramdocs}
    units_base: string or SymbolicObject
        units dimension associated with this Symbol,
        e.g. 'L' for length. If not simple (e.g. L^-3) use SymbolicObject.
        if string, units_base will be converted to UnitSymbol before storing.'''

with binding.to(Symbol, keep_local=True):
    @binding
    @format_docstring(paramdocs=_init_paramdocs)
    def __init__(self, s, subscripts=(), *, constant=False, **kw):
        '''initialize Symbol self.

        {paramdocs}
        '''
        units_base = kw.pop('units_base', None)
        _symbols_parent.__init__(self, s, subscripts=subscripts, constant=constant, **kw)
        self._units_base_init = units_base
        if isinstance(units_base, str):
            units_base = INITIALIZERS.unit_symbol(units_base)
        self._units_base = units_base

    @binding
    def _init_properties(self):
        '''returns dict for initializing another symbol like self.'''
        kw = _symbols_parent._init_properties(self)
        kw['units_base'] = self.units_base
        return kw

Symbol.units_base = property(lambda self: getattr(self, '_units_base', None),
                             lambda self, value: setattr(self, '_units_base', value),
        doc='''units dimension associated with this Symbol, e.g. L or t for length or time.
        Note that the units_base attribute is writable, and not used when checking equality.''')


''' --------------------- UNITS-RELATED METHODS --------------------- '''

with binding.to(Symbol):
    @binding.bind(keep_local=True)  # keep _repr_contents in local namespace so that later packages can refer to it.
    def _repr_contents(self, **kw):
        '''returns contents to put inside 'Symbol()' in repr for self.'''
        contents = _symbols_parent._repr_contents(self, **kw)
        if DEFAULTS.DEBUG_UNITS and (self.units_base is not None):
            contents.append(f'units_base={self.units_base}')
        return contents


''' --------------------- UNIT SYMBOLS --------------------- '''

class UnitSymbol(Symbol):
    '''Symbol which is a unit. Otherwise behaves like a Symbol.
    if s starts & ends with '[', ']', trim those characters before storing.
    assert self is not a vector, and order is not provided.

    note: vector=None by default, indicating to treat this object as "possibly a vector, possibly not".
    '''
    def __init__(self, s, subscripts=(), *, constant=True, vector=None, **kw):
        if s.startswith('[') and s.endswith(']'):
            s = s[1:-1]  # trim '[' and ']'.
        super().__init__(s, subscripts=subscripts, constant=constant, vector=vector, **kw)
        order = getattr(self, 'order', None)
        if order is not None:
            raise UnitsPatternError(f'Expected {type(self).__name__}.order=None but got order={order}')
        vector = getattr(self, 'vector', None)
        if vector:
            raise UnitsPatternError(f'Expected bool({type(self).__name__}.vector)==False but got vector={vector}')

    def is_unit(self):
        '''returns True, because self is a unit.'''
        return True

    def __str__(self, **kw):
        superstr = super().__str__(**kw)
        return f'[{superstr}]'


''' --------------------- Create a UnitSymbol object --------------------- '''
# UNIT_SYMBOLS stores all the UnitSymbol objects ever created.
# the idea is that when about to creating a new UnitSymbol which equals one in here,
#   instead return the already-existing UnitSymbol from in here.

UNIT_SYMBOLS = StoredInstances(UnitSymbol)

@initializer_for(UnitSymbol)
def unit_symbol(s, subscripts=(), *, constant=True, **kw):
    '''makes (or gets already existing) unit symbol.
    s: string
        if it starts & ends with '[', ']' those characters will be trimmed.
    expect order=None, bool(vector)=False, if either are provided in **kw.
    see help(INITIALIZERS.symbol) for more kw options.
    '''
    result = UNIT_SYMBOLS.get_new_or_existing_instance(UnitSymbol, s,
                                subscripts=subscripts, constant=constant, **kw)
    return result
