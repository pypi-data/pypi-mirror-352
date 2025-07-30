"""
Package Purpose: Miscellaneous quality-of-life functions.
This package is intended to provide functions which:
- are helpful for solving specific, small problems
- could be useful in other projects as well
    i.e., these should not depend on other parts of SymSolver.
    (One exception: they may depend on the default values in defaults.py)

This file:
Imports the main important objects throughout this subpackage.
"""

from .arrays import (
    iter_array, itarrayte,
    array_expand_elements,
    ObjArrayInfo, NumArrayInfo,
    stats, array_info, array_info_str,
    array_max, array_min,
    array_argmax, array_argmin,
    slicer_at_ax, slice_at_ax, ax_to_abs_ax,
    array_select_max_imag, array_select_min_imag,
    array_select_max_real, array_select_min_real,
    looks_flat, nest_shape,
)
from .comparisons import (
    skiperror_min, skiperror_max, min_number, max_number,
    similarity, very_similar, maybe_similar, not_similar,
)
from .dicts import (
    dictlike_in_attr, Dict,
    Binning,
)
from .display import (
    _repr, _str, view,
    ViewRateLimiter,
    Viewable, viewlist, viewtuple, viewdict,
    view_after_message,
    short_repr, _str_nonsymbolic,
    lightweight_maybe_viewer, MaybeViewer, maybe_viewer,
    print_clear,
    help_str,
)
from .equality import (
    equals,
    list_equals, dict_equals, unordered_list_equals, equal_sets,
    int_equals,
)
from .finds import (
    find, multifind,
    argmin, argmax,
    FastFindable, fastfindlist, fastfindtuple, fastfindviewlist, fastfindviewtuple,
)
from .history import (
    git_hash_local, git_hash, git_hash_here, git_hash_SymSolver,
)
from .imports import (
    ImportFailed,
    enable_reload, reload,
    import_relative,
)
from .iterables import (
    is_iterable, is_dictlike,
    argsort, nargsort, argsort_none_as_small, argsort_none_as_large, sort_by_priorities,
    counts, counts_idx, counts_sublist_indices, pop_index_tracker, _list_without_i,
    default_sum,
    dichotomize, categorize, Categorizer, group_by,
    walk, deep_iter, walk_depth_first, walk_breadth_first,
    layers, structure_string,
    appended_unique,
    Container, ContainerOfList, ContainerOfArray, ContainerOfDict,
)
from .numbers import (
    is_integer, is_number, is_real_number, is_real_negative_number,
    infinity, INF, INFINITY,
    POS_INFINITY, POS_INF, PLUS_INF, PLUS_INFINITY,   # aliases for INF
    NEG_INFINITY, NEG_INF, MINUS_INF, MINUS_INFINITY, # aliases for -INF
    isqrt, isqrt_and_check, isqrt_if_square,
)
from .multiprocessing import (
    Task,
    CrashIfCalled, UniqueTask, UNSET_TASK, identity, IdentityTask,
    TaskContainer, TaskList, TaskArray,
    TaskContainerCallKwargsAttrHaver,
    TaskGroup, TaskPartition,
    mptest_add100, mptest_sleep, mptest_sleep_add100, mptest_echo,
    check_pickle, copy_via_pickle,
    _paramdocs_tasks,
)
from .oop_tools import (
    bind_to, Binding,
    StoredInstances,
    apply,
    caching_attr_simple, caching_attr_simple_if, caching_with_state,
    caching_attr_with_params_if, caching_attr_with_params_and_state_if,
    caching_property_simple,
    CallablesTracker,
    maintain_attrs, MaintainingAttrs,
    CustomNewDoesntInit,
    Singleton,
    operator_from_str, BINARY_MATH_OPERATORS,
    OpClassMeta, Opname_to_OpClassMeta__Tracker, Opname_to_Classes__Tracker,
)
from .plots import (
    centered_extent, centered_extent_from_extent, centered_extent1D,
    get_symlog_ticks, evenly_spaced_idx,
    colors_from_cmap,
    extended_cmap, cmap_extended,
    with_colorbar_extend, _colorbar_extent, _set_colorbar_extend,
    make_colorbar_axes, make_cax, make_colorbar_axis,
    colorbar,
    MaintainAxes,
)
from .properties import (
    alias, alias_to_result_of, alias_child, alias_in,
    simple_property, simple_setdefault_property, simple_setdefaultvia_property,
    weakref_property_simple,
)
from .pytools import (
    format_docstring,
    value_from_aliases,
    assert_values_provided,
    printsource,
    inputs_as_dict, _inputs_as_dict__maker,
    get_locals_up,
    _identity_function,
    documented_namedtuple,
    weakref_property_simple,
    format_,
)
from .sentinels import (
    Sentinel,
    UNSET, NO_VALUE, RESULT_MISSING,
)
from .sets import (
    Set,
)
from .timing import (
    Profile,
    PROFILE, profiling, print_profile,
    Stopwatch, TickingWatch,
    ProgressUpdater,
    TimeLimit,
)