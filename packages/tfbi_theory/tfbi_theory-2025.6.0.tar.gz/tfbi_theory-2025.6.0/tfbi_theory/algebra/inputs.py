"""
File Purpose: managing inputs to the TFBI
"""
import numpy as np
import xarray as xr

import SymSolver as ss

from .vars import load_vars, TFBI_SS_PRESETS
from ..errors import (
    InputError, InputMissingError, InputConflictError,
    DimensionError,
)
from ..tools import (
    alias_child,
    UNSET,
    format_docstring,
    is_iterable,
    xarray_grid, xarray_angle_grid, vector_from_polar,
    xarray_sel,
    xarray_broadcastable_array,
    xarray_drop_vars,
)


# load variables DIRECTLY INTO LOCALS().
load_vars(locals())


''' --------------------- Tools for picking k values --------------------- '''

class kPicker():
    '''helps to choose k values.

    k can have any variation across any dimensions (thanks to xarray!),
        but must at least vary across 'component' dim, with:
        k.isel(component=0): k parallel to E_un0 (E in the u_neutral=0 frame).
        k.isel(component=1): k parallel to -E_un0 cross B.

    self.k tells currently picked values of k.
    self.kx is a shorthand for k.isel(component=0)
    self.ky is a shorthand for k.isel(component=1)

    use self.pick_mod() and self.pick_ang() for convenient methods to set mod and ang.

    ds: None or xarray.Dataset
        dataset containing inputs for TFBI, possibly also containing ldebye and/or lmfp.
    mod: UNSET, None, dict, or xarray.DataArray
        magnitude of k, i.e. |k|.
        UNSET --> use self.DEFAULT_MOD (here, None. Subclass might set new defaults.)
        None --> must be provided later before getting self.k.
        dict --> use self.pick_mod(**mod) to set mod.
            provide an empty dict to use the defaults. (Subclass might set new defaults.)
                DEFAULT_MOD_MIN = 2 * np.pi / 1e3 
                DEFAULT_MOD_MAX = (0.1, 'kminmax')
                DEFAULT_MOD_N = None  # (require user to input this value)
                DEFAULT_MOD_LOGSPACE = True
    lmod: UNSET, None or dict
        UNSET --> use self.DEFAULT_LMOD (here, None. Subclass might set new defaults.)
        if dict, use self.pick_lmod(**lmod) to set mod.
        (provide an empty dict to use the defaults, see above^)
    ang: UNSET, None, dict, or xarray.DataArray
        angle [in radians] of k with respect to the +x axis.
        UNSET --> use self.DEFAULT_ANG (here, None. Subclass might set new defaults.)
        None --> must be provided later before getting self.k.
        dict --> use self.pick_ang(**ang) to set ang.
            provide an empty dict to use the defaults. (Subclass might set new defaults.)
                DEFAULT_DEGSPAN = 180
                DEFAULT_DEGSTEP = None  # (require user to input this value)

    Can be inferred from ds if not provided directly:
    ldebye; kdebye: None, str, tuple of str, number, or xarray.DataArray
        debye length; 2 * np.pi / ldebye.
        self.pick_mod() allows to use 'kdebye' as shorthand for max.
        str or tuple of str --> use ds[first available string] if possible, else None.
        None --> use self.KEY_ALIASES.get('ldebye') and .get('kdebye').
                (if still None, treat as "not provided")
        Provide ldebye or kdebye but not both.
    lmfp, kmfp: None, str, tuple of str, number, or xarray.DataArray
        collisional mean free path; 2 * np.pi / lmfp.
        self.pick_mod() allows to use 'kmfp' as shorthand for max.
        str or tuple of str --> use ds[first available string] if possible, else None.
        None --> use self.KEY_ALIASES.get('lmfp') and .get('kmfp').
                (if still None, treat as "not provided")
        Provide lmfp or kmfp but not both.
    '''
    KEY_ALIASES = {
        'ldebye': ('ldebye', 'eqperp_ldebye'),
        'lmfp': ('lmfp', 'eqperp_lmfp', 'mean_free_path', 'eqperp_mean_free_path'),
    }

    DEFAULT_MOD = None
    DEFAULT_LMOD = None
    DEFAULT_ANG = None

    DEFAULT_DEGSPAN = 180
    DEFAULT_DEGSTEP = None
    DEFAULT_MOD_MIN = 2 * np.pi / 1e3   # default min k corresponds to max scale size = 1e3 meters
    DEFAULT_MOD_MAX = (0.1, 'kminmax')  # default max k corresponds to min scale size = 10 * max(lmfp, ldebye)
    DEFAULT_MOD_N = None
    DEFAULT_MOD_LOGSPACE = True

    DEFAULT_MOD_FLUID = None
    DEFAULT_MOD_IFLUID = None
    DEFAULT_REDUCE_FLUIDS = False

    def __init__(self, ds=None, *, mod=UNSET, lmod=UNSET, ang=UNSET,
                 ldebye=None, kdebye=None, lmfp=None, kmfp=None):
        if mod is UNSET: mod = self.DEFAULT_MOD
        if lmod is UNSET: lmod = self.DEFAULT_LMOD
        if ang is UNSET: ang = self.DEFAULT_ANG
        if (mod is not None) and (lmod is not None):
            raise InputConflictError("cannot provide both mod and lmod.")
        self.ds = ds
        self.mod = mod
        self.ang = ang
        self.init_fluid_dim()
        self.init_kdebye(ldebye=ldebye, kdebye=kdebye)
        self.init_kmfp(lmfp=lmfp, kmfp=kmfp)
        if isinstance(mod, dict):
            self.pick_mod(**mod)
        elif isinstance(lmod, dict):
            self.pick_lmod(**lmod)
        if isinstance(ang, dict):
            self.pick_ang(**ang)

    def init_fluid_dim(self):
        '''initialize self.fluid_dim = 'fluid' or 'fluid_sort',
        whichever appears in self.ds. (At least 1 must appear in self.ds.dims.)
        '''
        if 'fluid' in self.ds.dims:
            self.fluid_dim = 'fluid'
        elif 'fluid_sort' in self.ds.dims:
            self.fluid_dim = 'fluid_sort'
        else:
            raise InputError("Expected 'fluid' or 'fluid_sort' dim in ds.")

    def init_kdebye(self, ldebye=None, kdebye=None):
        '''set self.kdebye appropriately based on ldebye, kdebye, and self.ds.'''
        if self.ds is not None:
            if ldebye is None: ldebye = self.KEY_ALIASES.get('ldebye', None)
            if kdebye is None: kdebye = self.KEY_ALIASES.get('kdebye', None)
            if isinstance(ldebye, str): ldebye = (ldebye,)
            if isinstance(kdebye, str): kdebye = (kdebye,)
            if isinstance(ldebye, tuple):
                ldebye = next((self.ds[key] for key in ldebye if key in self.ds), None)
            if isinstance(kdebye, tuple):
                kdebye = next((self.ds[key] for key in kdebye if key in self.ds), None)
        if kdebye is not None and ldebye is not None:
            raise InputConflictError("cannot provide both kdebye and ldebye.")
        self.kdebye = kdebye
        if ldebye is not None:
            self.ldebye = ldebye

    def init_kmfp(self, lmfp=None, kmfp=None):
        '''set self.kmfp appropriately based on lmfp, kmfp, and self.ds.'''
        if self.ds is not None:
            if lmfp is None: lmfp = self.KEY_ALIASES.get('lmfp', None)
            if kmfp is None: kmfp = self.KEY_ALIASES.get('kmfp', None)
            if isinstance(lmfp, str): lmfp = (lmfp,)
            if isinstance(kmfp, str): kmfp = (kmfp,)
            if isinstance(lmfp, tuple):
                lmfp = next((self.ds[key] for key in lmfp if key in self.ds), None)
            if isinstance(kmfp, tuple):
                kmfp = next((self.ds[key] for key in kmfp if key in self.ds), None)
        if kmfp is not None and lmfp is not None:
            raise InputConflictError("cannot provide both kmfp and lmfp.")
        self.kmfp = kmfp
        if lmfp is not None:
            self.lmfp = lmfp

    # # # PROPERTIES # # #
    @property
    def k(self):
        '''k, an xarray.DataArray with dims ('component', 'kang', 'kmod' or 'log_kmod'),
        possibly additional dims or coords as well, depending on inputs.
        Fails if either ang or mod not provided yet. (see also: self.pick_ang, self.pick_mod)

        recalculates every time this is accessed; for efficiency may want to store result somewhere.
        setting self.k = value is prohibited.
        del self.k resets self.ang and self.mod to None.
        '''
        return self.get_k()
    @k.setter
    def k(self, value):
        raise AttributeError("k is read-only. Use self.pick_ang() and self.pick_mod() to set ang and mod.")
    @k.deleter
    def k(self):
        self.ang = None
        self.mod = None

    def get_k(self, component=['Ehat', '-ExBhat']):
        '''return k, an xarray.DataArray with dims ('component', 'kang', 'kmod' or 'log_kmod'),
        possibly additional dims or coords as well, depending on inputs.
        Fails if either ang or mod not provided yet. (see also: self.pick_ang, self.pick_mod)
        '''
        if self.ang is None:
            raise InputMissingError("ang must be provided before getting k. Consider using self.pick_ang()")
        if self.mod is None:
            raise InputMissingError("mod must be provided before getting k. Consider using self.pick_mod()")
        k = vector_from_polar(self.mod, self.ang, component=component)
        return k

    kx = property(lambda self: self.k.isel(component=0),
                  doc="k parallel to E_un0 (E in the u_neutral=0 frame)")
    ky = property(lambda self: self.k.isel(component=1),
                    doc="k parallel to -E_un0 cross B")

    lmfp = property(lambda self: None if self.kmfp is None else 2 * np.pi / self.kmfp,
                    doc="collisional mean free path. Note: lmfp = 2 * pi / kmfp")
    @lmfp.setter
    def lmfp(self, value):
        if value is not None:
            value = 2 * np.pi / value
            if getattr(value, 'name', None) is not None:
                value = value.rename(value.name.replace('lmfp', 'kmfp'))
        self.kmfp = value

    ldebye = property(lambda self: None if self.kdebye is None else 2 * np.pi / self.kdebye,
                      doc="debye length. Note: ldebye = 2 * pi / kdebye")
    @ldebye.setter
    def ldebye(self, value):
        if value is not None:
            value = 2 * np.pi / value
            if getattr(value, 'name', None) is not None:
                value = value.rename(value.name.replace('ldebye', 'kdebye'))
        self.kdebye = value

    @property
    def kminmax(self):
        '''return pointwise minimum of all likely k max bounds: self.kmfp and self.kdebye.
        if either is None, return None. (This is the most restrictive max k bound.)
        '''
        if self.kmfp is None or self.kdebye is None:
            return None
        else:
            return np.minimum(self.kmfp, self.kdebye).rename('kminmax')

    @property
    def lmaxmin(self):
        '''return pointwise maximum of all likely l min bounds: self.lmfp and self.ldebye.
        if either is None, return None. (This is the most restrictive min l bound.)
        '''
        if self.lmfp is None or self.ldebye is None:
            return None
        else:
            return np.maximum(self.lmfp, self.ldebye).rename('lmaxmin')

    # # # PICKING K # # #
    def get_ds(self):
        '''gets a copy of self.ds but after assigning self.k as data_var 'k'.'''
        return self.ds.assign(k=self.k)

    def pick_ang(self, min=-90, max=None, N=None, *, rad_in=False,
                 step=None, degstep=None, radstep=None,
                 span=None, degspan=None, radspan=None,
                 inclusive=None, **kw_angle_grid):
        '''pick and return angle values [in radians], also setting self.ang = result.
        result dim & name will always be 'kang'.

        if min or max is None and no span params are provided,
            here will use degspan = self.DEFAULT_DEGSPAN (default=180)
        if N is None and no step params are provided,
            here will use degstep = self.DEFAULT_DEGSTEP (default=5)

        min, max: None or number
            min and max angle values.
            None --> infer from span
        N: None or number
            number of points in grid. None = "unspecified"
        rad_in: bool
            whether the inputs are in radians (if True) or degrees (if False).
        step: None or number
            step size between points, in same units as input (depends on rad_in). None = "unspecified"
        radstep: None or number
            step size between points, in radians. None = "unspecified"
        degstep: None or number
            step size between points, in degrees. None = "unspecified"
        span: None or number
            max - min, in same units as input (depends on rad_in). None = "unspecified"
        radspan: None or number
            max - min, in radians. None = "unspecified"
        degspan: None or number
            max - min, in degrees. None = "unspecified"
        inclusive: None or 2-tuple of bool
            whether to include min and max values.
            None --> use (False, True) if min < 0 else (True, False).

        Any additional kwargs are passed directly to xarray_angle_grid().
        '''
        if (min is None or max is None) and (span is None and degspan is None and radspan is None):
            degspan = self.DEFAULT_DEGSPAN
        if (N is None) and (step is None and degstep is None and radstep is None):
            degstep = self.DEFAULT_DEGSTEP
        kw_pass = dict(N=N, step=step, degstep=degstep, radstep=radstep,
                          span=span, degspan=degspan, radspan=radspan, **kw_angle_grid)
        if inclusive is None:
            if min is None or callable(min):
                inclusive = (True, False)
            else:
                inclusive = (False, True) if (min < 0) else (True, False)
        kw_here = dict(inclusive=inclusive, name='kang')
        self.ang = xarray_angle_grid(min, max, **kw_pass, **kw_here)
        return self.ang

    def pick_mod(self, min=None, max=None, N=None, *, logspace=None,
                 fluid=UNSET, ifluid=UNSET, reduce_fluids=UNSET, step=None, span=None, ratio=None,
                 logstep=None, inclusive=(True, True), **kw_xarray_grid):
        '''pick and return magnitude values, also setting self.mod = result.
        result name will always be 'kmod'.
        result dim will be 'kmod' if min and max are 1D;
            it will be 'kmod_dim' if min or max are arrays.
            Either way, will always have result['kmod'].equals(result).

        if min or max is None, when span and ratio are both unspecified,
            use defaults as needed: min = self.DEFAULT_MOD_MIN; max = self.DEFAULT_MOD_MAX.
        if N is None, when step and logstep are both unspecified,
            use default: N = self.DEFAULT_MOD_N.
        if logspace is None, and provided N (not step or logstep),
            use default: logspace = self.DEFAULT_MOD_LOGSPACE (default=True)

        min, max: None, number, str, tuple of (number, str), or callable, xarray.DataArray
            min & max values, always in linear space.
            number --> use as is.
            tuple --> must be (number, str); replace with number * (limit implied by str)
            str --> must be 'kmfp', 'kdebye', 'kminmax'; replace with corresponding attribute from self.
                kmfp = 2pi/(collisional mean free path)
                kdebye = 2pi/(debye length)
                kminmax = min(kmfp, kdebye), the most restrictive possible bound.
            callable f --> use min=f(max) or max=f(min). (cannot both be callable)

        fluid: UNSET, None, int, str, or other specifier for 'fluid' dimension
            if provided, and min or max is a DataArray with 'fluid' dimension,
            xarray_sel(min or max, fluid=fluid) to select the min or max.
            (k is NOT allowed to vary with fluid.)
            UNSET --> if ifluid also UNSET, use self.DEFAULT_MOD_FLUID.
        ifluid: UNSET, None, int, or indexer (e.g. slice) suitable for isel
            if provided, and min or max is a DataArray with 'fluid' or 'fluid_sort' dimension,
            use (min or max).isel(fluid=ifluid) to select the min or max.
            (k is NOT allowed to vary with fluid.)
            UNSET --> if fluid also UNSET, use self.DEFAULT_MOD_IFLUID.
        reduce_fluids: UNSET, False, 'nmean', or 'ldebye_tot'
            if min or max has 'fluid' dimension (after sel(fluid) or ifluid if appropriate),
            tells how to reduce the 'fluid' dimension.
            UNSET --> use self.DEFAULT_REDUCE_FLUIDS.
            False --> don't reduce 'fluid' dimension; crash instead.
            'nmean' --> take the density-weighted mean across all fluids.
                        Requires self.ds['n'] to exist and also have 'fluid' dimension.
            'ldebye_tot' --> convert as if doing 'ldebye_total':
                        ldebye_joined = sqrt( 1 / sum_fluids(1 / ldebye^2)).
                        Since this function is in k-space, we have:
                        klim_joined = sqrt(sum_fluids(klim^2)).

        all the other inputs are passed to xarray_grid(); see help(xarray_grid()) for details.
        '''
        if fluid is UNSET and ifluid is UNSET:
            fluid = self.DEFAULT_MOD_FLUID
            ifluid = self.DEFAULT_MOD_IFLUID
        if reduce_fluids is UNSET:
            reduce_fluids = self.DEFAULT_REDUCE_FLUIDS
        # bookkeeping
        if (min is None or max is None) and (span is None and ratio is None):
            if min is None: min = self.DEFAULT_MOD_MIN
            if max is None: max = self.DEFAULT_MOD_MAX
        if N is None and (step is None and logstep is None):
            N = self.DEFAULT_MOD_N
        if (logspace is None) and (N is not None and step is None and logstep is None):
            logspace = self.DEFAULT_MOD_LOGSPACE
        kw_pass = dict(N=N, step=step, span=span, ratio=ratio,
                       logspace=logspace, logstep=logstep, inclusive=inclusive,
                       **kw_xarray_grid)
        kw_here = dict(name='kmod')
        if fluid is not None and ifluid is not None:
            raise InputConflictError('cannot provide both fluid and ifluid.')
        # handle str and tuple inputs
        lims = [min, max]
        for i, lim, lname in [(0, min, 'min'), (1, max, 'max')]:
            safety = None
            if isinstance(lim, tuple):
                safety = lim[0]
                lim = lim[1]
            if isinstance(lim, str):
                if lim == 'kmfp':
                    lim = self.kmfp
                    if lim is None: raise InputMissingError(f"{lname}='kmfp' but self.kmfp is None.")
                elif lim == 'kdebye':
                    lim = self.kdebye
                    if lim is None: raise InputMissingError(f"{lname}='kdebye' but self.kdebye is None.")
                elif lim == 'kminmax':
                    lim = self.kminmax
                    if lim is None: raise InputMissingError(f"{lname}='kminmax' but self.kminmax is None.")
                else:
                    raise InputError(f"{lname}={lim!r} not recognized. Expected 'kmfp', 'kdebye', or 'kminmax'.")
            if safety is not None:
                lim = lim * safety
            lims[i] = lim
        min, max = lims
        # handle fluid dimension
        lims = [min, max]
        for i, lim, lname in [(0, min, 'min'), (1, max, 'max')]:
            lim = self.reduce_fluid_dim(lim, fluid=fluid, ifluid=ifluid, reduce_fluids=reduce_fluids)
            lims[i] = lim
        min, max = lims
        # result
        result = xarray_grid(min, max, **kw_pass, **kw_here)
        if 'fluid' in result.dims or 'fluid_sort' in result.dims:
            errmsg = ('k cannot vary with fluid or fluid_sort.\n'
                      '(probably min or max callable which added fluid dim...)')
            raise DimensionError(errmsg)
        self.mod = result
        return self.mod

    def pick_lmod(self, min=None, max=None, N=None, **kw_pick_mod):
        '''pick and return magnitude values for k, based on min & max for l.
        Roughly equivalent to self.pick_mod(min=max, max=min),
            but with string support here for l strings instead of k strings:

         min, max: None, number, str, tuple of (number, str), or xarray.DataArray
            min & max l values, always in linear space.
            number or DataArray --> use 2 * pi / value.
            tuple --> must be (number, str); replace with number * (limit implied by str)
            str --> must be 'lmfp', 'ldebye', 'lmaxmin'; replace with corresponding attribute from self.
                lmfp = collisional mean free path
                ldebye = debye length
                lmaxmin = max(lmfp, ldebye), the most restrictive possible bound.
            callable --> NOT supported here; see self.pick_mod instead.

        [implementation notes] steps here are:
            - swap min & max (since k = 2 * pi / l)
            - swap any strs to relevant k string
            - for any tuples, use 1/safety factor.
            - call self.pick_mod with the appropriately adjusted inputs.
            E.g. default min=(10, 'lmaxmin') corresponds to pick_mod(..., max=(1/10, 'kminmax'))
        '''
        STR_CONVERT = {'lmfp': 'kmfp', 'ldebye': 'kdebye', 'lmaxmin': 'kminmax'}
        klims = dict(min=max, max=min)
        for lim, val in klims.items():
            if isinstance(val, str):
                val = STR_CONVERT.get(val, val)
                klims[lim] = val
            elif isinstance(val, tuple):
                safety = 1 / val[0]
                val = val[1]
                if isinstance(val, str):
                    val = STR_CONVERT.get(val, val)
                klims[lim] = (safety, val)
            elif callable(val):
                raise InputError("callable not supported in pick_lmod; Use pick_mod instead.")
            else:  # number or DataArray. Convert from l to k
                klims[lim] = 2 * np.pi / val
        return self.pick_mod(**klims, N=N, **kw_pick_mod)

    def reduce_fluid_dim(self, lim, *, fluid=None, ifluid=None, reduce_fluids=False):
        '''return lim but without fluid (or fluid_sort) dimensions.
        if not possible, crash.
        (if lim was originally not a DataArray, return lim unchanged.)

        lim: None, number, callable, or DataArray
            probably min or max during self.pick_mod,
            but also allowed to supply any other value.
        fluid: None, int, str, or other specifier for 'fluid' or 'fluid_sort' dim
            if provided, xarray_sel(array, {fluid_dim: fluid}).
        ifluid: None or int
            if provided, array.isel({fluid_dim: ifluid}
            if min or max has 'fluid' dimension (after sel(fluid) or ifluid if appropriate),
        reduce_fluids: False, 'nmean', or 'ldebye_tot'
            tells how to reduce the 'fluid' dimension, if necessary.
            False --> don't reduce 'fluid' dimension; crash instead.
            'nmean' --> take the density-weighted mean across all fluids.
                        Requires self.ds['n'] to exist and also have 'fluid' dimension.
            'ldebye_tot' --> convert as if doing 'ldebye_total':
                        ldebye_joined = sqrt( 1 / sum_fluids(1 / ldebye^2)).
                        Since this function is in k-space, we have:
                        klim_joined = sqrt(sum_fluids(klim^2)).
        '''
        if not (hasattr(lim, 'dims') and ('fluid' in lim.dims or 'fluid_sort' in lim.dims)):
            return lim  # not a DataArray with fluid_dim --> return without making any changes.
        if (fluid is None) and (ifluid is None) and (not reduce_fluids):
            errmsg = (f"result cannot vary with fluid, but lim has 'fluid' or 'fluid_sort' dim.\n"
                      f"Input different lim, or input kwarg fluid or ifluid to sel or isel the fluid,\n"
                      f"or use reduce_fluids='nmean' or 'ldebye_tot' to average (after sel or isel).")
            raise DimensionError(errmsg)
        # sel(fluid) or isel(ifluid), if appropriate
        elif fluid is not None:
            if self.fluid_dim == 'fluid_sort':
                errmsg = ('fluid kwarg when self.fluid_dim == "fluid_sort" instead of "fluid".\n'
                          'Consider using ifluid kwarg instead.')
                raise NotImplementedError(errmsg)
            lim = xarray_sel(lim, {self.fluid_dim: fluid})
        elif ifluid is not None:
            lim = lim.isel({self.fluid_dim: ifluid})
        # reduce_fluids, if appropriate
        if self.fluid_dim in lim.dims:
            if not reduce_fluids:
                errmsg = ('result still varies with fluid even after sel(fluid=fluid) or isel(fluid=ifluid)')
                raise DimensionError(errmsg)
            elif reduce_fluids == 'nmean':
                if 'n' not in self.ds:
                    errmsg = ("reduce_fluids='nmean', but self.ds does not have 'n' for density weighting.")
                    raise InputError(errmsg)
                # get density, sliced in the same way as lim was sliced:
                n = self.ds['n']
                if fluid is not None:
                    n = xarray_sel(n, {self.fluid_dim: fluid})
                elif ifluid is not None:
                    n = n.isel({self.fluid_dim: ifluid})
                # density weighting:
                lim = (lim * n).sum(self.fluid_dim) / n.sum(self.fluid_dim)
            elif reduce_fluids == 'ldebye_tot':
                lim = np.sqrt((lim ** 2).sum(self.fluid_dim))
            else:
                errmsg = f'unrecognized reduce_fluids: {reduce_fluids!r}. Expected False, "nmean", or "ldebye_tot".'
                raise InputError(errmsg)
        return lim

    # # # DISPLAY # # #
    def __repr__(self):
        if self.ang is None:
            ang_info = 'None'
        else:
            if isinstance(self.ang, xr.DataArray):
                min = self.ang.min().item()
                max = self.ang.max().item()
                sizes = dict(self.ang.sizes)
                ang_info = f'{type(self.ang).__name__}(min={min:.2g}, max={max:.2g}, sizes={sizes})'
            else:  # not xarray object
                ang_info = f'{type(self.ang).__name__}(...)'
        if self.mod is None:
            mod_info = 'None'
        else:
            if isinstance(self.mod, xr.DataArray):
                min = self.mod.min().item()
                max = self.mod.max().item()
                sizes = dict(self.mod.sizes)
                mod_info = f'{type(self.mod).__name__}(min={min:.2e}, max={max:.2e}, sizes={sizes})'
            else:
                mod_info = f'{type(self.mod).__name__}(...)'
        kmfp_info = 'None' if self.kmfp is None else f'<{type(self.kmfp).__name__} object>'
        kdebye_info = 'None' if self.kdebye is None else f'<{type(self.kdebye).__name__} object>'
        return f'{type(self).__name__}(ang={ang_info}, mod={mod_info}, kmfp={kmfp_info}, kdebye={kdebye_info})'


