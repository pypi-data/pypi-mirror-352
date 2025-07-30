"""
File Purpose: Set without hashing

(Set without hashing is slower than set, but behaves like set.)
"""

from .oop_tools import caching_attr_simple
from .display import ViewableSortable
from .equality import (
    equals,
)


class Set(ViewableSortable):
    '''"set" which may be inefficient (doesn't require hashing) but otherwise behaves like a set.
    Note: Set(Set(contents)) returns a new set with the same contents.
    E.g. x = Set(mylist); y = Set(x); y.contents is mylist  # << gives True.

    Note: uses hashing if possible.
    '''
    def __init__(self, contents, equals=equals):
        self.contents = contents
        self.equals = equals
        self._reduce()

    def _reduce(self):
        '''remove duplicates in self.
        Or, flattens self (if self.contents is a Set, self.contents = self.contents.contents)
        If contents are hashable, this will be faster. But hashing is not required.
        '''
        contents = self.contents
        if isinstance(contents, Set):
            # flatten self; no need to remove duplicates since contents was a Set.
            self.contents = tuple(self.contents.contents)
            return
        # remove duplicates
        try:
            self.contents = tuple(set(contents))
            return
        except TypeError:  # not all contents are hashable..
            pass  # handled below
        # [TODO][EFF] make more efficient if SOME contents are hashable,
        #   instead of jumping straight to the "don't try hashing at all" case.
        # not using hashing at all
        result = []
        for s in contents:
            for r in result:
                if self.equals(r, s):
                    break
            else:  # didn't break
                result.append(s)
        self.contents = tuple(result)

    def __eq__(self, x):
        '''returns self == x. Equality holds when all of the following are True:
        - for s in self, s in x.
        - for s in x, s in self.
        - len(x) == len(self)
        '''
        if x is self:
            return True
        # check lengths first for efficiency in easy False case.
        if len(self) != len(x):
            return False
        # loop through terms; confirm each appears in x else return False
        xl = [t for t in x]
        for term in self:
            for i, xi in enumerate(xl):
                if self.equals(term, xi):
                    xl.pop(i)
                    break
            else:  # didn't break
                return False
        return True

    @caching_attr_simple
    def __hash__(self):
        '''returns hashing for self IF POSSIBLE (i.e. if all elements of self.contents are hashable).
        Else raises TypeError.
        '''
        return hash((type(self), tuple(self.contents)))

    def __iter__(self):
        return iter(self.contents)

    def __getitem__(self, i):
        return self.contents[i]

    def __len__(self):
        return len(self.contents)

    def __add__(self, b):
        return Set(list(self) + list(b))  # [TODO][EFF] we already know self and b have no duplicates..

    def __radd__(self, b):
        return Set(list(b) + list(self))

    def __sub__(self, b):
        return Set([s for s in self if not s in b])

    # # # DISPLAY # # #
    def __repr__(self):
        return 'Set({})'.format(self.contents)

    def _view_contents(self):
        return self

    def __str__(self):
        contents = ', '.join([str(x) for x in self._view_sorted()])
        return fr'\Big\{{ {contents} \Big\}}'