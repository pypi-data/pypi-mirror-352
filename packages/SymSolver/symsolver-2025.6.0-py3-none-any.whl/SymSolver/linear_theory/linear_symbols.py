"""
File Purpose: update Symbol class appropriately to handle linear theory: 0th or 1st order.

Just includes the "basic" linear-theory-related content, e.g. "order"

Note: the call signature for initializing symbols here intentionally does not make kwargs explicit,
    e.g. it does not put vector=False, hat=False in the function defintion, but rather **kw.
    This is in case of potentially rewriting the code so that modules (like this one) which
    adjust Symbol can be imported in a different order in the future.
    The "final" top-level symbol initializer code SHOULD make the kwargs more explicit, for convenience.
"""

from .linear_theory_tools import get_order, _order_docs, MIXED_ORDER
from ..basics import Symbol
from ..errors import LinearizationPatternError
from ..vectors import _symbols_module as _symbols_parent
from ..initializers import initializer_for
from ..tools import (
    alias, alias_to_result_of,
    appended_unique,
    Binding, format_docstring,
)
from ..defaults import DEFAULTS, ZERO, ONE

binding = Binding(locals())


''' --------------------- CREATION / INITIALIZATION --------------------- '''

# # # CREATION / INITIALIZATION # # #
_init_paramdocs = \
    fr'''{_symbols_parent._init_paramdocs}
    order: None or value, default None
        'order' of this Symbol, in the sense of linear theory.
        {_order_docs}'''

with binding.to(Symbol, keep_local=True):
    @binding
    @format_docstring(paramdocs=_init_paramdocs)
    def __init__(self, s, subscripts=(), *, constant=None, **kw):
        '''initialize Symbol self.

        {paramdocs}
        '''
        order = kw.pop('order', None)
        if (constant is None) and (order == ZERO) and DEFAULTS.SYMBOLS_o0_CONSTANT:
            constant = True
        _symbols_parent.__init__(self, s, subscripts=subscripts, constant=constant, **kw)
        self._order = order

    @binding
    def _init_properties(self):
        '''returns dict for initializing another symbol like self.'''
        kw = _symbols_parent._init_properties(self)
        kw['order'] = self.order
        return kw

    _kwargs_like_docs = f'''{_symbols_parent._kwargs_like_docs}
            order = get_order(obj)'''

    @binding.bind(methodtype=staticmethod)
    @format_docstring(_kwargs_like_docs=_kwargs_like_docs)
    def kwargs_like(obj):
        '''returns dict of kwargs for creating Symbol like obj.
        Those kwargs will be:
            {_kwargs_like_docs}
        '''
        kw = _symbols_parent.kwargs_like(obj)
        kw['order'] = get_order(obj)
        return kw

Symbol.order = property(lambda self: self._order,
                        doc='''order of this Symbol, in the sense of linear theory''')


''' --------------------- LINEAR THEORY-RELATED METHODS --------------------- '''

with binding.to(Symbol):
    # # # CREATION / INITIALIZATION # # #
    @binding
    def as_oNone(self):
        '''returns copy of self with order=None, or self if self.order is None already.'''
        return self if self.order is None else self._new(order=None)

    @binding
    def as_o0(self):
        '''returns copy of self with order=0, or self if self.order==0 already.'''
        return self if self.order==ZERO else self._new(order=ZERO)

    @binding
    def as_o1(self):
        '''returns copy of self with order=1, or self if self.order==1 already.'''
        return self if self.order==ONE else self._new(order=ONE)

    # # # EQUALITY # # #
    # two Symbols are only equal if they match in these attrs:
    Symbol._EQ_TEST_ATTRS = appended_unique(Symbol._EQ_TEST_ATTRS, ['order'])

    # # # ORDER & LINEARIZING # # #
    @binding
    def get_order(self):
        '''returns the order of self, in the sense of linear theory.'''
        return self.order

    @binding
    def get_o0(self):
        '''returns 0th order (see: linear_theory) form of self.
        if self is constant, return self.
        else if self already had a non-None order, raise LinearizationPatternError.
        else, return self.as_o0()
        '''
        if self.constant:
            return self
        elif self.order is None:
            return self.as_o0()
        else:
            errmsg = f"0th order form of {type(self).__name__} with non-None order (={self.order}) not allowed."
            raise LinearizationPatternError(errmsg)

    @binding
    def get_o1(self):
        '''returns 1st order (see: linear_theory) form of self.
        if self is constant, return 0.
        if self already had a non-None order, raise LinearizationPatternError.
        else, return self.as_o1()
        '''
        if self.constant:
            return ZERO
        elif self.order is None:
            return self.as_o1()
        else:
            errmsg = f"1st order form of {type(self).__name__} with non-None order (={self.order}) not allowed."
            raise LinearizationPatternError(errmsg)

    # # # STRING # # #
    @binding
    def __str__(self):
        '''string representation of self.'''
        s_str = self._vsym_str()
        order = self.order
        if order is MIXED_ORDER:
            order = '*' if DEFAULTS.DEBUG_LINEARIZING else None
        if order is not None:
            order_str = f'^{{({order})}}'
            s_str = f'{{{s_str}}}{order_str}'
        subs_str = self._subs_str()
        return s_str + subs_str

    @binding.bind(keep_local=True)  # keep _repr_contents in local namespace so that later packages can refer to it.
    def _repr_contents(self, **kw):
        '''returns contents to put inside 'Symbol()' in repr for self.'''
        contents = _symbols_parent._repr_contents(self, **kw)
        if self.order is not None:
            contents.append(f'order={self.order}')
        return contents

    @binding
    def _str_protect_power_base(self, **kw__None):
        '''returns whether str of self needs protecting if it appears in base of power.
        i.e., returns whether self.order is non-None.
        '''
        return (self.order is not None)