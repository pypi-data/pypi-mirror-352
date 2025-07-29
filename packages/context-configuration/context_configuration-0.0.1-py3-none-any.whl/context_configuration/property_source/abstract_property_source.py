from abc import ABC
from typing import Dict, Callable, Optional, Any

from ..converter.default_converter import default_converter, convert
from ..protocol.converter import Converter
from ..protocol.property_source import OrderedPropertySource, P


class AbstractPropertySource(OrderedPropertySource, ABC):
    _properties: Optional[Dict[str, Any]] = None
    _converter: Dict[type, Callable] = {}
    _order: int = 0

    def __init__(self, order=0):
        self._order = order
        self._converter = default_converter()

    def add_converter(self, converter: Converter):
        self._converter[converter.for_type()] = converter.convert

    def contains_property(self, name: str) -> bool:
        try:
            self._get(name)
            return True
        except KeyError:
            return False

    def get_property(self, name: str, cls: Optional[P] = None):
        if (name is None) or (name == "") or (".." in name) or (name.startswith(".")) or (name.endswith(".")):
            raise KeyError("Property name cannot be empty, start or end with a dot "
                           "or contain two consecutive dots ('..')")

        value = self._get(name)

        if cls is None:
            return value

        if type(value) is cls:
            return value

        return convert(value, self._converter, cls)

    def get_order(self) -> int:
        return self._order

    def _get(self, name: str) -> Any:
        key_levels = name.split(".")
        properties_level = self._properties
        while 0 < len(key_levels):
            key = key_levels.pop(0)
            if key not in properties_level:
                raise KeyError(f"Could not find property '{name}'")
            properties_level = properties_level[key]
        return properties_level
