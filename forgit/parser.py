from inspect import getmembers
from typing import Union, Dict, Any, List, Type

from forgit.forges.abstract import Issue, PullRequest, Release

UniversalForgeTypeCls = Union[Issue, PullRequest, Release]
UniversalForgeType = Union[Type[Issue], Type[PullRequest], Type[Release]]


def _get_class_data(input_cls: UniversalForgeTypeCls) -> Dict[str, Any]:
    result = {}
    for key, value in getmembers(input_cls):
        if not key.startswith("_"):
            result[key] = getattr(input_cls, key)

    return result


def _get_type_class_attrs(type_cls: UniversalForgeType) -> List[str]:
    result = []
    # this may be wrong true in the future
    for member in getmembers(type_cls):
        if "__init__" in member:  # member is a tuple
            result += list(member[1].__code__.co_names)
            continue

        if not any([isinstance(item, property) for item in member]):
            continue

        # is property
        for member_item in member:
            if isinstance(member_item, str):
                result.append(member_item)

    return result


def parse_data(
    input_cls: UniversalForgeTypeCls, target_type: UniversalForgeType
) -> Dict[str, Any]:
    input_cls_data = _get_class_data(input_cls)
    target_props_and_attrs = _get_type_class_attrs(target_type)
    result = {}
    for key, value in input_cls_data.items():
        if key in target_props_and_attrs:
            result[key] = value

    # TODO: co s chybejicima datama v resultu
    return result
