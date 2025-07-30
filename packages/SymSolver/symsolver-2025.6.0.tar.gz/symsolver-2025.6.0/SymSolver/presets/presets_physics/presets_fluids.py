"""
File Purpose: "fluids" preset vars & equations

These are:
    - inherently related to physics; specifically, the fluid equations
    - not required for full functionality in other parts of SymSolver

[TODO] more preset fluid equation options
"""

from ..presets_tools import Presets, load_presets
from ...basics import EquationSystem
from ...precalc_operators import summation

from ...initializers import INITIALIZERS
from ...defaults import ZERO

ONE_THIRD = INITIALIZERS.rational(1,3)


PS = Presets('FLUIDS', 'PHYSICS')
@PS.creator
def define_presets():
    '''define presets for the presets_fluids module'''

    ''' --------------------- load fluid vars --------------------- '''

    fluid_vars = load_presets('FLUID_VARS', dst=globals())
    # ^ also loads into this namespace: ns, rhos, Ps, Ts, us, vs, qs, ms, nusj, g
    #  and those vars with 'e', 'i', or 'j' instead of s.

    _em_vars = load_presets('EM_VARS')
    E, B, J = (_em_vars[_key] for _key in ('E', 'B', 'J'))

    _consts = load_presets('PHYSICAL_CONSTANTS')
    gamma, kB = (_consts[_key] for _key in ('gamma', 'kB'))


    ''' --------------------- Fluid equations --------------------- '''

    _mom_s = (ns * us.dt_advective('s'),
                            - Ps.grad() / ms
                            + ns * qs / ms * (E + us.cross(B)))
    _momcol_s = (ns * us.dt_advective('s'),
                            - Ps.grad() / ms
                            + ns * qs / ms * (E + us.cross(B))
                            + ns * summation(nusj * (uj - us), 'j'))

    eqs_fluid_s_dict = {
        'continuity_s': (ns.dpt() + (ns * us).div(), ZERO),
        # momentum without collisions
        'momentum_s': _mom_s,
        # momentum with collisions
        'momcol_s': _momcol_s,
        # momentum without collisions and without inertia
        'momentum_inertialess_s': (ZERO, _mom_s[1]),
        # heating, adiabatic, in terms of pressure
        'adiabatic_s': (Ps.dt_advective('s') + gamma * Ps * us.div(), ZERO),
        # heating, with collisions, assuming gamma=5/3, in terms of temperature
        'heating_s': (Ts.dt_advective('s') + 2 * ONE_THIRD * Ts * us.div(),
                      summation(2 * ms / (ms + mj) * nusj *
                                (mj * ONE_THIRD / kB * (uj - us).dot(uj - us) + (Tj - Ts)),
                                'j')
                     ),
    }


    eqs_fluid_s = EquationSystem.from_dict(eqs_fluid_s_dict)
    eqs_fluid   = eqs_fluid_s.del_ss('s').relabeled(lambda label: label[:-2])
    eqs_fluid_e = eqs_fluid_s.ss('s', 'e').relabeled(lambda label: label[:-1]+'e')
    eqs_fluid_i = eqs_fluid_s.ss('s', 'i').relabeled(lambda label: label[:-1]+'i')

    eq_continuity_s = eqs_fluid_s['continuity_s']
    eq_momentum_s = eqs_fluid_s['momentum_s']
    eq_momcol_s = eqs_fluid_s['momcol_s']
    eq_adiabatic_s = eqs_fluid_s['adiabatic_s']
    eq_heating_s = eqs_fluid_s['heating_s']


    ''' --------------------- Set Presets --------------------- '''

    PS.set(['eqs_fluid', 'eqs_fluid_s', 'eqs_fluid_e', 'eqs_fluid_i',
            'eq_continuity_s', 'eq_momentum_s', 'eq_momcol_s', 'eq_adiabatic_s', 'eq_heating_s',
            ], locals())
