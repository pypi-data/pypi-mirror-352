"""
File Purpose: compress IterableSymbolicObject

objects which are equal will be replaced by the same object.
For example:
    obj1 = x + 1
    obj2 = x + 1
    obj3 = obj1 * obj2**7
    obj3.compress() creates:
    obj4 = obj1 * obj1**7

There should also be other options, such as:
    - count number of appearances of each object
    - diagnostics about number of replaced objects
    - set a minimum "complexity threshold"; ignore objects with lower complexity

[TODO] also update some routines to check if an object is compressed,
    and don't do the same substitutions or simplifications multiple times.

[TODO] option for replacing objects with cascade of equations
    replacing complicated objects with multiple appearances by a new symbol & equation.

[TODO] improve caching
"""
import collections

from .abelian_operations import AbelianOperation
from .substitutions import SubbableObject, is_subbable
from ._complexity import ComplexityBinning, complexity
from ..tools import (
    Binding,
    view_after_message,
)
from ..defaults import DEFAULTS

binding = Binding(locals())


''' --------------------- SubbableObject compress --------------------- '''

with binding.to(SubbableObject):
    @binding
    def compress2(self, cthresh=0, *, _cbins=None, **kw):
        '''returns self or equivalent replacement.
        attempts to reduce number of different objects which are equal.
        For example:
            x = symbol('x')
            obj1 = x + 1
            obj2 = x + 1
            assert obj1 is not obj2
            obj3 = obj1 * obj2
            obj4 = obj3.compress()
            assert obj4[0] is obj4[1]  # i.e., obj4 <--> obj1 * obj1

        cthresh: int, default 0
            only compress objects with complexity above this threshold.
            [EFF] note: larger cthresh means less compression, but can be much faster.
        '''
        if not is_subbable(self):
            return self
        if _cbins is None and DEFAULTS.CACHING_PROPERTIES:
            if cthresh >= getattr(self, '_cached_compress_cthresh', -1):
                # ">=" because smaller threshhold compresses all larger complexity things too.
                return self
        # this function's substitution rule for self:
        cbins = ComplexityBinning() if _cbins is None else _cbins
        c = cbins.binner(self)
        if c < cthresh:
            return self  # self's terms guaranteed to have complexity < c (< cthresh).
        try:
            _c, i, bin_ = cbins.index(self, return_bin=True)
        except ValueError:  # didn't find self in bins.
            pass  # handled below
        else:  # found a match!
            return bin_[i]  # equivalent to self but possibly a different object.
        # << didn't find self in bins
        # first, compress all the terms inside self. Then, bin the result.
        # ASSUMES:
        #   - complexity(result) == complexity(self)
        #   - none of the terms in self are equivalent to self.
        def compress2_rule(term):
            return term.compress2(cthresh, _cbins=cbins, **kw)
        newself = self._substitution_loop(compress2_rule, **kw)  # self, compressed.
        newself._cached_compress_cthresh = cthresh
        cbins.bin(newself, key=c)
        return newself

# with binding.to(AbelianOperation):
#     @binding
#     def compress(self, cthresh=0, *, _cabs=None, **kw):
#         '''returns self or equivalent replacement.
#         attempts to reduce number of different objects which are equal.
#         For example:
#             x = symbol('x')
#             obj1 = x + 1
#             obj2 = x + 1
#             assert obj1 is not obj2
#             obj3 = obj1 * obj2
#             obj4 = obj3.compress()
#             assert obj4[0] is obj4[1]  # i.e., obj4 <--> obj1 * obj1

#         cthresh: int, default 0
#             only compress objects with complexity above this threshold.
#             [EFF] note: larger cthresh means less compression, but can be much faster.
#         '''
#         cabs = dict() if _cabs is None else cabs
#         cls = type(self)
#         tcabs = cabs.setdefault(cls, dict())  # dict of {id: list of sets of ids of other terms}
#         # SubbableObject compress first 
#         self = SubbableObject.compress(self, cthresh=cthresh, _cabs=cabs, **kw)
#         # combining terms..
#         #  at this point, all the terms inside self are fully compressed,
#         #  and all type(self) objects inside of self appear in tcabs.
        

# # OLD -- SLOW # #
with binding.to(SubbableObject):
    @binding
    def compress1(self, cthresh=0):
        '''returns self or equivalent replacement.
        attempts to reduce number of different objects which are equal.
        For example:
            x = symbol('x')
            obj1 = x + 1
            obj2 = x + 1
            assert obj1 is not obj2
            obj3 = obj1 * obj2
            obj4 = obj3.compress()
            assert obj4[0] is obj4[1]  # i.e., obj4 <--> obj1 * obj1

        cthresh: int, default 0
            only compress objects with complexity above this threshold.

        [TODO] debug...
        [TODO][EFF] this method is slow...
        '''
        subtree = self.subtree()
        cbins = ComplexityBinning()
        trees = dict()  # {complexity: {id(obj): subtree}}
        repeats = dict()  # {complexity: [(subtree of obj, subtree of replacement) pairs]}
        for child in subtree.walk():
            obj = child.obj
            trees[id(obj)] = child
            if not is_subbable(obj):
                continue
            matched, (c, i, bin_) = cbins.bin_or_index(obj, return_bin=True)
            if matched and c >= cthresh:
                replacement = trees[id(bin_[i])]
                repeats.setdefault(c, []).append((child, replacement))
        repeat_items = sorted(repeats.items(), key=lambda item: item[0], reverse=True)
        for c, replacements in repeat_items:
            for tree_obj, tree_rep in replacements:
                tree_obj.obj = tree_rep.obj
                tree_obj.changed = False  # ignore tree_obj children when reconstructing.
        return subtree.reconstruct()


# # OLD - MISSES REPEATED OBJECTS # #
with binding.to(SubbableObject):
    @binding
    def compress0(self, cthresh=0, *, _cbins=None, **kw):
        '''returns self or equivalent replacement from cbins.
        complexity_threshold: int
            only compress objects with complexity above this threshold.
        
        _cbins is intended for internal use only.

        [TODO] debug... sometimes misses repeated objects.
                --> Use compress2 instead. compress2 solves this issue.
        '''
        if not is_subbable(self):
            return self
        if _cbins is None and DEFAULTS.CACHING_PROPERTIES and getattr(self, '_is_compressed', False):
            return self
        # this function's substitution rule for self:
        cbins = ComplexityBinning() if _cbins is None else _cbins
        c = cbins.binner(self)
        if c >= cthresh:
            matched, (_c, i, bin_) = cbins.bin_or_index(self, return_bin=True)
            if matched:
                result = bin_[i]  # equivalent to self but possibly a different object.
                result._is_compressed = True
                return result
        # loop through terms in self, if applicable.
        def compress0_rule(term):
            return term.compress0(cthresh, _cbins=cbins, **kw)
        return self._substitution_loop(compress0_rule, **kw)


# # CHOOSE WHICH TO USE FOR "COMPRESS" # #
SubbableObject.compress = SubbableObject.compress2
