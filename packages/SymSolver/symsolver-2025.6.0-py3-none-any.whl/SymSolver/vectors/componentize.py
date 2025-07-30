"""
File Purpose: componentize() and component() methods
for expanding things into their components in an OrthonormalBasis.

- Rather than always write "u dot xhat", it is common convention to write "u_x".
    - Note: this pattern is only when xhat is part of an OrthonormalBasis.
        E.g. if Bhat is just shorthand for Bvec/|Bvec|, but not part of an OrthonormalBasis,
        then "u dot Bhat" should not turn into "u_B".
- Replace vectors by their components in a specified basis
    E.g. vector u, basis (xhat, yhat, zhat) --> u_x xhat + u_y yhat + u_z zhat
- Replace a vector equation by multiple equations, one for each component
    E.g. vector u, vector w, basis (xhat yhat), equation(5*c*u, w)
    --> equation_system(equation(5*c*u_x, w_x), equation(5*c*u_y, w_y))

"COMPONENT" VS "COMPONENTIZE"
- u.component(xhat) will return the xhat component of vector u.
    E.g. Symbol('u', vector=True).component(xhat) --> u dot xhat,   or if using shorthand: u_x
- u.componentize(basis) will replace all vector Symbols in u with a sum of their components.
    E.g. (vector u).componentize((xhat, yhat)) --> (u dot xhat) xhat + (u dot yhat) yhat

DEFAULT BEHAVIOR CONTROLS:
- default basis to use: defaults.DEFAULTS.COMPONENTS_BASIS
    - if this is set to a non-None value, use this basis by default.
    - basis for a single call (and any internal calls) can always be set via:
        kwarg 'basis', for components() and componentize() routines.
- default "whether to use shorthand": defaults.DEFAULTS.COMPONENTS_SHORTHAND
    - if set to True, will use shorthand by default. E.g. "k dot xhat --> k_x".
    - shorthand for a single call (and any internal calls) can be set via:
        kwarg 'shorthand', for component(), components(), and componentize() routines;
        kwarg 'components_shorthand' for simplification routines (e.g. simplify(), simplified())
"""
import builtins  # for non-ambiguous sum
from textwrap import indent

from .basis import (
    OrthonormalBasis,
    is_basis_vector, is_orthonormal_basis_vector,
)
from .dot_product import (
    DotProductBase,
)
from .vectors_tools import (
    is_vector,
    scalar_vector_get_factors,
)
from ..attributors import attributor
from ..abstracts import (
    SymbolicObject, AbstractOperation, IterableSymbolicObject,
    simplify_op, simplify_op_skip_for, SIMPLIFY_OPS_SKIP,
    simplify_op_DONT_skip, simplify_op_DO_skip,
)
from ..basics import (
    Symbol, Sum, Product, Equation, EquationSystem,
    equation_system,
)
from ..errors import (
    ComponentPatternError,
    VectorialityError,
    InputMissingError,
)
from ..initializers import INITIALIZERS
from ..tools import (
    Dict,
    alias,
    Binding, format_docstring, caching_attr_simple_if,
)
from ..defaults import DEFAULTS
from ..defaults import COMPONENTS as defaults_COMPONENTS  # << used in defining _COMPONENTS_SETTER

binding = Binding(locals())


''' --------------------- Convenience - Componentize --------------------- '''

def get_default_basis():
    '''returns DEFAULTS.COMPONENTS_BASIS, or raise InputMissingError if it is None.'''
    result = DEFAULTS.COMPONENTS_BASIS
    if result is None:
        raise InputMissingError('no default basis found; DEFAULTS.COMPONENTS_BASIS is None.')
    return result

def get_default_ndim(basis=None):
    '''returns DEFAULTS.COMPONENTS_NDIM, if it is not None,
    otherwise returns len(get_default_basis() if basis is None else basis), if possible,
    otherwise raises InputMissingError.
    '''
    result = DEFAULTS.COMPONENTS_NDIM
    if result is None:
        if basis is None:
            try:
                basis = get_default_basis()
            except InputMissingError:
                errmsg = ("no default ndim found; DEFAULTS.COMPONENTS_NDIM is None."
                          "Also tried ndim=len(default basis), but that value is None as well.")
                raise InputMissingError(errmsg)
        result = len(basis)
    return result

