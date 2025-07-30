"""
File Purpose: define some variables related to (basic) TFBI theory.
"""
import SymSolver as ss
from SymSolver import (  # some of the things we will use a lot here:
    symbols, symbol,
    equation, equation_system, EquationSystem,
)


ONE_THIRD = ss.rational(1, 3)

# load variables from SymSolver DIRECTLY INTO locals().
TFBI_SS_PRESETS = ss.load_presets('FLUIDS', 'PLASMA_QUANTS',
                                     'MISC', 'REQUIRED',
                                     'PHYSICAL_CONSTANTS',
                                     dst=locals())

# aliases to existing variables
k = K
omega = OMEGA

# other useful quantities
sum_s = ss.summation_operator('s')
Bhat = B.as_hat()
E0hat = E.o0.as_hat()
khat = K.as_hat()

# TFBI-related variables:
As, Bs, Cs, Fs, Ws, omegas = \
    symbols(r'\mathcal{A} \mathcal{B} \mathcal{C} F \mathcal{W} \omega', ['s'])

# units scaling variables:
omegau, ku, uu = \
    symbols(r'\omega k u', ['u'])


''' --------------------- Loading vars into namespace --------------------- '''

LOAD_VARS_KEYS = list(TFBI_SS_PRESETS.keys()) + [
    'ONE_THIRD', 'k', 'khat', 'omega',
    'Bhat', 'E0hat',
    'sum_s', 'As', 'Bs', 'Cs', 'Fs', 'Ws', 'omegas',
    'omegau', 'ku', 'uu',
]

_VARS_LOCALS = locals()

def load_vars(namespace=None):
    '''defines tfbi variables in namespace (if provided), and returns dict of loaded values.
    E.g. load_vars(locals()) populates locals with tfbi terms.

    These variables are listed in LOAD_VARS_KEYS.
    '''
    result = dict()
    for key in LOAD_VARS_KEYS:
        result[key] = _VARS_LOCALS[key]
    if namespace is not None:
        for key in result:
            namespace[key] = result[key]
    return result
