"""
File Purpose: Miscellaneous quality-of-life functions for Object Oriented Programming tasks.
"""

import functools

from ...defaults import DEFAULTS, OnOffSwitch


''' --------------------- Apply if attribute exists --------------------- '''

def apply(x, fstr, *args, **kwargs):
    '''return x.fstr(*args, **kwargs), or x if x doesn't have an 'fstr' attribute.'''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    # pop default if it was provided.
    doing_default = 'default' in kwargs
    if doing_default:
        default = kwargs.pop('default')
    # call x.fstr(*args, **kwargs)   # (kwargs with 'default' popped.)
    if hasattr(x, fstr):
        return getattr(x, fstr)(*args, **kwargs)
    elif doing_default:
        return default
    else:
        return x


''' --------------------- Maintain Attributes (context manager) --------------------- '''

def maintain_attrs(*attrs):
    '''return decorator which restores attrs of obj after running function.
    It is assumed that obj is the first arg of function.
    '''
    def attr_restorer(f):
        @functools.wraps(f)
        def f_but_maintain_attrs(obj, *args, **kwargs):
            '''f but attrs are maintained.'''
            __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
            with MaintainingAttrs(obj, *attrs):
                return f(obj, *args, **kwargs)
        return f_but_maintain_attrs
    return attr_restorer

class MaintainingAttrs():
    '''context manager which restores attrs of obj to their original values, upon exit.'''
    def __init__(self, obj, *attrs):
        self.obj = obj
        self.attrs = attrs

    def __enter__(self):
        self.memory = dict()
        for attr in self.attrs:
            if hasattr(self.obj, attr):
                self.memory[attr] = getattr(self.obj, attr)

    def __exit__(self, exc_type, exc_value, traceback):
        for attr, val in self.memory.items():
            setattr(self.obj, attr, val)


class SettingAttrs():
    '''context manager which sets attrs of obj upon entry, then restores to original values upon exit.
    note: any originally-unset attrs will be deleted upon exit.
    '''
    def __init__(self, obj, **attrs_and_values):
        self.obj = obj
        self.attrs_and_values = attrs_and_values

    def __enter__(self):
        self.memory = dict()
        for attr, val in self.attrs_and_values.items():
            # remember old obj.attr
            try:
                self.memory[attr] = getattr(self.obj, attr)
            except AttributeError:
                pass  # << obj.attr doesn't exist, so don't assign memory[attr].
            # set new obj.attr
            try:
                setattr(self.obj, attr, val)
            except Exception:  # failed to set attr... restore all old attrs then crash.
                self.__exit__()
                raise

    def __exit__(self, *_args, **_kw):
        not_in_memory = self.attrs_and_values.copy()
        for attr, val in self.memory.items():
            setattr(self.obj, attr, val)
            del not_in_memory[attr]
        for attr in not_in_memory.keys():
            try:
                delattr(self.obj, attr)
            except AttributeError:
                pass  # << that's fine; we just needed to ensure attr doesn't exist.

def with_attrs(**attrs_and_values):
    '''return decorator which sets attrs of object before running function then restores them after.
    It is assumed that obj is the first arg of function.
    '''
    def attr_setter_then_restorer(f):
        @functools.wraps(f)
        def f_but_set_then_restore_attrs(obj, *args, **kwargs):
            '''f but attrs are set beforehand then restored afterward.'''
            __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
            with SettingAttrs(obj, **attrs_and_values):
                return f(obj, *args, **kwargs)
        return f_but_set_then_restore_attrs
    return attr_setter_then_restorer


''' --------------------- enabled() and disabled() for OnOffSwitch --------------------- '''
# note: not using @binding from binding.py since that module imports this file.

def enabled(self):
    '''returns a context manager that sets self.state=True upon entry; restore original state upon exit.'''
    return SettingAttrs(self, state=True)

def disabled(self):
    '''returns a context manager that sets self.state=False upon entry; restore original state upon exit.'''
    return SettingAttrs(self, state=False)

OnOffSwitch.enabled = enabled
OnOffSwitch.disabled = disabled

del enabled   # << remove from local namespace.
del disabled  # << remove from local namespace.