"""
File Purpose: TfbiDisprel manages dispersion relation algebra.
"""
import numpy as np
import xarray as xr

import SymSolver as ss

from .inputs import TfbiInputManagerStarred
from ..errors import InputMissingError, InputConflictError
from ..tools import (
    alias_child, simple_cachef_property,
    UNSET,
    ProgressUpdater, format_docstring,
    xarray_from_broadcastable,
)

class TfbiDisprel():
    '''manages dispersion relation algebra.
    Consider using one of the predefined TfbiDisprel objects instead.

    w: Symbol
        the value to solve for. E.g. omega or omegastar
    coeffs: EquationSystem
        must have equations for omegas, Ws, As, Bs, Cs, Fs,
        and Fs must be the final equation.
    disprel: Equation
        the dispersion relation. Probably contains symbols defined in coeffs.
    charged_s: None or list of strings
        list of strings for charged species, e.g. ('e-', 'H+', 'C+')
        None --> trying to expand summation over species will cause crash,
            unless self.charged_s is provided later.
    values: None or EquationSystem
        values to plug into the disprel. It's okay to contain unused values.
        None --> trying to numerically evaluate disprel will cause crash,
            unless self.values is provided later.
    ds: None or xarray.Dataset
        if provided, used when converting results into xarray.DataArray.

    Examples:
        # do it all at once:
        disprel1 = TfbiDisprel(...)
        result = disprel1.growth_root()
        # inspect intermediate results: might want to checK:
        disprel1.Fs()
        disprel1.casc
        disprel1.pfrac

        # do it in steps (easier to check timing)
        disprel2 = TfbiDisprel(...)
        _casc = disprel2.calc_casc()
        _pfrac = disprel2.calc_pfrac()   # uses cached casc.
        result = disprel2.growth_root()  # uses cached pfrac.
    '''
    def __init__(self, w, coeffs, disprel, charged_s=None, *,
                 values=None, ds=None):
        self.w = w
        self.coeffs = coeffs
        self.disprel = disprel
        self.charged_s = charged_s
        self.values = values
        self.ds = ds

    # # # ALGEBRA # # #
    def Fs(self):
        '''returns Fs with all coeffs plugged into it, and polyfractionized in w.

        If algebra is done properly, result should be a ratio of polynomials in w,
            with degree 2 numerator / degree 4 denominator.
        '''
        coeffs = self.coeffs
        w = self.w
        tmp = coeffs.cascade(keep_eqs=False).simplified()
        result = tmp.polyfractionize(w, simplify=True)
        return result

    def poly(self):
        '''returns disprel like: polyfraction(w) = 0, with all coeffs plugged in.'''
        # bookkeeping / inputs
        charged_s = self.charged_s
        if charged_s is None:
            raise InputMissingError('charged_s required to expand summation in disprel.')
        w = self.w
        fscalc = self.Fs()
        disp = self.disprel
        # algebra
        disp = disp.subtract_rhs().subs(fscalc)
        disp = disp.expand_summations(iset=charged_s, only=True)  # if only=False, also simplifies
        pfrac0 = disp.lhs.polyfraction(w)
        pfsimp = pfrac0.simplify()
        poly = ss.equation(pfsimp, 0)
        return poly

    def calc_casc(self, *, clear_s=True, **kw_cascadify):
        '''returns full disprel with all vals plugged in, as a Cascade of equations.'''
        poly = self.poly()
        casc = poly.cascadify(clear_s=clear_s, **kw_cascadify)
        self._casc = casc  # caching; relevant to self.casc property
        return casc

    casc = simple_cachef_property('_casc', 'calc_casc')

    # # # NUMERICALLY EVALUATE # # #
    @property
    def values(self):
        '''values to plug into the disprel. It's okay to contain unused values.
        Setting self.values to a new value will clear any cached pfrac and parr.

        None --> trying to numerically evaluate disprel will cause crash,
            unless self.values is provided later.
        '''
        return self._values
    @values.setter
    def values(self, values):
        if values is not getattr(self, '_values', None):  # setting to a new value
            del self.pfrac  # delete self.pfrac if it exists (it depends on self.values)
            del self.parr   # delete self.parr if it exists (it depends on self.values)
        self._values = values

    def calc_pfrac(self):
        '''plug self.values into self.casc --> eq like pfrac = 0 --> return pfrac.
        Uses cached casc; to recalculate, first del self.casc or use self.calc_casc().
        '''
        # bookkeeping
        values = self.values
        if values is None:
            raise InputMissingError('values required to numerically evaluate disprel.')
        w = self.w
        casc = self.casc
        # evaluating
        tmp = casc.subs(*values).simplify(evaluate_numbers=True)
        def simplify_casc_eq(eq):
            return eq.simplify(collect_polys=[w], collect_poly_format=True)
        dispval = tmp.cascade(simplify=simplify_casc_eq)
        pfrac = dispval.lhs
        self._pfrac = pfrac
        return pfrac

    pfrac = simple_cachef_property('_pfrac', 'calc_pfrac')

    def calc_parr(self):
        '''returns self.pfrac.to_mp_array().
        Uses cached pfrac; to recalculate, first del self.pfrac or use self.calc_casc().
        '''
        pfrac = self.pfrac
        parr = pfrac.to_mp_array()
        self._parr = parr
        return parr

    parr = simple_cachef_property('_parr', 'calc_parr')

    def get_parr_verbose(self):
        '''gets self.parr, but with some timing info printouts, or a printout that parr was already in cache.'''
        updater = ProgressUpdater(print_freq=0)  # always print
        if hasattr(self, '_parr'):
            updater.print('parr already in cache.')
            result = self.parr
        else:
            if hasattr(self, '_casc'):
                updater.print('casc already in cache.')
            else:
                casc_updater = ProgressUpdater(print_freq=0)
                casc_updater.print('getting casc...')
                _casc = self.casc  # caches resulting casc
                casc_updater.finalize('calc_casc()', end='\n')
            parr_updater = ProgressUpdater(print_freq=0)
            parr_updater.print('getting parr from casc...')
            result = self.parr  # uses cached self.casc value
            parr_updater.finalize('calc_parr() (given known casc)', end='\n')
        updater.finalize('calc_parr()')
        return result

    def growth_root(self, *, to_omega=True, to_xarray=UNSET, return_ds=False, verbose=True,
                    careful='deval', ncpu=None, ncoarse=10, **kw_growth_root):
        '''returns the omega (or w) which solves self.pfrac & has largest imaginary part.

        to_omega: bool
            whether to convert result to self.to_omega(w_values)
            if False, result will be values for self.w, NOT necessarily omega.
        to_xarray: UNSET or bool
            whether to convert result to an xarray.DataArray, via xarray_from_broadcastable(self.ds, result)
            UNSET --> True if self.ds is not None.
        return_ds: bool
            whether to return self.ds.assign(omega=result), instead of just result.
        verbose: bool
            whether to do printouts 
        careful, ncpu, ncoarse, other kwargs:
            passed to self.parr.growth_root(...). 
            Changing these may affect computation time, but should not affect the result itself.
            ncpu = 1 means single processor. None means "multiprocessing with as many cpus as available."
            ncoarse is for mulitprocessing strategy: number of polynomials to assign to each task.
                (if finding roots of a single polynomial is very fast,
                    increase ncoarse to reduce multiprocessing communication overhead.)
        '''
        w = self.w
        updater = ProgressUpdater(print_freq=0 if verbose else -1)  # print all statements if verbose, else nothing.
        parr = self.get_parr_verbose() if verbose else self.parr  # <-- might take a while if not yet cached!
        if to_xarray is UNSET: to_xarray = (self.ds is not None)
        if to_omega: self._check_can_get_to_omega()  # <-- crash before growth_root if to_omega would crash.
        # this line can take a long time!  (parr.growth_root manages its own progress update printouts.)
        result = parr.growth_root(careful=careful, ncpu=ncpu, ncoarse=ncoarse, **kw_growth_root)  # <-- values of w
        self._w_values = result  # save values in case of crash
        try:
            result = self.to_omega(result) if to_omega else result
            result = self.to_xarray(result, name='omega') if to_xarray else result
            if isinstance(result, xr.DataArray) and return_ds:
                result = self.ds.assign(omega=result)
        except Exception:
            print('crashed in growth_root during to_omega or to_xarray. raw results saved to self._w_values.')
            raise
        else:
            del self._w_values  # <-- no crash, no need to save raw values here anymore.
        updater.finalize('growth_root() (from start to finish, but using cache when available)', always=True)
        return result

    def _check_can_get_to_omega(self):
        '''ensure self knows how to get to_omega(w_values)'''
        self.to_omega(np.arange(10) + 1j * np.arange(10))

    def to_omega(self, w_values):
        '''return omega inferred from w_values.
        Here, just returns w_values, unchanged. Subclass might override.
        '''
        return w_values

    def to_xarray(self, array, name=None):
        '''return xarray.DataArray from "broadcastable" array, with dims corresponding to self.ds.dims.
        if name is provided, result.rename(name)
        '''
        result = xarray_from_broadcastable(self.ds, array)
        if name is not None:
            result = result.rename(name)
        return result

    # # # INSPECTION # # #
    def casc_info(self):
        '''returns stats about the cascade of the disprel.
        this is a dict of:
            'len': number of eqns in the cascade
            'complexity_all': complexity of the cascade (more terms --> larger)
            'complexity_final': complexity of the final equation of the cascade.
        [TODO] this should probably be implemented directly in casc class, not here...
        '''
        casc = self.casc
        result = dict(
            len=len(casc),
            complexity_all=casc.complexity(),
            complexity_final=casc[-1].complexity()
        )
        return result

    def is_quasineutral(self):
        '''guesses whether self assumed quasineutrality.
        If not quasineutral there should be a k^2 term in the disprel.
        Here, just checks where the disprel's rhs is 0.
        '''
        return self.disprel.rhs == 0

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}(charged_s={self.charged_s})'


