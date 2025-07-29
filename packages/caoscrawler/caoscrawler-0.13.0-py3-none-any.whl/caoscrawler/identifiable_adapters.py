#!/usr/bin/env python3
# encoding: utf-8
#
# ** header v3.0
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2021-2022 Henrik tom Wörden
#               2021-2022 Alexander Schlemmer
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

from __future__ import annotations

import logging
import warnings
from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Any

import linkahead as db
import yaml
from linkahead.cached import cached_get_entity_by, cached_query
from linkahead.utils.escape import escape_squoted_text

from .exceptions import (InvalidIdentifiableYAML, MissingIdentifyingProperty,
                         MissingRecordType, MissingReferencingEntityError)
from .identifiable import Identifiable
from .sync_node import SyncNode
from .utils import has_parent

logger = logging.getLogger(__name__)


def _retrieve_RecordType(id=None, name=None):
    """
    Retrieve the RecordType from LinkAhead. For mocking purposes.
    """
    return db.RecordType(name=name, id=id).retrieve()


def get_children_of_rt(rtname):
    """Supply the name of a recordtype. This name and the name of all children RTs are returned in
    a list"""
    escaped = escape_squoted_text(rtname)
    recordtypes = [p.name for p in cached_query(f"FIND RECORDTYPE '{escaped}'")]
    if not recordtypes:
        raise MissingRecordType(f"Record type could not be found on server: {rtname}")
    return recordtypes


def convert_value(value: Any) -> str:
    """Return a string representation of the value suitable for the search query.

    This is for search queries looking for the identified record.

    Parameters
    ----------
    value: Any
      The value to be converted.

    Returns
    -------
    out: str
      the string reprensentation of the value.

    """

    if isinstance(value, db.Entity):
        return str(value.id)
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, bool):
        return str(value).upper()
    elif isinstance(value, str):
        return escape_squoted_text(value)
    else:
        return str(value)


