"""
File Purpose: all custom error types defined in SymSolver.tools are defined in this file.
"""
import warnings

from .defaults import DEFAULTS


''' --------------------- GENERIC ERRORS --------------------- '''

# # # INPUT ERRORS # # #

class InputError(TypeError):
    '''error indicating something is wrong with the inputs, e.g. to a function.'''
    pass

class InputConflictError(InputError):
    '''error indicating two or more inputs provide conflicting information.
    E.g. foo(lims=None, vmin=None, vmax=None) receiving lims=(1,7), vmin=3, might raise this error,
    if the intention is for vmin and vmax to be aliases to lims[0] and lims[1].
    '''
    pass

class InputMissingError(InputError):
    '''error indicating that an input is missing AND doesn't have an appropriate default value.
    E.g. default=None; def foo(kwarg=None): if kwarg is None: kwarg=default; but foo expects non-None value.
    '''
    pass

class ImportFailedError(ImportError):
    '''error indicating that an import failed in the past, which is why a module cannot be accessed now.'''
    pass


# # # NOT IMPLEMENTED ERRORS # # #

class CatchableNotImplementedError(NotImplementedError):
    '''error indicating something is not implemented; but, it's okay to catch this error instead of crashing.
    For example, if _str_nonsymbolic is not implemented for int, we can still default to _str instead.
    '''
    pass


# # # ARRAY RELATED ERRORS # # #

class DimensionalityError(ValueError):
    '''error indicating dimensionality issue, e.g. wrong number of dimensions'''
    pass


''' --------------------- GENERIC WARNINGS --------------------- '''

# # # SYMSOLVER WARNING # # #

class SymSolverWarning(Warning):
    '''warning made by somewhere (other than tools) in the SymSolver package.
    (for warnings in tools, use the warnings module directly,
        so that the tools are easier to copy-paste elsewhere.)
    '''
    pass

def warn_SymSolver(message):
    '''warnings.warn(message, category=SymSolverWarning)'''
    return warnings.warn(message, category=SymSolverWarning, stacklevel=2)

warn = warn_SymSolver  # alias


# # # NOT IMPLEMENTED WARNING # # #

class NotImplementedWarning(SymSolverWarning):
    '''warning indicating that "falling back to a different option" was used due to missing code.
    For example, when evaluating derivatives,
    if implemented take_derivative of Power(x, 2) but not Power(2, x),
    then take_derivative(Power(2, x), x) might raise this, then return DerivativeOperation(Power(2, x), x).
    '''
    pass

def warn_NotImplemented(message):
    '''warnings.warn(message, category=NotImplementedWarning)'''
    return warnings.warn(message, category=NotImplementedWarning, stacklevel=2)


# # # TIMEOUT WARNING # # #

class TimeoutWarning(RuntimeWarning, SymSolverWarning):
    '''warning indicating a timeout occurred.'''
    pass

def warn_Timeout(message, force=False):
    '''warnings.warn(message, category=TimeoutWarning) if "enabled".
    "enabled" <--> DEFAULTS.TIMEOUT_WARNINGS enabled, OR force=True.
    '''
    if force or DEFAULTS.TIMEOUT_WARNINGS:
        return warnings.warn(message, category=TimeoutWarning, stacklevel=2)

class TimeoutError(Exception):
    '''error indicating a timeout.'''
    pass


''' --------------------- ERRORS FOR SUBPACKAGES --------------------- '''

# # # BASICS # # #

class PatternError(ValueError):
    '''error indicating issue with pattern matching, e.g. "doesn't look like -1 * value".'''
    pass


# # # VECTORS # # #

class VectorPatternError(PatternError):
    '''error indicating issue with vector pattern matching, e.g. "doesn't look like A dot B cross C".'''
    pass

class VectorialityError(ValueError):
    '''error indicating incompatible vectorialities (e.g. incompatible ranks)'''
    pass

class BasisNotFoundError(PatternError):
    '''error indicating that there is no Basis matching the specified criteria.'''
    pass

class MetricUndefinedError(PatternError):
    '''error indicating some operation required a metric but it was not defined.'''
    pass

class ComponentPatternError(PatternError):
    '''error indicating an issue related to components.'''
    pass


# # # PRECALC OPERATORS # # #

class OperatorMathError(PatternError):
    '''error indicating issue with doing math with operators, e.g. "multiplied two operators together".
    operators are like "unevaluated functions". can add, but not multiply or exponentiate.
    '''
    pass

class SummationIndicesMissingError(PatternError):
    '''error indicated the summation cannot be evaluated because some amount of info about indices is missing.
    E.g. imin=5, but imax not provided. Another example: imin=imax=iset=None.
    '''
    pass


# # # LINEAR THEORY # # #

class LinearizationPatternError(PatternError):
    '''error indicating an issue with linearization,
    e.g. attempting to linearize a symbol with existing order.
    '''
    pass

class LinearizationNotImplementedError(NotImplementedError):
    '''error indicating that a linearization algorithm was requested but not yet implemented.
    For example, (N**x).get_o1(), where N is constant and x is not,
    should be linearizable but requires to taylor expand N**x.
    It's easier to just implement (x**N), so we implemented that first and use this error in the meantime.
    '''
    pass

class PlaneWavesPatternError(PatternError):
    '''error indicating an issue with assume_plane_waves,
    e.g. assuming plane waves when there are still non-partial derivatives, or terms with mixed order.
    '''
    pass


# # # POLYNOMIALS # # #

class PolynomialPatternError(PatternError):
    '''error indicating an issue with pattern-matching related to polynomials.
    E.g. trying to add polynomials with different vars.'''
    pass

class PolyFractionPatternError(PolynomialPatternError):
    '''error indicating an issue with pattern-matching related to PolyFractions.
    E.g. trying to add PolyFractions with different vars.'''
    pass

class PolynomialNotImplementedError(CatchableNotImplementedError):
    '''error indicating an issue with something not being implemented, related to polynomials.
    As a "Catchable" error, the implication is that it's okay to intentionally use this error
        for code flow / control. E.g. raise it if "easy solution" is impossible, for an easy_solve function.
    '''
    pass


# # # ESSENCES # # #

class EssencePatternError(PatternError):
    '''pattern error during essentialization process'''
    pass


# # # SOLVING # # #

class SolvingPatternError(PatternError):
    '''PatternError during solving equations'''
    pass


# # # UNITS # # #

class UnitsPatternError(PatternError):
    '''PatternError when testing units'''
    pass


''' --------------------- TOOLS ERRORS --------------------- '''

class BindingError(ValueError):
    '''error indicating an issue with binding; see tools.binding.'''
    pass
