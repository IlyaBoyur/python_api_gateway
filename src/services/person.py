from functools import lru_cache

from src.common.key_value_database import IKeyValueDatabase
from src.common.search_engine import ISearchEngine
from src.common.search_engine.filter_fields import (
    Filter,
    InFilter,
    LimitOffsetFilter,
    NotInFilter,
    OrderingField,
    OrderingFilter,
    SearchFilter,
)
from src.common.search_engine.filtersets import AsyncFilterSet
from src.models.base import BaseSchema
from src.models.person import Person, PersonFilterSchema

from .base import BaseEntityService

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5
PERSON_INDEX = "persons"


class PersonFilterSet(AsyncFilterSet):
    id = Filter("id")
    ids = InFilter("id")
    excluded_ids = NotInFilter("id")
    name = SearchFilter("name")
    pagination = LimitOffsetFilter("pagination")
    order = OrderingFilter(
        id=OrderingField("id"),
        name=OrderingField("name.raw"),
    )


class PersonService(BaseEntityService[Person, PersonFilterSchema]):
    """Cодержит бизнес-логику по работе с персонами."""

    schema: type[BaseSchema] = Person
    filter_set: AsyncFilterSet = PersonFilterSet
    index_name: str = PERSON_INDEX
    cache_expire_secs: int = PERSON_CACHE_EXPIRE_IN_SECONDS

    def __init__(self, key_value_database: IKeyValueDatabase, search_engine: ISearchEngine) -> None:
        super().__init__(key_value_database, search_engine, self.index_name, self.cache_expire_secs)
