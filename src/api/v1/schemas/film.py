import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.models.base import BaseOutSchema, BaseSchema
from src.models.film import Film

from .actor import ActorOutSchema
from .director import DirectorOutSchema
from .writer import WriterOutSchema


class FilmOutSchema(BaseOutSchema):
    id: uuid.UUID = Field(description="ID")
    title: str = Field(description="Название")
    description: str = Field(description="Описание")
    imdb_rating: float = Field(description="Рейтинг")
    genres: str = Field(description="Жанры")
    actors: list[ActorOutSchema] = Field(description="Актеры", default_factory=list)
    directors: list[DirectorOutSchema] = Field(description="Режиссеры", default_factory=list)
    writers: list[WriterOutSchema] = Field(description="Сценаристы", default_factory=list)

    @classmethod
    def from_entity(cls, film: Film) -> "FilmOutSchema":
        return FilmOutSchema(
            id=film.id,
            title=film.title,
            description=film.description,
            imdb_rating=film.imdb_rating,
            genres=film.genres,
            actors=[ActorOutSchema.from_entity(actors) for actors in film.actors],
            directors=[DirectorOutSchema.from_entity(directors) for directors in film.directors],
            writers=[WriterOutSchema.from_entity(writer) for writer in film.writers],
        )


class FilmsResultSchema(BaseModel):
    results: list[FilmOutSchema]
