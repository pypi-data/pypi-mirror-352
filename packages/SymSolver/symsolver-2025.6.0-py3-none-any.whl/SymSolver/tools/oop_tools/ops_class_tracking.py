"""
File Purpose: OpsClassTracking
track ops associated with class(es).

Tracking operations to apply to each class and (whether to apply them to) its subclasses can be difficult.
It is especially difficult if one wishes to use same-named aliases for these functions.
In SymSolver, one example is the _simplify_id() operations.
    There are many of them, including
        _sum_simplify_id, _commutative_simplify_id, _product_simplify_id.
    But _sum_simplify_id starts out by calling _commutative_simplify_id,
    so we don't want to call _commutative_simplify_id again right away.
How can we track which ops to call for a class and all its subclasses,
while also allowing to skip some by default, but sometimes don't skip them if user wishes?
    Maybe there is an elegant solution, but we didn't figure one out.
    Instead, we use the code in this file to facilitate the solution.

OpClassMeta
    provides meta info about a single op and class
    and relative order to apply the op (if there are other ops tracking this class)

Opname_to_OpClassMeta__Tracker
    tracks many pieces of OpClassMeta.
    using subordering_for_class(cls) tells all ops to use on cls, in order.
"""
import textwrap
import collections

from .binding import (
    Binding,
)
from ..properties import (
    alias, alias_in,
)
from ..display import (
    help_str,
)
from ..finds import find, multifind
from ...errors import InputError
from ...defaults import DEFAULTS

binding = Binding(locals())


''' --------------------- Meta --------------------- '''

class OpClassMeta():
    '''stores meta-info about class-tracking operation.
    f: callable object
        the "op" associated with this object.
    target: type
        the "class" associated with this object.
        "f tracks target" (and possibly other targets we don't know about here.)
    order: number, default 0
        relative order for applying f to target. (lower --> apply sooner)
        relative compared to other tracked ops for target.
    doc: None or string
        more notes/info associated with this tracking meta.
        note: currently, not much implemented to interact with doc besides tracking it.
        (e.g. doc won't appear in repr or str of self.)
    '''
    def __init__(self, f, target=None, order=0, doc=None):
        if not callable(f):
            raise TypeError('expected callable f.')
        self.f = f
        self.order = order
        self.target = target
        self.doc = doc

    def __getitem__(self, i):
        if i==0:
            return self.f
        elif i==1:
            return self.order
        elif i==2:
            return self.target
        else:
            raise KeyError(i)


''' --------------------- Tracking Meta for multiple Ops --------------------- '''

