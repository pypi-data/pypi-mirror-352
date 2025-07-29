#!/usr/bin/env python
# encoding: utf-8
#
# This file is a part of the LinkAhead project.
#
# Copyright (C) 2023 Indiscale GmbH <info@indiscale.com>
# Copyright (C) 2023 Florian Spreckelsen <f.spreckelsen@indiscale.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.
#
"""Convert a data model into a json schema.

Sometimes you may want to have a `json schema <https://json-schema.org>`_ which describes a
LinkAhead data model, for example for the automatic generation of user interfaces with third-party
tools like `rjsf <https://rjsf-team.github.io/react-jsonschema-form/docs/>`_.  Then this is the
right module for you!

The :mod:`json_schema_exporter <caosadvancedtools.json_schema_exporter>` module has one main class,
:class:`JsonSchemaExporter`, and a few utility and wrapper functions.

For easy usage, you may simply import `recordtype_to_json_schema` and use it on a fully referenced
RecordType like this::

  import caosadvancedtools.models.parser as parser
  import caosadvancedtools.json_schema_exporter as jsex

  model = parser.parse_model_from_yaml("my_model.yml")

  # get the data model schema for the "Journey" recordtype
  schema, ui_schema = recordtype_to_json_schema(
      rt=model.get_deep("Journey"),
      do_not_create=["Continent"],         # only choose from existing Records
      multiple_choice=["visited_cities"],
      rjsf=True                            # also create a UI schema
  )

For more details on how to use this wrapper, read the `function documentation
<recordtype_to_json_schema>`.

Other useful functions are `make_array`, which creates an array out of a single schema, and
`merge_schemas`, which as the name suggests allows to combine multiple schema definitions into a
single schema.

"""

from collections import OrderedDict
from typing import Any, Iterable, Optional, Sequence, Union

import linkahead as db
from linkahead.cached import cache_clear, cached_query
from linkahead.common.datatype import get_list_datatype, is_list_datatype
from linkahead.utils.get_entity import get_entity_by_name

from .models.data_model import DataModel


