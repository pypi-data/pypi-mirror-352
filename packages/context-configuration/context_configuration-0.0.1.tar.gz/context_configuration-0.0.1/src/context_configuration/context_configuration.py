from random import random
from typing import List, Callable, Dict, Tuple, Any
from collections import namedtuple

from .converter.default_converter import default_converter, convert
from .converter.iso_format_datetime_converter import IsoFormatDateTimeConverter
from .protocol.property_source import PropertySource, OrderedPropertySource, P




Property = namedtuple('Property', ['argument', 'property_name', 'type'])


class ContextConfiguration(PropertySource):
    """
    Loads the default configuration file from the 'profiles' folder, and if the environment variable 'RF_STAGE'
    is set, it will load the configuration file for this stage as well. The stage configuration overwrites
    the local configuration. The default environment should hold the configuration for the production system.
    """

    _property_sources: List[OrderedPropertySource] = []
    _converter: Dict[type, Callable] = {}
    _immutable: bool = False
    _bean_store: Dict[int, Any] = {}

    def __init__(self, property_sources: List[OrderedPropertySource], converter: Dict[type, Callable]):
        """ Loads the configuration files from disk according to the stage

            Raises
                Exception
                    If the environment variable 'RF_STAGE' is set but no configuration file
                    for the stage could be found
        """
        self._converter = default_converter()
        datetime_converter = IsoFormatDateTimeConverter()
        self._converter[datetime_converter.for_type()] = datetime_converter.convert
        self._property_sources = property_sources
        self._converter.update(converter)

        self._make_immutable()

    def contains_property(self, name: str) -> bool:
        for source in self._property_sources:
            if source.contains_property(name):
                return True
        return False

    def get_property(self, name: str, cls: type[P]) -> P:
        if not self.contains_property(name):
            raise KeyError(f"Could not find property '{name}'")

        for source in self._property_sources:
            if not source.contains_property(name):
                continue

            value = source.get_property(name, cls)
            return convert(value, self._converter, cls)
        raise KeyError(f"Could not find property '{name}'")


    def _make_immutable(self) -> None:
        sorted(self._property_sources, key=lambda source: source.get_order)
        self._immutable = True

    def properties(self, properties: List[Property], is_singleton: bool = True) -> Any:

        def decorator(func) -> Any:
            def wrapper():
                if is_singleton and id(func) in self._bean_store:
                    return self._bean_store[id(func)]
                kwargs = {}
                for prop in properties:
                    kwargs[prop.argument] = self.get_property(prop.property_name, prop.type)
                    kwargs[prop.argument] = f"{kwargs[prop.argument]} {random()}"
                result = func(**kwargs)
                self._bean_store[id(func)] = result
                return result

            return wrapper

        return decorator


class ContextConfigurationBuilder:
    _property_sources: List[OrderedPropertySource] = []
    _converter: Dict[type, Callable] = {}
    _order: 0

    def with_property_source(self, property_source: OrderedPropertySource):
        self._property_sources.append(property_source)
        return self

    def with_converter(self, converter: Tuple[type, Callable]):
        _type, _callable = converter
        self._converter[_type] = callable
        return self

    def build(self) -> ContextConfiguration:
        return ContextConfiguration(self._property_sources, self._converter)
