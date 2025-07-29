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

import warnings

import lxml.etree


class StructureElement(object):
    """Base class for elements in the hierarchical data structure.

Parameters
----------

name: str
  The name of the StructureElement.  May be used for pattern matching by CFood rules.
    """

    def __init__(self, name: str):
        # Used to store usage information for debugging:
        self.metadata: dict[str, set[str]] = {
            "usage": set()
        }

        self.name = name

    def __str__(self):
        return self.get_name()

    def get_name(self):
        return self.name


class FileSystemStructureElement(StructureElement):
    """StructureElement representing an element of a file system, like a directory or a simple file.

Parameters
----------

name: str
  The name of the StructureElement.  May be used for pattern matching by CFood rules.

path: str
  The path to the file or directory.
    """

    def __init__(self, name: str, path: str):
        super().__init__(name)
        self.path = path

    def __str__(self):
        class_name_short = str(self.__class__).replace(
            "<class \'", "")[:-2]
        return "{}: {}, {}".format(class_name_short, self.name, self.path)


class NoneElement(StructureElement):
    pass


class Directory(FileSystemStructureElement):
    pass


class File(FileSystemStructureElement):
    """StrutureElement representing a file."""
    pass


class JSONFile(File):
    pass


class DictElement(StructureElement):
    def __init__(self, name: str, value: dict):
        super().__init__(name)
        self.value = value


class TextElement(StructureElement):
    def __init__(self, name: str, value: str):
        super().__init__(name)
        self.value = value


class DictTextElement(TextElement):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning("This class is depricated. Please use TextElement."))
        super().__init__(*args, **kwargs)


class IntegerElement(StructureElement):
    def __init__(self, name: str, value: int):
        super().__init__(name)
        self.value = value


class DictIntegerElement(IntegerElement):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning("This class is depricated. Please use IntegerElement."))
        super().__init__(*args, **kwargs)


class BooleanElement(StructureElement):
    def __init__(self, name: str, value: bool):
        super().__init__(name)
        self.value = value


class DictBooleanElement(BooleanElement):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning("This class is depricated. Please use BooleanElement."))
        super().__init__(*args, **kwargs)


class ListElement(StructureElement):
    def __init__(self, name: str, value: list):
        super().__init__(name)
        self.value = value


class DictListElement(ListElement):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning("This class is depricated. Please use ListElement."))
        super().__init__(*args, **kwargs)


class FloatElement(StructureElement):
    def __init__(self, name: str, value: float):
        super().__init__(name)
        self.value = value


class DictFloatElement(FloatElement):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning("This class is depricated. Please use FloatElement."))
        super().__init__(*args, **kwargs)


class Dict(DictElement):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning("This class is depricated. Please use DictElement."))
        super().__init__(*args, **kwargs)


class DictDictElement(DictElement):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning("This class is depricated. Please use DictElement."))
        super().__init__(*args, **kwargs)


class XMLTagElement(StructureElement):
    """
    Stores elements of an XML tree.
    """

    def __init__(self, element: lxml.etree.Element):
        super().__init__(element.getroottree().getelementpath(element))
        self.tag = element


class XMLTextNode(StructureElement):
    """
    Stores text nodes of XML trees.
    """

    def __init__(self, element: lxml.etree.Element):
        """
        Initializes this XML text node.

        Please note that, although syntactically similar, it is semantically
        different from TextElement:
        - TextElements have a meaningful name, e.g. a key in a key-value pair. This name can
          be matched using the match_name entry.
        - XMLTextNodes just have a text and the name is just for identifying the structure element.
          They can only be matched using the match entry in the XMLTextNodeConverter.
        """
        super().__init__(element.getroottree().getelementpath(element) + "/text()")
        self.tag = element
        self.value = element.text


class XMLAttributeNode(StructureElement):
    """
    Stores text nodes of XML trees.
    """

    def __init__(self, element: lxml.etree.Element,
                 key: str):
        """
        Initializes this XML attribute node.

        element: The xml tree element containing the attribute.
        key: The key which identifies the attribute in the list of attributes.
        """
        super().__init__(element.getroottree().getelementpath(element) + "@" + key)
        self.value = element.attrib[key]
        self.key = key
        self.tag = element
