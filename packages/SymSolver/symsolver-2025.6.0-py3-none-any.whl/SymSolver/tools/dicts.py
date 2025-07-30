"""
File Purpose: Dict without hashing, and dictlike behavior for other objects

(Dict without hashing is slower than dict, but behaves like dict.)
"""
import collections

from .display import viewlist
from .equality import (
    equals,
)
from .finds import (
    find, fastfindlist
)
from .sentinels import NO_VALUE

from ..defaults import DEFAULTS


def dictlike_in_attr(attr):
    '''returns a wrapper f(cls) which adds methods to the cls so it behaves like a dict.
    Those methods assume the dict-behavior should be associated with attribute attr.
    E.g. attr is the attribute in instances of cls where the dict of information is kept.

    [TODO] refactor using MutableMapping from collections abc
    '''
    def cls_but_dictlike_in_attr(cls):
        '''adds methods to cls so it behaves like dict stored in attr, then returns cls.'''
        def __setitem__(self, key, value): getattr(self, attr)[key] = value
        cls.__setitem__ = __setitem__

        def __getitem__(self, key): return getattr(self, attr)[key]
        cls.__getitem__ = __getitem__

        def __delitem__(self, key): del getattr(self, attr)[key]
        cls.__delitem__ = __delitem__

        def __contains__(self, key): return key in getattr(self, attr)
        cls.__contains__ = __contains__

        def keys(self): return getattr(self, attr).keys()
        cls.keys = keys

        def items(self):  return getattr(self, attr).items()
        cls.items = items

        def values(self): return getattr(self, attr).values()
        cls.values = values

        def get(self, key, default=None): return getattr(self, attr).get(key, default)
        cls.get = get
        
        return cls
    return cls_but_dictlike_in_attr

class Dict():
    '''"dict" which is inefficient (doesn't use hashing) but otherwise behaves like a dict.
    if default is provided (i.e. not NO_VALUE),
        value for key will be assigned default upon first access if get before set.

    [EFF] for efficiency, can use get_i, set_i, del_i methods if index of key is already known.
        This reduces number of key comparisons required (comparing via self.equals).
    [EFF] _keys and _values are stored as fastfindlist objects,
        which internally store dict of {id(obj): indices where obj appears} for faster finding.
        This means that self ASSUMES self.equals(obj, obj) for all objs.
    '''
    def __init__(self, equals=equals, default=NO_VALUE):
        self._keys = fastfindlist()
        self._values = fastfindlist()
        self.equals = equals
        self.default = default

    def disable_default(self):
        '''sets self.default=NO_VALUE.
        E.g., useful if using default internally but don't want end-result to have a default.
        '''
        self.default = NO_VALUE

    def keys(self):
        return self._keys.copy()
    def values(self):
        return self._values.copy()
    def items(self):
        return list(zip(self._keys, self._values))

    def __repr__(self):
        items_str = ', '.join([f'{key}={value}' for key, value in self.items()])
        return f'Dict({items_str})'

    def __iter__(self):
        return iter(self._keys)

    def _index(self, key):
        '''index of key in self. raise KeyError if not found.'''
        result = self.find(key)
        if result is None:
            raise KeyError(key)
        else:
            return result

    def find(self, key):
        '''find key in self; return index, or None if not found.'''
        return find(self._keys, key, equals=self.equals)

    def __contains__(self, key):
        '''returns key in self'''
        return self.find(key) is not None

    def __getitem__(self, key):
        try:
            i = self._index(key)
        except KeyError:
            if self.default is not NO_VALUE:
                return self.default
            else:
                raise
        return self._values[i]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def get_i(self, i):
        '''return i'th value in self'''
        return self._values[i]

    def __setitem__(self, key, value):
        i = self.find(key)
        if i is None:
            self._keys.append(key)
            self._values.append(value)
        else:
            self.set_i(i, value, key=key)
            # ^ we set key too because it may be a different object (even though equals(old key, new key)).

    def set_i(self, i, value, *, key=NO_VALUE):
        '''set value for i'th key.
        key: any object, default NO_VALUE
            if provided (i.e. not NO_VALUE), also set i'th key to the value provided.'''
        self._values[i] = value
        if key is not NO_VALUE:
            self._keys[i] = key

    def __len__(self):
        return len(self._keys)

    def __delitem__(self, key):
        i = self._index(key)
        self.del_i(i)

    def del_i(self, i):
        '''delete i'th key & value.'''
        self._keys.pop(i)
        self._values.pop(i)

    def clear(self):
        '''remove all keys & values from self.'''
        self._keys.clear()
        self._values.clear()


''' --------------------- Binning --------------------- '''

