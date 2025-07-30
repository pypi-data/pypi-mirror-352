"""
File Purpose: TfbiDisprelC

Similar to TfbiDisprelB, but includes a few more simplifications:
    mstar = 1 + tfbiB_mstar
    use "ldebye^-2" as a symbol, instead of ldebye symbol, squared.
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

LOAD_TFBI_C_KEYS = list(LOAD_VARS_KEYS)    # start with copy of load vars keys.
tfbiC_defs_dict = dict()  # dict of defined equations
tfbiC_sols_dict = dict()  # dict of solutions to defined equations.

def Csymbol(localname, *args_symbol, **kw_symbol):
    '''creates and returns symbol, and appends localname to LOAD_TFBI_C_KEYS'''
    LOAD_TFBI_C_KEYS.append(localname)
    return symbol(*args_symbol, **kw_symbol)
def Cdef(label, lhs, rhs):
    '''sets tfbiC_defs_dict[label] = equation(lhs, rhs, label=label)'''
    tfbiC_defs_dict[label] = equation(lhs, rhs, label=label)
def Csol(label, solve_for, **kw_solve):
    '''sets tfbiC_sols_dict[label] = tfbiC_defs_dict[label].solve(solve_for)'''
    tfbiC_sols_dict[label] = tfbiC_defs_dict[label].solve(solve_for, **kw_solve)
    
k = K
omega = OMEGA

# # ldebye^-2 as its own symbol
ldebyes_neg2 = Csymbol('ldebyes_neg2', r'\lambda^{-2}', ['s'])
Cdef('ldebyes_neg2', ldebyes_neg2, ldebyes**-2)
Csol('ldebyes_neg2', ldebyes**-2)

# # "Adimensionalize" # #
# frequency scale  (E.g. if 1 Hz, nustarsn = nusn / 1 Hz.)
# omega = omega / omegau
omegastar = Csymbol('omegastar', r'\omega^{*}')
Cdef('omegastar', omegastar, omega / omegau)
Csol('omegastar', omega)

# wavenumber scale  (E.g. if 1/m, kstar = |k| / 1 m)
# kstar = k / ku
kstar = Csymbol('kstar', r'k^{*}')
Cdef('kstar', kstar, k.mag / ku)
Csol('kstar', k.mag)

# velocity scale (== omegau / ku)
Cdef('uu', uu, omegau / ku)
# Will put Csol('uu', uu) later; order matters for subsitutions. See below.

# omegastars = omegas / omegau
omegastars = Csymbol('omegastars', r'\omega^{*}', ['s'])
Cdef('omegastars', omegastars, omegas / omegau)
Csol('omegastars', omegas)

# ustars = us0 / uu
ustars = Csymbol('ustars', r'u^{*}', ['s'], vector=True)
Cdef('ustars', ustars, us.o0 / uu)
Csol('ustars', us.o0)

# Tstars = (kB Ts0 / ms) * (1 / uu**2)
Tstars = Csymbol('Tstars', r'T^{*}', ['s'])
Cdef('Tstars', Tstars, (kB * Ts.o0 / ms) / uu**2)
Csol('Tstars', Ts.o0)
Tstarn = Csymbol('Tstars', r'T^{*}', ['n'])
Cdef('Tstarn', Tstarn, (kB * Tn / mn) / uu**2)
Csol('Tstarn', Tn)

# mstars = 1 + (ms / mn)
mstars = Csymbol('mstars', r'm^{*}', ['s'])
Cdef('mstars', mstars, 1 + ms / mn)
Csol('mstars', ms)

# Estar = (E / B) / uu
Estar = Csymbol('Estar', r'E^{*}')
Cdef('Estar', Estar, (E.o0.mag / B.mag) / uu)
Csol('Estar', E.o0.mag)

# nustarsn = nusn / omegau
nustarsn = Csymbol('nustarsn', r'\nu^{*}', ['s', 'n'])
Cdef('nustarsn', nustarsn, nusn / omegau)
Csol('nustarsn', nusn)

# ustarks = ustars dot khat
ustarks = Csymbol('ustarks', r'u^{*}', ['k', 's'])
Cdef('ustarks', ustarks, ustars.dot(khat))
Csol('ustarks', ustars.dot(khat))

# ustarls = ustars dot (khat.cross(Bhat))   # "lhat = khat.cross(Bhat)"
ustarls = Csymbol('ustarls', r'u^{*}', ['l', 's'])
_tmp = ustars.dot(khat.cross(Bhat)).simplify()
Cdef('ustarls', ustarls, _tmp)
Csol('ustarls', _tmp)

# put solution for uu later; order matters during substitutions.
Csol('uu', uu)

# equation system with starred definitions
tfbiC_stars_def = EquationSystem.from_dict(tfbiC_defs_dict)
tfbiC_stars_sol = EquationSystem.from_dict(tfbiC_sols_dict)

# # plug starred definitions into 0th order & dispersion relation # #
# also some other things:
#   hatify E0 and k (e.g. E.o0 = E.o0.mag * E.o0.hat)
#   ignore un. ([TODO] make ustarn instead, to test when un!=0)

# 0th order equations
tfbiC_o0_def = tfbiA_o0_sol.hatify(E.o0, k).subs(*tfbiC_stars_sol).simplify() 
tfbiC_o0_sol = tfbiC_o0_def.solution_put('Ts0', Tstars)

# coeffs (omegas, Ws, As, Bs, Cs, Fs)
tfbiC_coeffs = tfbiA_coeffs.ignore(un).hatify(E.o0, k).subs(*tfbiC_stars_sol)
tfbiC_coeffs = tfbiC_coeffs.simplified().subs(*tfbiC_stars_sol)

# disprel & quasineutral disprel
tfbiC_disprel = tfbiA_disprel.subs(*tfbiC_stars_sol)
tfbiC_disprel = tfbiC_disprel.simplified().subs(*tfbiC_stars_sol)
tfbiC_disprel_QN = tfbiA_disprel_QN.subs(*tfbiC_stars_sol)
tfbiC_disprel_QN = tfbiC_disprel_QN.simplified().subs(*tfbiC_stars_sol)


''' --------------------- Loading vars into namespace --------------------- '''

LOAD_TFBI_C_KEYS.extend([
    'tfbiC_stars_def', 'tfbiC_stars_sol',
    'tfbiC_o0_def', 'tfbiC_o0_sol',
    'tfbiC_coeffs', 'tfbiC_disprel', 'tfbiC_disprel_QN',
])

_TFBI_C_LOCALS = locals()

def load_tfbiC(namespace=None):
    '''defines tfbi C terms in namespace (if provided), and returns dict of loaded values.
    E.g. load_tfbiC(locals()) populates locals with tfbiC terms.

    These variables are listed in LOAD_TFBI_C_KEYS.
    '''
    result = dict()
    for key in LOAD_TFBI_C_KEYS:
        result[key] = _TFBI_C_LOCALS[key]
    if namespace is not None:
        for key in result:
            namespace[key] = result[key]
    return result


''' --------------------- TfbiDisprelC --------------------- '''

class TfbiDisprelC(TfbiDisprelStarred):
    '''TfbiDisprelC: TfbiDisprelB but slightly improved for simplicity & efficiency:
    mstar = 1 + tfbiB_mstar. Also, use "ldebye^-2" as its own symbol.
    '''
    w = omegastar
    coeffs = tfbiC_coeffs
    disprel = tfbiC_disprel
    o0def = tfbiA_o0_def
    o0sol = tfbiA_o0_sol

    # for convenience:
    o0stardef = tfbiC_o0_def
    o0starsol = tfbiC_o0_sol
    stardef = tfbiC_stars_def
    starsol = tfbiC_stars_sol
    vv = load_tfbiC()  # dict of vars & equations relevant to TfbiC.


class TfbiDisprelC_QN(TfbiDisprelC):
    '''TfbiDisprelC_QN: TfbiDisprelC with QN disprel instead of including k on RHS.'''
    disprel = tfbiC_disprel_QN
