"""
File Purpose: tools related to iterables
"""

import builtins
import collections

from .imports import ImportFailed
try:
    import numpy as np
except ImportError as err:
    np = ImportFailed('numpy', err=err)

from .dicts import (
    dictlike_in_attr,
)
from .equality import (
    equals,
)
from .finds import (
    find, multifind,   # these belong in this namespace; defined elsewhere to help avoid cyclic dependencies.
    argmin, argmax,
)
from .oop_tools import (
    caching_attr_simple_if                    
)
from .properties import alias_child
from .pytools import _identity_function
from .numbers import (
    NEG_INFINITY, POS_INFINITY,
)
from .sentinels import UNSET
from ..defaults import DEFAULTS


''' ----------------------------- Misc ----------------------------- '''

def is_iterable(x):
    '''returns True if x is iterable, False otherwise.'''
    try:
        iter(x)
        return True
    except TypeError:
        return False

def is_dictlike(x):
    '''returns True if x is dict-like, False otherwise.
    returns x.is_dictlike if it exists,
    else returns whether x has keys() and __getitem__.
    '''
    try:
        x_is_dictlike = x.is_dictlike
    except AttributeError:
        return hasattr(x, 'keys') and hasattr(x, '__getitem__')
    else:
        return x_is_dictlike()


''' --------------------- Sort --------------------- '''

def argsort(x, reverse=False, key=_identity_function):
    '''does an argsort using pythons builtin function: sorted'''
    return [ix[0] for ix in sorted(zip(range(len(x)), x), key=lambda ix: key(ix[1]), reverse=reverse)]

def nargsort(x, reverse=False, none=NEG_INFINITY):
    '''does an argsort but treats None like negative infinity.
    none: value. Default negative infinity (i.e. always less than everything except negative infinity)
        replace None with this value.
    '''
    key = lambda y: none if y is None else y
    return argsort(x, reverse=reverse, key=key)

def argsort_none_as_small(x, reverse=False):
    '''argsort, treating None as negative infinity.'''
    return nargsort(x, reverse=reverse, none=NEG_INFINITY)

def argsort_none_as_large(x, reverse=False):
    '''argsort, treating None as positive infinity.'''
    return nargsort(x, reverse=reverse, none=POS_INFINITY)

def sort_by_priorities(x, prioritize=[], de_prioritize=[], equals=lambda v1, v2: v1==v2):
    '''returns list of elements of x, reordered acoording to priorities.
    puts p in prioritize first (in order of prioritize) for any p which appear in x.
    puts p in de_prioritize last (de_prioritize[-1] goes at very end) for any p which appear in x.

    The equals key can be used to provide a custom "equals" function.
    For example, to prioritize any elements of x containing 'MEFIRST', you could do:
        sort_by_priorities(x, ['MEFIRST'], equals=lambda sp, sx: sp in sx)
    (Note that the second arg passed to equals will be the element of x.)
    '''
    start  = []
    middle = []
    end    = []
    for y in x:
        i = find(prioritize, y, default=None, equals=equals)
        if i is not None:
            start  += [(y, i)]
        else:
            j = find(de_prioritize, y, default=None, equals=equals)
            if j is not None:
                end += [(y, j)]
            else:
                middle += [y]
    # sort start and end
    start = [start[i][0] for i in argsort(start, key=lambda y_i: y_i[1])]
    end   = [end[i][0]   for i in argsort(end,   key=lambda y_i: y_i[1])]
    # return result
    return start + middle + end


''' --------------------- Misc. Shallow Iteration --------------------- '''
# iterate an iterable; accomplish some helpful task.

def counts(x, equals=equals):
    '''converts x (an iterable) to a list of tuples: (y, number of times y appears in x).'''
    result = []
    for y in x:
        for zi, [z, zcount] in enumerate(result):
            if equals(y, z):
                result[zi][1] += 1
                break
        else:  # didn't find y in result
            result.append([y, 1])
    return result

