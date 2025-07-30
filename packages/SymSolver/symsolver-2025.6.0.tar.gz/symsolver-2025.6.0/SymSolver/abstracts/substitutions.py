"""
File Purpose: SubbableObject. See also SubstitutionInterface.
(directly subclasses SymbolicObject)

TODO:
    - option to sub many things at the same time. e.g. (x-->y and y-->x) implying (x/y) --> (y/x)
    - when value to sub is a numpy array, create a SymbolicNumpyArray object first.
        - [TODO] define the SymbolicNumpyArray class. The goal is to make an object which
          mostly behaves like numpy arays, but returns boolean on checks for equality,
          instead of returning array of booleans.
"""
from .symbolic_objects import (
    SymbolicObject,
    is_number,
    symdeplayers,
)
from ..attributors import attributor
from ..tools import (
    equals, apply,
    find, Set,
    walk,
    weakref_property_simple, structure_string, layers,
    array_info_str,
    ProgressUpdater,
    alias, caching_attr_simple_if,
    Binding,
)
from ..defaults import DEFAULTS, ZERO

binding = Binding(locals())


''' --------------------- Convenience Functions --------------------- '''

@attributor
def is_subbable(x):
    '''returns whether any substitutions could be performed in x.
    returns x.is_subbable() if available, else False.
    '''
    try:
        x_is_subbable = x.is_subbable
    except AttributeError:
        return False
    else:
        return x_is_subbable()

@attributor
def is_interface_subbable(x):
    '''returns whether x should appear as an option in a SubstitutionInterface.
    returns x.is_interface_subbable() if available, else False.
    '''
    try:
        x_is_interface_subbable = x.is_interface_subbable
    except AttributeError:
        return False
    else:
        return x_is_interface_subbable()

@attributor
def interface_subbables(x):
    '''returns list of subbables in x to appear as options in a SubstitutionInterface.
    returns x.interfaces_subbables if available, else [].
    '''
    try:
        x_interface_subbables = x.interface_subbables
    except AttributeError:
        return []
    else:
        return x_interface_subbables()


''' --------------------- SubbableObject --------------------- '''

