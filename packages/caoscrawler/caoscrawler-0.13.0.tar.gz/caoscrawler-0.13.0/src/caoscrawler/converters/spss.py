# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2024 IndiScale GmbH <info@indiscale.com>
# Copyright (C) 2024 Daniel Hornung <d.hornung@indiscale.com>
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

"""Converter for SAV files (stored by SPSS)."""

from __future__ import annotations  # Can be removed with 3.10.

import argparse
from collections import OrderedDict
from typing import Any, Optional

import numpy as np
import pandas as pd
import pyreadstat
import yaml

from ..stores import GeneralStore
from ..structure_elements import File, StructureElement
from . import converters

READSTAT_TYPES = {
    "double": "DOUBLE",
    "string": "TEXT",
}
ORIGINAL_TYPES = {
    "EDATE8": "DATETIME",
}


class SPSSConverter(converters.TableConverter):
    """Converter for SAV files (stored by SPSS)."""

    def create_children(self, values: GeneralStore, element: StructureElement) -> list:
        assert isinstance(element, File)
        # The default dtype backend "numpy_nullable" does not handle dates well.
        # Note that pandas.ArrowDtype is considered experimental (in Pandas 2.2).
        df = pd.io.spss.read_spss(element.path, dtype_backend="pyarrow")
        dtypes = read_column_types(element.path)

        # Fix datetime columns
        for name, dtype in dtypes.items():
            if dtype != "DATETIME":
                continue
            col = df.loc[:, name]
            col.fillna(np.nan, inplace=True)
            col.replace([np.nan], [None], inplace=True)

        return self._children_from_dataframe(df)


def read_column_types(savfile: Optional[str] = None, meta: Optional[Any] = None) -> dict[str, str]:
    """Read SAV file and return the column types.

Optionally, take data from a previours reading.

Parameters
----------
savfile : Optional[str]
    The SAV file to read.

meta : Optional
    The meta data result from `pyreadstat.read_sav(...)`.

Returns
-------
out : dict[str, str]
    The column names and types.
    """
    if not meta:
        _, meta = pyreadstat.read_sav(savfile, metadataonly=True)
    elif savfile is not None:
        raise ValueError("Only one of `savfile` and `meta` must be given.")
    dtypes: dict[str, str] = {}
    for name in meta.column_names:
        datatype = ORIGINAL_TYPES.get(meta.original_variable_types[name],
                                      READSTAT_TYPES[meta.readstat_variable_types[name]])
        dtypes[name] = datatype
    return dtypes


