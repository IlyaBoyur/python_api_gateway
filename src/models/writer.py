import uuid

from pydantic import Field

from .base import BaseSchema


class Writer(BaseSchema):
    id: uuid.UUID = Field(description="ID")
    name: str = Field(description="Имя")
