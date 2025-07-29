# This file is a part of the LinkAhead project.
#
# Copyright (C) 2023 IndiScale GmbH <info@indiscale.com>
# Copyright (C) 2022 Florian Spreckelsen <f.spreckelsen@indiscale.com>
# Copyright (C) 2023 Daniel Hornung <d.hornung@indiscale.com>
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

"""
This module (and script) provides methods to read a DataModel from a YAML file.

If a file name is passed to parse_model_from_yaml it is parsed and a DataModel
is created. The yaml file needs to be structured in a certain way which will be
described in the following.

The file should only contain a dictionary. The keys are the names of
RecordTypes or Properties. The values are again dictionaries describing the
entities. This information can be defined via the keys listed in KEYWORDS.
Notably, properties can be given in a dictionary under the xxxx_properties keys
and will be added with the respective importance. These properties can be
RecordTypes or Properties and can be defined right there.
Every Property or RecordType only needs to be defined once anywhere. When it is
not defined, simply the name can be supplied with no value.
Parents can be provided under the 'inherit_from_xxxx' keywords. The value needs
to be a list with the names. Here, NO NEW entities can be defined.
"""
import argparse
import sys
from typing import List, Optional, Union

import jsonref
import jsonschema
import linkahead as db
import yaml
from linkahead.common.datatype import get_list_datatype

from .data_model import LINKAHEAD_INTERNAL_PROPERTIES, DataModel

# Keywords which are allowed in data model descriptions.
KEYWORDS = ["importance",
            "datatype",  # for example TEXT, INTEGER or REFERENCE
            "unit",
            "description",
            "recommended_properties",
            "obligatory_properties",
            "suggested_properties",
            "inherit_from_recommended",
            "inherit_from_suggested",
            "inherit_from_obligatory",
            "role",
            "value",
            ]

# TODO: check whether it's really ignored
# These KEYWORDS are not forbidden as properties, but merely ignored.
KEYWORDS_IGNORED = [
    "unit",
]

JSON_SCHEMA_ATOMIC_TYPES = [
    "string",
    "boolean",
    "integer",
    "number",
    "null"
]


# Taken from https://stackoverflow.com/a/53647080, CC-BY-SA, 2018 by
# https://stackoverflow.com/users/2572431/augurar


class SafeLineLoader(yaml.SafeLoader):
    """Load a line and keep meta-information.

    Note that this will add a `__line__` element to all the dicts.
    """

    def construct_mapping(self, node, deep=False):
        """Overwritung the parent method."""
        mapping = super().construct_mapping(node, deep=deep)
        # Add 1 so line numbering starts at 1
        mapping['__line__'] = node.start_mark.line + 1

        return mapping
# End of https://stackoverflow.com/a/53647080


class TwiceDefinedException(Exception):
    def __init__(self, name):
        super().__init__("The Entity '{}' was defined multiple times!".format(
            name))


class YamlDefinitionError(RuntimeError):
    def __init__(self, line, template=None):
        if not template:
            template = "Error in YAML definition in line {}."
        super().__init__(template.format(line))


class JsonSchemaDefinitionError(RuntimeError):
    # @author Florian Spreckelsen
    # @date 2022-02-17
    # @review Daniel Hornung 2022-02-18
    def __init__(self, msg):
        super().__init__(msg)


def parse_model_from_yaml(filename, existing_model: Optional[dict] = None, debug: bool = False):
    """Parse a data model from a YAML file.

This is a convenience function if the Parser object is not needed, it calls
``Parser.parse_model_from_yaml(...)`` internally.


Parameters
----------

existing_model : dict, optional
  An existing model to which the created model shall be added.

debug : bool, optional
  If True, turn on miscellaneous debugging.  Default is False.
    """
    parser = Parser(debug=debug)

    return parser.parse_model_from_yaml(filename, existing_model=existing_model)


