# encoding: utf-8
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2024 Indiscale GmbH <info@indiscale.com>
# Copyright (C) 2021 Henrik tom Wörden
# Copyright (C) 2021 Alexander Schlemmer
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

"""Converters take structure elements and create Records and new structure elements from them."""

from __future__ import annotations

import datetime
import json
import logging
from datetime import date
import os
import re
import warnings
from abc import ABCMeta, abstractmethod
from inspect import signature
from string import Template
from typing import Any, Callable, Optional, Union
from caosadvancedtools.table_importer import XLSImporter
import linkahead as db
import pandas as pd
import yaml
import yaml_header_tools
from jsonschema import ValidationError, validate

from ..stores import GeneralStore, RecordStore
from ..structure_elements import (BooleanElement, DictElement, Directory, File,
                                  FloatElement, IntegerElement, JSONFile,
                                  ListElement, NoneElement, StructureElement,
                                  TextElement)
from ..utils import has_parent

# These are special properties which are (currently) treated differently
# by the converters:
SPECIAL_PROPERTIES = ("description", "name", "id", "path",
                      "file", "checksum", "size")
ID_PATTERN = r"\D[.\w]*"
SINGLE_VAR_RE = re.compile(r"^\$(\{)?(?P<varname>" + ID_PATTERN + r")(\})?$")
logger = logging.getLogger(__name__)


class CrawlerTemplate(Template):
    # This also adds a dot to the default pattern.
    # See: https://docs.python.org/3/library/string.html#template-strings
    # Default flags is re.IGNORECASE
    braceidpattern = ID_PATTERN


def _only_max(children_with_keys):

    return [max(children_with_keys, key=lambda x: x[1])[0]]


def _only_min(children_with_keys):

    return [min(children_with_keys, key=lambda x: x[1])[0]]


# names of functions that can be used to filter children
FILTER_FUNCTIONS = {
    "only_max": _only_max,
    "only_min": _only_min,
}


def str_to_bool(x):
    if str(x).lower() == "true":
        return True
    elif str(x).lower() == "false":
        return False
    else:
        raise RuntimeError("Should be 'true' or 'false'.")

# TODO: Comment on types and inheritance
# Currently, we often check the type of StructureElements, because serveral converters assume that
# they are called only with the appropriate class.
# Raising an Error if the type is not sufficient (e.g. TextElement instead of DictElement) means
# that the generic parent class StructureElement is actually NOT a valid type for the argument and
# type hints should reflect this.
# However, we should not narrow down the type of the arguments compared to the function definitions
# in the parent Converter class. See
# - https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
# - https://stackoverflow.com/questions/56860/what-is-an-example-of-the-liskov-substitution-principle
# - https://blog.daftcode.pl/covariance-contravariance-and-invariance-the-ultimate-python-guide-8fabc0c24278
# Thus, the problem lies in the following design:
# Converter instances are supposed to be used by the Crawler in a generic way (The crawler calls
# `match` and `typecheck` etc) but the functions are not supposed to be called with generic
# StructureElements. One direction out of this would be a refactoring that makes the crawler class
# expose a generic function like `treat_element`, which can be called with any StructureElement and
# the Converter decides what to do (e.g. do nothing if the type is one that it does not care
# about).
# https://gitlab.indiscale.com/caosdb/src/caosdb-crawler/-/issues/64


class ConverterValidationError(Exception):

    """To be raised if contents of an element to be converted are invalid."""

    def __init__(self, msg):
        self.message = msg


def create_path_value(func):
    """Decorator for create_values functions that adds a value containing the path.

    should be used for StructureElement that are associated with file system objects that have a
    path, like File or Directory.

    """

    def inner(self, values: GeneralStore, element: StructureElement):
        func(self, values=values, element=element)
        values.update({self.name + ".path": element.path})
    return inner


def replace_variables(propvalue: Any, values: GeneralStore):
    """
    This function replaces variables in property values (and possibly other locations,
    where the crawler can replace cfood-internal variables).

    If ``propvalue`` is a single variable name preceeded by a ``$`` (e.g. ``$var`` or ``${var}``),
    then the corresponding value stored in ``values`` is returned.
    In any other case the variable substitution is carried out as defined by string templates
    and a new string with the replaced variables is returned.
    """
    # We only replace string variable names. If it is not a string the value stays unchanged
    if not isinstance(propvalue, str):
        return propvalue

    # Check if the replacement is a single variable containing a record:
    match = SINGLE_VAR_RE.match(propvalue)
    if match is not None:
        varname = match.group("varname")
        if varname in values:
            return values[varname]

    propvalue_template = CrawlerTemplate(propvalue)
    return propvalue_template.safe_substitute(**values.get_storage())


def handle_value(value: Union[dict, str, list], values: GeneralStore):
    """Determine whether the given value needs to set a property,
    be added to an existing value (create a list) or
    add as an additional property (multiproperty).

    Variable names (starting with a "$") are replaced by the corresponding value stored in the
    ``values`` GeneralStore.

Parameters
----------

value: Union[dict, str, list]
  - If *str*, the value to be interpreted. E.g. "4", "hello" or "$a"
    etc. No unit is set and collection mode is determined from the
    first character:
    - '+' corresponds to "list"
    - '*' corresponds to "multiproperty"
    - everything else is "single"
  - If *dict*, it must have a ``value`` key and may ``unit``, and
    ``collection_mode``. The returned tuple is directly created from
    the corresponding values if they are given; ``unit`` defaults to
    None and ``collection_mode`` is determined from ``value`` as
    explained for the str case above, i.e.,
    - if it starts with '+', collection mode is "list",
    - in case of '*', collection mode is "multiproperty",
    - and everything else is "single".
  - If *list*, each element is checked for variable replacement and the
    resulting list will be used as (list) value for the property

Returns
-------

out: tuple
  - the final value of the property; variable names contained in `values` are replaced.
  - the final unit of the property; variable names contained in `values` are replaced.
  - the collection mode (can be single, list or multiproperty)
    """
    # @review Florian Spreckelsen 2022-05-13

    propunit = None
    propvalue = None
    collection_mode = None
    if isinstance(value, dict):
        if "value" not in value:
            # TODO: how do we handle this case? Just ignore?
            #       or disallow?
            raise NotImplementedError(f"This definition has no \"value\": {value}")
        propvalue = value["value"]
        if "unit" in value:
            propunit = replace_variables(value["unit"], values)
        # can be "single", "list" or "multiproperty"
        if "collection_mode" in value:
            collection_mode = value["collection_mode"]
    else:
        propvalue = value
    if collection_mode is None:
        if isinstance(propvalue, str):
            # Determine collection mode from string value
            collection_mode = "single"
            if propvalue.startswith("+"):
                collection_mode = "list"
                propvalue = propvalue[1:]
            elif propvalue.startswith("*"):
                collection_mode = "multiproperty"
                propvalue = propvalue[1:]
        elif isinstance(propvalue, list):
            # TODO: (for review)
            #       This is a bit dirty right now and needed for
            #       being able to directly set list values. Semantics is, however, a bit
            #       different from the two cases above.
            collection_mode = "single"

            # variables replacement:
            returnvalue = list()
            for element in propvalue:
                # Do the element-wise replacement only, when its type is string:
                if isinstance(element, str):
                    returnvalue.append(replace_variables(element, values))
                else:
                    returnvalue.append(element)

            return (returnvalue, propunit, collection_mode)
        else:
            # value is another simple type
            collection_mode = "single"
            # Return it immediately, otherwise variable substitution would be done and fail:
            return (propvalue, propunit, collection_mode)

    propvalue = replace_variables(propvalue, values)
    return (propvalue, propunit, collection_mode)


