"""
File Purpose: defines "E & M" preset vars

These are:
    - inherently related to physics; specifically, the E & M equations
    - not required for full functionality in other parts of SymSolver
"""

from ..presets_tools import Presets
from ...basics import symbols
from ...units import UNI


PS = Presets('EM_VARS', 'EM', 'PHYSICS')
@PS.creator
def define_presets():
    '''define presets for the presets_em_vars module'''

    ''' --------------------- EM vars --------------------- '''

    E, B, J = symbols(('E', 'B', 'J'), vector=True)
    E.units_base = UNI.E
    B.units_base = UNI.B
    J.units_base = UNI.J

    ''' --------------------- Set Presets --------------------- '''

    PS.set('E B J', locals())
