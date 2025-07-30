"""
Package Purpose: "essence of an expression, with respect to one variable" in SymSolver.
Motivation: to solve an equation with x and lots of other factors,
    by hand, might replace a combination of many factors or sum of constants with a single letter.
        E.g. 7 y z u x + 8 g / i + l p**2 = 0    -->    A1 x + A2 = 0
    SymSolver aims to take a similar approach to solving equations.

Note: the essences package is built with the assumption that expand() will be run before essentialize().
    in particular, internal Sums are not expanded by essentialize, and the non-x summands in them
    will be essentialized in a possibly non-useful way, and won't look for duplicates in other internal sums.
    e.g. 7 y * (x + 3) + z * (x + 3)   -->   A1 * (x + A2) + A3 * (x + A4)

This file:
Imports the main important objects throughout this subpackage.
"""
# module references - in case other packages require direct access to these modules.
# Note: we discourage directly accessing these modules for non-internal use.
from . import essence_combine as _essence_combine_module
from . import essence_matches as _essence_matches_module
from . import essence_symbols as _essence_symbols_module
from . import essentialize as _essentialize_module

# importing contents from the modules...
from .essence_combine import (
    has_only_essence_symbols, get_first_essence_symbol,
    has_any_essence_symbols,
)
from .essence_matches import (
    essence_matches, matching_essence,
    essence_match_and_track,
)
from .essence_symbols import (
    EssenceSymbol, ESSENCE_SYMBOLS,
    new_essence_symbol, new_essence_symbol_like, new_essence_symbol_to_replace,
    essence_symbol_for,
) 
from .essentialize import (
    essentialize,
    restore_from_essentialized,
)
from .pattern_symbols import (
    PatternSymbol, PATTERN_SYMBOLS,
    new_pattern_symbol, new_pattern_symbol_like,
    new_pattern_symbol_matching_only,
    essence_pattern_matches,
    subs_pattern_matched,
)