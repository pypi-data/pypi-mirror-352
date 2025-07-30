"""
File Purpose: TfbiDisprelCmns

Like TfbiDisprelC, but allows charged-fluid-dependent neutral masses: m_n --> m_{n,s}.
This can be relevant if most important collisions are with different neutrals
    for ions than for electrons. E.g. {e,H} collisions, and {H+,O2} collisions.
Or, can be relevant if fudging m_e, when using PIC collision algorithm which depends on m_n,
    and want e momentum change due to collisions to still be correct even though m_e is not.

Double-checking the TFBI derivation reveals it should be
    compaitble with each fluid having a different associated m_n,
    if we just replace m_n with m_{n,s} in all the coefficients
    (e.g. As, Bs, Cs --> sub m_n for m_{n,s}, anywhere m_n appears)
"""
from SymSolver import symbol

from .disprel_A import tfbiA_o0_def, tfbiA_o0_sol
from .disprel_C import (
    TfbiDisprelC,
    tfbiC_o0_def, tfbiC_o0_sol, tfbiC_coeffs,
    tfbiC_disprel, tfbiC_disprel_QN,
    tfbiC_stars_def, tfbiC_stars_sol,
    load_tfbiC, LOAD_TFBI_C_KEYS,
)
from .inputs import TfbiInputManagerStarred

# load variables DIRECTLY INTO LOCALS().
load_tfbiC(locals())

''' --------------------- definitions here --------------------- '''

mns = symbol('m', ('n', 's'))  # species-dependent neutral mass.

LOAD_TFBI_Cmns_KEYS = list(LOAD_TFBI_C_KEYS)
LOAD_TFBI_Cmns_KEYS.append('mns')

tfbiCmns_o0_def_unstarred = tfbiA_o0_def.sub(mn, mns)
tfbiCmns_o0_sol_unstarred = tfbiA_o0_sol.sub(mn, mns)
tfbiCmns_o0_def = tfbiC_o0_def.sub(mn, mns)
tfbiCmns_o0_sol = tfbiC_o0_sol.sub(mn, mns)
tfbiCmns_coeffs = tfbiC_coeffs.sub(mn, mns)
tfbiCmns_disprel = tfbiC_disprel.sub(mn, mns)
tfbiCmns_disprel_QN = tfbiC_disprel_QN.sub(mn, mns)
tfbiCmns_stars_def = tfbiC_stars_def.sub(mn, mns)
tfbiCmns_stars_sol = tfbiC_stars_sol.sub(mn, mns)


''' --------------------- Cmns input manager --------------------- '''

class TfbiInputManagerCmns(TfbiInputManagerStarred):
    '''TfbiInputManagerCmns: TfbiInputManagerStarred, but with m_{n,s} instead of m_n.
    i.e., neutral mass is now a fluid-dependent var, instead of a scalar.
    Documentation below is very similar to TfbiInputManagerC, but updated appropriately.

    stores inputs for the TFBI, for TfbiDisprelStarred subclasses.

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
        -- VECTORS --
        (must have 'component' dim but not 'fluid' dim.)
            k: wavenumber. Components, in order, via k.isel(component=i):
                0: k parallel to E_un0 (E in the u_neutral=0 frame).
                1: k parallel to -E_un0 cross B.
                2: k parallel to B. (Must be 0 else NotImplementedError)..
        -- FLUID SCALARS --
        (must have 'fluid' dim but not 'component' dim. fluid 0 should be electron.)
            m: mass of each species.
            m_n: neutral mass associated with each species.
                (symbolically, internally, it goes into m_{n,s}.)
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
    SCALARS = TfbiInputManagerStarred.SCALARS.copy()
    del SCALARS['m_n']

    FLUID_SCALARS = TfbiInputManagerStarred.FLUID_SCALARS.copy()
    FLUID_SCALARS['m_n'] = mns

    # all other functionality inherited from TfbiInputManagerStarred.


''' --------------------- Loading vars into namespace --------------------- '''

_TFBI_Cmns_LOCALS = locals()

def load_tfbiCmns(namespace=None):
    '''defines tfbi Cmns terms in namespace (if provided), and returns dict of loaded values.
    E.g. load_tfbiCmns(locals()) populates locals with tfbiC terms.

    These variables are listed in LOAD_TFBI_Cmns_KEYS.
    '''
    result = dict()
    for key in LOAD_TFBI_Cmns_KEYS:
        result[key] = _TFBI_Cmns_LOCALS[key]
    if namespace is not None:
        for key in result:
            namespace[key] = result[key]
    return result


''' --------------------- TfbiDisprelCmns --------------------- '''

class TfbiDisprelCmns(TfbiDisprelC):
    '''TfbiDisprelCmns: TfbiDisprelC but allows specie-dependent neutral masses.
    Replaces m_{n,s} from TfbiDisprelC, with m_n.
    '''
    input_manager_cls = TfbiInputManagerCmns

    # w = omegastar   # inherited from TfbiDisprelC
    coeffs = tfbiCmns_coeffs
    disprel = tfbiCmns_disprel
    o0def = tfbiCmns_o0_def_unstarred
    o0sol = tfbiCmns_o0_sol_unstarred

    # for convenience:
    o0stardef = tfbiCmns_o0_def
    o0starsol = tfbiCmns_o0_sol
    stardef = tfbiCmns_stars_def
    starsol = tfbiCmns_stars_sol
    vv = load_tfbiCmns()  # dict of vars & equations relevant to TfbiCmns.


class TfbiDisprelCmns_QN(TfbiDisprelCmns):
    '''TfbiDisprelCmns_QN: TfbiDisprelCmns with QN disprel instead of including k on RHS.'''
    disprel = tfbiCmns_disprel_QN