@format_docstring(kpicker_docs=kPicker.__doc__)
class kPickerLowres(kPicker):
    '''kPicker but with low-resolution defaults.
    These defaults are best suited for solving TFBI quickly across many physical parameters.

    here, DEFAULT_DEGSTEP = 15, and DEFAULT_MOD_N = 10.

    Additionally, uses DEFAULT_MOD=dict() and DEFAULT_ANG=dict(),
        i.e. initializing kPickerLowres(ds) will pick_mod() and pick_ang(), by default.
        contrast to kPicker(ds), which expects pick_mod() and pick_ang() to be called later,
            unless providing kwargs mod=dict(...) and ang=dict(...).

    Finally, uses DEFAULT_IFLUID = slice(1,None), and DEFAULT_REDUCE_FLUIDS = 'ldebye_tot',
        which are "reasonable" ways to handle input ds with a 'fluid' or 'fluid_sort' dim.


    To better understand what is being picked, use kPicker() directly, instead;
        kPicker will crash (instead of returning defaults) if you didn't provide enough details.

    kPicker docs copied below, for convenience:
    -------------------------------------------
    {kpicker_docs}
    '''
    DEFAULT_MOD = dict()
    DEFAULT_ANG = dict()

    DEFAULT_DEGSTEP = 15
    DEFAULT_MOD_N = 10

    DEFAULT_IFLUID = slice(1, None)
    DEFAULT_REDUCE_FLUIDS = 'ldebye_tot'


