# -*- coding: utf-8 -*-
import os
import pytest
from omnicli.errors import (
    ArgListMissingError,
    InvalidBooleanValueError,
    InvalidFloatValueError,
    InvalidIntegerValueError,
)
from omnicli import parse_args


@pytest.fixture
def clean_env():
    """Remove all OMNI_ARG related environment variables before each test."""
    # Store original environment
    old_env = {k: v for k, v in os.environ.items() if k.startswith("OMNI_ARG_")}

    # Remove all OMNI_ARG variables
    for k in list(os.environ.keys()):
        if k.startswith("OMNI_ARG_"):
            del os.environ[k]

    yield

    # Restore original environment
    for k in list(os.environ.keys()):
        if k.startswith("OMNI_ARG_"):
            del os.environ[k]
    os.environ.update(old_env)


@pytest.mark.usefixtures("clean_env")
def test_missing_arg_list():
    """Should raise ArgListMissingError when OMNI_ARG_LIST is not set."""
    with pytest.raises(ArgListMissingError) as exc:
        parse_args()
    assert 'Are you sure "argparser: true" is set for this command?' in str(exc.value)


@pytest.mark.usefixtures("clean_env")
def test_empty_arg_list():
    """Should return empty Namespace when OMNI_ARG_LIST is empty."""
    os.environ["OMNI_ARG_LIST"] = ""
    args = parse_args()
    assert not vars(args)


@pytest.mark.usefixtures("clean_env")
def test_string_arg_defaults():
    """Should handle string arguments with proper defaults."""
    os.environ["OMNI_ARG_LIST"] = "test1 test2"
    os.environ["OMNI_ARG_TEST1_TYPE"] = "str"
    os.environ["OMNI_ARG_TEST1_VALUE"] = "value"
    os.environ["OMNI_ARG_TEST2_TYPE"] = "str"
    # Deliberately not setting TEST2_VALUE

    args = parse_args()
    assert args.test1 == "value"
    assert args.test2 == ""  # Empty string is default for str type


@pytest.mark.usefixtures("clean_env")
def test_non_string_arg_defaults():
    """Should handle non-string arguments with None defaults."""
    os.environ["OMNI_ARG_LIST"] = "num1 num2"
    os.environ["OMNI_ARG_NUM1_TYPE"] = "int"
    os.environ["OMNI_ARG_NUM1_VALUE"] = "42"
    os.environ["OMNI_ARG_NUM2_TYPE"] = "int"
    # Deliberately not setting NUM2_VALUE

    args = parse_args()
    assert args.num1 == 42
    assert args.num2 is None


@pytest.mark.usefixtures("clean_env")
def test_array_handling():
    """Should handle arrays with proper sizing and None values."""
    os.environ["OMNI_ARG_LIST"] = "numbers"
    os.environ["OMNI_ARG_NUMBERS_TYPE"] = "int/3"
    os.environ["OMNI_ARG_NUMBERS_VALUE_0"] = "1"
    # Deliberately skipping VALUE_1
    os.environ["OMNI_ARG_NUMBERS_VALUE_2"] = "3"

    args = parse_args()
    assert args.numbers == [1, None, 3]


@pytest.mark.usefixtures("clean_env")
def test_bool_array():
    """Should handle boolean arrays with proper defaults."""
    os.environ["OMNI_ARG_LIST"] = "flags"
    os.environ["OMNI_ARG_FLAGS_TYPE"] = "bool/3"
    os.environ["OMNI_ARG_FLAGS_VALUE_0"] = "true"
    # Deliberately skipping VALUE_1
    os.environ["OMNI_ARG_FLAGS_VALUE_2"] = "false"

    args = parse_args()
    assert args.flags == [True, None, False]


@pytest.mark.usefixtures("clean_env")
def test_float_array():
    """Should handle float arrays with proper defaults."""
    os.environ["OMNI_ARG_LIST"] = "floats"
    os.environ["OMNI_ARG_FLOATS_TYPE"] = "float/4"
    os.environ["OMNI_ARG_FLOATS_VALUE_0"] = "1.1"
    # Deliberately skipping VALUE_1
    os.environ["OMNI_ARG_FLOATS_VALUE_2"] = "3.3"
    os.environ["OMNI_ARG_FLOATS_VALUE_3"] = "4"

    args = parse_args()
    assert args.floats == [1.1, None, 3.3, 4.0]


@pytest.mark.usefixtures("clean_env")
def test_string_array_defaults():
    """Should handle string arrays with proper defaults."""
    os.environ["OMNI_ARG_LIST"] = "words"
    os.environ["OMNI_ARG_WORDS_TYPE"] = "str/3"
    os.environ["OMNI_ARG_WORDS_VALUE_0"] = "hello"
    # Deliberately skipping VALUE_1
    os.environ["OMNI_ARG_WORDS_VALUE_2"] = "world"

    args = parse_args()
    assert args.words == ["hello", "", "world"]


