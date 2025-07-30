"""
File Purpose: look up "magic" operator from string

E.g. '__add__' --> operator.__add__
The challenge is that the operator module does not include reverse methods, e.g. '__radd__'.
"""

import operator

from ..pytools import format_docstring


def operator_from_str(s):
    '''returns the (binary, builtin) operator corresponding to string s.
    E.g. '__add__' --> operator.__add__.
    If s is not an attribute of operator, checks for reverse methods,
        e.g. if s == '__rsub__', returns lambda x, y: y - x
    '''
    try:
        return getattr(operator, s)
    except AttributeError:
        pass  # handled below
    try:
        opstr_without_r = _no_r_operator_from_str(s)
    except ValueError:
        raise ValueError(f'no operator corresponding with s={repr(s)}') from None
    try:
        op_without_r = getattr(operator, opstr_without_r)
    except AttributeError:
        raise ValueError(f'no operator corresponding with s={repr(s)}') from None
    else:
        @format_docstring(opstr=opstr_without_r)
        def op(x, y):
            '''returns {opstr}(y, x)'''
            return op_without_r(y, x)
        return op

def _no_r_operator_from_str(s):
    '''returns s without 'r' after '__'. E.g. '__rsub__' --> '__sub__'.
    If that is impossible, raise ValueError.
    '''
    if not s.startswith('__r'):
        raise ValueError(f"cannot remove 'r' after '__' for s not starting with '__r'. Got s={repr(s)}")
    s_without_lead = s[len('__r') : ]
    return f'__{s_without_lead}'

_BINARY_MATH_OPSTRS = ['__add__', '__radd__', '__sub__', '__rsub__', '__mul__', '__rmul__',
                       '__truediv__', '__rtruediv__', '__floordiv__', '__rfloordiv__',
                       '__pow__', '__rpow__', '__mod__', '__rmod__', '__matmul__', '__rmatmul__']
BINARY_MATH_OPERATORS = {opstr : operator_from_str(opstr) for opstr in _BINARY_MATH_OPSTRS}