class Opname_to_OpClassMeta__Tracker():
    '''track many OpClassMeta values. All keys must be unique.
    keys = fname, values = OpClassMeta value associated with fname.
    
    Convenient behaviors for end-user:
        print(self) shows which ops are in self.
        self.help() gives docs on all ops in self.
        self(cls) tells ops associated with class cls, ordered appropriately by order parameter.

        self.aliases maps fnames to aliases
        self.alias_to_originals maps aliases to original fnames
        self.lookup(s) looks up s in original fnames and in aliases.
    '''
    def __init__(self):
        self.ops = dict()
        self.aliases = dict()
        self.alias_to_originals = dict()
        self._state_number = 0
        self._reset_cache()

    state_number = property(lambda self: self._state_number,
        doc='''state number of self. If state number has not changed, results will be the same
        e.g. same results from self.ordering, iter(self), self.subordering, etc.''')

    def _reset_cache(self):
        '''resets cache, and increments state_number.'''
        self._state_number += 1
        self._target_ordered_cache = {} # cache of orderings associated with classes. keys will be classes (which are hashable).
        self._target_unordered_cache = {} # cache of unordered fname lists associated with classes. keys will be classes.

    # # # TRACK NEW OP # # #
    def track_op(self, f, target, order=0, doc=None, alias=None, aliases=None):
        '''adds f to self using key=f.__name__.

        f: callable object
            the "op" associated with this meta info
        target: type
            the "class" associated with this meta info. think: "f tracks target"
        order: number, default 0
            relative order for applying f to target. (lower --> apply sooner)
            relative compared to other ops tracked in self for target (or any of target's parents)
        doc: None or string
            more notes/info associated with this tracking meta.
            note: currently, not much implemented to interact with doc.
        alias: None or string
            if provided, tell self that this is an alias of f.
        aliases: None or iterable of strings
            if provided, tell self that these are aliases of f.

        returns fname, meta
        '''
        meta = OpClassMeta(f, target, order=order, doc=doc)
        fname, meta = self.track_op_meta(meta)
        if alias is not None:
            self.track_alias(fname, alias)
        if aliases is not None:
            for alias in aliases:
                self.track_alias(fname, alias)
        return fname, meta

    def track_op_meta(self, meta):
        '''adds OpClassMeta to self at key meta.f.__name__
        returns fname, meta.'''
        if not isinstance(meta, OpClassMeta):
            raise TypeError(f'expected OpClassMeta but got object of type {type(meta).__name__}')
        f = meta.f
        fname = f.__name__
        if fname in self.keys():
            raise KeyError(f"expected all fnames to be unique but got repeat: {fname}")
        self.ops[fname] = meta
        self._reset_cache()
        return fname, meta

    def track_alias(self, fname, alias):
        '''tells self that alias is an alias for op with name fname.'''
        if not fname in self.keys():
            raise KeyError(f'{repr(fname)} not in self.keys()')
        try:
            self.aliases[fname].append(alias)
        except KeyError:
            self.aliases[fname] = [alias]
        try:
            self.alias_to_originals[alias].append(fname)
        except KeyError:
            self.alias_to_originals[alias] = [fname]

    def alias_lookup(self, s, mode='both'):
        '''look up s in all fnames and all aliases.
        returns dict with all keys containing s in the key.

        mode: 'both', 'alias', or 'original'
            'alias' --> lookup in aliases; values are lists of aliases.
                        keys are keys of self.aliases, i.e. keys are original fnames.
            'original' --> lookup in alias_to_originals; values are lists of original fnames.
                        keys are keys of self.alias_to_originals, i.e. keys are aliases.
            'both' --> lookup in aliases then in originals; combine the results into 1 dict.
        '''
        if mode == 'alias':
            return {key: val for key, val in self.aliases.items() if s in key}
        elif mode == 'original':
            return {key: val for key, val in self.alias_to_originals.items() if s in key}
        elif mode == 'both':
            aliases = self.alias_lookup(s, 'alias')
            originals = self.alias_lookup(s, 'original')
            return {**aliases, **originals}
        else:
            errmsg = f"Invalid mode; expected one of ['alias', 'original', 'both'], but got mode={repr(mode)}"
            raise InputError(errmsg)

    def target_lookup(self, s):
        '''returns dict of targets --> list of unique fnames,
        for which s appears in fname or in alias to fname, for target.
        (result contains only the actual fnames, not any aliases.)
        '''
        result = collections.defaultdict(list)
        a_to_o = self.alias_lookup(s, 'original')
        o_to_a = self.alias_lookup(s, 'alias')
        fnames = [*o_to_a.keys(), *[fname for fnames in a_to_o.values() for fname in fnames]]
        for fname in fnames:
            target = self[fname].target
            if fname not in result[target]:
                result[target].append(fname)
        return dict(result)

    # # # USEFUL METHOD -- TRACK AND BIND, AS A FUNCTION DECORATOR # # #
    def track_and_bind_op(self, target, order=0, doc=None, alias=None, aliases=None):
        '''returns a function decorator deco(f) which adds f to self AND binds f to target.

        target: type
            the "class" associated with this meta info. think: "f tracks target"
            the function being decorated will be bound to target, at attribute name f.__name__.
        order: number, default 0
            relative order for applying f to target. (lower --> apply sooner)
            relative compared to other ops tracked in self for target (or any of target's parents)
            in case of tie, all tied funcs might be applied in any order.
        doc: None or string
            more notes/info associated with this tracking meta.
            note: currently, not much implemented to interact with doc.
        alias: None or string
            if provided, tell self that this is an alias of f,
            and also sets target.(alias) to point to target.(f.__name__).
        aliases: None or list of strings
            if provided, tell self that these are aliases of f.
            Similar to alias but allows to provide multiple values.
        '''
        def track_and_bind_then_return_f(f):
            fname, meta = self.track_op(f, target, order=order, doc=doc, alias=alias, aliases=aliases)
            setattr(target, fname, f)
            if alias is not None:
                alias_in(target, fname, alias)
            return f
        return track_and_bind_then_return_f

    # # # DICT-LIKE BEHAVIOR # # #
    def __getitem__(self, fname):
        '''get OpClassMeta value associated with fname in self.'''
        return self.ops[fname]

    def keys(self): return self.ops.keys()
    def values(self): return self.ops.values()
    def items(self): return self.ops.items()
    def __len__(self): return len(self.ops)
    def __iter__(self): return iter(self.keys())
    def __contains__(self, key): return key in self.ops

    # # # ORDERING # # #
    def order_sort(self, fnames):
        '''sorts fnames according to order parameters. Does not attempt caching.'''
        return sorted(fnames, key=lambda fname: self[fname].order)

    # # # ITERATE # # #
    def class_ops_unordered(self, target, caching=True):
        '''returns keys in self associated with target, in no particular order.
        "association" is determined by subclassing. i.e. issubclass(target, self[key].target)
        Caches result (if caching=True); cache clears if any items are added or changed in self.
        '''
        if caching:
            try:
                return self._target_unordered_cache[target]
            except KeyError:
                pass  # didn't find in cache. handled below.
        result = [fname for fname, fmeta in self.items() if issubclass(target, fmeta.target)]
        if caching:
            self._target_unordered_cache[target] = result
        return result

    def subordering_for_class(self, target):
        '''returns ordering for keys in self associated with target, respecting order parameter from OpClassMeta.
        "association" is determined by subclassing. i.e. issubclass(target, self[key].target)
        Caches result; cache clears if any items are added or changed in self.
        '''
        try:
            return self._target_ordered_cache[target]
        except KeyError:
            pass  # didn't find in cache, handled below
        _fnames_for_class = self.class_ops_unordered(target, caching=False)
        result = self.order_sort(_fnames_for_class)
        self._target_ordered_cache[target] = result  # put in cache
        return result

    def class_ops_iter(self, target):
        '''iterates through keys in self associated with target, ordered by self.subordering_for_class(target)'''
        for fname in self.subordering_for_class(target):
            yield fname

    # # # CONVENIENCE METHOD -- CALL <--> subordering_for_class # # #
    __call__ = alias('subordering_for_class')  # enables self(cls) --> self.subordering_for_class(cls)

    # # # USEFUL METHOD -- TRACKED OPS FOR CLASS, PROPERTY MAKER # # #
    def tracked_ops_property(self, cache_attr, doc=None):
        '''returns a property that gives self.subordering_for_class(type(instance where property is used)).
        
        cache_at: string
            attribute for --instance where property is used-- in which to cache result.
            This is required to help ensure the lookups are fast, if repeated.
        doc: None or string
            doc for the property.
        '''
        def get_subordering_for_instance(obj):
            '''getter method for the property being defined here.
            Handles caching, and returns self.subordering_for_class(type(obj)).
            '''
            obj_cls = type(obj)
            # caching
            try:
                cached = obj_cls.__dict__[cache_attr]  # __dict__, not getattr, in case of subclassing.
            except KeyError:
                pass  # result wasn't cached; we will calculate after the 'else' block.
            else:
                if cached[0] == self._state_number:
                    return cached[1]
            # result
            result = self.subordering_for_class(obj_cls)
            # caching
            setattr(obj_cls, cache_attr, (self._state_number, result))
            # result
            return result

        return property(get_subordering_for_instance, doc=doc)


