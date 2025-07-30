"""
File Purpose: convert a SymSolver expression to python
i.e. to something which can be evaluated in python.
"""
import builtins

from .power import Power
from .product import Product
from .sum import Sum
from .symbols import Symbol
from .equation import Equation
from .equation_system import EquationSystem
from ..abstracts import SymbolicObject, IterableSymbolicObject
from ..attributors import attributor
from ..tools import (
    Set,
    Binding,
)
binding = Binding(locals())


''' --------------------- convenience --------------------- '''

@attributor
def to_python(x):
    '''returns SSPython object from x.to_python() if possible,
    else raise NotImplementedError if x a SymbolicObject,
    else return SSPython object which just gives str(x).
        [TODO] more sophisticated than str(x)?
    '''
    try:
        x_to_python = x.to_python
    except AttributeError:
        if isinstance(x, SymbolicObject):
            raise NotImplementedError(f'{type(x)}.to_python()')
        else:
            def _return_str_x(*deps):
                return str(x)
            return SSPython(_return_str_x, name='constant', dependencies=[], deplayers=0, assign=False)
    else:
        return x_to_python()

def _clean_python_varname(s):
    r'''convert s to an acceptable variable name for python code.
    removes these characters: \ { } [ ] / as well as any whitespace.
    '''
    s = str(s)
    for char in r'\/{}[]' + ' \t\n':
        if char in s:
            s = s.replace(char, '')
    return s


''' --------------------- SSPython class --------------------- '''

