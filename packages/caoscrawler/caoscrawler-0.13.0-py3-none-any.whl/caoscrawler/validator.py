#!/usr/bin/env python3
# encoding: utf-8
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2024 Indiscale GmbH <info@indiscale.com>
# Copyright (C) 2024 Alexander Schlemmer
#
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
#
# ** end header
#

"""
This module contains functions to validate the output of a scanner run with a
json schema.
"""

import jsonschema
import linkahead as db
# from caosadvancedtools.models.parser import parse_model_from_string
from caosadvancedtools.json_schema_exporter import recordtype_to_json_schema
from caosadvancedtools.models.parser import parse_model_from_yaml
from jsonschema import ValidationError
from linkahead.high_level_api import convert_to_python_object


def load_json_schema_from_datamodel_yaml(filename: str) -> dict[str, dict]:
    """
    Load a data model yaml file (using caosadvancedtools) and convert
    all record types into a json schema using the json_schema_exporter module.

    Arguments
    ---------
    filename: str
        The filename of the yaml file to load.

    Returns
    -------
    A dict of json schema objects. The keys are the record types for which the schemas
    are generated.
    """

    model = parse_model_from_yaml(filename)

    rt_schemas = {}
    for el_key, el in model.items():
        if isinstance(el, db.RecordType):
            rt_schemas[el_key] = recordtype_to_json_schema(el)

    return rt_schemas


def representer_ordereddict(dumper, data):
    """
    Helper function to be able to represent the converted json schema objects correctly as yaml.
    This representer essentially replaced OrderedDict objects with simple dict objects.

    Since Python 3.7 dicts are ordered by default, see e.g.:
    https://softwaremaniacs.org/blog/2020/02/05/dicts-ordered/en/

    Example how to use the representer:
    ```python
    yaml.add_representer(OrderedDict, caoscrawler.validator.representer_ordereddict)
    ```
    """
    return dumper.represent_data(dict(data))


def _apply_schema_patches(pobj: dict):
    """
    Changes applied:
    - properties are moved vom subitem "proeprties" to top-level.
    - The following keys are deleted: parents, role, name, description, metadata, properties
    """
    if "properties" not in pobj:
        # this is probably a file
        return pobj
    for prop in pobj["properties"]:
        if isinstance(pobj["properties"][prop], dict):
            pobj[prop] = _apply_schema_patches(pobj["properties"][prop])
        else:
            pobj[prop] = pobj["properties"][prop]

    for keyd in ("parents", "role", "name",
                 "description", "metadata", "properties"):
        if keyd in pobj:
            del pobj[keyd]

    return pobj


def convert_record(record: db.Record):
    """
    Convert a record into a form suitable for validation with jsonschema.

    Uses `high_level_api.convert_to_python_object`
    Afterwards `_apply_schema_patches` is called recursively to refactor the dictionary
    to match the current form of the jsonschema.

    Arguments:
    ----------
    record: db.Record
      The record that is supposed to be converted.
    """
    pobj = convert_to_python_object(record).serialize()
    return _apply_schema_patches(pobj)


def validate(records: list[db.Record], schemas: dict[str, dict]) -> list[tuple]:
    """
    Validate a list of records against a dictionary of schemas.
    The keys of the dictionary are record types and the corresponding values are json schemata
    associated with that record type. The current implementation assumes that each record that is
    checked has exactly one parent and raises an error if that is not the case.
    The schema belonging to a record is identified using the name of the first (and only) parent
    of the record.

    Arguments:
    ----------

    records: list[db.Record]
      List of records that will be validated.

    schemas: dict[str, dict]
      A dictionary of JSON schemas generated using `load_json_schema_from_datamodel_yaml`.

    Returns:
    --------
    A list of tuples, one element for each record:

    - Index 0: A boolean that determines whether the schema belonging to the record type of the
               record matched.
    - Index 1: A validation error if the schema did not match or None otherwise.
    """

    retval = []
    for r in records:
        if len(r.parents) != 1:
            raise NotImplementedError(
                "Schema validation is only supported if records have exactly one parent.")
        parname = r.parents[0].name
        if parname not in schemas:
            raise RuntimeError(
                "No schema for record type {} in schema dictionary.".format(parname))
        try:
            jsonschema.validate(convert_record(r), schemas[parname])
            retval.append((True, None))
        except ValidationError as ex:
            retval.append((False, ex))
    return retval
