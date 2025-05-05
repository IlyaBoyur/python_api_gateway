THIS_FILE := $(lastword $(MAKEFILE_LIST))
BACKEND_CONTAINER_NAME := app
COMPOSE_FILES := -f docker-compose.yml


include .env


debugee-on:
	docker compose down app && \
	docker compose run -d -p 5678:5678 -p 8080:8080 app poetry run python -m debugpy --listen 0.0.0.0:5678 -m uvicorn --host 0.0.0.0 --port 8080 --reload src.main:app

debugee-off:
	docker compose kill app && \
	docker compose up -d app

start:
	docker compose $(COMPOSE_FILES) up --remove-orphans -d

stop:
	docker compose $(COMPOSE_FILES) stop $(c)

down:
	docker compose $(COMPOSE_FILES) down $(c)

restart:
	docker compose $(COMPOSE_FILES) restart

rebuild:
	docker compose $(COMPOSE_FILES) up -d --remove-orphans --build

ps:
	docker compose ps

logs:
	docker compose $(COMPOSE_FILES) logs --tail=300 -f $(c)

test:
	docker compose exec $(BACKEND_CONTAINER_NAME) poetry run pytest ./$(c)

shell:
	docker compose $(COMPOSE_FILES) exec $(BACKEND_CONTAINER_NAME) sh

ipython:
	docker compose $(COMPOSE_FILES) exec $(BACKEND_CONTAINER_NAME) poetry run ipython --ext="autoreload"

init:
	make rebuild

redis:
	docker compose exec redis redis-cli

.PHONY: start stop down restart rebuild ps logs test shell ipython init redis