class IdentifiableAdapter(metaclass=ABCMeta):
    """Base class for identifiable adapters.

    Some terms:

    - A *registered identifiable* defines an identifiable template, for example by specifying:
        - Parent record types
        - Properties
        - ``is_referenced_by`` statements
    - An *identifiable* belongs to a concrete record.  It consists of identifying attributes which
      "fill in" the *registered identifiable*.  In code, it can be represented as a Record based on
      the *registered identifiable* with all the values filled in.
    - An *identified record* is the result of retrieving a record from the database, based on the
      *identifiable* (and its values).

    General question to clarify:

    - Do we want to support multiple identifiables per RecordType?
    - Current implementation supports only one identifiable per RecordType.

    The list of referenced by statements is currently not implemented.

    The IdentifiableAdapter can be used to retrieve the three above mentioned objects (registered
    identifiabel, identifiable and identified record) for a Record.

    """

    @staticmethod
    def create_query_for_identifiable(ident: Identifiable, startswith: bool = False):
        """
        This function is taken from the old crawler:
        caosdb-advanced-user-tools/src/caosadvancedtools/crawler.py

        uses the properties of ident to create a query that can determine
        whether the required record already exists.

        If ``startswith`` is True, use ``LIKE`` for long string values to test if the strings starts
        with the first 200 characters of the value.
        """

        query_string = "FIND RECORD "
        if ident.record_type is not None:
            escaped_rt = escape_squoted_text(ident.record_type)
            query_string += f"'{escaped_rt}'"
        for ref in ident.backrefs:
            eid = ref
            if isinstance(ref, db.Entity):
                eid = ref.id
            query_string += " WHICH IS REFERENCED BY " + str(eid) + " AND"

        query_string += " WITH "

        if ident.name is not None:
            query_string += "name='{}'".format(escape_squoted_text(ident.name))
            if len(ident.properties) > 0:
                query_string += " AND "

        query_string += IdentifiableAdapter.create_property_query(
            ident, startswith=startswith
        )

        # TODO Can these cases happen at all with the current code?
        if query_string.endswith(" AND WITH "):
            query_string = query_string[: -len(" AND WITH ")]
        if query_string.endswith(" AND "):
            query_string = query_string[: -len(" AND ")]
        return query_string

    def all_identifying_properties_exist(
        self, node: SyncNode, raise_exception: bool = True
    ):
        """checks whether all identifying properties exist and raises an error if
        that's not the case. It furthermore raises an error if "name" is part of
        the identifiable, but the node does not have a name.

        If raise_exception is False, the function returns False instead of raising an error.

        Backreferences are not checked.

        Returns True if all identifying properties exist.

        Last review by Alexander Schlemmer on 2024-05-24.
        """
        if node.registered_identifiable is None:
            if raise_exception:
                parents = [p.name for p in node.parents]
                parents_str = "\n".join(f"- {p}" for p in parents)
                raise RuntimeError("No registered identifiable for node with these parents:\n"
                                   + parents_str)
            else:
                return False
        for prop in node.registered_identifiable.properties:
            if prop.name.lower() == "is_referenced_by":
                continue
            if prop.name.lower() == "name":
                if node.name is None:
                    if raise_exception:
                        i = MissingIdentifyingProperty("The node has no name.")
                        i.prop = "name"
                        raise i
                    else:
                        return False
                else:
                    continue

            # multiple occurances are ok here. We deal with that when actually creating an
            # identifiable (IDs of referenced Entities might need to get resolved first).
            if (
                len(
                    [
                        el
                        for el in node.properties
                        if el.name.lower() == prop.name.lower()
                    ]
                )
                == 0
            ):
                if raise_exception:
                    i = MissingIdentifyingProperty(
                        f"The property {prop.name} is missing."
                    )
                    i.prop = prop.name
                    raise i
                else:
                    return False

        return True

    @staticmethod
    def __create_pov_snippet(pname: str, pvalue, startswith: bool = False):
        """Return something like ``'name'='some value'`` or ``'name' LIKE 'some*'``.

        If ``startswith`` is True, the value of strings will be cut off at 200 characters and a ``LIKE``
        operator will be used to find entities matching at the beginning.
        """
        if startswith and isinstance(pvalue, str) and len(pvalue) > 200:
            operator_value_str = f" LIKE '{escape_squoted_text(pvalue[:200])}*'"
        else:
            operator_value_str = "='" + convert_value(pvalue) + "'"
        result = "'" + escape_squoted_text(pname) + "'" + operator_value_str
        return result

    @staticmethod
    def create_property_query(entity: Identifiable, startswith: bool = False):
        """Create a POV query part with the entity's properties.

        Parameters
        ----------

        entity: Identifiable
          The Identifiable whose properties shall be used.

        startswith: bool, optional
          If True, check string typed properties against the first 200 characters only.  Default is False.
        """
        query_string = ""
        pov = IdentifiableAdapter.__create_pov_snippet  # Shortcut
        for pname, pvalue in entity.properties.items():
            if pvalue is None:
                query_string += "'" + escape_squoted_text(pname) + "' IS NULL AND "
            elif isinstance(pvalue, list):
                for v in pvalue:
                    query_string += pov(pname, v, startswith=startswith) + " AND "

            # TODO: (for review)
            #       This code would allow for more complex identifiables with
            #       subproperties being checked directly.
            #       we currently do not need them and they could introduce
            #       problems in the local caching mechanism.
            #       However, it could be discussed to implement a similar mechanism.
            # elif isinstance(p.value, db.Entity):
            #     query_string += ("'" + p.name + "' WITH (" +
            #                      IdentifiableAdapter.create_property_query(p.value) +
            #                      ") AND ")
            else:
                query_string += pov(pname, pvalue, startswith=startswith) + " AND "
        # remove the last AND
        return query_string[:-4]

    @abstractmethod
    def get_registered_identifiable(self, record: db.Entity):
        """
        Check whether an identifiable is registered for this record and return its definition.
        If there is no identifiable registered, return None.
        """
        pass

    @abstractmethod
    def get_file(self, identifiable: db.File):
        warnings.warn(
            DeprecationWarning("This function is deprecated. Please do not use it.")
        )
        """
        Retrieve the file object for a (File) identifiable.
        """
        pass

    @staticmethod
    def get_identifying_referenced_entities(record, registered_identifiable):
        """Create a list of all entities that are referenced by record
           and that are used as identying properties of the identifiable.

           Last review by Alexander Schlemmer on 2024-05-29.
        """
        refs = []
        for prop in registered_identifiable.properties:
            pname = prop.name.lower()
            if pname == "name" or pname == "is_referenced_by":
                continue
            if record.get_property(prop.name) is None:
                logger.error(f"Record with missing identifying property:\n{record}\n"
                             f"This property is missing: {prop.name}\n")
                raise RuntimeError("Missing identifying Property")
            pval = record.get_property(prop.name).value
            if not isinstance(prop.value, list):
                pval = [prop.value]
            for val in pval:
                if isinstance(val, db.Entity):
                    refs.append(val)
        return refs

    def get_identifiable(self, se: SyncNode, identifiable_backrefs: set[SyncNode]) -> Identifiable:
        """
        Take the registered identifiable of given SyncNode ``se`` and fill the property values to
        create an identifiable.

        Args:
            se: the SyncNode for which the Identifiable shall be created.
            identifiable_backrefs: a set (Type: set[SyncNode]), that contains SyncNodes
                                   with a certain RecordType, that reference ``se``

        Returns:
            Identifiable, the identifiable for record.

        Last review by Alexander Schlemmer on 2024-05-29.
        """

        property_name_list_A = []
        identifiable_props = {}
        name = None

        if se.registered_identifiable is None:
            raise ValueError("no registered_identifiable")

        # fill the values:
        for prop in se.registered_identifiable.properties:
            # TDOO:
            # If there are multiproperties in the registered_identifiable, then only the LAST is
            # taken into account (later properties overwrite previous one in the dict below).
            if prop.name == "name":
                name = se.name
                continue

            if prop.name.lower() == "is_referenced_by":
                for el in identifiable_backrefs:
                    if not isinstance(el, SyncNode):
                        raise ValueError("Elements of `identifiable_backrefs` must be SyncNodes")
                if len(identifiable_backrefs) == 0:
                    raise MissingReferencingEntityError(
                        f"Could not find referencing entities of type(s): {prop.value}\n"
                        f"for registered identifiable:\n{se.registered_identifiable}\n"
                        f"There were {len(identifiable_backrefs)} referencing entities to "
                        "choose from.\n"
                        f"This error can also occur in case of merge conflicts in the referencing"
                        " entities."
                    )
                elif len([e.id for e in identifiable_backrefs if el.id is None]) > 0:
                    raise RuntimeError("Referencing entity has no id")
                # At this point we know that there is at least one referencing SyncNode
                # with an ID. We do not need to set any property value (the reference will be used
                # in the backrefs argument below) and can thus continue with the next identifying
                # property
                continue

            options = [p.value for p in se.properties if p.name.lower() == prop.name.lower()]
            if len(options) == 0:
                raise MissingIdentifyingProperty(
                    f"The following record is missing an identifying property:\n"
                    f"RECORD\n{se}\nIdentifying PROPERTY\n{prop.name}"
                )
            for ii, el in enumerate(options):
                if isinstance(el, SyncNode):
                    options[ii] = el.id
                    if el.id is None:
                        raise RuntimeError(
                            "Reference to unchecked in identifiable:\n"
                            f"{prop.name}:\n{el}"
                        )
                else:
                    options[ii] = el
            if not all([f == options[0] for f in options]):
                raise RuntimeError("differing prop values ")

            identifiable_props[prop.name] = options[0]
            property_name_list_A.append(prop.name)

        # check for multi properties in the record:
        if len(set(property_name_list_A)) != len(property_name_list_A):
            raise RuntimeError(
                "Multi properties used in identifiables could cause unpredictable results and "
                "are not allowed. You might want to consider a Property with a list as value."
            )

        # use the RecordType of the registered Identifiable if it exists
        # We do not use parents of Record because it might have multiple
        try:
            return Identifiable(
                record_id=se.id,
                record_type=se.registered_identifiable.parents[0].name,
                name=name,
                properties=identifiable_props,
                backrefs=[e.id for e in identifiable_backrefs],
            )
        except Exception as exc:
            logger.error(exc)
            logger.error(f"Error while creating identifiable for this record:\n{se}")
            raise

    @abstractmethod
    def retrieve_identified_record_for_identifiable(self, identifiable: Identifiable):
        """
        Retrieve identifiable record for a given identifiable.

        This function will return None if there is either no identifiable registered
        or no corresponding identified record in the database for a given record.

        Warning: this function is not expected to work correctly for file identifiables.
        """
        pass

    @staticmethod
    def referencing_entity_has_appropriate_type(parents, register_identifiable):
        """returns true if one of the parents is listed by the 'is_referenced_by' property

        This function also returns True if 'is_referenced_by' contains the wildcard '*'.

        Last review by Alexander Schlemmer on 2024-05-29.
        """
        if register_identifiable.get_property("is_referenced_by") is None:
            return False
        if register_identifiable.get_property("is_referenced_by").value is None:
            return False

        appropriate_types = []
        for rt in register_identifiable.get_property("is_referenced_by").value:
            appropriate_types.extend(get_children_of_rt(rt))
        appropriate_types = [el.lower() for el in appropriate_types]
        if "*" in appropriate_types:
            return True
        for parent in parents:
            if parent.name.lower() in appropriate_types:
                return True
        return False


