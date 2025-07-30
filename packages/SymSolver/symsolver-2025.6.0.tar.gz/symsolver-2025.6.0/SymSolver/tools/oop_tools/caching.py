"""
File Purpose: methods related to caching

[TODO] use weakref in caches which remember multiple results
[TODO] rewrite longer caching rountines in an object-oriented way?
"""

import collections
import functools
import inspect
import operator

from ..equality import dict_equals
from ..pytools import format_docstring, _inputs_as_dict__maker
from ..sentinels import NO_VALUE
from ...defaults import DEFAULTS


''' --------------------- Caching --------------------- '''

def caching_attr_simple(f):
    '''returns g(x, *args, **kw) which does f(x, *args, **kw) but also caches result.'''
    cache_attr_name = f'_cached_{f.__name__}'
    @functools.wraps(f)
    def f_but_caching(x, *args, **kw):
        '''does f with caching.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        try:
            return getattr(x, cache_attr_name)
        except AttributeError:
            pass  # result not yet cached; handled below.
        result = f(x, *args, **kw)
        setattr(x, cache_attr_name, result)
        return result
    return f_but_caching

def caching_attr_simple_if(cache_if, attr_name=None, cache_fail_ok=False):
    '''returns a function decorator for f(x, *args, **kw) which does caching if cache_if().

    cache_if: callable of 0 arguments
        attempt caching if cache_if().
    attr_name: None or string
        which attribute (of x) to cache to.
        None --> use '_cached_{f.__name__}'
    cache_fail_ok: bool, default False
        whether it is okay to fail to store the cached info, if caching.
        (e.g. if cache_if() and x is a tuple, raise AttributeError unless fail_ok=True)
    '''
    def f_but_caching_attr_simple_if(f):
        '''function decorator for f but first checks cache if cache_if().'''
        cache_attr_name = attr_name if attr_name is not None else f'_cached_{f.__name__}'
        @functools.wraps(f)
        def f_but_maybe_caching(x, *args, **kw):
            '''does f, but does caching if cache_if()'''
            __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
            caching = cache_if()
            if caching:
                try:
                    return getattr(x, cache_attr_name)
                except AttributeError:
                    pass  # result not yet cached.
            result = f(x, *args, **kw)
            if caching:
                try:
                    setattr(x, cache_attr_name, result)
                except AttributeError:  # can't set attr, e.g. maybe self is a tuple.
                    if not cache_fail_ok:
                        raise AttributeError(f'failed to set x.{cache_attr_name} for type(x)={type(x)}.') from None
            return result
        return f_but_maybe_caching
    return f_but_caching_attr_simple_if

def caching_with_state(f, state_attr='_state', attr_name=None, state_equals=None):
    '''return function which does f(self, *args, **kw) but also caching, considering self._state.

    state_attr: str, default '_state'
        consider self.(state_attr) when caching;
        only do caching if state now matches state when cached.
    attr_name: None or string
        which attribute (of x) to cache to.
        None --> use '_cached_{f.__name__}'
    state_equals: None or callable
        if provided, use this to determine equality between states, instead of '=='.

    Note: not "persistent"; only remembers the result & state from most-recent call.
    '''
    cache_attr_name = attr_name if attr_name is not None else f'_cached_{f.__name__}'
    @functools.wraps(f)
    @format_docstring(state_attr=state_attr)
    def f_but_caching_with_state(self, *args, **kw):
        '''does f, but restore cached value if self.{state_attr} matches cached state.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        current_state = getattr(self, state_attr)
        try:
            result = getattr(self, cache_attr_name)  # --> (state, result of f)
        except AttributeError:  # <-- found nothing in cache
            pass  # handled after the else block.
        else:  # <-- found something in cache. Now, check state.
            if state_equals is None:
                if result[0] == current_state:
                    return result[1]
            elif state_equals(result[0], current_state):  # <-- "custom comparison"
                return result[1]
        # <-- cached doesn't have result with state matching current state.
        result = f(self, *args, **kw)
        setattr(self, cache_attr_name, (current_state, result))
        return result
    return f_but_caching_with_state

