from dataclasses import dataclass, is_dataclass

from ..protocol.converter import Converter, T
import inspect
import typing

class DataclassConverter(Converter[T: dataclass]):

    def __init__(self, cls: T):
        if not is_dataclass(cls):
            raise ValueError(f"Expecting class '{cls}' of type dataclass.")
        self._cls = cls

    def for_type(self) -> dataclass:
        return self._cls

    def convert(self, properties) -> dataclass:
        if not isinstance(properties, dict):
            raise ValueError("Given value must be a dict, cannot convert to a dataclass.")

        sig = inspect.signature(self._cls)

        kw_arguments = {}
        for param in sig.parameters.values():
            kw_arguments[param.name] = None
            if param.name not in properties:
                if param.default != inspect.Parameter.empty:
                    properties[param.name] = param.default
                    continue
                if param.annotation == typing.Optional[str]:
                    continue
                if param.annotation == typing.Optional[int]:
                    continue
                if param.annotation == typing.Optional[float]:
                    continue
                raise ValueError(f"Required key '{param.name}' not found in configuration parameters.")
            if type(properties[param.name]) != param.annotation:
                raise ValueError(f"Required key '{param.name}' is of wrong type "
                                 f"(expected: '{param.annotation}', "
                                 f"given: '{type(properties[param.name])}'.")
            kw_arguments[param.name] = properties[param.name]
        try:
            return self._cls(**kw_arguments)
        except ValueError as e:
            raise ValueError(f"Could not convert '{properties}' to dataclass of type '{self._cls}'.") from e
