"""
File Purpose: Basis
also, getting components from vectors.

Note: Basis breaks the "SymSolver objects are immutable" design principle,
    in that it works by "telling" its contents that they are basis vectors,
    e.g. by adjusting x._basis_appearances.
For this reason, it is recommended that if Basis is involved in your math,
    >> put objects in the Basis BEFORE using the objects anywhere. <<

[TODO] should references back to Basis be weakrefs?
[TODO][EFF][maybe] skip all basis-related simplifications until at least 1 Basis object has been created.
"""

from .binary_vector_products import BinaryVectorProduct
from .cross_product import CrossProduct
from .dot_product import DotProduct
from .box_product import BoxProduct
from .vectors_tools import (
    is_vector, is_unit_vector,
    scalar_vector_get_factors,
)
from ..attributors import attributor
from ..abstracts import (
    SymbolicObject, IterableSymbolicObject,
    SimplifiableObject,
    simplify_op,
    get_symbols,
)
from ..basics import (
    get_summands,
)
from ..errors import (
    VectorPatternError, VectorialityError,
    BasisNotFoundError, MetricUndefinedError,
    InputMissingError,
)
from ..initializers import initializer
from ..tools import (
    apply, _repr,
    equals,
    StoredInstances,
    caching_attr_simple,
    Binding, format_docstring,
)
from ..defaults import ONE, ZERO

binding = Binding(locals())


''' --------------------- Convenience - Appearance in Basis(es) --------------------- '''

# # # GET BASIS APPEARANCES # # #
def get_basis_appearances(x):
    '''returns [(basis, x index in basis) for each Basis basis containing x].
    if possible, just returns x._basis_appearances, since this info is stored there.
    otherwise, return [].
    '''
    try:
        return x._basis_appearances
    except AttributeError:
        return []

def _get_basistype_appearances(x, basis_type):
    '''returns (basis, x index in basis) for each basis_type basis containing x.
    basis_type: type
        only include (basis, x index in basis) in the result if isinstance(basis, basis_type)
    '''
    return [(basis, i) for (basis, i) in get_basis_appearances(x) if isinstance(basis, basis_type)]

def get_orthonormal_basis_appearances(x):
    '''returns (basis, x index in basis) for each OrthonormalBasis containing x.'''
    return _get_basistype_appearances(x, OrthonormalBasis)

def get_orthonormal_basis_3d_appearances(x):
    '''returns (basis, x index in basis) for each OrthonormalBasis3D containing x.'''
    return _get_basistype_appearances(x, OrthonormalBasis3D)

# # # IS BASIS VECTOR # # #
def _is_basistype_vector(x, basis_type):
    '''returns whether x appears in a basis_type basis,
    i.e. len(_get_basis_type_appearances(x, basis_type)) > 0.
    '''
    return len(_get_basistype_appearances(x, basis_type)) > 0

def is_basis_vector(x):
    '''returns whether x appears in any Basis.'''
    return _is_basistype_vector(x, Basis)

def is_orthonormal_basis_vector(x):
    '''returns whether x appears in any OrthonormalBasis'''
    return _is_basistype_vector(x, OrthonormalBasis)

def is_orthonormal_basis_3d_vector(x):
    '''returns whether x appears in any OrthonormalBasis3D'''
    return _is_basistype_vector(x, OrthonormalBasis3D)

# # # SHARED BASIS THEN INDICES # # #
def _shared_basistype_then_indices(x, y, basis_type):
    '''returns (basis, (x index in basis, y index in basis)) for a basis_type basis containing x and y.
    if multiple such basis objects exist, return the oldest (i.e. first-created) one containing x.
    raise BasisNotFoundError if this task is impossible.

    basis_type: type
        only consider basis objects for which isinstance(basis, basis_type)
    '''
    x_ba = _get_basistype_appearances(x, basis_type)
    if len(x_ba) > 0:  # [EFF] for efficiency, stop here if x appears in no basis_type basis objects.
        y_ba = _get_basistype_appearances(y, basis_type)
        if len(y_ba) > 0:  # [EFF] for efficiency, stop here if y appears in no basis_type basis objects.
            for xbasis, xi in x_ba:
                for ybasis, yi in y_ba:
                    if equals(xbasis, ybasis):
                        return (xbasis, (xi, yi))
    raise BasisNotFoundError(f'no shared {basis_type.__name__} basis for {x} and {y}')

