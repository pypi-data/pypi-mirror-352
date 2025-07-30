"""
File Purpose: SystemSolver for solving system of equations
Note: doesn't follow the "immutable" design principle of SymSolver.
    Contents may be editted directly.

Meanwhile, SystemSolveState inherits from EquationSystem,
    and also tracks the remaining targets, and some other methods for solving equations.
    Note: SystemSolveState is intended for internal use, and ease of user inspection.

[TODO] test any of the code in this file...
"""

from .equation_solve import (
    SOLVE_METHOD_INFOS, ELIMINATE_METHOD_INFOS,
)
from ..abstracts import SymbolicObject
from ..basics import EquationSystem
from ..errors import SolvingPatternError, InputError
from ..essences import (
    essentialize,
)
from ..initializers import initializer_for, INITIALIZERS
from ..vectors import (
    components_count,
    is_vector,
)
from ..tools import (
    _repr, _str,
    documented_namedtuple, _list_without_i,
    caching_attr_simple_if, alias_to_result_of,
    ProgressUpdater,
    Binding, format_docstring,
)
binding = Binding(locals())

from ..defaults import DEFAULTS, ZERO


''' --------------------- SystemSolveState --------------------- '''

class SystemSolveState(EquationSystem):
    '''EquationSystem with more info helpful for solving a system of equations.
    contains the current system of equations and the remaining targets.
    Also some convenience for inspecting that information.
        E.g. self.imap_target_to_eqns, self.imap_eqn_to_targets.
    '''
    # # # INITIALIZATION / CREATION # # #
    def __init__(self, *eqns, targets):
        super().__init__(*eqns)
        self.targets = targets

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another instance of type(self) to be like self,
        via self._new(*args, **kw). Note these will be overwritten in _new by any **kw entered.'''
        kw = super()._init_properties()
        kw['targets'] = self.targets
        return kw

    # # # TOOLS / INSPECTION # # #
    @property
    def imap_target_to_equations(self):
        '''dict of {i: [all j such that self[j] contains targets[i]]}. self[j] is the j'th equation.'''
        return self._targets_mapping()[0]

    @property
    def imap_equation_to_targets(self):
        '''dict of {j: [all i such that self[j] contains targets[i]]}. self[j] is the j'th equation.'''
        return self._targets_mapping()[1]

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def _targets_mapping(self):
        '''returns (imap_target_to_eqns, imap_eqn_to_targets).
        imap_target_to_eqns:  dict of {i: [all j such that self[j] contains targets[i]]}
        imap_eqn_to_targets:  dict of {j: [all i such that self[j] contains targets[i]]}
        '''
        targets = self.targets
        eqns = list(self)
        imap_target_to_eqns = {i: [] for i in range(len(self.targets))}
        imap_eqn_to_targets = {i: [] for i in range(len(self))}
        for i, target in enumerate(self.targets):
            for j, eqn in enumerate(self):
                if eqn.contains_deep(target):
                    imap_target_to_eqns[i].append(j)
                    imap_eqn_to_targets[j].append(i)
        return (imap_target_to_eqns, imap_eqn_to_targets)

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def components_count_targets(self, ndim=None, **kw):
        '''return sum of components_count(target) for target in self.targets
        components_count is 1 for scalars, ndim for vectors. If ndim is None, use get_default_ndim(**kw).
        '''
        return sum(components_count(target, ndim=ndim, **kw) for target in self.targets)

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def components_count_equations(self, ndim=None, unsolved_only=True, **kw):
        '''return sum of components_count(eqn) for eqn in self.unsolved_system()
        components_count is 1 for scalars, ndim for vectors. If ndim is None, use get_default_ndim(**kw).

        unsolved_only: bool, default True
            whether to only count components from the unsolved equations in self.
        '''
        eqns = tuple(eqn for eqn in self if not eqn.solved) if unsolved_only else tuple(self)
        return sum(components_count(eqn, ndim=ndim, **kw) for eqn in eqns)

    nfree = alias_to_result_of('components_count_targets',
        doc='''alias to components_count_targets(). Number of free variable components in self.
            Scalars count as 1, vectors count as ndim. Only considers self.targets.''')

    nconstrain = alias_to_result_of('components_count_equations',
        doc='''alias to components_count_equations(). Number of equation components in self.
            Scalars count as 1, vectors count as ndim. Only considers unsolved equations in self.''')