@format_docstring(kpicker_docs=kPicker.__doc__)
class kPickerMidres(kPicker):
    '''kPicker but with mid-resolution defaults.
    These defaults are best suited for solving TFBI across a few sets of physical parameters.

    Here, DEFAULT_DEGSTEP = 3, and DEFAULT_MOD_N = 30.

    Additionally, uses DEFAULT_MOD=dict() and DEFAULT_ANG=dict(),
        i.e. initializing kPickerHighres(ds) will pick_mod() and pick_ang(), by default.
        contrast to kPicker(ds), which expects pick_mod() and pick_ang() to be called later,
            unless providing kwargs mod=dict(...) and ang=dict(...).

    Finally, uses DEFAULT_IFLUID = slice(1,None), and DEFAULT_REDUCE_FLUIDS = 'ldebye_tot',
        which are "reasonable" ways to handle input ds with a 'fluid' or 'fluid_sort' dim.


    To better understand what is being picked, use kPicker() directly, instead;
        kPicker will crash (instead of returning defaults) if you didn't provide enough details.

    kPicker docs copied below, for convenience:
    -------------------------------------------
    {kpicker_docs}
    '''
    DEFAULT_MOD = dict()
    DEFAULT_ANG = dict()

    DEFAULT_DEGSTEP = 3
    DEFAULT_MOD_N = 30

    DEFAULT_IFLUID = slice(1, None)
    DEFAULT_REDUCE_FLUIDS = 'ldebye_tot'


