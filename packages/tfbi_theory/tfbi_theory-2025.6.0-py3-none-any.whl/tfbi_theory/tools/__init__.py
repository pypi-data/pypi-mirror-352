"""
Package purpose: misc tools; portable (not specific to tfbi_theory).
"""
from .grids import (
    xarray_range, XarrayGrid, xarray_grid, xarray_angle_grid,
    vector_from_polar,
)
from .imports import (
    enable_reload, reload,
    import_relative,
    ImportFailed,
)
from .properties import (
    alias, alias_to_result_of, alias_child, alias_key_of, alias_in,
    weakref_property_simple,
    simple_property, simple_tuple_property,
    simple_setdefault_property, simple_setdefaultvia_property,
    elementwise_property,
    simple_cachef_property,
)
from .pytools import (
    format_docstring,
    printsource, displaysource,
    is_iterable,
    inputs_as_dict, _inputs_as_dict__maker,
    value_from_aliases,
    help_str, print_help_str, _help_str_paramdocs,
    indent_doclines, indent_paramdocs,
)
from .sentinels import (
    Sentinel,
    UNSET, NO_VALUE, ATTR_UNSET, RESULT_MISSING,
)
from .timing import (
    Profile,
    PROFILE, profiling, print_profile,
    Stopwatch, TickingWatch,
    ProgressUpdater,
    TimeLimit,
)
from .xarrays import (
    # dimensions
    xarray_promote_dim, xarray_ensure_dims,
    xarray_drop_unused_dims, xarray_drop_vars,
    # broadcasting
    xarray_broadcastable_array, xarray_broadcastable_from_dataset,
    xarray_from_broadcastable,
    # copying
    xarray_copy_kw,
    # indexing
    xarray_search, xarray_sel,
)