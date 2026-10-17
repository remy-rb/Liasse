# 01: Skeleton: backend, frontend, compose, Makefile

**What to build:** A developer runs `make setup` then `make dev` and gets Postgres (with pgvector), the FastAPI backend and the React PWA shell running with hot reload. The shell is a mobile-first layout built with Tailwind CSS and shadcn/ui defaults (header, navigation placeholders for Documents, Inbox, Search, Ask, Upload) and shows the backend's health, fetched through the TypeScript client generated from the OpenAPI schema. Settings are validated at startup and the backend refuses to start with a clear message when a required setting is missing. This establishes the repo layout (`backend/` with uv, `frontend/` in the bulletproof-react structure, root Docker Compose and Makefile), Alembic migrations, and the test and lint setup every later ticket builds on.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [x] `make setup` installs both sides and creates `.env` from a commented `.env.example`
- [x] `make dev` starts Postgres in Docker plus backend and frontend with hot reload
- [x] `make up` / `make down` run and stop the full stack in Docker
- [x] A health endpoint reports backend and database status; the shell displays it via the generated client and TanStack Query
- [x] `make api-client` regenerates the TypeScript client from the OpenAPI schema
- [x] Missing or invalid settings stop the backend at startup with a message naming the setting
- [x] Alembic is configured with an initial (empty or base) migration that `make dev` applies
- [x] Frontend follows the bulletproof-react layout (`app`, `features`, `components`, `lib`) with Tailwind and shadcn/ui installed; the shell is usable at phone width
- [x] `make test` runs pytest (with a real Postgres) and Vitest, each with at least one passing test through the highest seam (HTTP API / rendered component)
- [x] `make lint` lints and type-checks both sides