def shared_basis_then_indices(x, y):
    '''returns (basis, (x index in basis, y index in basis)) for a Basis basis containing x and y.
    if multiple such basis objects exist, return the oldest (i.e. first-created) one containing x.
    raise BasisNotFoundError if this task is impossible.
    '''
    return _shared_basistype_then_indices(x, y, Basis)

def shared_orthonormal_basis_then_indices(x, y):
    '''returns (basis, (x index in basis, y index in basis)) for an OrthonormalBasis basis containing x and y.
    if multiple such basis objects exist, return the oldest (i.e. first-created) one containing x.
    raise BasisNotFoundError if this task is impossible.
    '''
    return _shared_basistype_then_indices(x, y, OrthonormalBasis)

def shared_orthonormal_basis_3d_then_indices(x, y):
    '''returns (basis, (x index in basis, y index in basis)) for an OrthonormalBasis3D basis containing x and y.
    if multiple such basis objects exist, return the oldest (i.e. first-created) one containing x.
    raise BasisNotFoundError if this task is impossible.
    '''
    return _shared_basistype_then_indices(x, y, OrthonormalBasis3D)


''' --------------------- Attach _basis_appearances to SymbolicObject --------------------- '''

def _symbolic_object_get_basis_appearances(x):
    '''gets basis appearances from x.
    returns x._basis_appearances_data if it exists.
    Otherwise, sets x._basis_appearances_data = [], then returns it.
    '''
    try:
        return x._basis_appearances_data
    except AttributeError:
        x._basis_appearances_data = []
        return x._basis_appearances_data

SymbolicObject._basis_appearances = property(
    _symbolic_object_get_basis_appearances,
    lambda self, value: setattr(self, '_basis_appearances_data', value),
    doc='''list of (basis, position in basis) tuples, one for each basis containing this SymbolicObject.''',
)


''' --------------------- Basis --------------------- '''

class Basis(IterableSymbolicObject):
    '''ordered list of basis vectors.
    if not _basis_assign, self._basis_assign_vectors() should be called later,
        or else the vectors won't know they are part of a Basis.
    '''
    def __init__(self, *terms, _basis_assign=True, **kw):
        if not all(is_vector(v) for v in terms):
            raise VectorialityError('All terms in a Basis must be vectors.')
        super().__init__(*terms, **kw)
        self._init_basis_assigned = False
        if _basis_assign:
            self._init_basis_assign_vectors()
        
    def _init_basis_assign_vectors(self):
        '''tell each vector that it is part of basis self, and its position in self.
        then sets self._init_basis_assigned = True.
        '''
        for i, vector in enumerate(self.terms):
            self._basis_assign(vector, i)
        self._init_basis_assigned = True

    def _basis_assign(self, v, i=None):
        '''tells v that it is the i'th basis vector in basis self.'''
        v._basis_appearances.append((self, i))

    def _repr_contents(self, **kw):
        '''returns contents to put inside 'Basis' in repr for self.'''
        return [_repr(v, **kw) for v in self.terms]


''' --------------------- OrthonormalBasis --------------------- '''

_metric_paramdoc = \
    '''metric: None or iterable (but not an iterator)
        The diagonal of the metric tensor for this basis.
        (Other elements of the metric tensor are 0 since the basis is Orthogonal.)
        None --> Any code requiring use of this metric should raise a MetricUndefinedError.
        Example: for (xhat, yhat, zhat) Cartesian coordinates, use metric = (1,1,1).'''

