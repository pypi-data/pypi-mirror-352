"""
File Purpose: Derivative objects

[TODO] vector derivative operator/ion should be a separate operator/ion;
    when initializing, should give a vector operator/ion or not, based on dvar.
"""
from .derivatives_tools import take_derivative
from ...abstracts import (
    SymbolicObject, SubbableObject,
    simplify_op,
    _equals0, contains_deep,
)
from ...initializers import initializer_for, INITIALIZERS
from ...precalc_operators import (
    LinearOperator, LinearOperation,
    is_operator,
)
from ...vectors import (
    is_vector,
)
from ...tools import (
    _repr, _str,
    equals,
    format_docstring,
    caching_attr_simple,
)
from ...defaults import ZERO, ONE


''' --------------------- property docs --------------------- '''

_derivative_propdocs = {
    'dvar': '''taking the derivative with respect to this variable. E.g. x in d/dx''',
    'partial': '''whether this is a partial derivative''',
} 

''' --------------------- DerivativeSymbol --------------------- '''

class DerivativeSymbol(SubbableObject):
    '''derivative Symbol. For something like d/dx.
    Contains no rules for evaluating / calling on an object to create a derivative;
    not intended for direct use. See DerivativeOperator or DerivativeOperation instead.

    dvar: object, probably a SymbolicObject.
        taking the derivative with respect to this variable.
    partial: bool, default False
        whether this is a partial derivative.  
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, dvar, partial=False):
        '''initialize self to be d/d(dvar).'''
        self._dvar = dvar
        self._partial = partial

    dvar = property(lambda self: self._dvar, doc=_derivative_propdocs['dvar'])
    partial = property(lambda self: self._partial, doc=_derivative_propdocs['partial'])

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another instance of type(self) to be like self,
        via self._new(*args, **kw). Note these will be overwritten in _new by any **kw entered.
        '''
        kw = super()._init_properties()
        kw['partial'] = self.partial
        return kw

    def _init_args(self):
        '''returns args to go before entered args during self._new, for self.initializer.
        self._new(*args, **kw) will lead to self.initializer(*self._init_args(), *args, **kw).
        '''
        return (self.dvar,)

    def with_partial(self, partial):
        '''returns copy of self with partial=partial.'''
        return self._new(partial=partial)

    def as_partial(self):
        '''returns copy of self with partial=True'''
        return self.with_partial(True)

    def as_total(self):
        '''returns copy of self with partial=False'''
        return self.with_partial(False)

    # # # DISPLAY # # #
    def _repr_contents(self, **kw):
        '''returns contents to put inside 'DerivativeSymbol()' in repr for self.'''
        contents = [_repr(self.dvar, **kw)]
        if self.partial:
            contents.append(f'partial={_repr(self.partial, **kw)}')
        return contents

    def __str__(self, **kw):
        '''string representation of self.'''
        d = r'\partial' if self.partial else 'd'
        return fr'\frac{{{d}}}{{{d} {_str(self.dvar, **kw)}}}'

    # # # EQUALITY # # #
    def __eq__(self, b):
        '''returns whether self==b.'''
        try:
            return SymbolicObject.__eq__(self, b)
        except NotImplementedError:
            pass  # handled below
        if not equals(self.dvar, b.dvar):
            return False
        if not equals(self.partial, b.partial):
            return False
        return True

    @caching_attr_simple
    def __hash__(self):
        return hash((type(self), self.dvar, self.partial))


''' --------------------- DerivativeOperator --------------------- '''

_derivative_paramdocs = \
    '''dvar_or_derivative_symbol: object, probably a SymbolicObject, possibly a DerivativeSymbol
        DerivativeSymbol --> use this derivative symbol;
            and in this case, IGNORE other kwargs: partial.
        else --> taking the derivative with respect to this variable, e.g. x in d/dx.
    partial: bool, default False
        whether this is a partial derivative.
        partial derivatives treat as constant any quantities without explicit dependence on dvar.'''

