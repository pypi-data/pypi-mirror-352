#!/usr/bin/env python3
# encoding: utf-8
#
# This file is a part of the CaosDB Project.
#
# Copyright (C) 2023 Research Group Biomedical Physics,
# Max-Planck-Institute for Dynamics and Self-Organization Göttingen
# Alexander Schlemmer <alexander.schlemmer@ds.mpg.de>
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
This is the scanner.

This was where formerly the ``_crawl(...)`` function from ``crawl.py`` was located.

This is just the functionality that extracts data from the file system.
"""

from __future__ import annotations

import importlib
import logging
import os
import warnings
from collections.abc import Callable
from typing import Any, Optional, Union

import linkahead as db
import yaml
from importlib_resources import files
from jsonschema import validate

from .converters import Converter
from .debug_tree import DebugTree
from .stores import GeneralStore, RecordStore
from .structure_elements import Directory, StructureElement
from .version import check_cfood_version

logger = logging.getLogger(__name__)


def load_definition(crawler_definition_path: str) -> dict:
    """
    Load a cfood from a crawler definition defined by
    crawler definition path and validate it using cfood-schema.yml.

    Arguments:
    ----------
    crawler_definition_path: str
         Path to the crawler definition file in yaml format.

    Returns:
    --------
    dict containing the crawler definition.
    """

    # Load the cfood from a yaml file:
    with open(crawler_definition_path, encoding="utf-8") as f:
        crawler_definitions = list(yaml.safe_load_all(f))

    crawler_definition = _load_definition_from_yaml_dict(crawler_definitions)

    return _resolve_validator_paths(crawler_definition, crawler_definition_path)


def _load_definition_from_yaml_dict(crawler_definitions: list[dict]) -> dict:
    """Load crawler definitions from a list of (yaml) dicts `crawler_definitions` which
    contains either one or two documents.

    Doesn't resolve the validator paths in the cfood definition, so for
    internal and testing use only.

    Arguments:
    ----------
    crawler_definitions: list[dict]
         List of one or two dicts containing (optionally) metadata and the crawler definition.

    Returns:
    --------
    dict containing the crawler definition.
    """
    if len(crawler_definitions) == 1:
        # Simple case, just one document:
        crawler_definition = crawler_definitions[0]
        metadata = {}
    elif len(crawler_definitions) == 2:
        metadata = crawler_definitions[0]["metadata"] if "metadata" in crawler_definitions[0] else {
        }
        crawler_definition = crawler_definitions[1]
    else:
        raise RuntimeError(
            "Crawler definition must not contain more than two documents.")

    check_cfood_version(metadata)

    # TODO: at this point this function can already load the cfood schema extensions
    #       from the crawler definition and add them to the yaml schema that will be
    #       tested in the next lines of code:

    # Load the cfood schema:
    with open(str(files('caoscrawler').joinpath('cfood-schema.yml')), "r") as f:
        schema = yaml.safe_load(f)

    # Add custom converters to converter enum in schema:
    if "Converters" in crawler_definition:
        for key in crawler_definition["Converters"]:
            schema["cfood"]["$defs"]["converter"]["properties"]["type"]["enum"].append(
                key)
    if len(crawler_definitions) == 2:
        if "Converters" in metadata:
            for key in metadata["Converters"]:
                schema["cfood"]["$defs"]["converter"]["properties"]["type"]["enum"].append(
                    key)
        # TODO: We need a similar thing for "Transformers".

    # Validate the cfood schema:
    validate(instance=crawler_definition, schema=schema["cfood"])

    return crawler_definition


def _resolve_validator_paths(definition: dict, definition_path: str):
    """Resolve path to validation files with respect to the file in which
    the crawler was defined.

    """

    for key, value in definition.items():

        if key == "validate" and isinstance(value, str):
            # Validator is given by a path
            if not value.startswith('/'):
                # Not an absolute path
                definition[key] = os.path.join(os.path.dirname(definition_path), value)
                if not os.path.isfile(definition[key]):
                    # TODO(henrik) capture this in `crawler_main` similar to
                    # `ConverterValidationError`.
                    raise FileNotFoundError(
                        f"Couldn't find validation file {definition[key]}")
        elif isinstance(value, dict):
            # Recursively resolve all validators
            definition[key] = _resolve_validator_paths(value, definition_path)

    return definition


def create_converter_registry(definition: dict):
    """
    Currently the converter registry is a dictionary containing for each converter:
    - key is the short code, abbreviation for the converter class name
    - module is the name of the module to be imported which must be installed
    - class is the converter class to load and associate with this converter entry

    Formerly known as "load_converters".

    all other info for the converter needs to be included in the converter plugin
    directory:
    schema.yml file
    README.md documentation
    """

    # Defaults for the converter registry:
    with open(str(files('caoscrawler').joinpath('default_converters.yml')), "r") as f:
        converter_registry: dict[str, dict[str, str]] = yaml.safe_load(f)

    # More converters from definition file:
    if "Converters" in definition:
        for key, entry in definition["Converters"].items():
            if key in ["Dict", "DictTextElement", "DictIntegerElement", "DictBooleanElement",
                       "DictDictElement", "DictListElement", "DictFloatElement"]:
                warnings.warn(DeprecationWarning(f"{key} is deprecated. Please use the new"
                                                 " variant; without 'Dict' prefix or "
                                                 "'DictElement' in case of 'Dict'"))

            converter_registry[key] = {
                "converter": entry["converter"],
                "package": entry["package"]
            }

    # Load modules and associate classes:
    for key, value in converter_registry.items():
        module = importlib.import_module(value["package"])
        value["class"] = getattr(module, value["converter"])
    return converter_registry


def create_transformer_registry(definition: dict[str, dict[str, str]]):
    """
    Currently the transformer registry is a dictionary containing for each transformer:
    - key is the short code, abbreviation for the converter class name
    - module is the name of the module to be imported which must be installed
    - class is the transformer function to load and associate with this converter entry

    all other info for the converter needs to be included in the converter plugin
    directory:
    schema.yml file
    README.md documentation

    Please refer to the docstring of function "scanner" for more information about the
    detailed structure of the transformer functions.
    """

    # Defaults for the transformer registry:
    with open(str(files('caoscrawler').joinpath('default_transformers.yml')), "r") as f:
        transformer_def: dict[str, dict[str, str]] = yaml.safe_load(f)

    registry: dict[str, Callable[[Any, dict], Any]] = {}
    # More transformers from definition file:
    if "Transformers" in definition:
        for key, entry in definition["Transformers"].items():
            transformer_def[key] = {
                "function": entry["function"],
                "package": entry["package"]
            }

    # Load modules and associate classes:
    for key, value in transformer_def.items():
        module = importlib.import_module(value["package"])
        registry[key] = getattr(module, value["function"])
    return registry


def initialize_converters(crawler_definition: dict, converter_registry: dict):
    """
    takes the cfood as dict (`crawler_definition`) and creates the converter objects that
    are defined on the highest level. Child Converters will in turn be created during the
    initialization of the Converters.
    """
    converters = []

    for key, value in crawler_definition.items():
        # Definitions and Converters are reserved keywords
        # on the top level of the yaml file.
        # TODO: there should also be a top level keyword for the actual
        #       CFood to avoid confusion between top level keywords
        #       and the CFood.
        if key == "Definitions":
            continue
        elif key == "Converters":
            continue
        elif key == "Transformers":
            continue
        converters.append(Converter.converter_factory(
            value, key, converter_registry))

    return converters

# --------------------------------------------------------------------------------
# Main scanner function:
# --------------------------------------------------------------------------------


def scanner(items: list[StructureElement],
            converters: list[Converter],
            general_store: Optional[GeneralStore] = None,
            record_store: Optional[RecordStore] = None,
            structure_elements_path: Optional[list[str]] = None,
            converters_path: Optional[list[str]] = None,
            restricted_path: Optional[list[str]] = None,
            crawled_data: Optional[list[db.Record]] = None,
            debug_tree: Optional[DebugTree] = None,
            registered_transformer_functions: Optional[dict] = None) -> list[db.Record]:
    """Crawl a list of StructureElements and apply any matching converters.

    Formerly known as ``_crawl(...)``.

    Parameters
    ----------
    items: list[StructureElement]
        structure_elements (e.g. files and folders on one level on the hierarchy)

    converters: list[Converter]
        locally defined converters for treating structure elements. A locally
        defined converter could be one that is only valid for a specific subtree
        of the originally cralwed StructureElement structure.

    general_store, record_store: GeneralStore, RecordStore, optional
        This recursion of the crawl function should only operate on copies of
        the global stores of the Crawler object.

    restricted_path : list[str], optional
        traverse the data tree only along the given path. For example, when a
        directory contains files a, b and c, and b is given as ``restricted_path``, a
        and c will be ignored by the crawler. When the end of the given path is
        reached, traverse the full tree as normal. The first element of the list
        provided by ``restricted_path`` should be the name of the StructureElement
        at this level, i.e. denoting the respective element in the items
        argument.

    registered_transformer_functions : dict, optional
        A dictionary of transformer functions that can be used in the "transform" block
        of a converter and that allows to apply simple transformations to variables extracted
        either by the current converter or to other variables found in the current variable store.

        Each function is a dictionary:

        - The key is the name of the function to be looked up in the dictionary of registered
          transformer functions.
        - The value is the function which needs to be of the form:
            def func(in_value: Any, in_parameters: dict) -> Any:
                pass

    """
    # This path_found variable stores wether the path given by restricted_path was found in the
    # data tree
    path_found = False
    if restricted_path is not None and len(restricted_path) == 0:
        restricted_path = None

    if crawled_data is None:
        crawled_data = []

    if general_store is None:
        general_store = GeneralStore()

    if record_store is None:
        record_store = RecordStore()

    if structure_elements_path is None:
        structure_elements_path = []

    if converters_path is None:
        converters_path = []

    for element in items:
        element_path = os.path.join(*(structure_elements_path + [str(element.get_name())]))
        logger.debug(f"Dealing with {element_path}")
        for converter in converters:

            # type is something like "matches files", replace isinstance with "type_matches"
            # match function tests regexp for example
            if (converter.typecheck(element) and (
                    restricted_path is None or element.name == restricted_path[0])
                    and converter.match(element) is not None):
                path_found = True
                general_store_copy = general_store.create_scoped_copy()
                record_store_copy = record_store.create_scoped_copy()

                # Create an entry for this matched structure element that contains the path:
                general_store_copy[converter.name] = element_path

                # extracts values from structure element and stores them in the
                # variable store.
                converter.create_values(general_store_copy, element)

                # Apply transformers if there are any:
                converter.apply_transformers(general_store_copy,
                                             registered_transformer_functions)

                keys_modified = converter.create_records(
                    general_store_copy, record_store_copy, element)

                children = converter.create_children(general_store_copy, element)

                if debug_tree is not None:
                    # add provenance information for each variable
                    debug_tree.debug_tree[str(element)] = (
                        general_store_copy.get_storage(), record_store_copy.get_storage())
                    debug_tree.debug_metadata["copied"][str(element)] = (
                        general_store_copy.get_dict_copied(),
                        record_store_copy.get_dict_copied())
                    debug_tree.debug_metadata["usage"][str(element)].add(
                        "/".join(converters_path + [converter.name]))
                    mod_info = debug_tree.debug_metadata["provenance"]
                    # TODO: actually keys_modified must not be None. create_records should
                    #       always return a list.
                    if keys_modified is not None:
                        for record_name, prop_name in keys_modified:
                            # TODO: check
                            internal_id = record_store_copy.get_internal_id(
                                record_name)
                            record_identifier = record_name + \
                                "_" + str(internal_id)
                            converter.metadata["usage"].add(record_identifier)
                            mod_info[record_identifier][prop_name] = (
                                structure_elements_path + [element.get_name()],
                                converters_path + [converter.name])

                scanner(children, converter.converters,
                        general_store_copy, record_store_copy,
                        structure_elements_path + [element.get_name()],
                        converters_path + [converter.name],
                        restricted_path[1:] if restricted_path is not None else None,
                        crawled_data, debug_tree,
                        registered_transformer_functions)

                # Clean up converter:
                converter.cleanup()

    if restricted_path and not path_found:
        raise RuntimeError("A 'restricted_path' argument was given that is not contained in "
                           "the data tree")
    # if the crawler is running out of scope, copy all records in
    # the record_store, that were created in this scope
    # to the general update container.
    scoped_records = record_store.get_records_current_scope()
    for record in scoped_records:
        crawled_data.append(record)

    return crawled_data


# --------------------------------------------------------------------------------
# Main scanning interface functions:
# --------------------------------------------------------------------------------


def scan_directory(dirname: Union[str, list[str]], crawler_definition_path: str,
                   restricted_path: Optional[list[str]] = None,
                   debug_tree: Optional[DebugTree] = None):
    """ Crawl a single directory.

    Formerly known as "crawl_directory".

    Convenience function that starts the crawler (calls start_crawling)
    with a single directory as the StructureElement.

    Parameters
    ----------

    dirname: str or list[str]
        directory or list of directories to be scanned
    restricted_path: optional, list of strings
        Traverse the data tree only along the given path. When the end
        of the given path is reached, traverse the full tree as
        normal. See docstring of 'scanner' for more details.

    Returns
    -------
    crawled_data : list
        the final list with the target state of Records.
    """

    crawler_definition = load_definition(crawler_definition_path)
    # Load and register converter packages:
    converter_registry = create_converter_registry(crawler_definition)

    # Load and register transformer functions:
    registered_transformer_functions = create_transformer_registry(crawler_definition)

    if not dirname:
        raise ValueError(
            "You have to provide a non-empty path for crawling.")
    if not isinstance(dirname, list):
        dirname = [dirname]
    dir_element_list = []
    for dname in dirname:
        dir_structure_name = os.path.basename(dname)

        # TODO: needs to be covered somewhere else
        crawled_directory = dname
        if not dir_structure_name and dname.endswith(os.path.sep):
            if dname == os.path.sep:
                # Crawling the entire file system
                dir_structure_name = "root"
            else:
                # dirname had a trailing '/'
                dir_structure_name = os.path.basename(dname[:-1])
        dir_element_list.append(Directory(dir_structure_name, dname))

    return scan_structure_elements(
        dir_element_list,
        crawler_definition,
        converter_registry,
        restricted_path=restricted_path,
        debug_tree=debug_tree,
        registered_transformer_functions=registered_transformer_functions
    )


def scan_structure_elements(items: Union[list[StructureElement], StructureElement],
                            crawler_definition: dict,
                            converter_registry: Optional[dict] = None,
                            restricted_path: Optional[list[str]] = None,
                            debug_tree: Optional[DebugTree] = None,
                            registered_transformer_functions: Optional[dict] = None) -> (
                                list[db.Record]):
    """
    Start point of the crawler recursion.

    Formerly known as "start_crawling".

    Parameters
    ----------
    items: list
         A list of structure elements (or a single StructureElement) that is used for
         generating the initial items for the crawler. This could e.g. be a Directory.
    crawler_definition : dict
         A dictionary representing the crawler definition, possibly from a yaml
         file.
    restricted_path: list[str], optional
         Traverse the data tree only along the given path. When the end of the
         given path is reached, traverse the full tree as normal. See docstring
         of 'scanner' for more details.
    converter_registry: dict, optional
         Optional dictionary containing the converter definitions
         needed for the crawler definition. If none is given, it will
         be generated from the `crawler_definition`. Default is None.
    registered_transformer_functions: dict, optional
         Optional dictionary containing the transformer function
         definitions needed for the crawler definition. If none is
         given, it will be generated from the
         `crawler_definition`. Default is None.

    Returns
    -------
    crawled_data : list[db.Record]
        the final list with the target state of Records.
    """

    # This function builds the tree of converters out of the crawler definition.
    if not isinstance(items, list):
        items = [items]

    if converter_registry is None:
        converter_registry = create_converter_registry(crawler_definition)
    if registered_transformer_functions is None:
        registered_transformer_functions = create_transformer_registry(crawler_definition)
    # TODO: needs to be covered somewhere else
    # self.run_id = uuid.uuid1()
    converters = initialize_converters(crawler_definition, converter_registry)

    return scanner(
        items=items,
        converters=converters,
        restricted_path=restricted_path,
        debug_tree=debug_tree,
        registered_transformer_functions=registered_transformer_functions
    )
