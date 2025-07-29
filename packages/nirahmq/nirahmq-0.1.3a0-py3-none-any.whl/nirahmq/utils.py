#  SPDX-License-Identifier: AGPL-3.0-or-later
#  Copyright (C) 2025  Dionisis Toulatos

import re
from enum import Enum
from typing import Annotated

from pydantic import AfterValidator, BaseModel as PydanticBaseModel, ConfigDict


# Why in gods green earth does pydantic not allow to have an optional, non-nullable field
# that is not defined by default? Hence, this monstrosity of a custom singleton type hint below.
class _Unset(Enum):
    TOKEN = None


Unset = _Unset.TOKEN
"""A custom singleton type used by to indicate a value is unset."""

type Optional[T] = T | _Unset

type Required = None  # Required fields should always be defined like `Annotated[<actual type>, Required]`


def _validate_regex_string(value: str) -> str:
    try:
        re.compile(value)
        return value
    except re.error:
        raise ValueError(f"Invalid regex string: {value}")


type Regex = Annotated[str, AfterValidator(_validate_regex_string)]
"""A custom type alias used by :py:mod:`nirahmq` to validate a string is a valid regex pattern."""


def sanitize_string(string: str) -> str:
    """Sanitizes a string for use as an MQTT topic.

    .. note:: The sanitization is not an MQTT restriction but a Home Assistant one.

    :param str string: The string to be sanitized
    :return: The sanitized string
    :rtype: str
    """
    # Replace whitespace character between non-whitespace ones with single underscore
    string = re.sub(r"(\S)\s+(\S)", r"\1_\2", string)
    # Replace non-valid characters with nothing (remove them)
    # This handles any whitespaces that are at the beginning or at the end
    string = re.sub(r"[^a-zA-Z0-9_-]+", '', string)
    return string


def clamp[T](val: T, min_: T, max_: T) -> T:
    """Clamp a value in the range :math:`[min\\_, max\\_]`.

    :param T val: The value to be clamped
    :param T min\\_: The minimum allowed value (inclusive)
    :param T max\\_: The maximum allowed value (inclusive)
    :return: The clamped value
    :rtype: T
    """
    return min(max(val, min_), max_)


class BaseModel(PydanticBaseModel):
    """A customized :py:class:`pydantic.BaseModel` class for use by the rest of the library."""

    model_config = ConfigDict(
        validate_by_alias=True,
        validate_by_name=True,
        # use_enum_values=True,
        validate_default=True,
        strict=True,
        extra='forbid'
    )
