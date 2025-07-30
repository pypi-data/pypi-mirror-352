"""
File Purpose: defines "misc" preset values

These are:
    - not inherently related to physics
    - not required for full functionality in other parts of SymSolver
"""

from .presets_tools import Presets
from ..basics import symbols
from ..numbers import ImaginaryUnit


PS = Presets('MISC')
@PS.creator
def define_presets():
    '''define presets for the presets_misc module'''

    ''' --------------------- Misc --------------------- '''

    i = IUNIT    = ImaginaryUnit()
    e,           = symbols(('e',), constant=True)
    phi, theta   = symbols((r'\phi', r'\theta'))


    ''' --------------------- Set Presets --------------------- '''

    PS.set('i e IUNIT phi theta', locals())