''' --------------------- Tracking Meta for multiple Ops --------------------- '''

class Opname_to_Classes__Tracker():
    '''track list of classes for each opname.
    keys = fname, values = list of classes associated with fname.

    if a key has an empty list as its value, it indicates some target(s) have been removed;
    you can use self.retrack(key) to restore those targets, or check self.untracked to see which were removed.
    You can also use self.retrack_all() to restore all removed targets across all keys.

    Convenient methods for end-user:
        self(cls) tells op names associated with class cls.
    '''
    def __init__(self):
        self.ops = {}   # keys=fname, values=targets (classes associated with fname)
        self._state_number = 0
        self._reset_cache()

    state_number = property(lambda self: self._state_number,
        doc='''state number of self. If state number has not changed, results will be the same.''')

    def _reset_cache(self):
        self._state_number += 1
        self._target_unordered_cache = {} # cache of unordered fname lists associated with classes. keys will be classes.

    # # # TRACK NEW OP # # #
    def track_op(self, fname, *targets):
        '''adds fname to self using key=fname, targets=targets.

        fname: string
            key to add to self, with targets.
        targets: classes
            associated with fname, within context of self.
        '''
        if fname in self.keys():
            raise KeyError(f"expected all fnames to be unique but got repeat: {fname}")
        self.ops[fname] = list(targets)
        self._reset_cache()

    def track_target(self, fname, target):
        '''adds single target to self at key=fname.
        if already tracking fname, append target to its list,
            unless target already in its list, in which case do nothing.
        else start tracking fname with list [target].

        returns whether target was just now added to tracking (i.e. False if was already being tracked).
        '''
        try:
            sf = self[fname]
        except KeyError:
            self.track_op(fname, target)
            return True
        else:
            if target in sf:
                return False
            else:
                sf.append(target)
                return True

    # # # STOP TRACKING OP # # #
    def del_op(self, fname, *targets, require_exists=False):
        '''removes op(s) from self:
            if len(targets)>0, remove these targets from self[fname]
            else: remove all targets associated with fname.

        require_exists: bool, default False
            whether to require values to exist in self before removing them.
            if True, require all values to exist, else raise ValueError.
                if ANY values don't exist, raises ValueError before making any changes to self.

        returns list of all the deleted targets from self[fname].
        '''
        result = []
        try:
            sf = self[fname]
        except KeyError:
            if require_exists:
                raise ValueError(f'fname {fname} not found in self') from None
            else:
                return []
        if len(targets)==0:
            targets_idx = range(len(sf))
        else:
            targets_idx = multifind(sf, targets, default=None, require_exists=require_exists, force_unique=True)
            if not require_exists:  # (no None values allowed if require_exists)
                targets_idx = (i for i in targets_idx if i is not None)  # ignore the None values.
        for i in sorted(targets_idx, reverse=True): # sorting so we delete larger i first.
            result.append(sf.pop(i))
        self._reset_cache()
        return result

    def untrack(self, fname, *targets, exact=True):
        '''removes target(s) from self[fname]; remembers removed targets in case self.retrack is called later.
        Does not remove fname from self, even if no targets remain.
        if len(targets)==0, remove ALL targets from self[fname].

        remembered targets will be stored in self.untracked.

        exact: bool, default True
            whether to require exact matches for fname.
            False --> untrack any fnames in self which contain fname in their string,
                        as long as len(fname) >= 3, and there are no exact matches.

        returns (copy of) list of removed targets.
        '''
        removed = self.del_op(fname, *targets, require_exists=False)  # also handles self._reset_cache()
        if len(removed) == 0:
            if not exact: # search for non-exact matches
                if len(fname) < 3:
                    raise InputError(f'Crashing for safety due to very short fname (len < 3) (fname={repr(fname)})')
                fnames_to_untrack = [full_fname for full_fname in self.keys() if fname in full_fname]
                for fname_u in fnames_to_untrack:
                    removed += self.untrack(fname_u, *targets, exact=True)  # list addition
            return list(removed)  # << either an empty list, or list with names from non-exact matching.
        if fname in self.untracked:
            self.untracked[fname] += removed  # list addition
        else:
            self.untracked[fname] = removed
        return list(removed)

    @property
    def untracked(self):
        '''stores all the (fname, targets) which have been untrack()'ed from self.'''
        try:
            return self._untracked
        except AttributeError:
            self._untracked = dict()
            return self._untracked

    def retrack(self, fname, *targets, require_exists=False):
        '''adds target(s) to fname but ONLY if they appear in self.untracked[fname].
        if len(targets)==0, restore ALL targets from self.untracked[fname]

        require_exists: bool, default False,
            if True: if any of the targets (or fname) don't exist in self.untracked, raise ValueError.

        note: all retracked targets will be removed from self.untracked.

        returns (copy of) list of retracked targets.
        '''
        targets_to_retrack = []
        try:
            uf = self.untracked[fname]
        except KeyError:
            if require_exists:
                raise ValueError(f'fname {fname} not found in self.untracked.')
            else:
                return []
        if len(targets) == 0:
            targets_to_retrack = list(uf)
            targets_i_to_remove_from_uf = list(range(len(uf)))
        else:
            targets_to_retrack = []
            for target in targets:
                i = find(uf, target, default=None)
                if i is not None:
                    targets_to_retrack.append(target)
                    targets_i_to_remove_from_uf.append(i)
                elif require_exists:
                    raise ValueError(f'target {target} not found in self.untracked[{fname}]')
        # add targets to self[fname]
        sf = self[fname]
        for target in targets_to_retrack:
            sf.append(target)
        # remove targets from self.untracked[fname]
        for i in sorted(targets_i_to_remove_from_uf, reverse=True):  # reverse --> del large i first.
            del uf[i]
        # delete self.untracked[fname] if it has no targets remaining.
        if len(uf) == 0:
            del self.untracked[fname]
        # bookkeeping - reset cache
        self._reset_cache()
        # return result
        return targets_to_retrack

    def retrack_all(self):
        '''restores everything which has been untracked in self.
        returns (copy of) dict of what was retracked.
        '''
        result = dict()
        for fname in self.untracked:
            result[fname] = self.retrack(fname)
        return result

    # [TODO] make a better restore_defaults function...
    restore_defaults = alias('retrack_all')

    # # # DICT-LIKE BEHAVIOR # # #
    def __getitem__(self, fname):
        '''gets list of classes associated with fname in self.'''
        return self.ops[fname]

    def keys(self): return self.ops.keys()
    def values(self): return self.ops.values()
    def items(self): return self.ops.items()
    def __len__(self): return len(self.ops)
    def __iter__(self): return iter(self.keys())
    def __contains__(self, key): return key in self.ops

    # # # ITERATE # # #
    def class_ops_unordered(self, target, caching=True):
        '''returns keys in self associated with target, in no particular order.
        "association" is determined by subclassing. i.e. issubclass(target, self[key][i])
        Caches result (if caching=True); cache clears if any items are added or changed in self.
        '''
        if caching:
            try:
                return self._target_unordered_cache[target]
            except KeyError:
                pass  # didn't find in cache. handled below.
        result = [fname for fname, ftargets in self.items()
                    if any(issubclass(target, ft) for ft in ftargets)]
        if caching:
            self._target_unordered_cache[target] = result
        return result

    # # # CONVENIENCE METHOD -- CALL <--> class_ops_unordered # # #
    __call__ = alias('class_ops_unordered')  # enables self(cls) --> self.class_ops_unordered(cls)

    # # # USEFUL METHOD -- TRACKED OPS FOR CLASS, PROPERTY MAKER # # #
    def tracked_ops_property(self, cache_attr, doc=None):
        '''returns a property that gives self.class_ops_unordered(type(instance where property is used)).
        
        cache_attr: string
            attribute for --instance where property is used-- in which to cache result.
            This is required to help ensure the lookups are fast, if repeated.
        doc: None or string
            doc for the property.
        '''
        def get_fnames_for_instance(obj):
            '''getter method for the property being defined here.
            Handles caching, and returns self.class_ops_unordered(type(obj)).
            '''
            # caching
            try:
                cached = getattr(obj, cache_attr)
            except AttributeError:
                pass  # result wasn't cached; we will calculate after the 'else' block.
            else:
                if cached[0] == self._state_number:
                    return cached[1]
            # result
            result = self.class_ops_unordered(type(obj))
            # caching
            setattr(type(obj), cache_attr, (self._state_number, result))
            # result
            return result

        return property(get_fnames_for_instance, doc=doc)