class SSPython():
    '''class for storing python info about a SymSolver object.

    use self.code() to get python code as string.
    
    final: callable
        Will be given the dependencies as strings;
        should return a string of python code to evaluate the final expression,
            in terms of vars_ (and those dependencies).
        Example: for Sum, final might be:
            lambda *summands: ' + '.join(summands)
    dependencies: list of SSPython objects
        The objects with code that must be evaluated before the code given by self.final.
    deplayers: int
        symdeplayers(original object)
        self.code() puts expressions with smaller deplayers first.
    name: string, default 'obj'
        The base name to use for self when it appears as a dependency in another SSPython object.
        When converting to code as a dependency, will append '_i' to this name,
            where i is the next-largest unused integer for this name.
    force_name_int: bool, default True
        whether to force appending int to name.
    assign: bool, default True
        whether to add a line like "{name} = {final as code}" to the code
            if self appears as a dependency for another SSPython object.
            (If calling self.code(), ignore assign.)
    '''
    def __init__(self, final, dependencies=[], *, deplayers, id=None,
                 name='obj', force_name_int=True, assign=True):
        self.final = final
        self.dependencies = dependencies
        self.deplayers = deplayers
        self.id = id if id is not None else builtins.id(self)
        self.name = name
        self.force_name_int = force_name_int
        self.assign = assign
        self._init_check()

    def _init_check(self):
        '''checks that self.final is a callable, and that self.dependencies are SSPython objects.'''
        assert callable(self.final)
        for dep in self.dependencies:
            if not isinstance(dep, SSPython):
                raise TypeError(f'dependencies must be SSPython objects, but got {type(dep).__name__}')
            assert isinstance(dep, SSPython)

    # # # REPR # # #
    def __repr__(self):
        props = f'name={repr(self.name)}, len(dependencies)={len(self.dependencies)}, deplayers={self.deplayers}'
        return f'{type(self).__name__}({props})'

    # # # ITERATE THROUGH DEPENDENCIES # # #
    def _all_deps_dict(self):
        '''returns dict of {object id : dep} for all dependencies, their dependencies, etc.'''
        result = dict()
        for dep in self.dependencies:
            result[dep.id] = dep
            result.update(dep._all_deps_dict())
        return result

    def deplayers_to_deps(self):
        '''returns dict of {deplayers : [deps with that many deplayers]},
        for all dependencies, their dependencies, etc.
        '''
        alldeps = self._all_deps_dict()
        result = dict()
        for dep in alldeps.values():
            result.setdefault(dep.deplayers, []).append(dep)
        return result

    def iter_all_deps(self):
        '''yields all dependencies, their dependencies, etc., sorted by deplayers.
        (secondarily, sort by names.)'''
        deplayers_to_deps = self.deplayers_to_deps()
        for deplayers in sorted(deplayers_to_deps.keys()):
            for dep in sorted(deplayers_to_deps[deplayers], key=lambda dep: dep.name):
                yield dep

    def all_deps(self):
        ''''returns list of all dependencies, their dependencies, etc., sorted by deplayers.'''
        return list(self.iter_all_deps())

    def all_objs(self):
        '''returns self.all_deps() + [self].'''
        return self.all_deps() + [self]  # list addition

    # # # NAMES # # #
    def _unused_name(self, used_names=[], force_int=None):
        '''returns self.name_N, where N is the next-largest unused integer for this name.
        force_int: bool or None
            whether to force appending '_N'.
            if None, use self.force_name_int.
            If False, return self.name, if self.name is not in used_names.
        '''
        if force_int is None:
            force_int = self.force_name_int
        name = self.name
        i = 0
        result = f'{name}' + (f'_{i}' if force_int else '')
        while result in used_names:
            i = i + 1
            result = f'{name}_{i}'
        return result

    def _all_deps_names(self):
        '''returns unique names for self.all_deps(). give None for any deps with not dep.assign.'''
        result = []
        for dep in self.all_deps():
            name = dep._unused_name(used_names=result) if dep.assign else None
            result.append(name)
        return result

    def all_names(self):
        '''returns unique names for self.all_objs(). give None for any objs with not obj.assign.'''
        result = []
        for obj in self.all_objs():
            name = obj._unused_name(used_names=result) if obj.assign else None
            result.append(name)
        return result

    def id_to_name(self):
        '''returns dict of {obj.id: obj's unique name if obj.assign else None} for obj in self.all_objs().'''
        return {obj.id: name for obj, name in zip(self.all_objs(), self.all_names())}

    _clean_varname = staticmethod(_clean_python_varname)

    # # # CONVERT TO CODE # # #
    def id_to_rep(self):
        '''returns dict of {obj.id: obj's name if obj.assign else obj's code} for obj in self.all_objs().'''
        id_to_name = self.id_to_name()
        result = dict()
        for obj in self.all_objs():
            id_ = obj.id
            name = id_to_name[id_]
            result[id_] = name if name is not None else obj._final_expr(id_to_rep=result)
        return result

    def _final_expr(self, *, id_to_rep):
        '''returns string of code to evaluate just self.final in python,
        given a dict of {dep.id: dep's name if dep.assign else dep's code},
            which must include objs: each dep in self.dependencies.
        '''
        dep_names = [id_to_rep[dep.id] for dep in self.dependencies]
        return self.final(*dep_names)

    def _final_assignment(self, *, id_to_rep, id_to_name):
        '''returns (varname, code expression providing value for varname),
        given id_to_rep, a dict of {obj.id: obj's name if obj.assign else obj's code},
        and id_to_name, a dict of {obj.id: obj's name if obj.assign else None}.
        both dicts must include these objs: self, and each dep in self.dependencies.

        if not self.assign, use None instead of varname.
        '''
        name = id_to_name[self.id]
        expr = self._final_expr(id_to_rep=id_to_rep)
        return (name, expr)
    
    def code(self, final_as_eq=True):
        '''returns code to evaluate self and all dependencies, in python.
        final_as_eq: bool, default True
            whether final line will be an equation (as opposed to an expression).
            False --> returns something like 'expression'
            True --> returns something like 'result = expression'
        '''
        id_to_name = self.id_to_name()
        id_to_rep = self.id_to_rep()
        all_deps = self.all_deps()
        assigns = [obj._final_assignment(id_to_rep=id_to_rep, id_to_name=id_to_name) for obj in all_deps]
        lines = [f'{name} = {expr}' for name, expr in assigns if name is not None]
        final_expr = self._final_expr(id_to_rep=id_to_rep)
        if final_as_eq:
            lines.append(f'result = {final_expr}')
        else:
            lines.append(final_expr)
        return '\n'.join(lines)

    def print_code(self, **kw):
        '''prints self.code(**kw).'''
        print(self.code(**kw))


