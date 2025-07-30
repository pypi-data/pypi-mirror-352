"""
File Purpose: "custom presets example" vars & equations

These are:
    - not required for full functionality in other parts of SymSolver
    - (some of) my custom presets
    - related to [topic] in particular

This example file sets up code to define symbols Q and Q1,
    when load_presets('CUSTOM_EXAMPLE') is called
    (or when load_presets() is called, i.e. "load all presets").

By default, SymSolver imports this file but LOAD_EXAMPLE=False
    you can set LOAD_EXAMPLE = True in this file then reload it
    (import after restarting kernel, or SymSolver.reload()) to try it.

--- To define your own presets, make a new .py file like this one, in this folder. ---
    remove the LOAD_EXAMPLE=False and if LOAD_EXAMPLE lines
    (and de-indent the code inside the "if LOAD_EXAMPLE" block).
    the __init__.py in this folder will automatically import your custom .py files.

Debugging tips:
    - did you restart the kernel after changing the file? (or, use SymSolver.reload())
    - did you install SymSolver in "editable" mode? (pip install -e .)

For more examples, see the other presets_..._.py files in SymSolver.
"""

from ..presets_tools import Presets
from ...initializers import INITIALIZERS

LOAD_EXAMPLE = False

if LOAD_EXAMPLE:
    PS = Presets('CUSTOM_EXAMPLE', 'CUSTOM')   # you can put any strings here; used by load_presets.
    @PS.creator
    def define_presets():
        '''define presets for the custom_presets_example module'''

        # [TODO] define some custom vars here. e.g.:
        Q = INITIALIZERS.symbol('Q')
        Q1 = INITIALIZERS.symbol('Q', ['1'])

        # [TODO] use PS.set() to set the presets. e.g.:
        PS.set(('Q', 'Q1'), locals())   # add to the presets dictionary
