"""
File Purpose: Equation
This file just implements the Equation class, which stores info on lhs and rhs.
For routines that solve equations, see e.g. equation_solving.py.
"""
from .basics_tools import (
    gcf,
)
from .product import Product
from .symbols import Symbol
from ..abstracts import (
    OperationContainer, BinarySymbolicObject, SimplifiableObject, SubbableObject,
    simplify_op,
    _equals0,
    is_constant,
)
from ..initializers import initializer_for, INITIALIZERS
from ..tools import (
    equals, alias,
    format_docstring,
    operator_from_str, BINARY_MATH_OPERATORS,
)


''' --------------------- Equation --------------------- '''

class Equation(OperationContainer, BinarySymbolicObject,
               SimplifiableObject, SubbableObject):
    '''Equation, e.g. x==y.'''
    def __init__(self, lhs, rhs, *, label=None, solved=False, **kw):
        super().__init__(lhs, rhs, **kw)
        self.label = label
        self.solved = solved

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another instance of type(self) to be like self,
        via self._new(*args, **kw). Note these will be overwritten in _new by any **kw entered.
        '''
        kw = super()._init_properties()
        kw['label'] = self.label
        kw['solved'] = self.solved
        return kw

    def _repr_contents(self):
        '''returns contents to put inside 'Equation()' in repr for self.'''
        result = super()._repr_contents()
        if self.label is not None:
            result.append(f'label={repr(self.label)}')
        return result

    lhs = property(lambda self: self.t1,
                   lambda self, val: setattr(self, 't1', val),
                   doc='''left-hand-side of Equation.''')
    rhs = property(lambda self: self.t2,
                   lambda self, val: setattr(self, 't2', val),
                   doc='''right-hand-side of Equation.''')

    # # # ARITHMETIC # # #
    # NOTE: eqn arithmetic are defined later in this file,
    # also the code appears in a loop, not explicitly.
    # op(self, other Equation) --> op(self.lhs, other.lhs); op(self.rhs, other.rhs)
    # op(self, non-Equation obj) --> op(self.lhs, obj); obj(self.rhs, obj)

    # # # CONVENIENCE # # #
    def subtract_rhs(self):
        '''returns self.lhs - self.rhs = 0.'''
        return self._new(self.lhs - self.rhs, 0)

    def subtract_lhs(self):
        '''returns 0 = self.rhs - self.lhs'''
        return self._new(0, self.rhs - self.lhs)

    def with_label(self, label, *, force_new=True):
        '''returns new equation like self but with the label provided.
        force_new: bool
            whether to make a new equation even if label matches self.label.
        '''
        if force_new or (label != self.label):
            return self._new(*self, label=label)
        else:
            return self

    def relabeled(self, relabeler, *, force_new=True):
        '''returns new equation like self but relabeling using relabeler(self.label).
        relabeler: callable
            new label will be relabeler(self.label).
            if new label is independent of old label, use self.with_label(...) instead.
        force_new: bool
            whether to make a new equation even if relabeler(self.label)==self.label.
        '''
        label = relabeler(self.label)
        return self.with_label(label, force_new=force_new)

    def is_trivial(self):
        '''returns whether self is an equation of the form x=x.
        I.e., returns whether self.lhs == self.rhs.
        '''
        return equals(self.lhs, self.rhs)

    def assigns_symbol(self):
        '''returns whether self is an equation of the form x=expression, where x is a Symbol.'''
        return isintsance(self.lhs, Symbol)

    # # # MARKING SOLVED / UNSOLVED # # #
    # (Methods for actually solving equations should be provided elsewhere.
    # The methods here are just to mark whether the equation is "solved" or not.)
    def marked_as_solved(self):
        '''return copy of self with solved set to True.'''
        return self.with_set_attr('solved', True)
   
    def marked_as_unsolved(self):
        '''return copy of self with solved set to False.'''
        return self.with_set_attr('solved', False)

    as_solved = alias('marked_as_solved')
    as_unsolved = alias('marked_as_unsolved')

    # # # REPLACING SUBSCRIPTS # # #
    def subscriptize(self, old, listnew):
        '''self.ss(old, s) for s in listnew, making EquationSystem of result.
        if self.ss(old, s) makes no changes (i.e., is self), return EquationSystem(self).
        else, return EquationSystem with eqns self.ss(old, s) for s in listnew.
        '''
        if len(listnew)==0:
            return INITIALIZERS.equation_system()
        iter_new = iter(listnew)
        new0 = next(iter_new)
        result0 = self.ss(old, new0)
        if result0 is self:  # old not in subscripts of self.
            return INITIALIZERS.equation_system(self)
        result = [result0, *(self.ss(old, s) for s in iter_new)]
        return INITIALIZERS.equation_system(*result)


@initializer_for(Equation)
def equation(lhs, rhs, *, label=None, **kw):
    '''returns Equation representing lhs == rhs.
    This just means return Equation(lhs, rhs, label=label, **kw).
    '''
    return Equation(lhs, rhs, label=label, **kw)


''' --------------------- Equation math --------------------- '''

def _eqn_math(opstr, op=None):
    '''return a function g(self, b) to do op to each side.
    if b is an Equation, result is equation(op(self.lhs, b.lhs), op(self.rhs, b.rhs)).
    otherwise, result is super().opstr(b)
        (which applies super().opstr to each side; see OperationContainer for details)

    opstr: str
        use operator with this name.
        if op not provided, opstr must be a builtin magic method such as '__add__' or '__rtruediv__'.
    op: None or callable
        if provided, use this when b is an euqation
    '''
    if op is None:
        doc_op = f'op is the builtin operator implied by: {repr(opstr)}.'
        op = operator_from_str(opstr)
    else:
        doc_op = f'For non-equation b, does super().{repr(opstr)}(b).\nFor equation b, uses op={op}.'
    @format_docstring(doc_op=doc_op)
    def do_eqn_op(self, b):
        '''returns super().op(b) if b is not an equation, else equation(op(self.lhs, b.lhs), op(self.rhs, b.rhs))
        super().op(b) gives equation(op(self.lhs, b), op(self.rhs, b)); see OperationContainer for details.
        {doc_op}
        '''
        if isinstance(b, Equation):
            return self.bopwise(op, b)
        else:
            return getattr(super(Equation, self), opstr)(b)
    return do_eqn_op

for _opstr in BINARY_MATH_OPERATORS:
    setattr(Equation, _opstr, _eqn_math(_opstr))


''' --------------------- Equation SIMPLIFY_OPS --------------------- '''

@simplify_op(Equation, alias='_divide_common_factor')
def _equation_divide_common_factor(self, **kw__None):
    '''removes factor common to both sides, e.g.: a b x = a c y --> b x = c y.
    g x = 0 --> x = 0;   0 = g x --> 0 = x  (if g is nonzero constant AND x is not constant)
    Does not alter equations where both sides are the same, e.g. x=x.
    '''
    if equals(self.lhs, self.rhs):
        return self
    factor, lhs_over_f, rhs_over_f = gcf(self.lhs, self.rhs)
    # handle a b x = a c y --> b x = c y.
    if not equals(factor, 1):
        return self._new(lhs_over_f, rhs_over_f)
    # handle 'one side is 0'
    else: # equals(factor, 1):
        # handle gx=0 --> x=0 if g nonzero constant AND x non-constant.
        new_lhs = _divide_common_factor_c0_from_sides(self.lhs, self.rhs)
        if new_lhs is not self.lhs:
            return self._new(new_lhs, self.rhs)
        # handle 0=gx --> 0=x if g nonzero constant AND x non-constant.
        new_rhs = _divide_common_factor_c0_from_sides(self.rhs, self.lhs)
        if new_rhs is not self.rhs:
            return self._new(self.lhs, new_rhs)
        # handle "this simplification not applicable" case
        return self

def _divide_common_factor_c0_from_sides(side0, side1):
    '''helper for _divide_common_factor.
    returns None if [gx=0 --> x=0 with nonzero constant g] simplification is not applicable.
    (assumes side0 would be the Product side, and side1 would be the side equal to 0)
    If it is applicable, returns new side0, new side1 after doing the simplification.
    '''
    if isinstance(side0, Product) and _equals0(side1):
        constants, varys = side0.dichotomize(is_constant)
        if len(constants)>0 and len(varys)>0:
            constant = side0._new(*constants)
            if not _equals0(constant):
                return side0._new(*varys)
    return side0