def set_default_basis(new_default_basis):
    '''sets new_default_basis to be the default basis for componentize() routines.
    aside checking type and length, equivalent to DEFAULTS.COMPONENTS_BASIS = new_default_basis.

    new_default_basis: None or OrthonormalBasis instance
        None --> revert to having "no default" for basis.
        OrthonormalBasis --> use this value, but first, check default ndim:
            if DEFAULTS.COMPONENTS_NDIM is not None, raise ValueError unless it equals len(new_default_basis).
        non-None, non-OrthonormalBasis: --> raise TypeError
    '''
    if new_default_basis is not None:
        if isinstance(new_default_basis, OrthonormalBasis):
            default_ndim = DEFAULTS.COMPONENTS_NDIM
            if (default_ndim is not None) and (len(new_default_basis) != default_ndim):
                raise ValueError(f'len(new_default_basis) != DEFAULTS.COMPONENTS_NDIM (=={default_ndim})')
        else:
            raise TypeError(f'expected None or OrthonormalBasis; got {type(new_default_basis).__name__}')
    DEFAULTS.COMPONENTS_BASIS = new_default_basis

def set_default_ndim(new_default_ndim):
    '''sets new_default_ndim to be the default ndim for components_count() routines.
    aside from comparing with default basis, equivalent to DEFAULTS.COMPONENTS_NDIM = new_default_ndim.

    new_default_ndim: None or integer
        None --> revert to having "no default" for ndim.
            In the "no default ndim" case, use length(default basis) if possible.
        else --> use this value, but first, check default basis:
            if DEFAULTS.COMPONENTS_BASIS is not None, raise ValueError its length equals new_default_ndim.
    '''
    if new_default_ndim is not None:
        default_basis = DEFAULTS.COMPONENTS_BASIS
        if (default_basis is not None) and (len(default_basis) != new_default_ndim):
            raise ValueError(f'new_default_ndim != len(DEFAULTS.COMPONENTS_BASIS) (=={len(default_basis)})')
    DEFAULTS.COMPONENTS_NDIM = new_default_ndim

def _default_basis_if_None(basis):
    '''returns basis if not None, else DEFAULTS.COMPONENTS_BASIS if not None, else raise InputMissingError.'''
    if basis is not None:
        return basis
    try:
        return get_default_basis()
    except InputMissingError:
        errmsg = ('basis not found (got basis=None). Possible fixes: '
                  'enter basis as arg or kwarg, or set non-None value for DEFAULTS.COMPONENTS_BASIS.')
        raise InputMissingError(errmsg) from None

def _default_ndim_if_None(ndim, basis=None):
    '''returns ndim if not None, else get_default_ndim() if possible, else raise InputMissingError.'''
    if ndim is not None:
        return ndim
    try:
        return get_default_ndim(basis=basis)
    except InputMissingError:
        errmsg = ('ndim not found (got ndim=None). Possible fixes: '
                  'enter ndim as arg or kwarg, set non-None value of DEFAULTS.COMPONENTS_NDIM, '
                  'or set non-None value for DEFAULTS.COMPONENTS_BASIS (to use ndim=len(basis)).')
        raise InputMissingError(errmsg) from None

@attributor
def is_directly_componentizeable(obj):
    '''returns whether obj.componentize() might make direct replacements for components.
    Symbol, for example. But not Sum (since Sum just propogates componentize() call to its terms.
    Does this by returning obj._is_directly_componentizeable() if possible,
    else returns False.
    '''
    try:
        return obj._is_directly_componentizeable()
    except AttributeError:
        return False

@attributor
def componentize(x, basis=None, shorthand=None, **kw):
    '''componentizes x in basis.
    Rewrites all vectors into a sum of their components (times the appropriate unit vectors)
        e.g. componentize(u, (xhat, yhat)) --> (u dot xhat) xhat + (u dot yhat) yhat
    Also turns vector equations into multiple component equations.

    basis: None or iterable with elements members of an OrthonormalBasis. default None
        None --> use DEFAULTS.COMPONENTS_BASIS
    shorthand: None or bool, default None
        whether to convert to shorthand notation when possible (e.g. k dot xhat --> k_x)
        None --> use DEFAULTS.COMPONENTS_SHORTHAND

    returns x.componentize(basis, shorthand, **kw) if available, else x.
    '''
    try:
        x_componentize = x.componentize
    except AttributeError:
        return x
    else:
        basis = _default_basis_if_None(basis)
        return x_componentize(basis, shorthand=shorthand, **kw)

