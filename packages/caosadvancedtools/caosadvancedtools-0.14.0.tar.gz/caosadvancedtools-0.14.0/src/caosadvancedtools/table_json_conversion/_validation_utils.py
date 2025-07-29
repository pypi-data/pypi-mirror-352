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
Utilities for validation of conversion / import / export results.
For internal use.
"""

import datetime
import json
from copy import deepcopy
from typing import Union

import jsonschema


def validate_jsonschema(instance: Union[dict, int, str, bool],
                        schema: Union[str, dict]):
    """
    A table_json_conversion compatible variant of jsonschema.validate().
    Accepts instances with datetime instances and None in not-nullable entries.

    Parameters
    ----------
    instance : dict, int, str, bool
        Either a dict or a json entry to check against the given schema.
    schema : str, dict
        Either a dict with the jsonschema to check against, or a path to a file
        containing the same.
    """
    # Helper Functions
    def _in_schema(key, val, schema):
        """
        Checks whether a key: value pair is in the given schema or fulfills the
        criteria of a direct subschema (anyOf, allOf, oneOf).
        """
        if schema.get(key, None) == val:
            return True
        if 'anyOf' in schema:
            return any([_in_schema(key, val, sub) for sub in schema['anyOf']])
        if 'allOf' in schema:
            return all([_in_schema(key, val, sub) for sub in schema['allOf']])
        if 'oneOf' in schema:
            return [_in_schema(key, val, sub) for sub in schema['oneOf']].count(True) == 1
        return False

    def _remove_incompatible_vals(iterable, schema):
        """
        Removes Key: None and datetime instances from nested dicts and lists of
        any depth. Key: None is currently valid as there is no 'obligatory with
        value', and datetime cannot be checked by jsonschema.
        """
        if isinstance(iterable, list):
            schema = schema.get('items', schema)
            for elem in iterable:
                _remove_incompatible_vals(elem, schema)
        elif isinstance(iterable, dict):
            schema = schema.get('properties', schema)
            for key, elem in list(iterable.items()):
                if elem is None:
                    iterable.pop(key)
                elif isinstance(elem, (datetime.date, datetime.datetime)):
                    if (_in_schema('format', 'date', schema[key]) or
                            _in_schema('format', 'date-time', schema[key])):
                        iterable.pop(key)
                elif isinstance(iterable, (dict, list)):
                    try:
                        _remove_incompatible_vals(elem, schema[key])
                    except KeyError:
                        pass
        return iterable

    # If jsonschema is a file, load its content
    if isinstance(schema, str) and schema.endswith(".json"):
        with open(schema, encoding="utf-8") as content:
            schema = json.load(content)
    assert isinstance(schema, dict)
    # If instance is not a dict, remove_incompatible_values would not remove
    # the value if it is valid, so we need to check manually by wrapping
    instance = deepcopy(instance)
    if not isinstance(instance, dict):
        if _remove_incompatible_vals({'key': instance}, {'key': schema}) == {}:
            return
    # Clean dict and validate
    instance = _remove_incompatible_vals(deepcopy(instance), schema)
    jsonschema.validate(instance, schema=schema)
