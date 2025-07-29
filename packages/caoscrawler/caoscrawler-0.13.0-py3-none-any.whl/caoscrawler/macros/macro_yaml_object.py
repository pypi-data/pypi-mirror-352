#!/usr/bin/env python3
# encoding: utf-8
#
# ** header v3.0
# This file is a part of the CaosDB Project.
#
# Copyright (C) 2022 Alexander Schlemmer
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

# Function to expand a macro in yaml
# A. Schlemmer, 05/2022

import re
from copy import deepcopy
from dataclasses import dataclass
from string import Template
from typing import Any, Dict

_SAFE_SUBST_PAT = re.compile(r"^\$(?P<key>\w+)$")
_SAFE_SUBST_PAT_BRACES = re.compile(r"^\$\{(?P<key>\w+)}$")


@dataclass
class MacroDefinition:
    """
    Stores a macro definition.
    name: Name of the macro
    params: variables and default values to be substituted in keys or values
    definition: A dictionary that will be substituted including parameters
    """
    name: str
    params: Dict[str, Any]
    definition: Any


# This dictionary stores the macro definitions
macro_store: Dict[str, MacroDefinition] = dict()


def substitute(propvalue, values: dict):
    """
    Substitution of variables in strings using the variable substitution
    library from python's standard library.
    """
    # Simple matches are simply replaced by the raw dict entry.
    if match := (_SAFE_SUBST_PAT.fullmatch(propvalue)
                 or _SAFE_SUBST_PAT_BRACES.fullmatch(propvalue)):
        key = match.group("key")
        if key in values:
            return values[key]
    propvalue_template = Template(propvalue)
    return propvalue_template.safe_substitute(**values)


def substitute_dict(sourced: Dict[str, Any], values: Dict[str, Any]):
    """
    Create a copy of sourced.
    Afterwards recursively do variable substitution on all keys and values.
    """
    d = deepcopy(sourced)
    # Changes in keys:
    replace: Dict[str, str] = dict()
    for k in d:
        replacement = substitute(k, values)
        if replacement != k:
            replace[k] = replacement
    for k, v in replace.items():
        d[v] = d[k]
        del d[k]
    # Changes in values:
    for k, v in d.items():
        if isinstance(v, str):
            d[k] = substitute(v, values)
        elif isinstance(v, list):
            subst_list = list()
            for i in d[k]:
                if isinstance(i, str):
                    subst_list.append(substitute(i, values))
                elif isinstance(i, dict):
                    subst_list.append(substitute_dict(i, values))
                else:
                    subst_list.append(i)
            d[k] = subst_list
        elif isinstance(v, dict):
            d[k] = substitute_dict(v, values)
        else:
            pass
    return d


def defmacro_constructor(loader, node):
    """
    Function for registering macros in yaml files.

    It can be registered in pyaml using:
    yaml.SafeLoader.add_constructor("!defmacro", defmacro_constructor)
    """

    value = loader.construct_mapping(node, deep=True)
    params = {}
    if "params" in value:
        params = value["params"]
    macro = MacroDefinition(
        value["name"], params,
        value["definition"])
    macro_store[macro.name] = macro
    return {}


def macro_constructor(loader, node):
    """
    Function for substituting macros in yaml files.

    It can be registered in pyaml using:
    yaml.SafeLoader.add_constructor("!macro", macro_constructor)
    """
    res = dict()
    value = loader.construct_mapping(node, deep=True)
    for name, params_setter in value.items():
        if name in macro_store:
            # If params_setter is a list, run this for every element:
            if params_setter is not None and isinstance(params_setter, list):
                for el in params_setter:
                    macro = macro_store[name]
                    params = deepcopy(macro.params)
                    if el is not None:
                        if isinstance(el, dict):
                            params.update(el)
                        else:
                            raise RuntimeError("params type not supported")
                    else:
                        raise RuntimeError("params type must not be None")
                    params = substitute_dict(params, params)
                    definition = substitute_dict(macro.definition, params)
                    res.update(definition)
            else:
                # This is just a single macro:
                macro = macro_store[name]
                params = deepcopy(macro.params)
                if params_setter is not None:
                    if isinstance(params_setter, dict):
                        params.update(params_setter)
                    else:
                        raise RuntimeError("params type not supported")
                params = substitute_dict(params, params)
                definition = substitute_dict(macro.definition, params)
                res.update(definition)
        else:
            # If there is no macro with that name, just keep that node:
            res[name] = params_setter

    return res