@format_docstring(default_maxlen=DEFAULTS.CACHING_MAXLEN)
def caching_attr_with_params_if(cache_if, attr_name=None, *, maxlen=NO_VALUE, ignore=[],
                                cache_fail_ok=False, param_equals=None):
    '''returns a function decorator for f(x, *args, **kw) which does caching, associated with inputs.

    cache_if: callable of 0 arguments
        attempt caching if cache_if().
    attr_name: None or string
        which attribute (of x) to cache to.
        None --> use '_cached_{{f.__name__}}'
    maxlen: NO_VALUE, None, int, or callable (with 0 input args).
        max length for the cache.
        NO_VALUE --> use DEFAULTS.CACHING_MAXLEN  (default: {default_maxlen})
        None --> no maximum length
        callable --> call maxlen() to determine maxlen.
        If maxlen is reached, deletes oldest cached value when caching a new one.
        Note: maxlen for cache of x updates "dynamically", not just when f(x) first creates cache;
            e.g. setting a smaller DEFAULTS.CACHING_MAXLEN will cause x cache maxlen update,
                the next time f(x) is called (with *any* other args & kwargs).
    ignore: list of strings, default empty list
        ignore these inputs to f, for caching purposes.
    cache_fail_ok: bool, default False
        whether it is okay to fail to store the cached info, if caching.
        (e.g. if cache_if() and x is a tuple, raise AttributeError unless fail_ok=True)
    param_equals: None or callable, default None.  (another good option is operator.is_.)
        how to compare params when checking cache for the current inputs. 
        if None: tries '==', uses equals() if that fails.
        In case you care about order... does param_equals(new_param, cached_param).
    '''
    def f_but_caching_attr_with_params_if(f):
        '''function decorator for f but first checks cache if cache_if().'''
        cache_attr_name = attr_name if attr_name is not None else f'_cached_{f.__name__}'
        # get maxlen
        if maxlen is NO_VALUE:
            get_maxlen = lambda: DEFAULTS.CACHING_MAXLEN
        elif callable(maxlen):
            get_maxlen = maxlen
        else:
            get_maxlen = lambda: maxlen
        # params matching
        _inputs_as_paramdict = _inputs_as_dict__maker(f)
        # decorator for f which does caching
        @functools.wraps(f)
        def f_but_maybe_caching(x, *args, **kw):
            '''does f, but does caching if cache_if()'''
            __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
            if not cache_if():  # return result immediately if not caching.
                return f(x, *args, **kw)
            # else, do caching.
            # setup
            params_now = _inputs_as_paramdict(x, *args, **kw)  # << (also raises TypeError if invalid inputs for f)
            params_now = {key: val for key, val in tuple(params_now.items())[1:]}  # leave x out of the cache.
            for ignored_param in ignore:
                try:
                    del params_now[ignored_param]
                except KeyError:
                    pass  # ignored_param not in params_now, anyways. That's fine.
            x_cache_maxlen = get_maxlen()
            # get from cache, if possible
            try:
                cache = getattr(x, cache_attr_name)
                if cache.maxlen != x_cache_maxlen:
                    cache = collections.deque(cache, maxlen=x_cache_maxlen)  # adjust cache maxlen
                    must_set_cache_attr = True
                else:
                    must_set_cache_attr = False
            except AttributeError:
                cache = collections.deque(maxlen=x_cache_maxlen)  # create cache for the first time
                must_set_cache_attr = True
            else:
                # search cache for a match. Cache is a list of tuples (value, params).
                for (value_cached, params_cached) in cache:
                    if dict_equals(params_now, params_cached, equals=param_equals):
                        return value_cached
            # set cache attr (either a cache with new maxlen or created cache for the first time)
            if must_set_cache_attr:
                try:
                    setattr(x, cache_attr_name, cache)
                except AttributeError:
                    if not cache_fail_ok:
                        errmsg = f'failed to set x.{cache_attr_name} for x with type={type(x)}.'
                        raise AttributeError(errmsg) from None
            result = f(x, *args, **kw)
            cache.append((result, params_now))
            return result
        return f_but_maybe_caching
    return f_but_caching_attr_with_params_if

