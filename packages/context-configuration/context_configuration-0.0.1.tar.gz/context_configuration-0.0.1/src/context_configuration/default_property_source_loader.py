import os
from pathlib import Path
from typing import List, Any

from property_source.pyyaml_property_source import PyYAMLPropertySource
from protocol.property_source import PropertySource


class DefaultPropertySourcesLoader:
    property_sources: List[PropertySource] = []
    stage_config_file_pattern = "application-{profile}.yaml"

    def __init__(self, profiles: List[str], config_directory: str = None):
        for profile in profiles:
            self._add_property_source(profile)
        if config_directory is not None:
            self.config_directory = config_directory
        self.config_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "profiles"))

    def get_property_sources(self) -> List[PropertySource]:
        return self.property_sources

    def _add_property_source(self, profile: str) -> None:
        property_file_name = self.stage_config_file_pattern.format(profile=profile)
        property_file_path = Path(self.__get_absolute_file_path(property_file_name))
        config = PyYAMLPropertySource(property_file_path)
        self.property_sources.append(config)

    def __get_absolute_file_path(self, file) -> str | None | Any:
        if os.path.isfile(file):
            return file

        file_path = os.path.join(self.config_directory, file)
        if os.path.isfile(file_path):
            return str(file_path)

        return None