''' --------------------- DISPLAY for Op Class Tracking Objects --------------------- '''

def _name_else_obj(obj):
    '''returns obj.__name__ if it exists, else obj.'''
    try:
        return obj.__name__
    except AttributeError:
        return obj

# # # DISPLAY: OP CLASS META # # #
with binding.to(OpClassMeta):
    # # # STR # # #
    OpClassMeta.fname = property(lambda self: _name_else_obj(self.f))
    OpClassMeta.targetname = property(lambda self: _name_else_obj(self.target))

    @binding
    def _params_str(self):
        '''returns string for order and target in self.'''
        return f'order={self.order}, target={self.targetname}'

    @binding
    def __str__(self):
        return f'{type(self).__name__}({self.fname}, {self._params_str()})'

    @binding
    def print(self, *args, **kw):
        '''builtins.print(self, *args, **kw)'''
        print(self, *args, **kw)

    # # # REPR AND HELP # # #
    @binding
    def __repr__(self):
        return f'{type(self).__name__} instance with f={self.f}. See self.help() or print(self) for more info.'

    @binding
    def help_str(self):
        '''returns help string for self.'''
        result = f'{type(self).__name__} with order={self.order}, target={self.targetname}, f=\n'
        result += help_str(self.f)
        return result

    OpClassMeta.helpstr = alias('help_str')

    @binding
    def help(self):
        '''prints self.help_str()'''
        print(self.help_str())


