"""
File Purpose: INITIALIZERS

INITIALIZERS provides the functions used to initialize different operations,
when sometimes initializing the operation will actually lead to a different result.
    For example, product(*args) returns a Product object when there are 2 or more args,
    but product(arg) returns arg, while product() returns 1.

These functions are not defined inside this file in order to avoid cyclic dependency.
    For example, product.py defines product() but also needs to know the other initializers,
    such as sum. E.g. Product(x,y)+z --> sum(Product(x,y),z).
Instead, other modules should import this one and put their initializers in the INITIALIZERS object.
"""
from .tools import CallablesTracker

class _Initializers(CallablesTracker):
    '''holds the functions for initializing different objects throughout SymSolver.
    For example, sum and product.
    
    Those functions should be attached to the class instance INITIALIZERS after it is created.
    They can be accessed via indexing or as attributes, e.g. INITIALIZERS['sum'] or INITIALIZERS.sum.
    '''
    pass    

INITIALIZERS = _Initializers()
initializer = INITIALIZERS.tracking   # decorator which returns f but first puts f in list of initializers.

def initializer_for(target):
    '''factory which returns decorator which returns f but first sets target.initializer.
    uses target.initializer = property(lambda self: f, doc="function used to create a new instance of self")'''
    def _initializer_for_target(f):
        target.initializer = property(lambda self: f, doc='''function used to create a new instance of self''')
        return initializer(f)
    return _initializer_for_target
