import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.models.base import BaseOutSchema, BaseSchema
from src.models.genre import Genre

from .actor import ActorOutSchema
from .director import DirectorOutSchema
from .writer import WriterOutSchema


class GenreOutSchema(BaseOutSchema):
    id: uuid.UUID = Field(description="ID")
    name: str = Field(description="Название")
    description: str = Field(description="Описание")

    @classmethod
    def from_entity(cls, genre: Genre) -> "GenreOutSchema":
        return GenreOutSchema(
            id=genre.id,
            name=genre.name,
            description=genre.description,
        )


class GenreMultiOutSchema(BaseModel):
    results: list[GenreOutSchema]
