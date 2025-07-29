from typing import Protocol, TypeVar, Any

T = TypeVar('T')


class Converter(Protocol[T]):

    def for_type(self) -> T: ...

    def convert(self, properties: Any) -> T: ...
