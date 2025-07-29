#!/usr/bin/env python3
# encoding: utf-8
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2022 Henrik tom Wörden
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

from __future__ import annotations

import json
import logging
from datetime import datetime
from hashlib import sha256
from typing import Optional, Union

import linkahead as db

from .exceptions import MissingIdentifyingProperty
from .sync_node import SyncNode

logger = logging.getLogger(__name__)


class Identifiable():
    """
    The fingerprint of a Record in LinkAhead.

    This class contains the information that is used by the LinkAhead Crawler to identify Records.
    In order to check whether a Record exits in the LinkAhead Server, a query can
    be created using the information contained in the Identifiable.

    Parameters
    ----------
    record_type: str, this RecordType has to be a parent of the identified object
    name: str, the name of the identified object
    properties: dict, keys are names of Properties; values are Property values
                Note, that lists are not checked for equality but are interpreted as multiple
                conditions for a single Property.
    backrefs: list, TODO future
    """

    def __init__(self, record_id: Optional[int] = None, record_type: Optional[str] = None,
                 name: Optional[str] = None, properties: Optional[dict] = None,
                 backrefs: Optional[list[Union[int, str]]] = None):
        if (record_id is None and name is None
                and (backrefs is None or len(backrefs) == 0)
                and (properties is None or len(properties) == 0)):
            raise ValueError(
                "There is no identifying information. You need to add "
                "properties or other identifying attributes.")
        if properties is not None and 'name' in [k.lower() for k in properties.keys()]:
            raise ValueError("Please use the separete 'name' keyword instead of the properties "
                             "dict for name")
        self.record_id = record_id
        self.record_type = record_type
        self.name = name
        if name == "":
            self.name = None
        self.properties: dict = {}
        if properties is not None:
            self.properties = properties
        self.backrefs: list[Union[int, db.Entity]] = []
        if backrefs is not None:
            self.backrefs = backrefs

    def get_representation(self) -> str:
        return sha256(Identifiable._create_hashable_string(self).encode('utf-8')).hexdigest()

    @staticmethod
    def _value_representation(value) -> str:
        """returns the string representation of property values to be used in the hash function

        The string is the LinkAhead ID in case of SyncNode objects (SyncNode objects must have an ID)
        and the string representation of None, bool, float, int, datetime and str.
        """

        if value is None:
            return "None"
        elif isinstance(value, SyncNode):
            if value.id is not None:
                return str(value.id)
            else:
                raise RuntimeError("Python Entity (SyncNode) without ID not allowed")
        elif isinstance(value, list):
            return "[" + ", ".join([Identifiable._value_representation(el) for el in value]) + "]"
        elif (isinstance(value, str) or isinstance(value, int) or isinstance(value, float)
              or isinstance(value, datetime)):
            return str(value)
        else:
            raise ValueError(f"Unknown datatype of the value: {value}")

    @staticmethod
    def _create_hashable_string(identifiable: Identifiable) -> str:
        """
        creates a string from the attributes of an identifiable that can be hashed
        String has the form "P<parent>N<name>R<reference-ids>a:5b:10"
        """
        rec_string = "P<{}>N<{}>R<{}>".format(
            identifiable.record_type,
            identifiable.name,
            [Identifiable._value_representation(el) for el in identifiable.backrefs])
        # TODO this structure neglects Properties if multiple exist for the same name
        for pname in sorted(identifiable.properties.keys()):
            rec_string += ("{}:".format(pname) +
                           Identifiable._value_representation(identifiable.properties[pname]))
        return rec_string

    def __eq__(self, other) -> bool:
        """ Identifiables are equal if they share the same ID or if the representation is equal """
        if not isinstance(other, Identifiable):
            raise ValueError("Identifiable can only be compared to other Identifiable objects.")
        if self.record_id is not None and other.record_id is not None:
            return self.record_id == other.record_id
        elif self.get_representation() == other.get_representation():
            return True
        else:
            return False

    def __repr__(self):
        """ deterministic text representation of the identifiable """
        pstring = json.dumps({k: str(v) for k, v in self.properties.items()})
        return (f"{self.__class__.__name__} for RT {self.record_type}: id={self.record_id}; "
                f"name={self.name}\n"
                f"\tproperties:\n{pstring}\n"
                f"\tbackrefs:\n{self.backrefs}")
