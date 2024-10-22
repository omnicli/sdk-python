# -*- coding: utf-8 -*-
"""
omnicli - Python SDK for omni

This package provides functionality to build omni commands in python.
"""

from .errors import (
    ArgListMissingError,
    InvalidBooleanValueError,
    InvalidFloatValueError,
    InvalidIntegerValueError,
    OmniCliError,
)
from .argparser import (
    parse_args,
)

try:
    from .version import __version__  # type: ignore
except ImportError:
    __version__ = "0.0.0+unknown"

__all__ = [
    "ArgListMissingError",
    "InvalidBooleanValueError",
    "InvalidFloatValueError",
    "InvalidIntegerValueError",
    "OmniCliError",
    "parse_args",
]
