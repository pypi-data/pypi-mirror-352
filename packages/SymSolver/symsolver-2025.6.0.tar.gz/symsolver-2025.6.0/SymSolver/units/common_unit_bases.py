"""
File Purpose: commonly used unit bases.
"""
from ..initializers import INITIALIZERS
from ..tools import apply
from ..defaults import DEFAULTS

class _Stores_UnitBases():
    '''use self.make to make & store, or use self.store to store units.'''
    DEFAULT_BASES = ['L', 't', 'M', 'Q', 'K']
    EMPTY_BASE_STR = '1'   # we will set UNIT_BASES.one = unit_symbol(EMPTY_BASE_STR).
    ZERO_BASE_STR = '0'   # we will set UNIT_BASES.zero = unit_symbol(ZERO_BASE_STR).

    def __init__(self):
        self.bases = []

    def make_defaults(self):
        '''makes UnitSymbols in self.DEFAULT_BASES and also makes the identity unit.'''
        for ub in self.DEFAULT_BASES:
            self.make(ub)
        self.make(self.EMPTY_BASE_STR)

    def make(self, s):
        '''make new UnitSymbol and self.store it.'''
        sym = INITIALIZERS.unit_symbol(s)
        self.store(sym)
        return sym

    def store(self, usym):
        '''store UnitSymbol in self.bases and also setattr(self, usym.s, usym).'''
        self.bases.append(usym)
        setattr(self, usym.s, usym)

    def __getattr__(self, attr):
        '''makes and returns unit base: attr. (__getattr__ is only called if self.attr fails.)'''
        return self.make(attr)

    id = one = property(lambda self: getattr(self, self.EMPTY_BASE_STR),
                        doc='''identity unit, i.e. "dimensionless".''')
    zero = property(lambda self: getattr(self, self.ZERO_BASE_STR),
                    doc='''the number 0 (no units, but also destroys other units in multiplication)''')

UNIT_BASES = _Stores_UnitBases()


U = UNIT_BASES  # << alias for below
def uprop(f, doc=None):
    func = lambda self: apply(f(self), 'simplified') if DEFAULTS.UNITS_SIMPLIFY_SHORTHANDS else f(self)
    return property(func, doc=doc)

class UnitsShorthand():
    '''shorthand for things in terms of base units.'''
    L = uprop(lambda s: U.L, 'Length')
    t = uprop(lambda s: U.t, 'time')
    M = uprop(lambda s: U.M, 'Mass')
    Q = uprop(lambda s: U.Q, 'Charge')
    K = uprop(lambda s: U.K, 'Temperature')
    id = one = dimensionless = uprop(lambda s: U.id, 'identity, i.e. "dimensionless"')
    zero = uprop(lambda s: U.zero, 'the number 0 (no units, but also destroys other units in multiplication)')

    Hz = uprop(lambda s: 1/s.t, 'frequency, e.g. [1/s]')
    k = uprop(lambda s: 1/s.L, 'wavenumber, e.g. [1/m]')
    u = uprop(lambda s: s.L / s.t, 'speed, e.g. [m/s]')
    a = uprop(lambda s: s.L / s.t**2, 'acceleration, e.g. [m/s^2]')
    newton = uprop(lambda s: s.M * s.a, 'force, e.g. [kg*m/s^2]')
    P = uprop(lambda s: s.newton / s.L**2, 'pressure; energy density')
    joule = uprop(lambda s: s.newton * s.L, 'energy; work')
    watt = uprop(lambda s: s.joule / s.t, 'power')
    n = uprop(lambda s: 1/s.L**3, 'number density, e.g. [1/m^3]')
    rho = uprop(lambda s: s.M * s.n, 'mass density, e.g. [kg/m^3]')

    amp = uprop(lambda s: s.Q / s.t, 'current (not current density)')
    J = uprop(lambda s: s.amp / s.L**2, 'current density, e.g. [A/m^2]')
    volt = uprop(lambda s: s.joule / s.Q, 'voltage')
    E = uprop(lambda s: s.volt / s.L, 'electric field, e.g. [V/m]')
    farad = uprop(lambda s: s.Q / s.volt, 'capacitance')
    ohm = uprop(lambda s: s.volt / s.amp, 'resistance')
    B = uprop(lambda s: s.E / s.u, 'magnetic field, e.g. [Tesla]')
    eps0 = uprop(lambda s: s.farad / s.L, 'permittivity; units for epsilon_0')
    mu0 = uprop(lambda s: s.newton / s.amp**2, 'permeability; units for mu_0')

UNI = UnitsShorthand()
