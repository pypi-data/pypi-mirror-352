"""
File Purpose: Cascade; sequential evaluation of equation system.

[TODO] Also, simplify complicated equations by creating a Cascade of simpler equations.
"""
from .equation import Equation
from .equation_system import EquationSystem
from .symbols import new_symbol_like, Symbol, SYMBOLS
from ..attributors import attributor
from ..abstracts import (
    IterableSymbolicObject, OperationContainer,
    complexity, is_subbable, contains_deep,
)
from ..errors import PatternError, warn, InputConflictError
from ..initializers import initializer_for, INITIALIZERS
from ..tools import (
    viewlist, ProgressUpdater,
    Binding, format_docstring,
)
from ..defaults import DEFAULTS

binding = Binding(locals())


''' --------------------- convenience --------------------- '''

@attributor
def is_cascadify_subbable(x):
    '''returns whether x can be replaced by something during cascadify().
    returns x.is_cascadify_subbable() if possible, else is_subbable(x).
    '''
    try:
        x_is_cascadify_subbable = x.is_cascadify_subbable
    except AttributeError:
        return is_subbable(x)
    else:
        return x_is_cascadify_subbable()


''' --------------------- Cascade --------------------- '''

class Cascade(EquationSystem):
    '''a special EquationSystem where equations may be evaluated sequentially,
    and the final equation is "the most important".

    For example:
        x = 10 * a
        y = 7 * x - 20 * a
        z = x**2 + 9 * y + 3 * a

    If evaluated (see self.evaluate()), would give:
        z = 100 * a**2 + 9 * (7 * 10 * a - 20 * a) + 3 * a

    Note, lhs don't all need to be Symbols, but it is simpler if they are.
    E.g. if you replace y with y**3 everywhere in the example above, that would be fine.

    kwargs (used during self.evaluate):
        keep_eqs: bool, default False
            if keep_eqs, instead return a Cascade which contains all intermediate results as well.
        ignore: list
            eq.ignore(*ignore) after each substitution.
            NOTE: internally stored as ignore_ instead, to avoid overwriting the method named ignore.
        simplify: bool or callable, default True
            if True, eq.simplify() after each substitution.
            if callable, simplify(eq) after each substitution.
            NOTE: internally stored as simplify_ instead, to avoid overwriting the method named simplify.
        idx: None, list, or anything else which can be used to index self (e.g. slice)
            if provided, only evaluate the equations in self[idx] instead of all eqns in self.
            E.g. idx=(2,3,7) means self.evaluate() will plug eq 2 into 3 then 2 & 3 into 7, then return eq 7.
                if keep_eqs, the final result will have the new eqs 3 & 7, but all the same old eqs.
                otherwise, the final result will be only eq 7, even if it is not the last eq in self.
            if not keep_eqs, this is equivalent to self[idx].evaluate(...).
            for help on valid idx, see help(self.generic_indices)
        numeric: bool, default False
            if True, ignore simplify kwarg, and instead use simplify with only=['evaluate_numbers'].
            i.e., evaluate numbers & combinations of numbers whenever possible, but nothing else.
    Those kwargs are internally stored as '_cascade_{attr}' to avoid overwriting existing methods.
    E.g. ignore is stored as self._cascade_ignore, so you can still do self.ignore() as normal.
    '''
    def __init__(self, *eqns, keep_eqs=False, ignore=[], simplify=True, idx=None, numeric=False, **kw):
        super().__init__(*eqns, **kw)
        self._cascade_keep_eqs = keep_eqs
        self._cascade_ignore = ignore
        self._cascade_simplify = simplify
        self._cascade_idx = idx
        self._cascade_numeric = numeric

    @classmethod
    def from_equation_system(cls, eqsys, **kw):
        '''create Cascade (or cls) from eqsys. cls(*eqsys, **kw).'''
        return cls(*eqsys, **kw)

    def _init_properties(self):
        '''returns dict for initializing another Cascade like self.'''
        kw = super()._init_properties()
        kw.update(keep_eqs=self._cascade_keep_eqs,
                  ignore=self._cascade_ignore,
                  simplify=self._cascade_simplify,
                  idx=self._cascade_idx)
        return kw

    def evaluate(self, *, keep_eqs=None, ignore=None, simplify=None, idx=None,
                 print_freq=None, numeric=None, **kw__subs):
        '''evaluate the equations in self, one at a time, plugging in all previous equations.
        return an Equation which is the final result,
            from evaluating self[-1] (or self[idx][-1] if idx is not None).

        for help with kwargs (keep_eqs, ignore, simplify, idx), see help(self).

        if values are None here, will use the corresponding attributes (self._cascade_{attr}).
        (e.g. if ignore is None, ignore=self._cascade_ignore). Those can be input during __init__.
        '''
        if len(self)==0:
            raise PatternError('cannot evaluate an empty Cascade.')
        if keep_eqs is None: keep_eqs = self._cascade_keep_eqs
        if ignore is None: ignore = self._cascade_ignore
        if idx is None: idx = self._cascade_idx
        if numeric is None: numeric = self._cascade_numeric
        if numeric:
            if simplify is not None:
                raise InputConflictError('numeric=True implies "simplify" kwarg should not be used.')
            simplify = lambda x: x.simplify(only=['evaluate_numbers'])
        else:
            if simplify is None: simplify = self._cascade_simplify
        updater = ProgressUpdater(print_freq, wait=True)
        # list of eqs to evaluate.
        if idx is None:
            ilist = list(range(len(self)))
        else:
            ilist = self.generic_indices(idx)
        eqs = viewlist([eq for eq in self])   # viewlist here is just for debugging.
        vsubs = viewlist([])
        for i in ilist:
            updater.print(f'cascade evaluate at {i} of {len(ilist)}')
            eq = eqs[i]
            val = eq.subs(*vsubs, **kw__subs)
            if ignore:
                val = val.ignore(*ignore)
            if simplify:
                if callable(simplify):
                    val = simplify(val)
                else:
                    val = val.simplify()
            eqs[i] = val
            vsubs.append(val)
        updater.finalize('cascade evaluate')
        if keep_eqs:
            return self._new(*eqs)
        else:
            return eqs[ilist[-1]]

    def __getitem__(self, key):
        '''usually behaves like super().__getitem__, but if that fails, also try SYMBOLS.lookup(key).
        E.g., use self['S_{17}'] to get the equation S_{17} = ...
        '''
        try:
            return super().__getitem__(key)
        except KeyError as err:
            try:
                s_key = SYMBOLS.lookup(key)
            except KeyError:
                pass  # handled below; raise the original error to avoid confusion.
            else:
                try:
                    return super().__getitem__(s_key)
                except KeyError:
                    pass  # handled below; raise the original error to avoid confusion.
            raise err

    def simplify_steps(self, **kw__simplify):
        '''simplify the steps from self, but not the final equation.'''
        steps = self[:-1]
        steps = steps.simplify(**kw__simplify)
        return self._new(*steps, self[-1])


