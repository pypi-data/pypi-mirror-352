r"""
File Purpose: string representations of basic objects.

Creating "reasonable" strings is a surprisingly difficult task, with many components:
    PARENTHESES / ENCLOSURE:
        Only put parentheses where necessary, instead of around every non-Symbol SymbolicObject:
        Example: Sum(Product(9, -2, z), 5, Power(Power(u, -1), 3), Power(Product(6, x, Sum(y, Product(8, w)), 2))
        --> (9)(-2) z + 5 + (u^{-1})^{3} + (6 x (y + 8 w))^2

    NEGATIVE 1 IN PRODUCTS:
        Don't write -1 in products if -1 is the only number; just put a negative sign out front.
        Example: Product(z, -1, Sum(x, 2)) --> -z(x+2)
        Non-Example: Product(z, -1, 7) --> (-1)(7)z

    ADDITION VERSUS SUBTRACTION SIGN:
        Use '- x' instead of '+ -x' when adding a negative number.
        Example: Sum(x, -2, Product(-1, z, y)) --> x - 2 - z y

    WRITE PRODUCTS IN A REASONABLE ORDER:
        There is a "standard" way of writing products by hand, e.g. put numbers first.
        Example: Product(x, 3, c) --> 3cx    (for c constant, x not constant)

    WRITE FRACTIONS, BUT NOT TOO MANY FRACTIONS:
        It's nice to sometimes wite products as fractions, but limiting the number of fractions-within-fractions.
        We also don't want to put too many parentheses when we do something like this.
        Example: Product(x, Power(y, -1), Sum(Power(z, -2), 5), Power(Sum(Product(6, Power(u, -2)), 7), -3)
           --> \frac{x}{y (6 u^{-2} + 7)^3} (\frac{1}{z^2} + 5)         (limit = one layer of fractions.)

        We also want to allow the user to increase the limit on number of fractions-within-fractions, such as:
           --> \frac{x}{y (\frac{6}{u^2} + 7)^3} (\frac{1}{z^2} + 5)    (limit = two layers of fractions.)

To accomplish the parentheses / enclosure task in various situations, we check str_should_protect(x, situation).
This allows any object to define an appropriately named function for the situation, to decide whether it needs protecting.
The default is False (no protecting) because the connectivity of most objects' strings in python is unambiguous.
(e.g. numpy arrays look like [...]; the brackets make it clear that is one object.)


The position of the term can make a difference.
For example, Product and Sum need protection from Power if in the base, but not if in the exponent.
Also (eventually), derivatives needs protection from Product but not if they are the last term in the Product.

[TODO] Power with single-character symbol base should not use {} in base,
    e.g. x^{2} instead of {x}^{2}, this allows for more concise expressions when subscripts are involved,
    e.g. x_{n}^{2} puts the 2 above the n, while {x_{n}}^{2} puts the 2 after the n.

[TODO] _StrProtectCheckers() should probably inherit from tools.CallablesTracker.
"""

from .symbols import Symbol
from .sum import Sum
from .product import Product
from .power import Power
from .equation import Equation
from .equation_system import EquationSystem
from .basics_tools import (
    get_base_and_power, has_minus_sign,
)
from ..abstracts import (
    SymbolicObject,
    is_nonsymbolic, is_number, is_constant,
)
from ..attributors import attributor
from ..tools import (
    equals,
    is_integer,
    _str,
    categorize, Categorizer,
    Binding,
)
from ..defaults import DEFAULTS


binding = Binding(locals())


''' --------------------- _str_info, StringEncInfo --------------------- '''

@attributor
def _str_info(x, enc=None, **kw):
    '''returns x._str_info(enc=enc, **kw) if available, else StringEncInfo(str(x), None).
    The idea is that we want to know string for x and also outermost enclosure used for protecting x,
    so that we can swap between parentheses and brackets.
    E.g. surround (x+7)^2 + y in brackets if it needs protection, e.g. 5z[(x+7)^2 + y].

    enc: None or '()' or '[]'.
        if None, ignore.
        otherwise, force outermost enc in self to be the value povided.
    '''
    try:
        return x._str_info(enc=enc, **kw)
    except AttributeError:
        return StringEncInfo(_str(x, **kw), None)