@format_docstring(kpicker_docs=kPicker.__doc__)
class kPickerHighres(kPicker):
    '''kPicker but with high-resolution defaults.
    These defaults are best suited for solving TFBI precisely for one set of physical parameters.

    Here, DEFAULT_DEGSTEP = 1, and DEFAULT_MOD_N = 100.

    Additionally, uses DEFAULT_MOD=dict() and DEFAULT_ANG=dict(),
        i.e. initializing kPickerHighres(ds) will pick_mod() and pick_ang(), by default.
        contrast to kPicker(ds), which expects pick_mod() and pick_ang() to be called later,
            unless providing kwargs mod=dict(...) and ang=dict(...).

    Finally, uses DEFAULT_IFLUID = slice(1,None), and DEFAULT_REDUCE_FLUIDS = 'ldebye_tot',
        which are "reasonable" ways to handle input ds with a 'fluid' or 'fluid_sort' dim.


    To better understand what is being picked, use kPicker() directly, instead;
        kPicker will crash (instead of returning defaults) if you didn't provide enough details.

    kPicker docs copied below, for convenience:
    -------------------------------------------
    {kpicker_docs}
    '''
    DEFAULT_MOD = dict()
    DEFAULT_ANG = dict()

    DEFAULT_DEGSTEP = 1
    DEFAULT_MOD_N = 100

    DEFAULT_IFLUID = slice(1, None)
    DEFAULT_REDUCE_FLUIDS = 'ldebye_tot'


