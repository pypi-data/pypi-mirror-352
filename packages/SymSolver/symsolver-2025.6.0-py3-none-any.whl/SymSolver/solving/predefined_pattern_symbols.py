"""
File Purpose: define some pattern symbols for the rest of the package to use.
"""

from ..essences import (
    new_pattern_symbol_matching_only,
)
from ..defaults import DEFAULTS


# match ANY EssenceSymbol.
PSYMS_ANY = [new_pattern_symbol_matching_only([],
                    s=DEFAULTS.PATTERN__ANY_SYMBOL_STR) for _ in range(3)]
PSYM_A0, PSYM_A1, PSYM_A2 = PSYMS_ANY

# match ANY EssenceSymbol -- looks like 'x^*'
PSYM_X = new_pattern_symbol_matching_only([], s='x^*')

# match any SCALAR EssenceSymbol.
PSYMS_SCALAR = [new_pattern_symbol_matching_only(['vector'], vector=False,
                    s=DEFAULTS.PATTERN__SCALAR_SYMBOL_STR) for _ in range(3)]
PSYM_S0, PSYM_S1, PSYM_S2 = PSYMS_SCALAR

# match any VECTOR EssenceSymbol.
PSYMS_VECTOR = [new_pattern_symbol_matching_only(['vector'], vector=True,
                    s=DEFAULTS.PATTERN__VECTOR_SYMBOL_STR) for _ in range(3)]
PSYM_V0, PSYM_V1, PSYM_V2 = PSYMS_VECTOR