class StringEncInfo():
    '''stores string info about a SymbolicObject: string, enc.
    string: str(obj)
    enc: '()', '[]', or None.
        Indicates outermost protection used in string.
    protected: True, False, or None.
        Indicates whether outermost layer inside string is protected via enc.
        None --> don't know.
    '''
    def __init__(self, string, enc=None, protected=None, fraction_layers=0):
        self.string = string
        self.enc = enc
        self.protected = protected  # 
        self.fraction_layers = fraction_layers
    
    def __repr__(self):
        return f'{type(self).__name__}(string={repr(self.string)}, enc={repr(self.enc)}, fraction_layers={self.fraction_layers})'

    # # # STRING-LIKE BEHAVIOR # # #
    def __str__(self): return self.string
    def __len__(self): return len(self.string)
    def __iter__(self): return iter(self.string)
    def __getitem__(self, i): return self.string[i]
    def __getattr__(self, attr): return getattr(self.string, attr)


''' --------------------- enc, protection --------------------- '''

_OPPOSITE_ENC = {None: None, '()': '[]', '[]':'()'}
def _opposite_enc(enc=None):
    '''returns opposite enc. None --> None. '()' --> '[]'. '[]' --> '()'.'''
    return _OPPOSITE_ENC[enc]

def _usable_enc(enc=None):
    '''returns an enc that can be used. None --> '()'. Anything else --> itself.'''
    return '()' if enc is None else enc

def _get_enc(enc=None):
    r'''returns enc to actually use.
    Now, implementation will return '\left(', '\right)', or use [] instead of ().
    Eventually, might implement options to just use '(', ')' and/or preset sizes like '\Big(', '\Big)'.
    '''
    usable_enc = _usable_enc(enc)
    return (fr'\left{usable_enc[0]}', fr'\right{usable_enc[1]}')

def str_protected(s, enc=None):
    '''uses enc to return protected version of s.'''
    enc = _get_enc(enc)
    return f'{enc[0]} {s} {enc[1]}'

def str_info_protected(s, enc=None):
    '''uses enc to return StringEncInfo for protected version of s.'''
    enc = _usable_enc(enc)
    return StringEncInfo(str_protected(s, enc=enc), enc, protected=True)

def str_info_pia(x, protect, enc=None, **kw__str_info):
    '''returns StringEncInfo for string of x, Protected If Appropriate to the situation.
    x: object
        the object to be converted into string info.
    protect: bool
        whether to protect the string.
    enc: None or '()' or '[]'.
        if None, ignore.
        otherwise, force outermost enc to be the value povided.
        if protection is required, this means surround str(x) with enc, and use opposite enc during str(x).
        otherwise, this means pass enc to str(x).
    **kw__str_info: additional keyword args
        will be passed to _str_info(x)

    returns StringEncInfo(string of x protected if appropriate, outermost enc in that string)
    '''
    if protect:
        x_sinfo = _str_info(x, enc=_opposite_enc(enc), **kw__str_info)
        x_enc = _usable_enc(_opposite_enc(x_sinfo.enc))
        x_str = str_protected(str(x_sinfo), x_enc)
    else:
        x_sinfo = _str_info(x, enc=enc, **kw__str_info)
        x_enc = x_sinfo.enc
        x_str = str(x_sinfo)
    return StringEncInfo(x_str, x_enc, protected=protect)

class _StrProtectCheckers():
    '''stores list of functions used to check whether contents in strings should be protected.'''
    def __init__(self, *checkers):
        self.checkers = list(checkers)
    def __repr__(self):
        return f'{type(self).__name__}({self.checkers})'
    def __getitem__(self, i):
        return self.checkers[i]
    def append(self, val):
        self.checkers.append(val)
    def registerer(self):
        '''return func decorator which registers func as a checker.'''
        def register_as_checker(f):
            '''registers f as a checker, then returns f.'''
            self.append(f)
            return f
        return register_as_checker

STR_PROTECT_CHECKERS = _StrProtectCheckers()
str_protector = STR_PROTECT_CHECKERS.registerer()


''' --------------------- str for SymbolicObject --------------------- '''
# obj.__str__() for SymbolicObject returns str(obj._str_info()).

with binding.to(SymbolicObject):
    @binding
    def __str__(self, *args, **kw):
        '''string of self. Returns str(self._str_info(*args, **kw)) if available, else repr(self).'''
        try:
            self_str_info = self._str_info
        except AttributeError:
            return repr(self)
        else:
            return str(self_str_info(*args, **kw))


''' --------------------- str for Sum --------------------- '''

# # # STR_PROTECT_SUM_SUMMAND # # #
@str_protector
def _str_protect_sum_summand(x):
    '''return whether x needs protection from Sum.
    if available, returns x._str_protect_sum_summand().
    otherwise, returns False (by default, most things don't need protection from Sum).
    '''
    try:
        return x._str_protect_sum_summand()
    except AttributeError:
        return False