''' --------------------- TfbiInputManager --------------------- '''

class TfbiInputManager():
    '''stores inputs for the TFBI.
    CAUTION: intended to be immutable after initialization;
        checks are performed initially, but not at later times.
        Altering internal values (e.g. values in ds) might cause unexpected behavior.

    ds: xarray Dataset.
        dataset containing inputs for the TFBI.
        Internally stores ds.copy(), not the original ds.
    
    If using TfbiInputManager(ds) directly, ds must have keys:
        -- SCALARS --
        (no 'component' nor 'fluid' dims.)
            mod_B: magnitude of magnetic field.
            E_un0_perpmod_B: E in the u_neutral=0 frame, perp to B.
            kB: boltzmann constant.
            T_n: neutral temperature.
            m_n: neutral mass.
        -- VECTORS --
        (must have 'component' dim but not 'fluid' dim.)
            k: wavenumber. Components, in order, via k.isel(component=i):
                0: k parallel to E_un0 (E in the u_neutral=0 frame).
                1: k parallel to -E_un0 cross B.
                2 (if provided): k parallel to B. (Must be 0 else NotImplementedError)..
        -- FLUID SCALARS --
        (must have 'fluid' dim but not 'component' dim. fluid 0 should be electron.)
            m: mass of each species.
            nusn: collision frequency between specie and neutrals for each species.
            skappa: signed magnetization parameter for each species: q_s |B| / (m_s nusn)
            eqperp_ldebye: each species' debye length at its "equilibrium" temperature,
                        after considering zeroth order heating due to E_un0_perpmod_B.
                        # [TODO] eq_ldebye, which considers parallel heating as well,
                        #    if implementing the advanced theory allowing nonzero E dot B.
    Alternatively, it is acceptable to have 'fluid_sort' dim instead of 'fluid' dim;
        -- if using 'fluid_sort' dim, ds should also have: -- 
            'fluid_orig': original fluids, before sorting
            'fluid_index': sort order for fluids; probably multidimensional.
                    fluid_orig.isel(fluid_orig=fluid_index) tells fluid at each point.
        (Additionally, fluid_index.isel(fluid_sort=0) should be a constant array,
            with index corresponding to electrons.)
    '''
    vv = TFBI_SS_PRESETS

    def __init__(self, ds):
        self._ds = ds.copy()
        self.init_fluid_dim()
        self.init_checks()

    dims = alias_child('ds', 'dims')

    @property
    def ds(self):
        '''dataset in self. Intended to be immutable; don't edit this directly.'''
        return self._ds
    @ds.setter
    def ds(self, value):
        raise AttributeError("TfbiInputManager.ds intended to be immutable. Create new TfbiInputManager instead.")

    DIRECTIONS = {
        'E0hat': XHAT,
        'Bhat': ZHAT,
        'Kmag': (K.x**2 + K.y**2)**0.5,
    }
    @classmethod
    def get_directions(cls):
        '''return EquationSystem of "values" for directions of vectors, suitable for a TfbiDisprel.
        results are SymbolicObjects.
        '''
        result = {
            'E0hat': (E0hat, cls.DIRECTIONS['E0hat']),
            'Bhat': (Bhat, cls.DIRECTIONS['Bhat']),
            'Kmag': (K.mag, cls.DIRECTIONS['Kmag']),
        }
        return ss.EquationSystem.from_dict(result)

    SCALARS = {
        'mod_B': B.mag,
        'E_un0_perpmod_B': E.o0.mag,
        'kB': kB,
        'T_n': Tn,
        'm_n': mn,
    }
    FLUID_SCALARS = {
        'm': ms,
        'nusn': nusn,
        'eqperp_ldebye': ldebyes,
        'skappa': kappas,
    }
    VECTORS = {
        'k': K,
    }

    def init_fluid_dim(self):
        '''initialize self.fluid_dim = 'fluid' or 'fluid_sort',
        whichever appears in self.ds. (At least 1 must appear in self.ds.dims.)
        '''
        if 'fluid' in self.ds.dims:
            self.fluid_dim = 'fluid'
        elif 'fluid_sort' in self.ds.dims:
            self.fluid_dim = 'fluid_sort'
        else:
            raise InputError("Expected 'fluid' or 'fluid_sort' dim in ds.")

    def init_checks(self):
        '''ensure that self.ds has all the expected keys and dimensions.'''
        ds = self.ds
        fluid_dim = self.fluid_dim
        if 'component' not in ds.dims:
            raise InputError("Expected 'component' dim in ds.")
        # check that scalars don't have fluid dim and don't have component dim
        for key in self.SCALARS:
            if key not in ds:
                raise InputError(f"Expected key '{key}' in ds.")
            if 'component' in ds[key].dims:
                raise InputError(f"Expected '{key}' to not have 'component' dim.")
            if fluid_dim in ds[key].dims:
                raise InputError(f"Expected '{key}' to not have {fluid_dim!r} dim.")
        # check that fluid scalars have fluid dim but don't have component dim
        for key in self.FLUID_SCALARS:
            if key not in ds:
                raise InputError(f"Expected key '{key}' in ds.")
            if 'component' in ds[key].dims:
                raise InputError(f"Expected '{key}' to not have 'component' dim.")
            if fluid_dim not in ds[key].dims:
                raise InputError(f"Expected '{key}' to have 'fluid' or 'fluid_sort' dim.")
        # check that fluid0 looks good (i.e., is electron) (if possible)
        if fluid_dim == 'fluid':
            fluid0 = ds['fluid'][0].item()
        else:  # fluid_dim == 'fluid_sort'
            idx = ds['fluid_index'].isel(fluid_sort=0)
            idx0 = idx.values.flat[0]
            if np.any(idx != idx0):
                raise InputError("ds['fluid_index'].isel(fluid_sort=0) contains >1 unique value.")
            if 'fluid_orig' in ds:
                fluid0 = ds['fluid_orig'].isel(fluid_orig=idx0).item()
            else:
                fluid0 = idx0
        if hasattr(fluid0, 'is_electron') and not fluid0.is_electron():
            raise InputError("fluid 0 should be electron.")
        # check that vector don't have fluid dim but do have component dim.
        for key in self.VECTORS:
            if key not in ds:
                raise InputError(f"Expected key '{key}' in ds.")
            if 'component' not in ds[key].dims:
                raise InputError(f"Expected '{key}' to have 'component' dim.")
            if fluid_dim in ds[key].dims:
                raise InputError(f"Expected '{key}' to not have 'fluid' dim.")
        # check that there are at most 3 components for vectors.
        if ds['component'].size > 3:
            raise InputError(f"expect <=3 components; got {ds['component'].size}.")
        elif ds['component'].size==3:
            if ds['k'].isel(component=2) != 0:
                raise NotImplementedError("tfbi when k_z != 0. (z is parallel to B.)")
                # [TODO] more complete theory allows nonzero k dot B.

    def get_values(self):
        '''return EquationSystem of values, suitable for plugging into a TfbiDisprel.
        results are numpy array objects, broadcastable from self.ds to make room for all dims.
        '''
        values = dict()
        for k, sym in self.SCALARS.items():
            valk = self.ds[k]  # [TODO] if numpy: get numpy array instead of DataArray.
            values[k] = (sym, valk)
        #fluids = [f.item() for f in self.ds['fluid']]
        nfluids = self.ds[self.fluid_dim].size
        for k, sym in self.FLUID_SCALARS.items():
            valk = self.ds[k]  # [TODO] handle if numpy...
            valks = [valk.isel({self.fluid_dim: i}) for i in range(nfluids)]
            for i in range(nfluids):
                if i==0:
                    values[f'{k}_e'] = (sym.ss('s', 'e'), valks[i])
                else:
                    values[f'{k}_i{i}'] = (sym.ss('s', f'i{i}'), valks[i])
        for k, sym in self.VECTORS.items():
            valk = self.ds[k]
            valkx = valk.isel(component=0) # [TODO] handle if numpy
            valky = valk.isel(component=1) # [TODO] handle if numpy
            values[f'{k}_x'] = (sym.x, valkx)
            values[f'{k}_y'] = (sym.y, valky)
            if valk['component'].size == 3:
                valkz = valk.isel(component=2) # [TODO] handle if numpy
                values[f'{k}_z'] = (sym.z, valkz)
        # convert to numpy arrays
        for k, (sym, val) in values.items():
            values[k] = (sym, xarray_broadcastable_array(val, self.dims).data)
        # result:
        # don't need to include directions here, just values; directions handled by TfbiDisprelStarred.
        result = ss.EquationSystem.from_dict(values)
        return result

    # # # ALTERNATE CREATION OPTIONS # # #
    @classmethod
    def implied_from(cls, x, **kw):
        '''return TfbiInputManager with values implied from input here.
        x: xarray.Dataset or TfbiInputManager
            if isinstance of cls, return x unchanged.
            if Dataset, return cls(x)  # [TODO] more tricks to be lenient on inputs.
        '''
        if isinstance(x, cls):
            return x
        return cls(x, **kw)

    # # # DISPLAY # # #
    def __repr__(self):
        return f"<{self.__class__.__name__}; see self.ds or self.get_values()>"


