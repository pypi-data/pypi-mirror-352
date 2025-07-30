"""
File Purpose: SimplifiableObject, also see SIMPLIFY_OPS and EXPAND_OPS.

SimplifiableObject: provides methods for rewriting/simplifying/expanding.

SIMPLIFY_OPS and EXPAND_OPS: contain all simplification ops defined throughout SymSolver.
@simplify_op and @expand_op decorate ops to put pointers to them into SIMPLIFY_OPS and EXPAND_OPS.

SIMPLIFY_OPS_SKIP and EXPAND_OPS_SKIP: tell which ops to skip for which classes, by default.
"Skip by default" behavior can be adjusted:
    use SIMPLIFY_OPS.skip(funcname) to turn on "skip funcname by default".
    use SIMPLIFY_OPS.dont_skip(funcname) to turn off "skip funcname by default".
    similar for EXPAND_OPS.skip and EXPAND_OPS.dont_skip.
    "funcname" above can be the exact name (e.g. '_abstract_number_evaluate'),
        or an alias, e.g. 'evaluate_numbers'
            (applies to all ops with that alias, or an alias containing that string)
        or just part of the name, e.g. 'number_evaluate'
            (applies to all ops containing that string)

[TODO]:
    - connect DEFAULTS.TIMEOUT_SECONDS to timeout more dynamically than just at function definition.
    - maybe we should associate SIMPLIFY_OPS and EXPAND_OPS with the AbstractOperation class,
        instead of the ops throughout ALL of SymSolver.
    - simplify the code for tracking whether to skip or not skip ops.
        e.g. instead of SIMPLIFY_OPS and SIMPLIFY_SKIP_OPS,
        associate a "skip" flag with each op in SIMPLIFY_OPS.
"""

import collections
import functools
import textwrap
import time

from .symbolic_objects import SymbolicObject

from ..attributors import attributor
from ..errors import InputError, warn, warn_Timeout
from ..tools import (
    view, _str, _repr, apply,
    equals,
    find, multifind,
    alias,
    NO_VALUE,
    caching_attr_with_params_and_state_if,
    maybe_viewer,
    format_docstring,
    ProgressUpdater,
    Opname_to_OpClassMeta__Tracker, Opname_to_Classes__Tracker,
)
from ..defaults import DEFAULTS, ZERO

''' --------------------- Global values --------------------- '''

_timeout_warned = [False]


''' --------------------- Convenience --------------------- '''

@attributor
def simplify(x, **kw):
    '''simplifies x using ops from SIMPLIFY_OPS only.
    returns x.simplify(**kw) if possible, else return x.

    This operation should be "reasonably fast".
        Will loop recursively until result stops changing ("change" determined via 'is').
        But, SIMPLIFY_OPS shouldn't include operations which expand x,
            so this operation should complete eventually.
        If it is stalling for a long time, try again but with debug=True to see why.
    '''
    try:
        x_simplify = x.simplify
    except AttributeError:
        return x
    else:
        return x_simplify(**kw)

@attributor
def expand(x, **kw):
    '''expands x using ops from EXPAND_OPS only.
    returns x.expand(**kw) if possible, else return x.

    This operation should be "reasonably fast".
        Will loop recursively until result stops changing ("change" determined via 'is').
        But, EXPAND_OPS should only include operations which expand x,
            so this operation should complete eventually.
        If it is stalling for a long time, try again but with debug=True to see why.
    '''
    try:
        x_expand = x.expand
    except AttributeError:
        return x
    else:
        return x_expand(**kw)

@attributor
def simplified(x, loop=False, **kw):
    '''simplifies x using ops from both EXPAND_OPS and SIMPLIFY_OPS.
    returns x.simplified(**kw) if possible, else return x.

    loop: bool, default False
        whether to keep looping until result stops changing.
        False --> result is equivalent to x.expand().simplify()
    '''
    try:
        x_simplified = x.simplified
    except AttributeError:
        return x
    else:
        return x_simplified(loop=loop, **kw)

def _simplyfied(x, **kw__None):
    '''apply _simple_simplify to x, or return x if x doesn't have '_simple_simplify' attribute.'''
    return apply(x, '_simple_simplify')

