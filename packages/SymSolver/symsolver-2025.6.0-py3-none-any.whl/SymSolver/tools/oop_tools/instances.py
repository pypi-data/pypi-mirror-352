"""
File Purpose: manipulating instantiation of objects

E.g. "if an equivalent object already exists, return it instead of making a new one"

[TODO] use weakref?
"""

from ..dicts import Dict
from ..display import view_after_message, viewlist, Viewable
from ..pytools import inputs_as_dict
from ...errors import InputError, InputMissingError


class StoredInstances(Viewable):
    '''tracks which instances have been stored.
    use list(self) to see list of stored instances.

    force_type: None, or type
        if provided, ensure that all values are this type before storing, via self.store().
        Also if provided, make repr slightly prettier.
    prettyview: bool, default True
        if True, use viewlist in _ipython_display_
        else, print(self) in _ipython_display_.
    viewsort: None or callable
        if not None, use sorted(self, key=viewsort) before displaying.
        Only affects repr / display of self.

    Example setup:

    SYMBOLS = StoredInstances(Symbol)
    def symbol(*args, **kw):
        # create new symbol but first ensure no duplicates; if duplicate return it instead of new symbol.
        creator = Symbol  # Symbol(*args, **kw) will be used to create a new Symbol
        return SYMBOLS.get_new_or_existing_instance(creator, *args, **kw)
    '''
    # # # CREATION # # #
    def __init__(self, force_type=None, *, prettyview=True, viewsort=None):
        self.storage = {}
        self.hashes = {}  # {hash: [objs with that hash]} for all objs in storage, if all objs are hashable.
        self.force_type = force_type
        self.prettyview = prettyview
        self.viewsort = viewsort
        self._cache_new_instance_kw_increment = Dict()  # {(creator, inputs.items()): kw_increment value}

    # # # UPDATE CONTENTS # # #
    def store(self, value):
        if self.force_type is not None:
            if not isinstance(value, self.force_type):
                raise TypeError(f'got object of type {type(value).__name__}, expected type {self.force_type.__name__}')
        self.storage[id(value)] = value
        try:  # [EFF] use hashing for comparisons if all objects are hashable.
            hashed = hash(value)
        except TypeError:
            self.hashes = None  # << not all objs are hashable.
        else:
            self.hashes.setdefault(hashed, []).append(value)

    def clear(self, *, force=False):
        '''clears the contents of self.
        force: bool, default False
            True --> clear contents immediately
            False --> ask for user confirmation first.
        '''
        if not force:
            to_clear = self._clearing_prompt()
            if not to_clear:
                return
        self.storage.clear()
        self.hashes = {}
        self._cache_new_instance_kw_increment.clear()

    def _clearing_prompt(self, extra_message=''):
        '''prompt for clearing self. returns whether to clear or not.'''
        prompt = f'Are you sure you want to clear this {type(self).__name__}' + \
                 ('' if self.force_type is None else f' containing objects of type {self.force_type.__name__}') + \
                 '?\nIt may lead to unexpected behavior, if the objects previously stored here are ever used again.\n' + \
                 ('' if not extra_message else f'{extra_message}\n') + \
                 "Please input 'y' or 'yes' to continue, or 'n' or 'no' to abort: "
        choice_orig = input(prompt)
        choice = choice_orig.lower()  # << lowercase
        if choice in ('', 'n', 'no'):
            print('self.clear() aborted by user. Did not clear anything.')
            return False
        elif choice in ('y', 'yes'):
            return True
        else:
            raise InputError(f"Invalid choice: {repr(choice_orig)}. Expected 'yes' or 'no'.")

    def clear_if(self, condition, *, force=False):
        '''remove all elements from self for which condition(element).
        force: bool, default False
            True --> clear contents immediately
            False --> ask for user confirmation first.
        returns a viewlist of removed elements.
        '''
        if not force:
            to_clear = self._clearing_prompt(extra_message='Only clearing elements which satisfy the provided condition.')
            if not to_clear:
                return
        result = viewlist()
        for key, value in list(self.storage.items()):
            if condition(value):
                removed = self.storage.pop(key)
                result.append(removed)
        if len(result) > 0:
            self._cache_new_instance_kw_increment.clear()
        return result

    # # # GET NEW OR EXISTING INSTANCE # # #
    def _values_maybe_equal_to(self, obj):
        '''returns iterable of self.values() maybe equal to obj.
        if obj is hashable and all values in self are hashable too (i.e. self.hashes is not None),
            return iterable of values in self with same hash value as obj.
        else, return self.values().
        '''
        if self.hashes is None:
            return self.values()
        try:
            hashed = hash(obj)
        except TypeError:
            return self.values()
        else:
            return self.hashes.get(hashed, [])

    def get_new_or_existing_instance(self, creator, *args__create, attr_eq_check='__eq__', **kw__create):
        '''if specified object to be created already exists, return it. Otherwise return new one.
        creator: callable
            new_one = creator(*args__create, **kw__create).
            will use new_one to check against objects in self, for equivalency.
        attr_eq_check: string, default '__eq__'
            use (new_one.(attr_eq_check))(obj) when testing for equivalency between new_one and objects in self.
            if objects are all hashable, only test equivalency between objects with same hash value.
        *args__create and **kw__create are passed to creator.

        sets self._prev_new_or_existing_was_new = True if created a new instance else False.
        '''
        new_one = creator(*args__create, **kw__create)
        obj_equals_new = getattr(new_one, attr_eq_check)
        for existing_obj in self._values_maybe_equal_to(new_one):
            if obj_equals_new(existing_obj):
                self._prev_new_or_existing_was_new = False
                return existing_obj
        else:
            self.store(new_one)
            self._prev_new_or_existing_was_new = True
            return new_one

    def get_new_instance(self, creator, *args__create, attr_eq_check='__eq__', kw_increment='id_', **kw):
        '''if specified object to be created already exists, increment kw_increment (from kw) and try again.

        kw_increment: str
            look for this kwarg in kw (it must be provided).
            result = self.get_new_or_existing_instance(creator, *args, **kw)
            if result didn't already exist, return result.
            Otherwise, increment kw_increment by adding 1, then try again.
            To prevent infinite looping,
                if incrementing kw_increment doesn't affect the result
                (checked via attr_eq_check), raise InputError.

            [EFF] the "previous highest value for kw_increment" is stored in cache.
                The cached value is associated with all inputs including kw_increment.
                E.g. if kw_increment='n', doing get_new_instance(*inputs0, n=1) 100 times
                will look in the cache to pick the next value of n, each time after the first.
                Assuming there were no values already in self for n=1 through n=99, then the results
                will have n=1, n=2, ..., n=99, n=100. But, e.g., for the n=100 result,
                it will see n=99 in the cache and its first attempt will use n=100 (not n=0).

        The remaining inputs are the same as those in self.get_new_or_existing_instance():
            creator: callable
                new_one = creator(*args__create, **kw__create).
                will use new_one to check against objects in self, for equivalency.
            attr_eq_check: string, default '__eq__'
                use (new_one.(attr_eq_check))(obj) when testing for equivalency between new_one and objects in self.
            *args__create and **kw are passed to creator.

        [TODO] improve caching a bit.
        '''
        try:
            i = kw[kw_increment]
        except KeyError:
            errmsg = f'Must provide {repr(kw_increment)} in kwargs, or pick a different kw_increment.'
            raise InputMissingError(errmsg) from None
        kw['attr_eq_check'] = attr_eq_check

        # check cache for better starting point for kw_increment
        cache_inc = self._cache_new_instance_kw_increment
        inputs = inputs_as_dict(creator, *args__create, **kw)
        cache_key = (creator, tuple(inputs.items()))
        try:
            _i = cache_inc[cache_key]
        except KeyError:
            pass  # not found in cache.
        else:
            i = _i + 1  # use the next value of i.
            kw[kw_increment] = i
        
        # get result using these inputs; return it if it's new.
        result0 = self.get_new_or_existing_instance(creator, *args__create, **kw)
        if self._prev_new_or_existing_was_new:
            cache_inc[cache_key] = i
            return result0
        # else, we need to increment and then try again.
        result_prev = result0
        while True:
            i = i + 1
            kw[kw_increment] = i
            result = self.get_new_or_existing_instance(creator, *args__create, **kw)
            if self._prev_new_or_existing_was_new:
                cache_inc[cache_key] = i
                return result
            result__eq__ = getattr(result, attr_eq_check)
            if result__eq__(result_prev):
                errmsg = (f'Incrementing {repr(kw_increment)} from {i-1} to {i} and creating an object '
                          f'led to creating an equivalent object (when compared via obj.{attr_eq_check}). '
                          f'Might be impossible to get a new instance using this scheme. '
                          f'Maybe you meant to provide a different value for kw_increment (got {repr(kw_increment)})')
                raise InputError(errmsg)
            result_prev = result

    # # # REPR # # #
    def _repr_message(self):
        _type_str = 'objects' if self.force_type is None else f'{self.force_type.__name__} instances'
        return f'{type(self).__name__} containing {_type_str}:'

    def _repr_list(self):
        '''returns list(self), possibly sorted(..., key=self.viewsort).'''
        viewsort = self.viewsort
        if viewsort is None:
            return list(self)
        else:
            return sorted(self, key=viewsort)

    def __repr__(self):
        message = self._repr_message()
        return f'{message} {self._repr_list()}'

    def view(self, *args__str, **kw__str):
        '''does view(self)'''
        if self.prettyview:
            view_after_message(self._repr_message(), viewlist(self._repr_list()))
        else:
            print(self)
        

    # # # ITERATION / DICT / LIST-like BEHAVIOR # # #
    def keys(self):
        return self.storage.keys()
    def values(self):
        return self.storage.values()
    def items(self):
        return self.storage.items()
    def __iter__(self):
        return iter(self.values())
    def __getitem__(self, key):
        return self.storage[key]
    def __len__(self):
        return len(self.storage)
    def get(self, key, default=None):
        return self.storage.get(key, default=default)

    def index(self, value):
        '''returns key in self equal to value. raise ValueError if none found.'''
        idv = id(value)
        if idv in self.keys():
            return idv
        for key, v in self.items():
            if value==v:
                return key
        raise ValueError(f'{value} not in list')

    def __contains__(self, value):
        try:
            self.index(value)
        except ValueError:
            return False
        else:
            return True

    # # # REPR LOOKUP # # #
    def lookup_key(self, v):
        '''returns first key from self such that self[key]==v OR str(self[key])==s'''
        for key, value in self.items():
            if value==v:
                return key
            elif str(value)==v:
                return key
        raise KeyError(f'{v} and str({v}) not found.')

    def lookup(self, v):
        '''returns first value from self such that value==v OR str(value)==v'''
        key = self.lookup_key(v)
        return self[key]
