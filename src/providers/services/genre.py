from functools import lru_cache

from fastapi import Depends

from src.common.key_value_database import IKeyValueDatabase
from src.common.search_engine import ElasticSearchEngine, ISearchEngine
from src.providers.key_value_database import get_key_value_database
from src.providers.search_engine import get_search_engine
from src.services.genre import GenreService


@lru_cache
def get_genre_service(
    key_value_database: IKeyValueDatabase = Depends(get_key_value_database),
    search_engine: ISearchEngine = Depends(get_search_engine),
) -> GenreService:
    return GenreService(key_value_database, search_engine)