class JsonSchemaExporter:
    """A class which collects everything needed for the conversion.
    """

    def __init__(self, additional_properties: bool = True,
                 name_property_for_new_records: bool = False,
                 use_id_for_identification: bool = False,
                 description_property_for_new_records: bool = False,
                 additional_options_for_text_props: Optional[dict] = None,
                 additional_json_schema: Optional[dict[str, dict]] = None,
                 additional_ui_schema: Optional[dict[str, dict]] = None,
                 units_in_description: bool = True,
                 do_not_create: Optional[list[str]] = None,
                 do_not_retrieve: Optional[Union[list[str], str]] = None,
                 no_remote: bool = False,
                 use_rt_pool: Optional[DataModel] = None,
                 multiple_choice: Optional[list[str]] = None,
                 multiple_choice_guess: bool = False,
                 wrap_files_in_objects: bool = False,
                 ):
        """Set up a JsonSchemaExporter, which can then be applied on RecordTypes.

        Parameters
        ----------
        additional_properties : bool, optional
            Whether additional properties will be admitted in the resulting
            schema. Optional, default is True.
        name_property_for_new_records : bool, optional
            Whether objects shall generally have a `name` property in the generated schema.
            Optional, default is False.
        use_id_for_identification: bool, optional
            If set to true, an 'id' property is added to all records, and
            foreign key references are assumed to be ids.
        description_property_for_new_records : bool, optional
            Whether objects shall generally have a `description` property in the generated schema.
            Optional, default is False.
        additional_options_for_text_props : dict, optional
            Dictionary containing additional "pattern" or "format" options for
            string-typed properties. Optional, default is empty.
        additional_json_schema : dict[str, dict], optional
            Additional schema content for elements of the given names.
        additional_ui_schema : dict[str, dict], optional
            Additional ui schema content for elements of the given names.
        units_in_description : bool, optional
            Whether to add the unit of a LinkAhead property (if it has any) to the
            description of the corresponding schema entry. If set to false, an
            additional `unit` key is added to the schema itself which is purely
            annotational and ignored, e.g., in validation. Default is True.
        do_not_create : list[str], optional
            A list of reference Property names, for which there should be no option
            to create them.  Instead, only the choice of existing elements should
            be given.
        do_not_retrieve : list[str] or str, optional
            A list of RecordType names, for which no Records shall be retrieved.  Instead, only an
            object description should be given.  If this list overlaps with the `do_not_create`
            parameter, the behavior is undefined.
            If this parameter is the string "``auto``", only multiple choice references (see
            parameter ``multiple_choice``) will be retrieved.
            The default is the empty list.
        no_remote : bool, optional
            If True, do not attempt to connect to a LinkAhead server at all. Default is False. Note
            that the exporter may fail if this option is activated and the data model is not
            self-sufficient.
        use_rt_pool : models.data_model.DataModel, optional
            If given, do not attempt to retrieve RecordType information remotely but from this
            parameter instead.
        multiple_choice : list[str], optional
            A list of reference Property names which shall be denoted as multiple choice properties.
            This means that each option in this property may be selected at most once.  This is not
            implemented yet if the Property is not in ``do_not_create`` as well.
        multiple_choice_guess : bool, default=False
            If True, try to guess for all reference Properties that are not in ``multiple_choice``
            if they are enum-like and thus should be handled as multiple choice.
        wrap_files_in_objects : bool, optional
            Whether (lists of) files should be wrapped into an array of objects
            that have a file property. The sole purpose of this wrapping is to
            provide a workaround for a `react-jsonschema-form
            bug<https://github.com/rjsf-team/react-jsonschema-form/issues/3957>`_
            so only set this to True if you're using the exported schema with
            react-json-form and you are experiencing the bug. Default is False.

        Notes on reference properties
        -----------------------------

        List references will have the "uniqueItems" property set if:

        - ``do_not_retrieve`` is not set for the referenced RecordType
        - ``multiple_choice`` is true or guessed to be true (if ``multiple_choice_guess`` is set)

        """
        if not additional_options_for_text_props:
            additional_options_for_text_props = {}
        if not additional_json_schema:
            additional_json_schema = {}
        if not additional_ui_schema:
            additional_ui_schema = {}
        if not do_not_create:
            do_not_create = []
        if not do_not_retrieve:
            do_not_retrieve = []
        if not multiple_choice:
            multiple_choice = []

        cache_clear()

        self._additional_properties = additional_properties
        self._name_property_for_new_records = name_property_for_new_records
        self._use_id_for_identification = use_id_for_identification
        self._description_property_for_new_records = description_property_for_new_records
        self._additional_options_for_text_props = additional_options_for_text_props
        self._additional_json_schema = additional_json_schema
        self._additional_ui_schema = additional_ui_schema
        self._units_in_description = units_in_description
        self._do_not_create = do_not_create
        self._do_not_retrieve = do_not_retrieve
        self._no_remote = no_remote
        self._use_rt_pool = use_rt_pool
        self._multiple_choice = multiple_choice
        self._multiple_choice_guess = multiple_choice_guess
        self._wrap_files_in_objects = wrap_files_in_objects

    @staticmethod
    def _make_required_list(rt: db.RecordType):
        """Return the list of names of properties with importance db.OBLIGATORY."""
        required_list = []
        for prop in rt.properties:
            if rt.get_importance(prop.name) != db.OBLIGATORY:
                continue
            prop_name = prop.name
            required_list.append(prop_name)

        return required_list

    def _make_segment_from_prop(self, prop: db.Property, multiple_choice_enforce: bool = False
                                ) -> tuple[OrderedDict, dict]:
        """Return the JSON Schema and ui schema segments for the given property.

The result may either be a simple json schema segment, such as a `string
<https://json-schema.org/understanding-json-schema/reference/string>`_ element (or another
simple type), a combination such as `anyOf
<https://json-schema.org/understanding-json-schema/reference/combining#anyof>`_ or an `array
<https://json-schema.org/understanding-json-schema/reference/array>`_ element

Parameters
----------
prop : db.Property
    The property to be transformed.

multiple_choice_enforce : bool, default=False
    If True, this property shall be handled as multiple choice items.

Returns
-------

json_schema : OrderedDict
    The Json schema.

ui_schema : dict
    An appropriate UI schema.
        """
        json_prop = OrderedDict()
        ui_schema: dict = {}
        if prop.datatype == db.TEXT or prop.datatype == db.DATETIME:
            text_format = None
            text_pattern = None
            if prop.name in self._additional_options_for_text_props:
                if "pattern" in self._additional_options_for_text_props[prop.name]:
                    text_pattern = self._additional_options_for_text_props[prop.name]["pattern"]
                if "format" in self._additional_options_for_text_props[prop.name]:
                    text_format = self._additional_options_for_text_props[prop.name]["format"]
                elif prop.datatype == db.DATETIME:
                    # Set the date or datetime format if only a pattern is given ...
                    text_format = ["date", "date-time"]
            elif prop.datatype == db.DATETIME:
                # ... again, for those props that don't appear in the additional
                # options list.
                text_format = ["date", "date-time"]

            json_prop = self._make_text_property(prop.description, text_format, text_pattern)
            return self._customize(json_prop, ui_schema, prop)

        if prop.description:
            json_prop["description"] = prop.description
        if self._units_in_description and prop.unit:
            if "description" in json_prop:
                json_prop["description"] += f" Unit is {prop.unit}."
            else:
                json_prop["description"] = f"Unit is {prop.unit}."
        elif prop.unit:
            json_prop["unit"] = prop.unit

        if prop.datatype == db.BOOLEAN:
            json_prop["type"] = "boolean"
        elif prop.datatype == db.INTEGER:
            json_prop["type"] = "integer"
        elif prop.datatype == db.DOUBLE:
            json_prop["type"] = "number"
        # list-valued non-files
        elif is_list_datatype(prop.datatype) and not (
                self._wrap_files_in_objects
                and get_list_datatype(prop.datatype, strict=True) == db.FILE):
            json_prop["type"] = "array"
            list_element_prop = db.Property(
                name=prop.name, datatype=get_list_datatype(prop.datatype, strict=True))

            # Is this a multiple choice array?
            multiple_choice = prop.name in self._multiple_choice
            # breakpoint()
            if (not multiple_choice and self._multiple_choice_guess
                    and db.common.datatype.is_reference(list_element_prop.datatype)):
                multiple_choice = self._guess_recordtype_is_enum(list_element_prop.datatype)
            # breakpoint()

            # Get inner content of list
            json_prop["items"], inner_ui_schema = self._make_segment_from_prop(
                list_element_prop, multiple_choice_enforce=multiple_choice)
            if "type" in json_prop["items"] and (
                    json_prop["items"]["type"] in ["boolean", "integer", "number", "string"]
            ):
                json_prop["items"]["type"] = [json_prop["items"]["type"], "null"]

            if multiple_choice:
                # TODO: if not multiple_choice, but do_not_create:
                # "ui:widget" = "radio" & "ui:inline" = true
                # TODO: set threshold for number of items.
                json_prop["uniqueItems"] = True
                ui_schema["ui:widget"] = "checkboxes"
                ui_schema["ui:inline"] = True
            if inner_ui_schema:
                ui_schema["items"] = inner_ui_schema
        # scalar references
        elif prop.is_reference():
            # We must distinguish between multiple kinds of "reference" properties.

            # Case 1: Plain reference without RecordType
            if prop.datatype == db.REFERENCE:
                # No Record creation since no RT is specified and we don't know what
                # schema to use, so only enum of all Records and all Files.
                values = self._retrieve_enum_values("RECORD") + self._retrieve_enum_values("FILE")
                json_prop["enum"] = values
                if prop.name in self._multiple_choice:
                    json_prop["uniqueItems"] = True

            # Case 2: Files are data-url strings in json schema
            elif prop.datatype == db.FILE or (
                self._wrap_files_in_objects and
                    is_list_datatype(prop.datatype) and
                    get_list_datatype(prop.datatype, strict=True) == db.FILE
            ):
                # Singular FILE (wrapped or unwrapped), or wrapped LIST<FILE>
                if self._wrap_files_in_objects:
                    # Workaround for react-jsonschema-form bug
                    # https://github.com/rjsf-team/react-jsonschema-form/issues/3957:
                    # Wrap all FILE references (regardless whether lists or
                    # scalars) in an array of objects that have a file property,
                    # since objects can be deleted, files can't.
                    json_prop["type"] = "array"
                    json_prop["items"] = {
                        "type": "object",
                        "title": "Next file",
                        # TODO Why can't it be empty?
                        # The wrapper object must wrap a file and can't be empty.
                        "required": [  # "file"
                        ],
                        # Wrapper objects must only contain the wrapped file.
                        "additionalProperties": False,
                        "properties": {
                            "file": {
                                "title": "Enter your file.",
                                "type": "string",
                                "format": "data-url"
                            }
                        }
                    }
                    if not is_list_datatype(prop.datatype):
                        # Scalar file, so the array has maximum length 1
                        json_prop["maxItems"] = 1
                else:
                    json_prop["type"] = "string"
                    json_prop["format"] = "data-url"

            # Case 3: Reference property with a type
            else:
                prop_name = prop.datatype
                if isinstance(prop.datatype, db.Entity):
                    prop_name = prop.datatype.name

                # Find out if this property is an enum.
                is_enum = (multiple_choice_enforce
                           or
                           (self._multiple_choice_guess
                            and self._guess_recordtype_is_enum(prop_name)))
                # If `is_enum` -> always get values
                # Otherwise -> `do_not_retrieve` may prevent retrieval
                if is_enum or not (
                        (
                            isinstance(self._do_not_retrieve, list)
                            and prop_name in self._do_not_retrieve)
                        or (
                            self._do_not_retrieve == "auto"
                        )):
                    values = self._retrieve_enum_values(f"RECORD '{prop_name}'")
                else:
                    values = []

                if is_enum or prop.name in self._do_not_create:
                    # Only a simple list of values
                    json_prop["enum"] = values
                else:
                    if self._use_rt_pool:
                        rt = self._use_rt_pool.get_deep(prop_name)
                    elif self._no_remote:
                        rt = prop.datatype
                    else:
                        results = cached_query(f"FIND RECORDTYPE WITH name='{prop_name}'")
                        assert len(results) <= 1
                        if len(results):
                            rt = results[0]
                        else:
                            rt = db.Entity()

                    if isinstance(rt, str):
                        raise NotImplementedError("Behavior is not implemented when "
                                                  "_no_remote == True and datatype is given as a "
                                                  "string.")

                    subschema, ui_schema = self._make_segment_from_recordtype(rt)
                    if prop.is_reference():
                        if prop.name:
                            subschema["title"] = prop.name
                        if prop.description:
                            subschema["description"] = prop.description
                        if self._use_id_for_identification:
                            subschema["properties"]["name"] = {
                                "type": "string",
                                "description": "The name of the Record to be created"}
                            subschema["properties"]["id"] = {"type": "string"}
                            subschema["properties"].move_to_end("name", last=False)
                            subschema["properties"].move_to_end("id", last=False)
                            # {"oneOf": [{"type": "integer"}, {"type": "string"}]}

                    # if inner_ui_schema:
                    #     ui_schema = inner_ui_schema
                    if values:
                        subschema["title"] = "Create new"
                        json_prop["oneOf"] = [
                            {
                                "title": "Existing entries",
                                "enum": values,
                            },
                            subschema
                        ]
                    else:
                        json_prop = subschema

        else:
            raise ValueError(
                f"Unknown or no property datatype. Property {prop.name} with type {prop.datatype}")

        return self._customize(json_prop, ui_schema, prop)

    @staticmethod
    def _make_text_property(description="", text_format=None, text_pattern=None) -> OrderedDict:
        """Create a text element.

        Can be a `string <https://json-schema.org/understanding-json-schema/reference/string>`_
        element or an `anyOf
        <https://json-schema.org/understanding-json-schema/reference/combining#anyof>`_ combination
        thereof.

         Example:

        .. code-block:: json

                {
                  "type": "string",
                  "description": "Some description",
                  "pattern": "[0-9]{2..4}-[0-9]{2-4}",
                  "format": "hostname",
                }
        """
        prop: OrderedDict[str, Union[str, list]] = OrderedDict({
            "type": "string"
        })
        if description:
            prop["description"] = description
        if text_format is not None:
            if isinstance(text_format, list):
                # We want the type inside the options, not in the head:
                # "datetime property": {
                #   "anyOf": [
                #     {
                #       "type": "string",
                #       "format": "date"
                #     },
                #     {
                #       "type": "string",
                #       "format": "date-time"
                #     }]}
                prop.pop("type")
                prop["anyOf"] = [{"type": "string", "format": tf} for tf in text_format]
            else:
                prop["format"] = text_format
        if text_pattern is not None:
            prop["pattern"] = text_pattern

        return prop

    def _guess_recordtype_is_enum(self, rt_name: str) -> bool:
        """For a given RecordType, guess if it represents an enum.

        Parameters
        ----------
        rt_name : str
          Name of the RecordType to be guessed.

        Returns
        -------
        out : guess
          True, if the RecordType is guessed to be an enum.  False otherwise.
        """
        rt = get_entity_by_name(rt_name)
        return len(rt.get_properties()) == 0

    def _retrieve_enum_values(self, role: str):

        if self._no_remote:
            return []

        possible_values = cached_query(f"SELECT name, id FROM {role}")

        vals = []
        for val in possible_values:
            # if self._use_id_for_identification:
            #     vals.append(val.id)
            if val.name:
                vals.append(f"{val.name}")
            else:
                vals.append(f"{val.id}")

        return vals

    def _make_segment_from_recordtype(self, rt: db.RecordType) -> tuple[OrderedDict, dict]:
        """Return Json schema and uischema segments for the given RecordType.

        The result is an element of type `object
        <https://json-schema.org/understanding-json-schema/reference/object>`_ and typically
        contains more properties:

        .. code-block:: json

            {
                "type": "object",
                "title": "MyRecordtypeName",
                "properties": {
                    "number": { "type": "number" },
                    "street_name": { "type": "string" },
                    "street_type": { "enum": ["Street", "Avenue", "Boulevard"] }
                }
            }
        """

        schema: OrderedDict[str, Any] = OrderedDict({
            "type": "object"
        })
        ui_schema = {}

        schema["required"] = self._make_required_list(rt)
        schema["additionalProperties"] = self._additional_properties
        if rt.description:
            schema["description"] = rt.description

        if rt.name:
            schema["title"] = rt.name

        props = OrderedDict()
        if self._name_property_for_new_records:
            props["name"] = self._make_text_property("The name of the Record to be created")
        # if self._use_id_for_identification:
        #     props["id"] = self._make_text_property("The id of the Record")
        if self._description_property_for_new_records:
            props["description"] = self._make_text_property(
                "The description of the Record to be created")

        for prop in rt.properties:
            if prop.name in props:
                # Multi property
                raise NotImplementedError(
                    "Creating a schema for multi-properties is not specified. "
                    f"Property {prop.name} occurs more than once."
                )
            props[prop.name], inner_ui_schema = self._make_segment_from_prop(prop)
            if inner_ui_schema:
                ui_schema[prop.name] = inner_ui_schema

        if self._use_id_for_identification:
            props["name"] = {
                "type": "string",
                "description": "The name of the Record to be created"}
            props["id"] = {"type": "string"}
            props.move_to_end("name", last=False)
            props.move_to_end("id", last=False)

        schema["properties"] = props

        return schema, ui_schema

    def _customize(self, schema: OrderedDict, ui_schema: dict, entity: db.Entity = None) -> (
            tuple[OrderedDict, dict]):
        """Generic customization method.

Walk over the available customization stores and apply all applicable ones.  No specific order is
guaranteed (as of now).

        Parameters
        ----------
        schema, ui_schema : dict
          The input schemata.
        entity: db.Entity : , optional
          An Entity object, may be useful in the future for customizers.

        Returns
        -------
        out : Tuple[dict, dict]
          The modified input schemata.
        """

        name = schema.get("title", None)
        if entity and entity.name:
            name = entity.name
        for key, add_schema in self._additional_json_schema.items():
            if key == name:
                schema.update(add_schema)
        for key, add_schema in self._additional_ui_schema.items():
            if key == name:
                ui_schema.update(add_schema)

        return schema, ui_schema

    def recordtype_to_json_schema(self, rt: db.RecordType, rjsf: bool = False) -> Union[
            dict, tuple[dict, dict]]:
        """Create a jsonschema from a given RecordType that can be used, e.g., to
        validate a json specifying a record of the given type.

        Parameters
        ----------
        rt : RecordType
            The RecordType from which a json schema will be created.
        rjsf : bool, optional
            If True, uiSchema definitions for react-jsonschema-forms will be output as the second
            return value.  Default is False

        Returns
        -------
        schema : dict
            A dict containing the json schema created from the given RecordType's properties.

        ui_schema : dict, optional
            A ui schema.  Only if a parameter asks for it (e.g. ``rjsf``).
        """
        if rt is None:
            raise ValueError(
                "recordtype_to_json_schema(...) cannot be called with a `None` RecordType.")
        schema, inner_uischema = self._make_segment_from_recordtype(rt)
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        if rt.description:
            schema["description"] = rt.description
        schema, inner_uischema = self._customize(schema, inner_uischema, rt)

        if rjsf:
            uischema = {}
            if inner_uischema:
                uischema = inner_uischema
            return schema, uischema
        return schema


