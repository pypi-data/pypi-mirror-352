"""
File Purpose: EquationSystem
"""
from .equation import Equation
from ..abstracts import (
    OperationContainer, IterableSymbolicObject, SimplifiableObject, SubbableObject,
    SymbolicObject,
)
from ..errors import PatternError
from ..initializers import initializer_for, INITIALIZERS
from ..tools import (
    equals,
    format_docstring,
    viewdict,
)


''' --------------------- EquationSystem --------------------- '''

class EquationSystem(OperationContainer, IterableSymbolicObject,
                     SimplifiableObject, SubbableObject):
    '''system of equations, e.g. {x+y==7, y**2/x+z**4==0, z==3}
    Can have any number of equations, possibly even 0 equations.
    Note: attempts to follow the "immutable" design intention.
        Rather than changing an EquationSystem, make a new one with the desired changes.

    Duing substitution algorithms, can use kwarg unsolved_only=False to also sub into "solved" equations.
    '''
    # # # CREATING / INSTANTIATION # # #
    @classmethod
    def from_dict(cls, label_to_eqn_or_tuple):
        '''create an equation system given a dict which maps from labels to eqns;
        the eqns can be represented as Equation or tuple objects.
        Recommend: use string keys to allow index-by-label option for EquationSystem.

        [TODO] use classmethods instead of just the INITIALIZERS code;
            though the INITIALIZERS code could still point to the appropriate classmethods.
            Note: this method doesn't use cls; it always creates an EquationSystem.
        '''
        d = label_to_eqn_or_tuple
        return INITIALIZERS.equation_system(*d.values(), labels=d.keys())

    def to_dict(self):
        '''turn self into a dict that maps from labels to eqns. Requires all labels to be unique.'''
        result = viewdict()
        for eq in self:
            if eq.label in result:
                raise PatternError(f"Duplicate label, label={eq.label}.")
            result[eq.label] = eq
        return result

    # # # COMBINING EQUATION SYSTEMS / SLICING EQUATION SYSTEM # # #
    def __add__(self, x):
        '''return self + x. If x is an EquationSystem, return system joining self and x.
        Otherwise, add x to every side of every equation in self.
        '''
        if isinstance(x, EquationSystem):
            return self.extend(x)
        else:
            return super().__add__(x)

    def drop_trivial(self, remove_repeats=True):
        '''removes all equations of the form x=x, from self.
        Also remove equations which are repeats of previous equations.
        '''
        eqns = list(self)
        result = []
        for i, eqn in enumerate(eqns):
            if eqn.is_trivial():
                continue
            if remove_repeats:
                for j in range(i):
                    if equals(eqn, eqns[j]):
                        continue
            result.append(eqn)
        return self._new(*result)

    # # # SUBSTITUTIONS # # #
    def _subs_check_term(self, eq, unsolved_only=True, skip=[], **kw__super):
        '''returns whether to check eq during substitutions for self.
        if unsolved_only, check eqs only if they are not marked as solved.
        if skip is not an empty list, skip eq if eq is self[iskip] for any iskip in skip.
        otherwise, check all eqs.
        '''
        if any(eq is self[iskip] for iskip in skip):
            return False
        elif unsolved_only:
            return (not eq.solved)
        else:
            return super()._subs_check_term(eq, **kw__super)

    def defs_subs(self, *defpairs, **kw__subs_loop):
        '''return copy of self but replacing eqns with lhs in defpairs with (lhs, rhs) from defpairs.
        defpairs: (lhs, rhs) pairs
            any equation in self with matching lhs will have rhs replaced.

        Example:
            equation_system((x,1),(y,2),(z,3)).def_subs((x,4),(z,5))
            <--> equation_system((x,4),(y,2),(z,5))
        '''
        eqns = list(self)
        for lhs, rhs in defpairs:
            for i, eq in enumerate(eqns):
                if equals(eq.lhs, lhs):
                    eqns[i] = eqns[i]._new(lhs, rhs)
        return self._new(*eqns)

    # # # INDEXING # # #
    def _term_index_equality_check(self, item_from_self, term):
        '''tells whether item_from_self equals term for the purposes of indexing (see self.get_index).
        Specifically, also checks here if LHS of equation equals term. This allows indexing by LHS.
        Examples of equivalency of different indexing options:
        eqs = EquationSystem(Equation(x, 7), Equation(y, 1+z), Equation(u**2, -1)),
            eqs[0] <--> eqs[x] <--> eqs[Equation(x, y)];
            eqs[1] <--> eqs[y] <--> eqs[Equation(y, 1+z)];
            eqs[2] <--> eqs[u**2] <--> eqs[Equation(u**2, -1)].
        '''
        return equals(item_from_self[0], term) or super()._term_index_equality_check(item_from_self, term)

    def _is_indexkey(self, key):
        '''returns whether key might be a way to lookup an index of self via self.key_index().
        Here we return isinstance(key, str). I.e. strings (but nothing else) can be indexkeys.
        '''
        return isinstance(key, str)

    def _get_indexkey(self, term):
        '''returns indexkey from term.
        Here we return term.label, I.e. use an equation's "label" attribute its indexkey.
        '''
        return term.label

    @property
    def labels(self):
        '''labels of equations in self.
        Result has same length as self. Label will be None if not found.
        '''
        return tuple(getattr(eq, 'label', None) for eq in self)

    def with_labels(self, new_labels, *, force_new=True):
        '''create new equation system with same equations as in self but using new_labels.
        force_new: bool
            whether to make a new equation even if new label matches equation.label.
        '''
        return self._new(*(eqn.with_label(newl, force_new=force_new) for eqn, newl in zip(self, new_labels)))

    def relabeled(self, relabeler, *, force_new=True):
        '''create new equation system with same equations as in self but using relabeler to adjust labels.
        relabeler: callable
            new_label = relabeler(old label), for each equation in self.
            if new labels are independent of old label, use self.with_labels(...) instead.
        force_new: bool
            whether to make a new equation even if new label matches equation.label.
        '''
        return self._new(*(eqn.relabeled(relabeler, force_new=force_new) for eqn in self))

    # # # SOLVED / UNSOLVED -- TRACKING # # #
    solved = property(lambda self: tuple(i for i, eq in enumerate(self) if eq.solved),
            doc='''indices corresponding to solved equations in self.''')
    unsolved = property(lambda self: tuple(i for i, eq in enumerate(self) if not eq.solved),
            doc='''indices corresponding to unsolved equations in self.''')

    def marked_as_solved(self, i):
        '''return copy of self with eqn(s) i marked as solved.
        i: slice, int, str, SymbolicObject, or list of those things.
        '''
        generic_idx = self.generic_indices(i)
        return self._new(*((eq.marked_as_solved() if j in generic_idx else eq) for j, eq in enumerate(self)) )

    def marked_as_unsolved(self, i):
        '''return copy of self with eqn(s) i marked as unsolved.
        i: slice, int, str, SymbolicObject, or list of those things.
        '''
        generic_idx = self.generic_indices(i)
        return self._new(*((eq.marked_as_unsolved() if j in generic_idx else eq) for j, eq in enumerate(self)) )

    def unsolved_system(self):
        '''return EquationSystem with only the unsolved equations from self.'''
        return self._new(*(self[i] for i in self.unsolved))

    # # # SOLVING # # #
    def solution_put(self, i, var, *, subs=False, mark_solved=False, **kw__solve):
        '''return new system where eqn i is replaced by solution to eqn i for var var.
        if mark_solved, also mark that equation as solved.
        if subs, also sub the solution into all the other unsolved equations in the result.
        i: slice, int, str, or SymbolicObject
        '''
        i_int = self.get_index(i)
        solved_eq = self[i_int].solve(var, **kw__solve)
        result = self.put_solved_equation(i_int, solved_eq)
        if subs:
            result = result.subs(result[i_int], unsolved_only=True, **kw__solve)
        if not mark_solved:
            result = result.marked_as_unsolved(i_int)
        return result

    def put_solved_equation(self, ieq, solved_eq):
        '''return copy of self with self[ieq] replaced by solved_eq.marked_as_solved().
        ieq must be an integer; used to index a list rather than self.
        '''
        eqsolved = solved_eq.marked_as_solved()
        eqns = list(self)
        eqns[ieq] = eqsolved
        return self._new(*eqns)

    # # # REPLACING SUBSCRIPTS # # #
    def subscriptize(self, old, listnew):
        '''self.ss(old, s) for s in listnew, making EquationSystem of result.
        Useful if trying to make multiple versions of self with different subscripts,
        but only want multiples of equations that actually contain the subscripts.
        '''
        return self._new(*(eq for eqn in self for eq in eqn.subscriptize(old, listnew)))