def _op2op(_opstr, lenient=False):
    '''asserts _opstr starts with '_' and returns _opstr without the leading underscore.'''
    if lenient and _opstr[0] != '_':
        return _opstr
    else:
        assert _opstr[0] == '_', f"_opstr {repr(_opstr)} missing leading '_'. "
        return _opstr[1:]


''' --------------------- Which Ops are Available? - Meta/Info Tracking --------------------- '''

# # # ALL SIMPLIFY OR EXPAND OPS DEFINED THROUGHOUT SYMSOLVER # # #
SIMPLIFY_OPS = Opname_to_OpClassMeta__Tracker()
EXPAND_OPS   = Opname_to_OpClassMeta__Tracker()

_simpop_deco_factory_docs = \
    '''returns a function decorator deco(f) which adds f to {SIMP_OPS} and binds f to target.

    target: type
        the class for which f is a simplify operation.
        f will be bound to target, at attribute name f.__name__.
    order: number, default 0
        relative order for applying f to target. (lower --> apply sooner)
        relative compared to other ops tracked in {SIMP_OPS} for target (or any of target's parents)
        in case of tie, all tied funcs might be applied in any order.
    doc: None or string
        more notes/info associated with this tracking / the function being decorated.
        note: currently, not much implemented to interact with doc.
    alias: None or string
        if provided, tell SIMPLIFY_OPS that this is an alias of f,
        and also sets target.(alias) to point to target.(f.__name__).
    aliases: None or list of strings
        if provided, tell self that these are aliases of f.
        Similar to alias but allows to provide multiple values.'''

@format_docstring(docstring=_simpop_deco_factory_docs.format(SIMP_OPS='SIMPLIFY_OPS'))
def simplify_op(target, order=0, doc=None, alias=None, aliases=None):
    '''{docstring}'''
    return SIMPLIFY_OPS.track_and_bind_op(target, order=order, doc=doc, alias=alias, aliases=aliases)

@format_docstring(docstring=_simpop_deco_factory_docs.format(SIMP_OPS='EXPAND_OPS'))
def expand_op(target, order=0, doc=None, alias=None, aliases=None):
    '''{docstring}'''
    return EXPAND_OPS.track_and_bind_op(target, order=order, doc=doc, alias=alias, aliases=aliases)

# # # ALL SIMPLIFY OR EXPAND OPS TO SKIP BY DEFAULT (FOR AT LEAST ONE CLASS) ANYWHERE IN SYMSOLVER # # #
SIMPLIFY_OPS_SKIP = Opname_to_Classes__Tracker()
EXPAND_OPS_SKIP   = Opname_to_Classes__Tracker()

def simplify_op_skip_for(target, fname):
    '''tell _simplify() to (by default) skip op with name (or alias) fname, for class (or subclass of) target.
    returns whether we just now added target to SIMPLIFY_OPS_SKIP (i.e. False if it was already being tracked).
    '''
    return SIMPLIFY_OPS_SKIP.track_target(fname, target)

def expand_op_skip_for(target, fname):
    '''tell _expand() to (by default) skip op with name (or alias) fname, for class (or subclass of) target.
    returns whether we just now added target to EXPAND_OPS_SKIP (i.e. False if it was already being tracked).'''
    return EXPAND_OPS_SKIP.track_target(fname, target)

def _simplification_ops_state_number():
    '''returns tuple of _state_number for SIMPLIFY_OPS, SIMPLIFY_OPS_SKIP, EXPAND_OPS, and EXPAND_OPS_SKIP.'''
    objs = (SIMPLIFY_OPS, SIMPLIFY_OPS_SKIP, EXPAND_OPS, EXPAND_OPS_SKIP)
    return tuple(getattr(obj, '_state_number') for obj in objs)


''' --------------------- Adjust defaults for which ops to skip --------------------- '''

# # # Adjust defaults for which SIMPLIFY ops to skip # # #
def simplify_op_DONT_skip(funcname, *targets, exact=False):
    '''changes default behavior for simplify op with this funcname --> "actually, DON'T skip it".
    Only does anything if funcname was previously provided to simplify_op_skip_for() at some point.
    *targets:
        if provided, only change default behavior of funcname for these classes and their subclasses.
    exact: bool, default False
        whether to ONLY do exact string matches (and no aliases) for funcname.

    returns list of funcnames that we now will NOT skip, due to calling this method.
    '''
    result = SIMPLIFY_OPS_SKIP.untrack(funcname, *targets)
    if (not exact) and (len(result) == 0):  # no exact matches to "retrack"
        if len(funcname) < 3:
            raise InputError(f'Crashing for safety due to very short funcname (len < 3) (funcname={repr(funcname)})')
        target_to_fnames = SIMPLIFY_OPS.target_lookup(funcname)
        result = []
        for target, fnames in target_to_fnames.items():
            for fname in fnames:
                untracked = SIMPLIFY_OPS_SKIP.untrack(fname, target)
                if len(untracked) > 0:
                    result.append(fname)
    else:
        result = [funcname] if (len(result) > 0) else []
    return result