class TfbiDisprelPredefined(TfbiDisprel):
    '''TfbiDisprel with known equations attached to subclass.
    Not intended for direct usage; use a subclass instead.

    num_ions: None or int
        number of ions in the system. None --> provide later or via charged_s.
        int --> use charged_s = ('e', 'i1', 'i2', ..., 'iN') where N = num_ions.
    values: None or EquationSystem
        values to plug into the disprel. It's okay to contain unused values.
        None --> trying to numerically evaluate disprel will cause crash,
            unless self.values is provided later. 
    charged_s: None or list of strings
        None --> provide strings later, or via num_ions
        list of strings --> charged species, e.g. ('e-', 'H+', 'C+')

    Subclass should define:
        w: Symbol
            the value to solve for. E.g. omega or omegastar
        coeffs: EquationSystem
            must have equations for omegas, Ws, As, Bs, Cs, Fs,
            and Fs must be the final equation.
        disprel: Equation
            the dispersion relation. Probably contains symbols defined in coeffs.
    '''
    o0def = NotImplemented   # definitions for 0th order plasma equations
    o0sol = NotImplemented   # solutions for 0th order plasma equations

    def __init__(self, num_ions=None, *, values=None, charged_s=None):
        if num_ions is not None and charged_s is not None:
            errmsg = f'cannot provide both num_ions and charged_s; got num_ions={num_ions}, charged_s={charged_s}.'
            raise InputConflictError(errmsg)
        self.charged_s = charged_s
        self.num_ions = num_ions  # <-- must be after setting self.charged_s
        self.values = values

    @property
    def num_ions(self):
        '''number of ions in the system. None or int.
        setting num_ions=value will crash if incompatible with existing value
            (make a new Disprel object instead of altering num_ions,
            unless num_ions hasn't been set yet, i.e. num_ions=None still.)
        '''
        return None if self.charged_s is None else len(self.charged_s)-1
    @num_ions.setter
    def num_ions(self, value):
        if self.charged_s is None:
            self.charged_s = ('e', *tuple(f'i{i}' for i in range(1, value+1)))
        else:
            current_num = self.num_ions
            if value != current_num:
                errmsg = (f'new num_ions ({value}) incompatible with current num_ions ({current_num}).\n'
                          f'Instead of setting num_ions for existing {type(self).__name__}, make a new obj.')
                raise InputConflictError(errmsg)
            # else, current num_ions == value already.


