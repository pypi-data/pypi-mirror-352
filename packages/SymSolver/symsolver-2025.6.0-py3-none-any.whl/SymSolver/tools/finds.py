"""
File purpose: find first index/indices of element/s in list, via find/multifind

These are in their own file to mitigate cyclic import errors with iterables.py.
"""
import collections
from collections import defaultdict

from .display import viewlist, viewtuple
from .equality import (
    equals,
)


''' --------------------- Find --------------------- '''

def find(x, element, default=None, *, attempt_fast=True, equals=equals):
    '''find smallest index i for which equals(x[i], element);
    return None if no such i exists.

    if attempt_fast, try x.fastfind(element) first.
        kwargs will not be passed to fastfind (e.g. it won't respect 'equals')
        fastfind should raise ValueError if value not found.
        fastfind should also be blazingly fast, otherwise it's not worthwhile.
        (For example, if x stores a dictionary mapping id(element) to index in x,
        then x could implement fastfind which returns x[id(element)].)
    '''
    if attempt_fast:
        try:
            return x.fastfind(element)
        except (ValueError, AttributeError) as e:
            pass  # handled below
    try:
        return next(i for i, elem in enumerate(x) if equals(elem, element))
    except StopIteration:
        return default

def multifind(x, to_find, default=None, require_exists=False, force_unique=True, equals=equals):
    '''return list of (smallest index i for which equals(x[i], element) for element in to_find).
    x: iterable
        the list in which to search for values in to_find
    to_find: iterable
        the values to look for in to_find.
        result will be the list of indices in x of values from to_find.
    default: any value
        use this value instead of an index for each value from to_find which was not found in x.
    require_exists: bool, default False
        if True, require that all values in to_find exist in x,
            and raise ValueError if any values in to_find don't exist in x.
    force_unique: bool, default True
        if True, force that all indices in result will be unique,
            and raise ValueError if this is not possible.
    '''
    result = []
    xlist = list(x)
    i_to_search = set(range(len(xlist)))
    for element in to_find:
        try:
            i_element = (next(i for i in i_to_search if equals(xlist[i], element)))
        except StopIteration:
            if require_exists:
                errmsg = f'{element} not found in {xlist}'
                if len(i_to_search) < len(x):  # add info about i_to_search to avoid confusing message.
                    errmsg += f', in unused indices ({i_to_search})' 
                raise ValueError(errmsg) from None
            else:
                i_element = default
        else:
            if force_unique:
                i_to_search -= {i_element}
        result.append(i_element)
    return result


''' --------------------- Argmin/max --------------------- '''

def argmin(obj):
    '''index of minimum value in obj'''
    return min(range(len(obj)), key=lambda x: obj[x])

def argmax(obj):
    '''index of maximum value in obj'''
    return max(range(len(obj)), key=lambda x: obj[x])


''' --------------------- Iterables with fastfind --------------------- '''

class FastFindable():
    '''object with fastfind methods attached.'''
    # [TODO][EFF] if no obj id match, check for hashing match (if all objects are hashable)

    def _init_id_lookup(self):
        '''creats _id_lookup from self.'''
        _id_lookup = defaultdict(list)
        for i, obj in enumerate(self):
            _id_lookup[id(obj)].append(i)
        self._id_lookup = _id_lookup

    @property
    def _id_lookup(self):
        '''dict of {id(obj): [indices where obj appears in self]}.'''
        # [EFF] for efficiency, only calculate when requested.
        try:
            return self._id_lookup_internal
        except AttributeError:
            pass  # didn't calculate _id_lookup yet.
        self._init_id_lookup()
        return self._id_lookup_internal

    @_id_lookup.setter
    def _id_lookup(self, value):
        self._id_lookup_internal = value

    def fastfind(self, obj):
        '''returns first index of obj in self, or raises ValueError if not found.
        Only attempts "very fast" lookup using id(obj), doesn't check equality.
        '''
        try:
            return self._id_lookup[id(obj)][0]
        except IndexError:
            # note: this error needs to be less verbose since it gets raised often,
            # and we don't want to waste time converting objects to strings.
            raise ValueError(f'FastFindable.fastfind(obj): obj not found.')

    def __contains__(self, obj):
        '''check if obj in self using fastfind; fall back to super().__contains__ if not found.'''
        try:
            self.fastfind(obj)
        except ValueError:
            pass  # handled after else, to avoid complicated error messages
        else:
            return True
        return super().__contains__(obj)

    def index(self, obj):
        '''returns first index of obj in self, or raises ValueError if not found.
        uses self.fastfind for fast check; fall back to super().index if not found.
        '''
        try:
            return self.fastfind(obj)
        except ValueError:
            pass  # handled below, to avoid complicated error messages
        return super().index(obj)

    def copy(self):
        '''type(self)(super().copy())'''
        return type(self)(super().copy())


