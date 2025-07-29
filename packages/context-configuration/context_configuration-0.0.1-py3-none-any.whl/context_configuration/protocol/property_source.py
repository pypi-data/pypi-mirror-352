from typing import Protocol, TypeVar

P = TypeVar('P')


class PropertySource(Protocol):

    def contains_property(self, name: str) -> bool: ...

    def get_property(self, name: str, clazz: type[P]) -> P: ...


class OrderedPropertySource(PropertySource):

    def get_order(self) -> int: ...