@format_docstring(_metric_paramdoc=_metric_paramdoc)
class OrthonormalBasis(Basis):
    '''ordered list of mutually orthonormal basis vectors.
    {_metric_paramdoc}
    '''
    def __init__(self, *terms, metric=None, **kw):
        if not all(is_unit_vector(v) for v in terms):
            raise VectorPatternError('All terms in OrthonormalBasis must be unit vectors.')
        self._metric = metric
        super().__init__(*terms, **kw)

    metric = property(lambda self: self._metric,
        doc='''The diagonal of the metric tensor for this basis, or None if unknown.
        Any code requiring a metric but seeing metric=None should raise MetricUndefinedError.''')

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another instance of type(self) to be like self,
        via self._new(*args, **kw). Note these will be overwritten in _new by any **kw entered.
        '''
        kw = super()._init_properties()
        kw['metric'] = self.metric
        return 

    def __eq__(self, b):
        '''return self==b'''
        if not super().__eq__(b):
            return False
        if not equals(self.metric, b.metric):
            return False
        return True

    @caching_attr_simple
    def __hash__(self):
        return hash((super().__hash__(), self.metric))

    def _i_dot_j(self, i, j):
        '''evaluate dot product between i'th and j'th basis vectors from self.
        returns 1 if i==j, else 0.
        '''
        return ONE if i==j else ZERO

    def _repr_contents(self, **kw):
        '''returns contents to put inside 'OrthonormalBasis' in repr for self.'''
        contents = super()._repr_contents(**kw)
        metric = self.metric
        if metric is not None:
            contents.append(f'metric={metric}')
        return contents


''' --------------------- OrthonormalBasis3D --------------------- '''

# lookup for OrthonormalBasis3D._i_cross_j_to_neg_and_k method.
_I_CROSS_J_TO_NEG_AND_K = {
#   (i, j) : (neg, k)
    (0, 1) : (False, 2),  # basis[0] x basis[1] == basis[2]
    (0, 2) : ( True, 1),  # basis[0] x basis[2] == - basis[1]
    (1, 2) : (False, 0),
    (1, 0) : ( True, 2),
    (2, 0) : (False, 1),
    (2, 1) : ( True, 0),
}

@format_docstring(_metric_paramdoc=_metric_paramdoc)
class OrthonormalBasis3D(OrthonormalBasis):
    '''ordered list of precisely 3 mutually orthonormal basis vectors.
    {_metric_paramdoc}
    '''
    def __init__(self, xhat, yhat, zhat, metric=None, **kw):
        super().__init__(xhat, yhat, zhat, metric=metric, **kw)

    xhat = property(lambda self: self.terms[0], doc='''the first basis vector, e.g. xhat in (xhat, yhat, zhat)''')
    yhat = property(lambda self: self.terms[1], doc='''the first basis vector, e.g. yhat in (xhat, yhat, zhat)''')
    zhat = property(lambda self: self.terms[2], doc='''the first basis vector, e.g. zhat in (xhat, yhat, zhat)''')

    @staticmethod
    def _i_cross_j_to_neg_and_k(i, j):
        '''returns (neg, k) such that (-1 if neg else 1) * self[k] = self[i] cross self[j].
        returns (None, None) if self[i] cross self[j] = 0.
        '''
        if i == j:
            return (None, None)
        else:
            return _I_CROSS_J_TO_NEG_AND_K[(i, j)]

    def _i_cross_j(self, i, j):
        '''evaluate cross product between i'th and j'th basis vectors from self.'''
        neg, k = OrthonormalBasis3D._i_cross_j_to_neg_and_k(i, j)
        if k is None:  # i == j
            return ZERO
        if neg:
            return -self.terms[k]
        else:
            return self.terms[k]


''' --------------------- Initialize a Basis object --------------------- '''
# BASISES stores all the basis objects ever created.
# the idea is that when about to creating a new Basis which equals one in here,
#   instead return the already-existing Basis from in here.
# [TODO] just like for SYMBOLS, should replace __eq__ in Basis with a check for 'is',
#   but use the current __eq__ implementation only when creating a new basis.

BASISES = StoredInstances(Basis)

@initializer
def basis(*basis_vectors, orthonormal=True, force_3d=False, metric=None, **kw):
    '''return a Basis object containing these basis_vectors.
    if the specified Basis already exists, return it. Otherwise create a new one.

    basis_vectors: vector Symbol objects
        the vectors which form the basis.
    orthonormal: bool, default True
        whether to treat the vectors as orthonormal.
        if True and the vectors are not all unit vectors, raise VectorPatternError.
    force_3d: bool, default False
        if True, enforce that there are 3 basis vectors, else raise TypeError.
    metric: None or iterable (but not an iterator)
        None --> any code requiring use of this metric should raise a MetricUndefinedError.
        else --> if orthonormal=True, metric=the diagonal of the metric tensor for this basis.
                 else (orthonormal=False, metric is not None), raise NotImplementedError.
    **kw are passed to class's __init__ e.g. Basis.__init__(..., **kw)

    returns:
        an OrthonormalBasis3D if there are 3 basis vectors and orthonormal=True,
        else an OrthonormalBasis if orthonormal=True,
        else a Basis.
    '''
    len3 = (len(basis_vectors) == 3)
    if force_3d and not len3:
        raise TypeError(f'got {len(basis_vectors)} basis vectors but expected 3, since force_3d=True.')
    if orthonormal:
        if not all(is_unit_vector(v) for v in basis_vectors):
            errmsg = ('cannot include non-unit-vector when creating OrthonormalBasis. '
                      'Try using different vectors (e.g. Symbols with hat=True), '
                      'or use basis(..., orthonormal=False) to create a non-orthonormal Basis.')
            raise VectorPatternError(errmsg)
        creator = OrthonormalBasis3D if len3 else OrthonormalBasis
        kw['metric'] = metric  # << put metric into kw; Basis doesn't (yet) accept a metric kw.
    else:
        if metric is not None:
            raise NotImplementedError('non-None metric for non-Orthogonal basis')
        creator = Basis
    result = BASISES.get_new_or_existing_instance(creator, *basis_vectors, _basis_assign=False, **kw)
    if not result._init_basis_assigned:
        result._init_basis_assign_vectors()
    return result


''' --------------------- BinaryVectorProduct attachments --------------------- '''

with binding.to(BinaryVectorProduct):
    # # # HELPER METHODS FOR SIMPLIFICATION OPS # # #
    @binding
    def _get_scalar_factors_and_basis_vectors(self, basis_type=Basis):
        '''returns ((sf_t1, bv1), (sf_t2, bv2)), where:
            sf_t1 = scalar factors of self.t1,
            sf_t2 = scalar factors of self.t2,
            bv1 = basis_type basis_vector in self.t1,
            bv2 = basis_type basis_vector in self.t2,

        basis_type: type, default Basis
            enforce isinstance(bv1, basis_type) and isinstance(bv2, basis_type).

        raise BasisNotFoundError if this task is impossible.
        '''
        sf_t1, vf_t1 = scalar_vector_get_factors(self.t1)
        v1 = vf_t1[0]
        if not _is_basistype_vector(v1, basis_type):
            raise BasisNotFoundError(f'first factor does not contain a {basis_type.__name__} basis vector: {self}')
        sf_t2, vf_t2 = scalar_vector_get_factors(self.t2)
        v2 = vf_t2[0]
        if not _is_basistype_vector(v2, basis_type):
            raise BasisNotFoundError(f'second factor does not contain a {basis_type.__name__} basis vector: {self}')
        return ((sf_t1, v1), (sf_t2, v2))

    @binding
    def _get_scalar_factors_then_basis_then_indices(self, basis_type=Basis):
        '''returns ((sf_t1, sf_t2), basis, (i_bv1, i_bv2)), where:
            sf_t1 = scalar factors of self.t1,
            sf_t2 = scalar factors of self.t2,
            basis = basis shared by the vector factors in self.t1 and self.t2
            i_bv1 = index in basis of the basis_vector from self.t1
            i_bv2 = index in basis of the basis_vector from self.t2
        if multiple such basis objects exist, use the oldest one containing the vector factor in self.t1.

        basis_type: type, default Basis
            enforce isinstance(bv1, basis_type) and isinstance(bv2, basis_type).

        raise BasisNotFoundError if this task is impossible.
        '''
        (sf_t1, bv1), (sf_t2, bv2) = self._get_scalar_factors_and_basis_vectors(basis_type=basis_type)
        basis, (i_bv1, i_bv2) = _shared_basistype_then_indices(bv1, bv2, basis_type=basis_type)
        return ((sf_t1, sf_t2), basis, (i_bv1, i_bv2))


''' --------------------- Basis-Related Simplifications for Dot and Cross --------------------- '''

@simplify_op(DotProduct, alias='_basis_id')
def _dot_product_basis_id(self, **kw__None):
    '''simplifies dot products between basis vectors in self.'''
    try:
        (sf_t1, sf_t2), basis, (i_bv1, i_bv2) = \
                self._get_scalar_factors_then_basis_then_indices(basis_type=OrthonormalBasis)
    except BasisNotFoundError:
        return self  # return self, exactly, to help indicate nothing was changed.
    else: # successfully got scalar factors, a common OrthonormalBasis basis, and vectors' indices in that basis.
        dot_bvs = basis._i_dot_j(i_bv1, i_bv2)
        if dot_bvs is ONE:
            return self.product(*sf_t1, *sf_t2) # * 1. But for efficiency we don't include that '* 1'.
        elif dot_bvs is ZERO:
            return ZERO
        else:
            raise NotImplementedError('_i_dot_j giving something besides 0 or 1 in _dot_product_basis_id')

@simplify_op(CrossProduct, alias='_basis_id')
def _cross_product_basis_id(self, **kw__None):
    '''simplifies cross products between basis vectors in self.'''
    try:
        (sf_t1, sf_t2), basis, (i_bv1, i_bv2) = \
                self._get_scalar_factors_then_basis_then_indices(basis_type=OrthonormalBasis3D)
    except BasisNotFoundError:
        return self  # return self, exactly, to help indicate nothing was changed.
    else: # successfully got scalar factors, a common OrthonormalBasis3D basis, and vectors' indices in that basis.
        cross_bvs = basis._i_cross_j(i_bv1, i_bv2)
        if cross_bvs is ZERO:
            return ZERO
        else:
            return self.product(*sf_t1, *sf_t2, cross_bvs)

@simplify_op(BinaryVectorProduct, aliases=('_distribute_basis_id', '_simplifying_distribute'))
def _binary_vector_product_distribute_basis_id(self, **kw__basis_id):
    '''distributes in order to simplify basis ids hidden by distributive property.
    only distributes if self[0] and self[1] both contain OrthonormalBasis basis vectors.
        if distributing leads to no changes, returns self, unchanged (e.g. self[0] and self[1] were not Sums)
        otherwise, then applies _basis_id when possible to each summand in result of distributing.
    [TODO] do we need to also attempt _cycle_basis_id? Or will such cases always be handled just via simplify()?
    '''
    def _contains_basis_vector(obj):
        return any(is_orthonormal_basis_vector(s) for s in get_symbols(obj))
    if not _contains_basis_vector(self.t1) or not _contains_basis_vector(self.t2):
        return self  # return self, exactly, to help indicate nothing was changed.
    distributed = self._abstract_product_distribute(distribute_sum_if=_contains_basis_vector)
    if distributed is self:  # distributing accomplished nothing
        return self  # return self, exactly, to help indicate nothing was changed.
    # else: apply basis_id, because basis vectors exist and distributing accomplished something.
    summands = get_summands(distributed)
    if len(summands) == 1:
        return self  # return self, exactly, to help indicate nothing was changed.
    new_summands = []
    simplified_any_summands = False
    for summand in summands:
        try:  # try to apply _basis_id
            new_summand = summand._basis_id(**kw__basis_id)
        except AttributeError:
            new_summand = summand
        else:
            if new_summand is summand:
                new_summand = summand
            else:
                simplified_any_summands = True
        new_summands.append(new_summand)
    if not simplified_any_summands:
        return self  # return self, exactly, to help indicate nothing was changed.
    return self.sum(*new_summands)

@simplify_op(BoxProduct, alias='_cycle_basis_id')
def _box_product_cycle_basis_id(self, **kw__basis_id):
    '''simplify any basis ids in self, even if they are hidden due to the way self is currently written.
    (As a BoxProduct, self can be rewritten using the identity: A.(BxC) == B.(CxA) == C.(AxB))
    For example, yhat dot (u cross xhat) --> u dot (xhat cross yhat) --> u dot zhat,
        (this example assumes (xhat, yhat, zhat) form an OrthonormalBasis3D.)

    implementation note [EFF]:
        since we can only simplify here via _cross_product_basis_id,
        which itself can only simplify when OrthonormalBasis3D basis vectors are involved,
        if self._A is not an OrthonormalBasis3D basis vector, there is nothing to simplify.
    '''
    if not is_orthonormal_basis_3d_vector(self._A):
        return self  # return self, exactly, to help indicate nothing was changed.
    # first, simplify self._B_cross_C via basis_id, if possible.
    new_B_cross_C = self._B_cross_C._cross_product_basis_id(**kw__basis_id)
    if new_B_cross_C is not self._B_cross_C:  # basis id in B cross C did something
        return self._new(self._A, new_B_cross_C)
    # next, check other possibilities. first B.(CxA), then C.(AxB)
    for cycle_name in ('cycle_BCA', 'cycle_CAB'):
        cycled = getattr(self, cycle_name)()  # () calls the attribute which returns the cycled result.
        cycled_new_B_cross_C = cycled._B_cross_C._cross_product_basis_id(**kw__basis_id)
        if cycled_new_B_cross_C is not cycled._B_cross_C:  # basis id did something
            return cycled._new(cycled._A, cycled_new_B_cross_C)
    # if we didn't return by now, give up (we've tried everything already).
    return self  # return self, exactly, to help indicate nothing was changed.


''' --------------------- "PERFORM ALL" Basis-Related Simplifications --------------------- '''

with binding.to(SimplifiableObject):
    @binding
    def _simplify_basis_ids(self, **kw):
        '''applies all basis_id-related simplifications at top layer of self.'''
        self = apply(self, '_distribute_basis_id', **kw)
        self = apply(self, '_cycle_basis_id', **kw)
        self = apply(self, '_basis_id', **kw)
        return self

    @binding
    def simplify_basis_ids(self, **kw):
        '''applies all basis_id-related simplifications at all layers of self.'''
        return self.apply('_simplify_basis_id')