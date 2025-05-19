import uuid
from dataclasses import asdict, dataclass
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, parse_obj_as

from src.providers.cache import api_cache
from src.providers.services.person import get_person_service
from src.services.person import PersonFilterSchema, PersonService

from .schemas.person import PersonMultiOutSchema, PersonOutSchema

router = APIRouter()


@dataclass
class PersonQuery:
    id: uuid.UUID | None = Query(None)
    ids: list[uuid.UUID] | None = Query(None)
    excluded_ids: list[uuid.UUID] | None = Query(None)
    name: str | None = Query(None)
    pagination: tuple[int, int] | None = Query(None)
    order: list[str] | None = Query(None)


@router.get("/{person_id}")
async def person_details(
    person_id: uuid.UUID,
    person_service: Annotated[PersonService, Depends(get_person_service)],
) -> PersonOutSchema:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return PersonOutSchema.from_entity(person)


@router.get("/")
@api_cache(namespace="v1")
async def person_list(
    params: Annotated[PersonQuery, Depends(PersonQuery)],
    person_service: Annotated[PersonService, Depends(get_person_service)],
) -> PersonMultiOutSchema:
    filter_params = parse_obj_as(PersonFilterSchema, asdict(params))
    persons = await person_service.get_multi(filter_params)
    return PersonMultiOutSchema(results=[PersonOutSchema.from_entity(person) for person in persons])