with binding.to(Sum):
    @binding
    def _str_protect_sum_summand(self):
        '''returns True, because str needs protecting if it appears in another Sum.
        That protection indicates to the user that there are layered Sums,
        and they may want to simplify using _associative_flatten.
        '''
        return True

# # # SUM STR # # #
with binding.to(Sum):
    @binding
    def _str_info(self, enc=None, **kw):
        '''string for self, and info about enclosure in parentheses or brackets.

        enc: None or '()' or '[]'.
            if None, ignore. otherwise, force outermost enc in self to this value.

        Note: we only protect Sum from Sum; other terms are unprotected from Sum.
        '''
        # get string info for all terms in self, forcing them to have the same outer-most enc.
        sinfos = []
        protected = False
        for summand in self:
            protect = _str_protect_sum_summand(summand)
            protected = protected or protect
            sinfo = str_info_pia(summand, protect, enc=enc, **kw)
            sinfos.append(sinfo)
            if (enc is None) and (sinfo.enc is not None):
                enc = sinfo.enc
        # combine strings. use '- x' instead of '+ -x' if adding a negative number.
        result = str(sinfos[0])
        for sinfo in sinfos[1:]:
            sep = ' ' if str(sinfo).lstrip().startswith('-') else ' + '
            result += sep + str(sinfo)
        # return result, with info about enc.
        return StringEncInfo(result, enc, protected=protected)


''' --------------------- str for Power --------------------- '''

# # # STR PROTECT POWER BASE # # #
@str_protector
def _str_protect_power_base(x, **kw):
    '''returns whether x needs protecting due to being in the base of a Power.
    if available, returns x._str_protect_power_base(**kw).
    otherwise, returns True except for non-negative integers,
        with fewer digits than the display precision (DEFAULTS.STRINGREP_NUMBERS_PRECISION).
    '''
    try:
        x_str_protect_power_base = x._str_protect_power_base
    except AttributeError:
        pass  # handled after 'else' block.
    else:
        return x_str_protect_power_base(**kw)
    if is_nonsymbolic(x):
        if is_integer(x):
            precision = kw.get('numbers_precision', DEFAULTS.STRINGREP_NUMBERS_PRECISION)
            if abs(x) < 10**precision:  # << _str(x) will not have '\times' in it.
                return has_minus_sign(x)
    return True

with binding.to(Symbol):
    @binding
    def _str_protect_power_base(self, **kw__None):
        '''returns False, because str does not need protecting if it appears in base of Power.'''
        return False

with binding.to(Sum, Product):
    @binding
    def _str_protect_power_base(self, **kw__None):
        '''returns True, because str needs protecting if it appears in base of Power.'''
        return True

with binding.to(Power):
    @binding
    def _str_protect_power_base(self, **kw__None):
        '''returns True, because str needs protecting if it appears in base of Power.'''
        return True

# # # STR PROTECT POWER EXPO # # #
@str_protector
def _str_protect_power_expo(x, **kw):
    '''returns whether x needs protecting due to being in the exponent of a Power.
    if available, returns x._str_protect_power_expo().
    otherwise, returns False.
    '''
    try:
        return x._str_protect_power_expo(**kw)
    except AttributeError:
        return False

with binding.to(Power):
    @binding
    def _str_protect_power_expo(self, **kw__None):
        '''returns True, because str will be less ambiguous if protected when appearing in exponent of Power.'''
        return True

# # # POWER STR # # #
with binding.to(Power):
    @binding
    def _str_info(self, enc=None, **kw):
        '''string for self, and info about enclosure in parentheses or brackets.

        enc: None or '()' or '[]'.
            if None, ignore. otherwise, force outermost enc in self to this value.
        '''
        base_protect = _str_protect_power_base(self[0], **kw)
        expo_protect = _str_protect_power_expo(self[1], **kw)
        base_sinfo = str_info_pia(self[0], base_protect, enc=enc, **kw)
        expo_sinfo = str_info_pia(self[1], expo_protect, enc=enc, **kw)
        base_str = str(base_sinfo)
        expo_str = str(expo_sinfo)
        self_str = f'{{{base_str}}}^{{{expo_str}}}'
        self_enc = base_sinfo.enc
        return StringEncInfo(self_str, self_enc, protected=base_protect)


''' --------------------- str for Product --------------------- '''

# # # PRODUCT STR FACTORS ORDER # # #
def _product_str_factors_order(factors):
    '''returns factors, ordered for str representation.'''
    factors_lists = _STR_PRODUCT_FACTORS_CATEGORIES.categorize(factors)
    return tuple(factor for factors_list in factors_lists for factor in factors_list)

_STR_PRODUCT_FACTORS_CATEGORIES = Categorizer(
    ('negative_1', lambda factor: equals(factor, -1)),
    ('nonsymbol', is_nonsymbolic),
    ('number', is_number),
    ('constant', is_constant),
)

