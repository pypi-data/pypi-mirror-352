"""
File Purpose: provide convenient methods for the basics subpackage.

TODO:
    - caching for get_factors_numeric_and_other
"""

from ..tools import (
    Dict,
    equals,
    dichotomize,
    is_real_negative_number,
)
from ..abstracts import (
    is_number,
    _equals0,
)
from ..attributors import attributor
from ..errors import PatternError
from ..initializers import INITIALIZERS

from ..defaults import DEFAULTS, ZERO, ONE, MINUS_ONE


''' --------------------- Get pattern-fitting values --------------------- '''

@attributor
def get_base_and_power(x):
    '''returns base, power for x.
    The idea is: if x is a Power object, returns x[0], x[1]. Else, return x, 1.
    relies on Power implementing a get_base_and_power method.
    '''
    try:
        return x.get_base_and_power()
    except AttributeError:
        return (x, ONE)

@attributor
def get_factors(x, *, split_minus=False):
    '''returns list of factors for x.
    The idea is: if x is a Product object, returns list(x). Else, return [x].
    This function is specifically for the "standard" Product,
        not any "fancy" products like DotProduct. (e.g. get_factors(u dot v) --> [u dot v].)
    relies on Product implementing a get_factors method.

    split_minus: bool, default False
        if True, splits negative real numbers x into factors (-1, |x|), unless x=-1.
    '''
    try:
        return x.get_factors(split_minus=split_minus)
    except AttributeError:
        if split_minus and is_real_negative_number(x) and not equals(x, MINUS_ONE):
            return [MINUS_ONE, -x]
        else:
            return [x]

@attributor
def get_summands(x):
    '''returns the list of summands for x.
    The idea is: if x is a Sum object, returns list(x). Else, return [x].
    relies on Sum implementing a get_summands method.
    '''
    try:
        return x.get_summands()
    except AttributeError:
        return [x]


''' --------------------- Remove factors or summands --------------------- '''

@attributor
def without_factor(x, factor, *, missing_ok=False):
    '''returns x without this factor.
    The idea is: if x is a Product object, returns x.without_term(factor).
    otherwise, return 1 if x==factor,
    otherwise return x if missing_ok else raise ValueError.
    '''
    try:
        return x.without_factor(factor, missing_ok=missing_ok)
    except AttributeError:
        pass  # handled below to avoid complicated error messages if error
    if equals(x, factor):
        return ONE
    elif missing_ok:
        return x
    else:
        raise ValueError(f'without_factor(x, factor), factor!=x. factor={factor}, x={x}.')

@attributor
def without_summand(x, summand, *, missing_ok=False):
    '''returns x without this summand.
    The idea is: if x is a Sum object, returns x.without_summand(summand).
    otherwise, return 0 if x==summand,
    otherwise return x if missing_ok else raise ValueError.
    '''
    try:
        return x.without_summand(summand, missing_ok=missing_ok)
    except AttributeError:
        pass  # handled below to avoid complicated error messages if error
    if equals(x, summand):
        return ZERO
    elif missing_ok:
        return x
    else:
        raise ValueError(f'without_summand(x, summand), summand!=x. summand={summand}, x={x}.')


''' --------------------- Dichotomize by factors --------------------- '''

def get_factors_numeric_and_other(x):
    '''returns (numeric factors, non-numeric factors) of x.'''
    return dichotomize(get_factors(x), is_number)


''' --------------------- Count minus signs --------------------- '''

@attributor
def count_minus_signs_in_factors(x):
    '''returns number of factors of x which contain a minus sign.
    returns x.count_minus_signs_in_factors() if possible,
    else (1 if (x < 0) else 0) if evaluating (x < 0) is possible,
    else 0.
    '''
    try:
        x_count_minus_signs_in_factors = x.count_minus_signs_in_factors
    except AttributeError:
        pass  # handled after the else block
    else:
        return x_count_minus_signs_in_factors()
    try:
        x_negative = bool(x < ZERO)
    except (TypeError, ValueError):
        return 0  # 0 instead of ZERO since it is a count, rather than part of a math expression.
    else:
        return 1 if x_negative else 0

@attributor
def has_minus_sign(x):
    '''returns whether x has a leading minus sign when written as a string.
    returns x.has_minus_sign() if possible,
    else x < 0, if possible,
    else False.
    '''
    try:
        x_has_minus_sign = x.has_minus_sign
    except AttributeError:
        pass  # handled after the else block
    else:
        return x_has_minus_sign()
    try:
        return bool(x < ZERO)
    except (TypeError, ValueError):
        return False

