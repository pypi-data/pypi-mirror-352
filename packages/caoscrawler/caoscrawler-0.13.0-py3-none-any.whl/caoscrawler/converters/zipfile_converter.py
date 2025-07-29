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

This converter opens zip files, unzips them into a temporary directory and
exposes its contents as File structure elements.

"""

from __future__ import annotations

import os
import tempfile
from os.path import isdir, join
from zipfile import ZipFile

from ..stores import GeneralStore
from ..structure_elements import Directory, File, StructureElement
from .converters import SimpleFileConverter


class ZipFileConverter(SimpleFileConverter):

    """Convert zipfiles.
    """

    def setup(self):
        self._tempdir = None

    def cleanup(self):
        self._tempdir.cleanup()

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
            unzd_path = self._tempdir.name
            with ZipFile(element.path) as zipf:
                zipf.extractall(unzd_path)

            entity_ls = []
            for el in os.listdir(unzd_path):
                path = join(unzd_path, el)
                if isdir(path):
                    entity_ls.append(Directory(el, path))
                else:
                    entity_ls.append(File(el, path))

            return entity_ls
        else:
            raise ValueError("create_children was called with wrong type of StructureElement")
        return None
