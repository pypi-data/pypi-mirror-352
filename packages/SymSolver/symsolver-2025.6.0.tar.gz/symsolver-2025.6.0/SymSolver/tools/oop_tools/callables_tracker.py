"""
File Purpose: CallablesTracker

dict-like object which tracks callables.
"""
import inspect

class CallablesTracker(dict):
    '''dict-like object which tracks callables.

    Also, ensures keys match with callable.name.
    E.g. self.append(product) --> self['product'] = product.

    Also allows for getattr(name), e.g. self.product == self['product'].
    '''
    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}(keys={self.keys()})'

    # # # ESSENTIAL METHODS # # #
    def __setitem__(self, name, f):
        assert f.__name__ == name, f'key must match f.__name__ but got {repr(name)} and {repr(f.__name__)}'
        super().__setitem__(name, f)
        setattr(self, name, f)

    def append(self, f):
        '''puts callable f into self, with key==f.__name__.'''
        self[f.__name__] = f

    def tracking_decorator(self):
        '''returns a decorator which puts f into self, then returns f, unchanged.'''
        def _tracking_decorator(f):
            self.append(f)
            return f
        return _tracking_decorator

    tracking = property(lambda self: self.tracking_decorator(),
                        doc='''decorator which puts f into self, then returns f, unchanged.''')

    # # # CONVENIENT METHODS # # #
    def get(self, *fnames, _list_if_one=False):
        '''returns [self[fname] for fname in fnames].
        if only 1 fname, return self[fname] instead (by default).
        if _list_if_one and only 1 fname, return [self[fname]].
        '''
        result = [self[fname] for fname in fnames]
        if len(fnames) == 1 and not _list_if_one:
            return result[0]
        else:
            return result

    def modules(self, as_names=True, max_depth=None):
        '''{callable name: module where callable was defined} for callables stored here.
        if as_names, use module.__name__ instead of module.
        max_depth: None or int, default 2
            if as_names, and max_depth is provided, cut module names off before they reach this many '.'s.
            For example, max_depth=2 --> 'SymSolver.basics.sum' becomes 'SymSolver.basics' instead.
        '''
        result = {name: inspect.getmodule(f) for name, f in self.items()}
        if as_names:
            result = {name: _module_name_with_max_depth(module.__name__, max_depth) for name, module in result.items()}
        return result

    def from_modules(self, *modules, as_names=True, max_depth=2, sort=True):
        '''{module name: list of callables' names in self defined in module} for these modules.
        modules: modules or strings
            provide the modules to get callables from. Strings if as_names, modules otherwise.
            if empty, use all modules in self.
        as_names: bool, default True
            if False, list modules and callables instead of module names and callables' names.
        max_depth: None or int, default 2
            if as_names, and max_depth is provided, cut module names off before they reach this many '.'s.
            For example, max_depth=2 --> 'SymSolver.basics.sum' becomes 'SymSolver.basics' instead.
        sort: bool, default True
            whether to sort the final lists, and also the keys of the result.
        '''
        fname_to_module = self.modules(as_names=as_names, max_depth=max_depth)
        if len(modules)==0:
            modules = set(fname_to_module.values())
            if sort:
                modules = sorted(modules)
        result = {module: [] for module in modules}
        for name, f in self.items():
            module = fname_to_module[name]
            if module in modules:
                if as_names:
                    result[module].append(name)
                else:
                    result[module].append(f)
        if sort:
            result = {module: sorted(callables) for module, callables in result.items()}
        return result

def _module_name_with_max_depth(module_name, max_depth):
    '''return module name with at most this many "layers" of module in it.
    '.'.join(module_name.split('.')[:max_depth])
    max_depth can be None or int. None --> result equals module_name.
    For example, max_depth=2 means 'SymSolver.basics.sum' becomes 'SymSolver.basics' instead.
    '''
    return '.'.join(module_name.split('.')[:max_depth])