class fastfindtuple(FastFindable, tuple):
    '''tuple with fastfind method.
    internally, maintains a dict (at self._id_lookup) of {id(obj): indices where obj appears in self}.
    fastfind(obj) looks in this dict for id(obj).
    '''
    pass


class fastfindlist(FastFindable, list):
    '''list with fastfind method.
    internally, maintains a dict (at self._id_lookup) of {id(obj): indices where obj appears in self}.
    fastfind(obj) looks in this dict for id(obj).

    [EFF] note, self.append() and self.extend() are not much slower,
        since they don't affect the indices of other elements.
        self.pop() is a bit slower; need to update _id_lookup for all objects after the removed one.
        self[i] = val is not much slower since only one element is affected.
    [implementation] note: the implementation here is sort of "hacky",
        since we need to account for all the possible ways that
        the builtin list can be edited, and update self._id_lookup accordingly.
        [TODO] Mabye we should use abstract base class instead...
    '''
    def append(self, x):
        '''super().append(x) then update self._id_lookup'''
        super().append(x)
        self._id_lookup[id(x)].append(len(self)-1)

    def extend(self, x):
        '''super().extend(x) then update self._id_lookup'''
        L0 = len(self)
        super().extend(x)
        _id_lookup = self._id_lookup
        for i, obj in enumerate(x):
            _id_lookup[id(obj)].append(L0 + i)

    def pop(self, index=-1):
        '''super().pop(index) then update self._id_lookup'''
        L0 = len(self)
        obj = super().pop(index)

        ipos = range(L0)[index] if index < 0 else index  # positive index
        _id_lookup = self._id_lookup
        idx = _id_lookup[id(obj)]
        if len(idx)==1:
            del _id_lookup[id(obj)]
        else:
            idx.remove(ipos)
        for j in range(ipos, len(self)):
            idx = _id_lookup[id(self[j])]
            if len(idx)==1:
                # assert idx[0] == j + 1   # since we're shifting everything after ipos by -1.
                idx[0] = j
            else:
                kreplace = idx.index(j + 1)
                idx[kreplace] = j

    def __setitem__(self, i, x):
        '''super().__setitem__(i, x) then update self._id_lookup'''
        _id_lookup = self._id_lookup
        id_old = id(self[i])
        indices_prev = _id_lookup[id_old]
        super().__setitem__(i, x)
        # remove old id
        if len(indices_prev)==1:
            del _id_lookup[id_old]
        else:
            indices_prev.remove(i)
        # put new id
        _id_lookup[id(x)].append(i)

    def clear(self):
        '''super().clear() then update self._id_lookup'''
        super().clear()
        self._id_lookup.clear()

    def reverse(self):
        '''super().reverse() then update self._id_lookup'''
        super.reverse()
        self._init_id_lookup()

    def insert(self, i, x):
        raise NotImplementedError(f'{type(self).__name__}.insert().')

    def __delitem__(self, i):
        raise NotImplementedError(f'{type(self).__name__}.__delitem__(). use pop() instead.')

    def remove(self, x):
        raise NotImplementedError(f'{type(self).__name__}.remove(). use index() & pop() instead.')

    def __iadd__(self, value):
        raise NotImplementedError(f'{type(self).__name__}.__iadd__(). use extend() instead.')

    def __imul__(self, value):
        raise NotImplementedError(f'{type(self).__name__}.__imul__(). use extend() instead.')


### The following is the code I would like to put here,
### however it fails (TypeError: multiple bases have instance lay-out conflict):
# class fastfindviewtuple(fastfindtuple, viewtuple):
#     '''fastfindtuple with view methods too.
#     see help(fastfindtuple) and help(viewtuple) for docs.
#     '''
#     pass

### Minimal example that fails in a similar way is:
# class Foo(tuple): pass
# class Bar(tuple): pass
# class Foobar(Foo, Bar): pass

### Eventually it would be nice to solve the problem,
### but since fastfindtuple has very little code in it,
### it's easier for now to just copy-paste that code here, like this:
class fastfindviewtuple(FastFindable, viewtuple):
    '''viewtuple with fastfind method.
    internally, maintains a dict (at self._id_lookup) of {id(obj): indices where obj appears in self}.
    fastfind(obj) looks in this dict for id(obj).
    '''
    pass

class fastfindviewlist(fastfindlist, viewlist):
    '''fastfindlist with view methods too.
    see help(fastfindlist) and help(viewlist) for docs.
    '''
    pass
