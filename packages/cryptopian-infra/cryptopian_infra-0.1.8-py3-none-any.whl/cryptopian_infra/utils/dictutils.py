from copy import deepcopy
from decimal import Decimal


def merge_dict(base_dict: dict, override_dict: dict):
    result = deepcopy(base_dict)
    for key, value in override_dict.items():
        if key not in result:
            result[key] = value
        else:
            numeric_types = [int, float, Decimal]
            assert ((isinstance(base_dict[key], type(value)) and isinstance(value, type(base_dict[key]))) or
                    type(value) in numeric_types and type(base_dict[key]) in numeric_types), f"Unmatched types for key '{key}'"
            if type(value) is dict:
                result[key] = merge_dict(base_dict[key], value)
            else:
                result[key] = value
    return result


def remove_empty_fields(data: dict):
    result = {}
    for key, value in data.items():
        if value is not None and value != '' and value != []:
            if isinstance(value, dict):
                value = remove_empty_fields(value)
            result[key] = value
    return result
