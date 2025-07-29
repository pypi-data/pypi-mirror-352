#!/usr/bin/env python3

# This file is a part of the LinkAhead project.
#
# Copyright (C) 2021 IndiScale GmbH <www.indiscale.com>
# Copyright (C) 2021 Henrik tom Wörden <h.tomwoerden@indiscale.com>
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

import linkahead as db
from linkahead.apiutils import resolve_reference
from linkahead.common.utils import uuid

from .cfood import (assure_has_description, assure_has_parent,
                    assure_property_is)

# The pylint warnings triggered in this file are ignored, as this code is
# assumed to be deprecated in the near future. Should this change, they need
# to be reevaluated.


class EntityMapping(object):
    """
    map local entities to entities on the server

    the dict to_existing maps _cuid property to entity objects
    the dict to_target maps id property to entity objects
    """

    def __init__(self):
        self.to_existing = {}
        self.to_target = {}

    def add(self, target, existing):
        if target.cuid is None:
            target._cuid = str(uuid())       # pylint: disable=protected-access
        self.to_existing[str(target.cuid)] = existing
        self.to_target[existing.id] = target


def collect_existing_structure(target_structure, existing_root, em):
    """ recursively collects existing entities

    The collected entities are those that correspond to the ones in
    target_structure.


    em: EntityMapping
    """

    for prop in target_structure.properties:
        if prop.value is None:
            continue

        if not prop.is_reference(server_retrieval=True):
            continue

        if (len([p for p in target_structure.properties if p.name == prop.name])
                != 1):
            raise ValueError("Current implementation allows only one property "
                             "for each property name")

        if (existing_root.get_property(prop.name) is not None and
                existing_root.get_property(prop.name).value is not None):
            resolve_reference(prop)

            resolve_reference(existing_root.get_property(prop.name))
            referenced = existing_root.get_property(prop.name).value

            if not isinstance(referenced, list):
                referenced = [referenced]
            target_value = prop.value

            if not isinstance(target_value, list):
                target_value = [target_value]

            if len(target_value) != len(referenced):
                raise ValueError()

            for tent, eent in zip(target_value, referenced):
                em.add(tent, eent)
                collect_existing_structure(tent, eent, em)


def update_structure(em, updating: db.Container, target_structure: db.Record):
    """compare the existing records with the target record tree created
    from the h5 object

    Parameters
    ----------

    existing_structure
        retrieved entity; e.g. the top level identifiable

    target_structure : db.Record
        A record which may have references to other records.  Must be a DAG.
    """

    if target_structure.cuid in em.to_existing:
        update_matched_entity(em,
                              updating,
                              target_structure,
                              em.to_existing[target_structure.cuid])

    for prop in target_structure.get_properties():
        if prop.is_reference(server_retrieval=True):
            update_structure(em, updating, prop.value)


def update_matched_entity(em, updating, target_record, existing_record):
    """
    update the Record existing in the server according to the Record
    supplied as target_record
    """

    for parent in target_record.get_parents():
        if parent.name == "":
            raise ValueError("Parent name must not be empty.")
        assure_has_parent(existing_record, parent.name, force=True)

    if target_record.description is not None:
        # check whether description is equal
        assure_has_description(existing_record, target_record.description,
                               to_be_updated=updating)

    for prop in target_record.get_properties():
        # check for remaining property types

        if isinstance(prop.value, db.Entity):
            if prop.value.cuid in em.to_existing:
                value = em.to_existing[prop.value.cuid].id
            else:
                value = prop.value.id
        else:
            value = prop.value
        assure_property_is(existing_record, prop.name, value,
                           to_be_updated=updating)
