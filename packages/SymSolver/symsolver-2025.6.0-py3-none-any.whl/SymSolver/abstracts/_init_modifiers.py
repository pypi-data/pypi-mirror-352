"""
File Purpose: init modifiers for SymbolicObject

The idea is that some modules want to modify __init__,
e.g. to add sanity checks, like: "ensure all terms in a sum are vectors or all are not vectors".

One (not used) option is to make all those modules redefine the __init__ function(s) they wish to modify.
That can get rather confusing as soon as multiple modules wish to redefine the __init__;
since then each one needs to modify the prior one's already-modified __init__, to keep all functionality.

Another option (the one chosen here) is to provide a place to put modifiers which will be called.
In particular, the SymbolicObject.__init__(self) will call all funcs indicated by in self._INIT_MODIFIERS.
"""

from ..tools import (
    Binding,
    Opname_to_OpClassMeta__Tracker,
)

# # # ALL INIT MODIFIERS DEFINED THROUGHOUT SYMSOLVER # # #
INIT_MODIFIERS = Opname_to_OpClassMeta__Tracker()

def init_modifier(target, order=0, doc=None):
    '''returns a function decorator deco(f) which adds f to INIT_MODIFIERS and binds f to target.

    target: type
        the class for which f is an init modifier
        f will be bound to target, at attribute name f.__name__.
    order: number, default 0
        relative order for applying f to target. (lower --> apply sooner)
        relative compared to other ops tracked in INIT_MODIFIERS for target (or any of target's parents)
        in case of tie, all tied funcs might be applied in any order.
    doc: None or string
        more notes/info associated with this tracking / the function being decorated.
        note: currently, not much implemented to interact with doc.
    alias: None or string
        [TODO?][not yet implemented]
        if provided, tell INIT_MODIFIERS that this is an alias of f,
        and also sets target.(alias) to point to target.(f.__name__).
    '''
    return INIT_MODIFIERS.track_and_bind_op(target=target, order=order, doc=doc)
