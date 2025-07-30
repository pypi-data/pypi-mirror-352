"""
File Purpose: TfbiDisprelA

basic TFBI disprel. Matches Evans+2023.
"""
import SymSolver as ss
from SymSolver import (  # some of the things we will use a lot here:
    symbols, symbol,
    equation, equation_system, EquationSystem,
)

from .disprel import TfbiDisprelPredefined
from .vars import load_vars, LOAD_VARS_KEYS

# load variables DIRECTLY INTO LOCALS().
load_vars(locals())

# # Zeroth order terms (assuming strictly: B=B0 and Tn=Tn0) # #
tfbiA_o0_dict = {
    'momentum0': (0, E.o0 + us.o0.cross(B) - B.mag * us.o0/kappas),  # momentum but all derivatives == 0
    'heating0': (0, ONE_THIRD * mn * us.o0.dot(us.o0) / kB + Tn - Ts.o0),
}
tfbiA_o0_def = EquationSystem.from_dict(tfbiA_o0_dict)

eq_us0 = tfbiA_o0_def['momentum0'].solve(us.o0).with_label('us0')
eq_us0 = eq_us0.hatify(B, E.o0).simplified(ignoring=[E0hat.dot(Bhat)], magnitude_id=True)
eq_Ts0 = tfbiA_o0_def['heating0'].solve(Ts.o0, simplify=dict(magnitude_id=False)).with_label('Ts0')
eq_Ts0 = eq_Ts0.subs(eq_us0).simplified(magnitude_id=True, ignoring=[E0hat.dot(Bhat)])

tfbiA_o0_sol = equation_system(eq_us0, eq_Ts0)

# # Dispersion Relation in terms of constructed variables # #
tfbiA_coeffs_dict = {
    'omegas': (omegas, omega - k.dot(us.o0)),
    'Ws': (Ws, 1 - i * omegas / nusn),
    'As': (As, -1 * i * Ts.o0 * kB / ms * k.dot(k) / (nusn * omegas) * (Ws / (Ws**2 + kappas**2))),
    'Bs': (Bs, 4 * ONE_THIRD * mn / ((mn + ms) * omegas * (Ws**2 + kappas**2)) * 
                (us.o0 - un).dot(Ws * k + kappas * k.cross(Bhat))),
    'Cs': (Cs, omegas / (2 * i * (ms / (mn + ms)) * nusn + omegas)),  # mus^-1
    'Fs': (Fs, As / ( 1 - (1 + 2 * ONE_THIRD * Cs) * As - Bs * Cs)),
}
tfbiA_coeffs = EquationSystem.from_dict(tfbiA_coeffs_dict).simplify()

tfbiA_disprel = equation(sum_s(Fs / ldebyes**2), k.mag**2)  # <-- full disprel
tfbiA_disprel_QN = equation(sum_s(Fs / ldebyes**2), 0)  # <-- quasineutral


''' --------------------- Loading vars into namespace --------------------- '''

LOAD_TFBI_A_KEYS = LOAD_VARS_KEYS + [
    'tfbiA_o0_def', 'tfbiA_o0_sol',
    'tfbiA_coeffs', 'tfbiA_disprel', 'tfbiA_disprel_QN',
]

_TFBI_A_LOCALS = locals()

def load_tfbiA(namespace=None):
    '''defines tfbi A terms in namespace (if provided), and returns dict of loaded values.
    E.g. load_tfbiA(locals()) populates locals with tfbiA terms.

    These variables are listed in LOAD_TFBI_A_KEYS.
    '''
    result = dict()
    for key in LOAD_TFBI_A_KEYS:
        result[key] = _TFBI_A_LOCALS[key]
    if namespace is not None:
        for key in result:
            namespace[key] = result[key]
    return result


''' --------------------- TfbiDisprelA --------------------- '''

class TfbiDisprelA(TfbiDisprelPredefined):
    '''TfbiDisprelA. Basic TFBI disprel. Matches Evans+2023.'''
    w = omega
    coeffs = tfbiA_coeffs
    disprel = tfbiA_disprel

    o0def = tfbiA_o0_def
    o0sol = tfbiA_o0_sol

    vv = load_tfbiA()  # dict of vars & equations relevant to TfbiA.


class TfbiDisprelA_QN(TfbiDisprelA):
    '''TfbiDisprelA_QN: TfbiDisprelA with QN disprel instead of including k on RHS.'''
    disprel = tfbiA_disprel_QN