''' --------------------- binding to_python --------------------- '''

with binding.to(Symbol):
    @binding
    def to_python(self):
        '''returns SSPython object representing self. result.code() gives python code to evaluate.'''
        name = SSPython._clean_varname(str(self))
        final = lambda *deps: ' # user must provide a value here'
        deplayers = self.symdeplayers()
        return SSPython(final, name=name, id=id(self), deplayers=deplayers, force_name_int=False)

with binding.to(Sum):
    @binding
    def to_python(self):
        '''returns SSPython object representing self. result.code() gives python code to evaluate.'''
        final = lambda *deps: ' + '.join(deps)
        deps = [to_python(summand) for summand in self]
        deplayers = self.symdeplayers()
        return SSPython(final, name='sum', id=id(self), dependencies=deps, deplayers=deplayers)

with binding.to(Product):
    @binding
    def to_python(self):
        '''returns SSPython object representing self. result.code() gives python code to evaluate.'''
        final = lambda *deps: ' * '.join(deps)
        deps = [to_python(factor) for factor in self]
        deplayers = self.symdeplayers()
        return SSPython(final, name='mul', id=id(self), dependencies=deps, deplayers=deplayers)

with binding.to(Power):
    @binding
    def to_python(self):
        '''returns SSPython object representing self. result.code() gives python code to evaluate.'''
        final = lambda *deps: f'{deps[0]} ** {deps[1]}'
        deps = [to_python(self.base), to_python(self.exponent)]
        deplayers = self.symdeplayers()
        return SSPython(final, name='pow', id=id(self), dependencies=deps, deplayers=deplayers)

with binding.to(IterableSymbolicObject):
    @binding
    def to_python(self):
        '''returns SSPython object representing self. result.code() gives python code to evaluate.
        This is the default implementation for IterableSymbolicObject;
            the result will require that you separately define functions for each type of object,
            before you can actually evaluate the code.
        '''
        name = f'{type(self).__name__.lower()}'
        final = lambda *deps: f'{name}({", ".join(deps)})'
        deps = [to_python(arg) for arg in self]
        deplayers = self.symdeplayers()
        return SSPython(final, name=name, id=id(self), dependencies=deps, deplayers=deplayers)

with binding.to(Equation):
    @binding
    def to_python(self, as_assignment=None):
        '''returns SSPython object representing self. result.code() gives python code to evaluate.

        as_assignment: bool or None, default None
            whether to treat self as an "assignment" of a value to the lhs.
            None --> use self.assigns_symbol()
            if as_assignment, lhs tells name instead of a dependency; use rhs for final expression.
            otherwise, use name='equation', and (lhs, rhs) for final expression.
        '''
        if as_assignment is None: as_assignment = self.assigns_symbol()
        if as_assignment:
            name = SSPython._clean_varname(str(self.lhs))
            deps = [to_python(self.rhs)]
            final = lambda *deps: deps[0]
            deplayers = self.rhs.symdeplayers()
        else:
            name = 'equation'
            final = lambda *deps: f'({deps[0]}, {deps[1]})'
            deps = [to_python(self.lhs), to_python(self.rhs)]
            deplayers = self.symdeplayers()
        return SSPython(final, name=name, id=id(self), dependencies=deps, deplayers=deplayers)

with binding.to(EquationSystem):
    @binding
    def to_python(self, sequential=True):
        '''returns SSPython object representing self. result.code() gives python code to evaluate.

        sequential: bool, default True
            whether to treat self as a sequence of equations instead of a single object.
            True --> gives self[-1].to_python() but add earlier equations as dependencies.
            [TODO]
            False --> treat self as a single object; all symbols in self should be known before evaluating self.
        '''
        raise NotImplementedError('[TODO]')
