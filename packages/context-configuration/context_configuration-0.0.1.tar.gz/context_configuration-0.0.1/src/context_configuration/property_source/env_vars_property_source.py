import os
from typing import Any

from .abstract_property_source import AbstractPropertySource


class EnvVarsPropertySource(AbstractPropertySource):

    def __init__(self):
        super().__init__()

    def _get(self, name: str) -> Any:
        if name not in os.environ:
            raise KeyError(f"Could not find property '{name}'")
        return os.environ[name]
