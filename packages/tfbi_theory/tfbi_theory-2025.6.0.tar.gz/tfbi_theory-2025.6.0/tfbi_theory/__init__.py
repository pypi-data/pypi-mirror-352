"""Solving the linear theory of the Thermal Farley-Buneman Instability (TFBI).

[TODO] more details about tfbi_theory here.
"""

# File Purpose: importing important things from modules in this package.

# [TODO] explicit imports instead of *

__version__ = '2025.6.0'  # YYYY.MM.MICRO  # MM not 0M, to match pip normalization.
# For non-release versions, use YYYY.MM.MICRO-dev,
#    to indicate the version has no corresponding release.
# in practical terms, to publish new release:
#    (1) remove '-dev' & update version number. E.g. '2024.12.0'
#    (2) push commit with message like: '[VERSION] 2024.12.0'
#    (3) publish release (e.g. git tag, flit build, flit publish)
#    (4) restore '-dev' but do not alter version number. E.g. '2024.12.0-dev'.
#    (5) push commit with message like: '[VERSION] 2024.12.0-dev'

from .algebra import *
from .tools import *

from .defaults import DEFAULTS
from .errors import *
