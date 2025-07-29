#!/usr/bin/env python
# encoding: utf-8
#
# ** header v3.0
# This file is a part of the LinkAhead project.
#
# Copyright (C) 2018 Research Group Biomedical Physics,
# Max-Planck-Institute for Dynamics and Self-Organization Göttingen
# Copyright (C) 2020 Indiscale GmbH <info@indiscale.com>
# Copyright (C) 2020 Henrik tom Wörden
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
#
""" Crawls a file structure and inserts Records into LinkAhead based on what is
found.

LinkAhead can automatically be filled with Records based on some file structure.
The Crawler will iterate over the files and test for each file whether a CFood
exists that matches the file path. If one does, it is instanciated to treat the
match. This occurs in basically three steps:
1. create a list of identifiables, i.e. unique representation of LinkAhead Records
(such as an experiment belonging to a project and a date/time)
2. the identifiables are either found in LinkAhead or they are created.
3. the identifiables are update based on the date in the file structure
"""


import logging
import os
import traceback
import uuid
from datetime import datetime
from sqlite3 import IntegrityError

import linkahead as db
from linkahead.exceptions import BadQueryError

from .cache import IdentifiableCache, UpdateCache, get_pretty_xml
from .cfood import RowCFood, add_files, get_ids_for_entities_with_names
from .datainconsistency import DataInconsistencyError
from .datamodel_problems import DataModelProblems
from .guard import RETRIEVE, ProhibitedException
from .guard import global_guard as guard
from .serverside.helper import send_mail as main_send_mail
from .suppressKnown import SuppressKnown
from .utils import create_entity_link

# The pylint warnings triggered in this file are ignored, as this code is
# assumed to be deprecated in the near future. Should this change, they need
# to be reevaluated.


logger = logging.getLogger(__name__)


def separated(text):
    return "-"*60 + "\n" + text


def apply_list_of_updates(to_be_updated, update_flags=None,
                          update_cache=None, run_id=None):
    """Updates the `to_be_updated` Container, i.e., pushes the changes to LinkAhead
    after removing possible duplicates. If a chace is provided, uauthorized
    updates can be cached for further authorization.

    Parameters:
    -----------
    to_be_updated : db.Container
        Container with the entities that will be updated.
    update_flags : dict, optional
        Dictionary of LinkAhead server flags that will be used for the
        update. Default is an empty dict.
    update_cache : UpdateCache or None, optional
        Cache in which the intended updates will be stored so they can be
        authorized afterwards. Default is None.
    run_id : String or None, optional
        Id with which the pending updates are cached. Only meaningful if
        `update_cache` is provided. Default is None.
    """
    if update_flags is None:
        update_flags = {}

    if len(to_be_updated) == 0:
        return

    get_ids_for_entities_with_names(to_be_updated)

    # remove duplicates
    tmp = db.Container()

    for el in to_be_updated:
        if el not in tmp:
            tmp.append(el)

    to_be_updated = tmp

    info = "UPDATE: updating the following entities\n"

    for el in to_be_updated:
        info += str("\t" + create_entity_link(el))
        info += "\n"
    logger.info(info)

    logger.debug(to_be_updated)
    try:
        if len(to_be_updated) > 0:
            logger.info(
                "Updating {} Records...".format(
                    len(to_be_updated)))
        guard.safe_update(to_be_updated, unique=False,
                          flags=update_flags)
    except FileNotFoundError as e:
        logger.info("Cannot access {}. However, it might be needed for"
                    " the correct execution".format(e.filename))
    except ProhibitedException:
        try:
            update_cache.insert(to_be_updated, run_id)
        except IntegrityError as e:
            logger.warning(
                "There were problems with the update of {}.".format(
                    to_be_updated),
                extra={"identifier": str(to_be_updated),
                       "category": "update-cache"}
            )
            logger.debug(traceback.format_exc())
            logger.debug(e)
    except Exception as e:             # pylint: disable=broad-exception-caught
        DataModelProblems.evaluate_exception(e)


