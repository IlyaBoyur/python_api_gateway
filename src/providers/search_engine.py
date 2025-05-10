from functools import lru_cache

from fastapi import Depends

from src.common.search_engine import ElasticSearchEngine, ISearchEngine
from src.common.search_engine.elastic import ElasticDatabase
from src.core.config import Settings
from src.providers.settings import get_settings

elastic: ElasticDatabase = None


@lru_cache
def get_elastic_database() -> ElasticDatabase:
    return elastic


@lru_cache
def get_search_engine(
    es_database: ElasticDatabase = Depends(get_elastic_database),
) -> ISearchEngine:
    return ElasticSearchEngine(client=es_database)