@initializer_for(SystemSolveState)
def system_solve_state(*eqns, targets, **kw):
    '''the implementation here just returns SystemSolveState(*eqns, targets=targets, **kw)'''
    return SystemSolveState(*eqns, targets=targets, **kw)


''' --------------------- Solve Step Tracking --------------------- '''

SolveStepInfo = documented_namedtuple('SolveStepInfo', ['ieqn', 'itarget', 'method', 'eqn', 'target'],
        '''Info about a (potential) step to solve an EquationSystem.''',
        ieqn='''index of equation to solve during this step.''',
        itarget='''index of target to solve for during this step.''',
        method='''a SolverMethodInfo object, indicates method to use during this step.''',
        eqn='''(optional) equation to solve during this step.''',
        target='''(optional) target to solve for during this step.''',
        _defaults=(None, None), _module=(lambda: None).__module__,
        )

with binding.to(SolveStepInfo):
    SolveStepInfo.repr = SolveStepInfo.__repr__   # << use ssi.repr() to get "full" __repr__.
    @binding
    def __repr__(self):
        '''only put ieqn, itarget, and method, for brevity.'''
        return f'{type(self).__name__}(ieqn={self.ieqn}, itarget={self.itarget}, method={self.method}, ...)'



''' --------------------- SystemSolver --------------------- '''

