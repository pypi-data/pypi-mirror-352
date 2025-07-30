"""
File Purpose: misc. tools for units
"""
from ..attributors import attributor

@attributor
def is_unit(x):
    '''returns whether x is a unit. (i.e. a UnitSymbol, (unit)^(exponent), or product of units)
    returns x.is_unit() if possible, else False.
    '''
    try:
        x_is_unit = x.is_unit
    except AttributeError:
        return False
    else:
        return x_is_unit()