def recordtype_to_json_schema(rt: db.RecordType, additional_properties: bool = True,
                              name_property_for_new_records: bool = False,
                              use_id_for_identification: bool = False,
                              description_property_for_new_records: bool = False,
                              additional_options_for_text_props: Optional[dict] = None,
                              additional_json_schema: Optional[dict[str, dict]] = None,
                              additional_ui_schema: Optional[dict[str, dict]] = None,
                              units_in_description: bool = True,
                              do_not_create: Optional[list[str]] = None,
                              do_not_retrieve: Optional[Union[list[str], str]] = None,
                              no_remote: bool = False,
                              use_rt_pool: Optional[DataModel] = None,
                              multiple_choice: Optional[list[str]] = None,
                              multiple_choice_guess: bool = False,
                              rjsf: bool = False,
                              wrap_files_in_objects: bool = False
                              ) -> Union[dict, tuple[dict, dict]]:
    """Create a jsonschema from a given RecordType that can be used, e.g., to
    validate a json specifying a record of the given type.

    This is a standalone function which works without manually creating a
    JsonSchemaExporter object.

    Parameters
    ----------
    rt : RecordType
        The RecordType from which a json schema will be created.

    The other parameters are identical to the ones use by ``JsonSchemaExporter``

    Returns
    -------
    schema : dict
        A dict containing the json schema created from the given RecordType's properties.

    ui_schema : dict, optional
        A ui schema.  Only if a parameter asks for it (e.g. ``rjsf``).
    """

    exporter = JsonSchemaExporter(
        additional_properties=additional_properties,
        name_property_for_new_records=name_property_for_new_records,
        use_id_for_identification=use_id_for_identification,
        description_property_for_new_records=description_property_for_new_records,
        additional_options_for_text_props=additional_options_for_text_props,
        additional_json_schema=additional_json_schema,
        additional_ui_schema=additional_ui_schema,
        units_in_description=units_in_description,
        do_not_create=do_not_create,
        do_not_retrieve=do_not_retrieve,
        no_remote=no_remote,
        use_rt_pool=use_rt_pool,
        multiple_choice=multiple_choice,
        multiple_choice_guess=multiple_choice_guess,
        wrap_files_in_objects=wrap_files_in_objects
    )
    return exporter.recordtype_to_json_schema(rt, rjsf=rjsf)