def create_records(values: GeneralStore,
                   records: RecordStore,
                   def_records: dict) -> list[tuple[str, str]]:
    """
    Create records in GeneralStore `values` and RecordStore `records` as given
    by the definition in `def_records`.

    This function will be called during scanning using the cfood definition.
    It also should be used by CustomConverters to set records as automatic substitution
    and other crawler features are applied automatically.

    Parameters
    ----------
    values: GeneralStore
      This GeneralStore will be used to access variables that are needed during variable substitution
      in setting the properties of records and files.
      Furthermore, the records that are generated in this function will be stored in this GeneralStore
      **additionally to** storing them in the RecordStore given as the second argument to this function.

    records: RecordStore
      The RecordStore where the generated records will be stored.

    Returns
    -------
    : list[tuple[str, str]]
      A list of tuples containing the record names (1st element of tuple) and respective property names
      as 2nd element of the tuples. This list will be used by the scanner for creating the debug tree.

    """
    keys_modified = []

    for name, record in def_records.items():
        # If only a name was given (Like this:
        # Experiment:
        # ) set record to an empty dict / empty configuration
        if record is None:
            record = {}

        role = "Record"
        # This allows us to create e.g. Files
        if "role" in record:
            role = record["role"]

        # whether the record already exists in the store or not are actually really
        # different distinct cases for treating the setting and updating of variables:
        if name not in records:
            if role == "Record":
                c_record = db.Record()
            elif role == "File":
                c_record = db.File()
            else:
                raise RuntimeError("Role {} not supported.".format(role))
            # add the new record to the record store:
            records[name] = c_record
            # additionally add the new record to the general store:
            values[name] = c_record

            # add the "fallback" parent only for Records, not for Files:
            if (role == "Record" and "parents" not in record):
                c_record.add_parent(name)

        if isinstance(record, str):
            raise RuntimeError(
                "dict expected, but found str: {}".format(record))

    # We do a second run over the def_records, here. Having finished the first run
    # for creating the records (in the variable and records stores) makes sure that
    # records, that are defined on this level can already be accessed during variable substitution
    # in the properties that will be set in the next block.
    for name, record in def_records.items():
        # See above:
        if record is None:
            record = {}

        c_record = records[name]

        # Set the properties:
        for key, value in record.items():
            if key == "parents" or key == "role":
                continue

            # Allow replacing variables in keys / names of properties:
            key_template = CrawlerTemplate(key)
            key = key_template.safe_substitute(**values.get_storage())

            keys_modified.append((name, key))
            propvalue, propunit, collection_mode = handle_value(value, values)

            if key.lower() in SPECIAL_PROPERTIES:
                # e.g. description, name, etc.
                # list mode does not work for them
                if key.lower() == "path" and not propvalue.startswith(os.path.sep):
                    propvalue = os.path.sep + propvalue

                    # Convert relative to absolute paths:
                    propvalue = os.path.normpath(propvalue)
                setattr(c_record, key.lower(), propvalue)
            else:
                if c_record.get_property(key) is None:
                    if collection_mode == "list":
                        c_record.add_property(name=key, value=[propvalue], unit=propunit)
                    elif (collection_mode == "multiproperty" or
                          collection_mode == "single"):
                        c_record.add_property(name=key, value=propvalue, unit=propunit)
                else:
                    if collection_mode == "list":
                        if (propunit and c_record.get_property(key).unit
                                and propunit != c_record.get_property(key).unit):
                            raise RuntimeError(
                                f"Property '{key}' has contradictory units: "
                                f"{propunit} and {c_record.get_property(key).unit}"
                            )
                        c_record.get_property(key).value.append(propvalue)
                        if propunit and not c_record.get_property(key).unit:
                            c_record.get_property(key).unit = propunit
                    elif collection_mode == "multiproperty":
                        c_record.add_property(name=key, value=propvalue, unit=propunit)
                    elif collection_mode == "single":
                        c_record.get_property(key).value = propvalue
                        if propunit:
                            c_record.get_property(key).unit = propunit

        # no matter whether the record existed in the record store or not,
        # parents will be added when they aren't present in the record yet:
        if "parents" in record:
            c_record.parents.clear()
            for parent in record["parents"]:
                # Do the variables replacement:
                var_replaced_parent = replace_variables(parent, values)
                if not has_parent(c_record, var_replaced_parent):
                    c_record.add_parent(var_replaced_parent)
    return keys_modified


