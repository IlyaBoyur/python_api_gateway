import uuid
from dataclasses import asdict, dataclass
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, parse_obj_as

from src.providers.services import get_film_service
from src.services.film import FilmFilterSchema, FilmService

from .schemas.film import FilmOutSchema, FilmsResultSchema

router = APIRouter()


@dataclass
class FilmQuery:
    id: uuid.UUID | None = Query(None)
    ids: list[uuid.UUID] | None = Query(None)
    excluded_ids: list[uuid.UUID] | None = Query(None)
    title: str | None = Query(None)
    description: str | None = Query(None)
    imdb_rating: tuple[float | None, float | None] | None = Query(None)
    pagination: tuple[int, int] | None = Query(None)
    order: list[str] | None = Query(None)


@router.get("/{film_id}")
async def film_details(
    film_id: uuid.UUID, film_service: Annotated[FilmService, Depends(get_film_service)]
) -> FilmOutSchema:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return FilmOutSchema.from_entity(film)


@router.get("/")
async def film_list(
    params: Annotated[FilmQuery, Depends(FilmQuery)],
    film_service: Annotated[FilmService, Depends(get_film_service)],
) -> FilmsResultSchema:
    filter_params = parse_obj_as(FilmFilterSchema, asdict(params))
    films = await film_service.filter(filter_params)
    return FilmsResultSchema(results=[FilmOutSchema.from_entity(film) for film in films])