@initializer_for(Cascade)
def cascade(*eqn_or_tuple_objects, labels=None, **kw__cascade_init):
    '''create a new Cascade using the equations provided.
    Always returns a Cascade, even if no args are entered.

    *args: each should be either an Equation or a tuple.
        tuples will be converted to Equation objects.
        if any args are not an Equation or tuple, raise TypeError.
            (This helps prevent accidental errors when other iterables are involved.)
    labels: None or list of strings
        labels for eqns, if provided. Passed to INTIALIZERS.equation_system.

    kwargs are passed to Cascade().
    '''
    eqns = INITIALIZERS.equation_system(*eqn_or_tuple_objects, labels=labels)
    return Cascade(*eqns, **kw__cascade_init)


''' --------------------- EquationSystem to Cascade --------------------- '''

with binding.to(EquationSystem):
    @binding
    def as_cascade(self, **kw__cascade_init):
        '''return Cascade with equations in self.
        Cascade can be evaluated "sequentially" via Cascade.evaluate().
        '''
        return Cascade.from_equation_system(self, **kw__cascade_init)

    @binding
    def cascade(self, **kw__evaluate):
        '''return result of evaluating self sequentially.
        plugs eq0 into eq1; then 0 and 1 into eq2; then 0,1,2 into eq3, etc.
        Equivalent: self.as_cascade().evaluate(**kw__evaluate)
        '''
        return self.as_cascade().evaluate(**kw__evaluate)


