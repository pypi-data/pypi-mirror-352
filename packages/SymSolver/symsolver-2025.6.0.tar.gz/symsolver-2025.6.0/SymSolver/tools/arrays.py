"""
File Purpose: numpy arrays
"""

import collections

from .imports import ImportFailed
try:
    import numpy as np
except ImportError as err:
    np = ImportFailed('numpy', err=err)

from .iterables import is_iterable
from .pytools import format_docstring
from ..errors import InputMissingError, InputConflictError, DimensionalityError


''' ----------------------------- Iteration ----------------------------- '''

def itarrayte(arr, skip_masked=True):
    '''yields (array element, multi_index of that element)
    multi_index of x is the N-tuple such that arr[multi_index] == x.

    skip_masked: bool
        if True, and arr is a masked array, skip all masked points.
    '''
    it = np.nditer(arr, flags=['multi_index', 'refs_ok'])
    if np.ma.isMaskedArray(arr) and skip_masked:
        for x in it:
            if arr.mask[it.multi_index]:
                yield (x[()], it.multi_index)
    else:
        for x in it:
            yield (x[()], it.multi_index)

iter_array = itarrayte  # alias

ObjArrayInfo = collections.namedtuple('ObjArrayInfo', ['type_of_item_0', 'shape'])
NumArrayInfo = collections.namedtuple('NumArrayInfo', ['min', 'mean', 'max', 'shape'])

def array_expand_elements(arr, allow_non_iterable=False, **kw__array):
    '''expands elements from arr, an array of iterables which all have the same length.
    allow_non_iterable: bool, default False
        whether to return arr (as opposed to crashing) if elements of arr are non-iterable
    .'''
    arr_orig = arr
    arr = np.asanyarray(arr)
    # get elem0, check if iterable, determine shape.
    elem0 = next(itarrayte(arr))[0]
    try:
        L = len(elem0)
    except TypeError:
        if allow_non_iterable:
            return arr
        else:
            raise
    result = np.empty_like(arr, shape=(*arr.shape, L))
    # loop through arr and set values in result.
    for _, idx in itarrayte(arr):
        result[idx] = arr[idx]
    return result


''' ----------------------------- Slicing ----------------------------- '''

_indexer_docs = '''indexer: slice, int, or tuple of ints.
        slice or integer  --> use indexer directly.
        tuple of integers --> use slice(*indexer). E.g. (3,7,2) --> slice(3,7,2)'''

_ndim_and_arr_docs = '''ndim: positive integer, or None.
        number of dimensions of array that will be indexed.
        None --> use arr to determine ndim.
        Required if ax < 0.
    arr: array, or None.
        array that will be indexed (or an array with same number of dimensions).
        if not None, use arr to calculate ndim via np.ndim(arr).'''

@format_docstring(kwargdocs=_ndim_and_arr_docs)
def ax_to_abs_ax(ax, ndim=None, *, arr=None):
    '''get positive ax index for an array with ndim dimensions.
    ax: integer
        axis index. Can be negative if ndim or arr is also provided.
    {kwargdocs}
    
    returns ax as a positive index.
    '''
    if ax >= 0:
        return ax
    # else, setup:
    if ndim is None:
        if arr is None:
            raise InputMissingError(f'must provide ndim or arr when ax<0. Got ax={ax}.')
        else:
            ndim = np.ndim(arr)
    else:
        if arr is not None:
            raise InputConflictError(f"Provide only one of (arr, ndim); not both.")
    # calculation & result
    return range(ndim)[ax]

@format_docstring(argdocs=_indexer_docs, kwargdocs=_ndim_and_arr_docs)
def slicer_at_ax(indexer, ax, *, ndim=None, arr=None):
    '''return tuple of slices which, when applied to an array, indexes along axis number <ax>.

    {argdocs}
    axis: int
        axis at which to apply the indexing.
        Can be negative if ndim or arr is also provided.
    {kwargdocs}
    '''
    try:
        indexer[0]
    except TypeError: #indexer is a slice or an integer.
        pass  
    else: #assume indexer is a tuple of integers.
        indexer = slice(*indexer)
    return (slice(None),)*ax + (indexer,)