def simplify_op_DO_skip(funcname, *targets, exact=False):
    '''changes default behavior for simplify op with this funcname --> "actually, DO skip it".
    Search for the funcname (actually, anything containing this string, unless exact) in SIMPLIFY_OPS,
    UNLESS skipping this exact funcname was previously requested at some point,
        AND the default is different than usual (likely due to a call to simplify_op_DONT_skip),
    *targets:
        if provided, only change default behavior of funcname for these classes and their subclasses.
    exact: bool, default False
        whether to ONLY do exact string matches (and no aliases) for funcname.

    returns list of funcnames that we now WILL skip, due to calling this method.
    '''
    result = SIMPLIFY_OPS_SKIP.retrack(funcname, *targets)
    if (not exact) and (len(result) == 0):  # no exact matches to "retrack"
        if len(funcname) < 3:
            raise InputError(f'Crashing for safety due to very short funcname (len < 3) (funcname={repr(funcname)})')
        target_to_fnames = SIMPLIFY_OPS.target_lookup(funcname)
        result = []
        for target, fnames in target_to_fnames.items():
            for fname in fnames:
                wasnt_already_skipping = simplify_op_skip_for(target, fname)
                if wasnt_already_skipping:
                    result.append(fname)
    else:
        result = [funcname] if (len(result) > 0) else []
    return result

SIMPLIFY_OPS.skip = simplify_op_DO_skip
SIMPLIFY_OPS.disable = simplify_op_DO_skip
SIMPLIFY_OPS.dont_skip = simplify_op_DONT_skip
SIMPLIFY_OPS.enable = simplify_op_DONT_skip

def restore_simplify_op_skip_defaults():
    '''restores default values for SIMPLIFY_OPS_SKIP.'''
    SIMPLIFY_OPS_SKIP.restore_defaults()

# # # Adjust defaults for which EXPAND ops to skip # # #
def expand_op_DONT_skip(funcname, *targets, exact=False):
    '''changes default behavior for expand op with this funcname --> "actually, DON'T skip it".
    Only does anything if funcname was previously provided to expand_op_skip_for() at some point.
    *targets:
        if provided, only change default behavior of funcname for these classes and their subclasses.
    exact: bool, default False
        whether to ONLY do exact string matches (and no aliases) for funcname.

    returns list of funcnames that we now will NOT skip, due to calling this method.
    '''
    result = EXPAND_OPS_SKIP.untrack(funcname, *targets)
    if (not exact) and (len(result) == 0):  # no exact matches to "retrack"
        if len(funcname) < 3:
            raise InputError(f'Crashing for safety due to very short funcname (len < 3) (funcname={repr(funcname)})')
        target_to_fnames = EXPAND_OPS.target_lookup(funcname)
        result = []
        for target, fnames in target_to_fnames.items():
            for fname in fnames:
                untracked = EXPAND_OPS_SKIP.untrack(fname, target)
                if len(untracked) > 0:
                    result.append(fname)
    else:
        result = [funcname] if (len(result) > 0) else []
    return result

def expand_op_DO_skip(funcname, *targets, exact=False):
    '''changes default behavior for expand op with this funcname --> "actually, DO skip it".
    Search for the funcname (actually, anything containing this string) in EXPAND_OPS,
    UNLESS skipping this exact funcname was previously requested at some point,
        AND the default is different than usual (likely due to a call to expand_op_DONT_skip),
    *targets:
        if provided, only change default behavior of funcname for these classes and their subclasses.
    exact: bool, default False
        whether to ONLY do exact string matches (and no aliases) for funcname.

    returns list of funcnames that we now WILL skip, due to calling this method.
    '''
    result = EXPAND_OPS_SKIP.retrack(funcname, *targets)
    if (not exact) and (len(result) == 0):  # no exact matches to "retrack"
        if len(funcname) < 3:
            raise InputError(f'Crashing for safety due to very short funcname (len < 3) (funcname={repr(funcname)})')
        target_to_fnames = EXPAND_OPS.target_lookup(funcname)
        result = []
        for target, fnames in target_to_fnames.items():
            for fname in fnames:
                wasnt_already_skipping = expand_op_skip_for(target, fname)
                if wasnt_already_skipping:
                    result.append(fname)
    else:
        result = [funcname] if (len(result) > 0) else []
    return result

