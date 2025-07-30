"""
File Purpose: tools whose main purpose is to work with implementation details of Python.

E.g. manipulate function docstrings
"""
import collections
import inspect
import weakref

from ..errors import InputMissingError
from ..defaults import DEFAULTS

def format_docstring(*args__format, sub_indent=None, sub_ntab=None, **kw__format):
    '''returns a decorator of f which returns f, after updating f.__doc__ via f.__doc__.format(...)
    sub_indent: None or str
        if provided, indent all lines (after the first line) for each multiline string, before formatting.
    sub_ntab: int
        if provided when sub_indent is None, use sub_indent = sub_ntab * DEFAULTS.STRINGREP_TAB.
    '''
    if sub_indent is None and sub_ntab is not None:
        sub_indent = DEFAULTS.STRINGREP_TAB * sub_ntab
    if sub_indent is not None:
        args__format = [str(arg).replace('\n', '\n'+sub_indent) for arg in args__format]
        kw__format = {key: str(val).replace('\n', '\n'+sub_indent) for key, val in kw__format.items()}
    def return_f_after_formatting_docstring(f):
        f.__doc__ = f.__doc__.format(*args__format, **kw__format)
        return f
    return return_f_after_formatting_docstring

def value_from_aliases(*aliases):
    '''returns value from aliases.
    Precisely one of the aliases must be non-None, else raises InputMissingError.
    '''
    not_nones = [(a is not None) for a in aliases]
    Nvals     = sum(not_nones)
    if Nvals == 1:
        return aliases[next(i for (i, not_none) in enumerate(not_nones) if not_none)]
    else:
        raise InputMissingError(f'Expected one non-None value, but got {Nvals}!')

def assert_values_provided(**kw):
    '''raise InputMissingError if any of the kwargs' values are None.'''
    for key, val in kw.items():
        if val is None:
            raise InputMissingError(f'Must provide a non-None value for kwarg {repr(key)}.')

def printsource(obj):
    '''prints source code for object (e.g. call this on a function or class).'''
    print(inspect.getsource(obj))

def inputs_as_dict(callable_, *args, **kw):
    '''returns dict of all inputs to callable_ based on its signature and args & kwargs.
    raises TypeError if inputs would be invalid for callable_.
    Example:
        def foo(a, b=2, c=3, * d=4, e=5): pass
        inputs_as_dict(foo, 9, d=7, c=8) gives {'a':9, 'b':2, 'c':8, 'd':7, 'e':5}
        inputs_as_dict(foo, z=6) raises TypeError since foo doesn't accept kwarg 'z'.
    '''
    _iad_for_callable = _inputs_as_dict__maker(callable_)
    return _iad_for_callable(*args, **kw)

def _inputs_as_dict__maker(callable_):
    '''returns a function which returns dict of all inputs all inputs to callable_.'''
    f_signature = inspect.signature(callable_)
    def _inputs_as_dict(*args, **kw):
        '''returns dict of inputs as they would be named inside callable_'s namespace.
        includes params not input directly here, but defined by default for callable_.
        '''
        bound_args = f_signature.bind(*args, **kw)  # << will raise TypeError if inputs invalid for f.
        bound_args.apply_defaults()  # << include defaults
        params_now = bound_args.arguments  # << dict of {input name: value}.
        return params_now
    return _inputs_as_dict

def get_locals_up(up=1):
    '''returns locals() for the namespace <up> layers up from *where get_locals_up* is called.
    Examples:
        get_locals_up(0) == locals().
        def foo():
            return get_locals_up(1)
        foo() == locals()

    note: it may be better practice to require inputting locals() to your function, rather than using get_locals_up(1).
    Entering locals() directly makes it less surprising when your function interacts with that namespace.
    '''
    return inspect.stack()[up+1].frame.f_locals

def _identity_function(y):
    '''returns y, unchanged. Equivalent to lambda y: y'''
    return y

