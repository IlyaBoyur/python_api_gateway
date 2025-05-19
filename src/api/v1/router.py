from fastapi import APIRouter

from src.api.v1.film import router as film_router


def include_routers() -> APIRouter:
    main_router = APIRouter()
    main_router.include_router(film_router, prefix="/v1/films", tags=["Films"])
    return main_router

