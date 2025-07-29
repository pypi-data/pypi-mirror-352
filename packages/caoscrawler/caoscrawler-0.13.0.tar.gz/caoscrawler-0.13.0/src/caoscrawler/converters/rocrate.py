# encoding: utf-8
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2024 Indiscale GmbH <info@indiscale.com>
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

"""Converters take structure elements and create Records and new structure elements from them.

This converter converts ro-crate files which may also be .eln-files.

"""

from __future__ import annotations

import os
import re
import tempfile
from typing import Optional
from zipfile import ZipFile

import rocrate
from rocrate.rocrate import ROCrate

from ..stores import GeneralStore
from ..structure_elements import (Directory, File, ROCrateEntity,
                                  StructureElement)
from .converters import Converter, SimpleFileConverter, convert_basic_element


class ROCrateConverter(SimpleFileConverter):

    """Convert ro-crate files / directories.
    """

    def setup(self):
        self._tempdir = None

    def cleanup(self):
        self._tempdir.cleanup()

    def typecheck(self, element: StructureElement):
        """
        Check whether the current structure element can be converted using
        this converter.
        """
        return isinstance(element, File) or isinstance(element, Directory)

    def match(self, element: StructureElement) -> Optional[dict]:
        m = re.match(self.definition["match"], element.name)
        if m is None:
            return None
        return m.groupdict()

    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        """
        Loads an ROCrate from an rocrate file or directory.

        Arguments:
        ----------
        element must be a File or Directory (structure element).

        Returns:
        --------
        A list with an ROCrateElement representing the contents of the .eln-file or None
        in case of errors.
        """

        if isinstance(element, File):
            self._tempdir = tempfile.TemporaryDirectory()
            with ZipFile(element.path) as zipf:
                zipf.extractall(self._tempdir.name)
            crate_path = self._tempdir.name
            crate = ROCrate(crate_path)
            entity_ls = []
            for ent in crate.get_entities():
                entity_ls.append(ROCrateEntity(crate_path, ent))
            return entity_ls
        elif isinstance(element, Directory):
            # This would be an unzipped .eln file
            # As this is possible for rocrate files, I think it is reasonable
            # to support it as well.
            raise NotImplementedError()
        else:
            raise ValueError("create_children was called with wrong type of StructureElement")
        return None


class ELNFileConverter(ROCrateConverter):

    """Convert .eln-Files
    See: https://github.com/TheELNConsortium/TheELNFileFormat

    These files are basically RO-Crates with some minor differences:
    - The ro-crate metadata file is not on top-level within the .eln-zip-container,
      but in a top-level subdirectory.
    """

    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        """
        Loads an ROCrate from an .eln-file or directory.

        This involves unzipping the .eln-file to a temporary folder and creating an ROCrate object
        from its contents.

        Arguments:
        ----------
        element must be a File or Directory (structure element).

        Returns:
        --------
        A list with an ROCrateElement representing the contents of the .eln-file or None
        in case of errors.
        """

        if isinstance(element, File):
            self._tempdir = tempfile.TemporaryDirectory()
            with ZipFile(element.path) as zipf:
                zipf.extractall(self._tempdir.name)
            cratep = os.listdir(self._tempdir.name)
            if len(cratep) != 1:
                raise RuntimeError(".eln file must contain exactly one folder")
            crate_path = os.path.join(self._tempdir.name, cratep[0])
            crate = ROCrate(crate_path)
            entity_ls = []
            for ent in crate.get_entities():
                entity_ls.append(ROCrateEntity(crate_path, ent))
            return entity_ls
        elif isinstance(element, Directory):
            # This would be an unzipped .eln file
            # As this is possible for rocrate files, I think it is reasonable
            # to support it as well.
            raise NotImplementedError()
        else:
            raise ValueError("create_children was called with wrong type of StructureElement")
        return None


class ROCrateEntityConverter(Converter):

    def typecheck(self, element: StructureElement):
        """
        Check whether the current structure element can be converted using
        this converter.
        """
        return isinstance(element, ROCrateEntity)

    def match(self, element: StructureElement) -> Optional[dict]:
        # See https://gitlab.indiscale.com/caosdb/src/caosdb-crawler/-/issues/145
        # for a suggestion for the design of the matching algorithm.
        if not isinstance(element, ROCrateEntity):
            raise TypeError("Element must be an instance of ROCrateEntity.")

        # Store the result of all individual regexp variable results:
        vardict = {}

        # TODO: I accidentally used "match_type" instead
        #       of "match_entity_type". This was completely
        #       unnoticed. So add it to schema and adapt tests.

        if "match_entity_type" in self.definition:
            entity_type = element.entity.type
            if isinstance(entity_type, list):
                # TODO: this seems to be a bug in kadi4mat RO-Crates
                #       ./ has type ['Dataset']
                #       instead of type 'Dataset'
                entity_type = entity_type[0]
            m_type = re.match(self.definition["match_entity_type"], entity_type)
            if m_type is None:
                return None
            vardict.update(m_type.groupdict())

        if not self.match_properties(element.entity.properties(), vardict):
            return None

        return vardict

    def create_children(self, generalStore: GeneralStore, element: StructureElement):

        children = []

        eprops = element.entity.properties()

        # Add the properties:
        for name, value in eprops.items():
            if isinstance(value, dict):
                # This is - according to the standard - only allowed, if it's flat, i.e.
                # it contains a single element with key == "@id" and the id as value which
                # is supposed to be dereferenced:
                if not (len(value) == 1 and "@id" in value):
                    raise RuntimeError("The JSON-LD is not flat.")
                dereferenced = element.entity.crate.dereference(value["@id"])
                if dereferenced is not None:
                    children.append(
                        ROCrateEntity(element.folder, dereferenced))
                else:
                    # This is just an external ID and will be added  as simple DictElement
                    children.append(convert_basic_element(value, name))
            else:
                children.append(convert_basic_element(value, name))

        # Add the files:
        if isinstance(element.entity, rocrate.model.file.File):
            path, name = os.path.split(eprops["@id"])
            children.append(File(name, os.path.join(element.folder, path, name)))

        # Parts of this entity are added as child entities:
        for sublist in ("hasPart", "variableMeasured"):
            if sublist in eprops:
                for p in eprops[sublist]:
                    children.append(
                        ROCrateEntity(element.folder, element.entity.crate.dereference(
                            p["@id"])))
        # TODO: See https://gitlab.indiscale.com/caosdb/src/caosdb-crawler/-/issues/195 for discussion.

        return children