@initializer_for(EquationSystem)
def equation_system(*eqn_or_tuple_objects, labels=None):
    '''create a new EquationSystem using the equations provided.
    Always returns an EquationSystem, even if no args are entered.

    *args: each should be either an Equation or a tuple.
        tuples will be converted to Equation objects.
        if any args are not an Equation or tuple, raise TypeError.
            (This helps prevent accidental errors when other iterables are involved.)

    labels: None or list with length == number of equations (or tuples) input here.
        if labels[i] is provided, put label=labels[i] for the i'th input.
            (if i'th input was an Equation, make a new equation if the input label doesn't match.)
        Note: labels[i] = None indicates "no label provided".
        See also: EquationSystem.from_dict(labels_to_eqn_or_tuple),
            which provides similar functionality but allows to input a dict instead.

    implementation detail note:
        by using INITIALIZERS.equation, we ensure that equation_system() will remain appropriate
        even if a later module defines a new function as the initializer for equation.
    '''
    eqns = []
    if labels is None: labels = (None for _ in eqn_or_tuple_objects)
    for arg, label in zip(eqn_or_tuple_objects, labels):
        if isinstance(arg, tuple):
            eqn = INITIALIZERS.equation(*arg, label=label)
        elif isinstance(arg, Equation):
            if label is not None:
                eqn = arg.with_label(label, force_new=False)
            else:
                eqn = arg
        else:
            raise TypeError(f'expect all entries to be tuples or Equation but got {type(arg)}')
        eqns.append(eqn)
    return EquationSystem(*eqns)


@format_docstring(equation_system_docs=equation_system.__doc__)
def eqsys(*eqn_or_tuple_objects, labels=None, **kw):
    '''alias for INITIALIZERS.equation_system(...).
    
    {equation_system_docs}
    '''
    return INITIALIZERS.equation_system(*eqn_or_tuple_objects, labels=labels, **kw)