class Converter(object, metaclass=ABCMeta):
    """Converters treat StructureElements contained in the hierarchical sturcture.

    This is the abstract super class for all Converters.
    """

    def __init__(self, definition: dict, name: str, converter_registry: dict):
        """

        Parameters
        ----------
        definition: dict
          Please refer to ``src/doc/converters.rst`` to learn about the structure that the
          definition dict must have.
        converter_registry: dict
          A dictionary that contains converter names as keys and dicts as values. Those value dicts
          have the keys 'converter', 'package' and 'class'.  'converter' is the class name,
          'package' the module and 'class' the class instance of converters.
        """

        self.definition = definition
        self.name = name

        # Used to store usage information for debugging:
        self.metadata: dict[str, set[str]] = {
            "usage": set()
        }

        self.converters = []
        if "transform" in self.definition:
            if not isinstance(self.definition["transform"], dict):
                raise RuntimeError("The value corresponding to the 'transform' key in the "
                                   "converter definition must be a dict")
            for transformer_key, transformer in self.definition["transform"].items():
                if "in" not in transformer:
                    raise RuntimeError("In-variable not defined!")
                if "out" not in transformer:
                    raise RuntimeError("Out-variable not defined!")
                if "functions" not in transformer:
                    raise RuntimeError("No functions given for transformer!")
                if not isinstance(transformer["functions"], list):
                    raise RuntimeError("The value corresponding to the 'functions' key in the "
                                       "transform section must be a list")

                if not isinstance(transformer["in"], str):
                    raise RuntimeError("You should provide the variable name as string")

        if "subtree" in definition:
            for converter_name in definition['subtree']:
                converter_definition = definition["subtree"][converter_name]
                self.converters.append(Converter.converter_factory(
                    converter_definition, converter_name, converter_registry))

        self.setup()

    def setup(self):
        """
        Analogous to `cleanup`. Can be used to set up variables that are permanently
        stored in this converter.
        """
        pass

    @staticmethod
    def converter_factory(definition: dict, name: str, converter_registry: dict):
        """Create a Converter instance of the appropriate class.

        The `type` key in the `definition` defines the Converter class which is being used.
        """

        if definition is None:
            raise RuntimeError("Definition of converter \"{}\" is "
                               "empty".format(name))

        if "type" not in definition:
            raise RuntimeError(
                "Type is mandatory for converter entries in CFood definition.")

        if definition["type"] not in converter_registry:
            raise RuntimeError("Unknown Type: {}".format(definition["type"]))

        if "class" not in converter_registry[definition["type"]]:
            raise RuntimeError("Converter class not loaded correctly.")

        # instatiates an object of the required class, e.g. DirectoryConverter(definition, name)
        converter = converter_registry[definition["type"]]["class"](definition, name,
                                                                    converter_registry)

        return converter

    def create_values(self, values: GeneralStore, element: StructureElement):
        """
        Extract information from the structure element and store them as values in the
        general store.

        Parameters
        ----------

        values: GeneralStore
            The GeneralStore to store values in.

        element: StructureElement
            The StructureElement to extract values from.
        """
        m = self.match(element)
        if m is None:
            # this should never happen as the condition was checked before already
            raise RuntimeError("Condition does not match.")
        values.update(m)

    def match_properties(self, properties: dict, vardict: dict, label: str = "match_properties"):
        """This method can be used to generically match 'match_properties' from the cfood definition
        with the behavior described as follows:

        'match_properties' is a dictionary of key-regexps and value-regexp pairs. Each key matches
        a property name and the corresponding value matches its property value.

        What a property means in the context of the respective converter can be different, examples:

        * XMLTag: attributes of the node
        * ROCrate: properties of the ROCrateEntity
        * DictElement: properties of the dict

        label can be used to customize the name of the dictionary in the definition.

        This method is not called by default, but can be called from child classes.

        Typically it would be used like this from methods overwriting `match`::

            if not self.match_properties(<properties>, vardict):
                return None

        vardict will be updated in place when there are
        matches. <properties> is a dictionary taken from the structure
        element that contains the properties in the context of this
        converter.


        Parameters
        ----------

        properties: dict
            The dictionary containing the properties to be matched.

        vardict: dict
            This dictionary will be used to store the variables created during the matching.

        label: str
            Default "match_properties". Can be used to change the name
            of the property in the definition. E.g. the xml converter
            uses "match_attrib" which makes more sense in the context
            of xml trees.

        Returns
        -------

        : bool
            Returns True when properties match and False
            otherwise. The vardict dictionary is updated in place.

        """
        if label in self.definition:
            # This matcher works analogously to the attributes matcher in the XMLConverter
            for prop_def_key, prop_def_value in self.definition[label].items():
                match_counter = 0
                matched_m_prop = None
                matched_m_prop_value = None
                for prop_key, prop_value in properties.items():
                    # print("{} = {}".format(prop_key, prop_value))
                    # TODO: automatic conversion to str ok?
                    m_prop = re.match(prop_def_key, str(prop_key))
                    if m_prop is not None:
                        match_counter += 1
                        matched_m_prop = m_prop
                        # TODO: automatic conversion to str ok?
                        m_prop_value = re.match(prop_def_value, str(prop_value))
                        if m_prop_value is None:
                            return False
                        matched_m_prop_value = m_prop_value
                # TODO: How to deal with multiple matches?
                #       There are multiple options:
                #       - Allow multiple attribute-key matches: Leads to possible overwrites of variables
                #       - Require unique attribute-key and attribute-value matches: Very complex
                #       - Only allow one single attribute-key to match and run attribute-value match separately.
                #       Currently the latter option is implemented.
                # TODO: The ROCrateEntityConverter implements a very similar behavior.
                if match_counter == 0:
                    return False
                elif match_counter > 1:
                    raise RuntimeError("Multiple properties match the same {} entry.".format(label))
                vardict.update(matched_m_prop.groupdict())
                vardict.update(matched_m_prop_value.groupdict())
        return True

    def apply_transformers(self, values: GeneralStore, transformer_functions: dict):
        """
        Check if transformers are defined using the "transform" keyword.
        Then apply the transformers to the variables defined in GeneralStore "values".

        Parameters
        ----------

        values: GeneralStore
            The GeneralStore to store values in.

        transformer_functions: dict
            A dictionary of registered functions that can be used within this transformer block.
            The keys of the dict are the function keys and the values the callable functions of the
            form:

            def func(in_value: Any, in_parameters: dict) -> Any:
                pass
        """

        if "transform" not in self.definition:
            return
        for transformer_key, transformer in self.definition["transform"].items():
            in_value = replace_variables(transformer["in"], values)
            out_value = in_value

            for tr_func_el in transformer["functions"]:
                if not isinstance(tr_func_el, dict):
                    raise RuntimeError("Elements of the list of the functions key "
                                       "must be dictonaries!")
                if len(tr_func_el) != 1:
                    raise RuntimeError("List element dictionaries must have exactly"
                                       " one element with they key being the name"
                                       " of the function!")
                tr_func_key = list(tr_func_el.keys())[0]

                if tr_func_key not in transformer_functions:
                    raise RuntimeError("Unknown transformer function: {}".format(tr_func_key))

                # Do variable replacment on function parameters:
                if tr_func_el[tr_func_key] is not None:
                    # Create a copy of the function parameters:
                    tr_func_params = dict(tr_func_el[tr_func_key])
                    for key in tr_func_params:
                        tr_func_params[key] = replace_variables(tr_func_params[key], values)
                else:
                    tr_func_params = None

                # Retrieve the function from the dictionary:
                tr_func = transformer_functions[tr_func_key]
                # Call the function:
                sig = signature(tr_func)
                if len(sig.parameters) == 1 and len(tr_func_params) == 0:
                    out_value = tr_func(in_value)
                else:
                    out_value = tr_func(in_value, tr_func_params)
                # The next in_value is the current out_value:
                in_value = out_value
            # If everything succeeded, store the final value in the general store:
            match = SINGLE_VAR_RE.match(transformer["out"])
            if match is None:
                raise RuntimeError("'out' of the transformer definition must specify a single"
                                   f" variable name. It was {transformer['out']}")
            values[match.group('varname')] = out_value

    @abstractmethod
    def create_children(self, values: GeneralStore, element: StructureElement):
        pass

    def create_records(self, values: GeneralStore, records: RecordStore,
                       element: StructureElement):
        # TODO why is element passed but not used???
        # ANSWER: because it might be used by overriding child classes.

        if "records" not in self.definition:
            return []

        # TODO please rename due to conflict
        return create_records(values,
                              records,
                              self.definition["records"])

    def filter_children(self, children_with_strings:
                        list[tuple[StructureElement, str]], expr: str,
                        group: str, rule: str):
        """Filter children according to regexp `expr` and `rule`."""

        if rule not in FILTER_FUNCTIONS:
            raise RuntimeError(
                f"{rule} is not a known filter rule. Only "
                f"{list(FILTER_FUNCTIONS.keys())} are implemented."
            )

        to_be_filtered = []
        unmatched_children = []

        for (child, name) in children_with_strings:

            m = re.match(expr, name)
            if m is None:
                unmatched_children.append(child)
            else:
                to_be_filtered.append((child, m.groupdict()[group]))

        filtered_children = FILTER_FUNCTIONS[rule](to_be_filtered)

        return filtered_children + unmatched_children

    @abstractmethod
    def typecheck(self, element: StructureElement):
        """
        Check whether the current structure element can be converted using
        this converter.
        """
        pass

    @staticmethod
    def _debug_matching_template(name: str, regexp: list[str], matched: list[str],
                                 result: Optional[dict]):
        """ Template for the debugging output for the match function """
        msg = "\n--------" + name + "-----------\n"
        for exp, ma in zip(regexp, matched):
            msg += "matching reg:\t" + exp + "\n"
            msg += "matching val:\t" + ma + "\n"
            msg += "---------\n"
        if result is None:
            msg += "No match\n"
        else:
            msg += "Matched groups:\n"
            msg += str(result)+'\n'
        msg += "----------------------------------------\n"
        logger.debug(msg)

    @staticmethod
    def debug_matching(kind=None):
        def debug_matching_decorator(func):
            """
            decorator for the match function of Converters that implements debug for the match of
            StructureElements
            """

            def inner(self, element: StructureElement):
                mr = func(self, element)
                if "debug_match" in self.definition and self.definition["debug_match"]:
                    if kind == "name" and "match" in self.definition:
                        self._debug_matching_template(name=self.__class__.__name__,
                                                      regexp=[self.definition["match"]],
                                                      matched=[element.name],
                                                      result=mr)
                    elif kind == "name_and_value":
                        self._debug_matching_template(
                            name=self.__class__.__name__,
                            regexp=[self.definition["match"]
                                    if "match" in self.definition else "",
                                    self.definition["match_name"]
                                    if "match_name" in self.definition else "",
                                    self.definition["match_value"]
                                    if "match_value" in self.definition else ""],
                            matched=[element.name, element.name, str(element.value)],
                            result=mr)
                    else:
                        self._debug_matching_template(name=self.__class__.__name__,
                                                      regexp=self.definition["match"]
                                                      if "match" in self.definition else "",
                                                      matched=str(element),
                                                      result=mr)
                return mr
            return inner
        return debug_matching_decorator

    @abstractmethod
    def match(self, element: StructureElement) -> Optional[dict]:
        """
        This method is used to implement detailed checks for matching compatibility
        of the current structure element with this converter.

        The return value is a dictionary providing possible matched variables from the
        structure elements information.
        """
        pass

    def cleanup(self):
        """
        This function is called when the converter runs out of scope and can be used to
        clean up objects that were needed in the converter or its children.
        """
        pass


