#!/usr/bin/env python3
# encoding: utf-8
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2024 Henrik tom Wörden
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

from typing import TYPE_CHECKING, Any, Optional
from warnings import warn

import linkahead as db
import yaml
from linkahead.common.models import Parent, ParentList, PropertyList

from .exceptions import ImpossibleMergeError

if TYPE_CHECKING:
    from .identifiable import Identifiable


class TempID(int):
    """A special kind of int for negative temporary IDs.

    This allows to identify TempIDs in the presence of String IDs.
    A string ID might look like a negative integer.
    """
    pass


class SyncNode(db.Entity):
    """represents the information of an Entity as it shall be created in LinkAhead

    The following information is taken from an db.Entity object during initialization or when the
    object is updated using the `update` member function:
    - id
    - role
    - path
    - file
    - name
    - description
    - parents
    - properties

    Typically, this class is used in the following way:
    1. A SyncNode is initialized with a db.Entity object.
    2. The SyncNode object is possibly updated one or more times with other SyncNode objects.
    3. A db.Entity object is created (`export_entity`) that contains the combined information.
    """

    def __init__(
        self, entity: db.Entity, registered_identifiable: Optional[db.RecordType] = None,
        **kwargs
    ):
        super().__init__(name=entity.name,
                         id=entity.id,
                         description=entity.description,
                         **kwargs)
        # db.Entity properties
        self.role = entity.role
        self.path = entity.path
        self.file = entity.file
        self.parents = ParentList().extend(entity.parents)
        self.properties = PropertyList().extend(entity.properties)
        self._check_for_multiproperties()
        # other members
        self.identifiable: Optional[Identifiable] = None
        self.registered_identifiable = registered_identifiable

    def update(self, other: SyncNode) -> None:
        """Update this node with information of given ``other`` SyncNode.

        parents are added if they are not yet in the list properties
        are added in any case. This may lead to duplication of
        properties. We allow this duplication here and remove it when
        we create a db.Entity (export_entity function) because if
        property values are SyncNode objects, they might not be
        comparable (no ID, no identifiable) yet.

        Raises
        ------
        ValueError:
            The `other` SyncNode doesn't share identifiables with
            `this` SyncNode, so they can't be merged.
        ImpossibleMergeError:
            The two SyncNodes are incompatible in their attributes
            like "id", "role", "path", "file", "name", or
            "description".

        """

        if other.identifiable is not None and self.identifiable is not None:
            if (
                other.identifiable.get_representation()
                != self.identifiable.get_representation()
            ):
                raise ValueError(
                    "The SyncNode that is used with update must have an equivalent"
                    f" identifiable. I.e. you cannot merge entities with differing identifiables"
                    "The identifiables where:\n"
                    f"{self.identifiable._create_hashable_string(self.identifiable)}\n"
                    f"and\n{other.identifiable._create_hashable_string(other.identifiable)}."
                )

        if other.identifiable:
            self.identifiable = other.identifiable
        for attr in ["id", "role", "path", "file", "name", "description"]:
            if other.__getattribute__(attr) is not None:
                if self.__getattribute__(attr) is None:
                    self.__setattr__(attr, other.__getattribute__(attr))
                else:
                    if self.__getattribute__(attr) != other.__getattribute__(attr):
                        raise ImpossibleMergeError(
                            f"Trying to update {attr} but this would lead to an "
                            f"override of the value '{self.__getattribute__(attr)}' "
                            f"by the value '{other.__getattribute__(attr)}'",
                            pname=attr,
                            value_a=self.__getattribute__(attr),
                            value_b=other.__getattribute__(attr)
                        )
        for p in other.parents:
            if not parent_in_list(p, self.parents):
                self.parents.append(p)
        for p in other.properties:
            self.properties.append(p)

    def export_entity(self) -> db.Entity:
        """create a db.Entity object from this SyncNode

        Properties are only added once (based on id or name). If values do not match, an Error is
        raised. If values are SyncNode objects with IDs, they are considered equal if their IDs are
        equal.

        Raises
        ------
        RuntimeError:
            In case of a unsupported role, so no Entity can't be created.
        ImpossibleMergeError:
            In case of conflicting property values in this SyncNode.
        """
        ent = None
        if self.role == "Record":
            ent = db.Record()
        elif self.role == "File":
            ent = db.File()
        else:
            raise RuntimeError("Invalid role")
        for attr in ["id", "role", "path", "file", "name", "description"]:
            ent.__setattr__(attr, self.__getattribute__(attr))
        for p in self.parents:
            ent.add_parent(p)
        for p in self.properties:
            entval: Any = ent.get_property(p)
            if entval is None:
                ent.add_property(id=p.id, name=p.name, value=p.value, description=p.description,
                                 datatype=p.datatype, unit=p.unit)
            else:
                entval = entval.value
                unequal = False
                pval = p.value
                if isinstance(entval, list) != isinstance(pval, list):
                    unequal = True
                if not isinstance(entval, list):
                    entval = [entval]
                if not isinstance(pval, list):
                    pval = [pval]
                if len(entval) != len(pval):
                    unequal = True
                else:
                    for e_el, p_el in zip(entval, pval):
                        if isinstance(e_el, SyncNode) and e_el.id is not None:
                            e_el = e_el.id
                        if isinstance(p_el, SyncNode) and p_el.id is not None:
                            p_el = p_el.id
                        if e_el != p_el:
                            unequal = True

                if unequal:
                    ime = ImpossibleMergeError(
                        f"The crawler is trying to create an entity \n\n{self}\n\nbut there are "
                        "conflicting property values.",
                        pname=p.name, value_a=entval, value_b=pval
                    )
                    raise ime
        return ent

    def __repr__(self) -> str:
        """ somewhat concise text representation of the SyncNode """
        res = f"\n=====================================================\n{self.role}\n"
        res += yaml.dump(
            {
                "id": self.id,
                "name": self.name,
                "path": self.path,
                "parents": [el.name for el in self.parents],
            },
            allow_unicode=True,
        )
        res += "---------------------------------------------------\n"
        res += "properties:\n"
        d: dict[str, Any] = {}
        for p in self.properties:
            v = p.value
            d[p.name] = []
            if not isinstance(p.value, list):
                v = [v]
            for el in v:
                if isinstance(el, SyncNode):
                    d[p.name].append(
                        {
                            "id": el.id,
                            "name": el.name,
                            "path": el.path,
                            "parents": [e.name for e in el.parents],
                        }
                    )
                else:
                    d[p.name].append(el)

        return (
            res
            + yaml.dump(d, allow_unicode=True)
            + "=====================================================\n"
        )

    def _check_for_multiproperties(self):
        """ warns if multiproperties are present """
        ids = set()
        names = set()
        for p in self.properties:
            if p.name is not None:
                if p.name in names:
                    warn("Multiproperties are not supported by the crawler.")
                names.add(p.name)
            if p.id is not None:
                if p.id in ids:
                    warn("Multiproperties are not supported by the crawler.")
                ids.add(p.id)


def parent_in_list(parent: Parent, plist: ParentList) -> bool:
    """helper function that checks whether a parent with the same name or ID is in the plist"""
    return plist.filter_by_identity(parent)


def property_in_list(prop: db.Property, plist: PropertyList) -> bool:
    """helper function that checks whether a property with the same name or ID is in the plist"""
    return plist.filter_by_identity(prop)