class LocalStorageIdentifiableAdapter(IdentifiableAdapter):
    """
    Identifiable adapter which can be used for unit tests.
    """

    def __init__(self):
        warnings.warn(
            DeprecationWarning(
                "This class is deprecated. Please use the CaosDBIdentifiableAdapter."
            )
        )
        self._registered_identifiables = dict()
        self._records = []

    def register_identifiable(self, name: str, definition: db.RecordType):
        self._registered_identifiables[name] = definition

    def get_records(self):
        return self._records

    def get_file(self, identifiable: Identifiable):
        """
        Just look in records for a file with the same path.
        """
        candidates = []
        warnings.warn(
            DeprecationWarning("This function is deprecated. Please do not use it.")
        )
        for record in self._records:
            if record.role == "File" and record.path == identifiable.path:
                candidates.append(record)
        if len(candidates) > 1:
            raise RuntimeError("Identifiable was not defined unambigiously.")
        if len(candidates) == 0:
            return None
        return candidates[0]

    def store_state(self, filename):
        with open(filename, "w") as f:
            f.write(
                db.common.utils.xml2str(db.Container().extend(self._records).to_xml())
            )

    def restore_state(self, filename):
        with open(filename, "r") as f:
            self._records = db.Container().from_xml(f.read())

    # TODO: move to super class?
    def is_identifiable_for_record(
        self, registered_identifiable: db.RecordType, record: db.Record
    ):
        """
        Check whether this registered_identifiable is an identifiable for the record.

        That means:
        - The properties of the registered_identifiable are a subset of the properties of record.
        - One of the parents of record is the parent of registered_identifiable.

        Return True in that case and False otherwise.
        """
        if len(registered_identifiable.parents) != 1:
            raise RuntimeError("Multiple parents for identifiables not supported.")

        if not has_parent(record, registered_identifiable.parents[0].name):
            return False

        for prop in registered_identifiable.properties:
            if record.get_property(prop.name) is None:
                return False
        return True

    def get_registered_identifiable(self, record: db.Entity):
        identifiable_candidates = []
        for _, definition in self._registered_identifiables.items():
            if self.is_identifiable_for_record(definition, record):
                identifiable_candidates.append(definition)
        if len(identifiable_candidates) > 1:
            raise RuntimeError("Multiple candidates for an identifiable found.")
        if len(identifiable_candidates) == 0:
            return None
        return identifiable_candidates[0]

    def check_record(self, record: db.Record, identifiable: Identifiable):
        """
        Check for a record from the local storage (named "record") if it is
        the identified record for an identifiable which was created by
        a run of the crawler.

        Naming of the parameters could be confusing:
        record is the record from the local database to check against.
        identifiable is the record that was created during the crawler run.
        """
        if identifiable.record_type is not None and not has_parent(
            record, identifiable.record_type
        ):
            return False
        for propname, propvalue in identifiable.properties.items():
            prop_record = record.get_property(propname)
            if prop_record is None:
                return False

            # if prop is an entity, it needs to be resolved first.
            # there are two different cases:
            # a) prop_record.value has a registered identifiable:
            #      in this case, fetch the identifiable and set the value accordingly
            if isinstance(propvalue, db.Entity):  # lists are not checked here
                otherid = prop_record.value
                if isinstance(prop_record.value, db.Entity):
                    otherid = prop_record.value.id
                if propvalue.id != otherid:
                    return False

            elif propvalue != prop_record.value:
                return False
        return True

    def retrieve_identified_record_for_identifiable(self, identifiable: Identifiable):
        candidates = []
        for record in self._records:
            if self.check_record(record, identifiable):
                candidates.append(record)
        if len(candidates) > 1:
            raise RuntimeError(
                f"Identifiable was not defined unambigiously. Possible candidates are {candidates}"
            )
        if len(candidates) == 0:
            return None
        return candidates[0]