_components_count_paramdocs = \
    '''ndim: None or integer
        number of dimensions in a single vector; ndim == components_count(a vector).
        None --> use get_default_ndim(basis=basis)
    basis: None or OrthonomalBasis
        if provided, count components as if vectors each have len(basis) components.
        If ndim is provided (i.e., not None), assert that basis=None.
        If not None, use ndim=len(basis).'''

@attributor
@format_docstring(paramdocs=_components_count_paramdocs)
def components_count(x, ndim=None, basis=None, **kw):
    '''counts number of vector components of x, given the number of dimensions in a vector.
    result depends on what x represents:
        scalar --> 1
        vector --> ndim
        equation system --> sum(ndim if is_vector(eqn) else 1 for eqn in x)

    {paramdocs}

    returns x.components_count(ndim, basis, **kw) if available, else 1.
    '''
    # ndim = _default_ndim_if_None(ndim, basis=basis) # << SKIP here. if x is a scalar, don't need this info.
    try:
        return x.components_count(x, ndim=ndim, basis=basis, **kw)
    except AttributeError:
        return 1


''' --------------------- COMPONENT --------------------- '''
# # # get single component of vector. default -- use dot product # # #

# # # DEFAULT FOR COMPONENT # # #
with binding.to(AbstractOperation):
    @binding
    def component(self, x, **kw__None):
        '''returns x.dot(self), after ensuring that x is a member of an OrthonormalBasis.'''
        if not is_orthonormal_basis_vector(x):
            raise TypeError(f'component requires an OrthonormalBasis member x.')
        return x.dot(self)  # not self.dot(x) (in case self is an operator; see precalc_operators)

# # # SUM COMPONENT -- get component for summands # # #
with binding.to(Sum):
    @binding
    def component(self, x, **kw__component):
        '''returns sum of term.component(x) for each term in self.'''
        return self._new(*(term.component(x, **kw__component) for term in self))

# # # PRODUCT COMPONENT -- get component for vector factor # # #
with binding.to(Product):
    @binding
    def component(self, x, **kw__component):
        '''returns product of scalar factors in self and (vector factor from self).component(x)'''
        sfs, vfs = scalar_vector_get_factors(self, vector_if_None=False)
        if not len(vfs)==1:
            if len(vfs)==0:
                raise VectorialityError('Cannot get component of Product without a vector factor.')
            else:
                raise NotImplementedError('Component from product with more than 1 vector factor.')
        vf = vfs[0]
        vf_component = vf.component(x, **kw__component)
        return self._new(*sfs, vf_component)

# # # SYMBOL COMPONENT -- maybe use shorthand # # #
with binding.to(Symbol):
    @binding
    def component(self, x, shorthand=None):
        '''gets x-component of self. (usually this means: vec(k) --> x.dot(k) or k_x)
    
        x: member of an OrthonormalBasis.
            get this component of the vector which self represents.
            Note: if self.set_component(x, value) has been called, returns the value.
        shorthand: None or bool, default None
            None --> use DEFAULTS.COMPONENTS_SHORTHAND
            False --> return x.dot(self)
            True --> result depends on self.
                if self is not a unit vector (most common scenario):
                    return self.as_scalar() but with x.as_scalar() added to subscripts.
                else if self is a basis vector in any basis,
                    return x.dot(self)  (this helps to avoid confusing situations)
                otherwise, self is a unit vector but not in any basis, so
                    return (self.as_scalar() but with x.as_scalar() added to subscripts) / self.as_scalar()
        '''
        if not self.vector:
            raise VectorialityError(f"Can't get component of a scalar: {self}")
        if _ever_used_to_define_component(x):
            try:
                return self._get_defined_component(x)
            except ComponentPatternError:
                pass  # x component of self has not be predefined, but that's fine; see below.
        if not is_orthonormal_basis_vector(x):
            raise TypeError(f'component requires an OrthonormalBasis member x.')
        if shorthand is None: shorthand = DEFAULTS.COMPONENTS_SHORTHAND
        if shorthand:
            try:
                return _symbol_component_as_shorthand(self, x)
            except TypeError:
                pass # handled below
        # if we get this far, we failed to convert to shorthand.
        return x.dot(self)  # not self.dot(x) (in case self is an operator; see precalc_operators)

