"""
File Purpose: attach basic vector-related methods to objects.

The idea here is that we don't need new objects (e.g. "VectorSymbol" or "VectorSum")
but can instead add rules (e.g. "am I a vector?") to the existing objects.
"""
from .vectors_tools import (
    strictest_vectoriality, any_vectoriality, first_nonzero_vectoriality,
    is_vector, is_unit_vector, is_constant_scalar,
)
from ..abstracts import (
    IterableSymbolicObject,
    _equals0, is_constant,
    init_modifier,
)
from ..basics import (
    Sum, Product, Power, Equation, EquationSystem,
)
from ..basics import _string_rep 
from ..errors import VectorialityError
from ..tools import (
    equals,
    caching_attr_simple_if,
    Binding,
)
from ..defaults import DEFAULTS, ONE

binding = Binding(locals())


''' --------------------- IterableSymbolicObject attachments --------------------- '''

with binding.to(IterableSymbolicObject):
    @binding   #note: don't need caching on this one because get_symbols is cached.
    def get_vector_symbols(self):
        '''returns tuple of Symbol objects in self which are vectors.'''
        return tuple(s for s in self.get_symbols() if is_vector(s))


''' --------------------- IS_VECTOR --------------------- '''

with binding.to(IterableSymbolicObject):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def is_vector(self):
        '''returns whether self is a vector, i.e. whether any terms in self are vectors.
        note: returns None if all terms in self are 0. Otherwise returns True or False.
        Subclasses with more complicated vectoriality should overwrite this method.
        '''
        return any_vectoriality(*self)

with binding.to(Sum):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def is_vector(self):
        '''returns whether self is a vector, i.e. whether the first non-zero summand is a vector.
        note: returns None if all summands are 0.
        '''
        return first_nonzero_vectoriality(*self)

with binding.to(Product):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def is_vector(self):
        '''returns whether self is a vector, i.e. whether any factor is a vector.
        note: returns None if is_vector(factor) is None for any factor (e.g. if any factor is 0).
        '''
        for factor in self:
            vral = is_vector(factor)
            if vral is None:
                return None
            elif vral:
                return vral
        # << found no factors with vectoriality None or True; but at least one False.
        return False   # (assumes len(self)>0, which is fine because self is a Product.)

with binding.to(Power):
    @binding
    def is_vector(self):
        '''returns whether self is a vector, i.e. whether self.base is a vector.
        (note: error from vector raised to incompatible power, e.g. uvec**2, handled by __init__.)
        '''
        return is_vector(self.base)

with binding.to(EquationSystem):
    @binding
    def is_vector(self):
        '''raises TypeError; don't know how to answer "is this system of equations a vector".'''
        raise TypeError('not sure what this means: is_vector(EquationSystem instance)')


''' --------------------- INIT_MODIFIERS --------------------- '''

@init_modifier(Sum)
def _init_sum_vectoriality_check(self, *terms, check_rank=True, **kw):
    '''if terms' vectorialities are incompatible, raise VectorialityError unless check_rank=False.
    (e.g. vector + scalar is incompatible.)
    '''
    if check_rank:
        try:
            vral = strictest_vectoriality(*terms)
        except VectorialityError:
            raise VectorialityError("Cannot create Sum where some terms are vectors but others are not") from None

@init_modifier(Product)
def _init_product_vectoriality_check(self, *terms, **kw):
    '''if two or more terms are vectors, raise VectorialityError.'''
    n_vectors = 0
    for t in terms:
        if is_vector(t):
            n_vectors += 1
            if n_vectors >= 2:
                errmsg = "Cannot create Product of two or more vectors. Did you mean dot_product or cross_product?"
                raise VectorialityError(errmsg)

@init_modifier(Power)
def _init_power_vectoriality_check(self, base, exponent, **kw):
    '''raise VectorialityError in the following cases:
        (vector)^(any power other than 1)
        (any number other than 0)^(vector)
    '''
    if is_vector(base):
        if not equals(exponent, ONE):
            raise VectorialityError("vector ** value. Did you mean dot_product or cross_product?")
    if is_vector(exponent):
        if not _equals0(base):
            raise VectorialityError("value ** vector.")

@init_modifier(Equation)
def _init_equation_vectoriality_check(self, lhs, rhs, check_rank=True, **kw):
    '''initialize Equation.
    if lhs and rhs vectorialities are incompatible, raise VectorialityError unless check_rank=False.
        (e.g. vector == scalar is incompatible.)
    '''
    if check_rank:
        try:
            _ = strictest_vectoriality(lhs, rhs)
        except VectorialityError:
            if is_vector(lhs):
                errmsg = "LHS is vector but RHS is not!"
            else:
                errmsg = "RHS is vector but LHS is not!"
            raise VectorialityError(errmsg) from None


''' --------------------- Product Strings --------------------- '''

# for strings, change ordering so that:
#   - unit vectors appear last. (Note these may be constant.)
_spfc = _string_rep._STR_PRODUCT_FACTORS_CATEGORIES  # short-hand reference
_spfc.replace_or_append_category('constant', 'constant_scalar', is_constant_scalar)
_spfc.append_category('_default', None)  # << put "default" before unit vector.
_spfc.append_category('unit_vector', is_unit_vector)