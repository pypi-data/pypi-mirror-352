"""
File Purpose SummationOperator, SummationOperation

For summation notation, e.g. Sigma_{n=0}^{9} n^2

[TODO] disallow, or raise clear warning, summation object with index=None.
[TODO] make an initializer_for(SummationOperation)
"""
import textwrap  # for docs spacing
DOCS_TAB = ' '*4  # tab for docs.

from .linear_operations import LinearOperation
from .linear_operators import LinearOperator
from ..abstracts import (
    SymbolicObject,
    SubbableObject, is_subbable,
    SimplifiableObject,
    simplify_op, simplify_op_skip_for,
    contains_deep, contains_deep_subscript,
)
from ..basics import add
from ..errors import (
    PatternError, InputConflictError, SummationIndicesMissingError,
)
from ..initializers import INITIALIZERS, initializer_for
from ..tools import (
    _repr, _str,
    equals,
    caching_attr_simple, caching_attr_simple_if,
    format_docstring, Binding,
)
binding = Binding(locals())

from ..defaults import DEFAULTS


''' --------------------- indices from input; docs --------------------- '''

_summation_argdocs = \
    r'''imin: integer or None.
            minimum value of summation index during the summation.
        imax: integer or None.
            maximum value of summation index during the summation.'''

_summation_kwargdocs = \
    r'''iset: object or None.
            set (or list or tuple) of indices to use in the summation index to evaluate the summation.
            if provided, imin and imax must both be None.
                And the behavior depends on whether or not iset is iterable:
                iterable --> use these indices to evaluate the summation.
                    also, convert to tuple internally.
                else --> any attempts to get indices info will raise SummationIndicesMissingError.'''

_summation_propdocs = {
    'index': '''summation index, e.g. Symbol('n')''',
    'imin': '''minimum value of summation index during the summation''',
    'imax': '''maximum value of summation index during the summation''',
    'iset': '''set of indices to plug in for the summation index during the summation.
        Implementation note: imin and imax will be ignored if self.iset is not None.
        Though SymSolver recommends you do not edit _imin or _imax in an instance of this object;
        instead make a new object with the desired imin or imax, e.g. via self.with_imin(new_imin).''',
}   

@format_docstring(argdocs=_summation_argdocs, kwargdocs=_summation_kwargdocs)
def _summation_indices_kw_from_input(imin=None, imax=None, *, iset=None):
    '''returns (imin, imax, iset), after some quick checks:
        - Ensure iset is only provided if imin and imax are not provided.
        - If iset is iterable, convert it to a tuple.

    POSITIONAL-OR-KEYWORD ARGS:
        {argdocs}

    KEYWORD-ONLY ARGS:
        {kwargdocs}
    '''
    if iset is not None:
        if (imin is not None) or (imax is not None):
            raise InputConflictError('Cannot provide iset AND imin or imax.')
        try:
            _iset = tuple(iset)
        except TypeError:
            _iset = iset
    else:
        _iset = None
    return (imin, imax, _iset)


''' --------------------- SummationSymbol --------------------- '''

_summation_symbol_kwargdocs = \
    fr'''{_summation_kwargdocs}
        _big: bool, default True.
            whether to use '\sum' for the main symbol, i.e. the "big Sigma".
            True --> use '\sum'. index info will be directly above and below the symbol.
            False --> use '\Sigma'. index info will be sub/superscripts to the right of the symbol.'''

