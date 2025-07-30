"""
File Purpose: TfbiDisprelB

Similar to the TfbiDisprelA, but adimensionalizes some quantities,
and joins some quantities, to make stuff simpler
"""
from SymSolver import (
    symbols, symbol,
    equation, equation_system, EquationSystem,
)

from .disprel import TfbiDisprelStarred
from .disprel_A import (
    tfbiA_o0_def, tfbiA_o0_sol, tfbiA_coeffs,
    tfbiA_disprel, tfbiA_disprel_QN
)
from .vars import load_vars, LOAD_VARS_KEYS

# load variables DIRECTLY INTO LOCALS().
load_vars(locals())

''' --------------------- definitions here --------------------- '''

LOAD_TFBI_B_KEYS = list(LOAD_VARS_KEYS)    # start with copy of load vars keys.
tfbiB_defs_dict = dict()  # dict of defined equations
tfbiB_sols_dict = dict()  # dict of solutions to defined equations.

def Bsymbol(localname, *args_symbol, **kw_symbol):
    '''creates and returns symbol, and appends localname to LOAD_TFBI_B_KEYS'''
    LOAD_TFBI_B_KEYS.append(localname)
    return symbol(*args_symbol, **kw_symbol)
def Bdef(label, lhs, rhs):
    '''sets tfbiB_defs_dict[label] = equation(lhs, rhs, label=label)'''
    tfbiB_defs_dict[label] = equation(lhs, rhs, label=label)
def Bsol(label, solve_for, **kw_solve):
    '''sets tfbiB_sols_dict[label] = tfbiB_defs_dict[label].solve(solve_for)'''
    tfbiB_sols_dict[label] = tfbiB_defs_dict[label].solve(solve_for, **kw_solve)
    
k = K
omega = OMEGA

# # "Adimensionalize" # #
# frequency scale  (E.g. if 1 Hz, nustarsn = nusn / 1 Hz.)
# omega = omega / omegau
omegastar = Bsymbol('omegastar', r'\omega^{*}')
Bdef('omegastar', omegastar, omega / omegau)
Bsol('omegastar', omega)

# wavenumber scale  (E.g. if 1/m, kstar = |k| / 1 m)
# kstar = k / ku
kstar = Bsymbol('kstar', r'k^{*}')
Bdef('kstar', kstar, k.mag / ku)
Bsol('kstar', k.mag)

# velocity scale (== omegau / ku)
Bdef('uu', uu, omegau / ku)
# Will put Bsol('uu', uu) later; order matters for subsitutions. See below.

# omegastars = omegas / omegau
omegastars = Bsymbol('omegastars', r'\omega^{*}', ['s'])
Bdef('omegastars', omegastars, omegas / omegau)
Bsol('omegastars', omegas)

# ustars = us0 / uu
ustars = Bsymbol('ustars', r'u^{*}', ['s'], vector=True)
Bdef('ustars', ustars, us.o0 / uu)
Bsol('ustars', us.o0)

# Tstars = (kB Ts0 / ms) * (1 / uu**2)
Tstars = Bsymbol('Tstars', r'T^{*}', ['s'])
Bdef('Tstars', Tstars, (kB * Ts.o0 / ms) / uu**2)
Bsol('Tstars', Ts.o0)
Tstarn = Bsymbol('Tstars', r'T^{*}', ['n'])
Bdef('Tstarn', Tstarn, (kB * Tn / mn) / uu**2)
Bsol('Tstarn', Tn)

# mstars = ms / mn
mstars = Bsymbol('mstars', r'm^{*}', ['s'])
Bdef('mstars', mstars, ms / mn)
Bsol('mstars', ms)

# Estar = (E / B) / uu
Estar = Bsymbol('Estar', r'E^{*}')
Bdef('Estar', Estar, (E.o0.mag / B.mag) / uu)
Bsol('Estar', E.o0.mag)

# nustarsn = nusn / omegau
nustarsn = Bsymbol('nustarsn', r'\nu^{*}', ['s', 'n'])
Bdef('nustarsn', nustarsn, nusn / omegau)
Bsol('nustarsn', nusn)

