from enum import Enum
from datetime import datetime
from typing import Any
from sslib.helper.string import StringHelper


class DictEx:
    def to_dict(self, include_none: bool = False, camel_case: bool = True) -> dict:
        output = {}
        for k, v in self.__dict__.items():
            if not include_none and v is None:
                continue
            if camel_case:
                k = StringHelper.camel_case(k)
            output[k] = self._convert(v)
        return output

    def _convert(self, source: Any) -> Any:
        if isinstance(source, datetime):
            return StringHelper.datetime(source)
        if isinstance(source, Enum):
            return source.value

        from sslib.base import Entity

        if isinstance(source, list) is True or isinstance(source, Entity) is True:
            from sslib.util import JsonUtil

            return JsonUtil.from_json(JsonUtil.to_json(source=source))
        return source