@format_docstring(argdocs=_summation_argdocs, kwargdocs=_summation_symbol_kwargdocs)
class SummationSymbol(SubbableObject):
    r'''Summation Symbol. For something like: \Sigma_{{n=1}}^{{7}}.
    Contains no rules for evaluating / calling on an object to create a summation;
    not intended for direct use. See SummationOperator or SummationOperation instead.

    POSITIONAL-OR-KEYWORD ARGS:
        index: object, probably a SymbolicObject. or None
            summation index, e.g. Symbol('n').
        {argdocs}

    KEYWORD-ONLY ARGS:
        {kwargdocs}
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, index=None, imin=None, imax=None, *, iset=None, _big=True):
        '''initialize. Ensure iset is only provided if imin and imax are not provided.'''
        self._index = index
        self._big = _big
        _imin, _imax, _iset = _summation_indices_kw_from_input(imin=imin, imax=imax, iset=iset)
        self._imin = _imin
        self._imax = _imax
        self._iset = _iset

    index = property(lambda self: self._index, doc=_summation_propdocs['index'])
    imin  = property(lambda self: self._imin,  doc=_summation_propdocs['imin'])
    imax  = property(lambda self: self._imax,  doc=_summation_propdocs['imax'])
    iset  = property(lambda self: self._iset,  doc=_summation_propdocs['iset'])

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another instance of type(self) to be like self,
        via self._new(*args, **kw). Note these will be overwritten in _new by any **kw entered.
        '''
        kw = super()._init_properties()
        kw['index'] = self.index
        kw['imin'] = self.imin
        kw['imax'] = self.imax
        kw['iset'] = self.iset
        kw['_big'] = self._big
        return kw

    def with_index(self, new_index):
        '''returns copy of self with index=new_index'''
        return self._new(index=new_index)

    def with_imin(self, new_imin):
        '''returns copy of self with imin=new_imin'''
        return self._new(imin=new_imin)

    def with_imax(self, new_imax):
        '''returns copy of self with imax=new_imax'''
        return self._new(imax=new_imax)

    def with_iset(self, new_iset):
        '''returns copy of self with iset=new_iset'''
        return self._new(iset=new_iset)

    def with_ilims(self, new_imin, new_imax, new_iset=None):
        '''returns copy of self with imin=new_imin, imax=new_imax, and iset=new_iset.'''
        return self._new(imin=new_imin, imax=new_imax, iset=new_iset)

    # # # SUBSTITUTION # # #
    def _iter_substitution_terms(self, **kw__None):
        '''returns iterator over terms to check for substitution in self.
        This yields, from self, in this order: imin, imax, iset, index
        '''
        yield self.imin
        yield self.imax
        yield self.iset
        yield self.index

    def _new_after_subs(self, new_imin, new_imax, new_iset, new_index):
        '''returns new object like self; for internal use after checking for substitutions in imin, imax, and iset.
        The implementation here just retuns self._new(imin=new_imin, imax=new_imax, iset=new_iset).
        '''
        return self._new(imin=new_imin, imax=new_imax, iset=new_iset, index=new_index)

    def subs_subscripts(self, *subscript_subs, **kw):
        '''returns result of substituting subscript_subs into self.
        subscripts are subbed simultaneously, e.g. [x,y,z] subsubs ((x,y),(y,z),(z,a)) --> [y,z,a].

        ALSO checks for regular sub with self.index, subbing there if a match is found.
        i.e. if self.index == old, replace with new. (for any (old, new) in subscript_subs)

        if any substitutions were performed, returns self._new(subscripts=new_subscripts).
        '''
        result = super().subs_subscripts(*subscript_subs, **kw)
        for old, new in subscript_subs:
            if result.index == old:
                result = result._new(index=new)
        return result

    # # # DISPLAY # # #
    def _repr_contents(self, **kw):
        '''returns contents to put inside 'SummationSymbol()' in repr for self.'''
        contents = []
        for key in ('index', 'imin', 'imax', 'iset'):
            val = getattr(self, key)
            if val is not None:
                contents.append(f'{key}={_repr(val, **kw)}')
        return contents

    def __str__(self, **kw):
        '''string representation of self.
        [TODO] shorten str for long iterable iset, e.g. (2,4,6,...,20) instead of listing all terms.
        '''
        result = r'\sum' if self._big else r'\Sigma'
        index = self.index
        iset = self.iset
        imin = self.imin
        imax = self.imax
        if iset is None:
            # subscript
            if (imin is None) and (index is not None):
                result += f'_{{{_str(index, **kw)}}}'
            elif (imin is not None) and (index is None):
                result += f'_{{{_str(imin, **kw)}}}'
            elif (imin is not None) and (index is not None):
                result += f'_{{{_str(index, **kw)}={_str(imin, **kw)}}}'
            # supescript
            if (imax is not None):
                result += f'^{{{_str(imax, **kw)}}}'
        else:  # iset is not None -- handle subscript, and do no superscript.
            if index is None:
                result += f'_{{{_str(iset, **kw)}}}'
            else:
                result += fr'_{{{_str(index, **kw)} \ \in \ {_str(iset, **kw)}}}'
        return result

    # # # EQUALITY # # #
    def __eq__(self, b):
        '''returns whether self==b.'''
        try:
            return SymbolicObject.__eq__(self, b)
        except NotImplementedError:
            pass  # handled below
        if not equals(self.index, b.index):
            return False
        if not equals(self.imin, b.imin):
            return False
        if not equals(self.imax, b.imax):
            return False
        if not equals(self.iset, b.iset):
            return False
        return True

    @caching_attr_simple
    def __hash__(self):
        return hash((type(self), self.index, self.imin, self.imax, self.iset))

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def _equals0(self):
        '''returns whether self == 0.
        True result guarantees self == 0.
        False result means self might not equal 0 (or it might, but we can't tell that here.)
        '''
        try:
            return len(self.indices())==0
        except SummationIndicesMissingError:
            return False

    # # # INSPECTION # # #
    def indices(self):
        '''returns tuple of indices of self. raise SummationIndicesMissingError if this is impossible.
        Examples:
            imin=5, imax=9 --> (5,6,7,8)
            imin=1, imax=1 --> (1,)
            imin=7, imax=3 --> ()
            iset=[2,3,5,7] --> (2,3,5,7)
            imin=1, imax=None --> raise SummationIndicesMissingError
            iset=Symbol('S') --> raise SummationIndicesMissingError
            imin=None, imax=None, iset=None --> raise SummationIndicesMissingError
        '''
        if self.iset is None:
            imin = self.imin
            imax = self.imax
            # if can't determine indices, raise a SummationIndicesMissingError with helpful message.
            if (imin is None) or (imax is None):
                if (imin is None) and (imax is None):
                    not_provided = 'imin and imax were'
                else:
                    not_provided = 'imin was' if (imin is None) else 'imax was'
                raise SummationIndicesMissingError(f'{not_provided} not provided.')
            # else, return indices.
            return tuple(range(imin, imax+1))
        else:  # get indices from iset.
            try:
                return tuple(self.iset)
            except TypeError:
                raise SummationIndicesMissingError('iset is not iterable, cannot get indices.')


