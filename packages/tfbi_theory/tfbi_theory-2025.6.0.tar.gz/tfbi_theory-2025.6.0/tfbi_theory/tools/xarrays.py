"""
File Purpose: tools related to xarray stuff.
"""
import numpy as np
import xarray as xr

from .pytools import format_docstring
from ..errors import DimensionKeyError, DimensionValueError, DimensionalityError


''' --------------------- Docstrings --------------------- '''

_paramdocs_ensure_dims = {
    'promote_dims_if_needed': '''bool
        whether to promote non-dimension coords to dimensions.
        if False, raise DimensionKeyError if any relevant coord is not already a dimension.''',
    'missing_dims': '''str in ('ignore', 'warn', 'raise')
        what to do if any coord is not found:
            'ignore' --> do nothing.
            'warn' --> raise a warning.
            'raise' --> raise DimensionKeyError.''',
}


''' --------------------- Dimensions --------------------- '''

def is_iterable_dim(value, *, min_length=None):
    '''returns whether value represents multiple values (of a dimension).

    if value.ndim exists,
        return False if ndim==0,
        else True if ndim > 0,
        else raise DimensionValueError.
    # else, return whether iter(value) succeeds.  # <-- no longer used; use is_scalar from xr.
    else, return (not xr.core.utils.is_scalar(value))

    min_length: None or int
        if provided, before returning True, require that len(value) >= min_length.
    '''
    if hasattr(value, 'ndim'):
        ndim = value.ndim
        if ndim == 0:
            result = False
        elif ndim > 0:
            result = True
        else:
            raise DimensionValueError(f"expected ndim >= 0, but got ndim={ndim}.")
    else:
        result = (not xr.core.utils.is_scalar(value))
    if result and (min_length is not None):
        try:
            L = len(value)
        except TypeError:
            result = False  # couldn't determine length, so assume it's not long enough.
        else:
            result = result and (L >= min_length)
    return result

def xarray_promote_dim(array, coord, *coords_as_args):
    '''Promote this coord (or these coords) to be a dimension, if it isn't already.
    
    coord: str or iterable of strs
        name of coord(s) to promote.
        if already in array.dims, do nothing.
        if 0D, array.expand_dims(coord).
                (This occurs when coord has no associated dimension, in array.)
        if 1D, array.swap_dims(dict(dim=coord)),
                where dim is the dimension associated with coord.
        if 2D+, crash with DimensionalityError.

    returns array, or a copy of array where coord is one of the dimensions.
    '''
    coords = [coord] if isinstance(coord, str) else coord
    coords = list(coords) + list(coords_as_args)
    to_expand = []
    to_swap = {}
    for coord in coords:
        if coord in array.dims:
            continue  # no need to promote this dim.
        c = array.coords[coord]
        cdims = c.dims
        if len(cdims) == 0:
            to_expand.append(coord)
        elif len(cdims) == 1:
            d = cdims[0]
            if d in to_swap:
                errmsg = (f'multiple coords ({to_swap[d]!r}, {coord!r}) with same dimension ({d!r}), '
                            'cannot promote both of them at the same time.')
                raise DimensionKeyError(errmsg)
            to_swap[d] = coord
        else:
            errmsg = f'cannot promote_dim(coord={coord!r}) for coord with >1 dims: {cdims}'
            raise DimensionalityError(errmsg)
    if 0 == len(to_expand) == len(to_swap):
        return array  # nothing to change.
    array = array.expand_dims(tuple(to_expand))
    array = array.swap_dims(to_swap)
    return array

