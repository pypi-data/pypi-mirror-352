"""
File Purpose: logging, recording info about state of code, etc.

For reproducibility in the future.
E.g., with results, also save git hash for current version of the code.
"""

import os
import subprocess

from .sentinels import NO_VALUE

def git_hash_local(*, default=NO_VALUE):
    '''returns the hash for current git HEAD within the local directory

    default: any object
        if not NO_VALUE, and can't get hash (but filepath does exist),
        return default & print message, instead of crashing if can't get hash.
    '''
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    except subprocess.CalledProcessError:
        if default is not NO_VALUE:
            print(f'(failed to get git hash; returning default. At dir={repr(os.getcwd())})')
            return default
        raise

def git_hash(module_or_path='.', *, default=NO_VALUE):
    '''returns the hash for current git HEAD at the provided module or path.
    if string, treat it as a path; if module object, use path to module.__file__.
    module_or_path: string or module object, default '.'
        place to get git hash from.
        string --> path=module_or_path. If not a directory, also try os.path.dirname(path)
        module --> module=module_or_path. path=os.path.dirname(module.__file__)
    default: any object
        if provided, and can't get hash, return default & print message.
    '''
    try:
        if isinstance(module_or_path, str):
            path = module_or_path
        else:
            module = module_or_path
            path = module.__file__
        if not os.path.isdir(path):
            path = os.path.abspath(path)
            dirpath = os.path.dirname(path)
            if not os.path.isdir(dirpath):
                raise FileNotFoundError(f'{repr(path)} (not an existing directory). (\nalso {repr(dirpath)})')
            path = dirpath
        try:
            cwd0 = os.getcwd()
            os.chdir(path)
            return git_hash_local(default=default)
        finally:
            os.chdir(cwd0)
    except Exception:
        if default is not NO_VALUE:
            print(f'(failed to get git hash; returning default. For input={repr(module_or_path)})')
            return default
        raise

def git_hash_here(globals_):
    '''returns git hash for the __file__ in the namespace where this function is called.'''
    return git_hash(globals_['__file__'])

def git_hash_SymSolver():
    '''returns the hash for current git HEAD in SymSolver'''
    return git_hash_here(globals())
