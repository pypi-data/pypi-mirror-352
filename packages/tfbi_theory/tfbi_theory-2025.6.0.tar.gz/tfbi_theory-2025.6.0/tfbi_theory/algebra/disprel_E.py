"""
File Purpose: TfbiDisprelE

Similar to TfbiDisprelB, but includes a few more simplifications:
    mstar = 1 + tfbiB_mstar
    use "ldebye^-2" as a symbol, instead of ldebye symbol, squared.
    use kappastars = 1 + kappas^2
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

LOAD_TFBI_E_KEYS = list(LOAD_VARS_KEYS)    # start with copy of load vars keys.
tfbiE_defs_dict = dict()  # dict of defined equations
tfbiE_sols_dict = dict()  # dict of solutions to defined equations.

def Esymbol(localname, *args_symbol, **kw_symbol):
    '''creates and returns symbol, and appends localname to LOAD_TFBI_E_KEYS'''
    LOAD_TFBI_E_KEYS.append(localname)
    return symbol(*args_symbol, **kw_symbol)
def Edef(label, lhs, rhs):
    '''sets tfbiE_defs_dict[label] = equation(lhs, rhs, label=label)'''
    tfbiE_defs_dict[label] = equation(lhs, rhs, label=label)
def Esol(label, solve_for, **kw_solve):
    '''sets tfbiE_sols_dict[label] = tfbiE_defs_dict[label].solve(solve_for)'''
    tfbiE_sols_dict[label] = tfbiE_defs_dict[label].solve(solve_for, **kw_solve)
    
k = K
omega = OMEGA

# # ldebye^-2 as its own symbol
ldebyes_neg2 = Esymbol('ldebyes_neg2', r'\lambda^{-2}', ['s'])
Edef('ldebyes_neg2', ldebyes_neg2, ldebyes**-2)
Esol('ldebyes_neg2', ldebyes**-2)

# # 1+kappa^2 as its own symbol
kappastars = Esymbol('kappastars', r'\kappa^{*}', ['s'])
Edef('kappastars', kappastars, 1 + kappas**2)
Esol('kappastars', kappas**2)

# # "Adimensionalize" # #
# frequency scale  (E.g. if 1 Hz, nustarsn = nusn / 1 Hz.)
# omega = omega / omegau
omegastar = Esymbol('omegastar', r'\omega^{*}')
Edef('omegastar', omegastar, omega / omegau)
Esol('omegastar', omega)

# wavenumber scale  (E.g. if 1/m, kstar = |k| / 1 m)
# kstar = k / ku
kstar = Esymbol('kstar', r'k^{*}')
Edef('kstar', kstar, k.mag / ku)
Esol('kstar', k.mag)

# velocity scale (== omegau / ku)
Edef('uu', uu, omegau / ku)
# Esol below. order matters for subsitutions.

# omegastars = omegas / omegau
omegastars = Esymbol('omegastars', r'\omega^{*}', ['s'])
Edef('omegastars', omegastars, omegas / omegau)
Esol('omegastars', omegas)

# ustars = us0 / uu
ustars = Esymbol('ustars', r'u^{*}', ['s'], vector=True)
Edef('ustars', ustars, us.o0 / uu)
Esol('ustars', us.o0)

mstars = Esymbol('mstars', r'm^{*}', ['s'])

# Tstars = (kB Ts0 / ms) * (1 / uu**2)
Tstars = Esymbol('Tstars', r'T^{*}', ['s'])
Edef('Tstars', Tstars, (kB * Ts.o0 / ms) / uu**2)
Esol('Tstars', Ts.o0)
Tstarn = Esymbol('Tstars', r'T^{*}', ['n'])
Edef('Tstarn', Tstarn, (kB * Tn / mn) / uu**2)
Esol('Tstarn', Tn)

# mstars = 1 + (ms / mn)
Edef('mstars', mstars, 1 + ms / mn)
Esol('mstars', ms)

# Estar = (E / B) / uu
Estar = Esymbol('Estar', r'E^{*}')
Edef('Estar', Estar, (E.o0.mag / B.mag) / uu)
Esol('Estar', E.o0.mag)

# nustarsn = nusn / omegau
nustarsn = Esymbol('nustarsn', r'\nu^{*}', ['s', 'n'])
Edef('nustarsn', nustarsn, nusn / omegau)
Esol('nustarsn', nusn)

# ustarks = ustars dot khat
ustarks = Esymbol('ustarks', r'u^{*}', ['k', 's'])
Edef('ustarks', ustarks, ustars.dot(khat))
Esol('ustarks', ustars.dot(khat))

# ustarls = ustars dot (khat.cross(Bhat))   # "lhat = khat.cross(Bhat)"
ustarls = Esymbol('ustarls', r'u^{*}', ['l', 's'])
_tmp = ustars.dot(khat.cross(Bhat)).simplify()
Edef('ustarls', ustarls, ustarks + kappas * _tmp)
Esol('ustarls', _tmp)

# uu symbol defined above. Esol order matters during substitutions.
Esol('uu', uu)

# equation system with starred definitions
tfbiE_stars_def = EquationSystem.from_dict(tfbiE_defs_dict)
tfbiE_stars_sol = EquationSystem.from_dict(tfbiE_sols_dict)

# # plug starred definitions into 0th order & dispersion relation # #
# also some other things:
#   hatify E0 and k (e.g. E.o0 = E.o0.mag * E.o0.hat)
#   ignore un. ([TODO] make ustarn instead, to test when un!=0)

# 0th order equations
tfbiE_o0_def = tfbiA_o0_sol.hatify(E.o0, k).subs(*tfbiE_stars_sol).simplify() 
tfbiE_o0_sol = tfbiE_o0_def.solution_put('Ts0', Tstars)

# coeffs (omegas, Ws, As, Bs, Cs, Fs)
tfbiE_coeffs = tfbiA_coeffs.ignore(un).hatify(E.o0, k).subs(*tfbiE_stars_sol)
tfbiE_coeffs = tfbiE_coeffs.solution_put(0, omegastars).simplify()
tfbiE_coeffs = tfbiE_coeffs.simplified().subs(*tfbiE_stars_sol).simplify()

# disprel & quasineutral disprel
tfbiE_disprel = tfbiA_disprel.subs(*tfbiE_stars_sol)
tfbiE_disprel = tfbiE_disprel.simplified().subs(*tfbiE_stars_sol)
tfbiE_disprel_QN = tfbiA_disprel_QN.subs(*tfbiE_stars_sol)
tfbiE_disprel_QN = tfbiE_disprel_QN.simplified().subs(*tfbiE_stars_sol)


''' --------------------- Loading vars into namespace --------------------- '''

LOAD_TFBI_E_KEYS.extend([
    'tfbiE_stars_def', 'tfbiE_stars_sol',
    'tfbiE_o0_def', 'tfbiE_o0_sol',
    'tfbiE_coeffs', 'tfbiE_disprel', 'tfbiE_disprel_QN',
])

_TFBI_E_LOCALS = locals()

def load_tfbiE(namespace=None):
    '''defines tfbi B terms in namespace (if provided), and returns dict of loaded values.
    E.g. load_tfbiE(locals()) populates locals with tfbiE terms.

    These variables are listed in LOAD_TFBI_E_KEYS.
    '''
    result = dict()
    for key in LOAD_TFBI_E_KEYS:
        result[key] = _TFBI_E_LOCALS[key]
    if namespace is not None:
        for key in result:
            namespace[key] = result[key]
    return result


''' --------------------- TfbiDisprelE --------------------- '''

class TfbiDisprelE(TfbiDisprelStarred):
    '''TfbiDisprelE: TfbiDisprelB but slightly improved for simplicity & efficiency:
    mstar = 1 + tfbiB_mstar. Also, use "ldebye^-2" as its own symbol.
    '''
    w = omegastar
    coeffs = tfbiE_coeffs
    disprel = tfbiE_disprel

    # for convenience:
    o0def = tfbiA_o0_def
    o0sol = tfbiA_o0_sol
    o0stardef = tfbiE_o0_def
    o0starsol = tfbiE_o0_sol
    stardef = tfbiE_stars_def
    starsol = tfbiE_stars_sol
    vv = load_tfbiE()  # dict of vars & equations relevant to TfbiE.


class TfbiDisprelE_QN(TfbiDisprelE):
    '''TfbiDisprelE_QN: TfbiDisprelE with QN disprel instead of including k on RHS.'''
    disprel = tfbiE_disprel_QN