''' --------------------- SummationOperator --------------------- '''

_summation_operator_argdocs = \
    fr'''index_or_summation_symbol: None, SummationSymbol, or other object.
            SummationSymbol --> use this summation symbol;
                and in this case, IGNORE inputs: imin, imax, iset and _big.
            else --> summation index, e.g. Symbol('n').
        {_summation_argdocs}'''

@format_docstring(argdocs=_summation_operator_argdocs, kwargdocs=_summation_symbol_kwargdocs)
class SummationOperator(LinearOperator, SubbableObject):
    '''Summation Operator. For something like "summation from n=1 to n=7".

    Calling this operator returns a SummationOperation, e.g. "summation of n^2 from n=1 to n=7".
    Using self.evaluate evaluates the summation, or raises SummationIndicesMissingError if that's not possible.
        e.g. "summation from n=1 to n=7".evaluate(n^2) --> "1^2+2^2+3^2+4^2+5^2+6^2+7^2".

    POSITIONAL-OR-KEYWORD ARGS:
        {argdocs}

    KEYWORD-ONLY ARGS:
        {kwargdocs}
    '''
    # # # INITIALIZATION # # #
    def __init__(self, index_or_summation_symbol=None, imin=None, imax=None, *, iset=None, _big=True):
        '''initialize. if index_or_summation_symbol is a SummationSymbol, ignore the other kwargs.'''
        self._init_properties_memory = dict(index_or_summation_symbol=index_or_summation_symbol,
                                            imin=imin, imax=imax, iset=iset, _big=_big)
        if isinstance(index_or_summation_symbol, SummationSymbol):
            self._summation_symbol = index_or_summation_symbol
        else:
            index = index_or_summation_symbol
            self._summation_symbol = SummationSymbol(index=index, imin=imin, imax=imax, iset=iset, _big=_big)
        LinearOperator.__init__(self, f=None, frep=self._summation_symbol, circ=False)

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another instance of type(self) to be like self,
        via self._new(*args, **kw). Note these will be overwritten in _new by any **kw entered.
        '''
        kw = super()._init_properties()
        kw.update(self._init_properties_memory)
        return kw

    # # # OPERATOR STUFF # # #
    def _f(self, g):
        '''returns SummationOperation(self, g).
        self._f will be called when self is called with a non-operator g.
        '''
        return SummationOperation(self, g)

    def treats_as_constant(self, value):
        '''returns whether self treats value as constant.
        if self.index is None, return False
        else if super().treats_as_constant(value),
            return whether index never appears in any subscript in value.
        else return whether index never in value anywhere (checking subscripts, too).
        '''
        index = self.index
        if index is None:
            return False
        if contains_deep_subscript(value, index):
            return False
        if contains_deep(value, index):
            return False
        return True

    def _treats_as_distributable_constant(self, value):
        '''eturns whether self treats value as a constant which can be distributed.
        "distribute" meaning f(ax + by) --> a f(x) + b f(y).
        The implementation here just returns self.treats_as_constant(value),
            because sum can be distributed through ANY values (even vectors) if they are treated as constants.
        '''
        return self.treats_as_constant(value)

    def evaluate(self, g):
        '''evaluates self at g.'''
        return self(g).evaluate()

    # # # SUBSTITUTION # # #
    def _iter_substitution_terms(self, **kw__None):
        '''returns iterator over terms to check for substitution in self.
        This just yields self._summation_symbol.
        '''
        yield self._summation_symbol

    def _new_after_subs(self, new_summation_symbol):
        '''returns new object like self; for internal use after checking for substitutions in self._summation_symbol.
        The implementation here just retuns self._new(index_or_summation_symbol=new_summation_symbol).
        '''
        return self._new(index_or_summation_symbol=new_summation_symbol)

    # # # EQUALITY # # #
    def __eq__(self, b):
        '''returns whether self==b.'''
        try:
            return SymbolicObject.__eq__(self, b)
        except NotImplementedError:
            return equals(self._summation_symbol, b._summation_symbol)

    @caching_attr_simple
    def __hash__(self):
        return hash((type(self), self._summation_symbol))

    def _equals0(self):
        ''''returns whether self == 0.'''
        return self._summation_symbol._equals0()

    # # # ALIASES TO SUMMATION SYMBOL STUFF # # #
    index = property(lambda self: self._summation_symbol.index, doc=_summation_propdocs['index'])
    imin  = property(lambda self: self._summation_symbol.imin,  doc=_summation_propdocs['imin'])
    imax  = property(lambda self: self._summation_symbol.imax,  doc=_summation_propdocs['imax'])
    iset  = property(lambda self: self._summation_symbol.iset,  doc=_summation_propdocs['iset'])

    def _init_properties_from_summation_symbol(self):
        '''returns dict of kwargs to use when initializing another instance of type(self) to be like self,
        via self._new_with_sumsym_attr(*args, **kw).
        '''
        kw = super()._init_properties()
        kw['index_or_summation_symbol'] = self.index
        kw['imin'] = self.imin
        kw['imax'] = self.imax
        kw['iset'] = self.iset
        kw['_big'] = self._big
        return kw

    def _new_with_sumsym_attr(self, *args, **kw):
        '''return self._new(...) but using settings from self._summation_symbol as defaults.'''
        kw__new = self._init_properties_from_summation_symbol()  # defaults
        kw__new.update(kw)   # updated with values entered into **kw here.
        return self._new(*args, **kw__new)

    def with_index(self, new_index):
        '''returns copy of self with index=new_index'''
        return self._new_with_sumsym_attr(index_or_summation_symbol=new_index)

    def with_imin(self, new_imin):
        '''returns copy of self with imin=new_imin'''
        return self._new_with_sumsym_attr(imin=new_imin)

    def with_imax(self, new_imax):
        '''returns copy of self with imax=new_imax'''
        return self._new_with_sumsym_attr(imax=new_imax)

    def with_iset(self, new_iset):
        '''returns copy of self with iset=new_iset'''
        return self._new_with_sumsym_attr(iset=new_iset)

    def with_ilims(self, new_imin, new_imax, new_iset=None):
        '''returns copy of self with imin=new_imin, imax=new_imax, and iset=new_iset.'''
        return self._new_with_sumsym_attr(imin=new_imin, imax=new_imax, iset=new_iset)

    @format_docstring(docstring=SummationSymbol.indices.__doc__)
    def indices(self):
        '''{docstring}'''
        return self._summation_symbol.indices()

