"""
File Purpose: ImportFailed

put this error when an import fails.
This is a separate file from imports_reload.py to mitigate cyclic imports.
"""

import importlib
import inspect
import sys
import warnings

from ..errors import ImportFailedError
from ..defaults import DEFAULTS


''' --------------------- reloading --------------------- '''

def enable_reload(package='SymSolver'):
    '''smashes the import cache for the provided package.
    All modules starting with this name will be removed from sys.modules.
    This does not actually reload any modules.
    However, it means the next time import is called for those modules, they will be reloaded.
    returns tuple listing of all names of affected modules.

    package: str or module
        the package for which to enable reload. if module, use package.__name__.
    '''
    if inspect.ismodule(package):
        package = package.__name__
    l = tuple(key for key in sys.modules.keys() if key.startswith(package))
    for key in l:
        del sys.modules[key]
    return l

def reload(package='SymSolver', return_affected=False):
    '''reloads the provided package.
    Equivalent to enable_reload(package); import package.

    returns the reloaded package.
    if return_affected also return a list of all affected package names.

    NOTE: this reloads package but doesn't do it "in-place" (i.e. doesn't change the package variable).
    For example:
        import SymSolver as ss
        import mypackage as p0
        p1 = ss.reload(p0)
        p1 is p0 --> False, because p0 points to the pre-reload version of the package.

    Thus, to use this method, you should instead assign the package to the result, for example:
        import SymSolver as ss
        ss = ss.reload()

        # or, to reload a different package
        import mypackage as p
        p = ss.reload(p)

    package: str or module
        the package to reload. if module, use package.__name__.
    '''
    if inspect.ismodule(package):
        package = package.__name__
    affected = enable_reload(package)
    result = importlib.import_module(package)
    return (result, affected) if return_affected else result


''' --------------------- relative loading inside package --------------------- '''

def import_relative(name, globals):
    '''import a module relative to the caller's package; caller must provide globals().
    Examples: inside SymSolver.tools.arrays,
        import_relative('.numbers', globals()) <- equivalent -> import SymSolver.tools.numbers
        import_relative('..errors', globals()) <- equivalent -> import SymSolver.errors
    '''
    package = globals['__package__']
    return importlib.import_module(name, package=package)


''' --------------------- import failure handling --------------------- '''

class ImportFailed():
    '''set modules which fail to import to be instances of this class;
    initialize with modulename, additional_error_message.
    when attempting to call or access any attribute of the ImportFailed object,
        raises ImportFailedError('. '.join(modulename, additional_error_message)).
        If err is provided, also include err in the error message.
    Also, if DEFAULTS.IMPORT_FAILURE_WARNINGS, make warning immediately when initialized.

    Example:
    try:
      import zarr
    except ImportError as err:
      zarr = ImportFailed('zarr', 'This module is required for compressing data.', err=err)

    zarr.load(...)   # << attempt to use zarr
    # if zarr was imported successfully, it will work fine.
    # if zarr failed to import, this error will be raised:
         ImportFailedError: zarr. This module is required for compressing data.
         The original error was: ModuleNotFoundError("No module named 'zarr'")
    '''
    def __init__(self, modulename, additional_error_message='', *, err=None):
        self.modulename = modulename
        self.additional_error_message = additional_error_message
        self.err = err
        if DEFAULTS.IMPORT_FAILURE_WARNINGS:
            warnings.warn(f'Failed to import module {self.error_message()}')

    def error_message(self):
        str_add = str(self.additional_error_message)
        if len(str_add) > 0:
            str_add = '. ' + str_add
        result = self.modulename + str_add
        if self.err is not None:
            result += f'\nThe original error was: {self.err!r}'
        return result

    def __getattr__(self, attr):
        '''tells how to do self.attr when it would otherwise fail.
        Here, raise ImportFailedError.
        '''
        raise ImportFailedError(self.error_message())

    def __call__(self, *args__None, **kw__None):
        '''tells how to call self, e.g. self(...). Here, raise ImportFailedError.'''
        raise ImportFailedError(self.error_message())

    def __repr__(self):
        return f'{type(self).__name__}({repr(self.modulename)})'