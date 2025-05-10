import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.providers.services.film import get_film_service
from src.services.film import FilmService

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str


@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: uuid.UUID, film_service: Annotated[FilmService, Depends(get_film_service)]
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return Film(id=str(film.id), title=film.title)