@format_docstring(argdocs=_indexer_docs)
def slice_at_ax(arr, indexer, ax):
    '''slice arr (a numpy array) by applying indexer at axis number <ax>.

    See also: np.take().
        However; slicing creates a view, while np.take always copies data,
        so slicing may be the better option in many cases.

    {argdocs}
    axis: int
        axis at which to apply the indexing. (Negative values *are* supported here.)
    '''
    ax = ax_to_abs_ax(ax, arr=arr)
    slicer = slicer_at_ax(indexer, ax)
    return arr[slicer]


''' ----------------------------- Stats ----------------------------- '''

def stats(arr):
    '''return dict with min, mean, max.'''
    return dict(min=np.nanmin(arr), mean=np.nanmean(arr), max=np.nanmax(arr))

def array_info(arr):
    '''returns namedtuple of min, mean, max, shape.'''
    x = np.asarray(arr)
    if x.ndim == 0  or  x.size == 0:
        return arr   # return original input; it is easy to display.
    elif x.dtype == 'object':
        return ObjArrayInfo(x.dtype, x.shape)
    else:
        return NumArrayInfo(x.min(), x.mean(), x.max(), x.shape)

def array_info_str(arr):
    '''returns string with info about arr's type, and array_info.
    if len(arr) gives a TypeError, just return repr(arr) instead.
    '''
    ai = array_info(arr)
    if ai is arr:
        return repr(arr)
    else:
        return '{}; {}'.format(type(arr), ai)


''' ----------------------------- Simple Min / Max ----------------------------- '''

# TOOD: encapsulate this code better (avoid repetition between min and max).
def array_max(arrays, key=lambda arr: arr):
    '''returns an array containing max in each index according to key:
        result[idx] == max(key(array)[0][idx], ..., key(array)[n][idx])

    arrays: list or numpy array
        list --> a list of numpy arrays with the same shape
        numpy array --> treat the first dimension as the "list" dimension.
            e.g. shape (7, 3, 4) implies 7 arrays of shape (3, 4).
    '''
    arrays = np.asarray(np.broadcast_arrays(*arrays, subok=True))
    values = np.asarray([key(array) for array in arrays])
    argmax = np.nanargmax(values, axis=0)
    result = np.take_along_axis(arrays, np.expand_dims(argmax, 0), 0)    # shape here is (1, <shape of arrays[0]>)
    return result[0]

def array_min(arrays, key=lambda arr: arr):
    '''returns an array containing min in each index according to key:
        result[idx] == min(key(array)[0][idx], ..., key(array)[n][idx])

    arrays: list or numpy array
        list --> a list of numpy arrays with the same shape
        numpy array --> treat the first dimension as the "list" dimension.
            e.g. shape (7, 3, 4) implies 7 arrays of shape (3, 4).
    '''
    arrays = np.asarray(np.broadcast_arrays(*arrays, subok=True))
    values = np.asarray([key(array) for array in arrays])
    argmin = np.nanargmin(values, axis=0)
    result = np.take_along_axis(arrays, np.expand_dims(argmin, 0), 0)    # shape here is (1, <shape of arrays[0]>)
    return result[0]

def array_argmax(arr, **kw):
    '''unraveled argmax. **kw are passed to nanargmax.'''
    arr = np.asanyarray(arr)
    idx = np.nanargmax(arr, **kw)
    result = np.unravel_index(idx, arr.shape)
    return result

def array_argmin(arr, **kw):
    '''unraveled argmin. **kw are passed to nanargmin.'''
    arr = np.asanyarray(arr)
    idx = np.nanargmin(arr, **kw)
    result = np.unravel_index(idx, arr.shape)
    return result


