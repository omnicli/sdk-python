# -*- coding: utf-8 -*-
"""
Omni's argparser functionality

This provides a `parse_args` function that reads arguments from the
environment variables in which omni puts them, and returns them as a
Namespace object with the proper types, directly usable as if it was
the result of an `argparse.ArgumentParser.parse_args()` call.
"""

import os
from argparse import Namespace
from typing import Any, Dict, List, Optional, Tuple

from .errors import (
    ArgListMissingError,
    InvalidBooleanValueError,
    InvalidFloatValueError,
    InvalidIntegerValueError,
)


def _parse_type_info(type_str: str) -> Tuple[str, Optional[int]]:
    """
    Parse the type string into base type and array size if present.

    This can be in the shape:
        <type> for a single value
        <type>/<size> for an array
        <type>/<size>/<max_values> for grouped occurrences

    Args:
        type_str (str): The type string to parse.

    Returns:
        Tuple[str, Optional[int], bool]: The base type, array size and
        whether the occurrences are grouped.
    """
    parts = (type_str.split("/") + [None, None])[:3]
    base_type, size, group_occurrences = parts

    if size is not None:
        size = int(size)

    group_occurrences = group_occurrences is not None

    return base_type, size, group_occurrences


def _convert_value(value: str, type_name: str) -> Any:
    """Convert a string value to its proper type."""
    if type_name == "bool":
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        else:
            raise InvalidBooleanValueError(f"expected 'true' or 'false', got '{value}'")
    elif type_name == "int":
        try:
            return int(value)
        except ValueError:
            raise InvalidIntegerValueError(f"expected integer, got '{value}'")
    elif type_name == "float":
        try:
            return float(value)
        except ValueError:
            raise InvalidFloatValueError(f"expected float, got '{value}'")
    return value


def _get_arg_list() -> List[str]:
    """
    Get the list of available arguments from OMNI_ARG_LIST.

    Returns:
        List[str]: List of argument names in lowercase.

    Raises:
        ArgListMissingError: If OMNI_ARG_LIST environment variable is not set.
    """
    arg_list_str = os.getenv("OMNI_ARG_LIST")
    if arg_list_str is None:
        raise ArgListMissingError(
            "OMNI_ARG_LIST environment variable is not set. "
            'Are you sure "argparser: true" is set for this command?'
        )

    return [arg.lower() for arg in arg_list_str.split()]


def _get_arg_type(
    arg_name: str, index: Optional[int] = None
) -> Optional[Tuple[str, Optional[int], bool]]:
    """Get the type of the argument from the environment variables."""
    key = f"OMNI_ARG_{arg_name.upper()}_TYPE"
    if index is not None:
        key = f"{key}_{index}"

    type_str = os.getenv(key)
    if type_str is None:
        return None

    return _parse_type_info(type_str)


def _get_arg_value(
    arg_name: str, arg_type: str, index1: Optional[int] = None, index2: Optional[int] = None
) -> Optional[str]:
    """Get the value of the argument from the environment variables."""
    key = f"OMNI_ARG_{arg_name.upper()}_VALUE"
    if index1 is not None:
        key = f"{key}_{index1}"
        if index2 is not None:
            key = f"{key}_{index2}"

    value = os.getenv(key)
    if value is None:
        if arg_type == "str":
            return ""
        return None

    return _convert_value(value, arg_type)


def parse_args() -> Namespace:
    """
    Read omni arguments from environment variables.

    Returns:
        argparse.Namespace: Object containing the read arguments, with the
        proper types.

    Raises:
        ArgListMissingError: If OMNI_ARG_LIST environment variable is not set.
    """
    arg_list = _get_arg_list()

    # Early return if there are no arguments
    if not arg_list:
        return Namespace()

    # Prepare a disctionary to hold the arguments
    args_dict: Dict[str, Any] = {}

    for arg_name in arg_list:
        arg_type = _get_arg_type(arg_name)

        # If the type is not set, we set the value to None
        if arg_type is None:
            args_dict[arg_name] = None
            continue

        base_type, array_size, group_occurrences = arg_type

        if array_size is not None:
            if group_occurrences:
                # If occurrences are grouped, we need to recompose a nested
                # array since we will have two levels, we also need to get
                # the number of values for each group
                values = []
                for group_idx in range(array_size):
                    _, group_size, _ = _get_arg_type(arg_name, group_idx)
                    if group_size is None or group_size == 0:
                        values.append([])
                    else:
                        values.append(
                            [
                                _get_arg_value(arg_name, base_type, group_idx, idx)
                                for idx in range(group_size)
                            ]
                        )
                args_dict[arg_name] = values
            else:
                # If the argument is an array, we need to get each value
                # and store it in a list; we keep the "None" values if any
                # since the array has provided a size and we just follow it
                args_dict[arg_name] = [
                    _get_arg_value(arg_name, base_type, idx)
                    for idx in range(array_size)
                ]
        else:
            # If the argument is not an array, we just get the value
            args_dict[arg_name] = _get_arg_value(arg_name, base_type)

    return Namespace(**args_dict)
