"""
File Purpose: convert a SymSolver expression to python
i.e. to something which can be evaluated in python.
"""

from .abstract_operators import AbstractOperator
from .generic_operations import GenericOperation
from ..basics import SSPython, to_python
from ..tools import (
    Binding,
)

binding = Binding(locals())


''' --------------------- generic --------------------- '''

with binding.to(AbstractOperator):
    @binding
    def to_python(self):
        '''returns SSPython object representing self. result.code() gives python code to evaluate.'''
        name = SSPython._clean_varname(str(self.frep))
        final = lambda *deps: ' # please define this function before evaluating code...'
        deplayers = self.symdeplayers()
        return SSPython(final, name=name, id=id(self), deplayers=deplayers, force_name_int=False)

with binding.to(GenericOperation):
    @binding
    def to_python(self):
        '''returns SSPython object representing self. result.code() gives python code to evaluate.'''
        name = f'{SSPython._clean_varname(self.operator.frep)}_val'
        final = lambda *deps: f'{deps[0]}({deps[1]})'
        deps = [to_python(self.operator), to_python(self.operand)]
        deplayers = self.symdeplayers()
        return SSPython(final, name=name, id=id(self), dependencies=deps, deplayers=deplayers)