''' ----------------------------- Take Min / Max Along Axis ----------------------------- '''

def _take_indices_along_ax(arr, indices, axis=-1, keepdims=False):
    '''takes indices along axis of array. If keepdims, return immediately, otherwise remove axis afterwards.'''
    result = np.take_along_axis(arr, np.expand_dims(indices, axis=axis), axis=axis)
    if keepdims:
        return result
    else:
        return slice_at_ax(arr, 0, ax=axis)

def array_select_max_imag(arr, axis=-1, keepdims=False):
    '''selects maximum imaginary part along axis of array arr.
    result = np.take_along_axis(arr, np.expand_dims(np.argmax(np.imag(arr), axis=axis), axis=axis), axis=axis).
    if keepdims, return immediately; otherwise remove axis (e.g. result[...,0] if axis=-1).
    '''
    indices = np.argmax(np.imag(arr), axis=axis)
    return _take_indices_along_ax(arr, indices, axis=axis, keepdims=keepdims)

def array_select_min_imag(arr, axis=-1, keepdims=False):
    '''selects minimum imaginary part along axis of array arr.
    result = np.take_along_axis(arr, np.expand_dims(np.argin(np.imag(arr), axis=axis), axis=axis), axis=axis).
    if keepdims, return immediately; otherwise remove axis (e.g. result[...,0] if axis=-1).
    '''
    indices = np.argmin(np.imag(arr), axis=axis)
    return _take_indices_along_ax(arr, indices, axis=axis, keepdims=keepdims)

def array_select_max_real(arr, axis=-1, keepdims=False):
    '''selects maximum real part along axis of array arr.
    result = np.take_along_axis(arr, np.expand_dims(np.argmax(np.real(arr), axis=axis), axis=axis), axis=axis).
    if keepdims, return immediately; otherwise remove axis (e.g. result[...,0] if axis=-1).
    '''
    indices = np.argmax(np.real(arr), axis=axis)
    return _take_indices_along_ax(arr, indices, axis=axis, keepdims=keepdims)

def array_select_min_real(arr, axis=-1, keepdims=False):
    '''selects minimum real part along axis of array arr.
    result = np.take_along_axis(arr, np.expand_dims(np.argin(np.real(arr), axis=axis), axis=axis), axis=axis).
    if keepdims, return immediately; otherwise remove axis (e.g. result[...,0] if axis=-1).
    '''
    indices = np.argmin(np.real(arr), axis=axis)
    return _take_indices_along_ax(arr, indices, axis=axis, keepdims=keepdims)



''' --------------------- array from nested list --------------------- '''

def looks_flat(x):
    '''returns whether x looks flat, i.e. looks like an iterable with no internal layers.
    Only checks x[0]. (If x is not iterable, raise TypeError. If len(x)==0, return True).
    Note: might behave unexpectedly for strings.
    '''
    if not is_iterable(x):
        raise TypeError(f'looks_flat(x) expected iterable x but got x={x}')
    if len(x)==0:
        return True
    return not is_iterable(x[0])

def nest_shape(nested_list, is_element=looks_flat):
    '''returns the implied shape for a numpy object array constructed from nested_list.
    Only considers 0th element of list(s) (recursively, as needed). Stops when reaching an is_element(obj).
    To avoid infinite recursion, raise ValueError if current[0] is current (e.g. with strings).
    (To properly handle strings, provide a more sophisticated is_element than the default value.)
    
    is_element: callable of one input
        if is_element(obj), stop going deeper into lists.
        otherwise, append len(obj) to result, then inspect obj[0].
        (to start, use obj = nested_list.)
        default (looks_flat) stops when obj is iterable but obj[0] is not.
    '''
    shape = []
    current = nested_list
    while not is_element(current):
        if current[0] is current:
            raise DimensionalityError('nest_shape failed: obj[0] is obj. Crash to avoid infinite loop.')
        l = len(current)
        shape.append(l)
        current = current[0]
    return shape
