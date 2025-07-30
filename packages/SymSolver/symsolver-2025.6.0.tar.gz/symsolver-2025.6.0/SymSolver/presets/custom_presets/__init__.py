"""
Package Purpose: preset SymbolicObjects defined by the user.
To define your own presets, follow the format in custom_presets_example.py.

Debugging tips:
    - did you restart the kernel after changing the file? (or, use SymSolver.reload())
    - did you install SymSolver in "editable" mode? (pip install -e .)

This file:
Imports ALL .py files appearing inside this folder.
"""
import os
from ...tools import import_relative

_pylist = [_f for _f in os.listdir(os.path.dirname(__file__))
           if _f.endswith('.py') and _f != '__init__.py']
for _f in _pylist:
    _importname = f'.{_f[:-3]}'  # [:-3] to remove '.py'
    import_relative(_importname, globals())