class DirectoryConverter(Converter):
    """
    Converter that matches and handles structure elements of type directory.

    This is one typical starting point of a crawling procedure.
    """

    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        # TODO: See comment on types and inheritance
        if not isinstance(element, Directory):
            raise RuntimeError(
                "Directory converters can only create children from directories.")

        children = self.create_children_from_directory(element)

        if "filter" in self.definition:

            tuple_list = [(c, c.name) for c in children]

            return self.filter_children(tuple_list, **self.definition["filter"])

        return children

    @create_path_value
    def create_values(self, values: GeneralStore, element: StructureElement):
        super().create_values(values=values, element=element)

    def typecheck(self, element: StructureElement):
        return isinstance(element, Directory)

    # TODO basically all converters implement such a match function. Shouldn't this be the one
    # of the parent class and subclasses can overwrite if needed?
    @Converter.debug_matching("name")
    def match(self, element: StructureElement):
        # TODO: See comment on types and inheritance
        if not isinstance(element, Directory):
            raise RuntimeError("Element must be a directory.")
        m = re.match(self.definition["match"], element.name)
        if m is None:
            return None
        if "match_newer_than_file" in self.definition:
            last_modified = self._get_most_recent_change_in_dir(element)
            reference = self._get_reference_file_timestamp()
            if last_modified < reference:
                return None
        return m.groupdict()

    @staticmethod
    def create_children_from_directory(element: Directory):
        """
        Creates a list of files (of type File) and directories (of type Directory) for a
        given directory. No recursion.

        element: A directory (of type Directory) which will be traversed.
        """
        children: list[StructureElement] = []

        for name in sorted(os.listdir(element.path)):
            path = os.path.join(element.path, name)

            if os.path.isdir(path):
                children.append(Directory(name, path))
            elif os.path.isfile(path):
                children.append(File(name, path))

        return children

    @staticmethod
    def _get_most_recent_change_in_dir(element: Directory) -> datetime.datetime:
        """Return the datetime of the most recent change of any file
        or directory in the given Directory element.

        """
        most_recent = os.path.getmtime(element.path)

        for root, _, files in os.walk(element.path):
            mtimes = [os.path.getmtime(root)] + \
                [os.path.getmtime(os.path.join(root, fname)) for fname in files]
            if max(mtimes) > most_recent:
                most_recent = max(mtimes)

        return datetime.datetime.fromtimestamp(most_recent)

    def _get_reference_file_timestamp(self) -> datetime.datetime:
        """Return a time stamp read from a reference file if it
        exists. Otherwise return datetime.datetime.min, i.e., the
        earliest datetime known to datetime.

        """

        if "match_newer_than_file" not in self.definition:
            logger.debug("No reference file specified.")
            return datetime.datetime.min

        elif not os.path.isfile(self.definition["match_newer_than_file"]):
            logger.debug("Reference file doesn't exist.")
            return datetime.datetime.min

        with open(self.definition["match_newer_than_file"]) as ref_file:
            stamp_str = ref_file.readline().strip()
            try:
                return datetime.datetime.fromisoformat(stamp_str)
            except ValueError as e:
                logger.error(
                    f"Reference file in {self.definition['match_newer_than_file']} "
                    "doesn't contain a ISO formatted datetime in its first line. "
                    "Match regardless of modification times."
                )
                raise e


