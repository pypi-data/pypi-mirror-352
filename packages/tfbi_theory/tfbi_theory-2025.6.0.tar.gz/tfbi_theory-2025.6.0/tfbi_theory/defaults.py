"""
File Purpose: defaults in tfbi_theory package.
"""

class _Defaults():
    '''stores defaults for tfbi_theory package. Use DEFAULTS instead.
    (DEFAULTS is an instance of _Defaults(), instantiated at the bottom of defaults.py)
    '''
    def update(self, other_defaults):
        '''update self with other_defaults, overwriting any existing values.
        other_defaults: dict or _Defaults instance
            dict --> update from other_defaults.items()
            else --> update from other_defaults.__dict__.items()
        '''
        if not isinstance(other_defaults, dict):
            other_defaults = other_defaults.__dict__
        for key, value in other_defaults.items():
            setattr(self, key, value)

    TRACEBACKHIDE = True
    IMPORT_FAILURE_WARNINGS = False

    TAB = ' '*4   # size of a single tab, e.g. for docstrings.

    PROGRESS_UPDATES_PRINT_FREQ = 2  # seconds between progress updates

DEFAULTS = _Defaults()