def parse_model_from_string(string, existing_model: Optional[dict] = None, debug: bool = False):
    """Parse a data model from a YAML string

This is a convenience function if the Parser object is not needed, it calls
``Parser.parse_model_from_string(...)`` internally.

Parameters
----------

existing_model : dict, optional
  An existing model to which the created model shall be added.

debug : bool, optional
  If True, turn on miscellaneous debugging.  Default is False.
    """
    parser = Parser(debug=debug)

    return parser.parse_model_from_string(string, existing_model=existing_model)


def parse_model_from_json_schema(
        filename: str,
        top_level_recordtype: bool = True,
        types_for_missing_array_items: Optional[dict] = None,
        ignore_unspecified_array_items: bool = False,
        existing_model: Optional[dict] = None
):
    """Return a datamodel parsed from a json schema definition.

    Parameters
    ----------

    filename : str
        The path of the json schema file that is to be parsed

    top_level_recordtype : bool, optional
        Whether there is a record type defined at the top level of the
        schema. Default is true.

    types_for_missing_array_items : dict, optional
        dictionary containing fall-back types for json entries with `type:
        array` but without `items` specification. Default is an empty dict.

    ignore_unspecified_array_items : bool, optional
        Whether to ignore `type: array` entries the type of which is not
        specified by their `items` property or given in
        `types_for_missing_array_items`. An error is raised if they are not
        ignored. Default is False.

    existing_model : dict, optional
        An existing model to which the created model shall be added.  Not implemented yet.

    Returns
    -------

    out : Datamodel
        The datamodel generated from the input schema which then can be used for
        synchronizing with LinkAhead.

    Note
    ----
    This is an experimental feature, see ``JsonSchemaParser`` for information
    about the limitations of the current implementation.

    """
    if types_for_missing_array_items is None:
        types_for_missing_array_items = {}

    if existing_model is not None:
        raise NotImplementedError("Adding to an existing model is not implemented yet.")

    # @author Florian Spreckelsen
    # @date 2022-02-17
    # @review Timm Fitschen 2023-05-25
    parser = JsonSchemaParser(types_for_missing_array_items, ignore_unspecified_array_items)

    return parser.parse_model_from_json_schema(filename, top_level_recordtype)


class Parser(object):
    def __init__(self, debug: bool = False):
        """Initialize an empty parser object and initialize the dictionary of entities and the list of
        treated elements.

Parameters
----------

debug : bool, optional
  If True, turn on miscellaneous debugging.  Default is False.

        """
        self.model = {}
        self.treated = []
        self.debug = debug

    def parse_model_from_yaml(self, filename, existing_model: Optional[dict] = None):
        """Create and return a data model from the given file.

        Parameters
        ----------
        filename : str
          The path to the YAML file.

        existing_model : dict, optional
          An existing model to which the created model shall be added.

        Returns
        -------
        out : data_model.DataModel
          The created DataModel
        """
        with open(filename, 'r', encoding="utf-8") as outfile:
            ymlmodel = yaml.load(outfile, Loader=SafeLineLoader)

        return self._create_model_from_dict(ymlmodel, existing_model=existing_model)

    def parse_model_from_string(self, string, existing_model: Optional[dict] = None):
        """Create and return a data model from the given YAML string.

        Parameters
        ----------
        string : str
          The YAML string.

        existing_model : dict, optional
          An existing model to which the created model shall be added.

        Returns
        -------
        out : data_model.DataModel
          The created DataModel
        """
        ymlmodel = yaml.load(string, Loader=SafeLineLoader)

        return self._create_model_from_dict(ymlmodel, existing_model=existing_model)

    def _create_model_from_dict(self, ymlmodel, existing_model: Optional[dict] = None):
        """Create and return a data model out of the YAML dict `ymlmodel`.

        Parameters
        ----------
        ymlmodel : dict
          The dictionary parsed from a YAML file.

        existing_model : dict, optional
          An existing model to which the created model shall be added.

        Raises
        ------
        ValueError
          If model_dict is not a dict, model_dict["extern"] contains an
          unknown entry, or there is an unknown entry in model_dict.

        Returns
        -------
        out : data_model.DataModel
          The created DataModel
        """

        if not isinstance(ymlmodel, dict):
            raise ValueError("Yaml file should only contain one dictionary!")

        if existing_model is not None:
            self.model.update(existing_model)

        # Extern keyword:
        # The extern keyword can be used to include Properties and RecordTypes
        # from existing LinkAhead datamodels into the current model.
        # Any name included in the list specified by the extern keyword
        # will be used in queries to retrieve a property or (if no property exists)
        # a record type with the name of the element.
        # The retrieved entity will be added to the model.
        # If no entity with that name is found an exception is raised.

        if "extern" not in ymlmodel:
            ymlmodel["extern"] = []

        for name in ymlmodel["extern"]:
            if name in LINKAHEAD_INTERNAL_PROPERTIES:
                self.model[name] = db.Property(name=name).retrieve()
                continue
            for role in ("Property", "RecordType", "Record", "File"):
                if db.execute_query("COUNT {} \"{}\"".format(role, name)) > 0:
                    self.model[name] = db.execute_query(
                        f"FIND {role} WITH name=\"{name}\"", unique=True)
                    break
            else:
                raise ValueError("Did not find {}".format(name))

        ymlmodel.pop("extern")

        # add all names to ymlmodel; initialize properties

        for name, entity in ymlmodel.items():
            self._add_entity_to_model(name, entity)
        # initialize recordtypes
        self._set_recordtypes()
        self._check_and_convert_datatypes()

        for name, entity in ymlmodel.items():
            try:
                self._treat_entity(name, entity, line=ymlmodel["__line__"])
            except ValueError as err:
                err_str = err.args[0].replace("invalid keyword:",
                                              f"invalid keyword in line {entity['__line__']}:", 1)
                raise ValueError(err_str, *err.args[1:]) from err

