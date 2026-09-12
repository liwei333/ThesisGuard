.PHONY: help dev dev-api dev-web worker down up logs rebuild test lint typecheck migrate migrate-gen db-reset frontend-install frontend-check

# Default target
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ===========================================
# Docker Compose
# ===========================================
up: ## Start all services with Docker Compose
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## Show logs from all services
	docker compose logs -f

rebuild: ## Rebuild and restart all services
	docker compose down
	docker compose build --no-cache
	docker compose up -d

ps: ## Show running containers
	docker compose ps

# ===========================================
# Development (local, without Docker)
# ===========================================
dev-api: ## Run API locally (requires local postgres/redis/minio)
	uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

dev-web: ## Run web locally
	cd apps/web && npm run dev

worker: ## Run worker locally
	python -m apps.worker.main

# ===========================================
# Database
# ===========================================
migrate: ## Run database migrations
	DATABASE_URL=postgresql+asyncpg://$${POSTGRES_USER:-thesisguard}:$${POSTGRES_PASSWORD:-thesisguard_dev_password}@127.0.0.1:$${POSTGRES_HOST_PORT:-15432}/$${POSTGRES_DB:-thesisguard} alembic -c migrations/alembic.ini upgrade head

migrate-gen: ## Generate new migration (use: make migrate-gen MESSAGE="description")
	DATABASE_URL=postgresql+asyncpg://$${POSTGRES_USER:-thesisguard}:$${POSTGRES_PASSWORD:-thesisguard_dev_password}@127.0.0.1:$${POSTGRES_HOST_PORT:-15432}/$${POSTGRES_DB:-thesisguard} alembic -c migrations/alembic.ini revision --autogenerate -m "$(MESSAGE)"

migrate-down: ## Rollback one migration
	DATABASE_URL=postgresql+asyncpg://$${POSTGRES_USER:-thesisguard}:$${POSTGRES_PASSWORD:-thesisguard_dev_password}@127.0.0.1:$${POSTGRES_HOST_PORT:-15432}/$${POSTGRES_DB:-thesisguard} alembic -c migrations/alembic.ini downgrade -1

db-reset: ## Reset database (drop all tables and re-migrate)
	DATABASE_URL=postgresql+asyncpg://$${POSTGRES_USER:-thesisguard}:$${POSTGRES_PASSWORD:-thesisguard_dev_password}@127.0.0.1:$${POSTGRES_HOST_PORT:-15432}/$${POSTGRES_DB:-thesisguard} alembic -c migrations/alembic.ini downgrade base
	DATABASE_URL=postgresql+asyncpg://$${POSTGRES_USER:-thesisguard}:$${POSTGRES_PASSWORD:-thesisguard_dev_password}@127.0.0.1:$${POSTGRES_HOST_PORT:-15432}/$${POSTGRES_DB:-thesisguard} alembic -c migrations/alembic.ini upgrade head

# ===========================================
# Testing
# ===========================================
test: ## Run all backend tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage
	pytest tests/ -v --cov=backend --cov=apps --cov-report=html

# ===========================================
# Linting & Type Checking
# ===========================================
lint: ## Run ruff linter
	ruff check backend/ apps/

lint-fix: ## Run ruff linter with auto-fix
	ruff check --fix backend/ apps/

format: ## Format code with ruff
	ruff format backend/ apps/

typecheck: ## Run mypy type checking
	MYPYPATH=. mypy --explicit-package-bases backend apps --ignore-missing-imports

# ===========================================
# Frontend
# ===========================================
frontend-install: ## Install frontend dependencies
	cd apps/web && npm install

frontend-check: ## Type check and lint frontend
	cd apps/web && npm run typecheck
	cd apps/web && npm run lint

frontend-build: ## Build frontend for production
	cd apps/web && npm run build

# ===========================================
# Combined
# ===========================================
dev: up ## Alias for 'up'
	
check: lint typecheck test ## Run all checks (lint + typecheck + test)
