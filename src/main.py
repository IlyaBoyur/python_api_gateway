import logging

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from redis.asyncio import ConnectionPool, Redis
from src.api.v1 import film
from src.core.config import app_settings
from src.core.logger import LOGGING
from src.db import elastic, redis

app = FastAPI(
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=app_settings.app.name,
    # Адрес документации в красивом интерфейсе
    docs_url="/v1/docs",
    # Адрес документации в формате OpenAPI
    openapi_url="/v1/openapi.json",
    # Можно сразу сделать небольшую оптимизацию сервиса
    # и заменить стандартный JSON-сереализатор на более шуструю версию, написанную на Rust
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    """Подключиться к базам при старте сервера."""
    connection_pool: ConnectionPool = ConnectionPool.from_url(
        url=app_settings.redis.dsn, encoding="utf8", decode_responses=True
    )
    redis.redis = Redis(connection_pool=connection_pool)
    elastic.es = AsyncElasticsearch(hosts=[app_settings.es.dsn])


@app.on_event("shutdown")
async def shutdown():
    """Отключиться от баз при выключении сервера."""
    await redis.redis.close()
    await elastic.es.close()


app.include_router(film.router, prefix="/v1/films", tags=["films"])

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
