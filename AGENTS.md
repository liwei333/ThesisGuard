# AGENTS.md — ThesisGuard Engineering Guide

## Project Overview

ThesisGuard (论衡) is a personal trading research and decision support system.
It is NOT an auto-trading bot. Core philosophy:
- **Thesis First** — Every position must have a verifiable investment thesis
- **Fact > Narrative** — Structured facts over LLM storytelling
- **Risk Before Opportunity** — Market regime gates individual stock decisions
- **Immutable History** — Thesis versions, trade plans, and discipline records are never overwritten

## Technical Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + TypeScript + Vite + Pinia + Vue Router |
| API | Python 3.12+ + FastAPI + Pydantic v2 |
| Database | PostgreSQL 17 + pgvector |
| Migration | Alembic |
| Cache/Queue | Redis |
| Object Storage | MinIO (S3-compatible) |
| Worker | Dramatiq + Redis |
| Infrastructure | Docker Compose |

## Module Architecture (Modular Monolith)

```
backend/
├── common/         # Shared infrastructure (db, config, events, security, storage)
├── instrument/     # Stock/ETF/index master data
├── watchlist/      # Watchlist management, classification
├── research/       # Research packages, modules, freshness
├── evidence/       # Evidence ingestion, source grading
├── thesis/         # Thesis engine, versions, validation, score ledger
├── expectation/    # Broker estimates, consensus, expectation snapshots
├── valuation/      # Bull/Base/Bear scenarios
├── price_in/       # Price-in analysis
├── market/         # Market regime engine
├── portfolio/      # Positions, capacity, correlation
├── trade_plan/     # Trade plan lifecycle, freeze/revise
├── catalyst/       # Catalyst tracking and validation
├── discipline/     # Trading discipline, violations
├── intelligence/   # News/policy intelligence
├── notification/   # Notification system
└── agent/          # Agent runtime (read-only in V1)
```

## Coding Conventions

### Python
- Use `async`/`await` for all I/O operations
- Pydantic v2 models for all API schemas
- SQLAlchemy 2.x with async sessions
- Type hints required on all public functions
- Ruff for formatting and linting
- All modules follow the pattern: `models.py`, `schemas.py`, `services.py`, `api.py`

### TypeScript
- Composition API (`<script setup>`)
- Strict TypeScript
- Auto-generated API client from OpenAPI spec (no hand-written URLs)
- Pinia stores for state management

## Key Design Rules

1. **LLM is NOT the system of record** — LLM outputs are proposals; domain services commit final state
2. **No overwriting history** — Thesis versions, trade plans use append-only versioning
3. **Structured facts in DB, evidence in RAG, raw files in MinIO**
4. **Market regime gates all trading decisions**
5. **Single position max 4 stocks; 5th triggers replacement PK**

## Work Packages

- WP-01: Engineering skeleton (current)
- WP-02: Instrument + Watchlist
- WP-03: Research Package
- WP-04: Evidence
- WP-05: Thesis Engine (most critical)
- WP-06: Research UI
- WP-07: Read-only Agent
- WP-08: Incremental Update

## Commands

```bash
# Development
make dev          # Start all services
make dev-api      # Start API only
make dev-web      # Start web only
make worker       # Start worker

# Database
make migrate      # Run migrations
make migrate-gen  # Generate new migration
make db-reset     # Reset database

# Quality
make test         # Run all tests
make lint         # Run linters
make typecheck    # Type checking (Python)
make frontend-check  # Type checking + lint (Frontend)

# Docker
make up           # docker compose up -d
make down         # docker compose down
make logs         # docker compose logs -f
make rebuild      # Rebuild and restart
```

## Testing Strategy

- Unit tests for domain services
- Integration tests for API endpoints
- Worker task tests with mocked broker
- Frontend component tests with Vitest

## Documentation

All significant design decisions should be documented in `docs/`.
Refer to `ThesisGuard_V1_Technical_Architecture_Design.md` for the full architecture.
