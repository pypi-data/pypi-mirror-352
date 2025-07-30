"""
File Purpose: provide convenient methods for the derivatives subpackage.
"""
from ...attributors import attributor
from ...initializers import INITIALIZERS


''' --------------------- "instance checks" --------------------- '''

@attributor
def is_derivative_operator(obj):
    '''returns whether obj is a derivative operator,
    via obj.is_derivative_operator() if available, else False.
    '''
    try:
        obj_is_derivative_operator = obj.is_derivative_operator
    except AttributeError:
        return False
    else:
        return obj_is_derivative_operator()

@attributor
def is_derivative_operation(obj):
    '''returns whether obj is a derivative operation,
    via obj.is_derivative_operation() if available,
    else is_derivative_operator(obj.operator) is obj.operator exists,
    else False.
    '''
    try:
        obj_is_derivative_operation = obj.is_derivative_operation
    except AttributeError:
        try:
            operator = obj.operator
        except AttributeError:
            return False
        else:
            return is_derivative_operator(operator)
    else:
        return obj_is_derivative_operation

@attributor
def is_partial_derivative_operator(obj):
    '''returns whether obj is a derivative operator for a partial derivative,
    via obj.is_partial_derivative_operator() if available, else False.
    '''
    try:
        obj_is_partial_derivative_operator = obj.is_partial_derivative_operator
    except AttributeError:
        return False
    else:
        return obj_is_partial_derivative_operator()


''' --------------------- derivative-like behavior --------------------- '''

def _get_dvar(obj):
    '''returns variable with respect to which the derivative is being taken.
    returns obj.dvar if it exists, else obj._get_dvar() if possible, else raise AttributeError.
    '''
    try:
        return obj.dvar
    except AttributeError:
        pass  # handled below
    try:
        obj_get_dvar = obj._get_dvar
    except AttributeError:
        errmsg = f"obj of type ({type(obj).__name__}) has no attribute 'dvar' or method '_get_dvar'."
        raise AttributeError(errmsg) from None
    else:
        return obj_get_dvar()

def _replace_derivative_operator(obj, value):
    '''returns result of replacing the derivative_operator in obj with the value provided.
    returns obj._replace_derivative_operator(value) if possible, else raise AttributeError.
    Note: for DerivativeOperator objects, this should just return value.
    '''
    return obj._replace_derivative_operator(value)


''' --------------------- take derivative --------------------- '''

@attributor
def take_derivative(y, dvar_or_derivative_operator, partial=False, **kw):
    '''takes derivative: d(y)/d(dvar).

    returns y.take_derivative(dvar, partial, **kw), else
        operator = INITIALIZERS.derivative_operator(dvar, partial, **kw);
        returns operator._evaluates_simple(y) if not None,
        else operator(y)

    note: for advanced or internal usage, may enter a DerivativeOperator for dvar instead.
    In that case, use operator = dvar instead, and returns operator(y).
    '''
    try:
        self_take_derivative = y.take_derivative
    except AttributeError:
        pass  # handled below
    else:
        return self_take_derivative(dvar_or_derivative_operator, partial=partial, **kw)
    operator = _operator_from_dvar_or_operator(dvar_or_derivative_operator, partial=partial, **kw)
    simple_result = operator._evaluates_simple(y)
    if simple_result is None:
        return operator(y)
    else:
        return simple_result

def _operator_from_dvar_or_operator(dvar_or_derivative_operator, **kw):
    '''returns a derivative operator, given dvar or a derivative operator.
    if the input is already a derivative operator, return it; otherwise make one.
    '''
    if is_derivative_operator(dvar_or_derivative_operator):
        return dvar_or_derivative_operator
    else:
        dvar = dvar_or_derivative_operator
        return INITIALIZERS.derivative_operator(dvar, **kw)