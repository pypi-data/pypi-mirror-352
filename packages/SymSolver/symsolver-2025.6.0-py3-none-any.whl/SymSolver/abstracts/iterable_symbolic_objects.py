"""
File Purpose: IterableSymbolicObject, also see BinarySymbolicObject
(directly subclasses SymbolicObject)

TODO:
    - maybe BinaryObject term attributes should have better names than 't1' and 't2'.
    - more efficienct comparisons:
        - put self._symbols = {symbol: number of times symbol appears across all terms in self}
        - then in __eq__, compare _symbols first. If _symbols don't match, __eq__ can return False.
    - use weakref for caching.
"""
import builtins  # for unambiguous sum
import collections
from .symbolic_objects import (
    SymbolicObject,
    is_constant, is_number,
    symdeplayers,
)
from ..attributors import attributor, ATTRIBUTORS
from ..tools import (
    equals, list_equals, apply,
    find, _list_without_i, dichotomize,
    Set, counts,
    walk,
    is_integer,
    _repr, viewtuple, viewlist, viewdict, fastfindviewtuple, 
    caching_attr_simple,
    alias, caching_attr_simple_if, caching_attr_with_params_if,
    layers, structure_string,
    Binding,
)
from ..defaults import DEFAULTS

binding = Binding(locals())


''' --------------------- Convenience Functions --------------------- '''

@attributor
def get_symbols(x):
    '''returns tuple of Symbol objects in x (or in terms of x), by checking x.get_symbols().
    if that method is unavailable, returns ().
    '''
    try:
        return x.get_symbols()
    except AttributeError:
        return ()

@attributor
def get_symbols_in(x, func):
    '''return tuple of Symbols objects in parts of x with bool(func(x))==True if func(x), else ().
    Accomplishes this by returning x.get_symbols_in(func) if possible, else ().
    '''
    try:
        return x.get_symbols_in(func)
    except AttributeError:
        return ()

@attributor
def contains_deep(obj, b):
    '''returns whether b is contained (via contains_deep) in obj.
    i.e. (b == obj) or (b in obj) or any(term.contains_deep(b) for term in obj)

    returns obj.contains_deep(b) if available, else (obj == b).
    '''
    try:
        obj_contains_deep_ = obj.contains_deep
    except AttributeError:
        return equals(obj, b)
    else:
        return obj_contains_deep_(b)

@attributor
def contains_deep_subscript(obj, s):
    '''returns whether s is contained (via contains_deep_subscript) in obj.
    i.e. (s in obj.subscripts) or any(term.contains_deep_subscript(s) for term in obj)

    returns obj.contains_deep_subscript(s) if available,
    else (s in obj.subscripts) if obj.subscripts available,
    else False.
    '''
    try:
        obj_contains_deep_subscript = obj.contains_deep_subscript
    except AttributeError:
        return s in getattr(obj, 'subscripts', [])
    else:
        return obj_contains_deep_subscript(s)

@attributor
def object_counts(x):
    '''return dict of {object id: number of times object appears anywhere in x}, comparing via 'is'.
    x is NOT included in the final dict.
    returns x.object_counts() if possible, else an empty dict.
    '''
    try:
        x_object_counts = x.object_counts
    except AttributeError:
        return dict()
    else:
        return x_object_counts()

@attributor
def object_id_lookup(x):
    '''return dict of {object id: object} for all objects appearing anywhere in x.
    x is NOT included in the final dict.
    returns x.object_id_lookup() if possible, else an empty dict.
    '''
    try:
        x_object_id_lookup = x.object_id_lookup
    except AttributeError:
        return dict()
    else:
        return x_object_id_lookup()

@attributor
def count_nodes(x):
    '''return 1 + sum of count_nodes(term) for term in x, by checking x.count_nodes().
    if that method is unavailable, returns 1.
    '''
    try:
        x_count_nodes = x.count_nodes
    except AttributeError:
        return 1
    else:
        return x_count_nodes()


''' --------------------- IterableSymbolicObject --------------------- '''