@format_docstring(default_simplify_mode=DEFAULTS.SOLVING_SYSTEM_SIMPLIFY_MODE)
class SystemSolver(SymbolicObject):
    '''helps with solving a system of equations.
    Aiming for a system of equations (target == expression) for target in targets.
    Possibly eliminating some equations & some targets along the way,
        e.g. upon reaching (target * expression == 0), may give (expression == 0).
        That will depend on some settings of this object [TODO]

    Default is "Dispersion relation mode" where targets will be eliminated,
        until finding an equation with only 1 target remaining,
        at which point that equation, with that target eliminated, is the result.

    simplify_mode: None, str, bool, or tuple. Default {default_simplify_mode}.
        how to simplify after each solvestep (and before the first solvestep).
        None --> use DEFAULTS.SOLVING_SYSTEM_SIMPLIFY_MODE
        'essentialize' --> self._essentialize()
        'simplify' or True --> self.system.simplify()
        'expand' --> self.system.expand()
        'simplified' --> self.system.simplified()
        False --> don't simplify at all
        tuple --> values must be options above; apply each in turn.
    simplify_now: bool, default True
        whether to simplify self during initialization, according to simplify mode.
    essentialize_solved: bool or None, default None
        whether to essentialize solved equation after each solvestep,
        before plugging it in to the other equations.
        None --> True if 'essentialize' in simplify_mode, else False.

    additional kwargs will be passed to simplify(), expand(), and/or simplified(),
        whenever doing those operations "by default",
        e.g. due to calling self._do_simplify after a solvestep, if simplify_mode='simplify'.
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, system, targets, *, simplify_mode=None, simplify_now=True, essentialize_solved=None,
                 **kw__simplify):
        self.systems = []  # << history of solve steps. (see property 'system' of type(self))
        self.system = INITIALIZERS.system_solve_state(*system, targets=targets)
        self._simplify_mode = simplify_mode
        self._essentialize_solved = essentialize_solved
        self.kw__simplify = kw__simplify
        # set up initial values for things
        self._is_simplified = False
        self.solution = None  # << solution (once it is known), after restore_from_essentialize()
        self._essentialized_solution = None  # << solution, before restore_from_essentialize()
        if simplify_now:
            self._do_simplify()

    # # # PROPERTIES # # #
    @property
    def system(self):
        '''the most recent form of the system of equations in self.'''
        return self.systems[-1]
    @system.setter
    def system(self, value):
        '''append value to self.systems, unless value is self.system already.'''
        if (len(self.systems) == 0) or (value is not self.systems[-1]):
            self.systems.append(value)

    targets = property(lambda self: self.system.targets,
                       doc='''the remaining targets to solve for in self.''')

    _is_simplified = property(lambda self: self.system._is_simplified,
                              lambda self, value: setattr(self.system, '_is_simplified', value),
            doc='''whether self.system is the result of self._do_simplify().''')

    simplify_mode = property(lambda self: self._simplify_mode if (self._simplify_mode is not None)
                                                else DEFAULTS.SOLVING_SYSTEM_SIMPLIFY_MODE,
                             lambda self, value: setattr(self, '_simplify_mode', value),
            doc='''how to simplify after each solvestep. More docs available in class description (use help()).''')

    essentialize_solved = property(lambda self: self._essentialize_solved if (self._essentialize_solved is not None)
                                                else ('essentialize' in self.simplify_mode),
                                   lambda self, value: setattr(self, '_essentialize_solved', value),
            doc='''whether to essentialize solved equation after each solvestep, before plugging into other equations.''')

    # # # DISPLAY # # # 
    def _repr_contents(self, **kw):
        '''list of contents to put as comma-separated list into repr of self.'''
        return [f'system={_repr(self.system, **kw)}', f'targets={_repr(self.targets, **kw)}']

    def __str__(self, **kw):
        '''returns self.system.__str__'''
        return self.system.__str__(**kw)

    def view_history(self, n=None, reverse=True, *, unsolved_only=False,
                     un_essentialized=True, simplify=False, **kw__simplify):
        '''does system.view() for system in self.systems.

        n: number or None
            number of systems to view. (Or -number to hide, if negative.)
            None --> show all systems.
        reverse: bool, default True
            whether to put youngest (i.e., current) system first in the order (vs. last, if False).
        unsolved_only: bool, default False
            whether to only show unsolved equations.
        un_essentialized: bool, default True
            whether to restore_from_essentialized() for each system just before viewing.
            (doesn't edit the original systems)
        simplify: bool, default False
            whether to simplify() for each system just before viewing.
            (doesn't edit the original systems)
        additional kwargs go to system.simplify() if simplify.
        '''
        ll = list(enumerate(self.systems))
        if reverse: ll = ll[::-1]
        if n is not None: ll = ll[:n]
        more_i_info = {0: ' (original system)', len(self.systems)-1: ' (current system)'}
        for i, system in ll:
            info = more_i_info.get(i, '')
            print(f"systems[{i}]{info}:")
            if un_essentialized:
                system = system.restore_from_essentialized(unsolved_only=unsolved_only)
            if simplify:
                system = system.simplify(**kw__simplify)
            system.view(unsolved_only=unsolved_only)

    def view_steps_simple(self, n=None, **kw__simplify):
        '''alias to self.view_history(), with n=n, reverse=False, simplify=True,
            un_essentialized=True, unsolved_only=False, **kw__simplify.

        I.e., shows the steps in self, in order from original system to final result.
        Show up to n steps (or all but -n steps, if n is negative).
        For each step, show all equations in the system, even the previously-solved ones.
        Also, before viewing, replace EssenceSymbols with what they represent,
            and simplify each equation, so it is easier to look at & understand.
        '''
        return self.view_history(n=n, reverse=False, simplify=True,
                un_essentialized=True, unsolved_only=False, **kw__simplify)

    # # # ESSENTIALIZING # # #
    def _essentialize(self, unsolved_only=True):
        '''put the equations in self into essentialized_expression == 0 format.
        if unsolved_only, only do this for the unsolved equations in self.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        self.system = self._essentialized(unsolved_only=unsolved_only)

    def _essentialized(self, unsolved_only=True):
        '''return result of putting eqs in self into essentialized_expression == 0 format.
        if unsolved_only, only do this for the unsolved equations in self.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self._essentialized_system(self.system, unsolved_only=unsolved_only)    

    def _essentialized_system(self, system, unsolved_only=True):
        '''return result of putting eqs in system into essentialized_expression == 0 format.
        essentializing with respect to targets in self.
        if unsolved_only, only do this for the unsolved equations in self.
        '''
        targets = self.targets
        eqns = [eqn if eqn.solved else
                    eqn._new(essentialize(eqn.subtract_rhs().lhs, targets=targets), ZERO)
                for eqn in system]
        return system._new(*eqns)

    # # # SIMPLIFYING # # #
    def _do_simplify(self, mode=None, **kw__simplify):
        '''simplifies system in self, based on mode (self.mode if None).

        mode: 'essentialize', 'simplify', 'expand', 'simplified', True, False, or None.
            how to simplify.
            see help(type(self)) for details on mode options.
            None --> use self.simplify_mode

        additional kwargs are passed to simplify(), simplified(), or expand() if any are called. 

        Afterwards, set self._is_simplified = True
        '''
        kw = {**self.kw__simplify, **kw__simplify}
        if mode is None:
            mode = self.simplify_mode
        modes = mode if isinstance(mode, tuple) else (mode,)
        system = orig_system = self.system
        for mode_ in modes:
            # simplify based on mode
            if mode_ == 'essentialize':
                system = self._essentialized_system(system, unsolved_only=True)
            elif mode_ == 'simplify' or mode_ == True:
                system = system.simplify(**kw)
            elif mode_ == 'expand':
                system = system.expand(**kw)
            elif mode_ == 'simplified':
                system = system.simplified(**kw)
            elif mode_ == False:
                pass  # << do nothing
            else:
                errmsg = ("Invalid mode. Options: ['essentialize', 'simplify', 'expand', 'simplified', True, False]. "
                          f"Got: mode={repr(mode_)}")
                raise InputError(errmsg)
        if system is not orig_system:
            self._is_simplified = True
            self.system = system

    # # # SOLVESTEP OPTIONS # # #
    _solving_order_docs = \
        '''Optimized for "Dispersion relation"-type systems, where the goal is
            to reach a nontrivial equation from self, containing none of the targets.

        The idea is that solving will occur in this order:
            - if any eqs have 0 targets, crash (not sure how to handle that).
            - if any eqs have 1 target, eliminate the target.
                (crash if there exists an equation with 1 target but eliminate is not possible.)
            - prioritize options in order of these "categories":
                - solving vector equations for vector targets
                - solving scalar equations for scalar targets
              within each "category", prioritize from fewest targets to most targets.'''

    @format_docstring(order_docs = _solving_order_docs)
    def iter_solvestep_options(self):
        '''yield solvestep options in self.
        Yields in order that they should be tested.

        [TODO][EFF] improve efficiency inside this function?

        {order_docs}
        '''
        system = self.system
        eqs = list(system)
        targets = system.targets   # == self.targets

        if len(targets) == 0:
            # [TODO] maybe this will be a SolvingPatternError eventually.
            #    for now, not exactly sure when it will occur, so using NotImplementedError.
            raise NotImplementedError(f'Solve attempt for SystemSolver object with 0 targets remaining')
        if len(eqs) == 0:
            # [TODO] maybe this will be a SolvingPatternError eventually.
            #    for now, not exactly sure when it will occur, so using NotImplementedError.
            raise NotImplementedError(f'Solve attempt for SystemSolver object with 0 equations remaining')

        t2e = system.imap_target_to_equations
        e2t = system.imap_equation_to_targets

        ieq_options = [i for i, eq in enumerate(eqs) if not eq.solved]

        ieq_to_ntargets = {i: len(e2t[i]) for i in ieq_options}
        ieqs = sorted(ieq_options, key=lambda ieq: ieq_to_ntargets[ieq])  # << sorted by number of targets.
        # if any eqs have 0 targets, crash
        if ieq_to_ntargets[ieqs[0]] == 0:
            # Equation with 0 targets.. should we just ignore it? For now, we crash. 
            # Don't need to handle this case for "Disperson relation"-type system.
            raise NotImplementedError(f'Not sure how to handle equation with 0 targets:\n{eqs[ieqs[0]]}')
        # if any eqs have 1 target, try to eliminate the target and return the result.
        elif ieq_to_ntargets[ieqs[0]] == 1:
            # Equation with 1 target.. hopefully we can eliminate the target.
            # Don't need to consider any other equations in this case,
            #   for "Disperson relation"-type system.
            ieq = ieqs[0]
            itarget = e2t[ieq][0]  # (<< the one and only target for this equation)
            for method in ELIMINATE_METHOD_INFOS.values():
                yield SolveStepInfo(ieq, itarget, method, eqn=eqs[ieq], target=targets[itarget])
            # crash if another equation *also* has 1 target.
            if (len(ieqs) > 1) and ieq_to_ntargets[ieqs[1]] == 1:
                target_info_str = f'(itarget={itarget}, target={targets[itarget]})'
                errmsg = (f'Multiple equations with exactly 1 target {target_info_str} each:\n'
                          f'{eqs[ieqs[0]]}\n\n{eqs[ieqs[1]]}')
                raise NotImplementedError(errmsg)
            return   # stop trying 
        # else, all eqs have 2 or more targets.
        # bookkeeping / pre-calculate some things:
        ieq_is_vector = {ieq: is_vector(eqs[ieq]) for ieq in ieqs}
        itarget_is_vector = [is_vector(targets[i]) for i, _target in enumerate(targets)]
        # first solve vector eqs for vector targets.
        for ieq in ieqs:
            eq = eqs[ieq]
            if ieq_is_vector[ieq]:
                for itarget in e2t[ieq]:
                    if itarget_is_vector[itarget]:
                        for method in SOLVE_METHOD_INFOS.values():
                            yield SolveStepInfo(ieq, itarget, method, eqn=eq, target=targets[itarget])
        # next, solve scalar eqs for scalar targets.
        for ieq in ieqs:
            eq = eqs[ieq]
            if not ieq_is_vector[ieq]:
                for itarget in e2t[ieq]:
                    if not itarget_is_vector[itarget]:
                        for method in SOLVE_METHOD_INFOS.values():
                            yield SolveStepInfo(ieq, itarget, method, eqn=eq, target=targets[itarget])
        # << if we get here, there's nothing left to try anymore.
        return    # return None; stop iterating.

    @format_docstring(order_docs = _solving_order_docs)
    def solvestep_options(self):
        '''return list of solvestep options in self, in the order that they should be tested.
        Equivalent to list(self.iter_solvestep_options()).

        {order_docs}
        '''
        return list(self.iter_solvestep_options())

    del _solving_order_docs  # << don't keep it in this namespace anymore.

    # # # DOING SOLVESTEP # # #
    def _eqsolve(self, ieq, itarget, method, *args__None, **kw__solve):
        '''"solve" equation ieq for target itarget using the method indicated.
        might "eliminate" instead of solve, depending on the method.
        Probably resulting in either (target == expression) or (expression == 0).

        Does not edit self.
        returns the resulting equation. Or, raise SolvingPatternError if can't solve.
        '''
        x = self.targets[itarget]
        eq = self.system[ieq]
        _quickcheck = getattr(eq, method.quickcheck)
        if _quickcheck(x):
            _method = getattr(eq, method.name)
            return _method(x, **kw__solve)
        else:
            raise SolvingPatternError(f'Failed to solve eqn {ieq} using method {method}')

    def take_solvestep(self, ieq, itarget, method, *args__None, **kw):
        '''"solve" equation ieq for target itarget using the method indicated.
        Plug solution into the other equations in self.
        EDITS SELF (note - the original; not a copy!), so that:
            self.system contains those updated equations,
            self.targets doesn't contain itarget anymore,
            and ieq is marked as solved.
        **kw go to solve method, self.system.subs(), and self._do_simplify().

        [TODO] handle "used an eliminate method" case
            (should we return a single equation then?...)

        raise SolvingPatternError if can't solve using those instructions.

        returns self if used a 'solve' method, else the solution (if used an 'eliminate' method).
        '''
        # solve (will raise SolvingPatternError if can't solve)
        solved_eq = self._eqsolve(ieq, itarget, method, **kw)
        if self.essentialize_solved:
            solved_eq = solved_eq.essentialize(targets=self.targets)
        system = self.system.put_solved_equation(ieq, solved_eq)
        system = system.subs(solved_eq, unsolved_only=True, **kw)
        # bookkeeping of remaining targets
        remaining_targets = _list_without_i(self.targets, itarget)
        system = system.with_set_attr('targets', remaining_targets)
        # edit self
        self.system = system
        self._is_simplified = False
        if 'eliminate' in method.name:
            self._essentialized_solution = solved_eq
            self.solution = solved_eq.restore_from_essentialized()
            return self.solution
        else:
            # simplify after solvestep:
            self._do_simplify(**kw)
            return self

    def solvestep(self, *, _verbose_errors=True, print_freq=None, **kw):
        '''perform the most appropriate next step for solving this system of equations.
        Does these things:
            1) determine the next-most-appropriate equation, variable, and method for solving.
            2) attempt to use that method on that equation & variable.
                If failed, return to step 1.
            3) if the method was a "solve" method, sub that solved eq into self, and return result.
                if the method was an "eliminate" method, return the result.
            if no methods work, raise SolvingPatternError
        '''
        updater = ProgressUpdater(print_freq, wait=True)
        _attempted_options = []
        for option in self.iter_solvestep_options():
            # bookkeeping / progress updates
            _attempted_options.append(option)
            def update_message():
                return (f'attempting: solve eq ({option.ieqn}) for target ({option.itarget}); '
                        f'method={repr(option.method.name)}, target={option.target}.')
            updater.printf(update_message)
            # attempt this option:
            try:
                result = self.take_solvestep(*option)
            except SolvingPatternError:
                continue
            else:
                break
        else:  # didn't break -- no good option
            errmsg = 'No solvestep methods worked!'
            if _verbose_errors:
                options_str = '\n'.join(str(opt) for opt in _attempted_options)
                errmsg += f' Attempted options:\n{options_str}'
            raise SolvingPatternError(errmsg)
        # << did break; found a good option. Return it.
        updater.finalize('solvestep')
        return result   # (could've put this inside the loop. Outside for easier debugging.)

    def solve(self, *, _verbose_errors=True, **kw):
        '''repeat solvestep until a solution is reached.'''
        result = self
        while result is self:
            result = self.solvestep(_verbose_errors=_verbose_errors, **kw)
        return result

with binding.to(EquationSystem):
    @binding
    def get_solver(self, targets, **kw__init):
        '''return SystemSolver to help with solving self, for the targets provided.
        Equivalent to SystemSolver(self, targets, **kw__init).
        '''
        return SystemSolver(self, targets, **kw__init)

    @binding
    def get_o1_solver(self, **kw__init):
        '''return SystemSolver to help with solving self, for targets = [all o1 symbols in self].
        Equivalent to SystemSolver(self, [s for s in self.get_symbols() if s.order==1], **kw__init).
        '''
        return SystemSolver(self, [s for s in self.get_symbols() if s.order==1], **kw__init)
