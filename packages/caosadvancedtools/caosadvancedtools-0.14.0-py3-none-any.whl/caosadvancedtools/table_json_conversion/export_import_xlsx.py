# encoding: utf-8
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2025 Indiscale GmbH <info@indiscale.com>
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
Utilities for automatically exporting and importing data to and from xlsx.
"""

import json
import tempfile
import warnings
import logging
from typing import Any, Iterable, Optional, Union
from pathlib import Path

from linkahead import (
    Container,
    # LinkAheadException,
    )
from linkahead.cached import cached_get_entity_by

from ..json_schema_exporter import JsonSchemaExporter, merge_schemas
from .table_generator import XLSXTemplateGenerator
from .fill_xlsx import fill_template

# The high_level_api import would normally warn about the API being
# experimental. We know this, so suppress the warning.
logging.disable(logging.WARNING)
from linkahead.high_level_api import (  # noqa: E402, pylint: disable=wrong-import-position
    convert_to_python_object,
    # query
    )
logging.disable(logging.NOTSET)


def _generate_jsonschema_from_recordtypes(recordtypes: Iterable,
                                          out_path: Optional[Union[str, Path]] = None) -> dict:
    """
    Generate a combined jsonschema for all given recordtypes.

    Parameters
    ----------
    recordtypes : Iterable
        List of RecordType entities for which a schema should be generated.
    out_path : str or Path, optional
        If given, the resulting jsonschema will also be written to the file
        given by out_path.
        Optional, default None

    Returns
    -------
    data_schema : dict
        The generated schema.
    """
    # Generate schema
    schema_generator = JsonSchemaExporter(additional_properties=False,
                                          name_property_for_new_records=False,
                                          use_id_for_identification=True,
                                          do_not_retrieve="auto",
                                          multiple_choice_guess=True)
    schemas = [schema_generator.recordtype_to_json_schema(recordtype)
               for recordtype in recordtypes]
    _, data_schema = merge_schemas(schemas, return_data_schema=True)
    # If indicated, save as json file
    if out_path is not None:
        with open(out_path, mode="w", encoding="utf8") as json_file:
            json.dump(data_schema, json_file, ensure_ascii=False, indent=2)
    # Return
    return data_schema


def _generate_jsondata_from_records(records: list,
                                    out_path: Optional[Union[str, Path]] = None) -> dict:
    """
    Extract relevant information (id, name, properties, etc.) from the given
    records and converts this information to json.

    Parameters
    ----------
    records :  Iterable
        List of high-level API objects from which the data will be converted to json.
    out_path : str or Path, optional
        If given, the resulting jsondata will also be written to the file given
        by out_path.
        Optional, default None

    Returns
    -------
    json_data : dict
        The given records data in json form.
    """
    json_data: dict[str, Any] = {}
    for record_obj in records:
        raw_data = record_obj.serialize(plain_json=True)

        parent_name = record_obj.get_parents()[0].name  # We do not handle multiple inheritance yet.
        if parent_name not in json_data:
            json_data[parent_name] = []
        json_data[parent_name].append(raw_data)
    # If indicated, save as json file
    if out_path is not None:
        with open(out_path, mode="w", encoding="utf8") as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=2, default=str)

    return json_data


def _generate_xlsx_template_file(schema: dict,
                                 out_path: Union[str, Path]):
    """
    Generate an empty XLSX template file for the given schema at the indicated
    location.

    Parameters
    ----------
    schema : dict
        Jsonschema for which an xlsx template should be generated.
    out_path : str, Path
        The resulting xlsx template will be written to the file at this path.
    """
    generator = XLSXTemplateGenerator()
    foreign_keys: dict = {}
    generator.generate(schema=schema, foreign_keys=foreign_keys,
                       filepath=out_path, use_ids_as_foreign=True)


def export_container_to_xlsx(records: Container,
                             xlsx_data_filepath: Union[str, Path],
                             include_referenced_entities: bool = False,
                             jsonschema_filepath: Optional[Union[str, Path]] = None,
                             jsondata_filepath: Optional[Union[str, Path]] = None,
                             xlsx_template_filepath: Optional[Union[str, Path]] = None):
    """Export the data of the given records to an xlsx file.

    Parameters
    ----------
    records : Container, Iterable
        List of records to export.
    xlsx_data_filepath : str, Path
        Write the resulting xlsx file to the file at this location.
    include_referenced_entities : bool
        If set to true, any records referenced by properties of those given in
        'records' will also be exported.
        Optional, default False
    jsonschema_filepath : str, Path
        If given, write the jsonschema to this file.
        Optional, default None
    jsondata_filepath : str, Path
        If given, write the json data to this file.
        Optional, default None
    xlsx_template_filepath : str, Path
        If given, write the xlsx template to this file.
        Optional, default None

    Limitations
    -----------

    This function drops any versioning information from versioned references, references are reduced
    to unversioned references.

    """

    # JSON schema and JSON data ############################

    # 1. Generate json schema for all top-level record types

    rt_ids = set()
    rt_names = set()
    recordtypes = set()
    for record in records:
        parent = record.parents[0]
        if parent.id:
            rt_ids.add(parent.id)
        else:
            rt_names.add(parent.name)
    for rt_name in rt_names:
        rt_ids.add(cached_get_entity_by(name=rt_name).id)
    for rt_id in rt_ids:
        recordtypes.add(cached_get_entity_by(eid=rt_id))

    # recordtype_ids = {recordtype.id for recordtype in recordtypes}
    # recordtypes = [execute_query(f"FIND RECORDTYPE WITH (ID = {rt_id})",
    #                              unique=True)
    #                for rt_id in recordtype_ids]
    # recordtype_names = {recordtype.name for recordtype in recordtypes}
    # recordtype_names.add("Sample.Preparation.SourceMaterial")
    # Generate schema and data from the records
    json_schema = _generate_jsonschema_from_recordtypes(recordtypes,
                                                        jsonschema_filepath)

    # 2. Generate json data for all entities.

    # Ensure every record is only handled once by using id as key.
    # entity_ids = {record.id for record in records}
    # If indicated, also get and add the records referenced on the first level
    # in the given container
    # if include_referenced_entities:
    #     for record in records:
    #         for prop in record.properties:
    #             if prop.is_reference() and prop.value is not None:
    #                 try:
    #                     ref_list = prop.value
    #                     if not isinstance(ref_list, list):
    #                         ref_list = [ref_list]
    #                     for element in ref_list:
    #                         if isinstance(element, (int, str)):
    #                             elem_id = element
    #                         elif isinstance(element, Entity):
    #                             elem_id = element.id
    #                         else:
    #                             warnings.warn(f"Cannot handle referenced "
    #                                           f"entity '{prop.value}'")
    #                             continue
    #                         entity_ids.add(elem_id)
    #                 except LinkAheadException as e:
    #                     warnings.warn(f"Cannot handle referenced entity "
    #                                   f"'{prop.value}' because of error '{e}'")

    # Retrieve data
    # if include_referenced_entities:
    #     # new_records = []
    #     # entity_ids = {record.id for record in records}
    #     # for entity_id in entity_ids:
    #     #     entity_id = str(entity_id).split('@')[0]
    #     #     new_records.extend(query(f"FIND ENTITY WITH (ID = {entity_id})"))
    #     # ToDo: Handle Files and other Entities (e.g. Properties) separately
    #     high_level_objs = convert_to_python_object(records, resolve_references=True)
    # else:
    #     high_level_objs = convert_to_python_object(records)

    high_level_objs = convert_to_python_object(records,
                                               resolve_references=include_referenced_entities)
    json_data = _generate_jsondata_from_records(high_level_objs, jsondata_filepath)

    # XLSX generation and filling with data ################

    # 1. Generate xlsx template

    # _generate_xlsx_template_file needs a file name, so use NamedTemporaryFile
    # ToDo: This might not work on windows, if not, fix _generate file handling
    if xlsx_template_filepath is None:
        xlsx_template_file = tempfile.NamedTemporaryFile(suffix='.xlsx')
        xlsx_template_filepath = xlsx_template_file.name
    else:
        xlsx_template_file = None
    _generate_xlsx_template_file(json_schema, xlsx_template_filepath)
    # Fill xlsx file with data
    with warnings.catch_warnings():
        # We have a lot of information in the json data that we do not need
        warnings.filterwarnings("ignore",
                                message="^.*Ignoring path with missing sheet index.*$")
        warnings.filterwarnings("ignore",
                                message="^.*No validation schema.*$")
        fill_template(data=json_data, template=xlsx_template_filepath,
                      result=xlsx_data_filepath)
    # Cleanup
    if xlsx_template_file is not None:
        xlsx_template_file.close()
