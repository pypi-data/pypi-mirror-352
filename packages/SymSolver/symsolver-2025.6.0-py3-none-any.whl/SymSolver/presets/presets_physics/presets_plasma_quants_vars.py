"""
File Purpose: "plasma quantities" preset vars

These are:
    - inherently related to physics; specifically, plasma quantities
    - not required for full functionality in other parts of SymSolver
"""

from ..presets_tools import Presets
from ...initializers import INITIALIZERS
from ...units import UNI


PS = Presets('PLASMA_QUANTS_VARS', 'PLASMA_QUANTS', 'PHYSICS')
@PS.creator
def define_presets():
    '''define presets for the presets_plasma_quant_vars module'''

    ''' --------------------- Frequencies --------------------- '''

    Omegas = INITIALIZERS.symbol(r'\Omega', ['s'])  # cyclotron frequency
    omegacs = INITIALIZERS.symbol(r'\omega', ['c', 's'])  # also cyclotron frequency
    omegaps = INITIALIZERS.symbol(r'\omega', ['p', 's'])  # plasma frequency

    for _s in (Omegas, omegacs, omegaps): _s.units_base = UNI.Hz


    ''' --------------------- Lengths --------------------- '''

    ldebyes = INITIALIZERS.symbol(r'\lambda', ['D', 's'])  # Debye length

    for _s in (ldebyes,): _s.units_base = UNI.L


    ''' --------------------- Dimensionless quantities --------------------- '''

    kappas = INITIALIZERS.symbol(r'\kappa', ['s'])  # qs B / (ms nu_sn).  Omegas / nu_sn

    for _s in (kappas,): _s.units_base = UNI.id


    ''' --------------------- Different subscripts --------------------- '''

    Omega = Omegas.del_ss('s')
    omegac = omegacs.del_ss('s')
    omegap = omegaps.del_ss('s')
    ldebye = ldebyes.del_ss('s')
    kappa = kappas.del_ss('s')

    Omegae = Omegas.ss('s', 'e')
    omegace = omegacs.ss('s', 'e')
    omegape = omegaps.ss('s', 'e')
    ldebyee = ldebyes.ss('s', 'e')
    kappae = kappas.ss('s', 'e')

    Omegai = Omegas.ss('s', 'i')
    omegaci = omegacs.ss('s', 'i')
    omegapi = omegaps.ss('s', 'i')
    ldebyei = ldebyes.ss('s', 'i')
    kappai = kappas.ss('s', 'i')


    ''' --------------------- Set Presets --------------------- '''

    PS.set(('Omega',  'omegac',  'omegap',  'ldebye',  'kappa',
            'Omegas', 'omegacs', 'omegaps', 'ldebyes', 'kappas',
            'Omegae', 'omegace', 'omegape', 'ldebyee', 'kappae',
            'Omegai', 'omegaci', 'omegapi', 'ldebyei', 'kappai',
           ), locals())
