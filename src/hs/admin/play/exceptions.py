""" This module provides exception classes.
"""



class MissingArgumentError(Exception):
    """ Raised when a mandatory argument is missing.
    """


class InvalidArgumentError(Exception):
    """ Raised when an argument has an invalid type or structure.
    """


class APIInitializationError(Exception):
    """ Raised when the HSAdmin API initialization failed.
    """


class APIInvokationError(Exception):
    """ Raised when an HSAdmin API invokation failed.
    """


class AmbiguousResultsError(Exception):
    """ Raised when ambiguous results were retrieved.
    """