''' --------------------- Cascadify --------------------- '''

# [TODO] allow objects to be represented as object with an underlying cascade,
# and combine cascades when combining objects.
# for now, it is only available for EquationSystems and Equations.

_cascadify_paramdocs = '''cthresh: int, default 2
            default complexity threshold.
            obj can only be replaced if complexity(obj) >= cthresh.
        s: str or None, default None
            name for new symbols.
            if None, use DEFAULTS.NEW_SYMBOL_STR (default 'S').
        skip: list of objects, default []
            skip replacing these objects AND any objects containing any of these objects.
        compress: bool, default True
            whether to compress self before replacing objects.
            usually you will want this to be True, unless you know self is already compressed,
            or have some other reason to want some equal-but-not-the-same-object terms to stay separate.
        container_ok: 'warn' or bool, default 'warn'
            whether it is ok to replace OperationContainer objects with Symbol objects.
            For example, if Equation(X, Y+7) appears twice, it might be replaced,
                and the result would include Equation(S_N, Equation(X, Y+7)) where S_N is some Symbol.
            'warn' --> make a warning but don't prevent it outright.
            False --> prevent it; don't try to replace any OperationContainer objects.
            True --> allow it and don't make a warning.
            [TODO] use default value of None and load default behavior from DEFAULTS instead.
        _check_type: bool, default True
            for internal use only.
            whether to convert self to cascade if self is not a Cascade already.
        clear_s: bool, default False
            if True, first do SYMBOLS.clear_s(s=s, force=True).
            WARNING: this can mess up all other objects containins any Symbol with s=s,
                so use with caution.
        simplify: bool or dict, default False
            if simplify is not False, simplify the resulting equations, as the cascade is built,
            via eqn.simplify(**simplify) for each equation. True --> use simplify=dict()
            This doesn't apply to the original equation (at the "bottom" of the cascade; i.e. result[-1]).
        additional kwargs go to Cascade.__init__, if _check_type AND self is not a Cascade yet.'''