class Crawler(object):
    def __init__(self, cfood_types, use_cache=False,
                 abort_on_exception=True, interactive=True, hideKnown=False,
                 debug_file=None, cache_file=None):
        """
        Parameters
        ----------
        cfood_types : list of CFood classes
               The Crawler will use those CFoods when crawling.
        use_cache : bool, optional
                    Whether to use caching (not re-inserting probably existing
                    objects into LinkAhead), defaults to False.
        abort_on_exception : if true, exceptions are raise.
                    Otherwise the crawler continues if an exception occurs.
        interactive : boolean, optional
                      If true, questions will be posed during execution of the
                      crawl function.
        debug_file : a file where debug output is saved. The path will be
                     printed when a critical error occured.
        cache_file : a file where the cached identifiables are stored. See
                     cache.py

        """

        self.cfood_types = cfood_types
        self.interactive = interactive
        self.report = db.Container()
        self.use_cache = use_cache
        self.hideKnown = hideKnown
        self.debug_file = debug_file
        self.abort_on_exception = abort_on_exception
        self.update_cache = UpdateCache()
        self.filterKnown = SuppressKnown()
        self.run_id = None
        advancedtoolslogger = logging.getLogger("caosadvancedtools")

        # TODO this seems to be a bad idea. What if the handler was not added
        # yet? What if there is another stream handler, which shall not be
        # filtered?

        for hdl in advancedtoolslogger.handlers:
            if hdl.__class__.__name__ == "StreamHandler":
                hdl.addFilter(self.filterKnown)

        if hideKnown is False:
            for cat in ["matches", "inconsistency"]:
                self.filterKnown.reset(cat)

        if self.use_cache:
            self.cache = IdentifiableCache(db_file=cache_file)
            self.cache.validate_cache()

    def iteritems(self):
        """ generates items to be crawled with an index"""
        yield 0, None

    @staticmethod
    def update_authorized_changes(run_id):
        """
        execute the pending updates of a specific run id.

        This should be called if the updates of a certain run were authorized.

        Parameters:
        -----------
        run_id: the id of the crawler run
        """
        cache = UpdateCache()
        inserts = cache.get_inserts(run_id)
        all_inserts = 0
        all_updates = 0
        for _, _, _, new, _ in inserts:
            new_cont = db.Container()
            new_cont = new_cont.from_xml(new)
            new_cont.insert(unique=False)
            logger.info("Successfully inserted {} records!".format(len(new_cont)))
            all_inserts += len(new_cont)
        logger.info("Finished with authorized inserts.")

        changes = cache.get_updates(run_id)

        for _, _, old, new, _ in changes:
            new_cont = db.Container.from_xml(new)
            ids = []
            tmp = db.Container()
            update_incomplete = False         # pylint: disable=unused-variable
            # remove duplicate entities
            for el in new_cont:
                if el.id not in ids:
                    ids.append(el.id)
                    tmp.append(el)
                else:
                    update_incomplete = True
            new_cont = tmp
            if new_cont[0].version:                 # pylint: disable=no-member
                valids = db.Container()
                nonvalids = db.Container()

                for ent in new_cont:
                    remote_ent = db.Entity(id=ent.id).retrieve()
                    if ent.version == remote_ent.version:       # pylint: disable=no-member
                        valids.append(ent)
                    else:
                        update_incomplete = True
                        nonvalids.append(remote_ent)
                valids.update(unique=False)
                logger.info("Successfully updated {} records!".format(
                    len(valids)))
                logger.info("{} Records were not updated because the version in the server "
                            "changed!".format(len(nonvalids)))
                all_updates += len(valids)
            else:
                current = db.Container()

                for ent in new_cont:
                    current.append(db.Entity(id=ent.id).retrieve())
                current_xml = get_pretty_xml(current)

                # check whether previous version equals current version
                # if not, the update must not be done

                if current_xml != old:
                    continue

                new_cont.update(unique=False)
                logger.info("Successfully updated {} records!".format(
                    len(new_cont)))
                all_updates += len(new_cont)
        logger.info("Some updates could not be applied. Crawler has to rerun.")
        logger.info("Finished with authorized updates.")
        return all_inserts, all_updates

    def collect_cfoods(self):
        """
        This is the first phase of the crawl. It collects all cfoods that shall
        be processed. The second phase is iterating over cfoods and updating
        LinkAhead. This separate first step is necessary in order to allow a
        single cfood being influenced by multiple crawled items. E.g. the
        FileCrawler can have a single cfood treat multiple files.

        This is a very basic implementation and this function should be
        overwritten by subclasses.

        The basic structure of this function should be, that what ever is
        being processed is iterated and each cfood is checked whether the
        item 'matches'. If it does, a cfood is instantiated passing the item
        as an argument.
        The match can depend on the cfoods already being created, i.e. a file
        migth no longer match because it is already treaded by an earlier
        cfood.

        should return cfoods, tbs and errors_occured.
        # TODO do this via logging?
        tbs text returned from traceback
        errors_occured True if at least one error occured
        """
        cfoods = []
        tbs = []
        errors_occured = False
        matches = {idx: [] for idx, _ in self.iteritems()}

        logger.debug(separated("Matching files against CFoods"))

        for Cfood in self.cfood_types:
            logger.debug("Matching against {}...".format(Cfood.__name__))

            for idx, item in self.iteritems():
                if Cfood.match_item(item):
                    try:
                        matches[idx].append(Cfood.__name__)
                        cfoods.append(Cfood(item))
                        logger.debug("{} matched\n{}.".format(
                            Cfood.__name__,
                            item))
                    except FileNotFoundError as e:
                        logger.info("Cannot access {}. However, it might be needed for"
                                    " the correct execution".format(e.filename))
                    except DataInconsistencyError as e:
                        logger.debug(traceback.format_exc())
                        logger.debug(e)
                        # TODO: Generally: in which cases should exceptions be raised? When is
                        # errors_occured set to True? The expected behavior must be documented.
                    except Exception as e:      # pylint: disable=broad-exception-caught
                        try:
                            DataModelProblems.evaluate_exception(e)
                        except Exception:       # pylint: disable=broad-exception-caught
                            pass
                        logger.debug("Failed during execution of {}!".format(
                            Cfood.__name__))
                        logger.debug(traceback.format_exc())
                        logger.debug(e)

                        if self.abort_on_exception:
                            raise e

                        errors_occured = True
                        tbs.append(e)

        logger.debug(separated("Number of Cfoods: "+str(len(cfoods))))
        logger.debug(separated("CFoods are collecting information..."))

        remove_cfoods = []

        for cfood in cfoods:
            try:
                cfood.collect_information()
            except DataInconsistencyError as e:
                logger.debug(traceback.format_exc())
                logger.debug(e)
                remove_cfoods.append(cfood)
            except FileNotFoundError as e:
                logger.info("Cannot access {}. However, it might be needed for"
                            " the correct execution".format(e.filename))
                remove_cfoods.append(cfood)
            except Exception as e:     # pylint: disable=broad-exception-caught
                try:
                    DataModelProblems.evaluate_exception(e)
                except Exception:      # pylint: disable=broad-exception-caught
                    pass
                logger.debug("Failed during execution of {}!".format(
                    cfood.__name__))
                logger.debug(traceback.format_exc())
                logger.debug(e)
                remove_cfoods.append(cfood)

                if self.abort_on_exception:
                    raise e

        for rm in remove_cfoods:
            cfoods.remove(rm)
            logger.debug("Removed {} due to an Error in "
                         "collect_information".format(str(rm)))

        logger.debug(
            separated("Trying to attach further items to created CFoods"))

        for cfood in cfoods:
            logger.debug("Matching against {}...".format(
                cfood.__class__.__name__))

            for idx, item in self.iteritems():
                if cfood.looking_for(item):
                    logger.debug("{} matched\n{}.".format(
                        cfood.__class__.__name__,
                        item))
                    cfood.attach(item)
                    matches[idx].append(cfood.__class__.__name__)

        self.check_matches(matches)

        return cfoods, tbs, errors_occured

    def check_matches(self, matches):
        for idx, item in self.iteritems():
            if len(matches[idx]) == 0:
                msg = ("The crawler has no matching rules for and is thus "
                       "ignoring:\n{}".format(item))

                logger.warning(msg, extra={"identifier": str(item),
                                           'category': "matches"})

            if len(matches[idx]) > 1:
                msg = ("Attention: More than one matching cfood!\n"
                       + "Tried to match {}\n".format(item)
                       + "\tRecordTypes:\t" + ", ".join(
                           matches[idx])+"\n")

                logger.debug(msg, extra={"identifier": str(item),
                                         'category': "matches"})

    def _cached_find_or_insert_identifiables(self, identifiables):
        if self.use_cache:
            hashes = self.cache.update_ids_from_cache(identifiables)

        self.find_or_insert_identifiables(identifiables)

        if self.use_cache:
            self.cache.insert_list(hashes, identifiables)

    def crawl(self, security_level=RETRIEVE, path=None):
        self.run_id = uuid.uuid1()
        logger.info("Run Id: " + str(self.run_id))
        guard.set_level(level=security_level)

        logger.info("Scanning the objects to be treated...")
        cfoods, tbs, errors_occured = self.collect_cfoods()

        if self.interactive and "y" != input("Do you want to continue? (y)"):
            return

        for cfood in cfoods:
            try:
                cfood.create_identifiables()
                self._cached_find_or_insert_identifiables(cfood.identifiables)

                cfood.update_identifiables()
                apply_list_of_updates(
                    cfood.to_be_updated,
                    cfood.update_flags,
                    update_cache=self.update_cache,
                    run_id=self.run_id)
            except FileNotFoundError as e:
                logger.info("Cannot access {}. However, it might be needed for"
                            " the correct execution".format(e.filename))
            except DataInconsistencyError as e:
                logger.debug(traceback.format_exc())
                logger.debug(e)
            except Exception as e:     # pylint: disable=broad-exception-caught
                try:
                    DataModelProblems.evaluate_exception(e)
                except Exception:      # pylint: disable=broad-exception-caught
                    pass
                logger.info("Failed during execution of {}!".format(
                    cfood.__class__.__name__))
                logger.debug(traceback.format_exc())
                logger.debug(e)

                if self.abort_on_exception:
                    raise e
                errors_occured = True
                tbs.append(e)

        pending_changes = self.update_cache.get_updates(self.run_id)

        if pending_changes:
            # Sending an Email with a link to a form to authorize updates is
            # only done in SSS mode

            if "SHARED_DIR" in os.environ:
                filename = Crawler.save_form([el[3]
                                              for el in pending_changes], path, self.run_id)
                Crawler.send_mail([el[3] for el in pending_changes], filename)

            for i, el in enumerate(pending_changes):

                logger.debug(
                    """
UNAUTHORIZED UPDATE ({} of {}):
____________________\n""".format(i+1, len(pending_changes)) + str(el[3]))
            logger.info("There where unauthorized changes (see above). An "
                        "email was sent to the curator.\n"
                        "You can authorize the updates by invoking the crawler"
                        " with the run id: {rid}\n".format(rid=self.run_id))

        if len(DataModelProblems.missing) > 0:
            err_msg = ("There were problems with one or more RecordType or "
                       "Property. Do they exist in the data model?\n")

            for ent in DataModelProblems.missing:
                err_msg += str(ent) + "\n"
            logger.error(err_msg)
            logger.error('Crawler finished with Datamodel Errors')
        elif errors_occured:
            msg = ("There were fatal errors during execution, please contact "
                   "the system administrator!")

            if self.debug_file:
                msg += "\nPlease provide the following path:\n{}".format(
                    self.debug_file)
            logger.error(msg)
            logger.error("Crawler terminated with failures!")
            logger.debug(tbs)
        else:
            logger.info("Crawler terminated successfully!")

    @staticmethod
    def save_form(changes, path, run_id):
        """
        Saves an html website to a file that contains a form with a button to
        authorize the given changes.

        The button will call the crawler with the same path that was used for
        the current run and with a parameter to authorize the changes of the
        current run.

        Parameters:
        -----------
        changes: The LinkAhead entities in the version after the update.
        path: the path defining the subtree that is crawled

        """
        from xml.sax.saxutils import escape

        linkahead_config = db.configuration.get_config()
        if ("advancedtools" in linkahead_config and "crawler.customcssfile" in
                linkahead_config["advancedtools"]):
            cssfile = linkahead_config["advancedtools"]["crawler.customcssfile"]
        else:
            cssfile = None
        # TODO move path related stuff to sss_helper
        form = """
<html>
<head>
  <meta charset="utf-8"/>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Crawler</title>
  <link rel="stylesheet" href="{url}/webinterface/css/bootstrap.css">
  <link rel="stylesheet" href="{url}/webinterface/css/webcaosdb.css"/>
  <link rel="stylesheet" href="{url}/webinterface/css/linkahead.css"/>
  <link rel="stylesheet" href="{url}/webinterface/css/dropzone.css">
  <link rel="stylesheet" href="{url}/webinterface/css/tour.css">
  <link rel="stylesheet" href="{url}/webinterface/css/leaflet.css">
  <link rel="stylesheet" href="{url}/webinterface/css/leaflet-coordinates.css">
  <link rel="stylesheet" href="{url}/webinterface/css/bootstrap-select.css">
  <link rel="stylesheet" href="{url}/webinterface/css/bootstrap-icons.css">
  {customcssfile}
  <script src="{url}/webinterface/webcaosdb.dist.js"></script>
</head>
<body>
<form method="post" action="{url}/scripting">
    <input type="hidden" name="call" value="crawl.py"/>
    <input type="hidden" name="-p0" value=""/>
    <input type="hidden" name="-p1" value="{path}"/>
    <input type="hidden" name="-Oauthorize-run" value="{rid}"/>
    <input type="submit" value="Authorize"/>
</form>
<pre>
<code>
{changes}
</code>
</pre>
<script>
        const wrapper = $(`
<div class="container caosdb-f-main">
  <div class="row caosdb-v-main-col">
    <div class="panel-group caosdb-f-main-entities"></div>
  </div>
</div>`);
        const code_element = $("code").remove();
        const entities_str = `<Response>${{code_element.text()}}</Response>`;
        const entities = str2xml(entities_str);
        transformation.transformEntities(entities).then((html) => {{
            wrapper.find(".caosdb-f-main-entities").append(html);
            wrapper.find(".caosdb-v-entity-header-buttons-list .glyphicon-comment").hide();
            $(document.body).append(wrapper);
            const message_bodies = $(wrapper).find(".caosdb-messages div div");
            console.log(message_bodies);

            for (const body of message_bodies.toArray()) {{
                const text = body.innerHTML;
                console.log(text);
                body.innerHTML = markdown.textToHtml(text);

            }}
        }});
    </script>
</body>
</html>
""".format(url=linkahead_config["Connection"]["url"],
           rid=run_id,
           changes=escape("\n".join(changes)),
           customcssfile='<link rel="stylesheet" href="{url}/webinterface/css/{customcssfile}"/>'.format(
               url=linkahead_config["Connection"]["url"], customcssfile=cssfile) if cssfile else "",
           path=path)

        if "SHARED_DIR" in os.environ:
            directory = os.environ["SHARED_DIR"]
        else:
            directory = "."
            logger.info("No 'SHARED_DIR' in environment, using '.' as fallback.")
        filename = str(run_id)+".html"
        randname = os.path.basename(os.path.abspath(directory))
        filepath = os.path.abspath(os.path.join(directory, filename))
        filename = os.path.join(randname, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(form)
        return filename

    @staticmethod
    def send_mail(changes, filename):
        """ calls sendmail in order to send a mail to the curator about pending
        changes

        Parameters:
        -----------
        changes: The LinkAhead entities in the version after the update.
        filename: path to the html site that allow the authorization
        """

        linkahead_config = db.configuration.get_config()
        text = """Dear Curator,
there where changes that need your authorization. Please check the following
carefully and if the changes are ok, click on the following link:

{url}/Shared/{filename}

{changes}
        """.format(url=linkahead_config["Connection"]["url"],
                   filename=filename,
                   changes="\n".join(changes))
        try:
            fro = linkahead_config["advancedtools"]["crawler.from_mail"]
            to = linkahead_config["advancedtools"]["crawler.to_mail"]
        except KeyError:
            logger.error("Server Configuration is missing a setting for "
                         "sending mails. The administrator should check "
                         "'from_mail' and 'to_mail'.")
            return

        main_send_mail(
            from_addr=fro,
            to=to,
            subject="Crawler Update",
            body=text)

    # TODO remove static?

    @staticmethod
    def find_or_insert_identifiables(identifiables):
        """ Sets the ids of identifiables (that do not have already an id from the
        cache) based on searching LinkAhead and retrieves those entities.
        The remaining entities (those which can not be retrieved) have no
        correspondence in LinkAhead and are thus inserted.
        """
        # looking for matching entities in LinkAhead when there is no valid id
        # i.e. there was none set from a cache

        existing = []
        inserted = []

        for ent in identifiables:
            if ent.id is None or ent.id < 0:
                logger.debug("Looking for: {}".format(
                    ent.id if ent.id is not None else ent.name))
                found = Crawler.find_existing(ent)

                if found is not None:
                    ent.id = found.id
            else:
                logger.debug("Id is known of: {}".format(ent))

            # insert missing, i.e. those which are not valid
            if ent.id is None or ent.id < 0:
                missing = ent
                ent.id = None
            else:
                missing = None
                existing.append(ent)

            if missing:
                try:
                    guard.safe_insert(missing, unique=False,
                                      flags={"force-missing-obligatory": "ignore"})
                    inserted.append(ent)
                except Exception as e:       # pylint: disable=broad-exception-caught
                    DataModelProblems.evaluate_exception(e)
        if len(existing) > 0:
            info = "Identified the following existing entities:\n"

            for ent in existing:
                info += str(ent)+"\n"
            logger.debug(info)
        else:
            logger.debug("Did not identify any existing entities")
        if len(inserted) > 0:
            info = "Inserted the following entities:\n"

            for ent in inserted:
                info += str(ent)+"\n"
            logger.debug(info)
        else:
            logger.debug("Did not insert any new entities")

        logger.debug("Retrieving entities from LinkAhead...")
        identifiables.retrieve(unique=True, raise_exception_on_error=False)

    @staticmethod
    def create_query_for_identifiable(ident):
        """
        uses the properties of ident to create a query that can determine
        whether the required record already exists.
        """
        # TODO multiple parents are ignored! Sufficient?
        if len(ident.get_parents()) == 0:
            raise ValueError("The identifiable must have at least one parent.")
        query_string = "FIND Record " + ident.get_parents()[0].name
        query_string += " WITH "
        if ident.name is None and len(ident.get_properties()) == 0:
            raise ValueError(
                "The identifiable must have features to identify it.")

        if ident.name is not None:
            query_string += "name='{}' AND".format(ident.name)

        for p in ident.get_properties():
            if p.datatype is not None and p.datatype.startswith("LIST<"):
                for v in p.value:
                    query_string += ("references "
                                     + str(v.id if isinstance(v, db.Entity)
                                           else v)
                                     + " AND ")
            else:
                query_string += ("'" + p.name + "'='" + str(get_value(p))
                                 + "' AND ")
        # remove the last AND
        return query_string[:-4]

    @staticmethod
    def find_existing(entity):
        """searches for an entity that matches the identifiable in LinkAhead

        Characteristics of the identifiable like, properties, name or id are
        used for the match.
        """
        query_string = Crawler.create_query_for_identifiable(entity)
        logger.debug(query_string)
        q = db.Query(query_string)
        # the identifiable should identify an object uniquely. Thus the query
        # is using the unique keyword
        try:
            r = q.execute(unique=True)
        except BadQueryError:
            # either empty or ambiguous response
            r = None

        # if r is not None:
        #     print("Found Entity with id:", r.id)
        # else:
        #     print("Did not find an existing entity.")

        return r


class FileCrawler(Crawler):
    def __init__(self, files, **kwargs):
        """
        Parameters
        ----------
        files : files to be crawled

        """
        super().__init__(**kwargs)
        self.files = files
        add_files({fi.path: fi for fi in files})

    def iteritems(self):
        for idx, p in enumerate(sorted([f.path for f in self.files])):
            yield idx, p

    @staticmethod
    def query_files(path):
        query_str = "FIND FILE WHICH IS STORED AT '" + (
            path if path.endswith("/") else path + "/") + "**'"
        q_info = "Sending the following query: '" + query_str + "'\n"
        files = db.execute_query(query_str)
        logger.info(
            q_info + "Found {} files that need to be processed.".format(
                len(files)))

        return files


class TableCrawler(Crawler):

    def __init__(self, table, unique_cols, recordtype, **kwargs):
        """
        Parameters
        ----------
        table : pandas DataFrame
        unique_cols : the columns that provide the properties for the
                      identifiable
        recordtype : Record Type of the Records to be created
        """
        self.table = table

        # TODO I do not like this yet, but I do not see a better way so far.
        class ThisRowCF(RowCFood):
            def __init__(self, item):
                super().__init__(item, unique_cols, recordtype)

        super().__init__(cfood_types=[ThisRowCF], **kwargs)

    def iteritems(self):
        for idx, row in self.table.iterrows():
            yield idx, row


def get_value(prop):
    """ Returns the value of a Property

    Parameters
    ----------
    prop : The property of which the value shall be returned.

    Returns
    -------
    out : The value of the property; if the value is an entity, its ID.

    """

    if isinstance(prop.value, db.Entity):
        return prop.value.id
    elif isinstance(prop.value, datetime):
        return prop.value.isoformat()
    else:
        return prop.value
