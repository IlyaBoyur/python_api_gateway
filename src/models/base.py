import uuid

import orjson
from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps


class BaseOutSchema(BaseSchema):
    id: int | uuid.UUID