class Binning(collections.defaultdict):
    '''collection of objects sorted into bins for faster comparison.

    binner: callable
        function to use for binning objects.
        use self.binner(obj) to get the bin key for obj.
    equals: callable, default tools.equals
        function to use for testing equality between two objects.
        all calls to equals will look like equals(obj, b) where b is the value already in self.

    use self.bin(obj) or self.append(obj) to put a new obj into self.

    Methods which put a single new object into self usually provide kwarg "key", for efficiency.
        It is easiest to just ignore this kwarg, when using this class.
        However, if you already calculated binner(obj), you can use key=binner(obj),
            to prevent binner(obj) from being called a second time.
    '''
    default_default_factory = fastfindlist  # << default factory to pass to collections.defaultdict.__init__.

    def __init__(self, binner, *, equals=equals):
        self.binner = binner
        self.equals = equals
        super().__init__(self.default_default_factory)

    def _new(self, **kw):
        kw = {'binner':self.binner, 'equals':self.equals, **kw}
        return type(self)(**kw)

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}({dict.__repr__(self)})'

    # # # BIN NEW OBJECT(S) # # #
    def bin(self, obj, *, key=NO_VALUE):
        '''put obj into the appropriate bin in self.
        returns (bin key, bin where obj was just appended)
        '''
        if key is NO_VALUE: key = self.binner(obj)
        bin_ = self[key]
        bin_.append(obj)
        return (key, bin_)

    append = property(lambda self: self.bin, doc='''alias to self.bin''')

    def bin_or_index(self, obj, *, return_bin=False, key=NO_VALUE):
        '''puts obj in self if it's not already there, and returns some info about what happened.

        returns (whether obj was already in self, index info),
            where index info is (bin key, index in bin).

        return_bin: bool, default False
            if True, index info will instead be (bin key, index in bin, bin)
        '''
        if key is NO_VALUE: key = self.binner(obj)
        try:
            info = self.index(obj, return_bin=return_bin, key=key)
        except ValueError:
            pass  # handled after the else block.
        else:
            return (True, info)
        # not already in self. Add then return info.
        key, bin_ = self.bin(obj, key=key)
        info = (key, 0, bin_) if return_bin else (key, 0)
        return (False, info)

    # # # FIND OBJECT IN SELF # # #
    def index(self, obj, *, return_bin=False, key=NO_VALUE):
        '''returns (bin key, index in bin) for first index in self with corresponding value equal to obj.
        raise ValueError if obj not found in self.
        You can use the result via self[bin key][index in bin] to get the match for obj, from self.

        return_bin: bool, default False
            if True, instead return (bin key, index in bin, bin).
        '''
        if key is NO_VALUE: key = self.binner(obj)
        bin_ = self[key]
        i = find(bin_, obj, equals=self.equals)
        if i is None:
            raise ValueError(f'obj not found in self; in bin key={key}')
        return (key, i, bin_) if return_bin else (key, i)

    def get_bin(self, obj):
        '''returns the list of objects in the same bin that obj would be in, in self.
        Equivalent to self[self.binner(obj)].
        '''
        return self[self.binner(obj)]

    def __contains__(self, obj):
        '''returns whether obj appears in self'''
        bin = self.get_bin(obj)
        return any(self.equals(obj, b) for b in bin_)

    # # # ITERATE THROUGH SELF # # #
    def flat(self):
        '''iterate through all bins in self, all objects in each bin, yielding 1 object at a time.'''
        for index, obj in self.bin_iter():
            yield obj

    def bin_iter(self):
        '''yields ((bin key, index in bin), obj), iterating through self.'''
        for key, bin_ in self.items():
            for i, obj in enumerate(bin_):
                yield ((key, i), obj)

    # # # UPDATE # # #
    def update(self, other, *, unique=True):
        '''update self with values from other Binning object.
        Assumes (but does not check) that other.binner(obj) == self.binner(obj) for all objs in self & other.
        if unique, only add objs that are not already in self.

        For dict-like update, use self.dict_update instead.
        '''
        for ((key, _i), obj) in other.bin_iter():
            if unique:
                self.bin_or_index(obj, key=key)
            else:
                self.bin(obj, key=key)

    def updated(self, other, *, unique=True):
        '''return result of updating self with values from other Binning object.
        (first makes a copy of self; self will not be altered.)
        '''
        result = self.copy()
        result.update(other, unique=unique)
        return result

    def dict_update(self, other):
        '''super().update(other)'''
        return super().update(other)

    # # # REMOVE OBJECT # # #
    def pop_index(self, key, i):
        '''pop obj at self[key][i]. Equivalent to self[key].pop(i)'''
        return self[key].pop(i)

    # # # COPY # # #
    def copy(self):
        '''returns a "deep" copy of self (same objects in result.flat() but reform the bin lists)'''
        result = self._new()
        for key, bin_ in self.items():
            result[key] = bin_[:]  # copy the bin list.
        return result

    def subset(self, *bin_keys, copy=True):
        '''returns new Binning like self but with only the specified keys.
        copy: bool, default True
            whether to use copies of bins.
            False --> result bins will point to the same exact lists as self bins.
        '''
        result = self._new()
        for key in bin_keys:
            bin_ = self[key]
            if copy:
                bin_ = bin_[:]
            result[key] = bin_
        return result
