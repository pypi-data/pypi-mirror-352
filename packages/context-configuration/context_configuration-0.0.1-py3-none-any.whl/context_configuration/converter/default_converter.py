from typing import Any, Callable, Dict

from ..protocol.property_source import P


def convert_string(value: Any) -> str:
    return str(value)


def convert_int(value: Any) -> int:
    return int(value)


def convert_float(value: Any) -> float:
    return float(value)


def default_converter() -> Dict[type, Callable]:
    return {
        str: convert_string,
        int: convert_int,
        float: convert_float,
    }

def convert(value: Any, converter_list: Dict[type, Callable], clazz: type[P]) -> P:
    for cls, converter_callable in converter_list.items():
        if cls == clazz:
            try:
                return converter_callable(value)
            except Exception as e:
                raise KeyError(f'Error while trying to convert {value} to {clazz.__name__}') from e
    raise KeyError(f"Could not convert property '{value}'to {clazz.__name__}, no converter found!")