class IterableSymbolicObject(SymbolicObject):
    '''SymbolicObject containing terms.'''
    def __init__(self, *terms, **kw):
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        self.terms = fastfindviewtuple(terms)  # tuple with nice display and fast find objects with matching id.
        super().__init__(*terms, **kw)

    def __eq__(self, b):
        try:
            return super().__eq__(b)
        except NotImplementedError:
            return list_equals(self.terms, b.terms)

    @caching_attr_simple
    def __hash__(self):
        return hash((type(self), self.terms))

    # # # DISPLAY # # #
    def _repr_contents(self, **kw):
        '''list of contents to put as comma-separated list into repr of self.'''
        return [_repr(t, **kw) for t in self]

    # # # LIST-LIKE BEHAVIOR # # #
    def __iter__(self):
        '''iterator over terms of self. returns iter(self.terms)'''
        return iter(self.terms)

    def __len__(self):
        return len(self.terms)

    def fastfind(self, element):
        '''returns self.terms.fastfind(element).
        returns first term for term in self.terms if term is element.
        raises ValueError if there are no matches (using 'is').
        '''
        return self.terms.fastfind(element)

    # # # INDEX BY INT / SLICE / SYMBOLIC OBJECT / "KEY" # # #
    # INDEX BY SYMBOLIC OBJECT #
    def term_index(self, term):
        '''gets index of term in terms of self.
        raise ValueError if term not found in self.
        '''
        i = find(self, term, default=None, equals=self._term_index_equality_check)
        if i is None:
            raise ValueError(f"value not found: {term}")
        else:
            return i

    index = alias('term_index')

    def _term_index_equality_check(self, item_from_self, term):
        '''tells whether item_from_self equals term for the purposes of indexing (see self.get_index).
        Here, this method just returns whether item_from_self==term.

        But, subclasses may wish to override it.
        For example, EquationSystem will override it
            so that it instead checks if the LHS of the equation equals term,
            i.e. item_from_self[0] == term.
        '''
        return equals(item_from_self, term)

    # INDEX BY KEY #
    def key_index(self, key):
        '''return index in self of term with key==self._get_indexkey(term).
        This allows for indexing by key, for subclasses which implement the methods:
            self._is_indexkey, self._get_indexkey.
        '''
        return self.key_index_mapping()[key]

    def _is_indexkey(self, key):
        '''returns whether key might be a way to lookup an index of self via self.key_index().
        The implementation here returns False, since by default no keys are supported.
        By overriding this method & _get_indexkey(), subclasses may use keys for indexing.
        Recommend: never use any key which is an int, slice, or SymbolicObject.
        '''
        return False

    def _get_indexkey(self, term):
        '''returns indexkey from term.
        Indexkey can be used by self.key_index() to determine index of term.
        The implementation here raises NotImplementedError.
        By overriding this method & _is_indexkey(), subclasses may use keys for indexing.
        Recommend: never use any key which is an int, slice, or SymbolicObject.
        '''
        raise NotImplementedError(f'{type(self).__name__}._get_index_key()')

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def key_index_mapping(self):
        '''returns dict with result[indexkey] = index of term with that indexkey.
        If indexkey is None, do not put it into the result.
        raise NotImplementedError if multiple terms have the same non-None indexkey.
        '''
        result = dict()
        for i, term in enumerate(self):
            indexkey = self._get_indexkey(term)
            if indexkey is None:
                continue
            if indexkey in result:
                raise NotImplementedError(f'Multiple terms with matching non-None indexkey: {repr(indexkey)}')
            result[indexkey] = i
        return result

    # INDEX BY INT / "KEY" / SYMBOLIC OBJECT #
    def get_index(self, i_or_symbo_or_key):
        '''gets index number corresponding to int, key, or symbolic object.
        i_or_symbo_or_key: int, SymbolicObject, or key.
            int --> return this value
            key --> return index of element in self with this key.
                    ("type"-checked via self._is_indexkey(this value))
            SymbolicObject --> return index of first element in self equal to this value.
            

        for equality checking, use self._term_index_equality_check(item_from_self, symbo).
        By default, that method just returns (item_from_self == symbo).
        But subclasses may override it.
        It is preferred to override that _term_index_equality_check, rather than get_index, if possible.
        '''
        if is_integer(i_or_symbo_or_key):
            i = i_or_symbo_or_key
            return i
        elif isinstance(i_or_symbo_or_key, SymbolicObject):
            symbo = i_or_symbo_or_key
            return self.term_index(symbo)
        elif self._is_indexkey(i_or_symbo_or_key):
            key = i_or_symbo_or_key
            return self.key_index(key)
        else:
            errmsg = ('Expected int, SymbolicObject, or key (with self._is_indexkey(key) == True), '
                      f'but got object: {i_or_symbo_or_key}')
            raise TypeError(errmsg)

    generic_index = alias('get_index')

    # GENERIC INDEXING - BY INT, "KEY", SLICE, SYMBOLIC OBJECT, or iterable of those things <<. #
    def generic_indices(self, idx):
        '''returns list of indices corresponding to idx.

        idx: int, str, SymbolicObject, slice, or iterable of ints or SymbolicObjects.
            slice --> return list(range(len(self)))[idx]
            key --> return index of element in self with this key.
                    ("type"-checked via self._is_indexkey(this value))
            SymbolicObject --> return [self.term_index(idx)]
            int --> return [idx]
            iterable --> return [self.get_index(i) for i in idx]

        '''
        if isinstance(idx, slice):
            result = list(range(len(self)))[idx]
        elif self._is_indexkey(idx):
            result = [self.key_index(idx)]
        elif isinstance(idx, SymbolicObject):
            result = [self.term_index(idx)]
        else:
            try:
                idx_iter = iter(idx)
            except TypeError:  # --> idx is an integer
                try:  # get i as a positive integer
                    i_simple = range(len(self))[idx]  # i as a single integer
                except IndexError as ierr:
                    errmsg = f'index {idx} out of range for {type(self).__name__} with len=={len(self)}'
                    raise IndexError(errmsg) from None
                result = [i_simple]
            else:  # --> idx is an interable, hopefully of int / key / slice / SymbolicObject objects.
                result = [self.get_index(i) for i in idx_iter]
        return result

    def get_terms(self, idx):
        '''returns tuple of terms at idx.

        idx: slice, int, SymbolicObject, or iterable of ints or SymbolicObjects.
            goes to self.generic_indices(idx).
        '''
        idxlist = self.generic_indices(idx)
        return tuple(self.terms[i] for i in idxlist)

    def __getitem__(self, idx):
        '''returns self[idx].

        idx: slice, int, SymbolicObject, or iterable of ints or SymbolicObjects.
            goes to self.generic_indices(idx).
            slice --> returns self._new(*(the terms implied by this slice))
            single implied term --> returns that term
            multiple or zero implied terms --> returns self._new(*(the implied terms))

        To override indexing behavior for any subclass,
            consider replacing _term_index_equality_check or get_index instead of __getitem__.
        '''
        terms = self.get_terms(idx)
        if (len(terms) == 1) and (not isinstance(idx, slice)):
            return terms[0]
        else:
            return self._new(*(terms))

    # # # LIST MANIPULATION # # #
    def extend(self, new_terms):
        '''returns new object with all the terms in self then the ones in new_terms.
        NOTE: new_terms should be an iterable. Like numpy.append, or list.extend.
        NOTE: self will not be altered! SymbolicObjects are intended to be immutable.
        '''
        return self._new(*self, *new_terms)

    def append(self, new_term):
        '''returns new object with all the terms in self followed by the new term.
        NOTE: self will not be altered! SymbolicObjcts are intended to be immutable.
        '''
        return self._new(*self, new_term)

    def extendleft(self, new_terms):
        '''returns new object with all the terms in new_terms then the ones in self.
        NOTE: new_terms should be an iterable. Like numpy.append, or list.extend.
        NOTE: self will not be altered! SymbolicObjects are intended to be immutable.
        '''
        return self._new(*new_terms, *self)

    def prepend(self, new_term):
        '''returns new object with all the terms in self followed by the new term.
        NOTE: self will not be altered! SymbolicObjcts are intended to be immutable.
        '''
        return self._new(new_term, *self)

    def without_term(self, x, *, missing_ok=False):
        '''returns self without x, i.e. remove one copy of x from terms in self.
        missing_ok: bool, default False
            controls behavior when x is missing from self.
            True --> that's fine; return self unchanged.
            False --> raise ValueError
        see also: self.without(), for more generic removal of term(s).
        '''
        try:
            i = self.term_index(x)
        except ValueError:
            if missing_ok:
                return self
            else:
                raise
        new_terms = _list_without_i(self, i)
        return self._new(*new_terms)

    def without(self, i, *, force_unique=True):
        '''returns self without the term(s) indicated by i.

        i: slice, int, SymbolicObject, or iterable of ints or SymbolicObjects.
            goes to self.generic_indices(i).
        force_unique: bool, default True
            False --> ignore this kwarg.
            True --> if any duplicate indices are detected, raise ValueError.
        '''
        idx = self.generic_indices(i)
        set_idx = set(idx)
        if force_unique and (len(idx) != len(set(idx))):
            counted = counts(idx)
            duplicates_str = '; '.join(f'{count[0]} appears {count[1]} times' for count in counted if count[1]>1)
            errmsg_help = 'To proceed anyway, use force_unique=False. To check the indices, use self.generic_indices(i)'
            raise ValueError(f'detected duplicate(s) in indices: {duplicates_str}. {errmsg_help}')
        idx_keep = sorted( set(range(len(self))) - set_idx )
        return self._new(*(self.terms[i] for i in idx_keep))

    def dichotomize(self, func):
        '''puts terms into dichotomy based on func.
        returns (terms where func(term)), (terms where not func(term))
        '''
        return dichotomize(self, func)

    # # # CONTAINMENT (e.g. x in self?) # # #
    def __contains__(self, b):
        '''returns whether b is equal to one of the terms of self.'''
        #return b in list(iter(self))  # < this doesn't work when b is a numpy array;
        #   it gives "ValueError: The truth value of an array with more than one element is ambiguous."
        return (find(self, b, default=None, equals=equals) is not None)

    @caching_attr_with_params_if(lambda: DEFAULTS.CACHING_CD, maxlen=lambda: DEFAULTS.CACHING_CD_MAXLEN)
    def contains_deep(self, b):
        '''returns whether b is contained (via contains_deep) in self.
        i.e. (b == self) or (b in self) or (term.contains_deep(b) for term in self)
        [EFF] note: does caching if DEFAULTS.CACHING_CD.
        '''
        if equals(self, b):
            return True
        if b in self:
            return True
        for term in self:
            if contains_deep(term, b):
                return True
        return False

    def contains_deep_like(self, like):
        '''returns whether any term in self (or within those terms... deep check) has like(term).
        i.e. like(self) or any(like(term) or term.contains_deep_like(like) for term in self)
        '''
        if like(self):
            return True
        for term in self:
            try:
                term_contains_deep_like = term.contains_deep_like
            except AttributeError:
                if like(term):
                    return True
            else:
                if term_contains_deep_like(like):  # like(term) checked during term.contains_deep_like(like).
                    return True
        return False

    @caching_attr_with_params_if(lambda: DEFAULTS.CACHING_CD, maxlen=lambda: DEFAULTS.CACHING_CD_MAXLEN)
    def contains_deep_subscript(self, s):
        '''returns whether self contains s in any subscripts.'''
        if s in getattr(self, 'subscripts', []):
            return True
        for term in self:
            if contains_deep_subscript(term, s):
                return True
        return False

    def contains_deep_anywhere(self, x):
        '''returns whether self contains x anywhere, including possibly as a subscript.'''
        return self.contains_deep_subscript(x) or self.contains_deep(x)

    @caching_attr_with_params_if(lambda: DEFAULTS.CACHING_CD, maxlen=lambda: DEFAULTS.CACHING_CD_MAXLEN)
    def contains_deep_inside(self, x, inside):
        '''returns whether x is contained (via contains_deep_inside) of self,
        inside of an object which is_opinstance of inside.
        E.g. ((u x B).k + 7).contains_deep_inside(u, ...)
            inside=CrossProduct --> True
            inside=DotProduct   --> True
            inside=Power        --> False
            inside=Equation     --> False
        Edge case note:
            if x == self, return False, even if self is_opinstance of inside.
        '''
        if isinstance(self, inside):
            return self.contains_deep(x)
        for term in self:
            if apply(term, 'contains_deep_inside', x, inside, default=False):
                return True
        return False

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def get_symbols(self):
        '''returns tools.Set of Symbol objects in self (or in terms of self).
        Set behaves like set but works even with unhashable objects. (though it's faster with hashing..)
        '''
        # [TODO][EFF] if tools.Set addition implemented in a more efficient way, use that here too.
        symbols = (s for term in self for s in get_symbols(term))
        unique_symbols = Set(symbols)
        return unique_symbols

    # [TODO] caching?
    def get_symbols_in(self, func):
        '''return tools.Set of Symbols objects in parts of self with func(part)==True if func(self)==True, else [].
        NOTE: this function is "SLOW" until we implement caching.
        '''
        if func(self):
            symbols = (s for term in self for s in get_symbols_in(term, func))
            unique_symbols = viewtuple(Set(symbols))
            return unique_symbols
        else:
            return ()

    # # # INSPECTION # # #
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def is_constant(self):
        '''returns whether self is constant.'''
        return all(is_constant(t) for t in self)

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def is_number(self):
        '''returns whether self is a number.'''
        return all(is_number(t) for t in self)

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
        return structure_string(self, nlayers=nlayers, type_=IterableSymbolicObject, tab=tab, _layer=_layer, _i=_i)

    def print_structure(self, *args, **kw):
        print(self.structure(*args, **kw))

    structure_print = alias('print_structure')

    def layers(self):
        '''return number of layers in self.
        layers(obj) = 1 + max(layers(term) for term in obj),
                    or = 0 if obj is not iterable.
        caching note: caching is handled by tools.layers
        '''
        return layers(self)

    def _pick_any_term(self):
        '''picks any term in self. [EFF] tries to pick "simplest" term, for efficiency.

        first, check if iter(term) fails for any term in self, and return it if found.
        next, check if layers() is fast, by checking DEFAULTS.CACHING_PROPERTIES,
            if layers() is fast, return term with smallest value for layers().
        if a term hasn't been picked yet, return self.terms[0]
        '''
        for term in self.terms:
            try:
                iter(term)
            except TypeError:
                return term   # term is very simple; can't even iterate through it!
        if DEFAULTS.CACHING_PROPERTIES: # layers() may be fast, thanks to caching
            return min(self.terms, key=layers)
        # if we haven't picked anything yet, return self.terms[0].
        # (will crash if len(self)==0. That's fine; we can't pick anything in that case.)
        return self.terms[0]

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def object_counts(self):
        '''return dict of {object id: number of times object appears anywhere in self}, comparing via 'is'.
        self is NOT included in the final dict.
        checks all objects inside of self as well.
        '''
        # implementation note: to better utilize caching, don't use self.walk().
        result = dict()
        for obj in self:
            id_ = id(obj)
            try:
                result[id_] += 1  # '+=' is okay since it is just integer addition
            except KeyError:
                result[id_] = 1
            obj_count = object_counts(obj)
            for key, count in obj_count.items():
                try:
                    result[key] += count  # '+=' is okay since it is just integer addition
                except KeyError:
                    result[key] = count
        return result
        # # implementation note: tried the code below, but it was much slower:
        # result = collections.Counter(id(obj) for obj in self)
        # for obj in self:
        #     result.update(object_counts(obj))
        # return result

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def object_id_lookup(self):
        '''return dict of {object id: object} for all objects appearing anywhere in self.
        self is NOT included in the final dict.
        returns self.object_id_lookup() if possible, else an empty dict.
        '''
        result = {id(obj): obj for obj in self}
        for obj in self:
            result.update(object_id_lookup(obj))
        return result

    def object_counts_view(self):
        '''return list of pairs (count, object). This is mainly for viewing / human-readability.
        For efficient coding methods, probably should stick to just self.object_counts().
        '''
        counts = self.object_counts()
        lookup = self.object_id_lookup()
        result = [viewtuple((count, lookup[key])) for key, count in counts.items()]
        return viewlist.with_view_sortkey(result, key=lambda pair: pair[1])

    def object_counts_lookup(self):
        '''return dict of {object id: (count, object)} for all objects appearing anywhere in self.
        self is NOT included in the final dict.
        "count" means number of times object appears anywhere in self, comparing via 'is'.
        '''
        counts = self.object_counts()
        lookup = self.object_id_lookup()
        result = viewdict({key: viewtuple((count, lookup[key])) for key, count in counts.items()})
        return result

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def count_nodes(self):
        '''return 1 + sum of count_nodes(term) for term in self'''
        return 1 + builtins.sum(count_nodes(term) for term in self)

    # # # IMMUTABILITY DESIGN INTENTION - SUPPORT # # #
    def copy(self):
        '''returns a copy of self.'''
        return self._new(*self)

    def with_set_attr(self, attr, value):
        '''returns a copy of self with attr set to value.'''
        result = self.copy()
        setattr(result, attr, value)
        return result

    def with_set_attrs(self, **attrs_and_values):
        '''returns a copy of self with attrs set to values.'''
        result = self.copy()
        for attr, value in attrs_and_values.items():
            result[attr] = value
        return result

    def with_replaced_at(self, i_or_symbo, value):
        '''returns a copy of self with i'th term set to value.
        Use self.get_index(i_or_symbo) to find index i.
        '''
        i = self.get_index(i_or_symbo)
        return self._new(*self[:i], value, *self[i:])
    
    replaced_at = alias('with_replaced_at')