def _symbol_component_as_shorthand(s, x):
    '''returns x component of Symbol s as shorthand, or raise TypeError if this is not possible.
    assumes (does not check) that s is a Symbol and a vector.
    
    x: a Symbol which is a member of an OrthonormalBasis.
        get this component of the vector which s represents.
        The isinstance(x, Symbol) check occurs after the "member of an OrthonormalBasis" check, for clarity.
    result will depend on s:
        if s is not a unit vector (most common scenario):
            return s.as_scalar() but with x.as_scalar() added to subscripts.
        else if s is a basis vector in any basis,
            raise TypeError
            (it could easily be confusing to use shorthand for "x-component of a basis vector" )
        otherwise, self is a unit vector but not in any basis, so
            return (self.as_scalar() but with x.as_scalar() added to subscripts) / self.as_scalar()
    '''
    if not is_orthonormal_basis_vector(x):
        raise TypeError(f'component as shorthand requires an OrthonormalBasis member x.')
    if not isinstance(x, Symbol):
        raise TypeError(f'expected Symbol but got {type(x).__name__}.')
    if is_basis_vector(s):
        raise TypeError('refusing to write in shorthand "x-component of basis vector s".')
    # if we got this far, x is a Symbol and a basis vector
    x = x.as_scalar()
    new_subscripts = tuple((*s.subscripts, x))
    s_as_scalar_with_subscript_x = s._new(vector=False, hat=False, subscripts=new_subscripts)
    if s.hat:  # s_hat dot x == (svec / s) dot x --> s_x / s
        return s_as_scalar_with_subscript_x / s.as_scalar()
    else:
        return s_as_scalar_with_subscript_x


''' --------------------- SYMBOL COMPONENT ALIASES --------------------- '''

_cdoc = '''{nth} component (1-indexed) of self using DEFAULTS.COMPONENTS_BASIS.
        Note: to turn on/off using shorthand, enable/disable DEFAULTS.COMPONENTS_SHORTHAND.'''

Symbol.c1 = Symbol.x = property(lambda self: self.component(get_default_basis()[0]), doc=_cdoc.format(nth='1st'))
Symbol.c2 = Symbol.y = property(lambda self: self.component(get_default_basis()[1]), doc=_cdoc.format(nth='2nd'))
Symbol.c3 = Symbol.z = property(lambda self: self.component(get_default_basis()[2]), doc=_cdoc.format(nth='3rd'))

del _cdoc


''' --------------------- COMPONENTS SHORTHAND SIMPLIFY_OP --------------------- '''

@simplify_op(DotProductBase, alias='_components_shorthand')
def _dot_product_components_shorthand(self, shorthand=True, **kw__None):
    '''converts k dot xhat --> k_x   (puts x in subscripts of k),
    for k a vector (possibly a unit vector) and xhat part of an OrthonormalBasis.
    (Also checks for xhat dot k --> k_x)

    shorthand: bool, default True
        if False, return self without changing anything.
        This is provided in case any other SymSolver simplification ops implement 'shorthand' as well,
            as a "kill switch" which disables all conversions to shorthand.
    '''
    if not shorthand:
        return self  # return self, exactly, to help indicate nothing was changed.
    if isinstance(self.t1, Symbol):  # check for k dot xhat
        try:
            return _symbol_component_as_shorthand(self.t1, self.t2)
        except TypeError:  # failed to convert to shorthand
            if isinstance(self.t2, Symbol):  # check for xhat dot k
                try:
                    return _symbol_component_as_shorthand(self.t2, self.t1)
                except TypeError:  # failed to convert to shorthand
                    pass # handled below
    return self  # return self, exactly, to help indicate nothing was changed.

# # # ADJUST "WHETHER TO USE SHORTHAND" DEFAULT # # #
# default isn't changed here.
# we attach the appropriate behavior to DEFAULTS.COMPONENTS_SHORTHAND here though;
# now, when setting DEFAULT.COMPONENTS_SHORTHAND = True (or False),
# it will also turn on (or off) "perform _dot_product_components_shorthand simplification by default".
_COMPONENTS_SHORTHAND_FNAME = '_dot_product_components_shorthand'
# initialize whether to skip, based on current default
if not DEFAULTS.COMPONENTS_SHORTHAND:
    simplify_op_skip_for(DotProductBase, _COMPONENTS_SHORTHAND_FNAME)
