#!/usr/bin/env python
# encoding: utf-8
#
# ** header v3.0
# This file is a part of the LinkAhead project.
#
# Copyright (C) 2020 Indiscale GmbH <info@indiscale.com>
# Copyright (C) 2020 Henrik tom Wörden <h.tomwoerden@indiscale.com>
# Copyright (C) 2020 Florian Spreckelsen <f.spreckelsen@indiscale.com>
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

# Note: This is implementing a cache on client side. It would be great if the server would provide
# something to replace this.
import os
import sqlite3
import tempfile
import warnings
from abc import ABC, abstractmethod
from copy import deepcopy
from hashlib import sha256

import linkahead as db
from lxml import etree


def put_in_container(stuff):
    if isinstance(stuff, list):
        stuff = db.Container().extend(stuff)

    if not isinstance(stuff, db.Container):
        stuff = db.Container().append(stuff)

    return stuff


def cleanXML(xml):
    # remove transaction benchmark
    props = xml.findall('TransactionBenchmark')

    for prop in props:
        parent = prop.find("..")
        parent.remove(prop)

    return xml


def get_pretty_xml(cont):
    cont = put_in_container(cont)
    xml = cont.to_xml(local_serialization=True)
    cleanXML(xml)

    return etree.tounicode(xml, pretty_print=True)


class AbstractCache(ABC):
    def __init__(self, db_file=None, force_creation=False):
        """
        db_file: The path of the database file.

        if force_creation is set to True, the file will be created
        regardless of a file at the same path already exists.
        """

        if db_file is None:
            tmppath = tempfile.gettempdir()
            self.db_file = os.path.join(tmppath, self.get_default_file_name())
        else:
            self.db_file = db_file

        if not os.path.exists(self.db_file) or force_creation:
            self.create_cache()
        else:
            self.check_cache()

    @abstractmethod
    def get_cache_schema_version(self):
        """
        A method that has to be overloaded that sets the version of the
        SQLITE database schema. The schema is saved in table version column schema.

        Increase this variable, when changes to the cache tables are made.
        """

    @abstractmethod
    def create_cache(self):
        """
        Provide an overloaded function here that creates the cache in
        the most recent version.
        """

    @abstractmethod
    def get_default_file_name(self):
        """
        Supply a default file name for the cache here.
        """

    def check_cache(self):
        """
        Check whether the cache in db file self.db_file exists and conforms
        to the latest database schema.

        If it does not exist, it will be created using the newest database schema.

        If it exists, but the schema is outdated, an exception will be raised.
        """
        try:
            current_schema = self.get_cache_version()
        except sqlite3.OperationalError:
            current_schema = 1

        if current_schema > self.get_cache_schema_version():
            raise RuntimeError(
                "Cache is corrupt or was created with a future version of this program.")
        elif current_schema < self.get_cache_schema_version():
            raise RuntimeError("Cache version too old. Please remove the current cache file:\n"
                               + self.db_file)

    def get_cache_version(self):
        """
        Return the version of the cache stored in self.db_file.
        The version is stored as the only entry in colum schema of table version.
        """
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("SELECT schema FROM version")
            version_row = c.fetchall()

            if len(version_row) != 1:
                raise RuntimeError("Cache version table broken.")

            return version_row[0][0]
        finally:
            conn.close()

    def run_sql_commands(self, commands, fetchall: bool = False):
        """Run a list of SQL commands on self.db_file.

Parameters
----------

commands:
  List of sql commands (tuples) to execute

fetchall: bool, optional
  When True, run fetchall as last command and return the results.
  Otherwise nothing is returned.
        """
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        for sql in commands:
            c.execute(*sql)

        if fetchall:
            results = c.fetchall()
        conn.commit()
        conn.close()

        if fetchall:
            return results


