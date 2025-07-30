"""
File Purpose: vector derivatives.

This is the nabla operator for the case when dvar is the position vector.

[TODO](maybe)[REF] instead, put these behaviors into DerivativeOperator and just use is_vector...

[TODO] strings.. e.g. protect u in d/du, if necessary. Also put operator at end of string for Product.
"""

from .derivative import (
    DerivativeSymbol, DerivativeOperator, DerivativeOperation,
)
from .derivatives_tools import (
    is_derivative_operator,
)
from ...abstracts import (
    simplify_op, simplify_op_skip_for,
)
from ...errors import VectorialityError, MetricUndefinedError, warn
from ...initializers import INITIALIZERS, initializer_for
from ...precalc_operators import (
    LinearOperator,
    OperationBinaryVectorProduct,
)
from ...vectors import (
    is_vector,
    _default_basis_if_None,
)
from ...tools import (
    _str, _repr,
    equals,
    Binding,
)
from ...defaults import DEFAULTS, ZERO, ONE

binding = Binding(locals())


''' --------------------- VectorDerivativeSymbol --------------------- '''

class VectorDerivativeSymbol(DerivativeSymbol):
    r'''vector derivative symbol, for something like d/dx with x a vector.

    Contains no rules for evaluating / calling on an object to create a derivative;
    not intended for direct use. See DerivativeOperator or DerivativeOperation instead.

    dvar: object, probably a SymbolicObject.
        taking the derivative with respect to this variable.
        must be a vector.
    partial: bool, default False
        whether this is a partial derivative.
    _nabla: False, True, or any other object
        whether to represent as '\nabla', if partial=True. (ignore if partial=False)
        False --> use \partial / \partial dvar
        True  --> use \nabla
        object --> use as a subscript, i.e.: \nabla_{str(the object)}
        Note: _nabla is for aesthetic purposes only. E.g., not considered during self.__eq__().
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, dvar, partial=False, _nabla=False):
        '''initialize self to be d/d(dvar).'''
        if not is_vector(dvar):
            raise VectorialityError('dvar must be a vector')
        super().__init__(dvar, partial=partial)
        self._nabla = _nabla

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another instance of type(self) to be like self,
        via self._new(*args, **kw). Note these will be overwritten in _new by any **kw entered.
        '''
        kw = super()._init_properties()
        kw['_nabla'] = self._nabla
        return kw

    def _with_nabla(self, _nabla):
        '''returns copy of self with _nabla=_nabla'''
        return self._new(_nabla=_nabla)

    # # # DISPLAY # # #
    def _repr_contents(self, **kw):
        '''returns contents to put inside 'VectorDerivativeSymbol()' in repr for self.'''
        contents = super()._repr_contents(**kw)
        if self._nabla is not False:
            contents.append(f'_nabla={_repr(self._nabla, **kw)}')
        return contents

    def __str__(self, **kw):
        '''string representation of self.'''
        if (self.partial) and (self._nabla is not False):
            if self._nabla is True:
                return r'\nabla'
            else:
                return fr'\nabla_{{{_str(self._nabla, **kw)}}}'
        else:
            return super().__str__(**kw)

    # # # INSPECTION # # #
    def is_vector(self):
        '''return True, because self is a vector.'''
        return True


''' --------------------- VectorDerivativeOperator --------------------- '''

