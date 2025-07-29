#!/usr/bin/env python3
# encoding: utf-8
#
# ** header v3.0
# This file is a part of the CaosDB Project.
#
# Copyright (C) 2023 Alexander Schlemmer <alexander.schlemmer@ds.mpg.de>
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
A structure containing debug tree information.
"""

from __future__ import annotations

from collections import defaultdict

import linkahead as db
import yaml
from importlib_resources import files
from jsonschema import validate
from linkahead.apiutils import (EntityMergeConflictError, compare_entities,
                                merge_entities)
from linkahead.common.datatype import is_reference

from .converters import Converter, ConverterValidationError, DirectoryConverter
from .macros import defmacro_constructor, macro_constructor
from .stores import GeneralStore, RecordStore, Store
from .structure_elements import Directory, NoneElement, StructureElement
from .version import check_cfood_version


class DebugTree(object):

    def __init__(self):
        # order in the tuple:
        # 0: general_store
        # 1: record_store
        self.debug_tree: dict[str, tuple] = dict()
        self.debug_metadata: dict[str, dict] = dict()
        self.debug_metadata["copied"] = dict()
        self.debug_metadata["provenance"] = defaultdict(lambda: dict())
        self.debug_metadata["usage"] = defaultdict(lambda: set())

        # TODO: turn the tuple into two individual elements
