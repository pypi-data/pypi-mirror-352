"""
File Purpose: "plasma quantities" preset equations

These are:
    - inherently related to physics; specifically, plasma quantities
    - not required for full functionality in other parts of SymSolver
"""

from ..presets_tools import Presets, load_presets
from ...basics import EquationSystem


PS = Presets('PLASMA_QUANTS', 'PHYSICS')
@PS.creator
def define_presets():
    '''define presets for the presets_plasma_quants module'''

    ''' --------------------- load plasma quants vars --------------------- '''

    pq_vars = load_presets('PLASMA_QUANTS_VARS', dst=globals())
    # ^ also loads into this namespace: Omegas, omegacs, omegaps, ldebyes, kappas,
    #   & versions with i, e, or nothing in place of s.

    _fluid_vars = load_presets('FLUID_VARS', dst=globals())
    # ^ also loads into this namespace: n, ns, rho, rhos, P, Ps, T, Ts, u, us, v, vs, q, qs, m, ms, g

    _em_vars = load_presets('EM_VARS')
    E, B, J = (_em_vars[_key] for _key in ('E', 'B', 'J'))

    _consts = load_presets('PHYSICAL_CONSTANTS')
    eps0, mu0, c = (_consts[_key] for _key in ('eps0', 'mu0', 'c'))


    ''' --------------------- plasma quants equations --------------------- '''

    eqs_plasma_quant_1f_dict = {
        'def_Omegas': (Omegas, qs * B.mag / ms),  # cyclotron
        'def_omegacs': (omegacs, qs * B.mag / ms),  # also cyclotron
        'def_omegaps': (omegaps**2, ns * qs**2 / (ms * eps0)),  # plasma oscillation (aka langmuir)
        'def_ldebyes': (ldebyes**2, eps0 * Ts / (ns * qs**2)),  # debye length (T in energy units)
        'def_kappas': (kappas, qs * B.mag / (ms * nusn)),   # kappa parameter..
    }

    eqs_plasma_quant_1f_s = EquationSystem.from_dict(eqs_plasma_quant_1f_dict)
    eqs_plasma_quant_1f_e = eqs_plasma_quant_1f_s.ss('s', 'e').relabeled(lambda label: label[:-1] + 'e')
    eqs_plasma_quant_1f_i = eqs_plasma_quant_1f_s.ss('s', 'i').relabeled(lambda label: label[:-1] + 'i')
    eqs_plasma_quant_1f   = eqs_plasma_quant_1f_s.del_ss('s').relabeled(lambda label: label[:-1])

    eqdef_Omegas, eqdef_omegacs, eqdef_omegaps, eqdef_ldebyes, eqdef_kappas = (eqs_plasma_quant_1f_s[_key]
            for _key in ['def_Omegas', 'def_omegacs', 'def_omegaps', 'def_ldebyes', 'def_kappas'])

    ''' --------------------- Set Presets --------------------- '''

    PS.set(['E', 'B', 'eps0', 'c',
            'eqs_plasma_quant_1f_s', 'eqs_plasma_quant_1f_e', 'eqs_plasma_quant_1f_i', 'eqs_plasma_quant_1f',
            'eqdef_Omegas', 'eqdef_omegacs', 'eqdef_omegaps', 'eqdef_ldebyes', 'eqdef_kappas',
            ], locals())
