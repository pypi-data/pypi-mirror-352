"""
Package Purpose: preset SymbolicObjects for SymSolver

Uses classes defined elsewhere to pre-define some objects for convenience.
E.g. some physical variables, some equations, some math objects.

This file:
Imports the main important objects throughout this subpackage.

Usage notes:
    presets will be stored in PRESETS (a dictionary)
    can also get them via get_presets(requests)
"""
# modules here
from . import presets_misc
from . import presets_required
from . import presets_units

# subpackages here
from . import custom_presets
from . import presets_physics

# tools
from .presets_tools import (
    PRESETS, PRESET_KINDS,
    get_presets, Presets, load_presets,
)

# load required presets
load_presets('REQUIRED', dst=locals())