@initializer_for(SummationOperator)
@format_docstring(argdocs=_summation_operator_argdocs, kwargdocs=_summation_symbol_kwargdocs)
def summation_operator(index_or_summation_symbol=None, imin=None, imax=None, *, iset=None, _big=True):
    '''initialize a SummationOperator object. For something like "summation from n=1 to n=7",
    but without specifying the operand (i.e. not yet specifying what should be summed).

    call this operator on the desired operand to create a SummationOperation object,
        e.g. summation_operator(...)(n**2)

    It is preferred to call this method instead of initializing directly from SummationOperator.

    POSITIONAL-OR-KEYWORD ARGS:
        {argdocs}

    KEYWORD-ONLY ARGS:
        {kwargdocs}
    '''
    return SummationOperator(index_or_summation_symbol, imin=imin, imax=imax, iset=iset, _big=_big)


''' --------------------- SummationOperation --------------------- '''

class SummationOperation(LinearOperation):
    '''Summation Operation. For something like "summation of n^2 from n=1 to n=7".
    Not intended for direct instantiation by user; please use the summation() function instead.

    Using self.evaluate evaluates the summation, or raises SummationIndicesMissingError if that's not possible.
        e.g. "summation of n^2 from n=1 to n=7".evaluate() --> "1^2+2^2+3^2+4^2+5^2+6^2+7^2".
    '''
    def __init__(self, summation_operator, operand, **kw):
        '''raise TypeError if summation_operator is not a SummationOperator instance.'''
        if not isinstance(summation_operator, SummationOperator):
            raise TypeError(f'expected SummationOperator but got {type(summation_operator)}')
        super().__init__(summation_operator, operand, **kw)

    def evaluate(self):
        '''tries to evaluate self.
        If this is impossible, raises an error:
            PatternError if it is impossible due to the summation index being None
            SummationIndicesMissingError if it is impossible due to insufficient indices info
        '''
        # setup
        summation_index = self.operator.index
        if summation_index is None:
            raise PatternError('Cannot evaluate() summation when summation index is None.')
        indices = self.operator.indices()
        # evaluating
        operand = self.operand
        subbable = is_subbable(operand)
        if subbable:
            return add(*(operand.sub_everywhere(summation_index, i) for i in indices))
        elif equals(operand, summation_index):
            return add(*indices)
        else:
            return len(indices) * operand