def counts_idx(x, equals=equals):
    '''converts x (an iterable) to a list of tuples: (y, list of indices where y appears in x).'''
    result = []
    for yi, y in enumerate(x):
        for zi, [z, zidx] in enumerate(result):
            if equals(y, z):
                result[zi][1].append(yi)
                break
        else:  # didn't find y in result
            result.append([y, [yi]])
    return result

def counts_sublist_indices(ll, equals=equals):
    '''converts ll (an iterable of iterables) to a list of tuples:
        [(y, dict of i: [j such that list_of_iterables[i][j] == y]) for x in ll for y in x]
    '''
    result = []
    for i, sublist in enumerate(ll):
        for j, y in enumerate(sublist):
            for k, [ry, r_indices] in enumerate(result):
                if equals(y, ry):
                    try:
                        result[k][1][i].append(j)
                    except KeyError:
                        result[k][1][i] = [j]   # initialize result[k][1][i].
                    break
            else:  # didn't find y in result
                result.append( (y, {i: [j]}) )
    return result

def pop_index_tracker(idx, popping):
    '''returns a new list of indices when popping are popped from the list that idx corresponds to.

    - decrements all indices larger than 7 by 1 if 7 is being popped.
    - removes indices which are being popped, if applicable.
    E.g., (idx=[1,4,8,15], popping=[4,5,9]) --> (1,6,12), because:
        - the 1 is unchanged.
        - the 4 is popped, entirely.
        - the 8 is not popped, however 2 indices are popped below it, so it becomes a 6.
        - the 15 is not popped, however 3 are popped below, so it becomes a 12.
    '''
    result = []
    for i in idx:
        if i in popping:
            continue
        else:
            i = i - sum(i > pop for pop in popping)
            result.append(i)
    return result

def _list_without_i(l, i):
    '''returns list without i'th element. (nondestructive)'''
    return [elem for j, elem in enumerate(l) if j!=i]

def default_sum(*summands, default=(None, 0)):
    '''return sum of summands, but replacing any occurence of default[0] with default[1].
    default: (placeholder, value). Default: (None, 0)
        while adding terms, treat any occurence of placeholder (default[0]) as value (default[1]).
        occurences detected via 'is', i.e. only when a summand point to the same object as placeholder.
    If there are no summands, or (summand is placeholder) for all summands, return placeholder.
    '''
    result = default[0]
    for term in summands:
        if result is default[0]:
            result = term
        else:
            if term is default[0]:
                term = default[1]
            result = result + term
    return result


''' --------------------- Categorize --------------------- '''

def dichotomize(x, condition=_identity_function):
    '''Returns ([y for y in x if condition(y)], [y for y in x if not condition(y)])'''
    good = []
    bad  = []
    for y in x:
        (good if condition(y) else bad).append(y)
    return (good, bad)

def categorize(x, *conditions):
    '''puts each y in x into the first applicable category from conditions.
    returns tuple of lists of elements in each category. len(result) == len(conditions) + 1.
    Elements belonging to no category are placed into the final list in the result
        (or somewhere else if one of the conditions is None)

    *conditions: functions or None
        each condition is a function which accepts 1 arg. It will be passed values of y from x.
        only bool(condition(y)) will be considered here.

        use None to indicate placement for the 'default' (i.e. belonging to no category).
            at most one condition is allowed to be None.
            if None does not appear in conditions, it is equivalent to putting None at the end.

    Example:
        categorize([1,3,4,7,-2,True,8,False], lambda y: y==1, lambda y: y%2==0)
        --> ([1, True], [4, -2, 8, False], [3, 7])
        categorize([1,3,4,7,-2,True,8,False], lambda y: y==1, None, lambda y: y%2==0)
        --> ([1, True], [3, 7], [4, -2, 8, False])
    '''
    iNone = find(conditions, None, default= -1, equals=lambda v1, v2: v1 is v2)
    assert (iNone == -1) or (None not in conditions[iNone+1:]), "multiple conditions are None."
    result = tuple([] for _ in range(len(conditions)+(1 if (iNone == -1) else 0)))
    for y in x:
        for i, condition in enumerate(conditions):
            if (condition is not None) and condition(y):
                result[i].append(y)
                break
        else:  # didn't break
            result[iNone].append(y)
    return result

