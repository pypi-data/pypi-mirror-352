"""
File Purpose: "E & M" preset vars & equations

These are:
    - inherently related to physics; specifically, the E & M equations
    - not required for full functionality in other parts of SymSolver
"""

from ..presets_tools import Presets, load_presets
from ...basics import EquationSystem
from ...precalc_operators import summation

from ...defaults import ZERO


PS = Presets('EM', 'PHYSICS')
@PS.creator
def define_presets():
    '''define presets for the presets_em module'''

    ''' --------------------- load EM vars --------------------- '''

    em_vars = load_presets('EM_VARS', dst=globals())
    # ^ loads E, B, J into this namespace, too.

    _fluid_vars = load_presets('FLUID_VARS')
    q, n, qs, ns, us, = (_fluid_vars[_key] for _key in ('q', 'n', 'qs', 'ns', 'us'))

    _consts = load_presets('PHYSICAL_CONSTANTS')
    eps0, mu0, c = (_consts[_key] for _key in ('eps0', 'mu0', 'c'))


    ''' --------------------- EM equations --------------------- '''

    eqs_em_dict = {
        'divE': (E.div(), q * n / eps0),   # a.k.a. 'Gauss'
        'divB': (B.div(), ZERO),           # a.k.a. 'Gauss for magnetic fields'
        'curlE': (E.curl(), -B.dpt()),     # a.k.a. 'Induction'
        'curlB': (B.curl(), mu0 * J + c**-2 * E.dpt()),  # a.k.a. 'Ampere with displacement current'
        'curlB_no_disp': (B.curl(), mu0 * J),            # a.k.a. 'Ampere without displacement current'
        'def_J': (J, summation(qs * ns * us, 's')),
    }

    _eqkeys = ('divE', 'divB', 'curlE', 'curlB')
    _eqkeys_no_disp = ('divE', 'divB', 'curlE', 'curlB_no_disp')

    eqs_em = EquationSystem.from_dict({key: eqs_em_dict[key] for key in _eqkeys})
    eqs_maxwell = eqs_em  # alias

    eqs_em_no_disp = EquationSystem.from_dict({key: eqs_em_dict[key] for key in _eqkeys_no_disp})
    eqs_maxwell_no_disp = eqs_em_no_disp  # alias

    eq_divE = eqs_em['divE']
    eq_divB = eqs_em['divB']
    eq_curlE = eqs_em['curlE']
    eq_curlB = eqs_em['curlB']
    eq_curlB_no_disp = eqs_em_no_disp['curlB_no_disp']

    eqdef_J = EquationSystem.from_dict({'def_J': eqs_em_dict['def_J']})['def_J']


    ''' --------------------- Set Presets --------------------- '''

    PS.set(['eps0', 'mu0', 'c', 'q', 'n',
            'eqs_em', 'eqs_em_no_disp', 'eqs_maxwell', 'eqs_maxwell_no_disp',
            'eq_divE', 'eq_divB', 'eq_curlE', 'eq_curlB', 'eq_curlB_no_disp',
            'eqdef_J',
            ], locals())
