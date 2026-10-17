# Run `make setup` once, then `make dev`.
-include .env
STORAGE_URL ?= $(CURDIR)/data
export

.PHONY: setup db dev up down test lint api-client

setup: ## Install both sides and create .env
	@test -f .env || sed "s/^SESSION_SECRET=change-me$$/SESSION_SECRET=$$(openssl rand -hex 32)/" .env.example > .env
	cd backend && uv sync
	cd frontend && pnpm install

db: ## Start Postgres in Docker
	docker compose up -d --wait db

dev: db ## Run backend, worker and frontend with hot reload (http://localhost:5173)
	cd backend && uv run alembic upgrade head
	@trap 'kill 0' INT TERM EXIT; \
	(cd backend && uv run uvicorn liasse.asgi:app --reload --port 8000) & \
	(cd backend && uv run python -m liasse.worker) & \
	(cd frontend && pnpm dev) & \
	wait

up: ## Run the full stack in Docker (http://localhost:$LIASSE_PORT)
	docker compose up -d --build --wait

down: ## Stop the Docker stack
	docker compose down

test: db ## Run backend and frontend tests
	cd backend && uv run pytest
	cd frontend && pnpm test

lint: ## Lint and type-check both sides
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy src tests migrations
	cd frontend && pnpm lint

api-client: ## Regenerate the TypeScript API client from the backend's OpenAPI schema
	cd backend && uv run python -m liasse.openapi > ../frontend/openapi.json
	cd frontend && pnpm api-client