class VectorDerivativeOperator(DerivativeOperator):
    r'''Derivative Operator. For something like d/dx, with x a vector.

    Calling this operator returns a DerivativeOperation, e.g. (d/dx)(y).
    Using self.evaluate evaluates the derivative, or returns self if unsure how to evaluate it.

    dvar_or_derivative_symbol: object, possibly a VectorDerivativeSymbol
        must be a vector (i.e. is_vector(obj) == True).
        VectorDerivativeSymbol --> use this derivative symbol;
            and in this case, IGNORE other inputs: partial.
        else --> taking the derivative with respect to this variable, e.g. x in d/dx.
    partial: bool, default False
        whether this is a partial derivative.
        partial derivatives treat as constant any quantities without explicit dependence on dvar.
    _nabla: False, True, or any other object
        whether to represent as '\nabla', if partial=True. (ignore if partial=False)
        False --> use \partial / \partial dvar
        True  --> use \nabla
        object --> use as a subscript, i.e.: \nabla_{str(the object)}
        Note: _nabla is for aesthetic purposes only. E.g., not considered during self.__eq__().
    '''
    def __init__(self, dvar_or_derivative_symbol, partial=False, _nabla=False):
        '''initialize. ensure dvar_or_derivative_symbol is a vector.'''
        if not is_vector(dvar_or_derivative_symbol):
            raise VectorialityError('dvar_or_derivative_symbol must be a vector')
        if isinstance(dvar_or_derivative_symbol, VectorDerivativeSymbol):
            self._derivative_symbol = dvar_or_derivative_symbol
        else:
            dvar = dvar_or_derivative_symbol
            self._derivative_symbol = VectorDerivativeSymbol(dvar, partial=partial, _nabla=_nabla)
        LinearOperator.__init__(self, f=None, frep=self._derivative_symbol, circ=False)
        
    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another instance of type(self) to be like self,
        via self._new(*args, **kw). Note these will be overwritten in _new by any **kw entered.
        '''
        kw = super()._init_properties()
        kw['partial'] = self.partial
        kw['_nabla'] = self._nabla
        return kw

    # # # OPERATOR STUFF # # #
    def _f(self, g):
        '''returns VectorDerivateOperation(self, g).
        self._f will be called when self is called with a non-operator g.
        '''
        return VectorDerivativeOperation(self, g)

    # # # ALIASES TO VECTOR DERIVATIVE SYMBOL STUFF # # #
    _nabla = property(lambda self: self._derivative_symbol._nabla,
            doc='''self._derivative_symbol._nabla. See help(VectorDerivativeSymbol) for docs.''')

    def _with_nabla(self, _nabla):
        '''returns copy of self with _nabla=_nabla'''
        return self._new(_nabla=_nabla)

    def is_vector(self):
        '''return True, because self is a vector.'''
        return True

    # # # COMPONENTS # # #
    def _component(self, x, _metric_x=ONE, shorthand=None, **kw):
        '''return the x component of self, i.e. _metric_x * d/d(u dot x) .
        intended for internal use / debugging.
        SymSolver users should use self.componentize() instead.

        x: vector SymbolicObject which is a member of an OrthonormalBasis.
            getting this component of self.
            this routine assumes but does not check that x is the appropriate type.
        _metric_x: value
            i'th component of the metric in the relevant basis where basis[i]==x.
        additional kwargs go to self.dvar.component().

        [TODO] using self._new instead of derivative_operator() to create the result...
            (but should create a non-vector derivative... but want subclass properties to be kept...)
        '''
        new_dvar = self.dvar.component(x, shorthand=shorthand, **kw)
        result = INITIALIZERS.derivative_operator(new_dvar, partial=self.partial, _nabla=self._nabla)
        if _metric_x is ONE:
            return result
        else:
            return _metric_x * result

    def _is_directly_componentizeable(self):
        '''returns True, because self is directly componentizeable.'''
        return True

    def componentize(self, basis=None, shorthand=None, if_missing_metric=None, **kw):
        r'''componentizes self in basis.
        Rewrites self into a sum of components (times the appropriate unit vectors)
            e.g. componentize(d/du, (xhat, yhat)) --> xhat d/du_x + yhat d/du_y,
            if 'd' is '\partial' and u is a vector.

        Not-Yet-Implemented Cases:
            - componentize for "total" derivatives, e.g. d/du when 'd' is not '\partial'.
                - in this case, just return self without componentizing.
            - componentize for curvilinear coordinates, i.e. when basis.metric != (1, 1, ..., 1)

        basis: None or iterable with elements members of an OrthonormalBasis. default None
            None --> use DEFAULTS.COMPONENTS_BASIS
            Note: must have non-None metric, else will return self or crash (see if_missing_metric).
            [TODO] allow for metrics other than all 1's (like (1,1,1)).
        shorthand: None or bool, default None
            whether to convert to shorthand notation when possible (e.g. k dot xhat --> k_x)
            None --> use DEFAULTS.COMPONENTS_SHORTHAND
        if_missing_metric: None, 'crash', 'warn', or 'ignore'
            how to behave if basis.metric is None.
            None --> use DEFAULTS.COMPONENTS_IF_MISSING_METRIC
            'crash' --> crash; raise MetricUndefinedError
            'warn' --> make warning message with repr of the crash that would have occurred if 'crash'.
                        then, return self, without componentizing.
            'ignore --> return self, without componentizing.
        additional kw go to self._component()
        '''
        if not self.partial:
            warn(f'Componentize for non-partial derivative (type={type(self)}) not implemented.')
            return self
        basis = _default_basis_if_None(basis)
        metric = getattr(basis, 'metric', None)
        if metric is None:
            # get value of if_missing_metric
            if if_missing_metric is None:
                if_missing_metric = DEFAULTS.COMPONENTS_IF_MISSING_METRIC
            # use value of if_missing_metric
            if if_missing_metric == 'ignore':
                return self  # return self, exactly, to help indicate nothing was changed.
            # else..
            errmsg = (f"{type(self).__name__}.componentize(basis) requires non-None basis.metric! "
                      "\nProvide a different basis, or use componentize(..., if_missing_metric='ignore') "
                      "to just skip this operation when basis.metric = None.")
            if if_missing_metric == 'crash':
                raise MetricUndefinedError(errmsg)
            elif if_missing_metric == 'ignore':
                warn(repr(MetricUndefinedError(errmsg)))
                return self  # return self, exactly, to help indicate nothing was changed.
            else:
                raise NotImplementedError(f'unrecognized value for if_missing_metric kwarg: {repr(if_missing_metric)}')
        # only implemented for cartesian coordinates:
        if all(equals(m, 1) for m in metric):
            components = tuple(self._component(vhat, shorthand=shorthand, **kw) for vhat in basis)
            return self.sum(*(vhat * component for component, vhat in zip(components, basis)))
        else:
            # [TODO] implement for any curvilinear coordinates (with a provided metric)
            raise NotImplementedError(f'{type(self).__name__}.componentize with non-cartesian basis.metric.')


@initializer_for(DerivativeOperator)
def derivative_operator(dvar_or_derivative_symbol, partial=False, _nabla=False):
    '''create a DerivativeOperator. For something like "d/dx".
    if input is a vector result will be a VectorDerivativeOperator.
    '''
    if is_vector(dvar_or_derivative_symbol):
        return VectorDerivativeOperator(dvar_or_derivative_symbol, partial=partial, _nabla=_nabla)
    else:
        return DerivativeOperator(dvar_or_derivative_symbol, partial=partial)


''' --------------------- VectorDerivativeOperation --------------------- '''

class VectorDerivativeOperation(DerivativeOperation):
    '''Vector Derivative Operation. For something like (d/dx)(y) with x a vector.
    (y possibly a vector, possibly not. Behavior defined here doesn't assume either way.)
    Not intended for direct instantiation by user; please use the [TODO -- WHICH FUNC?] function instead.

    Note: for position vector x, (d/dx)(y) = gradient(y)

    Using self.evaluate evaluates the derivative or returns self if unsure how to evaluate it.
    '''
    def __init__(self, vector_derivative_operator, operand, **kw):
        '''raises TypeError if vector_derivative_operator is not a VectorDerivativeOperator instance.'''
        if not isinstance(vector_derivative_operator, VectorDerivativeOperator):
            raise TypeError(f'expected VectorDerivativeOperator but got {type(vector_derivative_operator)}')
        super().__init__(vector_derivative_operator, operand, **kw)

    def evaluate(self):
        '''tries to evaluate self.
        The implementation here just returns 0 (if self treats operand as constant) or self.
        '''
        if self.treats_as_constant(self.operand):
            return ZERO
        else:
            return self


@initializer_for(DerivativeOperation)
def derivative_operation(derivative_operator, operand, **kw):
    '''create a DerivativeOperation object, from a derivative_operator and an operand.
    USERS: see the derivative() function instead; that function is much more user-friendly.

    implementation notes:
        - this function must put derivative_operator first, for appropriate behavior during self._new.
        - the implementation here just returns cls(derivative_operator, operand, **kw),
            where cls is VectorDerivativeOperation if is_vector(derivative_operator) else DerivativeOperation.
    '''
    if is_vector(derivative_operator):
        return VectorDerivativeOperation(derivative_operator, operand, **kw)
    else:
        return DerivativeOperation(derivative_operator, operand, **kw)


''' --------------------- VectorDerivativeOperation SIMPLIFY_OPS --------------------- '''

simplify_op_skip_for(VectorDerivativeOperation, '_derivative_operation_simplify_id')
@simplify_op(VectorDerivativeOperation, alias='_simplify_id')
def _vector_derivative_operation_simplify_id(self, **kw__None):
    '''converts d(constant)/dx --> 0. Does NOT convert dx/dx --> 1 (since this maybe isn't true for vectors?)
    This happens to be handled by the more general '_evaluate_operations' simplify op as well,
        so there is no need to run this if ALSO running _evaluate_operations.
        However, the implementation here is faster for these specific cases,
        because the implementation here only checks these cases but otherwise doesn't evaluate anything.
    '''
    if self.treats_as_constant(self.operand):
        return ZERO
    else:
        return self  # return self, exactly, to help indicate nothing was changed.


''' --------------------- IS_DERIVATIVE_OPERATION for OperationBinaryVectorProduct --------------------- '''

with binding.to(OperationBinaryVectorProduct):
    @binding
    def is_derivative_operation(self):
        '''returns whether self represents a derivative operation,
        i.e. whether self[0] is a derivative operator.
        '''
        return is_derivative_operator(self.t1)