class CaosDBIdentifiableAdapter(IdentifiableAdapter):
    """
    Identifiable adapter which can be used for production.
    """

    # TODO: don't store registered identifiables locally

    def __init__(self):
        self._registered_identifiables = {}

    def load_from_yaml_definition(self, path: str):
        """Load identifiables defined in a yaml file"""
        with open(path, "r", encoding="utf-8") as yaml_f:
            identifiable_data = yaml.safe_load(yaml_f)
        self.load_from_yaml_object(identifiable_data)

    def load_from_yaml_object(self, identifiable_data):
        """Load identifiables defined in a yaml object. """

        for rt_name, id_list in identifiable_data.items():
            rt = db.RecordType().add_parent(rt_name)
            if not isinstance(id_list, list):
                raise InvalidIdentifiableYAML(
                    f"Identifiable contents must be lists, but this was not: {rt_name}")
            for prop_name in id_list:
                if isinstance(prop_name, str):
                    rt.add_property(name=prop_name)
                elif isinstance(prop_name, dict):
                    for k, v in prop_name.items():
                        if k == "is_referenced_by" and not isinstance(v, list):
                            raise InvalidIdentifiableYAML(
                                f"'is_referenced_by' must be a list.  Found in: {rt_name}")
                        rt.add_property(name=k, value=v)
                else:
                    raise InvalidIdentifiableYAML(
                        "Identifiable properties must be str or dict, but this one was not:\n"
                        f"    {rt_name}/{prop_name}")

            self.register_identifiable(rt_name, rt)

    def register_identifiable(self, name: str, definition: db.RecordType):
        self._registered_identifiables[name.lower()] = definition

    def get_file(self, identifiable: Identifiable):
        warnings.warn(
            DeprecationWarning("This function is deprecated. Please do not use it.")
        )
        # TODO is this needed for Identifiable?
        # or can we get rid of this function?
        if isinstance(identifiable, db.Entity):
            return cached_get_entity_by(path=identifiable)
        if identifiable.path is None:
            raise RuntimeError("Path must not be None for File retrieval.")
        candidates = cached_get_entity_by(path=identifiable.path)
        if len(candidates) > 1:
            raise RuntimeError("Identifiable was not defined unambigiously.")
        if len(candidates) == 0:
            return None
        return candidates[0]

    def get_registered_identifiable(self, record: db.Entity):
        """
        returns the registered identifiable for the given Record

        It is assumed, that there is exactly one identifiable for each RecordType. Only the first
        parent of the given Record is considered; others are ignored
        """
        if len(record.parents) == 0:
            return None
        registered = []
        for parent in record.parents:
            prt = _retrieve_RecordType(id=parent.id, name=parent.name)
            reg = self._get_registered_for_rt(prt)
            if reg is not None:
                registered.append(reg)
        # TODO we might in future want to check whether the registered identifiables are the same
        if len(registered) > 1:
            raise RuntimeError("Multiple registered identifiables found for a Record "
                               f"with the following parents: {record.parents}")
        elif len(registered) == 1:
            return registered[0]
        else:
            return None

    def _get_registered_for_rt(self, rt: db.RecordType):
        """
        returns the registered identifiable for the given RecordType or the
        registered identifiable of the first parent
        """
        if rt.name.lower() in self._registered_identifiables:
            return self._registered_identifiables[rt.name.lower()]
        if len(rt.parents) == 0:
            return None
        registered = []
        for parent in rt.parents:
            prt = _retrieve_RecordType(id=parent.id, name=parent.name)
            reg = self._get_registered_for_rt(prt)
            if reg is not None:
                registered.append(reg)
        # TODO we might in future want to check whether the registered identifiables are the same
        if len(registered) > 1:
            ri_names = [i.name for i in registered]
            raise RuntimeError(f"Multiple registered identifiables found for the RecordType "
                               f" {rt.name} with the following parents: {rt.parents}\n"
                               f"Registered identifiables: {', '.join(ri_names)}")
        elif len(registered) == 1:
            return registered[0]
        else:
            return None

    def retrieve_identified_record_for_identifiable(self, identifiable: Identifiable):
        query_string = self.create_query_for_identifiable(identifiable)
        try:
            candidates = cached_query(query_string)
        except db.exceptions.HTTPServerError:
            query_string = self.create_query_for_identifiable(
                identifiable, startswith=True
            )
            candidates = cached_query(
                query_string
            ).copy()  # Copy against cache poisoning

            # Test if the candidates really match all properties
            for pname, pvalue in identifiable.properties.items():
                popme = []
                for i in range(len(candidates)):
                    this_prop = candidates[i].get_property(pname)
                    if this_prop is None:
                        popme.append(i)
                        continue
                    if not this_prop.value == pvalue:
                        popme.append(i)
                for i in reversed(popme):
                    candidates.pop(i)

        if len(candidates) > 1:
            raise RuntimeError(
                f"Identifiable was not defined unambiguously.\n{query_string}\nReturned the "
                f"following {candidates}."
                f"Identifiable:\n{identifiable.record_type}{identifiable.properties}"
            )
        if len(candidates) == 0:
            return None
        return candidates[0]
