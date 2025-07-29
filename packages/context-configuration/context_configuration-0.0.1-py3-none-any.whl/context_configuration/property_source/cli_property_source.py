import sys
from typing import List, Any

from ..property_source.abstract_property_source import AbstractPropertySource


class CLIPropertySource(AbstractPropertySource):

    def __init__(self):
        super().__init__()
        self._properties = {}
        cli_arguments = sys.argv
        argument_list = cli_arguments[1:]
        self._parse_arguments(argument_list)

    def _get(self, name: str) -> Any:
        if name not in self._properties:
            raise KeyError(f"Could not find property '{name}'")
        return self._properties[name]

    def _parse_arguments(self, argument_list: List[str]) -> None:
        while len(argument_list) != 0:
            argument = argument_list.pop(0)
            if argument.startswith("--"):
                self._parse_double_dash_argument(argument, argument_list)
                continue
            if argument.startswith("-"):
                self._parse_single_dash_argument(argument, argument_list)
                continue

    def _parse_double_dash_argument(self, argument: str, argument_list: List[str]) -> None:
        argument = argument[2:]
        if "=" in argument:
            cli_property = argument.split("=", 1)
            if len(cli_property[0]) == 0:
                return
            self._add_to_argument_list(cli_property[0], cli_property[1])
            return

        if len(argument_list) == 0:
            return

        next_arg = argument_list[0]
        if next_arg.startswith("-"):
            return

        self._add_to_argument_list(argument, argument_list.pop(0))

    def _parse_single_dash_argument(self, argument: str, argument_list: List[str]):
        argument = argument[1:]
        if len(argument) == 0:
            return

        if len(argument_list) == 0:
            return

        next_arg = argument_list[0]
        if next_arg.startswith("-"):
            return

        self._add_to_argument_list(argument, argument_list.pop(0))

    def _add_to_argument_list(self, argument_name: str, argument_value: str) -> None:
        argument_value = self._clean_argument_value(argument_value)

        if argument_name not in self._properties:
            self._properties[argument_name] = argument_value
            return

        if isinstance(self._properties[argument_name], list):
            self._properties[argument_name].append(argument_value)
            return

        self._properties[argument_name] = [self._properties[argument_name], argument_value]

    def _clean_argument_value(self, argument_value):
        for character in ["'", '"']:
            if argument_value.startswith(character) and argument_value.endswith(character):
                return argument_value[1:-1]
        return argument_value