with binding.to(Product):
    @binding
    def _str_factors_order(self):
        '''returns list of factors of self in order for str representation.'''
        return _product_str_factors_order(self)

# # # STR PROTECT PRODUCT FACTOR # # #
@str_protector
def _str_protect_product_factor(x, pre_factors=[], post_factors=[], **kw):
    '''returns whether x needs protecting due to being a factor in Product.

    if len(pre_factors) == len(post_factors) == 0, return False
        (this is basically like there not actually being a product at all...
        it can occur e.g. as we split up factors into numerator and denominator,
        rather than handling all factors at once.)
    otherwise, returns x._str_protect_product_factor(*args, **kw), if possible.
    otherwise...:
        if x is not the first factor, return True
        if next factor is nonsymbolic object OR a Power with nonsymbolic object base, return True
        otherwise, return False

    (factors are split into pre and post because some things will care about that.
    e.g. whether we can write grad(y) without parentheses depends on the factor after it.)
    '''
    if len(pre_factors) == 0 == len(post_factors):
        return False
    try:
        return x._str_protect_product_factor(pre_factors=pre_factors, post_factors=post_factors, **kw)
    except AttributeError:
        if len(pre_factors) > 0:
            # err on the side of caution; x without a _str_protect_product_factor method
            # should always be protected unless it is the first factor.
            # to make less protection, implement _str_protect_product_factor method for more things.
            return True
        if len(post_factors) > 0:
            next_factor = post_factors[0]
            if is_nonsymbolic(get_base_and_power(next_factor)[0]):
                return True
        return False

with binding.to(Sum):
    @binding
    def _str_protect_product_factor(self, **kw__None):
        '''returns True, because str needs protecting if it appears as a factor in Product.'''
        return True

with binding.to(Symbol, Power):
    @binding
    def _str_protect_product_factor(self, **kw__None):
        '''returns False, because str doesn't need protecting if it appears as a factor in Product.'''
        return False

with binding.to(Product):
    @binding
    def _str_protect_product_factor(self, **kw__None):
        '''returns True, because str needs protecting if it appears in another Product.
        That protection indicates to the user that there are layered Products,
        and they may want to simplify using _associative_flatten.
        '''
        return True

# # # PRODUCT STR INFO FROM FACTORS # # #
def _product_str_info_from_factors(*factors, enc=None, _one_if_empty=True, **kw):
    '''product string info from lists of factors.

    enc: None or '()' or '[]'.
        if None, ignore. otherwise, force outermost enc in self to this value.
    _one_if_empty: True or False
        how to behave when factors == () or factors == (-1,)
        factors == () --> this kwarg tells whether to return '1' (if True) or '' (if False)
        factors == (-1,) --> this kwarg tells whether to return '-1' (if True) '- ' (if False)
        (Note the actual returned value will be a StringEncInfo object with enc=None.)
    '''
    # handle the special case where _one_if_empty and factors [] or [-1].
    if len(factors) < 2 and _one_if_empty:
        if len(factors) == 0:
            return StringEncInfo('1', enc=None)
        elif equals(factors[0], -1):
            return StringEncInfo('-1', enc=None)
    # handle the special case where the first factor is -1: don't show the '1' in this case.
    if equals(factors[0], -1):
        result = '- '   # ignore the -1; start with a minus sign.
        factors_to_stringify = factors[1:]
    else:
        result = ''
        factors_to_stringify = factors
    # get string info for all factors in self, forcing them to have the same outer-most enc.
    sinfos = []
    protected = False
    for i, factor in enumerate(factors_to_stringify):
        protect = _str_protect_product_factor(factor, factors[:i], factors[i+1:], **kw)
        protected = protected or protect
        sinfo = str_info_pia(factor, protect, enc=enc, **kw)
        sinfos.append(sinfo)
        if (enc is None) and (sinfo.enc is not None):
            enc = sinfo.enc
    # combine strings.
    result = result + ' '.join(str(sinfo) for sinfo in sinfos)
    return StringEncInfo(result, enc, protected=protected)

