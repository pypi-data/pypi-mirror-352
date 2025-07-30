"""
File Purpose: tools related to comparing objects
E.g. >, <, max, min, similarity.
see also: equality.py, for testing equality.
"""

from .numbers import is_number, is_real_number
from ..errors import PatternError

''' --------------------- "type-forgiving" Min & Max --------------------- '''

def skiperror_min(arg0, *args, return_index=False):
    '''return min of args, skipping any TypeError or ValueError during loop.
    if two or more inputs, iterate through all inputs.
    if one input, iterate through it, and it must be iterable.
        inputting (arg0, arg1, arg2) equivalent to inputting ([arg0, arg1, arg2],)
    if return_index, also return index of min arg.
    '''
    iterable = arg0 if len(args)==0 else (arg0, *args)
    itering = iter(iterable)
    result = next(itering)
    iresult = 0
    for i, arg in enumerate(itering):
        try:
            arg_is_less = bool(arg < result)
        except (TypeError, ValueError):
            pass  # skip this arg; comparison fails.
        else:
            if arg_is_less:
                result = arg
                iresult = i + 1  # i starts at 0 but arg 1
    return (result, iresult) if return_index else result

def skiperror_max(arg0, *args, return_index=False):
    '''return max of args, skipping any TypeError or ValueError during loop.
    if two or more inputs, iterate through all inputs.
    if one input, iterate through it, and it must be iterable.
        inputting (arg0, arg1, arg2) equivalent to inputting ([arg0, arg1, arg2],)
    if return_index, also return index of min arg.
    '''
    iterable = arg0 if len(args)==0 else (arg0, *args)
    itering = iter(iterable)
    result = next(itering)
    iresult = 0
    for i, arg in enumerate(itering):
        try:
            arg_is_more = bool(arg > result)
        except (TypeError, ValueError):
            pass  # skip this arg; comparison fails.
        else:
            if arg_is_more:
                result = arg
                iresult = i + 1  # i starts at 0 but arg 1
    return (result, iresult) if return_index else result

def min_number(arg0, *args, skiperror=True, real_only=True, allow_default=False, return_index=False):
    '''return minimum arg which is_number. if only provided arg0, iterate over it.
    skiperror: bool, default True
        whether to skip TypeError and ValueError during comparison of numbers.
    real_only: bool, default True
        whether to only consider arg if is_real_number(arg).
        use is_real_number(arg) if real_only, else is_number(arg).
    allow_default: bool or object, default False
        controls behavior if there are no valid numbers in args:
            False --> crash with PatternError
            True --> return first arg.
            any other object --> return allow_default.
    return_index: bool, default False
        if True, return (min_number, index_of_min_number in args)
        currently incompatible with skiperror
    '''
    iterable = arg0 if len(args)==0 else (arg0, *args)
    list_ = list(iterable)
    numeric = is_real_number if real_only else is_number
    numbers = tuple(arg for arg in list_ if numeric(arg))
    if len(numbers) == 0:
        if allow_default is False:
            raise PatternError('no valid numbers in args')
        elif allow_default is True:
            return list_[0]
        else:
            return allow_default
    if skiperror:
        return skiperror_min(numbers, return_index=return_index)
    else:
        if return_index:
            raise NotImplementedError('[TODO] skiperror=True and return_index=True.')
        return min(numbers)

def max_number(arg0, *args, skiperror=True, real_only=True, allow_default=False, return_index=False):
    '''return maximum arg which is_number. if only provided arg0, iterate over it.
    skiperror: bool, default True
        whether to skip TypeError and ValueError during comparison of numbers.
    real_only: bool, default True
        whether to only consider arg if is_real_number(arg).
        use is_real_number(arg) if real_only, else is_number(arg).
    allow_default: bool or object, default False
        controls behavior if there are no valid numbers in args:
            False --> crash with PatternError
            True --> return first arg.
            any other object --> return allow_default.
    return_index: bool, default False
        if True, return (max_number, index_of_max_number in args)
        currently incompatible with skiperror
    '''
    iterable = arg0 if len(args)==0 else (arg0, *args)
    list_ = list(iterable)
    numeric = is_real_number if real_only else is_number
    numbers = tuple(arg for arg in list_ if numeric(arg))
    if len(numbers) == 0:
        if allow_default is False:
            raise PatternError('no valid numbers in args')
        elif allow_default is True:
            return list_[0]
        else:
            return allow_default
    if skiperror:
        return skiperror_max(numbers, return_index=return_index)
    else:
        if return_index:
            raise NotImplementedError('[TODO] skiperror=True and return_index=True.')
        return max(numbers)


''' --------------------- Similarities --------------------- '''

def similarity(x, y):
    '''returns some measure of the similarity of x and y, from 0 (different) to 1 (the same).
    x and y should be hashable iterables.
    [EFF] Might be slow for large x and y.
    '''
    return difflib.SequenceMatcher(None, x, y).ratio()

def very_similar(x, y):
    '''returns whether x and y qualify as "very similar" (similarity > 0.9)'''
    return similarity(x, y) > 0.9

def maybe_similar(x, y):
    '''returns whether x and y qualify as "maybe similar" (similarity > 0.7)'''
    return similarity(x, y) > 0.7

def not_similar(x, y):
    '''returns whether x and y qualify as "not similar" (similarity < 0.5)'''
    return similarity(x, y) < 0.5