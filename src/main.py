import logging

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, ORJSONResponse

from src.api.v1.router import include_routers
from src.common.exceptions import RepositoryError, ValidationServiceError
from src.common.key_value_database import RedisDatabase
from src.common.search_engine import ElasticDatabase
from src.common.uvloop import activate_uvloop
from src.core.logger import LOGGING
from src.providers import key_value_database, search_engine
from src.providers.settings import app_settings

app = FastAPI(
    title=app_settings.app.name,
    docs_url="/v1/docs",
    openapi_url="/v1/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    """Подключиться к базам при старте сервера."""
    activate_uvloop()
    key_value_database.redis_database = RedisDatabase.build(config=app_settings.redis.dict())
    search_engine.elastic = ElasticDatabase.build(config=app_settings.es.dict())


@app.on_event("shutdown")
async def shutdown():
    """Отключиться от баз при выключении сервера."""
    await key_value_database.redis_database.close()
    await search_engine.elastic.close()


app.include_router(include_routers())



@app.exception_handler(ValidationServiceError)
async def unicorn_exception_handler(request: Request, exc: ValidationServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status, content={"message": exc.message})


@app.exception_handler(RepositoryError)
async def repository_exception_handler(request: Request, exc: RepositoryError) -> JSONResponse:
    return JSONResponse(status_code=exc.status, content={"message": exc.message})


if __name__ == "__main__":
    # Приложение должно запускаться с помощью команды
    # `uvicorn main:app --host 0.0.0.0 --port 8080`
    # Но таким способом проблематично запускать сервис в дебагере,
    # поэтому сервер приложения для отладки запускаем здесь
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
