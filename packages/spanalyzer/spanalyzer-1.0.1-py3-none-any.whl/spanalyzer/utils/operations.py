# Script containing some operations that will be used through the spanalyzer

import os

import json

from copy import deepcopy

from typing import Any
from typing import Dict
from typing import List

from spanalyzer.python.script import FunctionSpecs
from spanalyzer.python.constants.keywords import PythonTelemetryKeywords

from spanalyzer.constants.telemetry import TelemetryCall


def conciliation(
    functions_lst: List[FunctionSpecs], telemetry_lst: Dict[str, Dict]
) -> Dict:
    """
    Function that will be used to conciliate the functions and the telemetry details.

    Args:
        functions_lst [List[FunctionSpecs]]: list of functions with their specs
        telemetry_lst [Dict[str, Dict]]: dictionary of telemetry details

    Returns:
        Dict: dictionary of telemetry details

    _Example_:
        >>> functions_lst = [
        ...     FunctionSpecs(
        ...         name='function_1',
        ...         start_lineno=3,
        ...         end_lineno=10,
        ...     ),
        ...     FunctionSpecs(
        ...         name='function_2',
        ...         start_lineno=13,
        ...         end_lineno=20,
        ...     ),
        ... ]
        >>> telemetry_lst = {
        ...     'tracers': [
        ...         {'name': 'test_tracer_1', 'line_number': 1, 'args': None},
        ...         {'name': 'test_tracer_2', 'line_number': 24, 'args': None},
        ...     ],
        ...     'spans': [
        ...         {'name': 'test_span_1', 'line_number': 12, 'args': None},
        ...         {'name': 'test_span_2', 'line_number': 24, 'args': None},
        ...     ],
        ...     'attributes': [
        ...         {'name': 'test_attribute_1', 'line_number': 19, 'args': None},
        ...         {'name': 'test_attribute_2', 'line_number': 24, 'args': None},
        ...     ],
        ...     'events': [
        ...         {'name': 'test_event_1', 'line_number': 2, 'args': None},
        ...         {'name': 'test_event_2', 'line_number': 13, 'args': None},
        ...     ],
        ...     'exceptions': {
        ...         2: True,
        ...     },
        ...     'ends': {
        ...         19: True,
        ...     },
        ...     'counter': [
        ...         {'name': 'test_counter_1', 'line_number': 19, 'args': None},
        ...         {'name': 'test_counter_2', 'line_number': 24, 'args': None},
        ...     ],
        ... }
        >>> conciliation(functions_lst, telemetry_lst)
        {
            'tracers': [
                {'name': 'test_tracer_1', 'line_number': 1, 'args': None},
                {'name': 'test_tracer_2', 'line_number': 24, 'args': None},
            ],
            'spans': [
                {'name': 'test_span_1', 'line_number': 12, 'args': None},
                {'name': 'test_span_2', 'line_number': 24, 'args': None},
            ],
            'attributes': [
                {'name': 'test_attribute_2', 'line_number': 24, 'args': None},
            ],
            'events': [
                {'name': 'test_event_1', 'line_number': 2, 'args': None},
                {'name': 'test_event_2', 'line_number': 13, 'args': None},
            ],
            'exceptions': {
                2: True,
            },
            'ends': {
                19: True,
            },
            'functions': {
                'function_1': {
                    'attributes': [
                        {'name': 'test_attribute_1', 'line_number': 19, 'args': None},
                    ],
                },
                'function_2': {
                    'events': [
                        {'name': 'test_event_2', 'line_number': 13, 'args': None},
                    ],
                    'ends': True,
                    'counter': [
                        {'name': 'test_counter_1', 'line_number': 19, 'args': None},
                    ],
                },
            },
        }
    """

    def is_in_function(value: int, function: FunctionSpecs) -> bool:
        """
        Check if the provided value is within the range of the function.

        Args:
            value [int]: value to check
            function [FunctionSpecs]: function to check

        Returns:
            bool: True if the value is within the range, False otherwise
        """

        return value in range(function.start_lineno, function.end_lineno)

    base_structure = deepcopy(PythonTelemetryKeywords.get_attributes_structure())

    output = {
        **base_structure,
        "functions": {
            func.name: {
                "docstring": func.docstring,
                **deepcopy(base_structure),
            }
            for func in functions_lst
        },
    }

    for key, value in telemetry_lst.items():
        for item in value:
            matched = False
            for func in functions_lst:
                if is_in_function(item["line_number"], func):
                    output["functions"][func.name][key].append(item)
                    matched = True
                    break
            if not matched:
                output[key].append(item)

    return filter_empty_dict(output)