# # # ITERATION # # #
with binding.to(IterableSymbolicObject):
    @binding
    def walk(self, *, require=None, requiretype=IterableSymbolicObject,
             depth_first=True, order=False, **kw):
        '''walk through all terms inside self, requiring require if provided.
        note: if depth_first but not order, will iterate through each "layer" in reverse order,
            since that is more efficient (see collections.deque.extendleft).
            If you need to preserve order, use style=True. OR use iter=builtins.reversed.

        require: None or callable
            if provided, only iterate through a term (including self) if require(term).
        requiretype: None, type, tuple of types. Default IterableSymbolicObject
            if not None, only iterate through a term (including self) if isinstance(term, requiretype).
        depth_first: bool
            if True, walk_depth_first. else, walk_breadth_first.
        order: bool, default False
            whether to use terms' original order, when doing depth first walk. Ignored if breadth first.
            False is more efficient, but True will maintain original order.
        **kw are passed to tools.walk()
        '''
        return walk(self, require=require, requiretype=requiretype, depth_first=depth_first, **kw)

    @binding
    def walk_symdeplayers(self):
        '''walk through all terms inside self, from most symdeplayers to least symdeplayers.
        self is not included in the walk.
        [EFF] this code is "reasonably efficient" but walk() is roughly 5 to 10 times faster.
        '''
        queue = dict()
        for term in self:
            queue.setdefault(symdeplayers(term), []).append(term)
        while queue:
            _maxlayers, maxlist = max(queue.items(), key=lambda pair: pair[0])
            for term in maxlist:
                yield term
                try:
                    iter_term = iter(term)
                except TypeError:  # this term is not iterable
                    continue
                for subterm in iter_term:
                    queue.setdefault(symdeplayers(subterm), []).append(subterm)
                    # note: symdeplayers(subterm) will ALWAYS be less than _maxlayers,
                    #  since symdeplayers(term) = 1 + max(symdeplayers(subterm) for subterm in terms)
            del queue[_maxlayers]


''' --------------------- BinarySymbolicObject --------------------- '''

class BinarySymbolicObject(IterableSymbolicObject):
    '''IterableSymbolicObject containing exactly 2 terms.'''
    def __init__(self, t1, t2, **kw):
        self.t1 = t1
        self.t2 = t2
        super().__init__(t1, t2, **kw)
