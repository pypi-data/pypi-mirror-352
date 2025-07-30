"""
File Purpose: SymbolicObject

SymbolicObject is the base class for all SymSolver symbolic objects.
This includes AbstractOperations, Polynomials, and Constants.

SymbolicObjects are intended to be immutable:
    Rather than editing a SymbolicObject, make a new one instead.
    Motivation was that it can be very easy to make mistakes if the objects change.
        For example: s=x+3; p=s*y; s[1]=7.
        Now, s==x+7. Should we have p=(x+3)*y, or p=(x+7)*y?
        This can easily be confusing and cause unexpected behavior.
        While SymSolver does not forbid s[1]=7, it would be better practice to do:
            l=list(s); l[1]=7; new_s=sum(*l)
            OR, perform the operation mathematically instead, e.g.:
            new_s = (s - 3 + 7).simplify()
        Additionally, SymSolver assumes immutability for SymbolicObjects:
            - some caching is performed by default which assumes immutability of SymbolicObjects,
            so if the objects are changed, results may be incorrect. Caching can be turned off via DEFAULTS.
            - [TODO] force immutability / make warning when immutability is not respected.
            at some point in the future, immutability may be "forced"
            (cannot be truly enforced without coding in C, which we won't do here.
            but maybe can enforce for the "usual" offenders, e.g. __setattr__ and __setitem__.)
    There is lots of architecture to support this.
    From an end-user perspective,
        the best idea is usually to perform operations mathematically.
    From an internal-coding perspective,
        just be careful about things :)
"""

from ._init_modifiers import (
    INIT_MODIFIERS,
)
from ..attributors import attributor
from ..tools import (
    view,
    equals,
    is_number,   # << imported into this namespace for historic & convenience reasons.
    layers,
    caching_attr_simple_if,
)
from ..defaults import DEFAULTS


''' --------------------- Convenience --------------------- '''

@attributor
def is_nonsymbolic(x):
    '''returns whether x is not a SymbolicObject.
    Equivalent to not isinstance(x, SymbolicObject)
    '''
    return not isinstance(x, SymbolicObject)

@attributor
def is_constant(x):
    '''returns whether x is a constant.
    returns x.is_constant() if possible, else True.
    Note that SymbolicObject.is_constant gives False by default.
    '''
    try:
        return x.is_constant()
    except AttributeError:
        return True

@attributor
def symdeplayers(x):
    '''return number of layers in self which depend on a SymbolicObject.
    returns x.symdeplayers() if possible, else 0.

    x.symdeplayers() gives 1 + max(symdeplayers(term) for term in self)
    '''
    try:
        return x.symdeplayers()
    except AttributeError:
        return 0

@attributor
def _equals0(x):
    '''returns whether x equals 0. Checks x._equals0() if possible, else x==0.
    (Some SymbolicObjects define obj._equals0() separately from __eq__.
    e.g. Product._equals0 can just return whether any terms equal 0.)
    '''
    try:
        return x._equals0()
    except AttributeError:
        return equals(x, 0)


''' --------------------- SymbolicObject --------------------- '''

