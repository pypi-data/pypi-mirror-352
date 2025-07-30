"""
File Purpose: tools for simple properties
"""
import weakref

from .sentinels import NO_VALUE
from .pytools import format_docstring


''' --------------------- Alias an attribute --------------------- '''

def alias(attribute_name, doc=None):
    '''returns a property which is an alias to attribute_name.
    if doc is None, use doc=f'alias to {attribute_name}'.
    '''
    return property(lambda self: getattr(self, attribute_name),
                    lambda self, value: setattr(self, attribute_name, value),
                    doc=f'''alias to {attribute_name}''' if doc is None else doc)

def alias_to_result_of(attribute_name, doc=None):
    '''returns a property which is an alias to the result of calling attribute_name.
    if doc is None, use doc=f'alias to {attribute_name}()'.
    '''
    return property(lambda self: getattr(self, attribute_name)(),
                    doc=f'''alias to {attribute_name}()''' if doc is None else doc)

def alias_child(child_name, attribute_name, doc=None, *, if_no_child=NO_VALUE):
    '''returns a property which is an alias to obj.child_name.attribute_name.
    if doc is None, use doc=f'alias to self.{child_name}.{attribute_name}'.
    includes getter AND setter methods.

    if_no_child: NO_VALUE or any object
        if provided (not NO_VALUE), return this instead if child is None or doesn't exist.
    '''
    if if_no_child is NO_VALUE:
        def getter(self):
            return getattr(getattr(self, child_name), attribute_name)
    else:
        def getter(self):
            child = getattr(self, child_name, None)
            return if_no_child if child is None else getattr(child, attribute_name)
    def setter(self, value):
        setattr(getattr(self, child_name), attribute_name, value)
    if doc is None:
        doc = f'''alias to self.{child_name}.{attribute_name}'''
    return property(getter, setter, doc)

def alias_in(cls, attr, new_attr):
    '''sets cls.new_attr to be an alias for cls.attr.'''
    setattr(cls, new_attr, alias(attr))


''' --------------------- Other properties --------------------- '''

def simple_property(internal_name, *, doc=None, default=NO_VALUE, setable=True, delable=True):
    '''return a property with a setter and getter method for internal_name.
    if 'default' provided (i.e., not NO_VALUE):
        - getter will have this default, if attr has not been set.
    setable: bool
        whether to allow this attribute to be set (i.e., define fset.)
    delable: bool
        whether to allow this attribute to be set (i.e., define fdel.)
    '''
    if default is NO_VALUE:
        def getter(self):
            return getattr(self, internal_name)
    else:
        def getter(self):
            return getattr(self, internal_name, default)
    if setable:
        def setter(self, value):
            setattr(self, internal_name, value)
    else:
        setter = None
    if delable:
        def deleter(self):
            delattr(self, internal_name)
    else:
        deleter = None
    return property(getter, setter, deleter, doc=doc)

def simple_setdefault_property(internal_name, setdefault, *, doc=None):
    '''return a property with a setter and getter method for internal_name.
    setdefault: callable of 0 arguments
        called to set value of internal_name when getter is called but internal_name is not set.
        E.g., setdefault = lambda: dict().

    Benefits include:
        - no need to initialize internal_name in __init__.
        - if this property is never used, setdefault is never called.
        - if internal_name's value is deleted, and this property is accessed later,
            setdefault will be called, instead of causing a crash.
        - the value can be adjusted after it is set, and the getter will give the new value.
            E.g. setdefault = lambda: dict(); self.attr['a'] = 5; self.attr --> dict(a=5);
            c.f. property(lambda: dict()); self.attr['a'] = 5; self.attr --> dict()
    '''
    def getter(self):
        try:
            return getattr(self, internal_name)
        except AttributeError:
            result = setdefault()
            setattr(self, internal_name, result)
            return result
    def setter(self, value):
        setattr(self, internal_name, value)
    def deleter(self):
        delattr(self, internal_name)
    return property(getter, setter, deleter, doc=doc)

def simple_setdefaultvia_property(internal_name, setdefaultvia, *, doc=None):
    '''return a property with a setter and getter method for internal_name.
    setdefaultvia: str
        self.internal_name = self.setdefaultvia(), when setting value of internal_name.
            This occurs whenever when getter is called but internal_name is not set.

    similar to simple_setdefault_property, except here the default is set via a method call,
        from a method in the object where this property is defined,
        instead of via a setdefault callable of 0 arguments.
    '''
    def getter(self):
        try:
            return getattr(self, internal_name)
        except AttributeError:
            pass  # handled below, to avoid stacked error message in case setdefaultvia fails.
        setdefault = getattr(self, setdefaultvia)
        result = setdefault()
        setattr(self, internal_name, result)
        return result
    def setter(self, value):
        setattr(self, internal_name, value)
    def deleter(self):
        delattr(self, internal_name)
    return property(getter, setter, deleter, doc=doc)


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