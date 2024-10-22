# -*- coding: utf-8 -*-
"""
Omni's error classes
"""


class OmniCliError(Exception):
    """Base exception for omnicli-related errors."""

    pass


class ArgListMissingError(OmniCliError):
    """Raised when the OMNI_ARG_LIST environment variable is missing."""

    pass


class InvalidValueError(OmniCliError):
    """Raised when an invalid value is encountered."""

    pass


class InvalidBooleanValueError(InvalidValueError):
    """Raised when an invalid boolean value is encountered."""

    pass


class InvalidIntegerValueError(InvalidValueError):
    """Raised when an invalid integer value is encountered."""

    pass


class InvalidFloatValueError(InvalidValueError):
    """Raised when an invalid float value is encountered."""

    pass
