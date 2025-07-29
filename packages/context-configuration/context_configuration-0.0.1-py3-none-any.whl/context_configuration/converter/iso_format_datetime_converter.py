from datetime import datetime
from typing import Any

from ..protocol.converter import Converter, T


class IsoFormatDateTimeConverter(Converter[datetime]):


    def for_type(self) -> T:
        return datetime

    def convert(self, properties: Any) -> datetime:
        if not isinstance(properties, str):
            raise ValueError("Given value must be a string, cannot convert to datetime")
        try:
            return datetime.fromisoformat(properties)
        except ValueError as e:
            raise ValueError(f"Could not convert '{properties}' to datetime") from e