@format_docstring(default_maxlen=DEFAULTS.CACHING_MAXLEN)
def caching_attr_with_params_and_state_if(cache_if, attr_name=None, *,
            maxlen=NO_VALUE, ignore=[], cache_fail_ok=False, param_equals=None,
            state=lambda x: 'DEFAULT_STATE', clear_cache_on_new_state=False):
    '''returns a function decorator for f(x, *args, **kw) which does caching, associated with inputs.

    cache_if: callable of 0 arguments
        attempt caching if cache_if().
    attr_name: None or string
        which attribute (of x) to cache to.
        None --> use '_cached_{{f.__name__}}'
    maxlen: NO_VALUE, None, int, or callable (with 0 input args).
        max length for the cache.
        NO_VALUE --> use DEFAULTS.CACHING_MAXLEN  (default: {default_maxlen})
        None --> no maximum length
        callable --> call maxlen() to determine maxlen.
        If maxlen is reached, deletes oldest cached value when caching a new one.
        Note: maxlen for cache of x updates "dynamically", not just when f(x) first creates cache;
            e.g. setting a smaller DEFAULTS.CACHING_MAXLEN will cause x cache maxlen update,
                the next time f(x) is called (with *any* other args & kwargs).
    ignore: list of strings, default empty list
        ignore these inputs to f, for caching purposes.
    cache_fail_ok: bool, default False
        whether it is okay to fail to store the cached info, if caching.
        (e.g. if cache_if() and x is a tuple, raise AttributeError unless fail_ok=True)
    param_equals: None or callable, default None.  (another good option is operator.is_.)
        how to compare params when checking cache for the current inputs.
        if None: tries '==', uses equals() if that fails.
        In case you care about order... does param_equals(new_param, cached_param).
    state: callable, with one input
        State associated with each cached value: state(x).
    clear_cache_on_new_state: bool, default False
        if True, the cache will be cleared if a new state is ever detected.
    '''
    def f_but_caching_attr_with_params_and_state_if(f):
        '''function decorator for f but first checks cache if cache_if().'''
        cache_attr_name = attr_name if attr_name is not None else f'_cached_{f.__name__}'
        # get maxlen
        if maxlen is NO_VALUE:
            get_maxlen = lambda: DEFAULTS.CACHING_MAXLEN
        elif callable(maxlen):
            get_maxlen = maxlen
        else:
            get_maxlen = lambda: maxlen
        # params matching
        _inputs_as_paramdict = _inputs_as_dict__maker(f)
        # decorator for f which does caching
        @functools.wraps(f)
        def f_but_maybe_caching(x, *args, **kw):
            '''does f, but does caching if cache_if()'''
            __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
            if not cache_if():  # return result immediately if not caching.
                return f(x, *args, **kw)
            # else, do caching.
            # setup
            params_now = _inputs_as_paramdict(x, *args, **kw)  # << (also raises TypeError if invalid inputs for f)
            params_now = {key: val for key, val in tuple(params_now.items())[1:]}  # leave x out of the cache.
            for ignored_param in ignore:
                try:
                    del params_now[ignored_param]
                except KeyError:
                    pass  # ignored_param not in params_now, anyways. That's fine.
            state_now = state(x)
            x_cache_maxlen = get_maxlen()
            # get from cache, if possible. Cache is a list of tuples (value, state, params).
            try:
                cache = getattr(x, cache_attr_name)
            except AttributeError:
                cache = collections.deque(maxlen=x_cache_maxlen)  # create cache for the first time
                must_set_cache_attr = True
            else:
                # clear cache due to state change, if necessary
                if clear_cache_on_new_state and (len(cache) > 0):
                    state_cache = cache[0][1]  # state of element 0 in cache.
                    # (note, all cache elements will have the same state if clear_cache_on_new_state.)
                    if state_now != state_cache:  # << new state --> reset cache.
                        cache = collections.deque(maxlen=x_cache_maxlen)
                        must_set_cache_attr = True
                # adjust cache maxlen if necessary
                if cache.maxlen != x_cache_maxlen:
                    cache = collections.deque(cache, maxlen=x_cache_maxlen)
                    must_set_cache_attr = True
                else:
                    must_set_cache_attr = False
                # << actually search cache, here. Cache is a list of tuples (value, state, params).
                for (value_cached, state_cached, params_cached) in cache:
                    if state_now == state_cached:
                        if dict_equals(params_now, params_cached, equals=param_equals):
                            return value_cached
            # set cache attr (either a cache with new maxlen or created cache for the first time)
            if must_set_cache_attr:
                try:
                    setattr(x, cache_attr_name, cache)
                except AttributeError:
                    if not cache_fail_ok:
                        errmsg = f'failed to set x.{cache_attr_name} for x with type={type(x)}.'
                        raise AttributeError(errmsg) from None
            result = f(x, *args, **kw)
            cache.append((result, state_now, params_now))
            return result
        return f_but_maybe_caching
    return f_but_caching_attr_with_params_and_state_if


''' --------------------- Caching Property --------------------- '''

def caching_property_simple(f):
    '''return property(f_but_caching, doc=f.__doc__).
    f_but_caching does f(self) the first time, else gets value from cache.
    cached attribute will be '_cached_{f.__name__}'
    f should be a function of self, only, because cache is simple and doesn't check args / kwargs.
    '''
    cache_attr = f'_cached_{f.__name__}'
    @functools.wraps(f)
    def f_but_caching(self):
        try:
            return getattr(self, cache_attr)
        except AttributeError:
            pass  # handled below
        result = f(self)
        setattr(self, cache_attr, result)
        return result
    return property(f_but_caching, doc=f.__doc__)