# ustarks = ustars dot khat
ustarks = Bsymbol('ustarks', r'u^{*}', ['k', 's'])
Bdef('ustarks', ustarks, ustars.dot(khat))
Bsol('ustarks', ustars.dot(khat))

# ustarls = ustars dot (khat.cross(Bhat))   # "lhat = khat.cross(Bhat)"
ustarls = Bsymbol('ustarls', r'u^{*}', ['l', 's'])
_tmp = ustars.dot(khat.cross(Bhat)).simplify()
Bdef('ustarls', ustarls, _tmp)
Bsol('ustarls', _tmp)

# put solution for uu later; order matters during substitutions.
Bsol('uu', uu)

# equation system with starred definitions
tfbiB_stars_def = EquationSystem.from_dict(tfbiB_defs_dict)
tfbiB_stars_sol = EquationSystem.from_dict(tfbiB_sols_dict)

# # plug starred definitions into 0th order & dispersion relation # #
# also some other things:
#   hatify E0 and k (e.g. E.o0 = E.o0.mag * E.o0.hat)
#   ignore un. ([TODO] make ustarn instead, to test when un!=0)

# 0th order equations
tfbiB_o0_def = tfbiA_o0_sol.hatify(E.o0, k).subs(*tfbiB_stars_sol).simplify() 
tfbiB_o0_sol = tfbiB_o0_def.solution_put('Ts0', Tstars)

# coeffs (omegas, Ws, As, Bs, Cs, Fs)
tfbiB_coeffs = tfbiA_coeffs.ignore(un).hatify(E.o0, k).subs(*tfbiB_stars_sol)
tfbiB_coeffs = tfbiB_coeffs.simplified().subs(*tfbiB_stars_sol)

# disprel & quasineutral disprel
tfbiB_disprel = tfbiA_disprel.subs(*tfbiB_stars_sol)
tfbiB_disprel = tfbiB_disprel.simplified().subs(*tfbiB_stars_sol)
tfbiB_disprel_QN = tfbiA_disprel_QN.subs(*tfbiB_stars_sol)
tfbiB_disprel_QN = tfbiB_disprel_QN.simplified().subs(*tfbiB_stars_sol)


''' --------------------- Loading vars into namespace --------------------- '''

LOAD_TFBI_B_KEYS.extend([
    'tfbiB_stars_def', 'tfbiB_stars_sol',
    'tfbiB_o0_def', 'tfbiB_o0_sol',
    'tfbiB_coeffs', 'tfbiB_disprel', 'tfbiB_disprel_QN',
])

_TFBI_B_LOCALS = locals()

def load_tfbiB(namespace=None):
    '''defines tfbi B terms in namespace (if provided), and returns dict of loaded values.
    E.g. load_tfbiB(locals()) populates locals with tfbiB terms.

    These variables are listed in LOAD_TFBI_B_KEYS.
    '''
    result = dict()
    for key in LOAD_TFBI_B_KEYS:
        result[key] = _TFBI_B_LOCALS[key]
    if namespace is not None:
        for key in result:
            namespace[key] = result[key]
    return result


''' --------------------- TfbiDisprelB --------------------- '''

class TfbiDisprelB(TfbiDisprelStarred):
    '''TfbiDisprelB: TfbiDisprel with adimensionalized variables'''
    w = omegastar
    coeffs = tfbiB_coeffs
    disprel = tfbiB_disprel
    o0def = tfbiA_o0_def
    o0sol = tfbiA_o0_sol

    # for convenience:
    o0stardef = tfbiB_o0_def
    o0starsol = tfbiB_o0_sol
    stardef = tfbiB_stars_def
    starsol = tfbiB_stars_sol
    vv = load_tfbiB()  # dict of vars & equations relevant to TfbiB.


class TfbiDisprelB_QN(TfbiDisprelB):
    '''TfbiDisprelB_QN: TfbiDisprelB with QN disprel instead of including k on RHS.'''
    disprel = tfbiB_disprel_QN