# attach "whether to do simplify op: component shorthand" to the setter for DEFAULTS.COMPONENTS_SHORTHAND.
def _defaults_components_shorthand_setter(self, value):
    '''sets COMPONENTS.SHORTHAND to value, and also adjusts SIMPLIFY_OPS appropriately.
    if value, ensures "whether to do simplify op: component shorthand" defaults to True.
    else, ensures "whether to do simplify op: component shorthand" defaults to False.
    '''
    # adjust simplify ops appropriately
    if value:
        simplify_op_DONT_skip(_COMPONENTS_SHORTHAND_FNAME)
    else:
        if _COMPONENTS_SHORTHAND_FNAME not in SIMPLIFY_OPS_SKIP:
            simplify_op_skip_for(DotProductBase, _COMPONENTS_SHORTHAND_FNAME)
        else:
            simplify_op_DO_skip(_COMPONENTS_SHORTHAND_FNAME)
    # actually set the value in defaults
    defaults_COMPONENTS.SHORTHAND.set(value)
DEFAULTS._COMPONENTS_SHORTHAND_SETTER = _defaults_components_shorthand_setter


''' --------------------- PREDEFINED COMPONENT for Symbol --------------------- '''

with binding.to(Symbol):
    @binding
    def define_component(self, x, value):
        '''define x component of self, so that self.component(x) --> value.
        and also during '_use_defined_components' simplify op: x.dot(self) or self.dot(x) --> value.
        '''
        try:
            clookup = self._defined_components
        except AttributeError:
            clookup = Dict()
        clookup[x] = value
        self._defined_components = clookup
        # bookkeeping:
        x._ever_used_to_define_component = True

    @binding
    def _get_defined_component(self, x):
        '''returns self._defined_components[x] if possible, else raise ComponentPatternError'''
        try:
            clookup = self._defined_components
        except AttributeError:
            raise ComponentPatternError('cannot _get_defined_component(); no components have been defined.') from None
        # else
        try:
            return clookup[x]
        except KeyError:
            raise ComponentPatternError(f'component not found: {x}') from None

@attributor
def _get_defined_component(obj, x):
    '''returns the x component of obj, if predefined.
    returns obj._get_defined_component(x) if possible,
    else raise ComponentPatternError.
    '''
    try:
        obj_get_defined_component = obj._get_defined_component
    except AttributeError:
        errmsg = f'obj of type {type(obj).__name__} does not support pre-defined components.'
        raise ComponentPatternError(errmsg) from None
    else:
        return obj_get_defined_component(x)

def _ever_used_to_define_component(x):
    '''return whether x was ever used to define a component of some object;
    see also: Symbol.define_component()
    '''
    return getattr(x, '_ever_used_to_define_component', False)

@simplify_op(DotProductBase, alias='_use_defined_components', order=-1)  # apply before '_components_shorthand'
def _dot_product_use_defined_components(self, **kw__None):
    '''uses defined components. [TODO] better docs...'''
    t1, t2 = self.t1, self.t2
    if _ever_used_to_define_component(t1):
        try:
            return _get_defined_component(t2, t1)  # get t1 component of t2
        except ComponentPatternError:
            pass  # t1 component of t2 is not predefined. handled below
    if _ever_used_to_define_component(t2):
        try:
            return _get_defined_component(t1, t2)  # get t2 component of t1
        except ComponentPatternError:
            pass  # t2 component of t1 is not predefined. handled below
    return self  # return self, exactly, to help indicate nothing was changed.


''' --------------------- COMPONENTS (PLURAL) --------------------- '''
# # # get tuple of component values for each component in basis. # # #

with binding.to(Symbol):
    @binding
    def components(self, basis=None, shorthand=None):
        '''returns tuple of (self.component(vhat) for vhat in basis).
        see self.component for details on 'shorthand' kwarg.

        basis: None or iterable with elements members of an OrthonormalBasis. default None
            None --> use DEFAULTS.COMPONENTS_BASIS
        '''
        return tuple(self.component(vhat, shorthand=shorthand) for vhat in _default_basis_if_None(basis))

with binding.to(Equation):
    @binding
    def components(self, basis=None):
        '''returns tuple of (self.rdot(vhat) for vhat in basis).
        if self is not a vector equation, raise TypeError instead.

        basis: None or iterable with elements members of an OrthonormalBasis. default None
            None --> use DEFAULTS.COMPONENTS_BASIS
        '''
        basis = _default_basis_if_None(basis)
        if is_vector(self):
            return tuple(self.rdot(vhat) for vhat in basis)
            # rdot instead of dot, in case self is an operator. see precalc_operators.
            # Note: Equation(lhs, rhs).rdot(vhat) <--> Equation(vhat.dot(lhs), vhat.dot(rhs))
        else:
            raise TypeError('cannot get components for scalar-valued equation.')