class SimpleFileConverter(Converter):
    """Just a file, ignore the contents."""

    def typecheck(self, element: StructureElement):
        return isinstance(element, File)

    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        return list()

    @create_path_value
    def create_values(self, values: GeneralStore, element: StructureElement):
        super().create_values(values=values, element=element)

    @Converter.debug_matching("name")
    def match(self, element: StructureElement):
        # TODO: See comment on types and inheritance
        if not isinstance(element, File):
            raise RuntimeError("Element must be a file.")
        m = re.match(self.definition["match"], element.name)
        if m is None:
            return None
        return m.groupdict()


class FileConverter(SimpleFileConverter):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning(
            "This class is deprecated. Please use SimpleFileConverter."))
        super().__init__(*args, **kwargs)


class MarkdownFileConverter(SimpleFileConverter):
    """Read the yaml header of markdown files (if a such a header exists)."""

    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        # TODO: See comment on types and inheritance
        if not isinstance(element, File):
            raise RuntimeError("A markdown file is needed to create children.")

        try:
            header = yaml_header_tools.get_header_from_file(
                element.path, clean=False)
        except yaml_header_tools.NoValidHeader:
            if generalStore is not None and self.name in generalStore:
                path = generalStore[self.name]
            else:
                path = "<path not set>"
            raise ConverterValidationError(
                "Error during the validation (yaml header cannot be read) of the markdown file "
                "located at the following node in the data structure:\n"
                f"{path}")
        except yaml_header_tools.ParseErrorsInHeader as err:
            if generalStore is not None and self.name in generalStore:
                path = generalStore[self.name]
            else:
                path = "<path not set>"
            raise ConverterValidationError(
                "Error during the validation (yaml header cannot be read) of the markdown file "
                "located at the following node in the data structure:\n"
                "{}\nError:\n{}".format(path, err))
        children: list[StructureElement] = []

        for name, entry in header.items():
            if isinstance(entry, list):
                children.append(ListElement(name, entry))
            elif isinstance(entry, str):
                children.append(TextElement(name, entry))
            else:
                if generalStore is not None and self.name in generalStore:
                    path = generalStore[self.name]
                else:
                    path = "<path not set>"
                raise RuntimeError(
                    "Header entry {} has incompatible type.\nFilename: {}".format(name, path))
        return children


def convert_basic_element(element: Union[list, dict, bool, int, float, str, None], name=None,
                          msg_prefix=""):
    """Convert basic Python objects to the corresponding StructureElements"""
    if isinstance(element, StructureElement):
        return element
    elif isinstance(element, list):
        return ListElement(name, element)
    elif isinstance(element, dict):
        return DictElement(name, element)
    elif isinstance(element, bool):
        return BooleanElement(name, element)
    elif isinstance(element, int):
        return IntegerElement(name, element)
    elif isinstance(element, float):
        return FloatElement(name, element)
    elif isinstance(element, str):
        return TextElement(name, element)
    elif element is None:
        return NoneElement(name)
    elif isinstance(element, datetime.date):
        return TextElement(name, str(element))
    else:
        raise NotImplementedError(
            msg_prefix + f"The object that has an unexpected type: {type(element)}\n"
            f"The object is:\n{str(element)}")


def validate_against_json_schema(instance, schema_resource: Union[dict, str]):
    """Validate given ``instance`` against given ``schema_resource``.

Parameters
----------

instance:
  Instance to be validated, typically ``dict`` but can be ``list``, ``str``, etc.

schema_resource:
  Either a path to the JSON file containing the schema or a  ``dict`` with the schema.
    """
    if isinstance(schema_resource, dict):
        schema = schema_resource
    elif isinstance(schema_resource, str):
        with open(schema_resource, 'r') as json_file:
            schema = json.load(json_file)
    else:
        raise ValueError("The value of 'validate' has to be a string describing the path "
                         "to the json schema file (relative to the cfood yml)  "
                         "or a dict containing the schema.")
    # validate instance (e.g. JSON content) against schema
    try:
        validate(instance=instance, schema=schema)
    except ValidationError as err:
        raise ConverterValidationError(
            f"\nCouldn't validate {instance}:\n{err.message}")


class DictElementConverter(Converter):
    """
**Operates on:** :py:class:`caoscrawler.structure_elements.DictElement`

**Generates:** :py:class:`caoscrawler.structure_elements.StructureElement`
    """

    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        # TODO: See comment on types and inheritance
        if not isinstance(element, DictElement):
            raise ValueError("create_children was called with wrong type of StructureElement")

        try:
            return self._create_children_from_dict(element.value)
        except ConverterValidationError as err:
            path = generalStore[self.name]
            raise ConverterValidationError(
                "Error during the validation of the dictionary located at the following node "
                "in the data structure:\n"
                f"{path}\n" + err.message)

    def _create_children_from_dict(self, data):
        if "validate" in self.definition and self.definition["validate"]:
            validate_against_json_schema(data, self.definition["validate"])

        children = []

        for name, value in data.items():
            children.append(convert_basic_element(
                value, name, f"The value in the dict for key:{name} has an unknown type."))

        return children

    def typecheck(self, element: StructureElement):
        return isinstance(element, DictElement)

    @Converter.debug_matching("name_and_value")
    def match(self, element: StructureElement):
        """
        Allways matches if the element has the right type.
        """
        # TODO: See comment on types and inheritance
        if not isinstance(element, DictElement):
            raise RuntimeError("Element must be a DictElement.")
        vardict = match_name_and_value(self.definition, element.name, element.value)

        if not self.match_properties(element.value, vardict):
            return None

        return vardict