def write_json(data: Dict, path: str):
    """
    Function that will create a json file with the data provided.

    Args:
        data [Dict]: data to be written into the json file
        path [str]: path to the json file
    """

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def filter_empty_dict(d: Dict, empty_values: List[Any] = [None, [], {}]) -> Dict:
    """
    Remove all the entries from the dictionary that are empty.

    Args:
        d (Dict): dictionary to filter
        empty_values (List[Any]): list of values to consider as empty

    Returns:
        Dict: filtered dictionary
    """

    keys_to_delete = []

    for key, value in d.items():
        if value in empty_values:
            keys_to_delete.append(key)
        elif isinstance(value, dict):
            d[key] = filter_empty_dict(value, empty_values)

    for key in keys_to_delete:
        del d[key]

    return d


def remove_call_duplicates(lst: List[TelemetryCall]) -> List[TelemetryCall]:
    """
    Remove duplicates from the list of telemetry calls.

    Args:
        lst (List[TelemetryCall]): list of telemetry calls

    Returns:
        List[TelemetryCall]: list of telemetry calls without duplicates

    _Example_:
        >>> lst = [
        ...     TelemetryCall(name='test_tracer_1', line_number=1, args=None),
        ...     TelemetryCall(name='test_tracer_2', line_number=1, args=None),
        ...     TelemetryCall(name='test_tracer_3', line_number=2, args=None),
        ...     TelemetryCall(name='test_tracer_1', line_number=1, args=None),
        ...     TelemetryCall(name='test_tracer_2', line_number=1, args=None),
        ... ]
        >>> remove_call_duplicates(lst)
        [
            TelemetryCall(name='test_tracer_1', line_number=1, args=None),
            TelemetryCall(name='test_tracer_2', line_number=1, args=None),
            TelemetryCall(name='test_tracer_3', line_number=2, args=None),
        ]
    """

    call_per_line = {}

    for call in lst:
        if call.line_number not in call_per_line:
            call_per_line[call.line_number] = call

    return list(call_per_line.values())


def folder_trim(lst: List[Dict], folder_key: str = "script") -> List[Dict]:
    """
    Remove the folder from the script path.

    Args:
        lst (List[Dict]): list of dictionaries
        folder_key (str): key of the folder in the script path

    Returns:
        List[Dict]: list of dictionaries with the folder trimmed

    _Example_:
        >>> lst = [
        ...     {'script': 'path/to/the/folder/subfolder/script.py', 'attribute_1': 'val1'},
        ...     {'script': 'path/to/the/folder/script1.py', 'attribute_2': 'val2'},
        ... ]
        >>> folder_trim(lst, folder_key='script')
        [
            {'script': 'folder/subfolder/script.py', 'attribute_1': 'val1'},
            {'script': 'folder/script1.py', 'attribute_2': 'val2'},
        ]
    """

    def find_folder_to_keep(paths: List[str]) -> str:
        """
        Find the folder that should be kept from the list of paths provided.

        Args:
            paths (List[str]): list of paths

        Returns:
            str: folder to keep

        _Example_:
            >>> paths = ['path/to/the/folder/subfolder/script.py', 'path/to/the/folder/script1.py']
            >>> find_folder_to_keep(paths)
            'folder'
        """

        split_paths = [path.split(os.sep) for path in paths]
        common_parts = os.path.commonprefix(split_paths)

        return os.sep.join(common_parts)

    def trim(path: str, base_folder: str) -> str:
        """
        Trim the path to the base folder.

        Args:
            path (str): path to trim
            base_folder (str): base folder

        Returns:
            str: trimmed path

        _Example_:
            >>> path = 'path/to/the/folder/subfolder/script.py'
            >>> base_folder = 'path/to/the/folder'
            >>> trim(path, base_folder)
            'folder/subfolder/script.py'
        """

        return path.replace(base_folder, "")

    script_paths = [item["script"] for item in lst]
    base_folder = (
        os.sep.join(find_folder_to_keep(script_paths).split(os.sep)[:-1]) + os.sep
    )

    return [{**item, "script": trim(item["script"], base_folder)} for item in lst]