@attributor
def seems_negative(x):
    '''returns whether x "seems like" a negative number, especially if in the exponent. Checks:
    returns x.seems_negative() if possible,
    else x < 0, if possible,
    else False.
    '''
    try:
        x_seems_negative = x.seems_negative
    except AttributeError:
        pass  # handled after the else block
    else:
        return x_seems_negative()
    try:
        return bool(x < ZERO)
    except (TypeError, ValueError):
        return False

def seems_positive(x):
    '''returns whether x "seems like" a positive number, especially if in the exponent.
    Equivalent to not seems_negative(x).
    '''
    return not seems_negative(x)

def exponent_seems_positive(x):
    '''returns whether x seems to have a positive exponent.'''
    base, power = get_base_and_power(x)
    if power is ONE:  # occurs often, especially whenever factor is not a Power instance.
        return True
    else:
        return seems_positive(power)

def exponent_seems_negative(x):
    '''returns whether x seems to have a negative exponent.'''
    base, power = get_base_and_power(x)
    if power is ONE:  # occurs often, especially whenever factor is not a Power instance.
        return False
    else:
        return seems_negative(power)


''' --------------------- Negation --------------------- '''

@attributor
def _is_surely_negation(x, y):
    '''True result is sufficient to indicate y == -x, but not necessary.
    The idea is: objects may implement some addition checks for negation,
    but they shouldn't need to re-implement the basic "x negates product(-1, x)" rule.
    E.g. CrossProduct._is_surely_negation(u, v) returns True when u=AxB, v=BxA.

    This function returns y._is_surely_negation(x) if possible, else False
    '''
    try:
        return y._is_surely_negation(x)
    except AttributeError:
        return False

@attributor
def is_negation(x, y):
    '''returns whether y == -x'''
    try:
        return y.is_negation(x)
    except AttributeError:
        pass
    try:
        return y._is_surely_negation(x)
    except AttributeError:
        pass
    xinfo = (get_factors_numeric_and_other(x), x)
    yinfo = (get_factors_numeric_and_other(y), y)
    return _is_negation__from_info(xinfo, yinfo)

def _is_negation__from_info(xinfo, yinfo):
    '''helper method for is_negation; returns result given info about x and y.
    info should be (get_factors_numeric_and_other(x), x) and similar for y.

    Provided for re-usability during sums._sum_simplify_x_minus_x.
    '''
    (xnum, xf), x = xinfo
    (ynum, yf), y = yinfo
    x_is_number = len(xf)==0
    y_is_number = len(yf)==0
    if x_is_number != y_is_number:  # x number, y not. OR y number, x not.
        return False
    if len(xnum)==0==len(ynum):
        return False # symbolic objects without numeric factors cannot be pairwise negations (need factor of -1).
    xnum_val = multiply(*xnum)
    ynum_val = multiply(*ynum)
    if equals(ynum_val, -1 * xnum_val):
        if x_is_number: # and y_is_number; implied since x_is_number != y_is_number was handled above.
            return True # << nums are opposite, and x and y are purely numeric.
        else: # x and y are both not purely numeric.
            xf_val = x._new(*xf) if len(xnum)>0 else x
            yf_val = y._new(*yf) if len(ynum)>0 else y
            if equals(yf_val, xf_val):
                return True
    return False


''' --------------------- Reciprocal --------------------- '''

def is_reciprocal(x, y):
    '''returns whether y = 1/x'''
    xbase, xpower = get_base_and_power(x)
    ybase, ypower = get_base_and_power(y)
    if equals(ypower, -1 * xpower) and equals(xbase, ybase):
        return True
    return False

@attributor
def get_reciprocal(x):
    '''returns reciprocal of x.
    (For internal usage, for efficiency. Users should instead do x**-1.
    Note, may need to simplify then, e.g. via (x**-1).simplified().)
    The idea is: if x is a Power object, returns copy of x but with exponent negated.
    And if x is a Product object, returns copy of x but with all exponents negated.
    '''
    try:
        return x.get_reciprocal()
    except AttributeError:
        return x**-1


''' --------------------- Common Base Among Terms --------------------- '''

