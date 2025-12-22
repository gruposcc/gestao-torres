#SHELL := /bin/bash

dev:
	@pnpm exec concurrently \
		--names 'FRONTEND, BACKEND' \
		--prefix-colors 'blue, green' \
		--kill-others-on-fail \
		'pnpm run dev' \
		'uv run --env-file .env scripts/dev.py'

create_superuser:
	@uv run --env-file .env scripts/create_superuser.py

migration:
	@uv run --env-file .env alembic revision --autogenerate -m initial  

migrate:
	@uv run --env-file .env alembic upgrade head 

.PHONY: dev migrate migration create_superuser