class PropertiesFromDictConverter(DictElementConverter):
    """Extend the :py:class:`DictElementConverter` by a heuristic to set
    property values from the dictionary keys.

    """

    def __init__(self, definition: dict, name: str, converter_registry: dict,
                 referenced_record_callback: Optional[callable] = None):

        super().__init__(definition, name, converter_registry)
        self.referenced_record_callback = referenced_record_callback

    def _recursively_create_records(self, subdict: dict, root_record: db.Record,
                                    root_rec_name: str,
                                    values: GeneralStore, records: RecordStore,
                                    referenced_record_callback: callable,
                                    keys_modified: list = []
                                    ):
        """Create a record form the given `subdict` and recursively create referenced records."""

        blacklisted_keys = self.definition["record_from_dict"][
            "properties_blacklist"] if "properties_blacklist" in self.definition["record_from_dict"] else []
        special_references = self.definition["record_from_dict"]["references"] if "references" in self.definition["record_from_dict"] else [
        ]

        for key, value in subdict.items():

            if key in blacklisted_keys:
                # We ignore this in the automated property generation
                continue
            if isinstance(value, list):
                if not any([isinstance(val, dict) for val in value]):
                    # no dict in list, i.e., no references, so this is simple
                    root_record.add_property(name=key, value=value)
                else:
                    if not all([isinstance(val, dict) for val in value]):
                        # if this is not an error (most probably it is), this
                        # needs to be handled manually for now.
                        raise ValueError(
                            f"{key} in {subdict} contains a mixed list of references and scalars.")
                    ref_recs = []
                    for ii, ref_dict in enumerate(value):
                        ref_var_name = f"{root_rec_name}.{key}.{ii+1}"
                        ref_rec, keys_modified = self._create_ref_rec(
                            ref_var_name,
                            key,
                            ref_dict,
                            special_references,
                            records,
                            values,
                            keys_modified,
                            referenced_record_callback
                        )
                        ref_recs.append(ref_rec)
                    root_record.add_property(name=key, value=ref_recs)

            elif isinstance(value, dict):
                # Treat scalar reference
                ref_var_name = f"{root_rec_name}.{key}"
                ref_rec, keys_modified = self._create_ref_rec(
                    ref_var_name,
                    key,
                    value,
                    special_references,
                    records,
                    values,
                    keys_modified,
                    referenced_record_callback
                )
                root_record.add_property(key, ref_rec)
            else:
                # All that remains are scalar properties which may or
                # may not be special attributes like name.
                if key.lower() in SPECIAL_PROPERTIES:
                    setattr(root_record, key.lower(), value)
                else:
                    root_record.add_property(name=key, value=value)
            keys_modified.append((root_rec_name, key))

        if referenced_record_callback:
            root_record = referenced_record_callback(root_record, records, values)

        return keys_modified

    def _create_ref_rec(
            self,
            name: str,
            key: str,
            subdict: dict,
            special_references: dict,
            records: RecordStore,
            values: GeneralStore,
            keys_modified: list,
            referenced_record_callback: callable
    ):
        """Create the referenced Record and forward the stores etc. to
        ``_recursively_create_records``.

        Parameters:
        -----------
        name : str
            name of the referenced record to be created in RecordStore and Value Store.
        key : str
            name of the key this record's definition had in the original dict.
        subdict : dict
            subdict containing this record's definition from the original dict.
        special_references : dict
            special treatment of referenced records from the converter definition.
        records : RecordStore
            RecordStore for entering new Records
        values : GeneralStore
            ValueStore for entering new Records
        keys_modified : list
            List for keeping track of changes
        referenced_record_callback : callable
            Advanced treatment of referenced records as given in the
            converter initialization.
        """
        ref_rec = db.Record()
        if key in special_references:
            for par in special_references[key]["parents"]:
                ref_rec.add_parent(par)
        else:
            ref_rec.add_parent(key)
        records[name] = ref_rec
        values[name] = ref_rec
        keys_modified = self._recursively_create_records(
            subdict=subdict,
            root_record=ref_rec,
            root_rec_name=name,
            values=values,
            records=records,
            referenced_record_callback=referenced_record_callback,
            keys_modified=keys_modified
        )
        return ref_rec, keys_modified

    def create_records(self, values: GeneralStore, records: RecordStore,
                       element: StructureElement):

        keys_modified = []

        rfd = self.definition["record_from_dict"]
        if rfd["variable_name"] not in records:
            rec = db.Record()
            if "name" in rfd:
                rec.name = rfd["name"]
            if "parents" in rfd:
                for par in rfd["parents"]:
                    rec.add_parent(par)
            else:
                rec.add_parent(rfd["variable_name"])
            records[rfd["variable_name"]] = rec
            values[rfd["variable_name"]] = rec

        else:
            rec = records[rfd["variable_name"]]

        keys_modified = self._recursively_create_records(
            subdict=element.value,
            root_record=rec,
            root_rec_name=rfd["variable_name"],
            values=values,
            records=records,
            referenced_record_callback=self.referenced_record_callback,
            keys_modified=keys_modified,
        )

        keys_modified.extend(super().create_records(
            values=values, records=records, element=element))

        return keys_modified


class DictConverter(DictElementConverter):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning(
            "This class is deprecated. Please use DictElementConverter."))
        super().__init__(*args, **kwargs)


class DictDictElementConverter(DictElementConverter):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning(
            "This class is deprecated. Please use DictElementConverter."))
        super().__init__(*args, **kwargs)


class JSONFileConverter(SimpleFileConverter):
    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        # TODO: See comment on types and inheritance
        if not isinstance(element, File):
            raise ValueError("create_children was called with wrong type of StructureElement")
        with open(element.path, 'r') as json_file:
            json_data = json.load(json_file)
        if "validate" in self.definition and self.definition["validate"]:
            try:
                validate_against_json_schema(json_data, self.definition["validate"])
            except ConverterValidationError as err:
                raise ConverterValidationError(
                    "Error during the validation of the JSON file:\n"
                    f"{element.path}\n" + err.message)
        structure_element = convert_basic_element(
            json_data,
            name=element.name + "_child_dict",
            msg_prefix="The JSON File contained content that was parsed to a Python object"
            " with an unexpected type.")
        return [structure_element]