#         Update properties that are part of record types:
#         e.g. add their datatypes, units etc..
#         Otherwise comparison of existing models and the parsed model become difficult.
        for name, ent in self.model.items():
            if not isinstance(ent, db.RecordType):
                continue
            props = ent.get_properties()
            for prop in props:
                if prop.name in self.model:
                    model_prop = self.model[prop.name]
                    # The information must be missing, we don't want to overwrite it accidentally:
                    if prop.datatype is None:
                        if isinstance(model_prop, db.RecordType):
                            prop.datatype = model_prop.name
                        else:
                            prop.datatype = model_prop.datatype
                    # TODO: Data type overwrite is allowed here (because
                    #       of lists), but this might change in the future.
                    # elif prop.datatype != model_prop.datatype:
                    #     raise RuntimeError("datatype must not be set, here. This is probably a bug.")
                    if prop.unit is None:
                        # No unit for plain reference properties
                        if not isinstance(model_prop, db.RecordType):
                            prop.unit = model_prop.unit
                    if prop.description is None:
                        prop.description = model_prop.description

        return DataModel(self.model.values())

    @staticmethod
    def _stringify(name, context=None):
        """Make a string out of `name`.

        Warnings are emitted for difficult values of `name`.

        Parameters
        ----------
        name :
          The value to be converted to a string.

        context : obj
          Will be printed in the case of warnings.

        Returns
        -------
        out : str
          If `name` was a string, return it. Else return str(`name`).
        """

        if name is None:
            print("WARNING: Name of this context is None: {}".format(context),
                  file=sys.stderr)

        if not isinstance(name, str):
            name = str(name)

        return name

    def _add_entity_to_model(self, name, definition):
        """ adds names of Properties and RecordTypes to the model dictionary

        Properties are also initialized.

        name is the key of the yaml element and definition the value.
        """

        if name == "__line__":
            return
        name = self._stringify(name)

        if name not in self.model:
            self.model[name] = None

        if definition is None:
            return

        if (self.model[name] is None and isinstance(definition, dict)
                # is it a property
                and "datatype" in definition
                # but not simply an RT of the model
                and not (get_list_datatype(definition["datatype"]) == name and
                         get_list_datatype(definition["datatype"]) in self.model)):

            # and create the new property
            self.model[name] = db.Property(name=name,
                                           datatype=definition["datatype"])
        elif (self.model[name] is None and isinstance(definition, dict)
              and "role" in definition):
            if definition["role"] == "RecordType":
                self.model[name] = db.RecordType(name=name)
            elif definition["role"] == "Record":
                self.model[name] = db.Record(name=name)
            elif definition["role"] == "File":
                # TODO(fspreck) Implement files at some later point in time
                raise NotImplementedError(
                    "The definition of file objects is not yet implemented.")

                # self.model[name] = db.File(name=name)
            elif definition["role"] == "Property":
                self.model[name] = db.Property(name=name)
            else:
                raise RuntimeError("Unknown role {} in definition of entity.".format(
                    definition["role"]))

        # for setting values of properties directly:
        if not isinstance(definition, dict):
            return

        # add other definitions recursively
        for prop_type in ["recommended_properties",
                          "suggested_properties", "obligatory_properties"]:

            if prop_type in definition:
                # Empty property mapping should be allowed.

                if definition[prop_type] is None:
                    definition[prop_type] = {}
                try:
                    for n, e in definition[prop_type].items():
                        if n == "__line__":
                            continue
                        self._add_entity_to_model(n, e)
                except AttributeError as ate:
                    if ate.args[0].endswith("'items'"):
                        line = definition["__line__"]

                        if isinstance(definition[prop_type], list):
                            line = definition[prop_type][0]["__line__"]
                        raise YamlDefinitionError(line) from None
                    raise

        if self.debug and self.model[name] is not None:
            self.model[name].__line__ = definition["__line__"]

    def _add_to_recordtype(self, ent_name, props, importance):
        """Add properties to a RecordType.

        Parameters
        ----------
        ent_name : str
          The name of the entity to which the properties shall be added.

        props : dict [str -> dict or :doc:`Entity`]
          The properties, indexed by their names.  Properties may be given as :doc:`Entity` objects
          or as dictionaries.

        importance
          The importance as used in :doc:`Entity.add_property`.

        Returns
        -------
        None

        """

        for n, e in props.items():

            if n in KEYWORDS:
                if n in KEYWORDS_IGNORED:
                    continue
                raise YamlDefinitionError("Unexpected keyword in line {}: {}".format(
                    props["__line__"], n))

            if n == "__line__":
                continue
            n = self._stringify(n)

            if isinstance(e, dict):
                if "datatype" in e and get_list_datatype(e["datatype"]) is not None:
                    # Reuse the existing datatype for lists.
                    datatype = db.LIST(get_list_datatype(e["datatype"]))
                else:
                    # Ignore a possible e["datatype"] here if it's not a list
                    # since it has been treated in the definition of the
                    # property (entity) already
                    datatype = None
                if "value" in e:
                    value = e["value"]
                else:
                    value = None

            else:
                value = e
                datatype = None

            self.model[ent_name].add_property(name=n,
                                              value=value,
                                              importance=importance,
                                              datatype=datatype)

    def _inherit(self, name, prop, inheritance):
        if not isinstance(prop, list):
            if isinstance(prop, str):
                raise YamlDefinitionError(
                    f"Parents must be a list but is given as string: {name} > {prop}")
            raise YamlDefinitionError("Parents must be a list, error in line {}".format(
                prop["__line__"]))

        for pname in prop:
            if not isinstance(pname, str):
                raise ValueError("Only provide the names of parents.")
            self.model[name].add_parent(name=pname, inheritance=inheritance)

    def _treat_entity(self, name, definition, line=None):
        """Parse the definition and the information to the entity."""

        if name == "__line__":
            return
        name = self._stringify(name)

        try:
            if definition is None:
                return

            # for setting values of properties directly:
            if not isinstance(definition, dict):
                return

            # These definition items must be handled even for list props.
            for prop_name, prop in definition.items():
                if prop_name == "description":
                    self.model[name].description = prop

            # For lists, everything else is not needed at this level.
            if ("datatype" in definition and definition["datatype"].startswith("LIST")):
                return

            if name in self.treated:
                raise TwiceDefinedException(name)

            # for reducing a little bit of code duplication:
            importance_dict = {
                "recommended_properties": db.RECOMMENDED,
                "obligatory_properties": db.OBLIGATORY,
                "suggested_properties": db.SUGGESTED
                }

            for prop_name, prop in definition.items():
                if prop_name == "__line__":
                    continue
                line = definition["__line__"]

                if prop_name == "unit":
                    self.model[name].unit = prop

                elif prop_name == "value":
                    self.model[name].value = prop

                elif prop_name == "description":
                    # Handled above
                    continue

                elif prop_name in importance_dict:
                    for imp_name, imp_val in importance_dict.items():
                        if prop_name == imp_name:
                            self._add_to_recordtype(
                                name, prop, importance=imp_val)

                            for n, e in prop.items():
                                self._treat_entity(n, e)

                # datatype is already set
                elif prop_name == "datatype":
                    continue

                # role has already been used
                elif prop_name == "role":
                    continue

                elif prop_name == "inherit_from_obligatory":
                    self._inherit(name, prop, db.OBLIGATORY)
                elif prop_name == "inherit_from_recommended":
                    self._inherit(name, prop, db.RECOMMENDED)
                elif prop_name == "inherit_from_suggested":
                    self._inherit(name, prop, db.SUGGESTED)

                else:
                    raise ValueError("invalid keyword: {}".format(prop_name))
        except AttributeError as ate:
            if ate.args[0].endswith("'items'"):
                raise YamlDefinitionError(line) from None
        except Exception as e:
            print("Error in treating: "+name)
            raise e
        self.treated.append(name)

    def _check_and_convert_datatypes(self):
        """ checks if datatype is valid.
        datatype of properties is simply initialized with string. Here, we
        iterate over properties and check whether it is a base datatype of a
        name that was defined in the model (or extern part)

        the string representations are replaced with linkahead objects

        """

        for _, value in self.model.items():

            if isinstance(value, db.Property):
                dtype = value.datatype
                is_list = False

                if get_list_datatype(dtype) is not None:
                    dtype = get_list_datatype(dtype)
                    is_list = True

                dtype_name = dtype
                if not isinstance(dtype_name, str):
                    dtype_name = dtype.name

                if dtype_name in self.model:
                    if is_list:
                        value.datatype = db.LIST(self.model[dtype_name])
                    else:
                        value.datatype = self.model[dtype_name]

                    continue

                if dtype in [db.DOUBLE,
                             db.REFERENCE,
                             db.TEXT,
                             db.DATETIME,
                             db.INTEGER,
                             db.FILE,
                             db.BOOLEAN]:

                    if is_list:
                        value.datatype = db.LIST(db.__getattribute__(  # pylint: disable=no-member
                            dtype))
                    else:
                        value.datatype = db.__getattribute__(  # pylint: disable=no-member
                            dtype)

                    continue

                raise ValueError("Property {} has an unknown datatype: {}".format(
                    value.name, dtype_name))

    def _set_recordtypes(self):
        """ properties are defined in first iteration; set remaining as RTs """

        for key, value in self.model.items():
            if value is None:
                self.model[key] = db.RecordType(name=key)