def make_array(schema: dict, rjsf_uischema: dict = None) -> Union[dict, tuple[dict, dict]]:
    """Create an array of the given schema.

The result will look like this:

.. code:: js

  { "type": "array",
    "items": {
        // the schema
      }
  }

Parameters
----------

schema : dict
  The JSON schema which shall be packed into an array.

rjsf_uischema : dict, optional
  A react-jsonschema-forms ui schema that shall be wrapped as well.

Returns
-------

schema : dict
  A JSON schema dict with a top-level array which contains instances of the given schema.

ui_schema : dict, optional
  The wrapped ui schema.  Only returned if ``rjsf_uischema`` is given as parameter.
    """
    result = {
        "type": "array",
        "items": schema,
        "$schema": "https://json-schema.org/draft/2020-12/schema",
    }

    if schema.get("description"):
        result["description"] = schema["description"]

    if rjsf_uischema is not None:
        ui_schema = {"items": rjsf_uischema}
        # Propagate ui: options up one level.
        for key in rjsf_uischema.keys():
            if key.startswith("ui:"):
                ui_schema[key] = rjsf_uischema[key]

        return result, ui_schema
    return result


def merge_schemas(schemas: Union[dict[str, dict], Iterable[dict]],
                  rjsf_uischemas: Optional[Union[dict[str, dict], Sequence[dict]]] = None,
                  return_data_schema=False) -> (Union[dict, tuple[dict, dict]]):
    """Merge the given schemata into a single schema.

The result will look like this:

.. code:: js

  {
    "type": "object",
    "properties": {
      // A, B, C
    },
    "required": [
      // "A", "B", "C"
    ],
    "additionalProperties": false
  }


Parameters
----------

schemas : dict[str, dict] | Iterable[dict]
  A dict or iterable of schemata which shall be merged together.  If this is a dict, the keys will
  be used as property names, otherwise the titles of the submitted schemata.  If they have no title,
  numbers will be used as a fallback.  Note that even with a dict, the original schema's "title" is
  not changed.
rjsf_uischemas : dict[str, dict] | Iterable[dict], optional
  If given, also merge the react-jsonschema-forms from this argument and return as the second return
  value.  If ``schemas`` is a dict, this parameter must also be a dict, if ``schemas`` is only an
  iterable, this paramater must support numerical indexing.
return_data_schema : bool, default False
  If set to True, a second schema with all top-level entries wrapped in an
  array will be returned. This is necessary if the schema describes the
  data layout of an XLSX file.
  Cannot be used together with rjsf_uischemas.

Returns
-------

schema : dict
  A JSON schema dict with a top-level object which contains the given schemata as properties.

uischema : dict
  If ``rjsf_uischemas`` was given, this contains the merged UI schemata.
data_schema : dict
  If ``return_data_schema`` was given, this contains the XLSX file schema.
    """
    sub_schemas: dict[str, dict] = OrderedDict()
    required = []
    ui_schema = None
    data_sub_schemas = OrderedDict()

    if isinstance(schemas, dict):
        sub_schemas = schemas
        required = [str(k) for k in schemas.keys()]
        if rjsf_uischemas is not None:
            if not isinstance(rjsf_uischemas, dict):
                raise ValueError("Parameter `rjsf_uischemas` must be a dict, because `schemas` is "
                                 f"as well, but it is a {type(rjsf_uischemas)}.")
            ui_schema = {k: rjsf_uischemas[k] for k in schemas.keys()}
    else:
        for i, schema in enumerate(schemas, start=1):
            title = schema.get("title", str(i))
            sub_schemas[title] = schema
            if return_data_schema:
                # data_sub_schemas[title] = {"type": "array", "items": schema}
                data_sub_schemas[title] = schema
            required.append(title)
        if rjsf_uischemas is not None:
            if not isinstance(rjsf_uischemas, Sequence):
                raise ValueError("Parameter `rjsf_uischemas` must be a sequence, because `schemas` "
                                 f"is as well, but it is a {type(rjsf_uischemas)}.")
            ui_schema = {}
            for i, title in enumerate(sub_schemas.keys()):
                ui_schema[title] = rjsf_uischemas[i]
            # ui_schema = {"index": ui_schema}

    result = {
        "type": "object",
        "properties": sub_schemas,
        "required": required,
        "additionalProperties": False,
        "$schema": "https://json-schema.org/draft/2020-12/schema",
    }
    if return_data_schema:
        data_schema = {
            "type": "object",
            "properties": data_sub_schemas,
            "required": required,
            "additionalProperties": False,
            "$schema": "https://json-schema.org/draft/2020-12/schema",
        }

    if ui_schema is not None:
        return result, ui_schema
    if return_data_schema:
        return result, data_schema
    return result