class IdentifiableCache(AbstractCache):
    """
    stores identifiables (as a hash of xml) and their respective ID.

    This allows to retrieve the Record corresponding to an indentifiable
    without querying.
    """

    def get_cache_schema_version(self):
        return 2

    def get_default_file_name(self):
        return "caosdb_identifiable_cache.db"

    def create_cache(self):
        """
        Create a new SQLITE cache file in self.db_file.

        Two tables will be created:
        - identifiables is the actual cache.
        - version is a table with version information about the cache.
        """
        self.run_sql_commands([
            ('''CREATE TABLE identifiables (digest TEXT PRIMARY KEY, caosdb_id INTEGER, caosdb_version TEXT)''',),
            ('''CREATE TABLE version (schema INTEGER)''',),
            ("INSERT INTO version VALUES (?)", (self.get_cache_schema_version(),))])

    @staticmethod
    def hash_entity(ent):
        """
        Format an entity as "pretty" XML and return the SHA256 hash.
        """
        xml = get_pretty_xml(deepcopy(ent))
        digest = sha256(xml.encode("utf-8")).hexdigest()

        return digest

    def insert(self, ent_hash, ent_id, ent_version):
        """
        Insert a new cache entry.

        ent_hash: Hash of the entity. Should be generated with Cache.hash_entity
        ent_id: ID of the entity
        ent_version: Version string of the entity
        """
        self.run_sql_commands([
            ('''INSERT INTO identifiables VALUES (?, ?, ?)''',
             (ent_hash, ent_id, ent_version))])

    def check_existing(self, ent_hash):
        """
        Check the cache for a hash.

        ent_hash: The hash to search for.

        Return the ID and the version ID of the hashed entity.
        Return None if no entity with that hash is in the cache.
        """
        res = self.run_sql_commands([('''Select * FROM identifiables WHERE digest=?''',
                                      (ent_hash,))], True)

        if len(res) == 0:
            return None
        else:
            return res[0][1:]

    def update_ids_from_cache(self, entities):
        """ sets ids of those entities that are in cache

        A list of hashes corresponding to the entities is returned
        """
        hashes = []

        for ent in entities:
            ehash = Cache.hash_entity(ent)
            hashes.append(ehash)
            eid = self.check_existing(ehash)

            if eid is not None:
                ent.id = eid[0]

        return hashes

    def insert_list(self, hashes, entities):
        """ Insert the ids of entities into the cache

        The hashes must correspond to the entities in the list
        """

        # Check whether all entities have IDs and versions:

        for ent in entities:
            if ent.id is None:
                raise RuntimeError("Entity has no ID.")

            if ent.version is None or ent.version.id is None:
                raise RuntimeError("Entity has no version ID.")

        for ehash, ent in zip(hashes, entities):
            if self.check_existing(ehash) is None:
                self.insert(ehash, ent.id, ent.version.id)

    def validate_cache(self, entities=None):
        """
        Runs through all entities stored in the cache and checks
        whether the version still matches the most recent version.
        Non-matching entities will be removed from the cache.

        entities: When set to a db.Container or a list of Entities
                  the IDs from the cache will not be retrieved from the CaosDB database,
                  but the versions from the cache will be checked against the versions
                  contained in that collection. Only entries in the cache that have
                  a corresponding version in the collection will be checked, all others
                  will be ignored. Useful for testing.

        Return a list of invalidated entries or an empty list if no elements have been invalidated.
        """

        res = self.run_sql_commands([(
            "SELECT caosdb_id, caosdb_version FROM identifiables", ())], True)

        if entities is None:
            # TODO this might become a problem. If many entities are cached,
            # then all of them are retrieved here...
            ids = [c_id for c_id, _ in res]
            ids = set(ids)
            entities = db.Container()
            entities.extend([db.Entity(id=c_id) for c_id in ids])
            entities.retrieve()

        v = {c_id: c_version for c_id, c_version in res}

        invalidate_list = []

        for ent in entities:
            if ent.version.id != v[ent.id]:
                invalidate_list.append(ent.id)

        self.run_sql_commands([(
            "DELETE FROM identifiables WHERE caosdb_id IN ({})".format(
                ", ".join([str(caosdb_id) for caosdb_id in invalidate_list])), ())])

        return invalidate_list


class UpdateCache(AbstractCache):
    """
    stores unauthorized inserts and updates

    If the Guard is set to a mode that does not allow an insert or update, the insert or update can
    be stored in this cache such that it can be authorized and performed later.
    """

    def get_cache_schema_version(self):
        return 3

    def get_default_file_name(self):
        return os.path.join(tempfile.gettempdir(), "crawler_update_cache.db")

    @staticmethod
    def get_previous_version(cont):
        """ Retrieve the current, unchanged version of the entities that shall
        be updated, i.e. the version before the update """

        old_ones = db.Container()

        for ent in cont:
            old_ones.append(db.execute_query("FIND ENTITY WITH ID={}".format(ent.id),
                                             unique=True))

        return old_ones

    def insert(self, cont, run_id, insert=False):
        """Insert a pending, unauthorized insert or update


        Parameters
        ----------
        cont: Container with the records to be inserted or updated containing the desired
              version, i.e. the state after the update.

        run_id: int
                The id of the crawler run
        insert: bool
                Whether the entities in the container shall be inserted or updated.
        """
        cont = put_in_container(cont)

        if insert:
            old_ones = ""
        else:
            old_ones = UpdateCache.get_previous_version(cont)
        new_ones = cont

        if insert:
            old_hash = ""
        else:
            old_hash = Cache.hash_entity(old_ones)
        new_hash = Cache.hash_entity(new_ones)
        self.run_sql_commands([('''INSERT INTO updates VALUES (?, ?, ?, ?, ?)''',
                                (old_hash, new_hash, str(old_ones), str(new_ones),
                                 str(run_id)))])

    def create_cache(self):
        """ initialize the cache """
        self.run_sql_commands([
            ('''CREATE TABLE updates (olddigest TEXT, newdigest TEXT, oldrep TEXT,
             newrep  TEXT, run_id TEXT, primary key (olddigest, newdigest, run_id))''',),
            ('''CREATE TABLE version (schema INTEGER)''',),
            ("INSERT INTO version VALUES (?)", (self.get_cache_schema_version(),))])

    def get(self, run_id, querystring):
        """ returns the pending updates for a given run id

        Parameters:
        -----------
        run_id: the id of the crawler run
        querystring: the sql query
        """

        return self.run_sql_commands([(querystring, (str(run_id),))], fetchall=True)

    def get_inserts(self, run_id):
        """ returns the pending updates for a given run id

        Parameters:
        -----------
        run_id: the id of the crawler run
        """

        return self.get(run_id, '''Select * FROM updates WHERE olddigest='' AND run_id=?''')

    def get_updates(self, run_id):
        """ returns the pending updates for a given run id

        Parameters:
        -----------
        run_id: the id of the crawler run
        """

        return self.get(run_id, '''Select * FROM updates WHERE olddigest!='' AND run_id=?''')


class Cache(IdentifiableCache):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning("This class is depricated. Please use IdentifiableCache."))
        super().__init__(*args, **kwargs)