class TfbiDisprelStarred(TfbiDisprelPredefined):
    '''TfbiDisprelStarred: TfbiDisprelPredefined with starred definitions.
    Not intended for direct usage; use a subclass instead.

    Quickstart guide:
        use a subclass, e.g. cls=TfbiDisprelC
        ds = ...   # dataset with appropriate inputs. see TfbiInputManager for details
        drel = cls.from_ds(ds)
        dsR = drel.solve()   # returns copy of ds but with dsR['omega']=self.growth_root().

    num_ions: None or int
        number of ions in the system. None --> provide later or via charged_s.
        int --> use charged_s = ('e', 'i1', 'i2', ..., 'iN') where N = num_ions.
    inputs: xarray.Dataset or TfbiInputManagerStarred.
        values to plug into the disprel. It's okay to contain unused values.
        None --> trying to numerically evaluate disprel will cause crash,
            unless self.set_inputs() is called later.
    directions: None or EquationSystem
        equations (in terms of SymbolicObjects) for E0hat, Bhat, and K.mag.
        None --> use default: E0hat=XHAT, Bhat=ZHAT, K.mag=(K.x**2 + K.y**2)**0.5.
        (default comes from self.input_manager_cls.get_directions())
    charged_s: None or list of strings
        None --> provide strings later, or via num_ions
        list of strings --> charged species, e.g. ('e-', 'H+', 'C+')

    Subclass should define:
        w: Symbol
            the value to solve for. E.g. omega or omegastar
        coeffs: EquationSystem
            must have equations for omegas, Ws, As, Bs, Cs, Fs,
            and Fs must be the final equation.
        disprel: Equation
            the dispersion relation. Probably contains symbols defined in coeffs.
    '''
    input_manager_cls = TfbiInputManagerStarred

    o0stardef = NotImplemented  # 0th order plasma equations, starred definitions
    o0starsol = NotImplemented  # 0th order plasma equations, starred solutions
    stardef = NotImplemented  # starred definitions for variables
    starsol = NotImplemented  # starred solutions for variables
    vv = NotImplemented  # {key: symbolic object} with all relevant symbolic objects

    def __init__(self, num_ions=None, inputs=None, *, directions=None, charged_s=None):
        super().__init__(num_ions=num_ions, charged_s=charged_s)
        self.inputs = inputs
        self.directions = directions
        self.init_directions()
        self.init_values_symbolic()
        if inputs is not None:
            self.set_inputs(inputs)

    ds = alias_child('inputs', 'ds')

    @staticmethod
    def infer_num_ions_from_ds(ds):
        '''return number of ions in ds: length of 'fluid' or 'fluid_sort' dimension, minus 1.
        (Assumes fluid_dim has 1 electron, and the rest are ions.)
        '''
        if ('fluid' not in ds.dims) and ('fluid_sort' not in ds.dims):
            raise InputMissingError('ds must have "fluid" or "fluid_sort" dimension, to infer num_ions.')
        if ('fluid' in ds.dims) and ('fluid_sort' in ds.dims):
            if len(ds.fluid) != len(ds.fluid_sort):
                raise InputConflictError('cannot infer num_ions when "fluid" and "fluid_sort" have different lengths.')
        fluid_dim = 'fluid' if 'fluid' in ds.dims else 'fluid_sort'
        num_ions = len(ds[fluid_dim]) - 1
        return num_ions

    @classmethod
    def from_ds(cls, ds, *, omegau=1e3, ku=None, **kw):
        '''new TfbiDisprelStarred from xarray.Dataset ds, via the following pattern:

        num_ions = cls.infer_num_ions_from_ds(ds)
        result = cls(num_ions=num_ions)
        result.set_inputs(ds, omegau=omegau, ku=ku)
        '''
        num_ions = cls.infer_num_ions_from_ds(ds)
        result = cls(num_ions=num_ions, **kw)
        result.set_inputs(ds, omegau=omegau, ku=ku)
        return result

    def init_directions(self):
        '''initialize self.directions = self.input_manager_cls.get_directions(),
        only if self.directions was previously None or did not exist.
        '''
        if getattr(self, 'directions', None) is None:
            self.directions = self.input_manager_cls.get_directions()

    def init_values_symbolic(self):
        '''initialize self.values_symbolic: componentized and subscriptized o0sol and stardef,
        also self.directions, and plugging in self.directions before componentizing.

        (subscriptize: eqs with 's' subscript --> copies with eq.ss('s', c) for c in self.charged_s)
        (componentize: vectors --> sub in x,y,z components. vector equations each become 3 eqs.)
        These are the symbolic-only versions; don't plug numerical values in yet.
        '''
        directions = self.directions
        result = directions
        # componentize
        o0alg = self.o0sol.subs(*directions).componentize().simplified()
        result = result.extend(o0alg)
        staralg = self.stardef.subs(*directions).componentize().simplified()
        result = result.extend(staralg)
        # subscriptize
        result = result.subscriptize('s', self.charged_s)
        self.values_symbolic = result

    def set_inputs(self, inputs, *, omegau=None, ku=None):
        '''set self.values from inputs, including starred definitions. Also returns self.values.
        Also sets self.inputs = TfbiInputManagerStarred object implied from inputs.

        inputs: xarray.Dataset or TfbiInputManagerStarred.
            values to plug into the disprel. It's okay to contain unused values.
            See help(self.input_manager_cls) for more info.
        omegau; ku: None, number, or xarray.DataArray
            arbitrary factors for "frequency units"; "wavenumber units".
            Helps numerics if close to relevant values, e.g. omega, nusn; |k|
            None --> check inputs for 'omegau' or 'ku'. use that if provided, else 1.
            Must be None if inputs is a TfbiInputManagerStarred.
        '''
        if isinstance(inputs, self.input_manager_cls) and (omega is not None or ku is not None):
            raise InputConflictError(f'omegau, ku must be None if inputs is a {self.input_manager_cls} instance.')
        inputs = self.input_manager_cls.implied_from(inputs, omegau=omegau, ku=ku)
        self.inputs = inputs
        values = inputs.get_values()
        derived = self.values_symbolic  # values derived from inputs
        derived = derived.subs(*values)
        derived = derived.cascade(keep_eqs=True, simplify=True)
        result = values.extend(derived)
        self.values = result
        return result

    def to_omega(self, w_values):
        '''return omega inferred from w_values.
        Here, returns self.starsol[OMEGA].rhs.subs((self.w, w_values), *self.values),
        '''
        self_w_to_omega = self.starsol[ss.OMEGA].rhs
        return self_w_to_omega.subs((self.w, w_values), *self.values).simplify()

    @format_docstring(growth_root_docs=TfbiDisprel.growth_root.__doc__)
    def solve(self, *, return_ds=True, **kw_growth_root):
        '''equivalent to self.growth_root(), but with return_ds=True by default.

        docs from TfbiDisprel.growth_root copied below
        ----------------------------------------------
        {growth_root_docs}
        '''
        return self.growth_root(return_ds=return_ds, **kw_growth_root)