class YAMLFileConverter(SimpleFileConverter):
    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        # TODO: See comment on types and inheritance
        if not isinstance(element, File):
            raise ValueError("create_children was called with wrong type of StructureElement")
        with open(element.path, 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
        if "validate" in self.definition and self.definition["validate"]:
            try:
                validate_against_json_schema(yaml_data, self.definition["validate"])
            except ConverterValidationError as err:
                raise ConverterValidationError(
                    "Error during the validation of the YAML file:\n"
                    f"{element.path}\n" + err.message)
        structure_element = convert_basic_element(
            yaml_data,
            name=element.name + "_child_dict",
            msg_prefix="The YAML File contained content that was parsed to a Python object"
            " with an unexpected type.")
        return [structure_element]


def match_name_and_value(definition, name, value):
    """Take match definitions from the definition argument and apply regular expression to name and
    possibly value.

    Exactly one of the keys ``match_name`` and ``match`` must exist in ``definition``,
    ``match_value`` is optional

Returns
-------

out:
  None, if match_name or match lead to no match. Otherwise, returns a dictionary with the
  matched groups, possibly including matches from using `definition["match_value"]`

    """
    if "match_name" in definition:
        if "match" in definition:
            raise RuntimeError("Do not supply both, 'match_name' and 'match'.")

        m1 = re.match(definition["match_name"], name)
        if m1 is None:
            return None
        else:
            m1 = m1.groupdict()
    elif "match" in definition:
        m1 = re.match(definition["match"], name)
        if m1 is None:
            return None
        else:
            m1 = m1.groupdict()
    else:
        m1 = {}

    if "match_value" in definition:
        # None values will be interpreted as empty strings for the
        # matcher.
        m_value = str(value) if (value is not None and not pd.isna(value)) else ""
        m2 = re.match(definition["match_value"], m_value, re.DOTALL)
        if m2 is None:
            return None
        else:
            m2 = m2.groupdict()
    else:
        m2 = {}

    values = dict()
    values.update(m1)
    values.update(m2)
    return values


class _AbstractScalarValueElementConverter(Converter):
    """A base class for all converters that have a scalar value that can be matched using a regular
    expression.

    values must have one of the following type: str, bool, int, float

    """

    default_matches = {
        "accept_text": False,
        "accept_bool": False,
        "accept_int": False,
        "accept_float": False,
    }

    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        return []

    def typecheck(self, element: StructureElement):
        """
        returns whether the type of StructureElement is accepted by this converter instance.
        """
        allowed_matches = self._merge_match_definition_with_default(self.default_matches,
                                                                    self.definition)
        return self._typecheck(element, allowed_matches)

    @Converter.debug_matching("name_and_value")
    def match(self, element: StructureElement):
        """
        Try to match the given structure element.

        If it does not match, return None.

        Else return a dictionary containing the variables from the matched regexp
        as key value pairs.
        """
        # TODO: See comment on types and inheritance
        if (not isinstance(element, TextElement)
                and not isinstance(element, BooleanElement)
                and not isinstance(element, IntegerElement)
                and not isinstance(element, FloatElement)):
            raise ValueError("create_children was called with wrong type of StructureElement")
        return match_name_and_value(self.definition, element.name, element.value)

    def _typecheck(self, element: StructureElement, allowed_matches: dict):
        """Return whether the type of StructureElement is accepted.

        Parameters: element: StructureElement, the element that is checked allowed_matches: Dict, a
        dictionary that defines what types are allowed. It must have the keys 'accept_text',
        'accept_bool', 'accept_int', and 'accept_float'.

        returns:  whether or not the converter allows the type of element

        """
        if (bool(allowed_matches["accept_text"]) and isinstance(element, TextElement)):
            return True
        elif (bool(allowed_matches["accept_bool"]) and isinstance(element, BooleanElement)):
            return True
        elif (bool(allowed_matches["accept_int"]) and isinstance(element, IntegerElement)):
            return True
        elif (bool(allowed_matches["accept_float"]) and isinstance(element, FloatElement)):
            return True
        else:
            return False

    def _merge_match_definition_with_default(self, default: dict, definition: dict):
        """
        returns a dict with the same keys as default dict but with updated values from definition
        where it has the same keys
        """

        result = {}
        for key in default:
            if key in definition:
                result[key] = definition[key]
            else:
                result[key] = default[key]
        return result


class BooleanElementConverter(_AbstractScalarValueElementConverter):
    default_matches = {
        "accept_text": False,
        "accept_bool": True,
        "accept_int": True,
        "accept_float": False,
    }


class DictBooleanElementConverter(BooleanElementConverter):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning(
            "This class is deprecated. Please use BooleanElementConverter."))
        super().__init__(*args, **kwargs)


class FloatElementConverter(_AbstractScalarValueElementConverter):
    default_matches = {
        "accept_text": False,
        "accept_bool": False,
        "accept_int": True,
        "accept_float": True,
    }


class DictFloatElementConverter(FloatElementConverter):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning(
            "This class is deprecated. Please use FloatElementConverter."))
        super().__init__(*args, **kwargs)


class TextElementConverter(_AbstractScalarValueElementConverter):
    default_matches = {
        "accept_text": True,
        "accept_bool": True,
        "accept_int": True,
        "accept_float": True,
    }

    def __init__(self, definition, *args, **kwargs):
        if "match" in definition:
            raise ValueError("""
The 'match' key is used to match a potential name of a TextElement. Please use
the 'match_value' key to match the value of the TextElement and 'match_name' for matching the name.
""")

        super().__init__(definition, *args, **kwargs)


class DictTextElementConverter(TextElementConverter):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning(
            "This class is deprecated. Please use TextElementConverter."))
        super().__init__(*args, **kwargs)


class IntegerElementConverter(_AbstractScalarValueElementConverter):
    default_matches = {
        "accept_text": False,
        "accept_bool": False,
        "accept_int": True,
        "accept_float": False,
    }


class DictIntegerElementConverter(IntegerElementConverter):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning(
            "This class is deprecated. Please use IntegerElementConverter."))
        super().__init__(*args, **kwargs)