@dictlike_in_attr('categories')
class Categorizer():
    '''class for holding categories and some info about categories, to use with categorize.'''
    def __init__(self, *key_category_tuples):
        self.set_categories(*key_category_tuples)

    def set_categories(self, *key_category_tuples):
        '''sets categories according to the (key, category) tuples provided.'''
        self.categories = collections.OrderedDict(key_category_tuples)

    def append_category(self, key, category):
        '''puts category with key as the last category in self.'''
        try:
            del self[key]
        except KeyError:
            pass  # it's fine; we just wanted to make sure self[key] doesn't exist.
        self[key] = category

    def replace_or_append_category(self, oldkey, newkey, category):
        '''replaces oldkey and its value with (newkey, category) if it exists, else appends (key, category).'''
        if oldkey in self:
            _new_tuples = ((newkey, category) if key==oldkey else (key, val) for key, val in self.items())
            self.set_categories(*_new_tuples)
        else:
            self.append_category(newkey, category)

    def categorize(self, x):
        '''categorize x according to categories in self.'''
        return categorize(x, *self.values())

    def __repr__(self):
        return f'{type(self).__name__}(keys=({", ".join(repr(key) for key in self.keys())}))'


def group_by(x, condition=_identity_function):
    '''Returns list of tuples of (list of consecutive terms in x, condition(term)),
    such that each list of terms contains all the consecutive terms in x for which condition(term) is the same.

    Example: group_by([1,5,3,2,4,7,6,2,8], lambda y: y % 2 == 0)
        --> [([1,5,3],False), ([2,4],True), ([7],False), ([6,2,8],True)]
    '''
    result = []
    if len(x) == 0:
        return result
    iter_x = iter(x)
    y = next(iter_x)
    c = condition(y)
    i = 0
    result.append(([y], c))
    for y in iter_x:
        prev_c = c
        c = condition(y)
        if prev_c == c:
            result[i][0].append(y)
        else:
            i += 1
            result.append(([y], c))
    return result


''' --------------------- Deep Iteration --------------------- '''
# working with iterables of iterables

def walk(x, require=None, *, requiretype=None, depth_first=True, order=False,
         iter=builtins.iter, priority=None):
    '''walk through all terms inside x, requiring require if provided.
    note: if depth_first but not order, will iterate through each "layer" in reverse order,
        since that is more efficient (see collections.deque.extendleft).
        If you need to preserve order, use style=True. OR use iter=builtins.reversed.

    require: None or callable
        if provided, only iterate through x if require(x).
    requiretype: None, type, or tuple of types.
        if provided, only iterate through x if isinstance(x, requiretype).
    depth_first: bool
        if True, walk depth first. else, walk breadth first.
    order: bool, default False
        whether to use terms' original order, when doing depth first walk. Ignored if breadth first.
        False is more efficient, but True will maintain original order.
    iter: callable, default builtins.iter
        iterate through iter(x) and iter(term) for term in x, etc.
        iter(t) should raise TypeError to prevent iteration of t
            (either because it's impossible, or just to avoid visiting its contents on this walk).
    priority: None or callable
        if provided, pick term with highest priority(term), instead of depth first or breadth first.
        default priority is 0, so any provided priority function must provide values >= 0.
    '''
    if (requiretype is not None) and not isinstance(x, requiretype):
        return   # stop generating.
    if (require is not None) and not require(x):
        return   # stop generating.
    try:
        iter_x = iter(x)
    except TypeError: # x is not iterable
        return   # stop generating.
    queue = collections.deque()
    # handle order
    if order and depth_first:
        def queue_extend(iterable):
            queue.extendleft(reversed(tuple(iterable)))
    else:
        queue_extend = queue.extendleft if depth_first else queue.extend
    # handle priority
    if priority is None:
        queue_next_term = queue.popleft
    else:
        pdict = dict()
        queue = dict()  # {priority: [terms with that priority]}
        def queue_extend(iterable):
            terms = tuple(iterable)
            priorities = tuple(priority(term) for term in terms)
            pdict.update({id(term): p for term, p in zip(terms, priorities)})
            for p, term in zip(priorities, terms):
                queue.setdefault(p, collections.deque()).append(term)
        def queue_next_term():
            pmax = max(queue.keys())
            qp = queue[pmax]
            result = qp.popleft()
            if len(qp) == 0:
                del queue[pmax]
            return result
    # begin the walk
    queue_extend(iter_x)
    while queue:
        term = queue_next_term()
        yield term
        if ((require is None) or require(term)) and ((requiretype is None) or isinstance(term, requiretype)):
            try:
                iter_term = iter(term)
            except TypeError: # term is not iterable
                pass
            else:
                queue_extend(iter_term)

