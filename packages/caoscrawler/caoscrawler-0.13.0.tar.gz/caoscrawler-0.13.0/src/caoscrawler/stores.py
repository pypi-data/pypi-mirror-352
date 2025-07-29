#!/usr/bin/env python3
# encoding: utf-8
#
# ** header v3.0
# This file is a part of the CaosDB Project.
#
# Copyright (C) 2021 Henrik tom Wörden
#               2021 Alexander Schlemmer
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

from collections import defaultdict


class Store(object):
    """
    Base class for record store and general store which act as storages for
    records and values used during crawling.
    """

    def __init__(self):
        self._storage = dict()
        # This dict stores whether the corresponding dict item in _storage
        # (same key) has been copied from another Store, or was created newly in this store.
        self._copied = dict()
        # This attribute stores an internal id for being able to distinguish multiple
        # ocurrences of the same thing in the store:
        self._ids = defaultdict(lambda: 0)

    def __getitem__(self, key: str):
        return self._storage[key]

    def __contains__(self, key: str):
        return key in self._storage

    def __delitem__(self, key: str):
        del self._storage[key]
        del self._copied[key]

    def update(self, other: dict):
        self._storage.update(other)
        for key in other:
            self._copied[key] = False
            self._ids[key] += 1

    def __setitem__(self, key: str, value):
        self._storage[key] = value
        self._copied[key] = False
        self._ids[key] += 1

    def get_storage(self):
        return self._storage

    def create_scoped_copy(self):
        s_copy = self.__class__()
        s_copy._storage = dict(self._storage)
        s_copy._copied = {key: True for key in self._copied}
        s_copy._ids = self._ids
        return s_copy

    def get_dict_copied(self):
        """
        Only for debugging.
        """
        return self._copied

    def get_internal_id(self, key):
        """
        Only for debugging.
        """
        return self._ids[key]


class GeneralStore(Store):
    pass


class RecordStore(Store):

    def get_names_current_scope(self):
        """
        Return the names of all records that were created in the current scope.
        """
        lst = []

        for key in self._storage:
            if not self._copied[key]:
                lst.append(key)
        return lst

    def get_records_current_scope(self):
        """
        Return all records that were created in the current scope.
        """
        lst = []

        for key in self._storage:
            if not self._copied[key]:
                lst.append(self[key])
        return lst
