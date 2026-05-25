.PHONY: up down shell test lint migrate seed

up:
	docker compose up -d

down:
	docker compose down

shell:
	flask shell

test:
	pytest

test-unit:
	pytest -m unit

lint:
	ruff check . && ruff format --check .

migrate:
	flask db upgrade

seed:
	python scripts/seed_db.py

worker:
	rq worker --url $$REDIS_URL submissions

