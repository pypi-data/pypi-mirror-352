"""
File Purpose: defines "physical constants" preset variables

These are:
    - inherently related to physics; specifically, physical constant
    - not required for full functionality in other parts of SymSolver

[TODO] some way to "load in" the value
"""

from ..presets_tools import Presets
from ...basics import symbols
from ...initializers import INITIALIZERS
from ...units import UNI


PS = Presets('PHYSICAL_CONSTANTS', 'PHYSICS')
@PS.creator
def define_presets():
    '''define presets for the presets_physical_constants module'''

    ''' --------------------- Physical constants --------------------- '''

    eps0, mu0, c = symbols((r'\epsilon_0', r'\mu_0', 'c'), constant=True)
    kB, gamma    = symbols(['k_B', r'\gamma'], constant=True)

    eps0.units_base = UNI.eps0
    mu0.units_base = UNI.mu0
    c.units_base = UNI.u
    kB.units_base = UNI.joule / UNI.K
    gamma.units_base = UNI.id


    ''' --------------------- Physical constants - values --------------------- '''

    _locals = locals()

    # # SI VALUES # #
    const_si_dict = {
        'eps0': 8.85418781e-12,  # [F/m]
        'mu0' : 1.256637062e-6,  # [H/m]
        'c'   : 2.99792e8,       # [m/s]
        'kB'  : 1.380649e-23,    # [m^2 kg s^-2 K^-1]
        'gamma': 5/3,            # [dimensionless]
    }

    _eqkeys = const_si_dict.keys()
    _eqtuples = tuple((_locals[key], const_si_dict[key]) for key in _eqkeys)
    eqs_physical_constants_si = INITIALIZERS.equation_system(*_eqtuples, labels=_eqkeys)

    del _locals  # << don't keep this pointer in this namespace

    ''' --------------------- Set Presets --------------------- '''

    PS.set('eps0 mu0 c kB gamma eqs_physical_constants_si', locals())
