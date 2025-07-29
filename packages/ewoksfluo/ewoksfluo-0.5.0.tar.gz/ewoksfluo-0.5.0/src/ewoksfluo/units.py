from pint import Unit
from pint import UnitRegistry

_UNIT_REGISTRY = None


def unit_registry():
    global _UNIT_REGISTRY
    if _UNIT_REGISTRY is None:
        _UNIT_REGISTRY = UnitRegistry()
    return _UNIT_REGISTRY


def units_as_str(units: Unit) -> str:
    return f"{units:~}"
