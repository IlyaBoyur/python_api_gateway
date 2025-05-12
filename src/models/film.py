import uuid

from pydantic import Field, validator

from .actor import Actor
from .base import BaseSchema
from .director import Director
from .writer import Writer


class FilmFilterSchema(BaseSchema):
    id: uuid.UUID | None = Field(default=None)
    ids: list[uuid.UUID] | None = Field(default=None)
    excluded_ids: uuid.UUID | None = Field(default=None)
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    imdb_rating: tuple[float | None, float | None] | None = Field(default=None)
    # created_range: tuple[datetime | None, datetime | None] | None = Field(default=None)
    pagination: tuple[int, int] | None = Field(default=None)
    order: list[str] | None = Field(default=None)

    @validator("id", "ids", "excluded_ids")
    def validate_uuids(cls, value):
        if value:
            if isinstance(value, list):
                return [str(item) for item in value]
            return str(value)
        return value

class Film(BaseSchema):
    id: uuid.UUID = Field(description="ID")
    title: str = Field(description="Название")
    description: str = Field(description="Описание")
    imdb_rating: float = Field(description="Рейтинг")
    genres: str = Field(description="Жанры")
    actors_names: str = Field(description="Имена актеров")
    directors_names: str = Field(description="Имена режиссеров")
    writers_names: str = Field(description="Имена сценаристов")
    actors: list[Actor] = Field(description="Актеры")
    directors: list[Director] = Field(description="Режиссеры")
    writers: list[Writer] = Field(description="Сценаристы")

    def __repr__(self) -> str:
        return f"Film(id={self.id})"