def documented_namedtuple(clsname, fields, clsdoc, *, _defaults=None, _module=None, **attrdocs):
    '''namedtuple with documentation attached to the class and the attributes.
    '_defaults' & '_module' go directly to collections.namedtuple's 'defaults' and 'module'

    Example:
        [In] MyTupleCls = documented_namedtuple('MyTupleClass', ('a', 'b'), 'stores a and b',
                                                a='doc for "a" here', b='doc for "b" here')
        [In] help(MyTupleCls)
            Help on class MyTupleClass in module SymSolver.tools.pytools:

            class MyTupleClass(builtins.tuple)
             |  MyTupleClass(a, b)
             |  
             |  stores a and b
             |  
             |  Info stored in attributes:
             |      'a': doc for "a" here
             |      'b': doc for "b" here
             |  
            ...

        [In] MyTupleCls.a
        [Out] _tuplegetter(0, 'doc for "a" here')

        [In] mytuple = MyTupleCls(7, 8);   mytuple  # show mytuple
        [Out] MyTupleClass(a=7, b=8)

        [In] mytuple[0], mytuple.a, mytuple[1], mytuple.b
        [Out] (7, 7, 8, 8)

    Note: to say "Help on class MyTupleClass in module module.where.MyTupleClass.was.defined:" instead,
        enter the module where MyTupleClass is defined, when defining the class.
        E.g. MyTupleCls = documented_namedtuple(..., _module=current_module)
        One way to get current module is by defining a function and getting its module;
            inline, this could be written as: (lambda: None).__module__
    '''
    cls = collections.namedtuple(clsname, fields, defaults=_defaults, module=_module)
    # attach docs for attrs #
    for attr, doc in attrdocs.items():
        getattr(cls, attr).__doc__ = doc
    # attach docs to cls -- including info about attrs.#
    if len(attrdocs) == 0:
        attdoc = ''
    else:
        TAB = ' '*4
        attrs_docstring = '\n'.join(f"{TAB}{TAB}'{attr}': {doc}" for attr, doc in attrdocs.items())
        attdoc = f'\n\n{TAB}Info stored in attributes:\n{attrs_docstring}'
    cls.__doc__ = clsdoc + attdoc
    return cls

def weakref_property_simple(internal_attr, doc=None):
    '''defines a property which behaves like the value it contains, but is actually a weakref.
    stores internally at internal_attr. Also set self.{internal_attr}_is_weakref = True.
    Setting the value actually creates a weakref. Getting the value calls the weakref.
    Note: if failing to create weakref due to TypeError,
        (e.g. "TypeError: cannot create weak reference to 'int' object")
        then just store the value itself. Also set self.{internal_attr}_is_weakref = False.
    '''
    internal_attr_is_weakref = f'{internal_attr}_is_weakref'
    @format_docstring(attr=internal_attr)
    def get_attr(self):
        '''gets self.{attr}(), or just self.{attr} if not self.{attr}_is_weakref.'''
        self_attr = getattr(self, internal_attr)
        if getattr(self, internal_attr_is_weakref):
            return self_attr()
        else:
            return self_attr

    @format_docstring(attr=internal_attr)
    def set_attr(self, val):
        '''sets self.{attr}'''
        try:
            result = weakref.ref(val)
        except TypeError:
            setattr(self, internal_attr_is_weakref, False)
            result = val
        else:
            setattr(self, internal_attr_is_weakref, True)
        setattr(self, internal_attr, result)

    @format_docstring(attr=internal_attr)
    def del_attr(self):
        '''deletes self.{attr}'''
        delattr(self, internal_attr)
    
    return property(get_attr, set_attr, del_attr, doc)


class FormatDefaultDict(dict):
    '''dict, but returns '{key}' if key is missing.
    E.g. FormatDefaultDict(a=1)['a'] == 1
         FormatDefaultDict(a=1)['b'] == '{b}'
    useful in str.format_map.
    '''
    def __missing__(self, key):
        return '{' + str(key) + '}'

def format_(s, **kw):
    '''behaves like str.format, however missing keys are ignored instead of raising KeyError.'''
    return s.format_map(FormatDefaultDict(**kw))