''' --------------------- IS_DIRECTLY_COMPONENTIZEABLE --------------------- '''

# # # IS_DIRECTLY_COMPONENTIZEABLE for Symbol # # #
with binding.to(Symbol):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def _is_directly_componentizeable(self):
        '''returns self.is_vector(), because self is directly componentizeable if it is a vector.'''
        return self.is_vector()

# # # CONTAINS_DEEP_DIRECTLY_COMPONENTIZEABLE for IterableSymbolicObject # # #
with binding.to(IterableSymbolicObject):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def _contains_deep_any_directly_componentizeable_(self):
        '''returns whether any term (possibly deep) within self is directly componentizeable.'''
        return self.contains_deep_like(is_directly_componentizeable)


''' --------------------- COMPONENTIZE --------------------- '''
# # # turn all vectors into their components. # # #

_componentize_paramdocs = \
    '''basis: None or iterable with elements members of an OrthonormalBasis. default None
            None --> use DEFAULTS.COMPONENTS_BASIS
        shorthand: None or bool, default None
            whether to convert to shorthand notation when possible (e.g. k dot xhat --> k_x)
            None --> use DEFAULTS.COMPONENTS_SHORTHAND'''

# # # DEFAULT COMPONENTIZE -- call componentize on each term in self. # # #
with binding.to(IterableSymbolicObject):
    @binding
    @format_docstring(paramdocs=_componentize_paramdocs)
    def componentize(self, basis=None, shorthand=None, **kw):
        '''componentizes all terms in self.
        i.e. substitute vectors with a sum of their components in the given basis.
        E.g. v --> (v dot xhat) xhat + (v dot yhat) yhat + (v dot zhat) zhat.

        [EFF] if there are no _is_directly_componentizeable objects in self, return self immediately.
            (but only if DEFAULTS.CACHING_PROPERTIES.
             Since then _contains_deep_any_directly_componentizeable_ is fast.)

        {paramdocs}
        '''
        if DEFAULTS.CACHING_PROPERTIES:
            if not self._contains_deep_any_directly_componentizeable_():
                return self   # nothing to componentize in self.
        basis = _default_basis_if_None(basis)
        return self._new(*(componentize(term, basis, shorthand=shorthand, **kw) for term in self))

# # # SYMBOL COMPONENTIZE, e.g. k --> k_x xhat + k_y yhat + k_z zhat # # #
with binding.to(Symbol):
    @binding
    @format_docstring(paramdocs=_componentize_paramdocs)
    def componentize(self, basis=None, shorthand=None, **kw__None):
        '''returns self as sum of components. (e.g. k --> k_x xhat + k_y yhat + k_z zhat)
        if self is not a vector, just returns self, unchanged.

        {paramdocs}
        '''
        if not self.vector:
            return self
        basis = _default_basis_if_None(basis)
        components = self.components(basis, shorthand=shorthand)
        return self.sum(*(component * vhat for component, vhat in zip(components, basis)))

# # # EQUATION COMPONENTIZE, returns an EquationSystem in case of vector-valued equation. # # #
with binding.to(Equation):
    @binding
    @format_docstring(paramdocs=_componentize_paramdocs)
    def componentize(self, basis=None, shorthand=None, _eff=True, **kw):
        '''returns EquationSystem of self written in basis.
        result will have vectors rewritten as a sum of components in basis.
        if self is vector-valued, returns EquationSystem with result.components(basis)
        otherwise, returns EquationSystem containing only result (i.e. only 1 equation).

        {paramdocs}
        _eff: bool, default True
            [EFF] whether to use _component_from_componentized() when getting components for vector-valued equations.
            Optional because it may be more or less efficient depending on the equations involved.
            efficiency not yet benchmarked.
            Note: if _eff=False, try doing result.simplify_basis_ids() afterwards.
        '''
        basis = _default_basis_if_None(basis)
        self_is_vector = self.is_vector()
        if _eff and self_is_vector:
            component_eqs = tuple(self._component_from_componentized(xhat, basis=basis, shorthand=shorthand, **kw) for xhat in basis)
        else:
            componentized_self = self.apply_operation(lambda x: componentize(x, basis=basis, shorthand=shorthand, **kw), _prevent_new=True)
            if self_is_vector:
                component_eqs = componentized_self.components(basis)
            else:
                component_eqs = (componentized_self,)
        return INITIALIZERS.equation_system(*component_eqs)

