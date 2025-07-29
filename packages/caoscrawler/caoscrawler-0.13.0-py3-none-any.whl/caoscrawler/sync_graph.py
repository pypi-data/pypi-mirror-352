#!/usr/bin/env python3
# encoding: utf-8
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2024 Henrik tom Wörden
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

"""
A data model class for the graph of entities that shall be created during synchronization of the
crawler.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Callable, Optional, Union

import linkahead as db
from linkahead.cached import cached_get_entity_by
from linkahead.exceptions import EmptyUniqueQueryError

from .identifiable import Identifiable
from .identifiable_adapters import IdentifiableAdapter
from .sync_node import SyncNode, TempID

logger = logging.getLogger(__name__)


def _set_each_scalar_value(
    node: SyncNode, condition: Callable[[Any], bool], value: Any
):
    """helper function that conditionally replaces each value element of each property of a node

    If the property value is a list, the replacement is done for each list entry.
    The replacement is only performed if the condition that
    is provided is fulfilled, i.e. the callable ``condition`` returns True. The callable
    ``condition`` must take the property value (or list element) as the sole argument.

    Args:
        node (SyncNode): The node which provides the properties (and their values) to operate on.
        condition (Callable): A function with one argument which is interpreted as a condition:
                              Only if it returns True for the property value, the action is
                              executed.
        value (Callable): A function returning a new value that is set as the property value. This
                          function receives the old value as the single argument.

    Last review by Alexander Schlemmer on 2024-05-24.
    """
    for p in node.properties:
        if isinstance(p.value, list):
            for ii, el in enumerate(p.value):
                if condition(el):
                    p.value[ii] = value(el)
        elif condition(p.value):
            p.value = value(p.value)


class SyncGraph:
    """
    A data model class for the graph of entities that shall be created during synchronization of
    the crawler.

    The SyncGraph combines nodes in the graph based on their identity in order to create a graph of
    objects that can either be inserted or updated in(to) the remote server. This combination of
    SyncNodes happens during initialization and later on when the ID of SyncNodes is set.

    When the SyncGraph is initialized, the properties of given entities are scanned and used to
    create multiple reference maps that track how SyncNodes reference each other.
    These maps are kept up to date when SyncNodes are merged because they are identified with each
    other. During initialization, SyncNodes are first merged based on their ID, path or
    identifiable.

    When additional information is added to the graph by setting the ID of a node
    (via `set_id_of_node`) then the graph is updated accordingly:
    - if this information implies that the node is equivalent to another node (e.g. has same ID),
      then they are merged
    - if knowing that one node does not exist in the remote server, then this might imply that some
      other node also does not exist if its identity relies on the latter.
    - The new ID might make it possible to create the identifiables of connected nodes and thus
      might trigger further merging of nodes based on the new identifiables.

    A SyncGraph should only be manipulated via one function:
    - set_id_of_node: a positive integer means the Entity exists, None means it is missing
    TODO what about String IDs

    The SyncGraph can be converted back to lists of entities which allow to perform the desired
    inserts and updates.

    Usage:
    - Initialize the Graph with a list of entities. Those will be converted to the SyncNodes of the
      graph.
    - SyncNodes that can be merged are automatically merged and SyncNodes where the existence can
      be determined are automatically removed from the list of unchecked SyncNodes:
      graph.unchecked.
    - You manipulate the graph by setting the ID of a SyncNode (either to a valid ID or to None).
      For example, you can check whether a SyncNode has an identifiable and then query the remote
      server and use the result to set the ID.
    - After each manipulation, the graph updates accordingly (see above)
    - Ideally, the unchecked list is empty after some manipulation.
    - You can export a list of entities to be inserted and one of entities to be updated with
      export_record_lists.

    Last review by Alexander Schlemmer on 2024-05-24.
    """

    # General implementation remark:
    # There are three cases where an update of one SyncNode can affect other nodes:
    # - mark existing (add identifiables)
    # - mark missing (add identifiables and add (negative) IDs)
    # - merge (add identifiables)
    #
    # We cannot get an infinite recursion where one update triggers another update and so on
    # because updates are conditional:
    # Setting an ID removes the node (immediately) from the unchecked list and it is only tried to
    # set an ID in _mark_missing if a node is in the uncheck list. Thus, setting the ID once
    # prevents future attempts to set the ID of the same node.
    # Also, setting an identifiable is only done when needed, i.e. there is no identifiable.
    # Note, that when ever one node is changed, we check all dependent nodes (see usage of
    # `_get_nodes_whose_identity_relies_on`) whether something should be updated. Thus, we cannot
    # miss a necessary update.
    def __init__(
        self, entities: list[db.Entity], identifiableAdapter: IdentifiableAdapter
    ):
        self.identifiableAdapter = identifiableAdapter
        # A dictionary allowing for quick lookup of sync nodes using their (possibly negative) IDs.
        # This dictionary is initially set using _mark_entities_with_path_or_id and later updated
        # using set_id_of_node or during merges of nodes.
        self._id_look_up: dict[Union[int, TempID, str], SyncNode] = {}
        # Similar as above for looking up nodes using paths
        self._path_look_up: dict[str, SyncNode] = {}
        # Similar as above for looking up nodes using identifiables. This dictionary uses the text
        # representation generated by get_representation method of Identifiable as keys.
        self._identifiable_look_up: dict[str, SyncNode] = {}
        # look up for the nodes that were marked as being missing (on the remote server)
        self._missing: dict[int, SyncNode] = {}
        # same for existing
        self._existing: dict[int, SyncNode] = {}
        # entities that are missing get negative IDs to allow identifiable creation
        self._remote_missing_counter = -1

        self.nodes: list[SyncNode] = []
        self._initialize_nodes(entities)  # list of all SemanticEntities
        # list all SemanticEntities that have not yet been checked
        self.unchecked = list(self.nodes)

        # initialize reference mappings (see _create_reference_mapping)
        (
            self.forward_references,  # id(node) -> full set of nodes referenced by the given node
            self.backward_references,  # id(node) -> full set of nodes referencing the given node
            # as above, subset where the reference properties are part of identifiables
            self.forward_references_id_props,
            self.backward_references_id_props,
            # as above, subset where references are part of identifiables due to "referenced_by"
            self.forward_references_backref,
            self.backward_references_backref,
        ) = self._create_reference_mapping(self.nodes)

        # remove entities with path or ID from unchecked list
        self._mark_entities_with_path_or_id()

        # add identifiables where possible
        for node in list(self.nodes):
            if self._identifiable_is_needed(node):
                self._set_identifiable_of_node(node)

        # everything in unchecked neither does have an ID nor a path.
        # Thus, it must be possible to create an
        # identifiable which is checked using the following function:
        for node in self.unchecked:
            self.identifiableAdapter.all_identifying_properties_exist(node)

    def set_id_of_node(self, node: SyncNode, node_id: Optional[str] = None):
        """sets the ID attribute of the given SyncNode to node_id.

        If node_id is None, a negative ID will be
        given indicating that the node does not exist on the remote server.
        Furthermore it will be marked as missing using _mark_missing.

        Last review by Alexander Schlemmer on 2024-05-24.
        """
        if node.id is not None:
            raise RuntimeError(
                "Cannot update ID.\n"
                f"It already is {node.id} and shall be set to {node_id}."
            )
        if node_id is None:
            node_id = TempID(self._get_new_id())
        node.id = node_id
        if node_id in self._id_look_up:
            self._merge_into(node, self._id_look_up[node.id])
        else:
            self._id_look_up[node.id] = node
            if isinstance(node.id, TempID):
                self._mark_missing(node)
            else:
                self._mark_existing(node)

    def export_record_lists(self):
        """exports the SyncGraph in form of db.Entities

        All nodes are converted to db.Entity objects and reference values that are SyncNodes are
        replaced by their corresponding (newly created) db.Entity objects.

        Since the result is returned in form of two lists, one with Entities that have a valid ID
        one with those that haven't, an error is raised if there are any SyncNodes without an
        (possibly negative) ID.

        Last review by Alexander Schlemmer on 2024-05-24.
        """
        # TODO reactivate once the implementation is appropriate
        # if len(self.unchecked) > 1:
        # self.unchecked_contains_circular_dependency()

        for el in self.nodes:
            if el.id is None:
                raise RuntimeError("Exporting unchecked entities is not supported")

        entities = []
        node_map = {}
        for el in self.nodes:
            entities.append(el.export_entity())
            node_map[id(el)] = entities[-1]

        for ent in entities:
            _set_each_scalar_value(
                ent,
                condition=lambda val: isinstance(val, SyncNode),
                value=lambda val: node_map[id(val)],
            )

        missing = [el for el in entities if el.id < 0]
        existing = [el for el in entities if el.id > 0]
        # remove negative IDs
        for el in missing:
            el.id = None

        return (missing, existing)

    def handle_negative_ids(self, entities: list[db.Entity]):
        """Find the lowest negative ID in ``entities`` and adapt ``_remote_missing_counter``.

        After this method has been called, ``self._remote_missing_counter`` will be smaller than the
        lowest negative ID.  The counter will never be increased.


        Parameters
        ----------
        entities : list[db.Entity]
          The entities to be checked.
        """

        smallest = 0
        for ent in entities:
            if isinstance(ent.id, int):
                # if ent.id < 0:
                #     raise ValueError("Negative ID")
                smallest = min(smallest, ent.id)
            elif isinstance(ent.id, str) and re.match(r"^-\d+$", ent.id):
                smallest = min(smallest, int(ent.id))
        if smallest <= self._remote_missing_counter:
            self._remote_missing_counter = smallest - 1

    def _identity_relies_on_unchecked_entity(self, node: SyncNode):
        """
        If a record for which it could not yet be verified whether it exists in LA or not is part
        of the identifying properties, this returns True, otherwise False

        Last review by Alexander Schlemmer on 2024-05-27.
        """

        return any(
            [
                id(ent) not in self._missing and id(ent) not in self._existing
                for ent in self.forward_references_id_props[id(node)]
            ]
            + [
                id(ent) not in self._missing and id(ent) not in self._existing
                for ent in self.backward_references_backref[id(node)]
            ]
        )

    def unchecked_contains_circular_dependency(self):
        """
        Detects whether there are circular references in the given entity list and returns a list
        where the entities are ordered according to the chain of references (and only the entities
        contained in the circle are included. Returns None if no circular dependency is found.

        TODO: for the sake of detecting problems for split_into_inserts_and_updates we should only
        consider references that are identifying properties.
        """
        raise NotImplementedError("This function is not yet properly implemented")
        # TODO if the first element is not part of the circle, then
        # this will not work
        # We must created a better implementation (see also TODO in docstring)
        circle = [self.unchecked[0]]
        closed = False
        while not closed:
            added_to_circle = False
            for referenced in self.forward_references[id(circle[-1])]:
                if referenced in self.unchecked:
                    if referenced in circle:
                        closed = True
                    circle.append(referenced)
                    added_to_circle = True
            if not added_to_circle:
                return None
        return circle

    def get_equivalent(self, entity: SyncNode) -> Optional[SyncNode]:
        """
        Return an equivalent SyncNode.

        Equivalent means that ID, path or identifiable are the same.
        If a new information was added to the given SyncNode (e.g. the ID), it might be possible
        then to identify an equivalent node (i.e. one with the same ID in this example).
        There might be more than one equivalent node in the graph. However, simply the first that
        is found is being returned. (When an equivalent node is found, the given node is
        typically merged, into the one that was found and after the merge the graph is again
        checked for equivalent nodes.)

        Returns None if no equivalent node is found.

        Last review by Alexander Schlemmer on 2024-05-28.
        """
        if entity.id is not None and entity.id in self._id_look_up:
            candidate = self._id_look_up[entity.id]
            if candidate is not entity:
                return candidate
        if entity.path is not None and entity.path in self._path_look_up:
            candidate = self._path_look_up[entity.path]
            if candidate is not entity:
                return candidate
        if (
            entity.identifiable is not None
            and entity.identifiable.get_representation() in self._identifiable_look_up
        ):
            candidate = self._identifiable_look_up[
                entity.identifiable.get_representation()
            ]
            if candidate is not entity:
                return candidate
        return None

    def _get_new_id(self):
        """returns the next unused temporary ID

        Last review by Alexander Schlemmer on 2024-05-24.
        """
        self._remote_missing_counter -= 1
        return self._remote_missing_counter

    def _set_identifiable_of_node(
        self, node: SyncNode, identifiable: Optional[Identifiable] = None
    ):
        """sets the identifiable and checks whether an equivalent node can be found with that new
        information. If an equivalent node is found, 'node' is merged into that node.

        if no identifiable is given, the identifiable is retrieved from the identifiable adapter

        Raises a ValueError if the equivalent node found does not have an identifiable.
        Raises a RuntimeError if there is no equivalent node found and
          the (unique) string representation of the identifiable of node is already contained in
          the identifiable_look_up.

        Last review by Alexander Schlemmer on 2024-05-29.
        """
        if identifiable is None:
            self.identifiableAdapter.all_identifying_properties_exist(node)
            identifiable = self.identifiableAdapter.get_identifiable(
                node, self.backward_references_backref[id(node)]
            )
        node.identifiable = identifiable
        equivalent_se = self.get_equivalent(node)
        if equivalent_se is not None:
            self._merge_into(node, equivalent_se)
        else:
            if node.identifiable.get_representation() in self._identifiable_look_up:
                raise RuntimeError("Identifiable is already in the look up")
            self._identifiable_look_up[node.identifiable.get_representation()] = node

    @staticmethod
    def _sanity_check(entities: list[db.Entity]):
        """
        Checks whether each record in entities has at least one parent.

        Last review by Alexander Schlemmer on 2024-05-24.
        """
        for ent in entities:
            if ent.role == "Record" and len(ent.parents) == 0:
                raise ValueError(f"Records must have a parent.\n{ent}")

    def _get_nodes_whose_identity_relies_on(self, node: SyncNode):
        """returns a set of nodes that reference the given node as identifying property or are
        referenced by the given node and the parent of the given node is listed as
        "is_referenced_by"

        Last review by Alexander Schlemmer on 2024-05-24.
        """
        return self.backward_references_id_props[id(node)].union(
            self.forward_references_backref[id(node)]
        )

    @staticmethod
    def _create_flat_list(
        ent_list: list[db.Entity], flat: Optional[list[db.Entity]] = None
    ):
        """
        Recursively adds entities and all their properties contained in ent_list to
        the output list flat.

        TODO: This function will be moved to pylib as it is also needed by the
              high level API.

        Last review by Alexander Schlemmer on 2024-05-29.
        """
        # Note: A set would be useful here, but we do not want a random order.
        if flat is None:
            flat = list()
        for el in ent_list:
            if el not in flat:
                flat.append(el)
        for ent in ent_list:
            for p in ent.properties:
                # For lists append each element that is of type Entity to flat:
                if isinstance(p.value, list):
                    for el in p.value:
                        if isinstance(el, db.Entity):
                            if el not in flat:
                                flat.append(el)
                                SyncGraph._create_flat_list([el], flat)
                elif isinstance(p.value, db.Entity):
                    if p.value not in flat:
                        flat.append(p.value)
                        SyncGraph._create_flat_list([p.value], flat)
        return flat

    @staticmethod
    def _create_reference_mapping(flat: list[SyncNode]):
        """
        Create six dictionaries that describe references among SyncNodes. All dictionaries use the
        Python ID of SyncNodes as keys.
        There is always one dictionary to describe the direction of the reference, i.e.
        map[id(node)] -> other where other is a set of SyncNodes that are being referenced by node.
        And then there is always one dictionary for the inverse direction. The two dictionaries are
        named "forward_" and "backward_", respectively.

        Then there are three kinds of maps being generated: One includes all references
        ("_references"), one includes references that are values of identifying properties
        ("_references_id_props") and one includes references that are relevant for identifying
        backreferences/"is_referenced_by" ("_references_backref"). I.e. the two latter are subesets
        of the former reference map.

        Arguments:
        ----------
           flat: list[SyncNode]
                 all SyncNodes that span the graph for which the reference map shall be created

        Last review by Alexander Schlemmer on 2024-05-29.
        """
        # TODO we need to treat children of RecordTypes somehow.
        forward_references: dict[int, set[SyncNode]] = {}
        backward_references: dict[int, set[SyncNode]] = {}
        forward_references_id_props: dict[int, set[SyncNode]] = {}
        backward_references_id_props: dict[int, set[SyncNode]] = {}
        forward_references_backref: dict[int, set[SyncNode]] = {}
        backward_references_backref: dict[int, set[SyncNode]] = {}

        # initialize with empty lists/dict
        for node in flat:
            forward_references[id(node)] = set()
            backward_references[id(node)] = set()
            forward_references_id_props[id(node)] = set()
            backward_references_id_props[id(node)] = set()
            forward_references_backref[id(node)] = set()
            backward_references_backref[id(node)] = set()
        for node in flat:
            for p in node.properties:
                val = p.value
                if not isinstance(val, list):
                    val = [val]
                for v in val:
                    if isinstance(v, SyncNode):
                        forward_references[id(node)].add(v)
                        backward_references[id(v)].add(node)
                        if (
                            node.registered_identifiable is not None
                            and len(
                                [
                                    el.name
                                    for el in node.registered_identifiable.properties
                                    if el.name == p.name
                                ]
                            )
                            > 0
                        ):
                            forward_references_id_props[id(node)].add(v)
                            backward_references_id_props[id(v)].add(node)
                        if (
                            v.registered_identifiable is not None
                            and IdentifiableAdapter.referencing_entity_has_appropriate_type(
                                node.parents, v.registered_identifiable
                            )
                        ):
                            forward_references_backref[id(node)].add(v)
                            backward_references_backref[id(v)].add(node)

        return (
            forward_references,
            backward_references,
            forward_references_id_props,
            backward_references_id_props,
            forward_references_backref,
            backward_references_backref,
        )

    def _mark_entities_with_path_or_id(self):
        """A path or an ID is sufficiently identifying. Thus, those entities can be marked as
        checked

        When this function returns, there is only one node for each ID (i.e. no two nodes with the
        same ID). The same is true for paths.

        This function also updates _id_look_up and _path_look_up

        Last review by Alexander Schlemmer on 2024-05-29.
        """
        for node in list(self.nodes):
            if node.id is not None:
                eq_node = self.get_equivalent(node)
                if eq_node is not None:
                    self._basic_merge_into(node, eq_node)
                else:
                    self._id_look_up[node.id] = node
                    self._mark_existing(node)

        for node in list(self.nodes):
            if node.path is not None:
                eq_node = self.get_equivalent(node)
                if eq_node is not None:
                    self._basic_merge_into(node, eq_node)
                else:
                    self._path_look_up[node.path] = node
                    try:
                        existing = cached_get_entity_by(path=node.path)
                    except EmptyUniqueQueryError:
                        existing = None
                    remote_id = None
                    if existing is not None:
                        remote_id = existing.id
                    self.set_id_of_node(node, remote_id)

    def _basic_merge_into(self, source: SyncNode, target: SyncNode):
        """tries to merge source into target and updates member variables

        - reference maps are updated
        - self.nodes is updated
        - self.unchecked is updated
        - lookups are being updated
        """
        # sanity checks
        if source is target:
            raise ValueError("source must not be target")

        target.update(source)

        # replace actual reference property values
        for node in self.backward_references[id(source)]:
            _set_each_scalar_value(
                node, condition=lambda val: val is source, value=lambda val: target
            )

        # update reference mappings
        for setA, setB in (
            (self.forward_references, self.backward_references),  # ref: source -> other
            (self.backward_references, self.forward_references),  # ref: other -> source
            (self.forward_references_id_props, self.backward_references_id_props),
            (self.backward_references_id_props, self.forward_references_id_props),
            (self.forward_references_backref, self.backward_references_backref),
            (self.backward_references_backref, self.forward_references_backref),
        ):
            for node in setA.pop(id(source)):
                setA[id(target)].add(node)
                setB[id(node)].remove(source)
                setB[id(node)].add(target)

        # remove unneeded SyncNode
        self.nodes.remove(source)
        if source in self.unchecked:
            self.unchecked.remove(source)
        # update look ups
        if target.id is not None:
            self._id_look_up[target.id] = target
        if target.path is not None:
            self._path_look_up[target.path] = target
        if target.identifiable is not None:
            self._identifiable_look_up[target.identifiable.get_representation()] = target

    def _merge_into(self, source: SyncNode, target: SyncNode):
        """tries to merge source into target and performs the necessary updates:
        - update the member variables of target using source (``target.update(source)``).
        - replaces reference values to source by target
        - updates the reference map
        - updates lookup tables
        - removes source from node lists
        - marks target as missing/existing if source was marked that way
        - adds an identifiable if now possible (e.g. merging based on ID might allow create an
          identifiable when none of the two nodes had the sufficient properties on its own before)
        - check whether dependent nodes can now get an identifiable (the merge might have set the
          ID such that dependent nodes can now create an identifiable)

        Last review by Alexander Schlemmer on 2024-05-29.
        """
        self._basic_merge_into(source, target)

        if (id(source) in self._existing and id(target) in self._missing) or (
            id(target) in self._existing and id(source) in self._missing
        ):
            raise RuntimeError("Trying to merge missing and existing")

        if id(source) in self._missing and id(target) not in self._missing:
            self._mark_missing(target)
        elif id(source) in self._existing and id(target) not in self._existing:
            self._mark_existing(target)

        # due to the merge it might now be possible to create an identifiable
        if self._identifiable_is_needed(target):
            self._set_identifiable_of_node(target)
        # This is one of three cases that affect other nodes:
        # - mark existing
        # - mark missing
        # - merge
        self._add_identifiables_to_dependent_nodes(target)

        eq_node = self.get_equivalent(target)
        if eq_node is not None:
            self._merge_into(target, eq_node)

    def _identifiable_is_needed(self, node: SyncNode):
        """
        This function checks:
        - the identifiable of node is None
        - the node has all properties that are needed for the identifiable
        - there are no unchecked entities that are needed for the identifiable of the node,
          neither as forward or as backward references

        Last review by Alexander Schlemmer on 2024-05-24.
        """
        return (
            node.identifiable is None
            and not self._identity_relies_on_unchecked_entity(node)
            and self.identifiableAdapter.all_identifying_properties_exist(
                node, raise_exception=False
            )
        )

    def _initialize_nodes(self, entities: list[db.Entity]):
        """create initial set of SyncNodes from provided Entity list"""
        entities = self._create_flat_list(entities)
        self._sanity_check(entities)
        self.handle_negative_ids(entities)
        se_lookup: dict[int, SyncNode] = {}  # lookup: python id -> SyncNode

        # Create new sync nodes from the list of entities, their registered identifiables
        # are set from the identifiable adapter.
        for el in entities:
            self.nodes.append(
                SyncNode(el, self.identifiableAdapter.get_registered_identifiable(el))
            )
            se_lookup[id(el)] = self.nodes[-1]

        # replace db.Entity objects with SyncNodes in references:
        for node in self.nodes:
            _set_each_scalar_value(
                node,
                condition=lambda val: id(val) in se_lookup,
                value=lambda val: se_lookup[id(val)],
            )

    def _add_identifiables_to_dependent_nodes(self, node):
        """For each dependent node, we check whether this allows to create an identifiable

        Last review by Alexander Schlemmer on 2024-05-29.
        """
        for other_node in self._get_nodes_whose_identity_relies_on(node):
            if self._identifiable_is_needed(other_node):
                self._set_identifiable_of_node(other_node)

    def _mark_missing(self, node: SyncNode):
        """Mark a sync node as missing and remove it from the dictionary of unchecked nodes.

        Last review by Alexander Schlemmer on 2024-05-24.
        """
        self._missing[id(node)] = node
        self.unchecked.remove(node)

        # This is one of three cases that affect other nodes:
        # - mark existing
        # - mark missing
        # - merge
        self._add_identifiables_to_dependent_nodes(node)
        # For each dependent node, we set the ID to None (missing)
        # (None is the default second argument of set_id_of_node.)
        for other_node in self._get_nodes_whose_identity_relies_on(node):
            if other_node in self.unchecked:
                self.set_id_of_node(other_node)

    def _mark_existing(self, node: SyncNode):
        """Mark a sync node as existing and remove it from the dictionary of unchecked nodes.

        Last review by Alexander Schlemmer on 2024-05-24.
        """
        if isinstance(node.id, TempID):
            raise ValueError("ID must valid existing entities, not TempID")
        self._existing[id(node)] = node
        self.unchecked.remove(node)
        # This is one of three cases that affect other nodes:
        # - mark existing
        # - mark missing
        # - merge
        self._add_identifiables_to_dependent_nodes(node)
