"""
File Purpose: Inequality
Very little "solving" or other "understanding" of the inequalities are presented here.
But we allow to represent inequalities via the Inequality class.
"""

from ..abstracts import (
    OperationContainer, BinarySymbolicObject, SimplifiableObject, SubbableObject,
)

from ..tools import (
    _str, _repr,
)



INEQUALITY_STRINGS = {
    'eq': ('eq', '__eq__',   '='  , '=='),
    'ne': ('ne', '__ne__', r'\neq', '!='),
    'gt': ('gt', '__gt__', r'\gt' , '>' ),
    'ge': ('ge', '__ge__', r'\geq', '>='),
    'lt': ('lt', '__lt__', r'\lt' , '<' ),
    'le': ('le', '__le__', r'\leq', '<='),
}
INEQUALITY_STRING_TYPE = {_ie: key for (key, _ies) in INEQUALITY_STRINGS.items() for _ie in _ies}
# e.g. {'ne': 'ne', '__ne__': 'ne', r'\neq': 'ne', '!=': 'ne', 'gt': 'gt', '__gt__': 'gt', ...}

INEQUALITY_STRING_MODES = {
    'type': 0,
    'key': 0,
    'magic': 1,
    'dunder': 1,
    'latex': 2,
    'mathtext': 2,
    'python': 3,
    'code': 3,
}


def inequality_interpret(relation_str, mode='magic'):
    r'''converts relation_str to the corresponding string in the given mode.
    E.g. (' != ', mode='magic') --> '__ne__';  ('__gt__', mode='latex') --> r'\gt'

    result will always be stripped (no leading / trailing whitespace).

    relation_str: string representing the relation in some mode.
        insensitive to leading and trailing spaces.
    mode: string telling which mode to use.
        case-insensitive.
        'type' or 'key' --> convert to two-letter representation
            E.g. 'ne', 'lt', 'ge'
        'magic' or 'dunder' --> convert to python magic method.
            E.g. '__ne__', '__lt__', '__ge__'
        'latex' or 'mathtext' --> convert to latex format.
            E.g. r'\neq', r'\lt', r'\geq'
        'python' or 'code' --> convert to python code format.
            E.g. '!=', '<', '>='
    '''
    mode_idx = INEQUALITY_STRING_MODES[mode.lower()]
    relation_strs = INEQUALITY_STRING_LOOKUP[relation_str.lower()]
    return relation_strs[mode_idx]

class Inequality(OperationContainer, BinarySymbolicObject,
                SimplifiableObject, SubbableObject):
    '''class for representing inequalities, e.g. x != 0.'''
    def __init__(self, t1, relation_str, t2, **kw):
        self.relation_type = INEQUALITY_STRING_TYPE[relation_str]
        super().__init__(t1, t2, **kw)

    def _new(self, t1, t2, **kw):
        result = self.initializer(t1, self.relation_type, t2, **kw)
        self._transmit_genes(result)
        return result

    lhs = property(lambda self: self[0],
                   lambda self, val: setattr(self, 't1', val),
                   doc='''left-hand-side of Inequality.''')
    rhs = property(lambda self: self[1],
                   lambda self, val: setattr(self, 't2', val),
                   doc='''right-hand-side of Inequality.''')
    _relation = property(lambda self: inequality_interpret(self.relation_type, mode='latex'),
                         doc='''relation string of self in latex form, e.g. r'\neq', r'\lt', r'\geq'.''')

    def __str__(self, mode='latex', **kw):
        relation = inequality_interpret(self.relation_str, mode=mode)
        lhs = _str(self.t1, **kw)
        rhs = _str(self.t2, **kw)
        result = '{} {} {}'.format(lhs, relation, rhs)
        return self._str_assumptions(str_in=result, **kw)

    def _repr_contents(self, **kw):
        return [_repr(self.t1, **kw), repr(self.relation_str), _repr(self.t2, **kw)]