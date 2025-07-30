"""
File Purpose: errors in tfbi_theory package.
"""


''' --------------------- Misc Errors --------------------- '''

class ImportFailedError(ImportError):
    '''error indicating that an import failed in the past, which is why a module cannot be accessed now.'''
    pass

class TimeoutError(Exception):
    '''error indicating a timeout.'''
    pass


''' --------------------- InputErrors --------------------- '''

class InputError(TypeError):
    '''error indicating something is wrong with the inputs, e.g. to a function.'''
    pass

class InputConflictError(InputError):
    '''error indicating two or more inputs provide conflicting information.
    E.g. foo(lims=None, vmin=None, vmax=None) receiving lims=(1,7), vmin=3, might raise this error,
    if the intention is for vmin and vmax to be aliases to lims[0] and lims[1].
    '''
    pass

class InputMissingError(InputError):
    '''error indicating that an input is missing AND doesn't have an appropriate default value.
    E.g. default=None; def foo(kwarg=None): if kwarg is None: kwarg=default; but foo expects non-None value.
    '''
    pass


''' --------------------- DimensionErrors --------------------- '''

class DimensionError(Exception):
    '''error indicating some issue with a dimension'''
    pass

class DimensionalityError(DimensionError):
    '''error indicating dimensionality issue, e.g. wrong number of dimensions'''
    pass

class DimensionSizeError(DimensionError):
    '''error indicating a dimension is the wrong size.'''
    pass

class DimensionKeyError(KeyError, DimensionError):
    '''error indicating missing value of a dimension (e.g. FluidKeyError, SnapKeyError).'''
    def __str__(self):
        '''use standard error string. Avoid KeyError string which uses repr(message).'''
        return super(KeyError, self).__str__()

class DimensionValueError(ValueError, DimensionError):
    '''error indicating some incompatibility regarding the value of a dimension (e.g. SnapValueError)'''
    pass


''' --------------------- PlottingErrors --------------------- '''

class PlottingError(ValueError):
    '''error indicating an issue with plotting'''
    pass
