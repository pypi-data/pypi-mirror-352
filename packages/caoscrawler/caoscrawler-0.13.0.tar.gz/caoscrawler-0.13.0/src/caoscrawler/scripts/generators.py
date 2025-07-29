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

"""Scripts and functions to generate datamodel yaml files and cfood skeletons.

For example from actual data files.
"""

import argparse
import csv
from collections import OrderedDict
from string import Template
from typing import Optional

import pandas as pd
import yaml

DM_TEMPLATE = """# auto-generated data model from file "[]{infile}".
# To insert a datamodel into LinkAhead, run:
#
# python3 -m caosadvancedtools.models.parser datamodel.yaml --sync
"""

HEADER_RT = """
###############
# RecordTypes #
###############

DummyRT:
  description: Note: Change name and enter description.
  recommended_properties:
    """

CFOOD_TEMPLATE = """
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
  records:
    DirRecord:    # One record for each directory.
  subtree:
    # This is the file
    thisfile:
      type: []{file}
      match: []{match}
      records:
        DatFileRecord:    # One record for each matching file
          role: File
          path: $thisfile
          file: $thisfile
      subtree:
        entry:
          type: Dict
          match: .* # Name is irrelevant
          records:
            BaseElement:    # One BaseElement record for each row in the CSV/TSV file
              DatFileRecord: $DatFileRecord
            DirRecord:
              BaseElement: +$BaseElement
          subtree: !macro
"""


class _CustomTemplate(Template):
    delimiter = "[]"  # "$" is used too much by the yaml template.


def csv_to_datamodel(infile: str, outfile: str, cfood: Optional[str] = None):
    """Parse the input csv and create basic datamodel in ``outfile``.

Parameters
----------
cfood: str
  If given, also create a cfood skeleton.
    """
    sniffer = csv.Sniffer()
    with open(infile, encoding="utf-8") as f_infile:
        max_sniff = 50000
        sniffed = sniffer.sniff(f_infile.read(max_sniff))
    df = pd.read_table(infile, sep=sniffed.delimiter, quotechar=sniffed.quotechar,
                       escapechar=sniffed.escapechar)

    properties = OrderedDict()
    for colname in df.columns:
        column = df[colname]
        dtype: Optional[str] = "TEXT"
        if pd.api.types.is_bool_dtype(column.dtype):
            dtype = "BOOLEAN"
        if pd.api.types.is_float_dtype(column.dtype):
            dtype = "DOUBLE"
        elif pd.api.types.is_integer_dtype(column.dtype):
            dtype = "INTEGER"
        properties[colname] = {
            "datatype": dtype
        }

    result = (_CustomTemplate(DM_TEMPLATE).substitute({"infile": infile})
              + HEADER_RT
              + "    ".join(yaml.dump(dict(properties),  # from OrderedDict to dict
                                      allow_unicode=True,
                                      sort_keys=False).splitlines(keepends=True))
              )
    with open(outfile, encoding="utf-8", mode="w") as myfile:
        myfile.write(result)

    #################
    # cfood section #
    #################
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
            if propdef["datatype"] == "BOOLEAN":
                dtype = "BooleanElement"
            elif propdef["datatype"] == "INTEGER":
                dtype = "IntegerElement"
            elif propdef["datatype"] == "DOUBLE":
                dtype = "FloatElement"
            elif propdef["datatype"] == "TEXT":
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

        sep = repr(sniffed.delimiter)
        sep = f'"{sep[1:-1]}"'
        match_str = f"""'.*[ct]sv'
      sep: {sep}
      # "header": [int]
      # "names": [str]
      # "index_col": [int]
      # "usecols": [int]
      # "true_values": [str]
      # "false_values": [str]
      # "na_values": [str]
      # "skiprows": [int]
      # "nrows": [int]
      # "keep_default_na": [bool]
        """

        cfood_str = (_CustomTemplate(CFOOD_TEMPLATE).substitute({"file": "CSVTableConverter",
                                                                 "match": match_str})
                     + prefix[2:] + "ColumnValue:\n" + "".join(defs_col_value)
                     + prefix[2:] + "ColumnValueReference:\n" + "".join(defs_col_value_ref)
                     )
        with open(cfood, encoding="utf-8", mode="w") as myfile:
            myfile.write(cfood_str)


def _parse_args_csv():
    """Parse the arguments."""
    parser = argparse.ArgumentParser(description="Create datamodel and cfood from CSV files.")
    parser.add_argument('-i', '--input', help="The input file.", required=True, dest="infile")
    parser.add_argument('-o', '--outfile', help="Yaml filename to save the result", required=True)
    parser.add_argument('--cfood', help="Yaml filename to create cfood output in", required=False)

    return parser.parse_args()


def csv_to_datamodel_main():
    """The main function for csv data handling."""
    args = _parse_args_csv()
    csv_to_datamodel(**vars(args))
