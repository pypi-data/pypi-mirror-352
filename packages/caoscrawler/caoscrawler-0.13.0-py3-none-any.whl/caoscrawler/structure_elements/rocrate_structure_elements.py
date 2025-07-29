#!/usr/bin/env python3
# encoding: utf-8
#
# ** header v3.0
# This file is a part of the CaosDB Project.
#
# Copyright (C) 2024 Alexander Schlemmer
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

from rocrate.model.entity import Entity

from .structure_elements import StructureElement


class ROCrateEntity(StructureElement):
    """
    Store entities contained in ROCrates.
    """

    def __init__(self, folder: str, entity: Entity):
        """
        Initializes this ROCrateEntity.

        Arguments:
        ----------
        folder: str
            The folder that contains the ROCrate data. In case of a zipped ROCrate, this
            is a temporary folder that the ROCrate was unzipped to.
            The folder is the folder containing the ro-crate-metadata.json.

        entity: Entity
            The ROCrate entity that is stored in this structure element.
            The entity automatically contains an attribute ".crate"
            that stores the ROCrate that this entity belongs to. It can be used
            e.g. to look up links to other entities (ROCrate.dereference).
        """
        super().__init__(entity.properties()["@id"])
        self.folder = folder
        self.entity = entity