class SubbableObject(SymbolicObject):
    '''provides rules for substitutions.

    Not intended to be instanced directly.
    Subclassing this class allows the subclass to have substitutions.

    For substitution functions, kw are propagated to all internal calls,
    in case a subclass wants to override that function and use kwargs.

    substitutions can be performed via:
        sub(old, new)
        sub_subscript(old, new)
        sub_everywhere(old, new)
        subs(*substitutions)
        subs_subscripts(*subscripts)
        subs_everywhere(*subs)

        aliases:
            replace    --> subs
            substitute --> subs
            ss             --> sub_subscript
            subscript_swap --> sub_subscript
            replace_subscripts --> subs_subscripts
            subsubs            --> subs_subscripts
            subssubs           --> subs_subscripts
            suball      --> sub_everywhere
            subsall     --> subs_everywhere
            replace_all --> subs_everywhere

    "substitute x for val, in self" means:
        if self == x:
            replace with val.
        elif self is iterable:
            for term in self:
                if term is a SubbableObject:
                    substitute x for val, in term
                else:
                    if term == x:
                        replace with val
        (note that "replace" means it will be replaced in the result, only.
        The original object will not be affected.)
    '''
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def is_subbable(self):
        '''returns whether any part of self might possibly be subbable.
        Numbers are defined to be unsubbable via this function.
        (A subclass could allow number substitutions by overriding this function.)
        [TODO] check efficiency -- is it faster to just try subbing, without first checking is_number?
        '''
        return (not is_number(self))

    # # # SUBSTITUTION HELPER FUNCTIONS # # #
    def _iter_substitution_terms(self, **kw__None):
        '''returns iterator over terms to check for substitution in self.
        default is to return iter(self), or [] if iter(self) makes TypeError.
        subclasses may want to overwrite this method instead of other substitution functions.
        E.g. option for EquationSystem to only consider "unsolved" equations for substitutions.
        '''
        try:
            return iter(self)
        except TypeError:
            return iter([])

    def _subs_check_term(self, term, *, _subbable_only=True, **kw__None):
        '''returns whether to check term during substitutions for self.
        Either way, term will still be included in the result.
        But, if result is False, term will not be checked for substitutions.

        The implementation here returns is_subbable(term) by default;
            i.e. skip non-subbable terms by default.

        _subbable_only: bool, default True
            whether to return is_subbable(term).
            False --> just return True. i.e. don't skip any terms.

        kw will be passed into this function from _substition_loop,
            i.e. this function will see all kwargs entered to any substitions method.
        '''
        return is_subbable(term) if _subbable_only else True

    def _new_after_subs(self, *post_subs_terms, **kw__new):
        '''returns new object like self after making appropriate substitutions from iter_substitution_terms.
        The implementation here just returns self._new(*post_subs_terms).
        subclasses may want to overwrite this method instead of other substitution functions.
        E.g. SummationOperator overwrites _iter_substitution_terms AND _new_after_subs,
            such that the 'summation index' is not checked for substitutions,
            while the 'imin', 'imax', and 'iset' are all checked for substitutions.
        '''
        return self._new(*post_subs_terms, **kw__new)

    def _substitution_loop(self, rule, **kw):
        '''the core loop of all substitution functions.
        Applies rule to all subbable terms in self._iter_substitution_terms(**kw),
        returning self._new_after_subs(*new_terms) if any terms were changed, else self.

        rule: callable accepting only 1 arg
            call rule(term) for each term to determine if it should be subbed.
            (only call it on terms which are subbable, i.e. is_subbable(term).)

        example, in the sub() function, use rule=lambda term: term.sub(old, new)
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        terms = tuple(self._iter_substitution_terms(**kw))
        new_terms = [(rule(term) if self._subs_check_term(term, **kw) else term) for term in terms]
        if all(n is t for (n, t) in zip(new_terms, terms)):  # subbed no terms
            return self  # return self, exactly, to help indicate nothing was changed.
        else:  # subbed at least one term
            return self._new_after_subs(*new_terms)

    # # # SUBSTITUTION BASIC FUNCTIONS # # #
    def sub(self, old, new, *, is_=False, layer_check=None, symbol_check=True, **kw):
        '''returns result of substituting old for new in self.
        returns self exactly (i.e. not a copy) if this substitution had no effect.

        [EFF] if you need sub to be faster, consider using is_=True, or layer_check=True.

        is_: bool, default False
            whether to use 'is' instead of '==', when comparing self to old.
        layer_check: None, bool, or int, default None
            whether to consider symdeplayers before checking for equality.
            if enabled:
                only check for equality if symdeplayers(self) == symdeplayers(old).
                only loop through terms in self if symdeplayers(self) > symdeplayers(old).
            None --> True if is_, else False.
            bool --> enabled if True, disabled if False
            int >= 1 --> assume, but do not check, that symdeplayers(old)==layer_check.
            == 0 --> disabled
        symbol_check: bool, default True
            whether to check if old appears in self.get_symbols() before attempting to sub.
            ONLY applies if old._is_basic_symbol, and self actually has a "get_symbols" method.
        '''
        if not is_subbable(self):
            return self
        if symbol_check and getattr(old, '_is_basic_symbol', False):
            try:
                self_get_symbols = self.get_symbols
            except AttributeError:
                pass  # nothing to check; self doesn't have get_symbols.
            else:
                if not any(s is old for s in self_get_symbols()):  # [EFF] '==' too slow; 'is' is okay.
                    return self
        # this function's substitution rule for self:
        looping = True
        checking_equal = True
        if layer_check is None: layer_check = bool(is_)
        if layer_check:
            if layer_check is True:
                layer_check = symdeplayers(old)
            slayer = symdeplayers(self)
            if slayer == layer_check:
                looping = False  # old can't be inside self; self terms each have fewer layers than old.
            else:
                checking_equal = False  # don't check self==old; they have different number of layers.
                if slayer < layer_check:
                    looping = False  # old can't be inside self; self has fewer layers than old.
        if checking_equal:
            if is_:
                if self is old:
                    return new
            else:
                if equals(self, old):
                    return new
        if not looping:
            return self
        # loop through terms in self, if applicable.
        def sub_rule(term):
            return term.sub(old, new, is_=is_, layer_check=layer_check, symbol_check=False, **kw)
        # ^ v symbol_check=False after first step because we aleady skipped if needed.
        return self._substitution_loop(sub_rule, is_=is_, layer_check=layer_check, symbol_check=False, **kw)

    def subs(self, *substitutions, print_freq=None, **kw):
        '''retuns result of substituting substitutions into self.
        basically equivalent to calling sub repeatedly using (old,new) pairs from substitutions.
        E.g. self.substitute((old0,new0),(old1,new1),(old2,new2)
            = self.sub(old0,new0).sub(old1,new1).sub(old2,new2)
        (Caveat: if result is no longer subabble at any point, return immediately.
        E.g. x.substitute((x,y),(y,7),(z,8)) --> y.substitute((y,7),(z,8)) --> 7

        print_freq: None or int
            seconds between printing progress updates.
            None --> use DEFAULTS.PROGRESS_UPDATES_PRINT_FREQ
            -1 --> never print progress updates.
        '''
        Nsubs = len(substitutions)
        updater = ProgressUpdater(print_freq, wait=True)  # wait print_freq before first print.
        for i, substitution in enumerate(substitutions):
            updater.print(f'subs at {i} of {Nsubs}')
            if is_subbable(self):
                self = self.sub(*substitution, **kw)
            else:
                break
        updater.finalize('subs')
        return self

    def sub_subscript(self, old, new, **kw):
        '''returns result of substituting old for new in subscripts of self or terms of self.'''
        return self.subs_subscripts((old, new), **kw)

    def subs_subscripts(self, *subscript_subs, **kw):
        '''returns result of substituting subscript_subs into self.
        subscripts are subbed simultaneously, e.g. [x,y,z] subsubs ((x,y),(y,z),(z,a)) --> [y,z,a].

        if any substitutions were performed, returns self._new(subscripts=new_subscripts).
        '''
        if not is_subbable(self):
            return self
        # this function's substitution rule for self:
        try:
            self_subscripts = self.subscripts
        except AttributeError:
            pass # self doesn't have subscripts...
        else:
            # sub subscript_subs directly into self.subscripts.
            subbed_any_here = False
            new_subscripts = []
            for s_cur in self_subscripts:
                for s_old, s_new in subscript_subs:
                    if s_cur == s_old:
                        new_subscripts.append(s_new)
                        subbed_any_here = True
                        break
                else: # didn't break
                    new_subscripts.append(s_cur)
            if subbed_any_here:
                self = self._new_after_subs(subscripts=new_subscripts)
                if not is_subbable(self):
                    return self
        # loop through terms in self, if applicable.
        def subs_subscripts_rule(term):
            return term.subs_subscripts(*subscript_subs, **kw)
        return self._substitution_loop(subs_subscripts_rule, **kw)

    def sub_everywhere(self, old, new, **kw):
        '''substitute old for new everywhere; in AND out of subscripts.
        Looks in subscripts first, then in not-subscripts.
        '''
        return self.sub_subscript(old, new, **kw).sub(old, new, **kw)

    def subs_everywhere(self, *subs, **kw):
        '''make these substitutions (of (key, new_value)) everywhere; in AND out of subscripts.
        Looks in subscripts first, then in not-subscripts.
        '''
        return self.subs_subscripts(*subs, **kw).subs(*subs, **kw)

    replace    = alias('subs')
    substitute = alias('subs')
    ss             = alias('sub_subscript')
    subscript_swap = alias('sub_subscript')
    replace_subscripts = alias('subs_subscripts')
    subsubs            = alias('subs_subscripts')
    subssubs           = alias('subs_subscripts')
    suball      = alias('sub_everywhere')
    subsall     = alias('subs_everywhere')
    replace_all = alias('subs_everywhere')

    # # # SUBSTITUTION CONVENIENCE FUNCTIONS # # #
    def subs_value(self, to_sub, value, **kw):
        '''returns result of substituting value into self for all quantities appearing in to_sub.
        Equivalent to self.subs(*((old, value) for old in to_sub), **kw).
        '''
        return self.subs(*((old, value) for old in to_sub), **kw)

    def subs_zero(self, *to_sub, **kw):
        '''returns result of substituting 0 into self for all quantities appearing in to_sub.
        Equivalent to self.subs_value(to_sub, 0, **kw).
        '''
        return self.subs_value(to_sub, ZERO, **kw)

    sub0   = alias('subs_zero')
    ignore = alias('subs_zero')

    def sub_generic_subscript(self, old, new, *, s='s', **kw):
        '''returns result of substituting new into old everywhere that old appears in self.
        old should by an object with s in subscripts.
        Matching is performed by checking everything except subscripts.
        If match occurs, sub new value with subscripts replaced appropriately.
        E.g. old=Ps, new=ns*Ts, self=7*Pi --> 7*(ni*Ti)

        [TODO] more generic implementation
        '''
        try:
            syms = self.get_symbols()
        except AttributeError:
            raise NotImplementedError('[TODO] subs_generic_subscript for self without get_symbols()')
        if not hasattr(old, 'subscripts'):
            raise NotImplementedError("[TODO] subs_generic_subscript for old without 'subscripts' attr")
        to_sub = []
        for sym in syms:
            if len(sym.subscripts)==1:
                i = sym.subscripts[0]
                old_i = old.ss(s, i)
                if old_i == sym:
                    new_i = new.ss(s, i) if is_subbable(new) else new
                    to_sub.append((old_i, new_i))
        return self.subs(*to_sub, **kw)

    def subs_generic_subscript(self, *subs, s='s', **kw):
        '''returns result of making substitutions in self,
        allowing for generic subscript matching and filling-in for subscript s.
        E.g.(Ps, ns*Ts), self=7*Pi --> 7*(ni*Ti)
        '''
        result = self
        for sub in subs:
            result = result.sub_generic_subscript(*sub, s=s, **kw)
        return result

    sub_gen = alias('sub_generic_subscript')
    subs_gen = alias('subs_generic_subscript')

    def del_subscripts(self, *subscripts, **kw):
        '''deletes subscripts anywhere they appear as subscripts in self (checks all layers of self).'''
        if not is_subbable(self):
            return self
        # this function's substitution rule for self:
        try:
            self_subscripts = self.subscripts
        except AttributeError:
            pass # self doesn't have subscripts...
        else:
            new_subscripts = tuple(s for s in self_subscripts if s not in subscripts)
            if len(new_subscripts) != len(self_subscripts):
                self = self._new_after_subs(subscripts=new_subscripts)
                if not is_subbable(self):
                    return self
        # loop through terms in self, if applicable.
        def del_subscripts_rule(term):
            return term.del_subscripts(*subscripts, **kw)
        return self._substitution_loop(del_subscripts_rule, **kw)

    del_ss = alias('del_subscripts')

    # # # SUBSTITUTION INTERFACE # # #
    def interface_subbables(self, **kw__iter_substitution_terms):
        '''returns list of subbables within self to appear as options in a SubstitutionInterface.
        The result will be a list of unique values; duplicates will be removed.
        '''
        if is_interface_subbable(self):
            result = [self]
        else:
            result = []
        for term in self._iter_substitution_terms(**kw__iter_substitution_terms):
            result += interface_subbables(term)
        uniques_result = list(Set(result))
        return uniques_result

    def substitution_interface(self, *args__subsi, **kw__subsi):
        '''returns an interface for making it easier to do substitutions into self.'''
        return SubstitutionInterface(self, *args__subsi, **kw__subsi)

    subs_interface      = alias('substitution_interface')
    substitution_helper = alias('substitution_interface')
    subs_helper         = alias('substitution_interface')
    allsub              = alias('substitution_interface')

    # # # SUBTREE # # #
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def subtree(self):
        '''returns SubTree.new_from(self). see help(SubTree) for details.'''
        return SubTree.new_from(self)


# # # OTHER ITERATION # # #
with binding.to(SubbableObject):
    @binding
    def _walk_substitution_terms(self, *, depth_first=True, check_subbable=True, **kw):
        '''walk through all _iter_substitution_terms in self,
        and their _iter_substitution_terms, etc.

        depth_first: bool, default True
            whether to walk depth first (True) or breadth first (False).
        check_subbable: bool, default True
            whether to check is_subbable(obj) before doing obj._iter_substitution_terms(**kw).
        '''
        def iter_sub_terms(obj):
            if check_subbable and not is_subbable(obj):
                raise TypeError('not subbable')
            try:
                return obj._iter_substitution_terms(**kw)
            except AttributeError:
                raise TypeError('no _iter_substitution_terms') from None
        return walk(self, depth_first=depth_first, iter=iter_sub_terms)


''' --------------------- SubstitutionInterface --------------------- '''

class SubstitutionInterface():
    '''helps manage substitutions.
    substitutions can be input via indexing of self.
    Can index via number, or SymbolicObject.

    Example:
        x = Symbol('x')
        y = Symbol('y')
        z = Symbol('z')
        obj = x + 7 * y / x + z
        subsi = SubstitutionInterface(obj, show_header=False)
        repr(subsi)
        >>> [0] Symbol('x') | None
            [1] Symbol('y') | None
            [2] Symbol('z') | None

        subsi[0] = 3
        repr(subsi)
        >>> [0] Symbol('x') | 3
            [1] Symbol('y') | None
            [2] Symbol('z') | None

        subsi[y] = np.arange(1000).reshape(10, 100)
        repr(subsi)
        >>> [0] Symbol('x') | 3
            [1] Symbol('y') | <class 'numpy.ndarray'>; NumArrayInfo(min=0, mean=499.5, max=999, shape=(10, 100))
            [2] Symbol('z') | None

        subsi.apply()      # equivalent to: obj.subs(*subsi)
        >>> 3 + 7 * np.arange(1000).reshape(10, 100) / 3 + z

    Note: long reprs (longer than _n_repr_max) of substitutions will be replaced with object.__repr__
    '''
    def __init__(self, subbable_object, show_header=True, _debug=False, _n_repr_max=200):
        assert isinstance(subbable_object, SubbableObject)
        self.obj = subbable_object
        self.show_header = show_header
        self._n_repr_max = _n_repr_max
        self._debug      = _debug
        self.subables    = self.obj.interface_subbables()
        self.subs = [None for _ in self.subables]

    def get_index(self, i_or_symbo):
        '''gets index number for subable.
        i_or_symbo: index or SymbolicObject.
            if SymbolicObject, return index of first subable equal to this value.
            Otherwise just return i.
        '''
        if isinstance(i_or_symbo, SymbolicObject):
            i = find(self.subables, i_or_symbo, default=None)
            if i is None:
                raise ValueError(f"value not found: {i_or_symbo}")
            else:
                return i
        else:
            return i_or_symbo

    def __setitem__(self, i_or_symbo, value):
        self.subs[self.get_index(i_or_symbo)] = value

    def __getitem__(self, i_or_symbo):
        i = self.get_index(i_or_symbo)
        return (self.subables[i], self.subs[i])

    def _internal_iter_(self):
        '''convenient iter for internal purposes, only.'''
        return zip(self.subables, self.subs)

    def __len__(self):
        '''returns len(self.subables)'''
        return len(self.subables)

    def __iter__(self):
        '''yields tuples of (subable, quant_to_sub) for all subs which have been entered.'''
        for subable, sub in self._internal_iter_():
            if sub is None:
                continue
            else:
                yield (subable, sub)

    def __repr__(self):
        if self._debug:
            return '{}; _debug=True. use __str__ to see interface.'.format(object.__repr__(self))
        else:
            return self.__str__()

    def __str__(self):
        if self.show_header:
            result = [('Welcome to SubstitutionInterface.\n'
                       'Enter the value of any quantity using the corresponding index.\n'
                       'For example: subsi = SubstitutionInterface(obj);\n'
                       '    subsi[0] = 7   # sets up subbing 7 for the quantity labeled [0].\n'
                       'To apply the substitutions, use subsi.apply().\n')]
        else:
            result = []
        for i, (subable, sub) in enumerate(self._internal_iter_()):
            reprsub = array_info_str(sub)
            result.append('[{}] {} | {}'.format(i, repr(subable), reprsub))
        return '\n'.join(result)

    def apply(self):
        '''applies all the substitutions in self to the originally input object.
        (Non-destructive; generates a new object rather than smashing the old object)
        '''
        return self.obj.subs(*self)

    do      = alias('apply')
    doit    = alias('apply')
    applied = alias('apply')


''' --------------------- SubTree --------------------- '''

class SubTree():
    '''SubTree aids with subbing when it is more complicated...
    The idea is to adjust children as needed anywhere within the SubTree,
    then reconstruct() at the end.

    This doesn't inherit from SymbolicObject because this is intended to be mutable,
    unlike SymbolicObjects.
    '''
    def __init__(self, obj, children=[], parent=None):
        self._obj     = obj
        self.children = children
        self.parent   = parent
        self._changed = None

    def _initial_assign_children(self, children):
        '''assign children to self, without adjusting anything else in self.
        Useful during __init__; children want to know self is their parent,
        which means self must be created before children can be created.
        '''
        self.children = children  # children isn't a property, so this is fine.

    @classmethod
    def new_from(cls, subobj, parent=None):
        '''create new SubTree from subbable object.'''
        result = cls(subobj, parent=parent)
        try:
            subobj_terms = subobj._iter_substitution_terms
        except AttributeError:
            pass
        else:
            children = [cls.new_from(child, parent=result) for child in subobj_terms()]
            result._initial_assign_children(children)
        return result

    parent = weakref_property_simple('_parent')

    @property
    def obj(self):
        '''object self represents. setting a value to obj also sets self.changed=True,
        and tells self.parent to set its changed to True.'''
        return self._obj
    @obj.setter
    def obj(self, value):
        self._obj = value
        self.changed = True

    @property
    def changed(self):
        '''whether self.obj has been changed OR any children have been changed.'''
        return self._changed
    @changed.setter
    def changed(self, value):
        if not self._changed:
            parent = self.parent
            if parent is not None:
                parent.changed = True
        self._changed = value

    def __getitem__(self, i):
        return self.children[i]

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def __setitem__(self, i, obj):
        '''set child[i] to obj'''
        subtree = type(self).new_from(obj)
        self.set_child(i, subtree)

    def set_child(self, i, subtree):
        '''assign child i to object'''
        children = self.children
        if not is_subbable(children[i].obj):
            raise TypeError(f'children[{i}].obj is not subbable.')
        children[i] = subtree
        self.changed = True

    def reconstruct(self):
        '''return orig if terms are unchanged, else orig._new_after_subs(*terms)'''
        if self.changed:
            new_kid_objs = [child.reconstruct() for child in self.children]
            return self.obj._new(*new_kid_objs)
        else:
            return self.obj

    def __repr__(self):
        return f'{type(self).__name__}({type(self.obj).__name__}, with {len(self.children)} children)'

    def structure(self, nlayers=10, *, tab='  ', _layer=0, _i=None):
        '''returns string for structure of self, cutting off at layer < layers.

        nlayers: int
            max number of layers to show.
        tab: str, default ' '*2.
            tab string (for pretty result). Inserts N tabs at layer N.
        _layer: int, default 0
            the current layer number.
        _i: None or int
            if provided, tells the index number of this object within the current layer.
        '''
        return structure_string(self, nlayers=nlayers, type_=SubTree, tab=tab, _layer=_layer, _i=_i)

    def print_structure(self, *args, **kw):
        print(self.structure(*args, **kw))

    def layers(self):
        '''return number of layers in self.
        layers(obj) = 1 + max(layers(term) for term in obj),
                    or = 0 if obj is not iterable.
        caching note: caching is handled by tools.layers
        '''
        return layers(self)

with binding.to(SubTree):
    @binding
    def walk(self, *, require=None, requiretype=SubTree, depth_first=True):
        '''walk through all terms inside self, requiring require if provided.
        require: None or callable
            if provided, only iterate through a term (including self) if require(term).
        requiretype: None, type, tuple of types. Default SubTree
            if not None, only iterate through a term (including self) if isinstance(term, requiretype).
        depth_first: bool
            if True, walk_depth_first. else, walk_breadth_first.
        '''
        return walk(self, require=require, requiretype=requiretype, depth_first=depth_first)
