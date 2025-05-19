from fastapi import APIRouter

from src.api.v1.film import router as film_router
from src.api.v1.genre import router as genre_router
from src.api.v1.person import router as person_router


def include_routers() -> APIRouter:
    main_router = APIRouter()
    main_router.include_router(film_router, prefix="/v1/films", tags=["Films"])
    main_router.include_router(genre_router, prefix="/v1/genres", tags=["Genres"])
    main_router.include_router(person_router, prefix="/v1/persons", tags=["Persons"])
    return main_router