def get_common_bases(*terms, allow_minus_1=True, split_minus=False):
    '''returns dict of common bases among the terms provided.
    result[base] = exponents, such that terms[i] has base ** exponents[i].
    Note: result is a tools.Dict, which behaves like a dict but doesn't require hashable keys.

    each term is regarded as a product of (possibly 1) factors,
        each factor regarded as base^exp (possibly with exp==1).

    allow_minus_1: bool, default True
        If False, remove -1 from result if it appears as a "common base".
    split_minus: bool, default False
        if True, split real negative numbers x into factors -1, |x|

    For example (note that results are tools.Dict objects, NOT dict objects):
        get_common_bases(x * 7, 7 * y) --> {7: [1, 1]}
        get_common_bases(x * y, 7 * z) --> {}
        get_common_bases(x * x**3 * y, 7 * x**-1) --> {x: [4, -1]}
        get_common_bases(x * y**2, 7 * y**-3 * z) --> {y: [2, -3]}
        get_common_bases(x * y**2, 7 * y**-3 * x) --> {x: [1, 1], y: [2, -3]}
        get_common_bases(x**2 * y**2, 7 * y**-3 * x**-3) --> {x: [2, -3], y: [2, -3]}
        get_common_bases( (x*y)**2, 7 * (y*x)**-3) --> {x*y: [2, -3]}
    '''
    # handle "no terms" case
    if len(terms) == 0:
        return Dict()
    # set up result with bases from first term
    result = Dict(default=[0])
    iter_terms = iter(terms)
    term0 = next(iter_terms)
    for factor in get_factors(term0, split_minus=split_minus):
        base, power = get_base_and_power(factor)
        if allow_minus_1 or not equals(base, MINUS_ONE):
            result[base] = [result[base][0] + power]
    # consider terms[1:]. Common bases must appear in all terms; remove any bases not in term.
    for term in iter_terms:
        term_result_i = dict()  # {i in result: power from term}
        # we need to consider all factors from this term & check against result.
        bases_and_powers = [get_base_and_power(factor) for factor in get_factors(term, split_minus=split_minus)]
        for base, power in bases_and_powers:
            j = result.find(base)
            if j is not None:
                try:
                    term_result_i[j] = term_result_i[j] + power
                except KeyError:
                    term_result_i[j] = power
        # put relevant factors from this term into result; remove any bases in result which are not in this term.
        for i in range(len(result))[::-1]:  # [::-1] --> largest first; so del_i doesn't mess up the ordering.
            try:
                power = term_result_i[i]
            except KeyError:
                result.del_i(i)
            else:
                if _equals0(power):
                    result.del_i(i)
                else:
                    result.get_i(i).append(power)
        # [EFF] if result is empty, no need to loop through other terms; no common bases found.
        if len(result) == 0:
            return result
    return result

def _adjusted_factor_powers(factors, base_power_tuples, *, mode='add', missing_ok=True):
        '''for (base, power) in base_power_tuples, add (or subtract) power to factor with this base.
        if base not in factors, put a new factor like (base ^ power).
    
        mode: 'add' or 'subtract'
            'add' --> add input power to existing power
            'subtract' --> subtract input power from existing power
        missing_ok: bool, default True
            whether it is okay for base to not be found in bases of factors.
            False --> raise PatternError if base not found in bases of factors.

        returns list of tuples (factor_or_tuple, True if it is a base_power_tuple else False)
            E.g. factors=[x^3, z^7], base_power_tuples=[(x, 2), (y, -1)]
                --> [((x,5), True), (z^7, False), ((y, -1), True)]
            Only converts factor to (base, power) for result if power was changed.

        The output is so "annoying" because basics_tools doesn't actually know about Sum / Product / Power.
        You can convert the output to a list of factors as follows:
            [power(f[0], f[1]) if ftup else f for (f, ftup) in result]
        '''
        factors_orig = factors  # << helps if debugging
        if mode not in ('add', 'subtract'):
            raise InputError(f'Invalid mode. Expected "add" or "subtract" but got {repr(mode)}')
        result = {i: (factor, False) for i, factor in enumerate(factors_orig)}
        inew = len(factors_orig)  # << i to use if we need to put a new factor at the end.
        base_and_powers = {i: get_base_and_power(factor) for i, factor in enumerate(factors_orig)}
        for (base, power) in base_power_tuples:
            try:
                i, ibase, ipower = next((i, ibase, ipower) for (i, (ibase, ipower))
                                        in base_and_powers.items() if equals(ibase, base))
            except StopIteration:
                if missing_ok:
                    result[inew] = ((base, power if mode=='add' else -power), True)  # True <--> "adjusted this one".
                    inew += 1
                    break  # fully handled this one; move on to the next (base, power).
                else:
                    raise PatternError(f'base not found: {base}') from None
            new_power = (ipower + power) if mode=='add' else (ipower - power)
            if _equals0(new_power):
                del result[i]
            elif new_power is ONE:
                result[i] = (ibase, False)
            else:
                result[i] = ((ibase, new_power), True)
            # [EFF] bookkeeping 
            del base_and_powers[i]  # << don't need to check this one anymore since we matched it already.
        result = list(result.values())
        return result


''' --------------------- Misc. Convenience Functions --------------------- '''

def multiply(*args):
    '''returns result of multiplying all the inputs together. (if no inputs, return 1.)'''
    return ONE if len(args)==0 else _multiply_some_args(*args)

def _multiply_some_args(t0, *args):
    '''returns result of multiplying all the inputs together, assuming there is at least one input.'''
    result = t0
    for arg in args:
        result = result * arg
    return result

