"""
File Purpose: update Symbol class appropriately to handle vectors.

Just includes the "basic" vector-related content, e.g. "is_vector".
More complicated things (e.g. .dot --> DotProduct) will be attached by other modules.

Note: the call signature for initializing symbols here intentionally does not make kwargs explicit,
    e.g. it does not put vector=False, hat=False in the function defintion, but rather **kw.
    This is in case of potentially rewriting the code so that modules (like this one) which
    adjust Symbol can be imported in a different order in the future.
    The "final" top-level symbol initializer code SHOULD make the kwargs more explicit, for convenience.
"""
from .vectors_tools import (
    is_vector, is_unit_vector,
)
from ..abstracts import SubbableObject, is_subbable
from ..basics import (
    Symbol,
)
from ..basics import _symbols_module as _symbols_parent
from ..initializers import initializer_for
from ..tools import (
    alias, alias_to_result_of,
    appended_unique,
    Binding, format_docstring,
)
from ..defaults import ONE

binding = Binding(locals())


''' --------------------- CREATION / INITIALIZATION --------------------- '''

# # # CREATION / INITIALIZATION # # #
_init_paramdocs = \
    fr'''{_symbols_parent._init_paramdocs}
    vector: bool, default False
        whether this Symbol represents a vector.
        if True, use '\vec' when displaying self, unless also self.hat.
    hat: bool, default False
        whether this Symbol represents a unit vector.
        if True, overwrite self.vector to True. And use '\hat' when displaying self.'''

with binding.to(Symbol, keep_local=True):
    @binding
    @format_docstring(paramdocs=_init_paramdocs)
    def __init__(self, s, subscripts=(), *, constant=False, **kw):
        '''initialize Symbol self.

        {paramdocs}
        '''
        vector = kw.pop('vector', False)
        hat = kw.pop('hat', False)
        _symbols_parent.__init__(self, s, subscripts=subscripts, constant=constant, **kw)
        self._vector = vector
        self._set_hat(hat)

    @binding
    def _init_properties(self):
        '''returns dict for initializing another symbol like self.'''
        kw = _symbols_parent._init_properties(self)
        kw['vector'] = self.vector
        kw['hat']    = self.hat
        return kw

    _kwargs_like_docs = f'''{_symbols_parent._kwargs_like_docs}
            vector = is_vector(obj)
            hat = is_unit_vector(obj)'''

    @binding.bind(methodtype=staticmethod)
    @format_docstring(_kwargs_like_docs=_kwargs_like_docs)
    def kwargs_like(obj):
        '''returns dict of kwargs for creating Symbol like obj.
        Those kwargs will be:
            {_kwargs_like_docs}
        '''
        kw = _symbols_parent.kwargs_like(obj)
        kw['vector'] = is_vector(obj)
        kw['hat'] = is_unit_vector(obj)
        return kw

Symbol.vector = property(lambda self: self._vector, doc='''whether the Symbol represents a vector''')
Symbol.hat = property(lambda self: self._hat, doc='''whether the Symbol represents a unit vector''')


''' --------------------- VECTOR-RELATED METHODS --------------------- '''

with binding.to(Symbol):
    # # # CREATION / INITIALIZATION # # #
    @binding
    def _set_hat(self, hat):
        '''sets self._hat. Also, if hat, sets self._vector=True.
        Intended for internal use only.
        Note: SymSolver assumes Symbols (and other SymbolicObjects) are immutable after initialization.
        '''
        self._hat = hat
        if hat:
            self._vector = True

    @binding
    def as_vector(self):
        '''returns copy of self with vector=True, or self if self.vector==True already.
        Note: the result will be a unit vector if self.hat==True.
        '''
        return self if self.vector else self._new(vector=True)

    @binding
    def as_scalar(self):
        '''returns copy of self with vector=False, or self if self.vector==False already.'''
        return self if not self.vector else self._new(vector=False, hat=False)

    @binding
    def as_unit_vector(self):
        '''returns copy of self with hat=True, or self if self.hat==True already.'''
        return self if self.hat else self._new(hat=True)

    Symbol.as_hat = alias('as_unit_vector')

    @binding
    def as_nonunit_vector(self):
        '''returns copy of self with vector=True, hat=False, or self if that is the case already.'''
        return self if (self.vector and not self.hat) else self._new(vector=True, hat=False)

    # # # MAGNITUDE AND DIRECTION # # #
    @binding
    def magnitude(self):
        '''returns magnitude == 1 if self.hat else self.as_scalar()'''
        return ONE if self.hat else self.as_scalar()

    @binding
    def direction(self):
        '''returns self.as_unit_vector(), but raises TypeError if not self.vector.'''
        if self.vector:
            return self.as_unit_vector()
        else:
            raise TypeError(f'Cannot get direction for non-vector: {repr(self)}')

    Symbol.mag = alias_to_result_of('magnitude')
    Symbol.dir = alias_to_result_of('direction')

    # # # EQUALITY # # #
    # two Symbols are only equal if they match in these attrs:
    Symbol._EQ_TEST_ATTRS = appended_unique(Symbol._EQ_TEST_ATTRS, ['vector', 'hat'])

    # # # VECTOR-NESS # # #
    @binding
    def is_vector(self):
        '''returns whether self is a vector.'''
        return self.vector

    @binding
    def is_unit_vector(self):
        '''returns whether self is a unit vector'''
        return self.hat

    # # # STRING # # #
    @binding
    def _vsym_str(self):
        r'''return string for self.s, with \vec or \hat if appropriate.'''
        s_str = str(self.s)
        if self.vector:
            v_command_str = r"\hat" if self.hat else r"\vec"
            s_str = f'{v_command_str}{{{s_str}}}'
        return s_str

    @binding
    def __str__(self):
        '''string representation of self.'''
        s_str = self._vsym_str()
        subs_str = self._subs_str()
        return s_str + subs_str

    @binding.bind(keep_local=True)  # keep _repr_contents in local namespace so that later packages can refer to it.
    def _repr_contents(self, **kw):
        '''returns contents to put inside 'Symbol()' in repr for self.'''
        contents = _symbols_parent._repr_contents(self, **kw)
        if self.hat:
            contents.append(f'hat={self.hat}')
        elif self.vector != False:  # (might be None)
            contents.append(f'vector={self.vector}')
        return contents


''' --------------------- Hatify --------------------- '''

with binding.to(Symbol):
    @binding
    def hatify(self, *vecs_to_hat, **kw__None):
        '''returns self.magnitude() * self.direction().
        if vecs_to_hat is provided but self is not in vecs_to_hat, returns self instead.
        '''
        if len(vecs_to_hat)==0 or (self in vecs_to_hat):
            direction = self.direction() # put direction first in case of TypeError.
            magnitude = self.magnitude()
            return magnitude * direction
        else:
            return self

with binding.to(SubbableObject):
    @binding
    def hatify(self, *vecs_to_hat, **kw):
        '''replace all x in vecs_to_hat with x.as_hat(), throughout self.
        If vecs_to_hat is empty, hatify ALL vectors in self.
        kw go to self._substitution_loop.
        '''
        if not is_subbable(self):
            return self
        # this function's subtitution rule for self:
        #   (note that the main hatification is handled by Symbol.hatify)
        if len(vecs_to_hat) == 0:
            vecs_to_hat = tuple(s for s in get_symbols(self) if (s.is_vector() and not s.is_unit_vector()))
        # loop through terms in self, if applicable.
        def hatify_rule(term):
            return term.hatify(*vecs_to_hat, **kw)
        return self._substitution_loop(hatify_rule, **kw)