# # # DISPLAY: OPNAME TO OP CLASS META -- TRACKER # # #
with binding.to(Opname_to_OpClassMeta__Tracker):
    # # # STR # # #
    @binding
    def __str__(self):
        '''string of self'''
        # setup for pretty string
        pretty_newline = '' if len(self)<2 else '\n'
        maxlen = max(len(repr(key)) for key in self.keys())
        # strings of each key and value, then join them together.
        keys, values = zip(*sorted(self.items(), key=lambda item: item[0]))  # alphabetical by key.
        key_strs = (f'{repr(key).ljust(maxlen)}' for key in keys)
        val_strs = (f'<callable with that name>, {val._params_str()}' for val in values)
        items_strs = (f'{key_str} : {val_str}' for key_str, val_str in zip(key_strs, val_strs))
        items_str = ',\n'.join(items_strs)
        return f'{type(self).__name__}({pretty_newline}{items_str}{pretty_newline})'

    @binding
    def print(self, *args, **kw):
        '''builtins.print(self, *args, **kw)'''
        print(self, *args, **kw)

    # # # REPR AND HELP # # #
    @binding
    def __repr__(self):
        result = (f'{type(self).__name__} instance containing {len(self)} ops. '
                  'See self.help() or print(self) for more info.')
        return result

    @binding
    def help_str(self, only=None, tab=None):
        '''returns help string for self.
        only: None or str, default None
            None --> help on all ops in self
            str --> help on only the ops in self which contain this string
        tab: None or str, default None
            use for indent. None --> use DEFAULTS.STRINGREP_TAB
        '''
        if tab is None: tab = DEFAULTS.STRINGREP_TAB
        result = [f'{type(self).__name__} instance containing {len(self)} ops.',
                  'This object behaves like a dictionary; you can get any one of the keys by indexing.',
                  'The keys, and values (with full documentation strings), stored here are printed below.']
        if only is not None:
            result.append(f'\n(Showing here help for only the ops containing {repr(only)} in their name)')
        result = ['\n'.join(result)]  # << header block. blocks will be joined by '\n\n'.
        for key, val in self.items():
            if (only is not None) and (only not in key):
                continue
            key_result = f'{repr(key)}:\n\n'
            valhelp = val.help_str()
            key_result += textwrap.indent(valhelp, tab)
            result.append(key_result)
        return '\n\n'.join(result)

    Opname_to_OpClassMeta__Tracker.helpstr = alias('help_str')

    @binding
    def help(self, only=None):
        '''prints self.help_str().
        only: None or str, default None
            None --> help on all ops in self
            str --> help on only the ops in self which contain this string
                E.g. self.help('simplify_id') --> only the ops with 'simplify_id' in their name.
        '''
        print(self.help_str(only=only))


# # # DISPLAY: OPNAME TO CLASSES -- TRACKER # # #
with binding.to(Opname_to_Classes__Tracker):
    @binding
    def __repr__(self):
        items_str = ', '.join([f'{repr(key)}: {val}' for key, val in self.items()])
        return f'{type(self).__name__}({items_str})'