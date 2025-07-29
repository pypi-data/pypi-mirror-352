# encoding: utf-8
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2024 Indiscale GmbH <info@indiscale.com>
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

"""Submodule containing all default and optional converters."""

from .. import utils
from .converters import *
from .xml_converter import *
from .zipfile_converter import ZipFileConverter

try:
    from .spss import SPSSConverter
except ImportError as err:
    SPSSConverter: type = utils.MissingImport(
        name="SPSSConverter", hint="Try installing with the `spss` extra option.",
        err=err)

try:
    from .rocrate import (ELNFileConverter, ROCrateConverter,
                          ROCrateEntityConverter)
except ImportError as err:
    ROCrateEntityConverter: type = utils.MissingImport(
        name="ROCrateEntityConverter", hint="Try installing with the `rocrate` extra option.",
        err=err)
    ROCrateConverter: type = utils.MissingImport(
        name="ROCrateConverter", hint="Try installing with the `rocrate` extra option.",
        err=err)
    ELNFileConverter: type = utils.MissingImport(
        name="ELNFileConverter", hint="Try installing with the `rocrate` extra option.",
        err=err)