def spss_to_yaml(savfile: str, yamlfile: str, cfood: Optional[str] = None) -> None:
    """Parse the *.sav and create basic datamodel in ``yamlfile``.

Parameters
----------
cfood: str
  If given, also create a cfood skeleton.
    """
    _, meta = pyreadstat.read_sav(savfile, metadataonly=True)
    dtypes = read_column_types(meta=meta)

    cfood_str = """
---
metadata:
  macros:
  - !defmacro
    # Simple column value -> property rule
    name: ColumnValue
    params:
      name: null
      belongsto: BaseElement
      type: TextElement
    definition:
      ${name}:
        type: ${type}
        match_name: ^${name}$$
        match_value: (?P<val>.*)
        records:
          ${belongsto}:
            ${name}: $$val
  - !defmacro
    # column value -> reference property
    name: ColumnValueReference
    params:
      name: null
      reftype: null  # RecordType of the reference
      belongsto: BaseElement
      type: TextElement  # References are always text, right?
    definition:
      ${name}:
        type: ${type}
        match_name: ^${name}$$
        match_value: (?P<val>.*)
        records:
          ${reftype}:
            name: $$val
          ${belongsto}:
            ${name}: $$${reftype}
  - !defmacro
    # Same as "ColumnValue", but also give name of property.
    name: ColumnValuePropname
    params:
      name: null
      propname: null
      belongsto: BaseElement
      type: TextElement
    definition:
      ${name}:
        type: ${type}
        match_name: ^${name}$$
        match_value: (?P<val>.*)
        records:
          ${belongsto}:
            ${propname}: $$val
---
directory: # corresponds to the directory given to the crawler
  type: Directory
  match: .* # we do not care how it is named here
  subtree:
    # This is the file
    thisfile:
      type: SPSSFile
      match: ".*sav"
      subtree:
        entry:
          type: Dict
          match: .* # Name is irrelevant
          records:
            MyParent:
          subtree: !macro
"""

    enums: dict[str, list[str]] = {}
    properties = OrderedDict()

    for name in meta.column_names:
        prop = {
            "datatype": dtypes[name],
        }
        desc = meta.column_names_to_labels.get(name)
        if desc and desc != name:
            prop["description"] = desc
        # Handle categorial variables
        if var_label := meta.variable_to_label.get(name):
            vvl = meta.variable_value_labels[name]
            # reproducible (and sensible) order
            label_values = [vvl[key] for key in sorted(vvl.keys())]
            if label_values not in enums.values():
                enums[var_label] = label_values
            else:
                var_label = [key for key, value in enums.items() if value == label_values][0]
            prop["datatype"] = var_label
        properties[name] = prop

    output = f"""# auto-generated data model from file "{savfile}".
# To insert a datamodel into LinkAhead, run:
#
# python3 -m caosadvancedtools.models.parser datamodel.yaml --sync

"""

    # Actual datamodel
    output += """
#########
# Enums #
#########

"""
    for name, values in enums.items():
        output += f"""{name}:
  description:
  # possible values: {values}\n"""

    output += ("""
###############
# RecordTypes #
###############

DummyRT:
  description: Note: Change name and enter description.
  recommended_properties:
    """
               + "    ".join(yaml.dump(dict(properties),  # from OrderedDict to dict
                                       allow_unicode=True,
                                       sort_keys=False).splitlines(keepends=True)))

    # Experimental: Enum creation
    output += """
###############
# Enum values #
###############
"""
    for name, values in enums.items():
        output += f"\n# ### {name} ###\n"
        for value in values:
            output += f"""
{value}:
  role: Record
  inherit_from_suggested:
    - {name}
"""

    with open(yamlfile, encoding="utf-8", mode="w") as myfile:
        myfile.write(output)

    if cfood:
        defs_col_value: list[str] = []
        defs_col_value_ref: list[str] = []
        prefix = " " * 14
        for name, propdef in properties.items():
            def_str = prefix + f"- name: {name}\n"
            dtype = None
            reftype = None
            defs = defs_col_value
            # Which type?
            if propdef["datatype"] == "DOUBLE":
                dtype = "FloatElement"
            elif propdef["datatype"] in ("TEXT", "DATETIME"):
                dtype = None
            else:
                reftype = propdef["datatype"]
                defs = defs_col_value_ref

            # Append according to types:
            if reftype:
                def_str += prefix + f"  reftype: {reftype}\n"
            if dtype:
                def_str += prefix + f"  type: {dtype}\n"

            # Store result
            defs.append(def_str)
            del defs

        cfood_str += (prefix[2:] + "ColumnValue:\n" + "".join(defs_col_value)
                      + prefix[2:] + "ColumnValueReference:\n" + "".join(defs_col_value_ref)
                      )
        with open(cfood, encoding="utf-8", mode="w") as myfile:
            myfile.write(cfood_str)


def _parse_arguments():
    """Parse the arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--input', help="The *.sav file.", required=True)
    parser.add_argument('-o', '--outfile', help="Yaml filename to save the result", required=True)
    parser.add_argument('--cfood', help="Yaml filename to create cfood output in", required=False)

    return parser.parse_args()


def spss_to_datamodel_main():
    """The main function of this script."""
    args = _parse_arguments()
    spss_to_yaml(savfile=args.input, yamlfile=args.outfile, cfood=args.cfood)
    print(f"Written datamodel to: {args.outfile}")
    if args.cfood:
        print(f"Written cfood to: {args.cfood}")