with binding.to(EquationSystem):
    @binding
    @format_docstring(_paramdocs=_cascadify_paramdocs)
    def cascadify(self, cthresh=2, *, s=None, skip=[], compress=True, container_ok='warn',
                  _check_type=True, debug=False, clear_s=False, simplify=False,
                  _updater=None, _update_freq=None, _top=True, **kw__cascade_init):
        '''replace non-Symbol objects appearing multiple times in self with a new Symbol.
        return a new EquationSystem with those replacements, and the "definitions" for the new symbols.

        Example:
            X, Y, Z = symbols('X Y Z')
            obj1 = (X+1)
            eqns = equation_system((9, obj1**2), (Y, Z * obj1))
            eqns.view()
                7 = (X + 1)**2
                Y = Z * (X + 1)
            casc = eqns.cascadify()
            casc.view()
                S_0 = X + 1
                7 = S_0^2
                Y = Z S_0
        
        {_paramdocs}
        '''
        # implementation note: replaces the most complex repeated object,
        #   then cascadify(compress=False) the result.
        #   Doing it in this order means there is no need to compress() multiple times.
        #   It also reduces complexity the fastest, making each iteration as short as possible.
        #   [TODO][EFF] increase efficiency by passing complexities to internal cascadify() call.
        # restrictions:
        #   never replaces a Symbol, since that could lead to infinite loop.
        #   make a warning if replacing any OperationContainers;
        #     e.g. it would be strange to replace an Equation with a Symbol.
        if _updater is None:
            if _update_freq is None:
                _update_freq = (0 if debug else -1)
            _updater = ProgressUpdater(_update_freq)
        if _check_type and not isinstance(self, Cascade):
            self = self.as_cascade(**kw__cascade_init)
        if compress:
            self = self.compress(cthresh=cthresh)
        if s is None:
            s = DEFAULTS.NEW_SYMBOL_STR
        if clear_s:
            SYMBOLS.clear_s(s=s, force=True)
        if not (simplify is False):
            if simplify is True:
                simplify = dict()

        counts = self.object_counts()
        lookup = self.object_id_lookup()
        # choose which object to replace, based on complexities of objects appearing multiple times.
        complexities = {id_: (obj, complexity(obj)) for id_, obj in lookup.items() if counts[id_]>1}
        complexities = {id_: (obj, c) for id_, (obj, c) in complexities.items()
                            if (c >= cthresh)
                                and (not isinstance(obj, Symbol))  # never replace a Symbol
                                and (container_ok or (not isinstance(obj, OperationContainer)))
                                # and is_subbable(obj)  # if obj isn't Subbable, self.sub won't allow it to get replaced.
                                #                       # [TODO] maybe should refactor self.sub to allow it instead...
                                # and (not any(contains_deep(obj, skip_obj) for skip_obj in skip))
                             }
        if len(complexities) == 0:  # no repeated objects; nothing left to do.
            return self
        _updater.print(f'cascadify sees {len(complexities)} candidates.')
        maxid_, (_maxobj, _maxc) = max(complexities.items(), key=lambda x: x[1][1])
        to_replace = lookup[maxid_]
        # check stuff
        if not is_cascadify_subbable(to_replace):
            complexities = {id_: (obj, c) for id_, (obj, c) in complexities.items() if is_cascadify_subbable(obj)}
            if len(complexities) == 0: return self
            maxid_, (_maxobj, _maxc) = max(complexities.items(), key=lambda x: x[1][1])
            to_replace = lookup[maxid_]
        if any(contains_deep(to_replace, skip_obj) for skip_obj in skip):
            # sorted_items = sorted(complexities.items(), key=lambda x: x[1][1], reverse=True)  # most complex first.
            # to_replace = sorted_items[1] 
            # while True:
            #     complexities = 
            complexities = {id_: (obj, c) for id_, (obj, c) in complexities.items()
                                if not any(contains_deep(obj, skip_obj) for skip_obj in skip)}
            if len(complexities) == 0: return self
            maxid_, (_maxobj, _maxc) = max(complexities.items(), key=lambda x: x[1][1])
            to_replace = lookup[maxid_]
        # resume...
        if (container_ok == 'warn') and isinstance(to_replace, OperationContainer):
            warn(f'replacing {type(to_replace).__name__} <{maxid_}> with Symbol. To skip, use container_ok=False')
        # replace the most complex repeated object
        new_sym = new_symbol_like(to_replace, s=s, order=None)
        new_eqn = INITIALIZERS.equation(new_sym, to_replace)
        if not (simplify is False): new_eqn = new_eqn.simplify(**simplify)
        replaced = self.sub(to_replace, new_sym, layer_check=True)  # [TODO] why does is_=True affect results?
        assert replaced is not self, 'sub() should have returned a new object; something went wrong here.'
        result0 = replaced.prepend(new_eqn)
        # cascadify then return result
        result = result0.cascadify(cthresh=cthresh, compress=False, _check_type=False, clear_s=False,
                                   s=s, skip=skip, debug=debug, _updater=_updater, simplify=simplify, _top=False)
        if _top:
            _updater.finalize('cascadify')
        return result

with binding.to(Equation):
    @binding
    @format_docstring(_paramdocs=_cascadify_paramdocs)
    def cascadify(self, cthresh=2, **kw):
        '''replace non-Symbol objects appearing multiple times in self with a new Symbol.
        return an EquationSystem with those replacements, and the "definitions" for the new symbols.

        The implementation here just makes an equation system with self as the only equation,
        then uses EquationSystem.cascadify(*args, **kw)

        {_paramdocs}
        '''
        eqsys = INITIALIZERS.equation_system(self)
        return eqsys.cascadify(cthresh=cthresh, **kw)

# # # IS_CASCADIFY_SUBBABLE # # #
with binding.to(Symbol):
    @binding
    def is_cascadify_subbable(self):
        '''return False, since Symbol should not be replaced during cascadify.'''
        return False