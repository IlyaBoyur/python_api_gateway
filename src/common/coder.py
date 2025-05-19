import abc
import datetime
import decimal
import json
from typing import Any

from fastapi.encoders import jsonable_encoder


class JsonEncoder(json.JSONEncoder):
    def default(self, o: Any) -> dict:
        if isinstance(o, datetime.datetime):
            return {"val": str(o), "_spec_type": "datetime"}
        elif isinstance(o, datetime.date):
            return {"val": str(o), "_spec_type": "date"}
        elif isinstance(o, decimal.Decimal):
            return {"val": str(o), "_spec_type": "decimal"}
        else:
            return jsonable_encoder(o)


class ICoder(abc.ABC):
    @abc.abstractclassmethod
    def encode(cls, value: Any) -> str:
        ...

    @abc.abstractclassmethod
    def decode(cls, value: Any) -> Any:
        ...


class NoDecodeJsonCoder(ICoder):
    """Json Coder, который при декодировании возвращает json строку."""

    @classmethod
    def encode(cls, value: Any) -> str:
        return json.dumps(value, cls=JsonEncoder)

    @classmethod
    def decode(cls, value: Any) -> str:
        return value
