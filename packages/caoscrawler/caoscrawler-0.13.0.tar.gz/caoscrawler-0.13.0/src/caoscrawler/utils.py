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

# Some utility functions, e.g. for extending pylib.

import sys
from posixpath import join as posixjoin
from typing import Optional
from urllib.parse import urljoin

import linkahead as db


def has_parent(entity: db.Entity, name: str):
    """
    A simple check, whether a parent with the given name exists.

    There is a similar, however more complex function in package caosdb.
    """

    for parent in entity.parents:
        if parent.name == name:
            return True
    return False


def MissingImport(name: str, hint: str = "", err: Optional[Exception] = None) -> type:
    """Factory with dummy classes, which may be assigned to variables but never used."""
    def _error():
        error_msg = f"This class ({name}) cannot be used, because some libraries are missing."
        if hint:
            error_msg += "\n\n" + hint

        if err:
            print(error_msg, file=sys.stdout)
            raise RuntimeError(error_msg) from err
        raise RuntimeError(error_msg)

    class _Meta(type):
        def __getattribute__(cls, *args, **kwargs):
            _error()

        def __call__(cls, *args, **kwargs):
            _error()

    class _DummyClass(metaclass=_Meta):
        pass

    _DummyClass.__name__ = name

    return _DummyClass


def get_shared_resource_link(host_url, filename):
    """Return a link adress which is basically {host_url}/Shared/{filename}.

    Use urllib.parse.join and os.path.join to prevent missing or extra ``/`` and the like.

    """

    if not host_url.endswith('/'):
        # Fill with trailing '/' s. that urljoin doesn't remove the context root.
        host_url += '/'
    # Use posixjoin to always have '/' in links, even when running on
    # Windows systems.
    return urljoin(host_url, posixjoin("Shared/", filename))
