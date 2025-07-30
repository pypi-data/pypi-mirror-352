"""
File Purpose: _sum_collect

NOTE: this is an add-on to Sum.
Importing this module will adjust the Sum class appropriately.
Failing to import this module will mean that Sum._sum_collect is not defined.


MOTIVATION:
    It's tricky to handle collecting things for Sum.
    There's not always a unique correct answer.

For instance, what should happen to x^2 + 5cx + 5c + 7x + 9?
"Reasonable" answers include but are not limited to:
    --> x(x + 5c + 7) + 5c + 9    ("greedy collection prioritizing x over c")
    --> x(x + 7) + 5c(x + 1) + 9  ("greedy collection prioritizing c over x")
    --> x^2 + 7x + 5c(x + 1) + 9  ("greedy collection prioritizing c over x, but keeping polynomial-format x when possible")
    --> x(x + 7) + 5cx + 5c + 9   ("greedy collection prioritizing x and c the same")
    --> x^2 + (5c + 7)x + 5c + 9  ("polynomial-format collection prioritizing x")
    --> x^2 + 5cx + 5c + 7x + 9   ("polynomial-format collection prioritizing x and c the same")
Perhaps this one is the most intuitive:
    --> x^2 + (5c + 7)x + 5c + 9  ("polynomial-format collection prioritizing x")
For constant c and variable x, I would personally choose this one, given no further context.


PRIORITY LEVEL:
    Things should be prioritized in different ways when collecting factors.

The default priority level prioritizes:
    Power
    > AbstractOperation
    > SymbolicObject which is_constant but not is_number
    > SymbolicObject which is_number
    > Number (non-symbolic)
Once the priorities are decided, we can perform the appropriate collection algorithm.
POST-REFACTOR (December 2022):
    Now, the priorities take "local view" when deciding whether to collect.
        I.e. ONLY collect if it does not put a same-or-higher-priority into an internal sum.
        E.g. 9c + xc --> (9+x)c is NEVER allowed, assuming priority(c)<=priority(x)
    Previously, a "global view" was used.
        This checked the rest of the terms first, which is more complicated.
        A same-or-higher-priority term could end up in an internal sum, if it only appeared once in the expression.
        E.g. 9c + xc --> (9+x)c was allowed, but 9c + xc + 3x --> (9+x)c + 3x was not.

[TODO] refactor the prioritizer code to use a class instead of function.
        That will make things easier to debug / inspect.
        Also might allow user to more easily provide custom priorities if desired.
[TODO] option to deprioritize certain things during collection. E.g., opposite of collect_these.
"""
from .basics_tools import (
    get_factors, get_base_and_power,
    multiply,
)
from .sum import Sum
from .power import Power

from ..abstracts import (
    SymbolicObject, AbstractOperation,
    is_number, is_constant,
    simplify_op, simplify_op_skip_for,
)
from ..tools import (
    argsort_none_as_small,
    find, equals, unordered_list_equals,
    format_docstring,
)
from ..defaults import DEFAULTS

''' --------------------- COLLECTION PRIORITY SYSTEM --------------------- '''
# # DEFAULTS # #
# intentionally set here, not in DEFAULTS. Not something that the user should edit or worry about.
DEFAULT_COLLECTION_PRIORITIES_CLASSES = {
    SymbolicObject: 10,
    AbstractOperation: 40,
    #Sum: 50,
    Power: 60,
}
DEFAULT_COLLECTION_PRIORITIES_CHECKS = {
    'is_number': 20,
    'is_constant': 30,
}
DEFAULT_COLLECTION_PRIORITY_LARGEST = max(*DEFAULT_COLLECTION_PRIORITIES_CLASSES.values(),
                                          *DEFAULT_COLLECTION_PRIORITIES_CHECKS.values())

for cls, val in DEFAULT_COLLECTION_PRIORITIES_CLASSES.items():
    setattr(cls, '_DEFAULT_SUM_COLLECT_PRIORITY', val)

# # PROPRERTY - SUM COLELCT PRIORITY # #
def _propget_sum_collect_priority(self):
    '''getter for _sum_collect_priority property of SymbolicObject.'''
    try:
        return self.sum_collect_priority   # cached (or user-entered) value
    except AttributeError:
        if is_number(self):
            result = DEFAULT_COLLECTION_PRIORITIES_CHECKS['is_number']
        elif is_constant(self):
            result = DEFAULT_COLLECTION_PRIORITIES_CHECKS['is_constant']
        else:
            result = self._DEFAULT_SUM_COLLECT_PRIORITY
        self.sum_collect_priority = result
        return result