class JsonSchemaParser(Parser):
    """Extends the yaml parser to read in datamodels defined in a json schema.

    **EXPERIMENTAL:** While this class can already be used to create data models
    from basic json schemas, there are the following limitations and missing
    features:

    * Due to limitations of json-schema itself, we currently do not support
      inheritance in the imported data models
    * The same goes for suggested properties of RecordTypes
    * Already defined RecordTypes and (scalar) Properties can't be re-used as
      list properties
    * Reference properties that are different from the referenced RT. (Although
      this is possible for list of references)
    * Values
    * Roles
    * The extern keyword from the yaml parser

    """
    # @author Florian Spreckelsen
    # @date 2022-02-17
    # @review Timm Fitschen 2023-05-25

    def __init__(self, types_for_missing_array_items=None,
                 ignore_unspecified_array_items=False):
        super().__init__()
        if types_for_missing_array_items is None:
            types_for_missing_array_items = {}
        self.types_for_missing_array_items = types_for_missing_array_items
        self.ignore_unspecified_array_items = ignore_unspecified_array_items

    def parse_model_from_json_schema(self, filename: str, top_level_recordtype: bool = True):
        """Return a datamodel created from the definition in the json schema in
        `filename`.

        Parameters
        ----------
        filename : str
            The path to the json-schema file containing the datamodel definition
        top_level_recordtype : bool, optional
            Whether there is a record type defined at the top level of the
            schema. Default is true.

        Returns
        -------
        out : data_model.DataModel
            The created DataModel
        """
        # @author Florian Spreckelsen
        # @date 2022-02-17
        # @review Timm Fitschen 2023-05-25
        with open(filename, 'r', encoding="utf-8") as schema_file:
            model_dict = jsonref.load(schema_file)

        return self._create_model_from_dict(model_dict, top_level_recordtype=top_level_recordtype)

    # ToDo: Fix https://gitlab.indiscale.com/caosdb/src/caosdb-advanced-user-tools/-/issues/139
    #       and remove pylint disable
    def _create_model_from_dict(self, model_dict: Union[dict, List[dict]], top_level_recordtype: bool = True):  # pylint: disable=arguments-renamed
        """Parse a dictionary and return the Datamodel created from it.

        The dictionary was typically created from the model definition in a json schema file.

        Parameters
        ----------
        model_dict : dict or list[dict]
            One or several dictionaries read in from a json-schema file
        top_level_recordtype : bool, optional
            Whether there is a record type defined at the top level of the
            schema. Default is true.

        Returns
        -------
        our : data_model.DataModel
            The datamodel defined in `model_dict`
        """
        # @review Timm Fitschen 2023-05-25
        if isinstance(model_dict, dict):
            model_dict = [model_dict]

        for ii, elt in enumerate(model_dict):
            try:
                jsonschema.Draft202012Validator.check_schema(elt)
            except jsonschema.SchemaError as err:
                key = elt["title"] if "title" in elt else f"element {ii}"
                raise JsonSchemaDefinitionError(
                    f"Json Schema error in {key}:\n{str(err)}") from err

            if top_level_recordtype:
                if "title" not in elt:
                    raise JsonSchemaDefinitionError(
                        f"Object {ii+1} is lacking the `title` key word")
                if "type" not in elt:
                    raise JsonSchemaDefinitionError(
                        f"Object {ii+1} is lacking the `type` key word")
                # Check if this is a valid Json Schema
                name = self._stringify(elt["title"], context=elt)
                self._treat_element(elt, name)
            elif "properties" in elt or "patternProperties" in elt:
                # No top-level type but there are entities
                if "properties" in elt:
                    for key, prop in elt["properties"].items():
                        name = self._get_name_from_property(key, prop)
                        self._treat_element(prop, name)
                if "patternProperties" in elt:
                    # See also treatment in ``_treat_record_type``. Since here,
                    # there is no top-level RT we use the prefix `__Pattern`,
                    # i.e., the resulting Record Types will be called
                    # `__PatternElement`.
                    self._treat_pattern_properties(
                        elt["patternProperties"], name_prefix="__Pattern")
            else:
                # Neither RecordType itself, nor further properties in schema,
                # so nothing to do here. Maybe add something in the future.
                continue

        return DataModel(self.model.values())

    def _get_name_from_property(self, key: str, prop: dict):
        # @review Timm Fitschen 2023-05-25
        if "title" in prop:
            name = self._stringify(prop["title"])
        else:
            name = self._stringify(key)

        return name

    def _get_atomic_datatype(self, elt):
        # @review Timm Fitschen 2023-05-25
        if elt["type"] == "string":
            if "format" in elt and elt["format"] in ["date", "date-time"]:
                return db.DATETIME
            else:
                return db.TEXT
        elif elt["type"] == "integer":
            return db.INTEGER
        elif elt["type"] == "number":
            return db.DOUBLE
        elif elt["type"] == "boolean":
            return db.BOOLEAN
        elif elt["type"] == "null":
            # This could be any datatype since a valid json will never have a
            # value in a null property. We use TEXT for convenience.
            return db.TEXT
        else:
            raise JsonSchemaDefinitionError(f"Unkown atomic type in {elt}.")

    def _treat_element(self, elt: dict, name: str):
        # @review Timm Fitschen 2023-05-25
        force_list = False
        if name in self.model:
            return self.model[name], force_list
        if "type" not in elt:
            # Each element must have a specific type
            raise JsonSchemaDefinitionError(
                f"`type` is missing in element {name}.")
        if name == "name":
            # This is identified with the LinkAhead name property as long as the
            # type is correct.
            if not elt["type"] == "string" and "string" not in elt["type"]:
                raise JsonSchemaDefinitionError(
                    "The 'name' property must be string-typed, otherwise it cannot "
                    "be identified with LinkAhead's name property."
                )
            return None, force_list
        # LinkAhead suports null for all types, so in the very special case of
        # `"type": ["null", "<other_type>"]`, only consider the other type:
        if isinstance(elt["type"], list) and len(elt["type"]) == 2 and "null" in elt["type"]:
            elt["type"].remove("null")
            elt["type"] = elt["type"][0]
        if "enum" in elt:
            ent = self._treat_enum(elt, name)
        elif elt["type"] in JSON_SCHEMA_ATOMIC_TYPES:
            ent = db.Property(
                name=name, datatype=self._get_atomic_datatype(elt))
        elif elt["type"] == "object":
            ent = self._treat_record_type(elt, name)
        elif elt["type"] == "array":
            ent, force_list = self._treat_list(elt, name)
        else:
            raise NotImplementedError(
                f"Cannot parse items of type '{elt['type']}' (yet).")
        if "description" in elt and ent.description is None:
            # There is a description and it hasn't been set by another
            # treat_something function
            ent.description = elt["description"]

        if ent is not None:
            self.model[name] = ent
        return ent, force_list

    def _treat_record_type(self, elt: dict, name: str):
        # @review Timm Fitschen 2023-05-25
        rt = db.RecordType(name=name)
        if "required" in elt:
            required = elt["required"]
        else:
            required = []
        if "properties" in elt:
            for key, prop in elt["properties"].items():
                name = self._get_name_from_property(key, prop)
                prop_ent, force_list = self._treat_element(prop, name)
                if prop_ent is None:
                    # Nothing to be appended since the property has to be
                    # treated specially.
                    continue
                importance = db.OBLIGATORY if key in required else db.RECOMMENDED
                if not force_list:
                    rt.add_property(prop_ent, importance=importance)
                else:
                    # Special case of rt used as a list property
                    rt.add_property(prop_ent, importance=importance,
                                    datatype=db.LIST(prop_ent))

        if "patternProperties" in elt:

            pattern_property_rts = self._treat_pattern_properties(
                elt["patternProperties"], name_prefix=name)
            for ppr in pattern_property_rts:
                # add reference to pattern property type. These can never be
                # obligatory since pattern properties cannot be required in the
                # original schema (since their actual names are not known a
                # priori).
                rt.add_property(ppr)

        if "description" in elt:
            rt.description = elt["description"]
        return rt

    def _treat_enum(self, elt: dict, name: str):
        # @review Timm Fitschen 2022-02-30
        if "type" in elt and elt["type"] == "integer":
            raise NotImplementedError(
                "Integer-enums are not allowd until "
                "https://gitlab.indiscale.com/caosdb/src/caosdb-server/-/issues/224 "
                "has been fixed."
            )
        rt = db.RecordType(name=name)
        for enum_elt in elt["enum"]:
            rec = db.Record(name=self._stringify(enum_elt))
            rec.add_parent(rt)
            self.model[enum_elt] = rec

        return rt

    def _treat_list(self, elt: dict, name: str):
        # @review Timm Fitschen 2023-05-25

        if "items" not in elt and name not in self.types_for_missing_array_items:
            if self.ignore_unspecified_array_items:
                return None, False
            raise JsonSchemaDefinitionError(
                f"The definition of the list items is missing in {elt}.")
        if "items" in elt:
            items = elt["items"]
            if "enum" in items:
                return self._treat_enum(items, name), True
            if items["type"] in JSON_SCHEMA_ATOMIC_TYPES:
                datatype = db.LIST(self._get_atomic_datatype(items))
                return db.Property(name=name, datatype=datatype), False
            if items["type"] == "object":
                if "title" not in items or self._stringify(items["title"]) == name:
                    # Property is RecordType
                    return self._treat_record_type(items, name), True
                else:
                    # List property will be an entity of its own with a name
                    # different from the referenced RT
                    ref_rt = self._treat_record_type(
                        items, self._stringify(items["title"]))
                    self.model[ref_rt.name] = ref_rt
                    return db.Property(name=name, datatype=db.LIST(ref_rt)), False
        else:
            # Use predefined type:
            datatype = db.LIST(self.types_for_missing_array_items[name])
            return db.Property(name=name, datatype=datatype), False

    def _get_pattern_prop(self):
        # @review Timm Fitschen 2023-05-25
        if "__pattern_property_pattern_property" in self.model:
            return self.model["__pattern_property_pattern_property"]
        pp = db.Property(name="__matched_pattern", datatype=db.TEXT)
        self.model["__pattern_property_pattern_property"] = pp
        return pp

    def _treat_pattern_properties(self, pattern_elements, name_prefix=""):
        """Special Treatment for pattern properties: A RecordType is created for
        each pattern property. In case of a `type: object` PatternProperty, the
        remaining properties of the JSON entry are appended to the new
        RecordType; in case of an atomic type PatternProperty, a single value
        Property is added to the RecordType.

        Raises
        ------
        NotImplementedError
            In case of patternProperties with non-object, non-atomic type, e.g.,
            array.

        """
        # @review Timm Fitschen 2023-05-25
        num_patterns = len(pattern_elements)
        pattern_prop = self._get_pattern_prop()
        returns = []
        for ii, (key, element) in enumerate(pattern_elements.items()):
            if "title" not in element:
                name_suffix = f"_{ii+1}" if num_patterns > 1 else ""
                name = name_prefix + "Entry" + name_suffix
            else:
                name = element["title"]
            if element["type"] == "object":
                # simple, is already an object, so can be treated like any other
                # record type.
                pattern_type = self._treat_record_type(element, name)
            elif element["type"] in JSON_SCHEMA_ATOMIC_TYPES:
                # create a property that stores the actual value of the pattern
                # property.
                propname = f"{name}_value"
                prop = db.Property(name=propname, datatype=self._get_atomic_datatype(element))
                self.model[propname] = prop
                pattern_type = db.RecordType(name=name)
                pattern_type.add_property(prop)
            else:
                raise NotImplementedError(
                    "Pattern properties are currently only supported for types " +
                    ", ".join(JSON_SCHEMA_ATOMIC_TYPES) + ", and object.")

            # Add pattern property and description
            pattern_type.add_property(pattern_prop, importance=db.OBLIGATORY)
            if pattern_type.description:
                pattern_type.description += f"\n\npattern: {key}"
            else:
                pattern_type.description = f"pattern: {key}"

            self.model[name] = pattern_type
            returns.append(pattern_type)

        return returns


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("data_model",
                        help="Path name of the data model file (yaml or json) to be used.")
    parser.add_argument("--sync", action="store_true",
                        help="Whether or not to sync the data model with the server.")
    parser.add_argument("--noquestion", action="store_true",
                        help="Whether or not to ask questions during synchronization.")
    parser.add_argument("--print", action="store_true",
                        help="Whether or not to print the data model.")

    args = parser.parse_args()
    if args.data_model.endswith(".json"):
        model = parse_model_from_json_schema(args.data_model)
    elif args.data_model.endswith(".yml") or args.data_model.endswith(".yaml"):
        model = parse_model_from_yaml(args.data_model)
    else:
        raise RuntimeError(f"Unknown file ending of data model: {args.data_model}")
    if args.print:
        print(model)
    if args.sync:
        model.sync_data_model(noquestion=args.noquestion)


if __name__ == "__main__":
    main()
