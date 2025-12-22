dev:
	@uv run --env-file .env scripts/dev.py

migration:
	@uv run --env-file .env alembic revision --autogenerate -m initial  

migrate:
	@uv run --env-file .env alembic upgrade head 

.PHONY: dev