@format_docstring(**_paramdocs_ensure_dims)
def xarray_ensure_dims(array, coords, *,
                       promote_dims_if_needed=True, missing_dims='raise',
                       assert_1d=False, return_existing_dims=False):
    '''return array but ensure these coords are dimensions.

    coords: str or iterable of strings
        coords to ensure are dimensions.
    promote_dims_if_needed: {promote_dims_if_needed}
            0D coord --> array.expand_dims(coord)
            1D coord --> array.swap_dims(dict(dim=coord)) for associated dim
            2D+ coord --> crash with DimensionalityError.
    missing_dims: {missing_dims}
    assert_1d: bool, default False
        whether to assert that each of these coords is 1D (after promoting if needed).
    return_existing_dims: bool, default False
        True --> returns [array, set of dims (from input coords) which actually exist]
        probably only useful if missing_dims != 'raise'.
    '''
    if isinstance(coords, str):
        coords = [coords]
    found_missing_dims = set()
    # promote coords
    for cname in coords:
        if promote_dims_if_needed and cname in array.coords:
            array = xarray_promote_dim(array, cname)
        if cname not in array.dims:
            found_missing_dims.add(cname)
            continue
        if assert_1d:
            c = array.coords[cname]
            if c.ndim != 1:
                errmsg = f'ensure_dims expected 1D coord={cname!r}, but got ndim={c.ndim}.'
                raise AssertionError(errmsg)
    # handle missing dims
    if len(found_missing_dims) > 0:
        if missing_dims not in ('ignore', 'warn', 'raise'):
            errmsg = f'invalid missing_dims={missing_dims!r}. Expected "ignore", "warn" or "raise".'
            raise InputError(errmsg)
        if missing_dims =='raise' or missing_dims == 'warn':  # define the error message
            c_or_d = 'coords' if promote_dims_if_needed else 'dims'
            errmsg = (f'Dimensions {found_missing_dims} not found in '
                      f'array.{c_or_d}={set(getattr(array, c_or_d))},\n'
                      f'and missing_dims={missing_dims!r} (using "ignore" would ignore this instead).')
            if missing_dims == 'raise':
                raise DimensionKeyError(errmsg)
            elif missing_dims == 'warn':
                warnings.warn(errmsg)
    # return result
    if return_existing_dims:
        existing_dims = set(coords) - found_missing_dims
        return array, existing_dims
    else:
        return array

def xarray_drop_unused_dims(dataset):
    '''dataset.drop_dims(dims which do not appear in any of the data_vars).'''
    used_dims = set()
    for v in dataset.data_vars:
        used_dims.update(dataset[v].dims)
    unused_dims = set(dataset.dims) - used_dims
    return dataset.drop_dims(unused_dims)

def xarray_drop_vars(dataset, names, *, errors='ignore', drop_unused_dims=True):
    '''dataset.drop_vars(names, errors=errors), then drop any unused dims.
    errors: 'ignore' or 'raise'
        what to do if any name not found in dataset.
        (passed directly to dataset.drop_vars)
    drop_unused_dims: bool
        whether to xarray_drop_unused_dims(result).
        True --> drop any dims which are no longer used by any remaining data_vars.
    '''
    result = dataset.drop_vars(names, errors=errors)
    if drop_unused_dims:
        result = xarray_drop_unused_dims(result)
    return result


''' --------------------- Broadcasting --------------------- '''

def xarray_broadcastable_array(array, dims):
    '''return broadcastable version of array, standardizing dims to the list provided.
    missing dims will be expanded to size 1. result dims will be put in this order.

    dims: list of str
        result will have all these dims, in this order, with size 1 if not present in array.
        if any array.dims not present in dims, raise DimensionKeyError.
    '''
    extra_dims = set(array.dims) - set(dims)  # dims in array
    if extra_dims:
        errmsg = (f'array not broadcastable to input dims={dims}, '
                  f'due to {extra_dims} in array.dims but not input dims.')
        raise DimensionKeyError(errmsg)
    missing_dims = tuple(set(dims) - set(array.dims))
    if missing_dims:
        array = array.expand_dims(missing_dims)
    return array.transpose(*dims)