_summation_initializer_argdocs = \
    fr'''operand: object, probably a SymbolicObject or numerical value
            the formula / value to which the summation applies,
            e.g. "n^2" in "summation of n^2 from n=1 to n=7".
        {_summation_operator_argdocs}'''

@format_docstring(argdocs=_summation_initializer_argdocs, kwargdocs=_summation_symbol_kwargdocs)
def summation(operand, index_or_summation_symbol=None, imin=None, imax=None, *, iset=None, _big=True):
    '''initialize a SummationOperation object. For something like "summation of n^2 from n=1 to n=7".

    POSITIONAL-OR-KEYWORD ARGS:
        {argdocs}

    KEYWORD-ONLY ARGS:
        {kwargdocs}
    '''
    operator = INITIALIZERS.summation_operator(index_or_summation_symbol,
                        imin=imin, imax=imax, iset=iset, _big=_big)
    return SummationOperation(operator, operand)


''' --------------------- Expand Summation --------------------- '''

simplify_op_skip_for(SummationOperation, '_summation_operation_evaluate')

@simplify_op(SummationOperation, alias='_expand_summations')
def _summation_operation_evaluate(self, *,
                                  summation_indices=None,
                                  summation_iset=None,
                                  summation_irange=None, **kw):
    '''evaluates Summation self.
    Note, this would also occur during 'evaluate_operations' (i.e., _generic_operation_evaluate).
    Putting it as a separate operation here allows to:
        - evaluate *just* the summations (but not other operations) if desired
        - use the alias 'expand_summations', e.g. obj.apply('expand_summations').

    summation_indices: None or dict
        if provided, self.specify_summation_indices to these indices, first.
        Options are imin, imax, and iset.
        see help(self.specify_summation_indices) for details.
    summation_iset: None or iterable
        if provided, self.specify_summation_indices(iset=summation_iset) first.
    summation_irange: None or tuple (imin, imax)
        if provided, self.specify_summation_indices(imin=imin, imax=imax) first.

    other kwargs go to self._generic_operation_evaluate.
    '''
    indices = dict()
    if summation_indices is not None:
        indices.update(summation_indices)
    if summation_iset is not None:
        indices['iset'] = summation_iset
    if summation_irange is not None:
        indices['imin'], indices['imax'] = summation_irange
    if indices:
        self = self.specify_summation_indices(**indices)
    return self._generic_operation_evaluate(**kw)

