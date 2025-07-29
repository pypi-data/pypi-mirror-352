from typing import Dict

from .abstract_property_source import AbstractPropertySource


class DictionaryPropertySource(AbstractPropertySource):

    def __init__(self, properties: Dict[str, any]):
        super().__init__()
        self._properties = properties