# # # EQUATION SYSTEM COMPONENTIZE -- note number of equations may change if any are vector-valued. # # #
with binding.to(EquationSystem):
    @binding
    @format_docstring(paramdocs=_componentize_paramdocs)
    def componentize(self, basis=None, shorthand=None, unsolved_only=True, _eff=True, **kw):
        '''returns self written in basis.
        result will have vectors rewritten as a sum of components in basis.
        each vector-valued equation will also be expanded into its components in basis.
        otherwise, returns EquationSystem containing only result (i.e. only 1 equation).

        {paramdocs}
        unsolved_only: bool, default True
            True --> only componentize equations in self which are not marked as solved.
            False --> componentize all equations in self.
        _eff: bool, default True
            [EFF] whether to use _component_from_componentized() when getting components for vector-valued equations.
            Optional because it may be more or less efficient depending on the equations involved.
            efficiency not yet benchmarked.
            Note: if _eff=False, try doing result.simplify_basis_ids() afterwards.

        if no equations in self are affected by this operation, returns self, exactly.
        '''
        basis = _default_basis_if_None(basis)
        result_eqs = []
        changed_any = False
        for eq in self:
            if unsolved_only and eq.solved:  # skip already-solved equation
                result_eqs.append(eq)
            else:
                componentized = eq.componentize(basis, _eff=_eff, shorthand=shorthand, **kw)  # has 1 or len(basis) equations.
                if not changed_any:  # check if anything changed
                    if not ((len(componentized)==1) and (componentized[0] is eq)):
                        changed_any = True
                for component_eq in componentized:
                    result_eqs.append(component_eq)
        if not changed_any:
            return self  # return self, exactly, to help indicate nothing was changed.
        else:
            return self._new(*result_eqs)


''' --------------------- [EFF] _component_from_componentized --------------------- '''
# "get component of componentized value" is a "common" problem.
# might be more efficient to do separate methods for it, rather than always get all the components to start.
# This is also the "more inuitive" way to get components.
#   E.g., components of u = v, with basis=(xhat, yhat), shorthand=True...
#   Using the methods in this section, it looks like:
#       we can go straight to the result:
#           {ux xhat = vx xhat; uy yhat = vy yhat}.
#       That's also what you might do, "by hand".
#   Meanwhile, using the "componentize then get single component" method, it would look like:
#       first, componentize: ux xhat + uy yhat = vx xhat + vy yhat
#       then, get components:
#           {(ux xhat + uy yhat) dot xhat = (vx xhat + vy yhat) dot xhat,
#           (ux xhat + uy yhat) dot yhat = (vx xhat + vy yhat) dot yhat}
#       then, if you apply to that result, result.simplify_basis_ids(), you will recover:
#           {ux xhat = vx xhat; uy yhat = vy yhat}.

# note: we assume all vectors have the _component_from_componentized method.

# # # DEFAULT COMPONENT FROM COMPONENTIZED -- return component after doing componentize # # #
with binding.to(IterableSymbolicObject):
    @binding
    def _component_from_componentized(self, xhat, basis=None, shorthand=None, **kw):
        '''return self.componentize(basis, shorthand, **kw).component(xhat, shorthand, **kw).
        [EFF] may be more efficient than calling those things directly,
            because subclasses can override this method to only get all the vector components when necessary.
        '''
        componentized = self.componentize(basis=basis, shorthand=shorthand, **kw)
        component = componentized.component(xhat, shorthand=shorthand, **kw)
        return component

# # # SUM COMPONENT FROM COMPONENTIZED -- return component from componentized for each summand # # #
with binding.to(Sum):
    @binding
    def _component_from_componentized(self, xhat, basis=None, shorthand=None, **kw):
        '''return xhat component from self.componentize().
        [EFF] may be more efficient than self.componentize().component(xhat),
            because it sometimes doesn't fully expand vectors.
        '''
        if not is_vector(self):
            raise VectorialityError(f"Can't get component of a scalar: {self}")
        summands_component = []
        for summand in self:
            # assume summand has this method because each summand must be a vector,
            # so it should be an IterableSymbolicObject or a Symbol.
            # this is in a for-loop instead of list comprehension for easier debugging in case of crash.
            component = summand._component_from_componentized(xhat, basis=basis, shorthand=shorthand, **kw)
            summands_component.append(component)
        return self._new(*summands_component)

