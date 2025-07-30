"""
File Purpose: defines "units" preset values
"""

from .presets_tools import Presets
from ..units import UNI

PS = Presets('UNITS')
@PS.creator
def define_presets():
    '''define presets for the presets_units module'''

    ''' --------------------- Units --------------------- '''

    # [TODO] any units we want to load here in particular??
    # Note: can already get units from UNI.
    #   E.g. UNI.L, UNI.newton. See help(UNI) for more details.


    ''' --------------------- Set Presets --------------------- '''

    PS.set('UNI', globals())
