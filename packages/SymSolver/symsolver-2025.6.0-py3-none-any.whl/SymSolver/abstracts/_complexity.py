"""
File Purpose: complexity for abstracts
"""
import builtins  # << for unambiguous sum
import collections
import operator

from .abstract_operations import AbstractOperation
from .associative_operations import AssociativeObject, AssociativeOperation
from .commutative_operations import CommutativeObject, CommutativeOperation
from .iterable_symbolic_objects import IterableSymbolicObject, BinarySymbolicObject
from .keyed_symbolic_objects import KeyedSymbolicObject
from .operation_containers import OperationContainer
from .simplifiable_objects import SimplifiableObject
from .substitutions import SubbableObject
from .symbolic_objects import SymbolicObject

from ..attributors import attributor
from ..tools import (
    Binning, equals, viewdict, fastfindviewlist,
    format_docstring,
    Binding, caching_attr_simple_if, caching_attr_with_params_if,
)

from ..defaults import DEFAULTS, ZERO

binding = Binding(locals())


''' --------------------- Convenience --------------------- '''

@attributor
def complexity(x):
    '''returns x.complexity() if available, else 1.'''
    try:
        x_complexity = x.complexity
    except AttributeError:
        return 1
    else:
        return x_complexity()

@attributor
def complexity_infosort(x, reverse=False):
    '''returns result of sorting x by complexity, but providing extra information in result.
    result will be a list of tuple (i, y, complexity(y)), such that x[i]=y,
        and [y for (i, y, c) in result] is listed in complexity order.
    if it is available, return x.complexity_indexsort(reverse) instead.

    if reverse, highest complexity comes first (instead of last).
    '''
    try:
        x_complexity_infosort = x.complexity_infosort
    except AttributeError:
        pass  # handled after the 'else' block to avoid complicated error messages.
    else:
        return x_complexity_infosort(reverse=reverse)
    # << didn't find x.complexity_infosort
    complexity_infos = [(i, y, complexity(y)) for i, y in enumerate(x)]
    return sorted(complexity_infos, key=lambda iyc: iyc[2], reverse=reverse)

@attributor
def complexity_bins(x):
    '''returns complexity bins for x, by doing x.complexity_bins().
    The result is a ComplexityBinning object containing all unique objects in x.
    Comparing objects is done via 'is'.
    x will not be in result.
    if x doesn't have a complexity_bins method, return ComplexityBinning() (with equals=builtin 'is')
    '''
    try:
        x_complexity_bins = x.complexity_bins
    except AttributeError:
        cbins = ComplexityBinning()
        cbins.comparing_is()
        return cbins
    else:
        return x_complexity_bins()


''' --------------------- complexity --------------------- '''

# default complexity for SymbolicObject
with binding.to(SymbolicObject):
    @binding
    def complexity(self):
        '''returns 1, the default complexity for a SymbolicObject.'''
        return 1

# default complexity: 1 + super().complexity()
default_complexity_classes = (
    AbstractOperation,
    AssociativeObject, AssociativeOperation,
    CommutativeObject, CommutativeOperation,
    BinarySymbolicObject,
    OperationContainer,
    SimplifiableObject,
    SubbableObject,
)

def _default_complexity_definer(cls):
    '''returns complexity function for cls.'''
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    @format_docstring(cls=cls.__name__)
    def complexity(self):
        '''returns 1 + super({cls}, self).complexity().'''
        return 1 + super(cls, self).complexity()
    return complexity

for cls in default_complexity_classes:
    binding.bind_to(cls, _default_complexity_definer(cls))

# non-default complexities:
with binding.to(IterableSymbolicObject, KeyedSymbolicObject):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def complexity(self):
        '''return sum of complexities of terms in self.'''
        return builtins.sum(complexity(term) for term in self)


''' --------------------- complexity sorting --------------------- '''

with binding.to(IterableSymbolicObject):
    @binding
    @caching_attr_with_params_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def complexity_infosort(self, reverse=False):
        '''returns result of sorting x by complexity, but providing extra information in result.
        result will be a list of tuples (i, y, complexity(y)), such that list(self)[i]=y,
            and [y for (i, y, c) in result] is listed in complexity order.

        if reverse, highest complexity comes first (instead of last).

        note: to simply sort by complexity, you can just do sorted(self, key=complexity) instead.
        '''
        complexity_infos = [(i, y, complexity(y)) for i, y in enumerate(self)]
        return sorted(complexity_infos, key=lambda iyc: iyc[2], reverse=reverse)


''' --------------------- ComplexityBinning --------------------- '''

class ComplexityBinning(Binning, viewdict):
    '''collection of objects binned by complexity for faster comparison.'''
    default_default_factory = fastfindviewlist
    _view_sortkey = True  # sort by keys, when viewing.

    def __init__(self, binner=complexity, **kw):
        super().__init__(binner=binner, **kw)

    def comparing_equal(self):
        '''sets self.equals = tools.equals.'''
        self.equals = tools.equals

    def comparing_is(self):
        '''sets self.equals = operator.is_.  This is the "is" operator.'''
        self.equals = operator.is_


with binding.to(IterableSymbolicObject, KeyedSymbolicObject):
    @binding
    @caching_attr_simple_if(lambda: DEFAULTS.CACHING_PROPERTIES)
    def complexity_bins(self):
        '''returns complexity bins for self.
        The result is a ComplexityBinning object containing all unique objects in self
        (and inside any IterableSymbolicObjects inside self, recursively).
        Result does not contain self.
        The ComplexityBinning's comparisons are done by 'is'.
        WARNING: editing result directly will mess up caching; use result.copy() if you want to edit.
        '''
        cbins = ComplexityBinning()
        cbins.comparing_is()
        for obj in self:
            cbins.bin_or_index(obj)
            obj_cbins = complexity_bins(obj)
            cbins.update(obj_cbins)
        return cbins