with binding.to(SimplifiableObject):
    @binding
    @format_docstring(argdocs=textwrap.indent(_summation_argdocs, DOCS_TAB),
                      kwargdocs=textwrap.indent(_summation_kwargdocs, DOCS_TAB))
    def expand_summations(self, imin=None, imax=None, *, iset=None, only=True, **kw__simplify):
        '''expand summations throughout self, after specifying summation indices.
        substitutes new values of imin, imax, and/or iset into SummationSymbol objects throughout self.
        Only sub into imin, imax, and/or iset values which were previously None; doesn't alter existing values.
        This allows to easily specify indices for all summations at a later time.

        Equivalent to self.simplify(expand_summations=True,
                    summation_iset=iset, summation_irange=(imin, imax), **kw__simplify)

        POSITIONAL-OR-KEYWORD ARGS:
        {argdocs}

        KEYWORD-ONLY ARGS:
        {kwargdocs}
            only: bool, None, or list of strings, default True.
                goes to simplify(..., only=only). If True or False, change value first:
                if only is True, use only=['_summation_operation_evaluate']
                if only is False, use only=None
        '''
        if only is True:
            only = ['_summation_operation_evaluate']
        elif only is False:
            only = None
        kw_use = {'only': only, '_summation_operation_evaluate': True}
        kw_use.update(kw__simplify)
        if not (imin is None and imax is None and iset is None):
            kw_use.update(summation_irange=(imin, imax), summation_iset=iset)
        result = self.simplify(**kw_use)
        return result


''' --------------------- specify summation indices --------------------- '''

with binding.to(SummationSymbol):
    @binding
    @format_docstring(argdocs=textwrap.indent(_summation_argdocs, DOCS_TAB),
                      kwargdocs=textwrap.indent(_summation_kwargdocs, DOCS_TAB))
    def specify_summation_indices(self, imin=None, imax=None, *, iset=None):
        '''substitutes new values of imin, imax, and/or iset into self.
        Only sub into imin, imax, and/or iset values which were previously None; doesn't alter existing values.

        POSITIONAL-OR-KEYWORD ARGS:
        {argdocs}

        KEYWORD-ONLY ARGS:
        {kwargdocs}
        '''
        # quick checks:
        if (imin is None) and (imax is None) and (iset is None):
            return self  # return self, exactly, to help indicate nothing was changed.
        if not is_subbable(self):
            return self
        # sub into self; only alter values which were previously None.
        replaced_any = False
        new_imin = self.imin
        if (imin is not None) and (new_imin is None):
            replaced_any = True
            new_imin = imin
        new_imax = self.imax
        if (imax is not None) and (new_imax is None):
            replaced_any = True
            new_imax = imax
        new_iset = self.iset
        if (iset is not None) and (new_iset is None):
            replaced_any = True
            new_iset = iset
        # create new summation symbol if anything was changed
        if replaced_any:
            return self._new(imin=new_imin, imax=new_imax, iset=new_iset)
        else:
            return self  # return self, exactly, to help indicate nothing was changed.

with binding.to(SubbableObject):
    @binding
    @format_docstring(argdocs=textwrap.indent(_summation_argdocs, DOCS_TAB),
                      kwargdocs=textwrap.indent(_summation_kwargdocs, DOCS_TAB))
    def specify_summation_indices(self, imin=None, imax=None, *, iset=None, **kw):
        '''substitutes new values of imin, imax, and/or iset into SummationSymbol objects throughout self.
        Only sub into imin, imax, and/or iset values which were previously None; doesn't alter existing values.
        This allows to easily specify indices for all summations at a later time.

        POSITIONAL-OR-KEYWORD ARGS:
            {argdocs}

        KEYWORD-ONLY ARGS:
            {kwargdocs}

        additional kwargs will be passed to _iter_substitution_terms().
        '''
        # quick checks:
        if (imin is None) and (imax is None) and (iset is None):
            return self  # return self, exactly, to help indicate nothing was changed.
        if not is_subbable(self):
            return self
        # loop through subbable terms in self, calling term.specify_summation_indices(...).
        def specify_summation_indices_rule(term):
            return term.specify_summation_indices(imin=imin, imax=imax, iset=iset, **kw)
        return self._substitution_loop(specify_summation_indices_rule, **kw)
