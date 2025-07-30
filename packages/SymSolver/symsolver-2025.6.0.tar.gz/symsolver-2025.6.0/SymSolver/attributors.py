"""
File Purpose: ATTRIBUTORS

ATTRIBUTORS provides the convenience functions throughout SymSolver.
"""
from .tools import CallablesTracker

class _Attributors(CallablesTracker):
    """holds the attributor functions throughout SymSolver.
    Use the instance ATTRIBUTORS, instead of calling _Attributors() again.

    These are the functions which tend to look like:
    def foo(x):
        '''returns x.foo() if possible, else <some default value>'''
        try:
            return x.foo()
        except AttributeError:
            return default_value

    They are convenient because you can call them on any object,
    but can also let each object implement its own version of the function if desired.

    For example, the get_factors() function from basics/basics_tools.py
        returns x.get_factors() if possible, else [x].
        Meanwhile Product.get_factors() returns a list of the product's factors.
    
    Functions can be accessed via indexing or as attributes,
        e.g. ATTRIBUTORS['get_factors'] or ATTRIBUTORS.get_factors.
    """
    def put_into(self, locals_, *keys):
        '''update locals_ using self. locals_ should be a dict, possibly locals().
        keys: iterable
            only update locals_ using the keys indicated here
            if empty list, use all the keys in self.
        '''
        if len(keys)==0:
            locals_.update(self)
        else:
            these_keys_only = {key: self[key] for key in keys}
            locals_.update(these_keys_only)

ATTRIBUTORS = _Attributors()
attributor = ATTRIBUTORS.tracking   # decorator which returns f but first puts f in list of attributors.