# # # PRODUCT STR # # #
with binding.to(Product):
    @binding
    def _str_info(self, fraction_layers=None, enc=None, **kw):
        '''string for self, and info about enclosure in parentheses or brackets.

        enc: None or '()' or '[]'.
            if None, ignore. otherwise, force outermost enc in self to this value.

        fraction_layers: None or int
            None --> read DEFAULTS.FRACTION_LAYERS
            int --> use fractions if >0. pass (fraction_layers - 1) to _str for base.

        NOTE: parentheses appearing around entire numerator or denominator? Maybe you need to simplify.
        [TODO] handle "put '- ' on the outside instead of top or bottom of fraction."
        [TODO] handle "put vectors on the outside instead of top of fraction." (but not cross products?)
        '''
        if fraction_layers is None:
            fraction_layers = DEFAULTS.STRINGREP_FRACTION_LAYERS
        # check for fractions, if we are allowed to write fractions...
        if fraction_layers > 0:
            numer_factors, denom_factors = self.fraction_dichotomize()
            # if self represents a fraction, write a fraction
            if len(denom_factors) > 0:
                numer_ordered = _product_str_factors_order(numer_factors)
                denom_ordered = _product_str_factors_order(denom_factors)
                kw_sff = dict(fraction_layers=fraction_layers-1, **kw)
                numer_sinfo = _product_str_info_from_factors(*numer_ordered, enc=enc, _one_if_empty=True, **kw_sff)
                denom_sinfo = _product_str_info_from_factors(*denom_ordered, enc=numer_sinfo.enc, **kw_sff)
                numer_str = str(numer_sinfo)
                denom_str = str(denom_sinfo)
                self_str = fr'\frac{{{numer_str}}}{{{denom_str}}}'
                self_enc = numer_sinfo.enc
                return StringEncInfo(self_str, self_enc)  # [TODO] protected? fraction_layers?
            else:   # otherwise, not a fraction; handle things below, instead.
                pass
        factors = self._str_factors_order()
        result = _product_str_info_from_factors(*factors, fraction_layers=fraction_layers, enc=enc, **kw)
        return result


''' --------------------- str for Equation --------------------- '''

with binding.to(Equation):
    @binding
    def _str_info(self, enc=None, align=False, **kw):
        '''string for self, and info about enclosure in parentheses or brackets.
        enc: None or '()' or '[]'.
            if None, ignore. otherwise, force outermost enc in self to this value.
        align: bool, default False
            True --> use '&='. False --> use '='.

        Note: we don't need to worry about protecting terms from being in an Equation.
        '''
        lhs_sinfo = _str_info(self[0], enc=enc, **kw)
        rhs_sinfo = _str_info(self[1], enc=lhs_sinfo.enc, **kw)  # force outermost enc in rhs same as in lhs.
        _eq_ = '&=' if align else '='
        self_str = f'{str(lhs_sinfo)} {_eq_} {str(rhs_sinfo)}'
        self_enc = lhs_sinfo.enc  # enc is determined by outermost enc in lhs or rhs.
        return StringEncInfo(self_str, self_enc, protected=False)


''' --------------------- str for EquationSystem --------------------- '''

with binding.to(EquationSystem):
    @binding
    def __str__(self, tab='  ', align=True, indexing=0, show_solved=True, **kw__str):
        '''string for self. No info about enclosure in parenthese or brackets because that's complicated.
        tab: string
            put this before each equation
        align: bool, default True
            whether to put in an align block (aligns on '=').
        indexing: int or None. default 0.
            number --> label equations with numbers (e.g. (1)), starting with this number.
            None --> don't put any numbers to label the equations.
        show_solved:
            True  --> show all equations in the system, even if they are "solved".
            False --> only show "unsolved" equations in the system.
            None  --> only show "unsolved" equations, except if all are "solved" then show all, instead.
        **kw__str:
            will be passed to _str(eq) for each eq in self that we convert to a string.
        '''
        # which equations to show (depending on show_solved)
        if show_solved or (show_solved is None and len(self.solved) == len(self)):
            ieqs, eqs = list(range(len(self))), [eq for eq in self]
        elif len(self.solved) == len(self):
            return (f' $EquationSystem({len(self)} equations, all solved); '
                    'Use show_solved=True to show all solved equations.$ ')
            # (the ' $', '$ ' are so that during view(), it looks like plaintext, not mathtext.)
        else:
            ieqs, eqs = zip(*[(i, self[i]) for i in self.unsolved])
        # get equation strings
        eqs = [tab + _str(eq, align=align, **kw__str) for eq in eqs]
        # put index numbers if doing indexing
        if indexing is not None:
            sep = r'&&' if align else r'\quad'
            eqs = [fr"({i+indexing}{'*' if i in self.solved else ''})    {sep}    {eq}" for i, eq in zip(ieqs, eqs)]
        # combine all the info into the result
        eqstr = (r' \\' + '\n').join(eqs)   # note: '\\' tells latex "newline"
        if align:
            result = r'$\begin{align}'+'\n' + eqstr + '\n'+r'\end{align}$'
        else:
            result = eqstr
        # return the result
        return result