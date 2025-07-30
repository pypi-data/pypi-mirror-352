"""
File Purpose: augment numbers module

e.g. simplification methods for numbers as they appear in basics.
"""
from .power import Power
from .product import Product
from ._lites import ProductLite
from ..abstracts import simplify_op, expand_op
from ..numbers import ImaginaryUnit, ImaginaryUnitPower, IUNIT

from ..tools import Binding
from ..defaults import ONE

binding = Binding(locals())


''' --------------------- simplifying --------------------- '''

@expand_op(Product, alias='_simplify_id')  # also an expand op so that we can do it during expand.
@simplify_op(Product, alias='_simplify_id')
def _product_imaginary_unit_combine(self, **kw__None):
    '''combine all imaginary units (raised to integer powers) in self into a single ImaginaryUnitPower.
    E.g. i * i'''
    prodl = ProductLite.from_term(self)
    affected = prodl.collect(only=[IUNIT])
    if len(affected) == 0:
        return self  # return self, exactly, to help indicate nothing was changed.
    iaffected = affected[0]  # index of PowerLite in ProductLite with base IUNIT.
    powl = prodl[iaffected]
    assert powl.base is IUNIT
    try:
        newbase = ImaginaryUnitPower.integer_power_id(powl.exp)
    except PatternError:  # power is not an integer; give up.
        return self  # return self, exactly, to help indicate nothing was changed.
    powl.base = newbase
    powl.exp = ONE
    return prodl.reconstruct()

@simplify_op(Power)
def _power_upcast_to_imaginary_unit_power(self, **kw__None):
    '''if self.base is the imaginary unit, return ImaginaryUnitPower(self.exp).'''
    if self.base is IUNIT:
        return ImaginaryUnitPower(self.exp)
    else:
        return self  # return self, exactly, to help indicate nothing was changed.


''' --------------------- display --------------------- '''

with binding.to(ImaginaryUnit, ImaginaryUnitPower):
    @binding
    def _str_protect_product_factor(self, **kw__None):
        '''returns False, because str doesn't need protecting if it appears as a factor in Product.'''
        return False