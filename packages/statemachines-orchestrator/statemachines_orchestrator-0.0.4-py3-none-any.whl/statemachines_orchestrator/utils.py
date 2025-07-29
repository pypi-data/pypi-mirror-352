"""Utility functions for the statemachines_orchestrator package."""

import sys
from functools import lru_cache
from typing import Any


class _UnknownType:
    pass


UNKNOWN_TYPE = _UnknownType()


def _get_machines_annotations(
    cls: type,
    cls_annotations: dict[str, Any],
) -> dict[str, type | _UnknownType]:
    return {
        machine_name: _get_class(cls, machine_name, cls_annotations[machine_name]) for machine_name in cls_annotations
    }


@lru_cache
def _get_types(cls: type) -> dict[str, type]:
    typing = sys.modules.get("typing")
    if typing is None:
        msg = "The 'typing' module is not available in sys.modules."
        raise ModuleNotFoundError(msg)
    return typing.get_type_hints(cls)


def _get_class(cls: type, machine_name: str, type_or_type_name: str | type) -> type | _UnknownType:
    if isinstance(type_or_type_name, type):
        return type_or_type_name
    try:
        return _get_types(cls)[machine_name]
    except (NameError, KeyError):
        return UNKNOWN_TYPE