class TfbiInputManagerStarred(TfbiInputManager):
    '''stores inputs for the TFBI, for TfbiDisprelStarred subclasses.

    ds: xarray Dataset.
        dataset containing inputs for the TFBI.
    omegau: None, number, or xarray.DataArray
        arbitrary factor for "frequency units" in starred dispersion relations.
        Helps numerics if close to omega or nusn values.
        None --> check ds for 'omegau'; use that if provided, else 1.
    ku: None, number, or xarray.DataArray
        arbitrary factor for "wavenumber units" in starred dispresion relations.
        Helps numerics if close to |k| or other relevant inverse length-scales' values.
        None --> check ds for 'ku'; use that if provided, else 1.
    
    If using TfbiInputManagerStarred(ds) directly, ds must have keys:
        -- SCALARS --
        (no 'component' nor 'fluid' dims.)
            mod_B: magnitude of magnetic field.
            E_un0_perpmod_B: E in the u_neutral=0 frame, perp to B.
            kB: boltzmann constant.
            T_n: neutral temperature.
            m_n: neutral mass.
        -- VECTORS --
        (must have 'component' dim but not 'fluid' dim.)
            k: wavenumber. Components, in order, via k.isel(component=i):
                0: k parallel to E_un0 (E in the u_neutral=0 frame).
                1: k parallel to -E_un0 cross B.
                2: k parallel to B. (Must be 0 else NotImplementedError)..
        -- FLUID SCALARS --
        (must have 'fluid' dim but not 'component' dim. fluid 0 should be electron.)
            m: mass of each species.
            nusn: collision frequency between specie and neutrals for each species.
            skappa: signed magnetization parameter for each species: q_s |B| / (m_s nusn)
            eqperp_ldebye: each species' debye length at its "equilibrium" temperature,
                        after considering zeroth order heating due to E_un0_perpmod_B.
                        # [TODO] eq_ldebye, which considers parallel heating as well,
                        #    if implementing the advanced theory allowing nonzero E dot B.
    Alternatively, it is acceptable to have 'fluid_sort' dim instead of 'fluid' dim;
        -- if using 'fluid_sort' dim, ds should also have: -- 
            'fluid_orig': original fluids, before sorting
            'fluid_index': sort order for fluids; probably multidimensional.
                    fluid_orig.isel(fluid_orig=fluid_index) tells fluid at each point.
        (Additionally, fluid_index.isel(fluid_sort=0) should be a constant array,
            with index corresponding to electrons.)

    Meanwhile, if ds does not have the following keys, internally store ds.copy() and add them:
        -- SCALARS --
            omegau: (use 1 if not provided) arbitrary factor for frequency units. Helps if close to omega.
            ku: (use 1 if not provided) arbitrary factor for wavenumber units. Helps if close to |k|
    '''
    def __init__(self, ds, *, omegau=None, ku=None):
        if 'omegau' in ds and omegau is not None and not np.all(omegau == ds['omegau']):
            raise InputConflictError("Provided omegau and ds['omegau'] conflict.")
        if 'ku' in ds and ku is not None and not np.all(ku == ds['ku']):
            raise InputConflictError("Provided ku and ds['ku'] conflict.")
        if omegau is None: omegau = 1
        if ku is None: ku = 1
        assigning = dict()
        if 'omegau' not in ds:
            assigning['omegau'] = omegau
        if 'ku' not in ds:
            assigning['ku'] = ku
        if assigning:
            ds = ds.assign(assigning)  # makes a copy & assigns new data vars in copy.
        super().__init__(ds)

    SCALARS = TfbiInputManager.SCALARS.copy()
    SCALARS.update({
        'omegau': omegau,
        'ku': ku,
        })
