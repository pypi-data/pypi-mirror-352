"""
File Purpose: AbstractOperator
(directly subclasses SymbolicObject)

Note: while technically operators might act on multiple arguments,
e.g. f(x,y,z), we do not allow for such operators in SymSovler (yet..?)
The implementation here is specifically for Operators which act on one argument.
"""

from ..abstracts import (
    AbstractOperation,
    SymbolicObject, IterableSymbolicObject,
    AssociativeObject, AssociativeOperation,
)
from ..errors import InputMissingError
from ..tools import (
    _repr, _str,
)


class AbstractOperator(AbstractOperation):
    '''SymbolicObject which behaves like an operator of one argument (e.g. f(x), x not yet specified).
    Has rules for:
        - acting like a function when called (e.g. self=f --> f(x) calls self on x)
        - function composition (e.g. AbstactOperators f, g; f(g) --> an abstract operator).
    and storing an operator which will be used when called.
    '''
    def __init__(self, f=None, frep=None, circ=True):
        r'''initialize AbstractOperator for operator f.
        f: callable or None
            callable --> the function self performs when called with args that are not AbstractOperators.
            None --> ignored here; self will call self._f instead.
                    Also Ensures self._f exists already, else raise InputMissingError
        frep: None or any other object, default None
            the object to use when representing self (e.g. during repr(self) or str(self)).
            None --> use f.
            str(self) will give str(frep).
            repr(self) will say, e.g. AbstractOperator(repr(frep)). (altered appropriately for subclasses.)
        circ: bool, default True
            whether to put a '\circ' after f before the next operation if composing with another operator.
            True --> e.g. f(g) --> f o g.    (This is the default)
            False --> e.g. f(g) --> fg.    (maybe useful e.g. if f is the 'nabla' operator or a 'multi-sum')
        '''
        if f is None:
            if not hasattr(self, '_f'):
                raise InputMissingError('Must specify f during __init__ or define _f for the class.')
        else:
            self._f = f
        self._frep = frep
        self._circ = circ
        SymbolicObject.__init__(self, f=f, frep=frep, circ=circ)

    f = property(lambda self: self._f,
            doc='''the function self performs when evaluated''')
    frep = property(lambda self: self._f if self._frep is None else self._frep,
            doc='''the object to use for representing self (e.g. during repr() or str())''')
    circ = property(lambda self: self._circ,
            doc=r'''whether to put a '\circ' after f if composed with another operator, e.g. f o g.''')

    def _repr_contents(self, **kw):
        '''returns contents to put inside 'AbstractOperator()' in repr for self.'''
        contents = [_repr(self.frep, **kw)]
        return contents

    def __str__(self, **kw):
        return _str(self.frep, **kw)

    def __call__(self, g):
        '''return self(g). result of calling operator on g.

        if g is an AbstractOperator:
            if type(g) is a "proper subclass" of type(self), return g.__rcall__(self),
            else, return a CompositeOperator: (f o g).
        Otherwise, evaluates the operation by calling self.f(g).
        '''
        if isinstance(g, AbstractOperator):
            # (note: "not isinstance(g, type(self))" is possible for a subclass which doesn't override __call__.)
            if isinstance(g, type(self)) and (type(g) != type(self)):  # type(g) is a "proper subclass" of type(self)
                return g.__rcall__(self)
            else:
                return CompositeOperator(self, g)
        else:
            return self.f(g)

    def __rcall__(self, g):
        '''return g(self). Result of calling operator g on self.'''
        raise NotImplementedError(f'{type(self).__name__}.__rcall__')

    def is_cascadify_subbable(self):
        '''return False, since AbstractOperators should not be replaced during cascadify, in general.'''
        # [TODO] move this function to a different file?
        return False


class CompositeOperator(AbstractOperator, AssociativeOperation):
    '''SymbolicObject which behaves like a composite operator e.g. (f o g).'''
    def __init__(self, *terms, **kw):
        '''terms are the AbstractOperators in self.'''
        if not all(isinstance(term, AbstractOperator) for term in terms):
            raise TypeError('expected only AbstractOperator instances.')
        AssociativeOperation.__init__(self, *terms, **kw)
        f = CompositeCallable(*terms, **kw)
        AbstractOperator.__init__(self, f)

    def __call__(self, g):
        '''return self(g). result of calling operator on g.

        if g is an AbstractOperator:
            if type(g)==type(self): 
                return a CompositeOperator: (self[0] o ... o self[-1] o g[0] o ... o g[-1]).
            else if type(g) is a "proper subclass" of type(self):
                let g handle this operation, via g.__rcall__(self).
            else:
                return a CompositeOperator: (self[0] o ... o self[-1] o g)
            
        Otherwise, evaluates the operation by calling self.f(g).
        '''
        if isinstance(g, AbstractOperator):
            if type(g) == type(self):
                return CompositeOperator(*self, *g)
            elif ifinstance(g, type(self)):  # then type(g) is a "proper subclass" of type(self)
                return g.__rcall__(self)     # so let g handle this operation instead.
            else:  # default, for all other kinds of AbstractOperator
                return self._new(*self, g)
        else:
            return self.f(g)

    def __rcall__(self, g):
        '''return g(self), where g is an AbstractOperator and type(self) is a "proper subclass" of type(g).
        this just returns a CompositeOperator: (g o self[0] o ... o self[-1])'''
        return self._new(g, *self)
        

class CompositeCallable(AssociativeObject):
    '''SymbolicObject to represent a callable composed of multiple callables, e.g. (f o g).
    The terms should be entered in composition order, e.g. (f, g, h) implies callable lambda x: f(g(h(x))).
    '''
    def __init__(self, *terms, **kw):
        '''terms must all be callable.'''
        if not all(callable(term) for term in terms):
            raise TypeError('expected only callable inputs, e.g. functions.')
        super().__init__(*terms, **kw)

    def __call__(self, *args, **kw__call):
        '''calls terms in self in appropriate order. sends **kw__call to every function.
        *args only go to the first-called function; then its result goes to the next, etc.
        appropriate order: "reverse", e.g. CompositeCallable(f, g, h)(x) --> f(g(h(x))).
        '''
        riter_terms = iter(self.terms[::-1])
        f_first = next(riter_terms)
        result = f_first(*args, **kw__call)
        for f in riter_terms:
            result = f(result, **kw__call)
        return result

    def __str__(self, **kw):
        result = ''
        i_final = len(self) - 1
        for i, f in enumerate(self):
            result += f'{_str(f, **kw) }'
            if f.circ and i < i_final:
                result += r'\circ '
        return result