def _propset_sum_collect_priority(self, value):
    '''setter for _sum_collect_priority of SymbolicObject.'''
    raise TypeError('''Cannot write to self._sum_collect_priority.
                    To set a default value, write to self.sum_collect_priority instead''')

SymbolicObject._sum_collect_priority = property(_propget_sum_collect_priority, _propset_sum_collect_priority,
        doc='''tells the collection priority of self during the _sum_collect simplify operation.
            _sum_collect will target higher priority objects first, and will ensure that
            collecting a lower priority object never prevents further collection of a higher priority object.
            Can manually adjust by writing to to self.sum_collect_priority.''')

# # CONVENIENT - GET SUM COLLECT PRIORITY FOR ANY OBJECT # #
def get_sum_collect_priority(obj):
    '''gets _sum_collect_priority of obj. Returns 0 for objects without this attribute.'''
    try:
        return obj._sum_collect_priority
    except AttributeError:
        return 0

# # SUM COLLECT USING PRIORITY SYSTEM # #
_local_view_on_priorities_docs = \
    '''Takes a "local" view on priorities:
        ONLY collect a term if it does not put a same-or-higher-priority into an internal sum.
        E.g. 9c + xc --> (9+x)c is NEVER allowed, assuming priority(c)<=priority(x)
    
        Thus, start by checking the highest priority factor(s) in each summand;
        if they would not be collected, don't perform the operation.
        If they could be collected, check other factors as well.
        E.g. 9xc + 7x --> x(9c + 7), but 9xc + 7xc --> xc(9 + 7)'''