def xarray_broadcastable_from_dataset(dataset, var=None, *, dims=None):
    '''return broadcastable versions of data_var(s) from dataset, standardizing data vars' dims.
    missing dims will be expanded to size 1. result's dims will be put in order.

    var: None, str, or list of str.
        str --> return a broadcastable version of this data_var. Result is an xarray.DataArray.
        list of str --> return dict of {v: broadcastable version of v} across v in var.
        None --> use var = list(dataset.keys())
    dims: None or list of str
        result will have all these dims, in this order, with size 1 if not present in array.
        if any array.dims not present in dims, raise DimensionKeyError.
        None --> use dataset.dims.
    '''
    if dims is None:
        dims = dataset.dims
    if isinstance(var, str):
        return xarray_broadcastable_array(dataset[var], dims)
    # else, return dict of {v: broadcastable version of v} across v in var.
    result = {}
    if var is None:
        var = list(dataset.keys())
    for v in var:
        result[v] = xarray_broadcastable_array(dataset[v], dims)
    return result

def xarray_from_broadcastable(array, broadcastable, *, dims=None, squeeze=True):
    '''return xarray from broadcastable values, using dims/coords/attrs from input.

    array: xarray.DataArray or xarray.Dataset
        read relevant dims, coords, and attrs from this array; copy to result.
    broadcastable: array (possibly numpy array) or dict of arrays
        result's data comes from this array(s).
        single array --> result.data = array.
        dict of arrays --> result.data = array[v] for v in array.  # [TODO] not yet implemented.
    dims: None or list of str
        list of dim names for broadcastable's dims. len(dims) == broadcastable.ndim.
        None --> use array.dims.
    squeeze: bool
        whether to squeeze away dims with size 1 in broadcastable.
        True --> result.dims will only include dims with size > 1 in broadcastable.
    '''
    if dims is None:
        dims = array.dims
    if isinstance(broadcastable, dict):
        raise NotImplementedError('xarray_from_broadcastable not yet implemented for dict inputs.')
    # else, broadcastable is a single array.
    shape = broadcastable.shape
    if len(dims) != len(shape):
        errmsg = f'length of broadcastable shape ({shape}) != length of input dims ({dims}).'
        raise DimensionalityError(errmsg)
    relevant_dims = [d for d, s in zip(dims, shape) if s > 1]
    kw = xarray_copy_kw(array, dims=relevant_dims)
    if squeeze:
        broadcastable = np.squeeze(broadcastable)
    else:
        kw['dims'] = dims  # using all dims not just relevant dims.
    return xr.DataArray(broadcastable, **kw)


''' --------------------- Coords --------------------- '''

def xarray_copy_kw(array, dims=None):
    '''return dict of info suitable for creating a similar array or dataset.
    result includes dims, coords, and attrs (unchanged, copied).

    dims: None, str, or iterable of str
        if provided, only include these dims (and related coords) in the result.
        Useful if only interested in some of the dims,
            e.g. if array has x,y,z,t dims but only want to mimic dims and coords from x,t.
    '''
    if isinstance(dims, str): dims = [dims]
    if dims is None: dims = array.dims
    elif any(d not in array.dims for d in dims):
        errmsg = (f'cannot copy_kw for dims={dims!r} because some dims not in array.dims={array.dims}.')
        raise DimensionKeyError(errmsg)
    coords = dict()
    for cname, cval in array.coords.items():
        if len(cval.dims) == 0:  # scalar coord; always keep!
            coords[cname] = cval
        elif len(cval.dims) == 1 and cval.dims[0] in dims:  # 1D coord, and relevant
            coords[cname] = cval
        elif all(d in dims for d in cval.dims):  # 2D+ coord, and all relevant dims exist
            coords[cname] = (tuple(cval.dims), cval.data)
    attrs = array.attrs.copy()
    return dict(dims=dims, coords=coords, attrs=attrs)


''' --------------------- Indexing --------------------- '''