deep_iter = walk  # alias

def walk_depth_first(x, require=None, *, requiretype=None):
    '''walk_depth_first through all terms inside x, requiring require if provided.
    require: None or callable
        if provided, only iterate through x if require(x).
    requiretype: None, type, or tuple of types.
        if provided, only iterate through x if isinstance(x, requiretype).
    '''
    return walk(x, require=require, requiretype=requiretype)

def walk_breadth_first(x, require=None, *, requiretype=None):
    '''walk_breadth_first through all terms inside x, requiring require if provided.
    require: None or callable
        if provided, only iterate through x if require(x).
    requiretype: None, type, or tuple of types.
        if provided, only iterate through x if isinstance(x, requiretype).
    '''
    return walk(x, require=require, requiretype=requiretype)

@caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES, cache_fail_ok=True)
def layers(obj):
    '''return number of layers in obj.

    non-iterable --> layers = 0
    iterable --> layers = 1+max(layers(term) for term in obj)

    note: caches result in object if possible; intended for use with immutable objects.
    '''
    try:
        iter_obj = iter(obj)
    except TypeError:
        return 0
    else:
        return 1 + max((layers(term) for term in iter_obj), default=0)

def structure_string(obj, nlayers=10, type_=None, *, tab='  ', _layer=0, _i=None):
    '''returns string for structure of obj, cutting off at layer < layers.
    nlayers: int
        max number of layers to show.
    type_: None, type, or tuple of types
        if provided, only expand structure for objects of this type (or one of these types, if tuple).
    tab: str, default ' '*2.
        tab string (for pretty result). Inserts N tabs at layer N.
    _layer: int, default 0
        the current layer number.
    _i: None or int
        if provided, tells the index number of this object within the current layer.
    '''
    istr = '' if _i is None else ', i={}'.format(_i)
    result = f'{tab * _layer}(L{_layer:d}{istr}) {type(obj).__name__}'
    if (type_ is not None) and (not isinstance(obj, type_)):
        return result
    obj_layers = layers(obj)
    if obj_layers > 0:
        result += f' with len=({len(obj):d}), and ({obj_layers:d}) internal layers'
    if (_layer < nlayers) and (len(obj) > 0):
        internals = [structure_string(t, nlayers=nlayers, type_=type_, tab=tab, _layer=_layer+1, _i=j)
                        for j, t in enumerate(obj)]
        result += '\n' + '\n'.join(internals)
    return result


''' --------------------- Unique additions --------------------- '''

def appended_unique(l, to_append):
    '''returns a new list with values from l then values from to_append,
    keeping the same order, but dropping any duplicate entries.

    Note: Python 3.7 or later. Relies on dict order being maintained.
    Equivalent to list(dict.fromkeys([*l, *to_append]))
    '''
    return list(dict.fromkeys((*l, *to_append)))