# # # PRODUCT COMPONENT FROM COMPONENTIZED -- componentize scalars; component from componentized vector # # #
with binding.to(Product):
    @binding
    def _component_from_componentized(self, xhat, basis=None, shorthand=None, **kw):
        '''return xhat component from self.componentize().
        [EFF] may be more efficient than self.componentize().component(xhat),
            because it sometimes doesn't fully expand vectors.
        '''
        sfs, vfs = scalar_vector_get_factors(self, vector_if_None=False)
        if not len(vfs)==1:
            if len(vfs)==0:
                raise VectorialityError('Cannot get component of Product without a vector factor.')
            else:
                raise NotImplementedError('Component from product with more than 1 vector factor.')
        vf = vfs[0]
        vf_component = vf._component_from_componentized(xhat, basis=basis, shorthand=shorthand, **kw)
        sfs_componentized = tuple(componentize(sf, basis=basis, shorthand=shorthand, **kw) for sf in sfs)
        return self._new(*sfs_componentized, vf_component)

# # # SYMBOL COMPONENT FROM COMPONENTIZED -- return Symbol component # # #
with binding.to(Symbol):
    @binding
    def _component_from_componentized(self, xhat, basis=None, shorthand=None, **kw__None):
        '''return xhat component from self.componentize(). I.e., returns self.component(xhat).
        First, ensures that xhat is in basis.

        [EFF] This function is an implementation detail to improve efficiency.
            It fits into the _component_from_componentized architecture implemented for other objects,
            like Sum and Product, which make this operation more efficient when only 1 component is desired.
            (And possibly more efficient even when multiple are desired.)
            However, it is silly to call directly from Symbol; just use self.component instead.
        '''
        basis = _default_basis_if_None(basis)
        if xhat not in basis:
            raise ComponentPatternError(f'xhat not in basis! xhat={xhat}; basis={basis}')
        else:
            return self.component(xhat, shorthand=shorthand)

# # # EQUATION COMPONENT FROM COMPONENTIZED -- return component from componentize for each side # # #
with binding.to(Equation):
    @binding
    def _component_from_componentized(self, xhat, basis=None, shorthand=None, **kw):
        '''return component from self.componentize().
        [EFF] may be more efficient than self.componentize().component(xhat),
            because it sometimes doesn't fully expand vectors.
        '''
        if not is_vector(self):
            raise VectorialityError(f"Can't get component of a scalar-valued equation: {self}")
        sides_component = []
        for side in self:
            # assume each side has this method because each side must be a vector,
            # so it should be an IterableSymbolicObject or a Symbol.
            # this is in a for-loop instead of list comprehension for easier debugging in case of crash.
            component = side._component_from_componentized(xhat, basis=basis, shorthand=shorthand, **kw)
            sides_component.append(component)
        return self._new(*sides_component)


''' --------------------- COMPONENTS COUNT --------------------- '''

# # # DEFAULT COMPONENTS COUNT -- 1 for scalars; ndim for vectors. # # #
with binding.to(SymbolicObject):
    @binding
    @format_docstring(paramdocs=indent(_components_count_paramdocs, ' '*4))
    def components_count(self, ndim=None, basis=None):
        '''counts number of vector components of self, given the number of dimensions in a vector.
        result = 1 for scalars; ndim for vectors.
        
        {paramdocs}
        '''
        if is_vector(self):
            ndim = _default_ndim_if_None(ndim, basis=basis)
            return ndim
        else:
            return 1

# # # EQUATION SYSTEM COMPONENTS COUNT -- sum of components count for each equation # # #
with binding.to(EquationSystem):
    @binding
    @format_docstring(paramdocs=indent(_components_count_paramdocs, ' '*4))
    def components_count(self, ndim=None, basis=None):
        '''counts number of vector components of self, given the number of dimensions in a vector.
        result = sum(eqn.components_count() for eqn in self)
        
        {paramdocs}
        '''
        return builtins.sum(eqn.components_count(ndim=ndim, basis=basis) for eqn in self)