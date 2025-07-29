#!/usr/bin/env python3
# encoding: utf-8
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2024 Indiscale GmbH <info@indiscale.com>
# Copyright (C) 2024 Henrik tom Wörden <h.tomwoerden@indiscale.com>
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

from typing import Any


class ForbiddenTransaction(Exception):
    """Thrown if an transactions is needed that is not allowed.
    For example an update of an entity if the security level is INSERT
    """
    pass


class ImpossibleMergeError(Exception):
    """Thrown if due to identifying information, two SyncNodes  or two Properties of SyncNodes
    should be merged, but there is conflicting information that prevents this.

    Parameters
    ----------
    msg : str
        A case-specific error message describing where the merger error occurred.
    pname : str
        The name of the property the values of which caused the merge error.
    value_a, value_b : Any
        The two values that couldn't be merged.

    Attributes
    ----------
    message : str
        A case-specific error message describing where the merger error occurred.
    values : tuple[Any]
        The two values that couldn't be merged.
    pname : str
        The name of the property the values of which caused the merge error.
    """

    def __init__(self, msg: str, pname: str, value_a: Any, value_b: Any):
        self.pname = pname
        self.values = (value_a, value_b)
        self.message = msg
        super().__init__(self, msg)

    def __str__(self):
        return (
            f"{self.message}\n\nThe problematic property is '{self.pname}' with "
            f"values '{self.values[0]}' and '{self.values[1]}'."
        )

    def __repr__(self):
        return self.__str__()


class InvalidIdentifiableYAML(Exception):
    """Thrown if the identifiable definition is invalid."""
    pass


class MissingIdentifyingProperty(Exception):
    """Thrown if a SyncNode does not have the properties required by the corresponding registered
    identifiable
    """
    pass


class MissingRecordType(Exception):
    """Thrown if an record type can not be found although it is expected that it exists on the
    server.
    """
    pass


class MissingReferencingEntityError(Exception):
    """Thrown if the identifiable requires that some entity references the given entity but there
    is no such reference """

    def __init__(self, *args, rts=None, **kwargs):
        self.rts = rts
        super().__init__(self, *args, **kwargs)