@format_docstring(takes_a_local_view_on_priorities=_local_view_on_priorities_docs)
def _sum_collect_prioritized(self, _sum_collect_prioritizer=None, **kw__None):
    '''collect routine for sum, taking into account obj._sum_collect_priority of factors.
    {takes_a_local_view_on_priorities}

    _sum_collect_prioritizer: None, or function of a single argument, f(obj)
        convert input into sum collect priority. Larger value --> prioritize first.
        None --> use get_sum_collect_priority,
            which returns obj._sum_collect_priority if possible, else 0.
        Other examples include:
            lambda obj: obj == x
                --> prioritize x above all else, but still attempt non-x collections if it doesn't put x into an internal sum.
            lambda obj: 1 if (obj == x) else None
                --> only attempt to collect x
            lambda obj: 1 if (get_base_and_power(obj)[0] == x) else None
                --> only attempt to collect factors like x^n.

    [TODO] _transmit_genes after collection. Needs a _transmit_genes that allows for multiple parents...
        E.g. t1=7xc, t2=5x --> collected=x*(7c + 1) and should maybe get genes from t1 and t2.
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    summands_factors = [get_factors(t) for t in self]
    # sort by priorities - just an argsort of numbers so hopefully fast even for large lists.
    if _sum_collect_prioritizer is None: _sum_collect_prioritizer = get_sum_collect_priority
    sfs_priorities = [[_sum_collect_prioritizer(f) for f in factors] for factors in summands_factors]
    sps_argsorts = [argsort_none_as_small(priorities, reverse=True) for priorities in sfs_priorities]
    sfps_sorted = [[(factors[i], priorities[i]) for i in argsort]
            for factors, priorities, argsort in zip(summands_factors, sfs_priorities, sps_argsorts)]
    # ^ sfps_sorted[j] is sorted_by_priority([(factor, priority) for each factor in self[j]])
    # (with highest priority appearing first in the sorted list).
    
    result_fps_and_torig = []
    collected_any = False
    for (fps, torig) in zip(sfps_sorted, self):
        for i, (rfps, rtorig) in enumerate(result_fps_and_torig):
            collected_fps, summand1_fps, summand2_fps = _sum_collect_prioritized_from_fps(fps, rfps)
            if len(collected_fps) > 0:
                # collected something.
                collected_any = True
                summand1_as_math = multiply(*(f for (f, _) in summand1_fps))
                summand2_as_math = multiply(*(f for (f, _) in summand2_fps))
                s1_plus_s2_f = summand1_as_math + summand2_as_math
                priority_s12 = _sum_collect_prioritizer(s1_plus_s2_f)
                s12_fp = (s1_plus_s2_f, priority_s12)
                # put s12_fp where it belongs, such that collected_fps is still sorted by priority.
                if priority_s12 is None:
                    collected_fps.append(s12_fp)
                else:
                    for j, (_, p) in enumerate(collected_fps):
                        if p < priority_s12:
                            collected_fps.insert(j, s12_fp)
                            break
                    else:  # didn't break
                        collected_fps.append(s12_fp)
                # replace result_fps[i] with collected_fps; don't add any other fps to result.
                result_fps_and_torig[i] = (collected_fps, None)  # torig irrelevant now that collection was performed.
                break # don't attempt to compare s12_fp with previous terms in result.
                # maybe will result in less collection. But sounds much cheaper than another loop...
        else:  # didn't break.
            result_fps_and_torig.append((fps, torig)) # this fps didn't match anything in result. so put it into result.
    if not collected_any:
        return self  # return self, exactly, to help indicate nothing was changed.
    # make new Sum with all the collected terms.
    summands = (torig if torig is not None else self.product(*(f for (f, _) in fps))
                for (fps, torig) in result_fps_and_torig)
    return self._new(*summands)
            
def _sum_collect_prioritized_from_fps(fps1, fps2):
    '''helper for _sum_collect_prioritized.
    COLLECT ALL COLLECTABLE FACTORS according to priority system.
    notes (based on the priority system):
        - if highest priority factors don't have the same priority, can't collect anything.
        - if collecting anything, must collect ALL highest-priority factors from each term.

    fps1, fps2: list of tuples
        list of (factor, priority) pairs, sorted in descending order of priority.

    return (collected fps, uncollected fps from fps1, uncollected fps from fps2)
    fps will each be in proper sorted order of priorities (highest to lower priority).
    The "mathematical" result after collection is equal to:
        product(*r0fs, sum(product(*r1fs), product(*r2fs)),
        where r<i>fs = [f for (f, p) in result[i]].
    '''
    ncol = _priorities_might_allow_collection((p for _, p in fps1), (p for _, p in fps2))  # number to collect
    if ncol:
        fs1 = [fps1[i][0] for i in range(ncol)]
        fs2 = [fps2[i][0] for i in range(ncol)]
        if unordered_list_equals(fs1, fs2):
            # collect! return (something like) product(*rfs[:ncol], sum(product(*rfs[ncol:]), product(*fs[ncol:]))
            # collect first ncol factors from fs and from rfs.
            collected_fps = fps1[:ncol]   # or fps2[:ncol]. They are the same factors.
            summand1_fps  = fps1[ncol:]
            summand2_fps  = fps2[ncol:]
            # collect anything from remaining uncollected summands. E.g. x(7c + 5c) --> xc(7 + 5)
            coll_deep_fps, summand1_fps, summand2_fps = _sum_collect_prioritized_from_fps(summand1_fps, summand2_fps)
            collected_fps += coll_deep_fps  # list addition
            return collected_fps, summand1_fps, summand2_fps
    # if we didn't return yet, collection was impossible. So, return ([], fps1, fps2)
    return [], fps1, fps2

def _priorities_might_allow_collection(ps1, ps2):
    '''helper for _sum_collect_prioritized_from_fps.
    returns number of terms to be collected if collection occurs between terms with priorities ps1 and ps2.
    Actually, if collction might be possible, returns minimum number of terms to be collected, if any.

    ps1 and ps2: iterable of priorities (use generators for efficiency)
        priorities of each terms, sorted in descending order.
        Example ps1=(p for p in sorted_priorities_list)
        None priority indicates "never attempt to collect" and should appear only after all non-None priorities.

    notes (based on the priority system):
        - if highest priority factors don't have the same priority, can't collect anything.
        - if different number of highest priority factors, can't collect anything.
            - (if collecting anything, must collect all or none of the highest priority factors.)

    E.g. ps1=[60,40,10], ps2=[50,20] --> False     # highest priority factors don't have the same priority
        ps1=[60,40,10], ps2=[60,50,40,30,20] --> 1 # same number (==1) of highest priority factors
        ps1=[50,50,40,10], ps2=[50,50,30] --> 2    # same number (==2) of highest priority factors
        ps1=[60,60,40,10], ps2=[60,10] --> False   # different number of highest priority factors 

    [TODO][REF] surely there is a cleaner way to write this code..
    '''
    # setup
    ps1 = iter(ps1)
    ps2 = iter(ps2)
    # get first term in each. Return False if either has no terms.
    try:
        p1 = next(ps1)
        p2 = next(ps2)
    except StopIteration:
        return False
    # setup pmax; return False if None or if p1 != p2
    pmax = p1
    if pmax is None:
        return False
    if pmax != p2:
        return False
    # if we got this far, the first terms match in ps1 and ps2,
    # so we must match at least 1 thing (if we are going to match anything at all)
    must_match = 1
    # loop through remaining terms...
    while True:
        # get next from ps1 and ps2:
        try:
            p1 = next(ps1)
        except StopIteration:
            try:
                p2 = next(ps2)
            except StopIteration:
                return must_match   # same number of highest priority factors, equal to len(list(ps1)) (and ps2 same length).
            else:
                if p2 == pmax:
                    return False   # different number of highest priority factors.
                else:
                    return must_match  # same number of highest priority factors, equal to len(list(ps1)) (and ps2 is longer).
        try:
            p2 = next(ps2)
        except StopIteration:
            if p1 == pmax:
                return False  # different number of highest priority factors.
            else:
                return must_match  # same number of highest priority factors, equal to len(list(ps2)) (and ps1 is longer).
        # check if p1 and p2 agree. Either increment must_match, return False, or return must_match.
        if p1 == pmax:
            if p2 == pmax:
                must_match += 1  # p1 and p2 are both highest priority.
            else:
                return False  # different number of highest priority factors.
        elif p2 == pmax:
            return False  # different number of highest priority factors.
        else:
            return must_match  # same number of highest priority factors. p1 and p2 are not highest-priority.


''' --------------------- GSCP (Get Sum Collect Priority) --------------------- '''

_gscp_paramdocs = \
    '''COLLECTION PRIORITY LIST KWARGS:
        if any of these is non-empty, use it instead of factor._sum_collect_priority to determine priorities.
        can only use one of these at a time; makes AssertionError if multiple are nonempty.

        collect_these: list (default empty list)
            prioritize collecting these things, if nonempty.
        collect_polys: list (default empty list)
            prioritize collecting any factor like x^n for x in this list.
        collect_ifs: list (default empty list)
            prioritze collecting any factor x with f(x)==True for (at least one) f in this list.

    COLLECTION PRIORITY LIST BEHAVIOR KWARGS
        these just affect the behavior of collection priority list kwargs.
        these only matter if one of those kwargs is used, i.e. nonempty list.

        collect_priority_only: bool (default False)
            whether to ONLY collect things from the provided list.
            If True, don't even attempt collection of anything unless it is prioritized in the list.
        collect_priority_equal: bool (default False)
            whether to treat all things from the provided list with the same priority.
            If False, assign priorities as highest-first. E.g. [x,y] --> priority(x) > priority(y)

    PRIORITIZER FUNCTION KWARG
        this is a direct interface to the low-level priorities functionality.
        (using the other kwargs effectively just leads to pre-made/convenient values for this kwarg.)
        can only use if the collection piority list kwargs are empty; otherwise makes AssertionError.

        _sum_collect_prioritizer: None or callable
            this function, if provided, will be used to determine priority of every factor.
            use priority=None to say "do not even attempt to collect this factor."
            Will be passed directly to _sum_collect_prioritized.'''

@format_docstring(paramdocs=_gscp_paramdocs)
def _get_gscp(collect_these=[], collect_polys=[], collect_ifs=[],
              collect_priority_only=False, collect_priority_equal=False, 
              _sum_collect_prioritizer=None):
    '''returns a function get_sum_collect_priority(factor) which tells the sum collect priority of factor.

    By default, the result will just yield factor._sum_collect_priority (or 0 if not provided).
    This default behavior can be changed via any of the kwargs below:

    {paramdocs}
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    kw__collect_settings = dict(collect_priority_only=collect_priority_only, collect_priority_equal=collect_priority_equal)
    if len(collect_these) > 0:
        assert len(collect_polys) == 0, "can only use one collection list kwarg but got nonempty 'collect_these' and 'collect_polys'."
        assert len(collect_ifs) == 0, "can only use one collection list kwarg but got nonempty 'collect_these' and 'collect_ifs'."
        assert _sum_collect_prioritizer is None, "cannot use _sum_collect_prioritizer and 'collect_these' simultaneously."
        prioritizer = _make_gscp(collect_these, 'collect_these', **kw__collect_settings)
    elif len(collect_polys) > 0:
        assert len(collect_ifs) == 0, "can only use one collection list kwarg but got nonempty 'collect_polys' and 'collect_ifs'."
        assert _sum_collect_prioritizer is None, "cannot use _sum_collect_prioritizer and 'collect_polys' simultaneously."
        prioritizer = _make_gscp(collect_polys, 'collect_polys', **kw__collect_settings)
    elif len(collect_ifs) > 0:
        assert _sum_collect_prioritizer is None, "cannot use _sum_collect_prioritizer and 'collect_ifs' simultaneously."
        prioritizer = _make_gscp(collect_ifs, 'collect_ifs', **kw__collect_settings)
    else:
        prioritizer = _sum_collect_prioritizer
    return prioritizer

# gscp <--> "get sum collect priority"
def _gscp_only_equal(obj, index, _list_len=None):
    '''priority, given index matching obj in collection priority list kwarg, when priority_only=True, priority_equal=True'''
    return None if index is None else 1

def _gscp_only_nonequal(obj, index, list_len):
    '''priority, given index matching obj in collection priority list kwarg, when priority_only=True, priority_equal=False'''
    return None if index is None else (list_len - index)

def _gscp_nononly_equal(obj, index, _list_len=None):
    '''priority, given index matching obj in collection priority list kwarg, when priority_only=False, priority_equal=True'''
    return get_sum_collect_priority(obj) if index is None else DEFAULT_COLLECTION_PRIORITY_LARGEST + 1

def _gscp_nononly_nonequal(obj, index, list_len):
    '''priority, given index matching obj in collection priority list kwarg, when priority_only=False, priority_equal=False'''
    return get_sum_collect_priority(obj) if index is None else DEFAULT_COLLECTION_PRIORITY_LARGEST + (list_len - index)

_GSCP_ONLY_AND_EQUAL__TO__FUNC = {
#  (only, equal) : func
    (True , True ): _gscp_only_equal,
    (True , False): _gscp_only_nonequal,
    (False, True ): _gscp_nononly_equal,
    (False, False): _gscp_nononly_nonequal,
}

def _gscp_find_equals_polys(element_of_collect_polys, obj):
    '''returns whether obj matches element_of_collect_polys in the sense of polynomials, i.e. obj base equals element'''
    return equals(get_base_and_power(obj)[0], element_of_collect_polys)

def _gscp_find_equals_ifs(element_of_collect_ifs, obj):
    '''returns whether obj matches element_of_collect_ifs in the sense of functions, i.e. element_of_collect_if(obj)==True'''
    return element_of_collect_ifs(obj)

_GSCP_LIST_KWARG_TO_FIND_EQUALS = {
#   kwarg : func to use for 'equals' in find
    'collect_these': equals,
    'collect_polys': _gscp_find_equals_polys,
    'collect_ifs': _gscp_find_equals_ifs,
}

def _make_gscp(collect_list, collect_list_kwarg, 
               collect_priority_only=None, collect_priority_equal=None):
    '''returns a function f(obj) which gets sum collect priority of obj, assuming collect_list is nonempty.'''
    L = len(collect_list)
    eqfunc = _GSCP_LIST_KWARG_TO_FIND_EQUALS[collect_list_kwarg]
    pfunc = _GSCP_ONLY_AND_EQUAL__TO__FUNC[(bool(collect_priority_only), bool(collect_priority_equal))]
    def prioritizer(obj):
        '''prioritizer func corresponding to the (already-provided) collect list.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        index = find(collect_list, obj, default=None, equals=eqfunc)
        return pfunc(obj, index, L)
    return prioritizer


''' --------------------- SUM_COLLECT FUNCTION --------------------- '''

simplify_op_skip_for(Sum, '_sum_collect')   # _sum_collect_greedy instead.

@simplify_op(Sum, alias='_collect')
@format_docstring(paramdocs=_gscp_paramdocs, takes_a_local_view_on_priorities=_local_view_on_priorities_docs)
def _sum_collect(self, collect_these=[], collect_polys=[], collect_ifs=[],
                 collect_priority_only=False, collect_priority_equal=False, 
                 _sum_collect_prioritizer=None, **kw__None):
    '''collect routine for sum, taking into account obj._sum_collect_priority of factors.
    {takes_a_local_view_on_priorities}

    By default, checks all factors, prioritized via factor._sum_collect_priority (or 0 if not provided).
    This default behavior can be changed via any of the kwargs below:

    {paramdocs}
    '''
    prioritizer = _get_gscp(collect_these=collect_these, collect_polys=collect_polys, collect_ifs=collect_ifs,
            collect_priority_only=collect_priority_only, collect_priority_equal=collect_priority_equal,
            _sum_collect_prioritizer=_sum_collect_prioritizer,
            )
    return _sum_collect_prioritized(self, _sum_collect_prioritizer=prioritizer, **kw__None)