class ListElementConverter(Converter):
    def create_children(self, generalStore: GeneralStore,
                        element: StructureElement):
        # TODO: See comment on types and inheritance
        if not isinstance(element, ListElement):
            raise RuntimeError(
                "This converter can only process ListElements.")
        children: list[StructureElement] = []
        for index, list_element in enumerate(element.value):
            children.append(
                convert_basic_element(
                    list_element,
                    name=f"{index}",
                    msg_prefix=f"The value at index {index} in the list as an unknown type."
                )
            )
        return children

    def typecheck(self, element: StructureElement):
        return isinstance(element, ListElement)

    @Converter.debug_matching("name")
    def match(self, element: StructureElement):
        # TODO: See comment on types and inheritance
        if not isinstance(element, ListElement):
            raise RuntimeError("Element must be a ListElement.")
        m = re.match(self.definition["match_name"], element.name)
        if m is None:
            return None
        if "match" in self.definition:
            raise NotImplementedError(
                "Match is not implemented for ListElement.")
        return m.groupdict()


class DictListElementConverter(ListElementConverter):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning(
            "This class is deprecated. Please use ListElementConverter."))
        super().__init__(*args, **kwargs)


class TableConverter(Converter):
    """This converter reads tables in different formats line by line and
    allows matching the corresponding rows.

    The subtree generated by the table converter consists of DictElements, each being
    a row. The corresponding header elements will become the dictionary keys.

    The rows can be matched using a DictElementConverter.

    """

    def get_options(self) -> dict:
        """Get specific options, e.g. from ``self.definitions``.

This method may to be overwritten by the specific table converter to provide information about the
possible options.  Implementors may use ``TableConverter._get_options(...)`` to get (and convert)
options from ``self.definitions``.

Returns
-------
out: dict
  An options dict.
        """
        return {}

    def _get_options(self, possible_options: list[tuple[str, Callable]]) -> dict:
        option_dict = dict()
        for opt_name, opt_conversion in possible_options:
            if opt_name in self.definition:
                el = self.definition[opt_name]
                # The option can often either be a single value or a list of values.
                # In the latter case each element of the list will be converted to the defined
                # type.
                if isinstance(el, list):
                    option_dict[opt_name] = [
                        opt_conversion(el_el) for el_el in el]
                else:
                    option_dict[opt_name] = opt_conversion(el)
        return option_dict

    def typecheck(self, element: StructureElement):
        return isinstance(element, File)

    @Converter.debug_matching("name")
    def match(self, element: StructureElement):
        # TODO: See comment on types and inheritance
        if not isinstance(element, File):
            raise RuntimeError("Element must be a File.")
        m = re.match(self.definition["match"], element.name)
        if m is None:
            return None
        return m.groupdict()

    @staticmethod
    def _children_from_dataframe(dataframe: pd.DataFrame):
        child_elements = list()
        for index, row in dataframe.iterrows():
            child_elements.append(
                DictElement(str(index), row.to_dict()))
        return child_elements


class XLSXTableConverter(TableConverter):
    """
**Operates on:** :py:class:`caoscrawler.structure_elements.File`

**Generates:** :py:class:`caoscrawler.structure_elements.DictElement`
    """

    def get_options(self):
        return self._get_options([
            ("sheet_name", str),
            ("header", int),
            ("names", str),
            ("index_col", int),
            ("usecols", int),
            ("true_values", str),
            ("false_values", str),
            ("na_values", str),
            ("parse_dates", bool),
            ("skiprows", int),
            ("nrows", int),
            ("keep_default_na", str_to_bool),
            ("converters", dict),
            ("obligatory_columns", str),
            ("existing_columns", list),
            ("unique_keys", list),
        ]
        )

    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        # TODO: See comment on types and inheritance
        if not isinstance(element, File):
            raise RuntimeError("Element must be a File.")
        options = self.get_options()
        if 'converters' in options:
            converters = options.pop('converters')
            for key, value in converters.items():
                if value == "int":
                    converters[key] = int
                elif value == "float":
                    converters[key] = float
                elif value == "str":
                    converters[key] = str
                elif value == "bool":
                    converters[key] = bool
                elif value == "date":
                    converters[key] = pd.to_datetime
                    # converters[key] = lambda x:  pd.to_datetime(x).to_pydatetime().date()
                elif value == "datetime":
                    converters[key] = pd.to_datetime
                elif value == "time":
                    converters[key] = pd.to_datetime
                else:
                    raise ValueError(f"Unknown conversion: '{value}'")
            xlsx_importer = XLSImporter(
                converters=converters,
                obligatory_columns=options.get("obligatory_columns", None),
                unique_keys=options.get("unique_keys", None),
                datatypes=None,
                existing_columns=options.get("existing_columns", None))
            table = xlsx_importer.read_file(element.path, **options)
        else:
            table = pd.read_excel(element.path, **options)
        return self._children_from_dataframe(table)


class CSVTableConverter(TableConverter):
    def get_options(self):
        return self._get_options([
            ("sep", str),
            ("delimiter", str),
            ("header", int),
            ("names", str),
            ("index_col", int),
            ("usecols", int),
            ("true_values", str),
            ("false_values", str),
            ("na_values", str),
            ("skiprows", int),
            ("nrows", int),
            ("keep_default_na", str_to_bool), ])

    def create_children(self, generalStore: GeneralStore,
                        element: StructureElement):
        # TODO: See comment on types and inheritance
        if not isinstance(element, File):
            raise RuntimeError("Element must be a File.")
        table = pd.read_csv(element.path, **self.get_options())
        return self._children_from_dataframe(table)


class DateElementConverter(TextElementConverter):
    """allows to convert different text formats of dates to Python date objects.

    The text to be parsed must be contained in the "date" group. The format string can be supplied
    under "date_format" in the Converter definition. The library used is datetime so see its
    documentation for information on how to create the format string.

    """

    # TODO make `date` parameter name configurable
    def match(self, element: StructureElement):
        matches = super().match(element)
        if matches is not None and "date" in matches:
            matches.update({"date": datetime.datetime.strptime(
                matches["date"],
                self.definition["date_format"] if "date_format" in self.definition else "%Y-%m-%d"
            ).date()})
        return matches


class DatetimeElementConverter(TextElementConverter):
    """Convert text so that it is formatted in a way that LinkAhead can understand it.

The text to be parsed must be in the ``val`` parameter. The format string can be supplied in the
``datetime_format`` node. This class uses the ``datetime`` module, so ``datetime_format`` must
follow this specificaton:
https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

    """

    # TODO make `val` parameter name configurable
    def match(self, element: StructureElement):
        matches = super().match(element)
        if matches is not None and "val" in matches:
            fmt_default = "%Y-%m-%dT%H:%M:%S"
            fmt = self.definition.get("datetime_format", fmt_default)
            dt_str = datetime.datetime.strptime(matches["val"], fmt).strftime(fmt_default)
            matches.update({"val": dt_str})
        return matches