@pytest.mark.usefixtures("clean_env")
def test_boolean_values():
    """Should handle boolean values correctly."""

    test_cases = {
        "flag1": ("true", True),
        "flag2": ("false", False),
        "flag3": ("True", True),
        "flag4": ("False", False),
        "flag5": ("tRuE", True),
        "flag6": ("fAlSe", False),
    }

    os.environ["OMNI_ARG_LIST"] = " ".join(test_cases.keys())
    for flag, (value, _) in test_cases.items():
        os.environ[f"OMNI_ARG_{flag.upper()}_TYPE"] = "bool"
        os.environ[f"OMNI_ARG_{flag.upper()}_VALUE"] = value

    args = parse_args()
    for flag, (_, expected) in test_cases.items():
        assert getattr(args, flag.lower()) is expected


@pytest.mark.usefixtures("clean_env")
def test_missing_type():
    """Should set None for arguments without a type definition."""
    os.environ["OMNI_ARG_LIST"] = "test"
    # Deliberately not setting OMNI_ARG_TEST_TYPE

    args = parse_args()
    assert args.test is None


@pytest.mark.usefixtures("clean_env")
def test_numeric_types():
    """Should handle numeric types correctly."""
    os.environ["OMNI_ARG_LIST"] = "int_val float_val"

    os.environ["OMNI_ARG_INT_VAL_TYPE"] = "int"
    os.environ["OMNI_ARG_INT_VAL_VALUE"] = "42"

    os.environ["OMNI_ARG_FLOAT_VAL_TYPE"] = "float"
    os.environ["OMNI_ARG_FLOAT_VAL_VALUE"] = "3.14"

    args = parse_args()
    assert args.int_val == 42
    assert isinstance(args.int_val, int)
    assert args.float_val == 3.14
    assert isinstance(args.float_val, float)


@pytest.mark.usefixtures("clean_env")
def test_case_sensitivity():
    """Should handle case sensitivity correctly:
    - Accept any case in OMNI_ARG_LIST
    - Use uppercase for environment variable names
    - Always use lowercase in the resulting Namespace
    """
    os.environ["OMNI_ARG_LIST"] = "TestArg UPPER_ARG lower_arg"

    # Set up environment variables (always uppercase in env vars)
    os.environ["OMNI_ARG_TESTARG_TYPE"] = "str"
    os.environ["OMNI_ARG_TESTARG_VALUE"] = "test"

    os.environ["OMNI_ARG_UPPER_ARG_TYPE"] = "str"
    os.environ["OMNI_ARG_UPPER_ARG_VALUE"] = "upper"

    os.environ["OMNI_ARG_LOWER_ARG_TYPE"] = "str"
    os.environ["OMNI_ARG_LOWER_ARG_VALUE"] = "lower"

    args = parse_args()

    # All attributes should be lowercase in the namespace
    assert args.testarg == "test"
    assert args.upper_arg == "upper"
    assert args.lower_arg == "lower"

    # Verify that the original casing is not preserved
    assert not hasattr(args, "TestArg")
    assert not hasattr(args, "UPPER_ARG")


@pytest.mark.usefixtures("clean_env")
def test_invalid_int_value():
    """Should raise ValueError for invalid numeric values."""
    os.environ["OMNI_ARG_LIST"] = "number"
    os.environ["OMNI_ARG_NUMBER_TYPE"] = "int"
    os.environ["OMNI_ARG_NUMBER_VALUE"] = "not_a_number"

    with pytest.raises(InvalidIntegerValueError):
        parse_args()


@pytest.mark.usefixtures("clean_env")
def test_invalid_float_value():
    """Should raise ValueError for invalid float values."""
    os.environ["OMNI_ARG_LIST"] = "number"
    os.environ["OMNI_ARG_NUMBER_TYPE"] = "float"
    os.environ["OMNI_ARG_NUMBER_VALUE"] = "not_a_number"

    with pytest.raises(InvalidFloatValueError):
        parse_args()


@pytest.mark.usefixtures("clean_env")
def test_invalid_bool_value():
    """Should raise ValueError for invalid boolean values."""
    os.environ["OMNI_ARG_LIST"] = "flag"
    os.environ["OMNI_ARG_FLAG_TYPE"] = "bool"
    os.environ["OMNI_ARG_FLAG_VALUE"] = "not_a_boolean"

    with pytest.raises(InvalidBooleanValueError):
        parse_args()
