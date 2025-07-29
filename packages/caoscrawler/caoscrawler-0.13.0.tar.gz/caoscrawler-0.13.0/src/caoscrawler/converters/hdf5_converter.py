#
# This file is a part of the CaosDB Project.
#
# Copyright (C) 2023 IndiScale GmbH <info@indiscale.com>
# Copyright (C) 2023 Florian Spreckelsen <f.spreckelsen@indiscale.com>
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

from typing import Optional

try:
    import h5py
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "Couldn't find module h5py. Did you install the crawler package with "
        "its optional `h5-crawler` dependency?"
    )

from typing import Union

import linkahead as db
import numpy as np

from ..stores import GeneralStore, RecordStore
from ..structure_elements import (DictElement, File, FloatElement,
                                  IntegerElement, StructureElement)
from .converters import (Converter, DictElementConverter, SimpleFileConverter,
                         convert_basic_element, match_name_and_value)


def convert_attributes(elt: Union[h5py.File, h5py.Group, h5py.Dataset]):
    """Convert hdf5 attributes to a list of either basic scalar structure elements or ndarrays.

    Parameters
    ----------
    elt : Union[h5py.File, h5py.Group, h5py.Dataset]
        The hdf5 element the attributes of which will be converted to structure
        elements.

    Returns
    -------
    converted : list[StructureElement]
        A list of the attributes converted to StructureElements (either basic
        scalar elements or ndarray).
    """

    converted = []
    for name, value in elt.attrs.items():
        converted.append(convert_basic_element_with_nd_array(
            value, name, f"The value of attribute {name} has an unknown type: {type(value)}."))

    return converted


def convert_h5_element(elt: Union[h5py.Group, h5py.Dataset], name: str):
    """Convert a given HDF5 element to the corresponding StructureElement.

    Parameters
    ----------
    elt : Union[h5py.Group, h5py.Dataset]
        The hdf5 element to be converted.
    name : str
        The name of the StructureElement that the hdf5 element is converted to.

    Raises
    ------
    ValueError
        In case of anything that is not convertible to a HDF5 structure element.

    Returns
    -------
    StructureElement
        The converted StructureElement.
    """

    if isinstance(elt, h5py.Group):

        return H5GroupElement(name, elt)

    if isinstance(elt, h5py.Dataset):

        return H5DatasetElement(name, elt)

    raise ValueError("The given element must be either a HDF5 Group or Dataset object.")


def convert_basic_element_with_nd_array(value, name: Optional[str] = None,
                                        internal_path: Optional[str] = None, msg_prefix: str = ""):
    """Convert a given object either to an ndarray structure element or to a
    basic scalar structure element.

    This function extends :func:`~caoscrawler.converters.convert_basic_element`
    by a special treatment for certain numpy objects, most importantly
    ndarrays. They are converted to a scalar in case of a size-1 array, to a
    list in case of a 1-d array, and to a ``H5NdarrayElement`` in all other
    cases. In addition, numpy integers and floats are also converted to
    IntegerElements and FloatElements, respectively.

    Parameters
    ----------
    value
        The object to be converted.
    name : str, optional
        The name of the structure element ``value`` is being converted
        to. Default is None.
    internal_path : str, optional
        The internal path of ``value`` within the HDF5 file. Default is None.
    msg_prefix : str, optional
        The prefix of the error message that will be raised. Default is ``""``.

    Returns
    -------
    StructureElement
        The StructureElement ``value`` was converted to.

    """

    if isinstance(value, np.ndarray):

        if value.size == 1:
            # this is a scalar stacked in a numpy array. We don't know its
            # actual shape, so we reshape first, then use the actual value
            # inside.
            value = value.reshape((1,))[0]

        elif np.squeeze(value).ndim == 1:
            # If the array is one-dimensional we can save it as a list
            value = list(np.squeeze(value))

        else:
            # real multi-dimensional array
            return H5NdarrayElement(name, value, internal_path)

    elif isinstance(value, np.int32) or isinstance(value, np.int64):

        return IntegerElement(name, value)

    elif isinstance(value, np.float64):

        return FloatElement(name, value)

    return convert_basic_element(value, name, msg_prefix)


class H5GroupElement(DictElement):
    """StructureElement specific for HDF5 groups"""

    def __init__(self, name: str, value: h5py.Group):
        super().__init__(name, value)