class SymbolicObject():
    '''base class for all SymSolver symbolic objects.
    Not necessarily an operation or a Symbol, e.g. Equation is a Symbolic object.
    '''
    # # # CREATING # # #
    initializer = property(lambda self: type(self),
            doc='''callable object to use when attempting to create a new object of type(self).
            default is type(self), i.e. initialize in the "usual way" for classes.
            However, subclasses may provide a different initializer.
            e.g. initializer for Product is product, to handle cases of 0 or 1 args.
            ''',
            )

    def _new(self, *args, **kw):
        '''create new instance of type(self),
        and same properties as self, except any which are overwritten by kw.
        calls _transmit_genes to pass genes on to child.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        init_props = self._init_properties()
        init_props.update(kw)
        init_args = self._init_args()
        result = self.initializer(*init_args, *args, **init_props)
        self._transmit_genes(result)
        return result

    def _init_properties(self):
        '''returns dict of kwargs to use when initializing another instance of type(self) to be like self,
        via self._new(*args, **kw). Note these will be overwritten in _new by any **kw entered.
        '''
        return dict()

    def _init_args(self):
        '''returns args to use before user-entered args when initializing another instance of type(self) like self,
        via self._new(*args, **kw). Note these will go before *args.'''
        return ()

    def _transmit_genes(self, x):
        '''if self has a _genes attribute, for gene in self._genes, set x.gene = self.gene.
        (If type(x) != type(self), don't transmit genes.)

        The idea is, genes are properties which should will be passed down anytime self._new is used,
            any number of times. E.g. self._new(...)._new(...) will have the same genes as self.

        returns whether we transmitted any genes.
        '''
        if (type(self) == type(x)) and hasattr(self, '_genes'):
            x._genes = self._genes
            for gene in self._genes:
                self_gene_value = getattr(self, gene)
                setattr(x, gene, self_gene_value)
            return len(self._genes) > 0
        return False

    def set_gene(self, gene_name, *value_or_blank):
        '''put gene_name as a gene of self. It will be transmitted whenever self._new() is called.
        *value_or_blank: 0 args or 1 arg.
            0 --> ignore
            1 --> self.gene_name will be assigned to the value provided.

        Example:
            x.set_gene('_secret', 7)     # x._secret = 7; and tells _new to pass on _secret.
            y = x._new()
            y._secret
            >>> 7
        '''
        vob = value_or_blank
        assert len(vob) in (0, 1), 'self.set_gene() expected 1 or 2 arguments but got {}'.format(1+len(vob))
        genes = getattr(self, '_genes', set())
        genes.add(gene_name)
        setattr(self, '_genes', genes)
        if len(vob) == 1:
            value = vob[0]
            setattr(self, gene_name, value)

    _INIT_MODIFIERS = INIT_MODIFIERS.tracked_ops_property('_cached_init_modifiers',
        doc='''The attributes of self containing functions to run during __init__. List of strings.''')

    def __init__(self, *args, **kw):
        '''runs all funcs indicated by self._INIT_MODIFIERS.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        for attr in self._INIT_MODIFIERS:
            _self_init_modifier_attr = getattr(self, attr)
            _self_init_modifier_attr(*args, **kw)   # call this init modifier.

    # # # EQUALITY # # #
    def __eq__(self, b):
        '''True is sufficient to indicate self == b, but might not be necessary.
        For example, (7+x-7).__eq__(x) will return False,
        although (7+x-7).simplify().__eq__(x) == True.

        here, we check (in the order shown here):
            if b and self are the same object, return True. (This can save lots of time.)
            if self has an '_equals0' method and _equals0(b), return self._equals0()
            if b is not an instance of type(self), return False
                (implementation note: this check uses self._type_precludes_generic_equality,
                so that subclasses can provide a different method if desired.)
            
        if none of these conditions are met, raise NotImplementedError.

        Subclasses can utilize this check in their __eq__ via:
            super_eq = super().__eq__(b)
            if super_eq is not NotImplemented:
                return super_eq
            else:
                # <subclass's further checks to determine equality>
        '''
        if b is self:
            return True
        if hasattr(self, '_equals0') and _equals0(b):
            return self._equals0()
        if self._type_precludes_generic_equality(b):
            return False
        raise NotImplementedError

    def _type_precludes_generic_equality(self, b):
        '''returns whether type(b) prevents self == b, for generic b.
        The implementation here is just:
            return not isinstance(b, type(self))
        However, subclasses may wish to override this method with a different implementation.

        Special objects, e.g. 0, might equal self regardless of type.
        '''
        return not isinstance(b, type(self))

    # # # DISPLAY # # #
    def view(self, *args__str, **kw__str):
        '''does view(self)'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return view(self, *args__str, **kw__str)

    def _ipython_display_(self):
        '''this is the method jupyter notebook calls to figure out how to show self.'''
        return self.view()

    def __repr__(self, **kw):
        '''returns <type(self)>(<repr_contents>)
        e.g. Symbol('x', subscripts=[1]), or Product(Symbol('x'), 7)
        '''
        repr_contents = ', '.join(self._repr_contents(**kw))
        return f'{type(self).__name__}({repr_contents})'

    def _repr_contents(self, **kw):
        '''list of contents to put as comma-separated list into repr of self.'''
        raise NotImplementedError(f'{type(self)}._repr_contents()')

    printsize = property(lambda self: len(str(self)), doc='''length of str(self)''')

    # # # NUMPY INTERACTIONS # # #
    __array_ufunc__ = None   # tell numpy to not handle arithmetic interactions.

    # # # CLASSIFICATION # # #
    def is_constant(self):
        '''returns False, since SymbolicObjects are non-constant, by default.
        Subclasses may override this method to implement different behavior.
        '''
        return False

    def is_number(self):
        '''returns False, since SymbolicObjects are not numbers by default.
        Subclasses may override this method to implement different behavior.
        '''
        return False

    # # # INSPECTION # # #
    @property
    def layers(self):
        '''return number of layers in self.
        non-iterable --> layers = 1
        iterable --> layers = 1+max(layers(term) for term in self)
        '''
        return layers(self)

    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def symdeplayers(self):
        '''return number of layers in self which depend on a SymbolicObject.
        non-iterable --> symdeplayers = 1
        iterable --> symdeplayers = 1 + max(symdeplayers(term) for term in self)
        '''
        try:
            iterable = iter(self)
        except TypeError:
            return 1
        else:
            return 1 + max(symdeplayers(term) for term in iterable)

    # # # CONVENIENCE # # #
    @property
    def type(self):
        '''returns type(self). For convenience. Sometimes it's just easier to write self.type.'''
        return type(self)