EXPAND_OPS.skip = expand_op_DO_skip
EXPAND_OPS.disable = expand_op_DO_skip
EXPAND_OPS.dont_skip = expand_op_DONT_skip
EXPAND_OPS.enable = expand_op_DONT_skip

def restore_expand_op_skip_defaults():
    '''restores default values for EXPAND_OPS_SKIP.'''
    EXPAND_OPS_SKIP.restore_defaults()

# # # Adjust defaults for which OF ANY (i.e. simplify OR expand) ops to skip # # #
def simp_op_DONT_skip(funcname, *targets):
    '''changes default behavior for simplify OR expand op with this funcname --> "actually, DON'T skip it".
    Only does anything if funcname was previously provided to simplify_op_skip_for() OR expand_op_skip_for() at some point.
    *targets:
        if provided, only change default behavior of funcname for these classes and their subclasses.
    '''
    simplify_op_DONT_skip(funcname, *targets)
    expand_op_DONT_skip(funcname, *targets)

def simp_op_DO_skip(funcname, *targets):
    '''changes default behavior for simplify OR expand op with this funcname --> "actually, DO skip it".
    Only does anything if funcname was previously provided to simplify_op_skip_for() OR expand_op_skip_for() at some point,
        AND the default is different than usual (likely due to a call to simplify_op_DONT_skip OR expand_op_DONT_skip)
    *targets:
        if provided, only change default behavior of funcname for these classes and their subclasses.
    '''
    simplify_op_DO_skip(funcname, *targets)
    expand_op_DO_skip(funcname, *targets)

def restore_simp_op_skip_defaults():
    '''restores default values for SIMPLIFY_OPS_SKIP and EXPAND_OPS_SKIP.'''
    restore_simplify_op_skip_defaults()
    restore_expand_op_skip_defaults()


''' --------------------- SimplifiableObject class --------------------- '''

