"""
Package Purpose: writing the dispersion relation
"""
from .disprel import TfbiDisprel, TfbiDisprelPredefined, TfbiDisprelStarred
from .disprel_A import TfbiDisprelA, TfbiDisprelA_QN, load_tfbiA, LOAD_TFBI_A_KEYS
from .disprel_B import TfbiDisprelB, TfbiDisprelB_QN, load_tfbiB, LOAD_TFBI_B_KEYS
from .disprel_C import TfbiDisprelC, TfbiDisprelC_QN, load_tfbiC, LOAD_TFBI_C_KEYS
from .disprel_Cmns import TfbiDisprelCmns, TfbiDisprelCmns_QN, load_tfbiCmns, LOAD_TFBI_Cmns_KEYS
# disprel_D name reserved to match D from InstabilityTheory package. Not as good as C though.
from .disprel_E import TfbiDisprelE, TfbiDisprelE_QN, load_tfbiE, LOAD_TFBI_E_KEYS

from .inputs import (
    kPicker, kPickerLowres, kPickerMidres, kPickerHighres,
    TfbiInputManager, TfbiInputManagerStarred,
)
from .vars import load_vars, TFBI_SS_PRESETS, LOAD_VARS_KEYS

# additional misc. imports:
from .disprel_Cmns import TfbiInputManagerCmns
