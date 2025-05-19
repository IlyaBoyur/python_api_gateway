import uuid

from pydantic import Field, validator

from .actor import Actor
from .base import BaseSchema
from .director import Director
from .writer import Writer


class GenreFilterSchema(BaseSchema):
    id: uuid.UUID | None = Field(default=None)
    ids: list[uuid.UUID] | None = Field(default=None)
    excluded_ids: list[uuid.UUID] | None = Field(default=None)
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    pagination: tuple[int, int] | None = Field(default=None)
    order: list[str] | None = Field(default=None)

    @validator("id", "ids", "excluded_ids")
    def validate_uuids(cls, value):
        if value:
            if isinstance(value, list):
                return [str(item) for item in value]
            return str(value)
        return value


class Genre(BaseSchema):
    id: uuid.UUID = Field(description="ID")
    name: str = Field(description="Название")
    description: str = Field(description="Описание")

    def __repr__(self) -> str:
        return f"Genre(id={self.id})"