''' ----------------------------- Generic Containers ----------------------------- '''

class Container():
    '''a container for multiple objects, & rules for enumerating & indexing.
    Here, implements self.__getitem__ so that self[i]=self.data[i],
        and self.enumerate which yields (i, self[i]) pairs.
    subclass should implement __init__, _enumerate_all, and new_empty.
    '''
    # # # THINGS THAT SUBCLASS SHOULD IMPLEMENT # # #
    def __init__(self, stuff):
        '''should set self.data = something related to stuff.'''
        raise NotImplementedError(f'{self.__class__.__name__}.__init__')

    def _enumerate_all(self):
        '''iterate through all objs in self, yielding (i, self[i]) pairs.
        Equivalent to self.enumerate(idx=None).
        The implementation will depend on the container type; subclass should implement.
        '''
        raise NotImplementedError(f'{self.__class__.__name__}._enumerate_all')

    def new_empty(self, fill=UNSET):
        '''return a new container of the same shape as self, filled with the value fill.
        The implementation will depend on the container type; subclass should implement.
        '''
        raise NotImplementedError(f'{self.__class__.__name__}.new_empty')

    def _size_all(self):
        '''return the number of objects in the container.
        The implementation will depend on the container type; subclass should implement.
        '''
        raise NotImplementedError(f'{self.__class__.__name__}.size_all')

    # # # GETITEM & ENUMERATE # # #
    def __getitem__(self, idx):
        return self.data[idx]

    def enumerate(self, idx=None):
        '''iterate through i in idx, yielding (i, self[i]) pairs.
        If idx is None, iterate through all objs in self (see self._enumerate_all).
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if idx is None:
            for i, selfi in self._enumerate_all():
                yield (i, selfi)
        else:
            for i in idx:
                yield (i, self[i])

    def size(self, idx=None):
        '''return the number of objects in the container, or in idx if provided.'''
        if idx is None:
            return self._size_all()
        return len(idx)

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{self.__class__.__name__}({self.data})'


class ContainerOfList(Container):
    '''a list-like container.'''
    def __init__(self, objs):
        self.data = [o for o in objs]

    def _enumerate_all(self):
        '''iterate through all objs in self, yielding (i, self[i]) pairs.'''
        return enumerate(self.data)

    def new_empty(self, fill=UNSET):
        '''return a new list of the same shape as self, filled with the value fill.'''
        return [fill for _ in self.data]

    def _size_all(self):
        '''the number of objects in this container. == len(self.data)'''
        return len(self.data)


class ContainerOfArray(Container):
    '''a numpy-array-like container.'''
    def __init__(self, arr):
        self.data = np.asanyarray(arr)

    def _enumerate_all(self):
        '''iterate through all objs in self, yielding (i, self[i]) pairs.'''
        return np.ndenumerate(self.data)

    def new_empty(self, fill=UNSET):
        '''return a new array of the same shape as self, filled with the value fill.'''
        return np.full_like(self.data, fill, dtype=object)

    def _size_all(self):
        '''the number of objects in this container. == self.data.size'''
        return self.data.size

    shape = alias_child('data', 'shape')
    ndim = alias_child('data', 'ndim')
    dtype = alias_child('data', 'dtype')


class ContainerOfDict(Container):
    '''a dict-like container.'''
    def __init__(self, d):
        self.data = dict(d)  # copy the dict (and ensure dict-like)

    def _enumerate_all(self):
        '''iterate through all objs in self, yielding (i, self[i]) pairs.'''
        return self.data.items()

    def new_empty(self, fill=UNSET):
        '''return a new dict of the same shape as self, filled with the value fill.'''
        return {k: fill for k in self.data.keys()}

    def _size_all(self):
        '''the number of objects in this container. == len(self.data)'''
        return len(self.data)

