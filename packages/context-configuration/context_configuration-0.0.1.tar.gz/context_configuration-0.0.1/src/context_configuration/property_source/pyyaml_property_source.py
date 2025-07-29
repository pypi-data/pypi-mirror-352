from pathlib import Path

import yaml

from .abstract_property_source import AbstractPropertySource


class PyYAMLPropertySource(AbstractPropertySource):

    def __init__(self, filename: Path) -> None:
        super().__init__()
        with open(filename, 'r') as file:
            self._properties = yaml.safe_load(file)
