import uuid

from pydantic import Field, validator

from .base import BaseSchema


class PersonFilterSchema(BaseSchema):
    id: uuid.UUID | None = Field(default=None)
    ids: list[uuid.UUID] | None = Field(default=None)
    excluded_ids: list[uuid.UUID] | None = Field(default=None)
    name: str | None = Field(default=None)
    pagination: tuple[int, int] | None = Field(default=None)
    order: list[str] | None = Field(default=None)

    @validator("id", "ids", "excluded_ids")
    def validate_uuids(cls, value):
        if value:
            if isinstance(value, list):
                return [str(item) for item in value]
            return str(value)
        return value


class Person(BaseSchema):
    id: uuid.UUID = Field(description="ID")
    name: str = Field(description="Имя")