def add(*args):
    '''returns result of adding all the inputs together. (if no inputs, return 0.)'''
    return ZERO if len(args)==0 else _add_some_args(*args)

def _add_some_args(t0, *args):
    '''returns result of adding all the inputs together, assuming there is at least one input.'''
    result = t0
    for arg in args:
        result = result + arg
    return result

def gcf(x, y):
    '''returns (the gcf between x and y, x/gcf, y/gcf).
    Prefers to use x.gcf() if it exists; otherwise tries y.gcf().
    If x and y both do not have 'gcf' attribute,
        if x == y, return (x, 1, 1),
        otherwise, return (1, x, y).
    '''
    if hasattr(x, 'gcf'):
        f, x_over_f, y_over_f = x.gcf(y)
    elif hasattr(y, 'gcf'):
        f, y_over_f, x_over_f = y.gcf(x)
    elif equals(x, y):
        f, x_over_f, y_over_f = (x, ONE, ONE)
    else:
        f, x_over_f, y_over_f = (ONE, x, y)
    return (f, x_over_f, y_over_f)

def _least_common_power(exp1, exp2):
    '''returns (lcp exp1 and exp2, exp1 - lcp, exp2 - lcp)
    useful if they appear in terms like x**exp1, x**exp2.
    if order can be determined (e.g. exp1 and exp2 both numbers),
        use lcp = exp1 if exp1 < exp2, else exp2.
    otherwise, use lcp = exp1.
    Examples:
        (5, 9) --> (5, 0, 4)
        (3, 1) --> (1, 2, 0)
        (-7, 2) --> (-7, 0, 9)
        (n, m) --> (n, 0, m - n)  # n and m not numbers, can't 
    '''
    try:
        lesser1 = (exp1 < exp2)
    except TypeError:
        lesser1 = True
    if lesser1:
        return (exp1, ZERO, exp2 - exp1)
    else:
        return (exp2, exp1 - exp2, ZERO)

def lcm_simple(x, y):
    '''returns (the lcm between x & y, lcm/x, lcm/y). lcm = "least common multiple".
    
    E.g. lcm(abc, acde) --> (ac, b, de)
    only checks for equal factors (or bases, if exponents are involved.)
    '''
    factors_x = {i: fx for i, fx in enumerate(get_factors(x))}  # for bookkeeping, remember original factors;
    factors_y = {j: fy for j, fy in enumerate(get_factors(y))}  # i: val, val==True if factor i altered by loop.
    bases_and_powers_x = {i: get_base_and_power(fx) for i, fx in factors_x.items()}
    bases_and_powers_y = {j: get_base_and_power(fy) for j, fy in factors_y.items()}
    bp_common = Dict(default=ZERO)  # {base: power}
    for i, (basex, powerx) in tuple(bases_and_powers_x.items()):  # tuple() in case of change during loop.
        for j, (basey, powery) in tuple(bases_and_powers_y.items()):
            if equals(basex, basey):
                lcp, pxnew, pynew = _least_common_power(powerx, powery)
                bp_common[basex] = bp_common[basex] + lcp
                if pynew is ZERO:  # y is fully accounted for, within bp_common
                    del bases_and_powers_y[j]
                    del factors_y[j]
                else:  # some part of fy remains..
                    bases_and_powers_y[j] = [basey, pynew]
                    factors_y[j] = True  # j'th factor altered by loop
                    powery = pynew
                if pxnew is ZERO:  # x is fully accounted for, within bp_common
                    del bases_and_powers_x[i]
                    del factors_x[i]
                    break
                else:  # some part of fx remains.. (so, keep looking in other y factors)
                    bases_and_powers_x[i] = [basex, pxnew]
                    factors_x[i] = True  # i'th factor altered by loop
                    powerx = pxnew
    def powered(b, p):
        return b if p is ONE else INITIALIZERS.power(b, p)
    gcf_factors = [powered(b, p) for b, p in bp_common.items() if p is not ZERO]
    x_over_gcf_factors = [powered(*bases_and_powers_x[i]) if fx is True else fx
                            for i, fx in factors_x.items()]   # factors of x / gcf
    y_over_gcf_factors = [powered(*bases_and_powers_y[i]) if fy is True else fy
                            for i, fy in factors_y.items()]   # factors of y / gcf
    lcm = INITIALIZERS.product(*gcf_factors, *x_over_gcf_factors, *y_over_gcf_factors)
    lcm_over_x = INITIALIZERS.product(*y_over_gcf_factors)
    lcm_over_y = INITIALIZERS.product(*x_over_gcf_factors)
    return (lcm, lcm_over_x, lcm_over_y)

def copy_if_possible(obj):
    '''returns obj.copy() if that method is available, else obj.'''
    try:
        return obj.copy()
    except AttributeError:
        return obj
