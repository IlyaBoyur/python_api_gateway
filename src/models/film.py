import uuid

from pydantic import Field

from .actor import Actor
from .base import BaseSchema
from .director import Director
from .writer import Writer


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