class SimplifiableObject(SymbolicObject):
    '''iterable symbolic object with simplification routines to apply recursively.

    Simplification routines with underscore apply directly to current layer, only;
    without underscore apply to all layers recursively.
    E.g. _flatten() will flatten this later; flatten() will flatten all layers.

    self.apply('s') applies routine named 's' or '_s' recursively where available.
    self.simplify applies all simplification routines at each layer.
    self._simplify applies all simplification routines at this layer.
    self.expand applies all expansion routies at each layer.
    self._expand applies all expansion routines at this layer.
    self.simplified applies all simplification and expansion routines at each layer.
    self._simplified applies all simplification and expansion routines at this layer.
    '''
    _SIMPLIFY_OPS = SIMPLIFY_OPS.tracked_ops_property('_cached_simplify_ops',
        doc='''The ops to use in _simplify. List of strings with leading underscore. Order matters.
        Determined automatically based on the SIMPLIFY_OPS associated with type(self).''')

    _EXPAND_OPS = EXPAND_OPS.tracked_ops_property('_cached_expand_ops',
        doc='''The ops to use in _expand. List of strings with leading underscore. Order matters.
        Determined automatically based on the EXPAND_OPS associated with type(self).''')

    _SIMPLIFY_OPS_SKIP = SIMPLIFY_OPS_SKIP.tracked_ops_property('_cached_simplify_ops_skip',
        doc='''The simplify ops to SKIP by default. List of strings with leading underscore. Order doesn't matter.
        Determined automatically based on the SIMPLIFY_OPS_SKIP associated with type(self) or parents of self.''')

    _EXPAND_OPS_SKIP = EXPAND_OPS_SKIP.tracked_ops_property('_cached_expand_ops_skip',
        doc='''The simplify ops to SKIP by default. List of strings with leading underscore. Order doesn't matter.
        Determined automatically based on the SIMPLIFY_OPS_SKIP associated with type(self) or parents of self.''')

    # Whether to do caching. None --> use abstract_operations.CACHING_OPS
    _simplification_ops_state_number = property(lambda self: _simplification_ops_state_number())

    # # # APPLY FUNC TO ALL LAYERS OF SELF # # #
    @caching_attr_with_params_and_state_if(lambda: DEFAULTS.CACHING_OPS,
            state=lambda self: _simplification_ops_state_number, clear_cache_on_new_state=True,
            ignore=['timeout', '_top', '_firsttime', 'debug'])
    def _f_all_layers(self, _f, *args__f, timeout=NO_VALUE, _top=True, bottom_up=False,
                      _firsttime=True, max_depth=None, apply_if=lambda self: True, **kw__f):
        '''Applies _f to all layers of self.
        does top layer first, then works down to inner-most layer.
        repeats on current layer until _f stops changing self.
        timeout: NO_VALUE, None, or number. Default NO_VALUE
            timeout after this many seconds have passed.
            NO_VALUE --> use DEFAULTS.TIMEOUT_SECONDS
            None --> never time out.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if not apply_if(self):
            return self
        if max_depth == 0:
            return self
        # # HANDLE TIMEOUT # #
        if timeout is NO_VALUE:
            timeout = DEFAULTS.TIMEOUT_SECONDS
        if _top:
            _timeout_warned[0] = False
        if timeout is not None and timeout <= 0:
            if not _timeout_warned[0]:
                warn_Timeout('Timed out during {} for self with id=({})'.format(_f, hex(id(self))))
                _timeout_warned[0] = True
            return self 
        tstart = time.time()
        def time_remaining():
            return None if timeout is None else (timeout - (time.time() - tstart))
        # kw management:
        kw_internal = dict(_top=False, bottom_up=bottom_up,
                           max_depth=None if max_depth is None else max_depth - 1)
        # # APPLY AT TOP LAYER # #
        if not (bottom_up and _firsttime):
            prev_self = None
            while prev_self is not self:
                prev_self = self
                self = apply(self, _f, *args__f, timeout=time_remaining(), **kw_internal, **kw__f)
        # # APPLY AT ONE LAYER DOWN # #
        if not isinstance(self, SimplifiableObject):
            result = self
        else:  # otherwise, apply to terms (one layer down)
            terms = []
            changed_any_terms = False
            try:
                terms = list(iter(self))
            except TypeError:
                result = self
            else: # self is iterable, so apply to all terms in self.
                for i, t in enumerate(terms):
                    if not isinstance(t, SimplifiableObject):
                        continue
                    t_prev = t
                    t_new = t._f_all_layers(_f=_f, *args__f, timeout=time_remaining(), **kw_internal, **kw__f)
                    terms[i] = t_new
                    if t_new is not t_prev:
                        changed_any_terms = True
                if changed_any_terms:
                    result = self._new_after_simp(*terms)
                else:
                    result = self # return self, exactly, to indicate no terms were changed.
                # if we changed anything, call at top layer again.
                if changed_any_terms or (bottom_up and _firsttime):
                    if isinstance(result, SimplifiableObject):
                        result = result._f_all_layers(_f=_f, *args__f, timeout=time_remaining(), **kw_internal, _firsttime=False, **kw__f)
        # # CACHE THEN RETURN RESULT # #
        return result

    _new_after_simp = SymbolicObject._new  # _f_all_layers uses _new_after_simp; subclasses can override.

    apply_internal = internal_apply = _f_all_layers   # aliases

    def apply(self, f, *args__f, **kw__f):
        '''Applies f to all layers of self.
        same as _f_all_layers, except that we first impose f starts with '_'.
        If it doesn't start with '_' yet, put a '_' in front.
        E.g. self.apply('distribute') == self.apply('_distribute')
        '''
        _f = '_' + f if f[0]!='_' else f
        return self._f_all_layers(_f, *args__f, **kw__f)

    # # # SIMPLIFY OR EXPAND USING ALL RELEVANT OPS # # #
    def _ops_to_do(self, _ATTR_OPS, _ATTR_OPS_SKIP, _OPS_ALIASES, only=None, **kw__ops):
        '''tells which ops to do.
        _ATTR_OPS: str
            attr name for default list of ops to do. '_SIMPLIFY_OPS' or '_EXPAND_OPS'.
        _ATTR_OPS_SKIP: str
            attr name for default list of ops to skip. '_SIMPLIFY_OPS_SKIP' or '_EXPAND_OPS_SKIP'.
        _OPS_ALIASES: dict
            dict with key opname, value list of aliases for op. 
        only: None (default) or list of strings (operation names)
            (can put any aliases of ops, i.e. with/without leading underscore, and from SIMPOP_ALIASES)
            None --> ignore this kwarg.
            else --> skip all ops not listed here.
        **kw__ops:
            (can put any aliases of ops, i.e. with/without leading underscore, and from SIMPOP_ALIASES)
            Any op here will either be performed or not, according to bool(kwargs's value).
                E.g. _ops_to_do(..., collect=False)
                    --> skip '_collect', 'collect', and any op in self._ATTR_OPS with '_collect' as an alias.
                    Equivalent to _ops_to_do(..., _collect=False).
        '''
        ops_to_do = []
        for _opstr in getattr(self, _ATTR_OPS):
            # get aliases for _opstr -- we will need to check all of these.
            _simpop_aliases = _OPS_ALIASES.get(_opstr, ())
            _aliases = (_opstr,          # original _opstr
                       *_simpop_aliases) # all aliases to _opstr
            aliases = set(al for _al in _aliases
                       for al in (_al, _op2op(_al, lenient=True)))  # test with AND without leading underscores.
            # check 'only' for all aliases.
            if only is not None:
                for al in aliases:
                    if al in only:
                        break
                else: # didn't break, i.e. _opstr and its aliases aren't in 'only'.
                    continue  # don't add _opstr to ops_to_do.
            # check kwargs for all aliases.
            for al in aliases:
                try:
                    do_op = kw__ops[al]
                except KeyError:
                    pass
                else:
                    break
            else:  # didn't break, i.e. never found _opstr or aliases in kw__ops.
                # since kwargs didn't control op, default is to do op if not in _ATTR_OPS_SKIP.
                do_op = _opstr not in getattr(self, _ATTR_OPS_SKIP)
            # finally, put in ops_to_do
            if do_op:
                ops_to_do.append(_opstr)
        return ops_to_do

    def _simplify_ops_to_do(self, only=None, **kw):
        '''tells which ops to do, for simplify.
        only: None (default) or list of strings (operation names)
            only do the operations listed here. (insensitive to leading underscore.)
        returns self._ops_to_do('_SIMPLIFY_OPS', '_SIMPLIFY_OPS_SKIP', SIMPLIFY_OPS.aliases, only=only, **kw).
        '''
        return self._ops_to_do('_SIMPLIFY_OPS', '_SIMPLIFY_OPS_SKIP', SIMPLIFY_OPS.aliases, only=only, **kw)

    def _expand_ops_to_do(self, only=None, **kw):
        '''tells which ops to do, for expand.
        only: None (default) or list of strings (operation names)
            only do the operations listed here. (insensitive to leading underscore.)
        returns self._ops_to_do('_EXPAND_OPS', '_EXPAND_OPS_SKIP', EXPAND_OPS.aliases, only=only, **kw).
        '''
        return self._ops_to_do('_EXPAND_OPS', '_EXPAND_OPS_SKIP', EXPAND_OPS.aliases, only=only, **kw)

    # # # SIMPLIFY # # #
    def _simplify(self, only=None, debug=False, ignoring=(),
                  stop_if=lambda x: False,
                  _top=True, timeout=NO_VALUE,
                  **kwargs):
        '''simplify this layer of self, using all _SIMPLIFY_OPS.
        (skips ops in _DEFAULT_FALSE_OPS, by default.)
        ops can be turned on/off via opname=True/False in kwargs.
        E.g. to turn off _collect, do _simplify(..., collect=False, ...)

        only: None (default) or list of strings (operation names)
            only do the operations listed here. (insensitive to leading underscore.)
        ignoring: iterable, default empty tuple
            values to ignore (i.e., set to 0).
            If result of any operation equals this value, return 0 immediately.
        if stop_if(self) (or stop_if(result of doing a simplification)),
            stop immediately and return the result.
        timeout: NO_VALUE, None, or number. Default NO_VALUE
            timeout after this many seconds have passed.
            NO_VALUE --> use DEFAULTS.TIMEOUT_SECONDS
            None --> never time out.
        debug: bool or int, default False
            whether to show debug info / how much debug info to show.
            False --> don't show any.
            True or >=1 --> show when this operation changes something.
            >=2 --> always show self to which this operation is applied.
            >=3 --> always show all EXPAND_OPS which are attempted.
            [TODO] make debug even prettier by tracking layer & adding tabs.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        # debugging stuff
        explain = maybe_viewer(on=debug)
        explain(f'<<< start _simplify for {type(self).__name__} at <{hex(id(self))}>:', view=self, queue=(debug<2))
        if debug >= 4: explain('  -- repr --> ' + repr(self))
        orig_self = self
        # ignoring stuff
        if any(equals(self, ig) for ig in ignoring):
            explain('Ignoring value (using 0 instead), indicated by "ignoring" kwarg.')
            return ZERO
        # timeout stuff
        if timeout is NO_VALUE: timeout = DEFAULTS.TIMEOUT_SECONDS
        tstart = time.time()
        def time_remaining():
            return None if timeout is None else (timeout - (time.time() - tstart))
        # figure out which ops to do. (figure this out beforehand, since the loop might change self.)
        ops_to_do = self._simplify_ops_to_do(only=only, **kwargs)
        # apply simplifying ops
        for _opstr in ops_to_do:
            # >> actually do op here <<
            if debug >= 3: explain(f'attempting {repr(_opstr)}', end='')
            prev_self = self
            self = apply(self, _opstr, _top=False, timeout=time_remaining(), debug=debug, **kwargs)
            if debug: # << [EFF] for efficiency, not necessary though (see help(maybe_viewer))
                if prev_self is self:
                    if debug >= 3: explain(f' (result unchanged)')
                else:
                    explain(f'  > changed by {repr(_opstr)} into this {type(self).__name__}: (id={hex(id(self))})', view=self)
            if any(equals(self, ig) for ig in ignoring):
                explain('Ignoring value (using 0 instead), indicated by "ignoring" kwarg.')
                return ZERO
            if not isinstance(self, SimplifiableObject) or stop_if(self):
                break
        if debug>=2 and (self is orig_self):
            explain(f' ... (no changes from _simplify)')
        return self

    def simplify(self, _loop=True, _top=True, only=None, **kw__simplify):
        '''simplify all layers of self. if _loop, keep looping up and down until there are no changes.
        (first simplify_id at all layers of self... [TODO] make this more generic..)
        '''
        if _top:
            debug = kw__simplify.get('debug', 0)
            if debug >= 4: print('--->>> INSIDE SIMPLIFY_ID <<<---')
            self = self.simplify(only=['simplify_id'], _loop=_loop, _top=False, **kw__simplify)
            if debug >= 4: print('---<<< OUTSIDE SIMPLIFY_ID >>>---')
            if not hasattr(self, '_f_all_layers'):
                return self
        kw__simplify['only'] = only
        result = self._f_all_layers(_f='_simplify', _top=False, **kw__simplify)
        if (result is self) or (not _loop):
            return result
        # if _loop, keep looping until there are no changes.
        rprev = None
        r = result
        while r is not rprev:
            rprev = r
            r = apply(r, '_f_all_layers', _f='_simplify', _top=False, **kw__simplify)
        return r

    # # # EXPAND # # #
    def _expand(self, only=None, ignoring=(),
                stop_if=lambda x: False,
                _top=True, timeout=NO_VALUE,
                debug=False,
                **kwargs):
        '''expand this layer of self.
        TODO: encapsulate instead of copy-pasting from _simplify.

        only: None (default) or list of strings (operation names)
            only do the operations listed here. (insensitive to leading underscore.)
        ignoring: iterable, default empty tuple
            values to ignore (i.e., set to 0).
            If result of any operation equals this value, return 0 immediately.
        if stop_if(self) (or stop_if(result of doing a simplification)),
            stop immediately and return the result.
        timeout: NO_VALUE, None, or number. Default NO_VALUE
            timeout after this many seconds have passed.
            NO_VALUE --> use DEFAULTS.TIMEOUT_SECONDS
            None --> never time out.
        debug: bool or int, default False
            whether to show debug info / how much debug info to show.
            False --> don't show any.
            True or >=1 --> show when this operation changes something.
            >=2 --> always show self to which this operation is applied.
            >=3 --> always show all EXPAND_OPS which are attempted.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        explain = maybe_viewer(on=debug)
        explain(f'>>> start _expand for {type(self).__name__} at <{hex(id(self))}>:', view=self, queue=(debug<2))
        orig_self = self
        # ignoring stuff
        if any(equals(self, ig) for ig in ignoring):
            explain('Ignoring value (using 0 instead), indicated by "ignoring" kwarg.')
            return ZERO
        # timeout stuff
        if timeout is NO_VALUE: timeout = DEFAULTS.TIMEOUT_SECONDS
        tstart = time.time()
        def time_remaining():
            return None if timeout is None else (timeout - (time.time() - tstart))
        # figure out which ops to do. (figure this out beforehand, since the loop might change self.)
        ops_to_do = self._expand_ops_to_do(only=only, **kwargs)
        # apply expanding ops
        for _opstr in ops_to_do:
            # >> actually do op here <<
            if debug >= 3: explain(f'attempting {repr(_opstr)}', end='')
            prev_self = self
            self = apply(self, _opstr, _top=False, timeout=time_remaining(), debug=debug, **kwargs)
            if debug: # << [EFF] for efficiency, not necessary though (see help(maybe_viewer))
                if prev_self is self:
                    if debug >= 3: explain(f' (result unchanged)')
                else:
                    explain(f'  > changed by {repr(_opstr)} into this {type(self).__name__}: (id={hex(id(self))})', view=self)
            if any(equals(self, ig) for ig in ignoring):
                explain('Ignoring value (using 0 instead), indicated by "ignoring" kwarg.')
                return ZERO
            if not isinstance(self, SimplifiableObject) or stop_if(self):
                break
        if debug>=2 and (self is orig_self):
            explain(f' ... (no changes from _expand)')
        return self

    def expand(self, **kw__expand):
        '''expands at all layers of self.'''
        return self._f_all_layers(_f='_expand', _top=False, **kw__expand)

    ## EXPAND AND SIMPLIFY ##
    def _anneal(self, **kw):
        '''expand and simplify this layer of self.
        (doesn't collect when simplifying.)
        '''
        self = apply(self, '_expand', **kw)
        self = apply(self, '_simplify', collect=False, **kw)
        return self

    def anneal(self, **kw):
        '''expand then simplify at each layer, for all layers of self.'''
        return self._f_all_layers(_f='_anneal', _top=False, **kw)

    ## CONVENIENCE ##
    def _simple_simplify(self):
        '''simplifies top layer of self using _flatten and _simplify_id,
        then _evaluate_numbers with evalue_abstract_only=True.
        '''
        self = apply(self, '_flatten')
        self = apply(self, '_simplify_id')
        self = apply(self, '_evaluate_numbers')
        return self

    def simplified(self, loop=False, LMAX=50, timeout=NO_VALUE, print_freq=2, **kw):
        '''returns self.expand().simplify().
        if loop, repeat until self stops changing or LMAX iterations have been performed.
        timeout: NO_VALUE, None, or number. Default NO_VALUE
            timeout after this many seconds have passed.
            NO_VALUE --> use DEFAULTS.TIMEOUT_SECONDS
            None --> never time out.
        '''
        updater = ProgressUpdater(print_freq=print_freq)
        if timeout is NO_VALUE: timeout = DEFAULTS.TIMEOUT_SECONDS
        tstart = time.time()
        def time_remaining():
            return None if timeout is None else (timeout - (time.time() - tstart))
        orig_self = self
        self = apply(self, 'expand', timeout=time_remaining(), **kw)
        self = apply(self, 'simplify', timeout=time_remaining(), **kw)
        if loop:
            i = 1
            while (i < LMAX) and (not equals(self, orig_self)):
                updater.print('Looping during simplified. At iteration i={}'.format(i), print_time=True)
                i += 1
                orig_self = self
                self = apply(self, 'expand', timeout=time_remaining(), **kw)
                self = apply(self, 'simplify', timeout=time_remaining(), **kw)
            if i >= LMAX:
                warnmsg_max_iterations = ('stopped simplified() for object <{}> after LMAX(={}) iterations;'
                                          'result might be not in simplest form.').format(hex(id(self)), LMAX)
                warn(warnmsg_max_iterations)
        updater.finalize()
        return self
