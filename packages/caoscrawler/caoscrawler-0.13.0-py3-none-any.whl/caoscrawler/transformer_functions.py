#!/usr/bin/env python3
# encoding: utf-8
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2024 Indiscale GmbH <info@indiscale.com>
# Copyright (C) 2024 Henrik tom Wörden <h.tomwoerden@indiscale.com>
# Copyright (C) 2023 Alexander Schlemmer <alexander.schlemmer@ds.mpg.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Definition of default transformer functions.

See https://docs.indiscale.com/caosdb-crawler/converters.html#transform-functions for more
information.

"""

import datetime
import re
from typing import Any


def submatch(in_value: Any, in_parameters: dict):
    """
    Substitute the variable if it matches the regexp stored in "match".

    Returns the "in" value if it does NOT match the reg exp of 'match'.
    Otherwise (if it matches) the value of 'then' stored in the second argument is returned.
    """
    if "match" not in in_parameters or "then" not in in_parameters:
        raise RuntimeError("Mandatory parameters missing.")
    if re.match(in_parameters["match"], in_value) is not None:
        return in_parameters["then"]
    return in_value


def split(in_value: Any, in_parameters: dict):
    """calls the string 'split' function on the first argument and uses the value of the key
    'marker' stored in the second argument
    """
    if "marker" not in in_parameters:
        raise RuntimeError("Mandatory parameter missing.")
    if not isinstance(in_value, str):
        raise RuntimeError("must be string")
    return in_value.split(in_parameters['marker'])


def replace(in_value: Any, in_parameters: dict):
    """calls the string 'replace' function on the first argument and uses the value of the keys
    'remove' and 'insert' stored in the second argument
    """
    if "remove" not in in_parameters or "insert" not in in_parameters:
        raise RuntimeError("Mandatory parameter missing.")
    if not isinstance(in_value, str):
        raise RuntimeError("must be string")
    return in_value.replace(in_parameters['remove'], in_parameters['insert'])


def date_parse(in_value: str, params: dict) -> str:
    """Transform text so that it is formatted in a way that LinkAhead can understand it.

Parameters
==========

- date_format: str, optional
    A format string using the ``datetime`` specificaton:
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    """
    fmt_default = "%Y-%m-%d"
    fmt = params.get("date_format", fmt_default)
    dt_str = datetime.datetime.strptime(in_value, fmt).strftime(fmt_default)
    return dt_str


def datetime_parse(in_value: str, params: dict) -> str:
    """Transform text so that it is formatted in a way that LinkAhead can understand it.


Parameters
==========

- datetime_format: str, optional
    A format string using the ``datetime`` specificaton:
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    """
    fmt_default = "%Y-%m-%dT%H:%M:%S"
    fmt = params.get("datetime_format", fmt_default)
    dt_str = datetime.datetime.strptime(in_value, fmt).strftime(fmt_default)
    return dt_str


def cast_to_int(in_value: Any, params: dict) -> int:
    """
    Cast the `in_value` to int.

    Parameters
    ==========
    No parameters.
    """
    return int(in_value)


def cast_to_float(in_value: Any, params: dict) -> float:
    """
    Cast the `in_value` to float.

    Parameters
    ==========
    No parameters.
    """
    return float(in_value)


def cast_to_bool(in_value: Any, params: dict) -> bool:
    """
    Cast the `in_value` to bool.

    This is done by comparing `in_value` to "True".
    Only "true", "True", "False" and "false" are accepted as possible values.
    All other input values raise an error.

    Parameters
    ==========
    No parameters.
    """
    val = str(in_value).lower()
    if val == "true":
        return True
    if val == "false":
        return False
    raise ValueError("Invalid value for type cast to bool: {}".format(in_value))


def cast_to_str(in_value: Any, params: dict) -> str:
    """
    Cast the `in_value` to str.

    Parameters
    ==========
    No parameters.
    """
    return str(in_value)
