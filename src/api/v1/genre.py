import uuid
from dataclasses import asdict, dataclass
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, parse_obj_as

from src.api.cache import api_cache
from src.providers.services import get_genre_service
from src.services.genre import GenreFilterSchema, GenreService

from .schemas.genre import GenreMultiOutSchema, GenreOutSchema

router = APIRouter()


@dataclass
class GenreQuery:
    id: uuid.UUID | None = Query(None)
    ids: list[uuid.UUID] | None = Query(None)
    excluded_ids: list[uuid.UUID] | None = Query(None)
    name: str | None = Query(None)
    description: str | None = Query(None)
    pagination: tuple[int, int] | None = Query(None)
    order: list[str] | None = Query(None)


@router.get("/{genre_id}")
async def genre_details(
    genre_id: uuid.UUID,
    genre_service: Annotated[GenreService, Depends(get_genre_service)],
) -> GenreOutSchema:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return GenreOutSchema.from_entity(genre)


@router.get("/")
@api_cache(namespace="v1")
async def genre_list(
    params: Annotated[GenreQuery, Depends(GenreQuery)],
    genre_service: Annotated[GenreService, Depends(get_genre_service)],
) -> GenreMultiOutSchema:
    filter_params = parse_obj_as(GenreFilterSchema, asdict(params))
    genres = await genre_service.get_multi(filter_params)
    return GenreMultiOutSchema(results=[GenreOutSchema.from_entity(genre) for genre in genres])
