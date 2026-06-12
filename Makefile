.PHONY: help up down build logs test lint clean reset migrate seed

SERVICES = backend frontend worker

help:
	@echo 'AI RAG Assistant - Makefile'
	@echo ''
	@echo '  make up        Start all services (detached)'
	@echo '  make down      Stop all services'
	@echo '  make build     Build all images'
	@echo '  make logs      Tail logs'
	@echo '  make test      Run backend tests'
	@echo '  make reset     Clean rebuild + up'
	@echo '  make migrate   Run DB migrations'
	@echo '  make seed      Upload sample documents'

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

test:
	docker compose exec backend pytest

lint:
	docker compose exec backend ruff check .
	docker compose exec backend mypy .

reset: down
	docker compose down -v
	docker compose up -d --build

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python -m app.workers.seed

ps:
	docker compose ps

worker:
	docker compose exec worker celery -A app.workers.celery_app worker --loglevel=info
