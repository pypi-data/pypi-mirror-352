"""
File Purpose: control creation of objects from calling classes.

E.g.:
    - metaclass where __new__ doesn't call __init__ unless it is object.__new__
    - class which follows the singleton pattern
"""
from .caching import caching_attr_simple
from ...defaults import DEFAULTS

''' --------------------- Metaclass which prevents __init__ --------------------- '''
# For most purposes it is easier and probably better design principle to not use this;
# instead just request users create instances via another function,
# e.g. "use product(*args) to create a Product instance, rather than Product(*args)".

class CustomNewDoesntInit(type):
    '''metaclass which changes behavior of class instantiation of inheritors.
    inheritors will only call __init__ automatically if their __new__ has not been overwritten.
        (i.e. if their __new__ is equal to object.__new__, then still call __init__.
        Otherwise, only call __init__ if told to do so.)
    use class MyClass(metaclass=CustomNewDoesntInit) to inherit this special power.
    '''
    def __call__(cls, *args, **kw):
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if cls.__new__ == object.__new__:
            x = object.__new__(cls)
            x.__init__(*args, **kw)
        else:
            x = cls.__new__(cls, *args, **kw)
        return x


''' --------------------- Singleton --------------------- '''

class Singleton(object, metaclass=CustomNewDoesntInit):
    '''class which returns old instance instead of making new one;
    there is only ever 0 or 1 instance of this class.

    the instance will be stored in cls.__it__, if it exists.
    (get it? "it", because it is the only one... like, this is it!)
    
    implementation note: only checks cls.__dict__ for "__it__",
    rather than attempting to get cls.__it__, in case cls inherits from a Singleton.
    E.g. for class Foo(Singleton): ...; class Bar(Foo): ...;
        there can be one instance of Foo and also one instance of Bar.
    '''
    def __new__(cls, *args, **kw):
        it = cls.__dict__.get('__it__', None)
        if it is None:  # create the first (and only) instance
            it = object.__new__(cls)
            it.__init__(*args, **kw)
            cls.__it__ = it
        return it  # note: thanks to CustomNewDoesntInit, this does not call it.__init__.

    @caching_attr_simple
    def __hash__(self):
        return hash((type(self), id(self)))
