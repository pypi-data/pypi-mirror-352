"""
File Purpose: defines "fluids" preset vars

These are:
    - inherently related to physics; specifically, the fluid equations
    - not required for full functionality in other parts of SymSolver
"""

from ..presets_tools import Presets
from ...basics import symbols, SYMBOLS
from ...units import UNI


PS = Presets('FLUID_VARS', 'FLUIDS', 'PHYSICS')
@PS.creator
def define_presets():
    '''define presets for the presets_fluid_vars module'''

    ''' --------------------- Generic Fluid vars --------------------- '''

    ns, rhos, Ps, Ts = symbols(('n', r'\rho', 'P', 'T'), ['s'])
    us, vs = symbols(('u', 'v'), ['s'], vector=True)
    qs, ms = symbols(('q', 'm'), ['s'], constant=True)
    nusj, = symbols((r'\nu',), ['s', 'j'])

    ns.units_base = UNI.n
    rhos.units_base = UNI.rho
    Ps.units_base = UNI.P
    Ts.units_base = UNI.K
    us.units_base = UNI.u
    vs.units_base = UNI.u
    qs.units_base = UNI.Q
    ms.units_base = UNI.M
    nusj.units_base = UNI.Hz


    ''' --------------------- Different subscripts --------------------- '''
    # note - symbols are each "singletons" so if you define an equivalent symbol you get the same object.
    # So, e.g., if you do ns.ss('s', 'e') in two different places you will get the same exact object out.
    # So, e.g., you can either use ne from here OR use ns.ss('s', 'e') when you want ne.

    n   = ns.del_ss('s')
    rho = rhos.del_ss('s')
    P   = Ps.del_ss('s')
    T   = Ts.del_ss('s')
    u   = us.del_ss('s')
    v   = vs.del_ss('s')
    q   = qs.del_ss('s')
    m   = ms.del_ss('s')

    ne   = ns.ss('s', 'e')
    rhoe = rhos.ss('s', 'e')
    Pe   = Ps.ss('s', 'e')
    Te   = Ts.ss('s', 'e')
    ue   = us.ss('s', 'e')
    ve   = vs.ss('s', 'e')
    qe   = qs.ss('s', 'e')
    me   = ms.ss('s', 'e')

    ni   = ns.ss('s', 'i')
    rhoi = rhos.ss('s', 'i')
    Pi   = Ps.ss('s', 'i')
    Ti   = Ts.ss('s', 'i')
    ui   = us.ss('s', 'i')
    vi   = vs.ss('s', 'i')
    qi   = qs.ss('s', 'i')
    mi   = ms.ss('s', 'i')

    nn   = ns.ss('s', 'n')
    rhon = rhos.ss('s', 'n')
    Pn   = Ps.ss('s', 'n')
    Tn   = Ts.ss('s', 'n')
    un   = us.ss('s', 'n')
    vn   = vs.ss('s', 'n')
    qn   = qs.ss('s', 'n')
    mn   = ms.ss('s', 'n')

    nj   = ns.ss('s', 'j')
    rhoj = rhos.ss('s', 'j')
    Pj   = Ps.ss('s', 'j')
    Tj   = Ts.ss('s', 'j')
    uj   = us.ss('s', 'j')
    vj   = vs.ss('s', 'j')
    qj   = qs.ss('s', 'j')
    mj   = ms.ss('s', 'j')

    nus = nusj.del_ss('s')
    nuej = nusj.ss('s', 'e')
    nuij = nusj.ss('s', 'i')
    nusn = nusj.ss('j', 'n')
    nuen = nuej.ss('j', 'n')
    nuin = nuij.ss('j', 'n')

    ''' --------------------- Misc. vars --------------------- '''

    g,       = symbols(('g',), vector=True, constant=True)

    g.units_base = UNI.a


    ''' --------------------- Set Presets --------------------- '''

    PS.set(  ('n' , 'rho' , 'P' , 'T' , 'u' , 'v' , 'q' , 'm' ,
              'ns', 'rhos', 'Ps', 'Ts', 'us', 'vs', 'qs', 'ms',
              'ne', 'rhoe', 'Pe', 'Te', 'ue', 've', 'qe', 'me',
              'ni', 'rhoi', 'Pi', 'Ti', 'ui', 'vi', 'qi', 'mi',
              'nj', 'rhoj', 'Pj', 'Tj', 'uj', 'vj', 'qj', 'mj',
              'nn', 'rhon', 'Pn', 'Tn', 'un', 'vn', 'qn', 'mn',
              'nusj', 'nus', 'nuej', 'nuij', 'nusn', 'nuen', 'nuin',
              'g',
              ), locals())
