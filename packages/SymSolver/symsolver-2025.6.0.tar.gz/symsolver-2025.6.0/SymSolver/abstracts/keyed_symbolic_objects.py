"""
File Purpose: KeyedSymbolicObject
(directly subclasses IterableSymbolicObject)

Rather than use a list of terms to store info, use a dictionary.

KeyedSymbolicObject is not used anywhere else in abstracts, basics, vectors, or precalc_operators.
An great example of a KeyedSymbolicObject subclass is Polynomial from the polynomials subpackage.
"""

from .iterable_symbolic_objects import IterableSymbolicObject
from .symbolic_objects import SymbolicObject
from ..tools import (
    equals, dict_equals,
    caching_attr_simple, alias,
    fastfindviewtuple,
    _repr,
)


class KeyedSymbolicObject(IterableSymbolicObject):
    '''SymbolicObject containing a dictionary of keys and associated values.

    IMMUTABILITY NOTE:
        KeyedSymbolicObjects should not be altered after their creation;
        instead, create a new KeyedSymbolicObject with the desired alterations.
        There are a few different methods to support this principle and make this task easier,
            such as: [TODO] put method names here.

    KEYS NOTE:
        Parts of the implementation of KeyedSymbolicObject assumes keys are not SymbolicObjects.
        For example, keys are ignored entirely during self.get_symbols(), which only considers values.

    DICT COPYING NOTE:
        [EFF] for efficiency, the input dict is stored internally without first making a copy.
        So, be careful to not edit the input dict outside of this object.
        Note you can copy a dict using dict.copy().
        Also note: using self.copy() will return a new object like self but with the dict copied as well.
    '''
    def __init__(self, dictionary, *args, **kw):
        self.dictionary = dictionary
        SymbolicObject.__init__(self, dictionary, *args, **kw)

    def __eq__(self, b):
        try:
            return SymbolicObject.__eq__(self, b)
        except NotImplementedError:
            return dict_equals(self.dictionary, b.dictionary)

    @caching_attr_simple
    def __hash__(self):
        return hash((type(self), tuple(self.dictionary.items())))

    @property
    def terms(self):
        '''values from self.values(). Includes caching.
        implementation note: allows self to behave like an IterableSymbolicObject in some ways,
        and to re-use some implementations from IterableSymbolicObject in this class.'''
        try:
            return self._cached_terms
        except AttributeError:
            result = fastfindviewtuple(self.values())
            self._cached_terms = result
            return result

    # # # DISPLAY # # #
    def _repr_contents(self, **kw):
        '''list of contents to put as comma-separated list into repr of self.'''
        return [_repr(self.dictionary, **kw)]

    # # # STANDARD DICT-LIKE BEHAVIOR # # #
    def __getitem__(self, key):
        '''return self[key]'''
        return self.dictionary[key]

    def keys(self):    return self.dictionary.keys()
    def values(self):  return self.dictionary.values()
    def items(self):   return self.dictionary.items()
    def __len__(self): return len(self.dictionary)
    def get(self, key, default=None):
        return self.dictionary.get(key, default)

    # # # COMPATIBILITY WITH SUBBABLE / SIMPLIFIABLE OBJECTS # # #
    def _new_from_values(self, *values, **kw):
        '''returns new object like self, with same keys as self.
        values MUST be the same length as self, otherwise this will fail.
        '''
        assert len(values) == len(self)
        return super()._new(dict(zip(self.keys(), values)), **kw)

    _new_after_subs = alias('_new_from_values')
    _new_after_simp = alias('_new_from_values')

    # # # IMMUTABILITY DESIGN INTENTION - SUPPORT # # #
    def copy(self):
        '''returns a NEW OBJECT like self but using a copy of self.dictionary.'''
        return self._new(self.dictionary.copy())

    def updated(self, *update_dict_or_empty, **update_kwargs):
        '''returns a NEW OBJECT like self, after self.dictionary.copy().update(updates)

        update_dict_or_empty: 0 or 1 args.
            If len(update_dict_or_empty) == 0, ignore.
            Else, using E = update_dict_or_empty[0]:
                If E has a .keys() method, then does result[key] = E[key] for key in E.
                Otherwise, does result[key] = value for (key, value) in E.
        update_kwargs:
            for key in update_kwargs, result[key] = update_kwargs[key]
        '''
        if len(update_dict_or_empty) >= 2:
            raise TypeError(f'updated expects 0 or 1 positional args but got {len(update_dict_or_empty)}.')
        dictcopy = self.dictionary.copy()
        dictcopy.update(*update_dict_or_empty, **update_kwargs)
        return self._new(dictcopy)

    def with_key_set_to(self, key, value):
        '''returns a NEW OBJECT like self, but with key set to value.'''
        return self.updated({key: value})