class H5DatasetElement(DictElement):
    """StructureElement specific for HDF5 datasets."""

    def __init__(self, name: str, value: h5py.Dataset):
        super().__init__(name, value)


class H5NdarrayElement(DictElement):
    """StructureElement specific for NDArrays within HDF5 files.

    Also store the internal path of the array within the HDF5 file in its
    ``internal_path`` attribute.

    """

    def __init__(self, name: str, value, internal_path: str):
        super().__init__(name, value)
        self.internal_path = internal_path


class H5FileConverter(SimpleFileConverter):
    """Converter for HDF5 files that creates children for the contained
    attributes, groups, and datasets.

    """

    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        """Create children from root-level file attributes and contained hdf5
        elements.

        """

        if not isinstance(element, File):

            raise ValueError("create_children should have been called with a File object.")

        ff = h5py.File(element.path, 'r')

        children = []

        for name, value in ff.items():

            children.append(convert_h5_element(value, name))

        children.extend(convert_attributes(ff))

        return children


class H5GroupConverter(DictElementConverter):
    """Converter for HDF5 groups that creates children from the group-level
    attributes and the contained subgroups and datasets.

    """

    def typecheck(self, element: StructureElement):

        return isinstance(element, H5GroupElement)

    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        """Create children from group attributes and hdf5 elements contained in
        this group.

        """

        if not isinstance(element.value, h5py.Group):

            raise ValueError("create_children should have been called with a HDF5 Group object.")

        children = []

        for name, value in element.value.items():

            children.append(convert_h5_element(value, name))

        children.append(convert_attributes(element.value))

        return children


class H5DatasetConverter(DictElementConverter):
    """Converter for HDF5 datasets that creates children from the dataset
    attributes and the contained array data.

    """

    def typecheck(self, element: StructureElement):

        return isinstance(element, H5DatasetElement)

    def create_children(self, generalStore: GeneralStore, element: StructureElement):
        """Create children from the dataset attributes and append the array data
        contained in this dataset.

        """

        if not isinstance(element.value, h5py.Dataset):

            raise ValueError("create_children should have been called with a HDF5 Dataset object")

        children = convert_attributes(element.value)

        children.append(
            H5NdarrayElement(
                name=self.name+"_ndarray",
                value=element.value,
                internal_path=element.value.name
            )
        )
        return children


class H5NdarrayConverter(Converter):
    """Converter for ndarrays contained in HDF5 files. Creates the wrapper
    record for this ndarray.

    """

    def __init__(self, definition: dict, name: str, converter_registry: dict):

        # Check that a non-empty name for the record that will be created for
        # the ndarray Record (within the cfood) is given
        if not ("recordname" in definition and definition["recordname"]):

            raise RuntimeError(f"Converter {name} lacks the `recordname` definition.")

        super().__init__(definition, name, converter_registry)

    def create_children(self, values: GeneralStore, element: StructureElement):
        """The ndarray doesn't have any further children."""

        return []

    def create_records(self, values: GeneralStore, records: RecordStore, element: StructureElement):
        """Create a wrapper record with name ``recordname``, type
        ``array_recordtype_name`` (default ``H5Ndarray``) and the internal path
        stored in a property with name ``internal_path_property_name`` (default
        ``internal_hdf5_path``).

        """

        rname = self.definition["recordname"]
        if "array_recordtype_name" in self.definition:
            rtname = self.definition["array_recordtype_name"]
        else:
            rtname = "H5Ndarray"

        if "internal_path_property_name" in self.definition:
            propname = self.definition["internal_path_property_name"]
        else:
            propname = "internal_hdf5_path"

        rec = db.Record().add_parent(rtname)
        records[rname] = rec
        values[rname] = rec

        rec.add_property(name=propname, value=element.internal_path)
        keys_modified = [(rname, propname)]

        keys_modified.extend(super().create_records(values, records, element))

        return keys_modified

    def typecheck(self, element: StructureElement):

        return isinstance(element, H5NdarrayElement)

    @Converter.debug_matching("name")
    def match(self, element: StructureElement):

        if not isinstance(element, H5NdarrayElement):

            raise RuntimeError("This converter can only be called with H5NdarrayElements.")

        return match_name_and_value(self.definition, element.name, element.value)
