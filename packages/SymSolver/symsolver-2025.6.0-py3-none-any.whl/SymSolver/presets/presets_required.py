"""
File Purpose: defines "required" preset values

These are:
    - not inherently related to physics
    - required for full functionality in other parts of SymSolver
"""

from .presets_tools import Presets
from ..basics import symbols
from ..calculus import STORES_NABLA, STORES_TIME, STORES_U
from ..initializers import INITIALIZERS
from ..linear_theory import PWQUANTS
from ..units import UNI

from ..defaults import DEFAULTS


PS = Presets('REQUIRED')

@PS.creator
def define_presets():
    '''define presets for the presets_required module'''

    ''' --------------------- Used by other parts of SymSolver --------------------- '''

    # # # COORDINATES # # #
    # define objects #
    X, Y, Z = symbols(('x', 'y', 'z'), units_base=UNI.L)
    XHAT, YHAT, ZHAT = (X.as_unit_vector(), Y.as_unit_vector(), Z.as_unit_vector())
    CARTESIAN_3D = INITIALIZERS.basis(XHAT, YHAT, ZHAT, metric=(1,1,1))
    # point to these objects #
    DEFAULTS.COMPONENTS_BASIS = CARTESIAN_3D

    # # # POSITION VECTOR # # #
    POSITION, = symbols(('x',), vector=True, units_base=UNI.L)
    POSITION.define_component(XHAT, X)
    POSITION.define_component(YHAT, Y)
    POSITION.define_component(ZHAT, Z)

    # # # COMMON DERIVATIVES # # #
    # define objects #
    NABLA = INITIALIZERS.derivative_operator(POSITION, partial=True, _nabla=True)
    TIME, = symbols(('t',), units_base=UNI.t)
    U,   = symbols(('u',),        vector=True, units_base=UNI.u)
    U_S, = symbols(('u',), ['s'], vector=True, units_base=UNI.u)
    # point to these objects #
    STORES_NABLA.NABLA = NABLA
    STORES_TIME.TIME = TIME
    STORES_U.U   = U
    STORES_U.U_S = U_S

    # # # PLANE WAVES # # #
    # define objects #
    OMEGA, = symbols((r'\omega',), units_base=UNI.Hz)
    K = KVEC = INITIALIZERS.symbol('k', vector=True, units_base=UNI.k)
    # point to these objects #
    PWQUANTS.OMEGA = OMEGA
    PWQUANTS.TIME = TIME
    PWQUANTS.K = K
    PWQUANTS.X = POSITION


    ''' --------------------- Set Presets --------------------- '''

    PS.set('X Y Z XHAT YHAT ZHAT CARTESIAN_3D POSITION NABLA OMEGA TIME K KVEC', locals())