def xarray_search(array, dim, value):
    '''return first index of value along dim
    (or coord. returns 0, not crash, if scalar coord which matches value.)
    Not efficient for large dims. For large sorted dims, see xarray.DataArray.searchsorted.

    crash with DimensionValueError if value not found in dim.
    '''
    for i, val in enumerate(np.atleast_1d(array.coords[dim].values)):
        if val == value:
            return i
    raise DimensionValueError(f'value={value!r} not found in array[{dim!r}]')

_sel_doc = xr.DataArray.sel.__doc__
if 'Examples\n' in _sel_doc:  # gives docstring with Examples removed
    _sel_doc = _sel_doc[:_sel_doc.index('Examples\n')].rstrip()
if 'Returns\n' in _sel_doc:  # gives docstring with Returns removed
    _sel_doc = _sel_doc[:_sel_doc.index('Returns\n')].rstrip()

@format_docstring(sel_doc=_sel_doc, **_paramdocs_ensure_dims)
def xarray_sel(array, indexers=None, *, promote_dims_if_needed=True,
               method=None, tolerance=None, drop=False, **indexers_as_kwargs):
    '''array.sel(...) but prioritize general applicability over efficiency:
        - promote non-dimension coordinate dims first if applicable
        - (if coord.dtype is object) check coord equality,
            e.g. 0==Fluid('e', 0)=='e', so could use Fluid('e', 0), 'e', or 0 in sel.
            - can also use list, tuple, or 1D non-string iterable,
                e.g. ['e', 3, 'Fe+'] to get multiple fluids.
            - can also use slice,
                e.g. slice('e', 'Fe+', 2) to get every other fluid,
                starting from 'e', stopping before the first 'Fe+' match.

    Assumes all indexing is for 1D dims. For indexing 2D+ dims, use xarray methods directly.

    promote_dims_if_needed: {promote_dims_if_needed}
    method: None or str
        method to use for inexact matches, for non-object dtype coords.

    xarray.DataArray.sel docs copied below:
    ----------------------------------------
        {sel_doc}
    '''
    if indexers is None:
        indexers = indexers_as_kwargs
    else:
        indexers = {**indexers, **indexers_as_kwargs}
    indexers_input = indexers
    sel_indexers = dict()  # indexing to delegate to xarray.sel
    obj_indexers = dict()  # indexing to handle here
    array_input = array  # <-- helps with debugging in case of crash.
    kw_ensure_dims = dict(promote_dims_if_needed=promote_dims_if_needed, missing_dims='raise',
                          assert_1d=True,  # because here doesn't implement any way to index 2D+ dims.
                          return_existing_dims=True,  # so we can avoid indexing any missing dims!
                          )
    array, existing_dims = xarray_ensure_dims(array, list(indexers_input.keys()), **kw_ensure_dims)
    for cname in existing_dims:
        if array[cname].dtype == object:
            obj_indexers[cname] = indexers_input[cname]
        else:
            sel_indexers[cname] = indexers_input[cname]
    # handle obj_indexers first.
    obj_isels = {}
    if len(obj_indexers) > 0:
        if method is not None:
            raise TypeError(f'cannot use method {method!r} with object dtype coords {list(obj_indexers)}.')
        for cname, index in obj_indexers.items():
            if is_iterable_dim(index):
                isel_here = []
                for ival in index:
                    isel_here.append(xarray_search(array, cname, ival))
                obj_isels[cname] = isel_here
            elif isinstance(index, slice):
                start, stop, step = index.start, index.stop, index.step
                istart, istop = None, None
                if start is not None:
                    istart = xarray_search(array, cname, start)
                if stop is not None:
                    istop = xarray_search(array, cname, stop)
                obj_isels[cname] = slice(istart, istop, step)
            else:  # index is a single value for a dim
                obj_isels[cname] = xarray_search(array, cname, index)
    array = array.isel(obj_isels, drop=drop)
    # handle sel_indexers
    return array.sel(sel_indexers, method=method, tolerance=tolerance, drop=drop)