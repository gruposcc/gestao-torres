#SHELL := /bin/bash

dev-full:
	@pnpm exec concurrently \
		--names 'FRONTEND, BACKEND' \
		--prefix-colors 'blue, green' \
		--kill-others-on-fail \
		'pnpm run dev' \
		'uv run --env-file .env scripts/dev.py'

dev:
	@uv run --env-file .env scripts/dev.py

create_superuser:
	@uv run --env-file .env scripts/create_superuser.py

migration:
	@cd ./src && uv run --env-file .env alembic revision --autogenerate -m initial

migrate:
	@cd ./src && uv run --env-file ../.env alembic upgrade head

prune_db:
	@docker volume rm really_aio_torres_db_data

prune_migrations:
	@rm -r ./src/alembic/versions/*.py

.PHONY: dev migrate migration create_superuser prune_db prune_migrations dev-full