@format_docstring(paramdocs=_derivative_paramdocs)
class DerivativeOperator(LinearOperator, SubbableObject):
    '''Derivative Operator. For something like d/dx.
    Not intended for direct instantiation by user; please use the derivative_operator() method instead.

    Calling this operator returns a DerivativeOperation, e.g. (d/dx)(y).
    Using self.evaluate evaluates the derivative, or returns self if unsure how to evaluate it.

    {paramdocs}
    '''
    # # # INITIALIZATION # # #
    def __init__(self, dvar_or_derivative_symbol, partial=False, **kw__None):
        '''initialize. if dvar_or_derivative_symbol is a DerivativeSymbol, ignore the other kwargs.'''
        if isinstance(dvar_or_derivative_symbol, DerivativeSymbol):
            self._derivative_symbol = dvar_or_derivative_symbol
        else:
            dvar = dvar_or_derivative_symbol
            self._derivative_symbol = DerivativeSymbol(dvar, partial=partial)
        LinearOperator.__init__(self, f=None, frep=self._derivative_symbol, circ=False)

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another instance of type(self) to be like self,
        via self._new(*args, **kw). Note these will be overwritten in _new by any **kw entered.
        '''
        kw = super()._init_properties()
        kw['partial'] = self.partial
        return kw

    # # # SIMPLE BEHAVIORS # # #
    def is_derivative_operator(self):
        '''return True, because self is a derivative operator'''
        return True

    def is_partial_derivative_operator(self):
        '''returns self.partial, which tells whether self is a partial derivative operator or not.'''
        return self.partial

    def _replace_derivative_operator(self, value):
        '''returns the result of replacing DerivativeOperator with value. i.e. just return value.'''
        return value

    # # # OPERATOR STUFF # # #
    def _f(self, g):
        '''returns DerivativeOperation(self, g).
        self._f will be called when self is called with a non-operator g.
        '''
        return DerivativeOperation(self, g)

    def treats_as_constant(self, value):
        '''returns whether self treats value as constant; None if answer unknown.
        if super().treats_as_constant(value), returns True.
        if self.partial,
            if contains_deep(value, self.dvar), return False
            otherwise, return None (i.e. "answer unknown")
        otherwise, return False (since total derivatives apply to all variables.)
        '''
        if super().treats_as_constant(value):
            return True  # self definitely treats value as constant
        if self.partial:
            dvar = self.dvar
            if contains_deep(value, dvar):
                return False  # self definitely treats value as non-constant
            else:
                return None  # answer unknown
        else:
            return False

    def evaluate(self, g):
        '''evaluates self at g.'''
        return self(g).evaluate()

    def _evaluates_simple(self, g):
        '''returns None, or special value from self(g) if the result would be simple.
        The implementation here returns None if g is an operator,
        else 0 if self.treats_as_constant(g),
        else 1 if self.dvar == g,
        else None.
        '''
        if is_operator(g):
            return None
        elif self.treats_as_constant(g):
            return ZERO
        elif equals(self.dvar, g):
            return ONE
        else:
            return None

    # # # SUBSTITUTION # # #
    def _iter_substitution_terms(self, **kw__None):
        '''returns iterator over terms to check for substitution in self.
        This just yields self._derivative_symbol.
        '''
        yield self._derivative_symbol

    def _new_after_subs(self, new_derivative_symbol):
        '''returns new object like self; for internal use after checking for substitutions in self._derivative_symbol.
        The implementation here just retuns self._new(dvar_or_derivative_symbol=new_derivative_symbol).
        '''
        return self._new(index_or_derivative_symbol=new_derivative_symbol)

    # # # EQUALITY # # #
    def __eq__(self, b):
        '''returns whether self==b.'''
        try:
            return SymbolicObject.__eq__(self, b)
        except NotImplementedError:
            return equals(self._derivative_symbol, b._derivative_symbol)

    @caching_attr_simple
    def __hash__(self):
        return hash((type(self), self._derivative_symbol))

    # # # ALIASES TO DERIVATIVE SYMBOL STUFF # # #
    dvar = property(lambda self: self._derivative_symbol.dvar, doc=_derivative_propdocs['dvar'])
    partial = property(lambda self: self._derivative_symbol.partial, doc=_derivative_propdocs['partial'])

    def with_partial(self, partial):
        '''returns copy of self with partial=partial.'''
        return self._new(partial=partial)

    def as_partial(self):
        '''returns copy of self with partial=True'''
        return self.with_partial(True)

    def as_total(self):
        '''returns copy of self with partial=False'''
        return self.with_partial(False)

    def is_vector(self):
        '''return self._derivative_symbol.is_vector()'''
        return self._derivative_symbol.is_vector()


@initializer_for(DerivativeOperator)
@format_docstring(paramdocs=_derivative_paramdocs)
def derivative_operator(dvar_or_derivative_symbol, partial=False):
    '''create a DerivativeOperator. For something like "d/dx".
    The implementation here just returns DerivativeOperator(dvar_or_derivative_symbol, partial=partial)

    {paramdocs}
    '''
    return DerivativeOperator(dvar_or_derivative_symbol, partial=partial)


''' --------------------- DerivativeOperation --------------------- '''

class DerivativeOperation(LinearOperation):
    '''Derivative Operation. For something like (d/dx)(y).
    Not intended for direct instantiation by user; please use the derivative() function instead.

    Using self.evaluate evaluates the derivative or returns self if unsure how to evaluate it.
    '''
    def __init__(self, derivative_operator, operand, **kw):
        '''raises TypeError if derivative_operator is not a DerivativeOperator instance.'''
        if not isinstance(derivative_operator, DerivativeOperator):
            raise TypeError(f'expected DerivativeOperator but got {type(derivative_operator)}')
        super().__init__(derivative_operator, operand, **kw)

    def is_derivative_operation(self):
        '''return True, because self is a derivative operation'''
        return True

    def _replace_derivative_operator(self, value):
        '''returns result of replacing DerivativeOperator with value. i.e. returns value(self.operand).'''
        return value.__call__(self.operand)

    def evaluate(self):
        '''tries to evaluate self.
        If unsure how to do it, just return self.
        '''
        return take_derivative(self.operand, self.operator)

    def _equals0(self):
        '''returns whether self==0.'''
        return self.treats_as_constant(self.operand) or _equals0(self.operand)


@initializer_for(DerivativeOperation)
def derivative_operation(derivative_operator, operand, **kw):
    '''create a DerivativeOperation object, from a derivative_operator and an operand.
    USERS: see the derivative() function instead; that function is much more user-friendly.

    implementation notes:
        - this function must put derivative_operator first, for appropriate behavior during self._new.
        - the implementation here just returns DerivativeOperation(derivative_operator, operand, **kw).
    '''
    return DerivativeOperation(derivative_operator, operand, **kw)

@format_docstring(paramdocs=_derivative_paramdocs)
def derivative(operand, dvar_or_derivative_symbol, partial=False, **kw):
    '''create a DerivativeOperation object. For something like (d/dx)(y).

    operand: object
        the object whose derivative is being taken. E.g. y from (d/dx)(y).
    {paramdocs}

    any additional kwargs are passed to INITIALIZERS.derivative_operator.
    '''
    operator = INITIALIZERS.derivative_operator(dvar_or_derivative_symbol, partial=partial, **kw)
    return INITIALIZERS.derivative_operation(operator, operand, **kw)


''' --------------------- DerivativeOperation SIMPLIFY_OPS --------------------- '''

@simplify_op(DerivativeOperation, alias='_simplify_id')
def _derivative_operation_simplify_id(self, **kw__None):
    '''converts d(constant)/dx --> 0, also dx/dx --> 1, if x is not a vector.
    This happens to be handled by the more general '_evaluate_operations' simplify op as well,
        so there is no need to run this if ALSO running _evaluate_operations.
        However, the implementation here is faster for these specific cases,
        because the implementation here only checks these cases but otherwise doesn't evaluate anything.

    implementation note: returns self.operator._evaluates_simple(self.operand) if not None, else self.
        Thus, subclasses may override this behavior.
    '''
    result = self.operator._evaluates_simple(self.operand)
    if result is None:
        return self  # return self, exactly, to help indicate nothing was changed.
    else:
        return result
