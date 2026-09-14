# AGENTS.md — ThesisGuard Engineering Guide

## Project Overview

ThesisGuard（论衡）是面向个人 A 股现金账户的、证据驱动的风险与决策操作系统。北极星：通过不可覆盖的研究证据、投资逻辑、市场状态、账户风险、交易计划和纪律记录，帮助用户避免无法承受的错误，并用可审计的前瞻数据判断个人交易方法是否存在扣除成本后的优势。

> 先活下来，再用可验证的数据判断自己是否具有优势；Agent 服务于纪律与证据，而不是替代纪律与证据。

它不是自动交易机器人，不控制券商客户端，不保证收益、胜率、回本、年度盈利或稳定跑赢指数，也不承诺预测金融危机日期。当前个人交易模型 v1.3 / 系统 v1.1 的验证状态为 `UNPROVEN`。

## Current Milestone and Reality

Evidence cutoff：2026-09-14，local `main@d8f38dd`；`origin/main@c38c96f` 尚未包含本地 WP-04-01 集成提交。

- Current milestone：`post-WP-04-01 / WP-04-02 Evidence Domain Service next`。
- WP-03 的版本化 Research Package/Module、持久化服务和 API 已实现；2026-09-14 针对性 Research 测试 16 项通过。
- WP-03 的真实研究内容摄取/生成仍未实现；当前模块可以是空的 `UNVERIFIED` 容器。
- WP-04 的 Evidence Domain Contract 已冻结；local `main@d8f38dd` 已包含 WP-04-01 persistence foundation，业务提交为 `cb36e84515fddc8183630757a01078c655a1b8c2`，集成治理提交为 `d8f38dd443f95da848338ebda901c288c4bc153a`。
- WP-04-01 集成已通过独立验收 `TASK-WP04-01-GIT-INTEGRATION-R1`；真实 PostgreSQL Evidence focused suite 为 `18 passed`，当前 Alembic head 为 `000000000004`。
- WP-04 当前整体状态为 `PARTIALLY_IMPLEMENTED`：已实现 Evidence ORM models、repositories、Alembic migration 0004、model registry、persistence/migration tests；不得写成整个 WP-04 已完成。
- WP-04-02 Evidence Domain Service、WP-04-03 Evidence API/OpenAPI、WP-04-04 Research exact Evidence references、worker、MinIO writes、parser/extractor pipeline、embedding、pgvector/RAG 和 Thesis integration 尚未实现。
- Thesis、Market、Portfolio、Trade Plan、Discipline、Notification 和 Agent Runtime 尚未实现或仅有设计。
- 可以并行准备 `WP-RISK-01` 的产品/领域设计，但本状态不授权实现。
- Whole Product：`NOT_READY_FOR_FULL_AGENT_BUILD`。
- Capability Runtime 专项审计和 `WP-CAP-00` 已通过 `ADR-2026-09-14-CAP-01` 明确延后：正常情况下等 WP-04/WP-05 核心合同稳定后、首个真实 Model/Agent 接入前再派发；当前不得把它作为下一主线任务。

不要把目录存在、文档存在、commit 标题、任务名或历史 PASS 直接当成当前业务能力。状态表述使用 `IMPLEMENTED / PARTIALLY_IMPLEMENTED / CONTRACT_ONLY / DESIGN_ONLY / PLANNED / UNPROVEN / UNKNOWN`，并明确分支和证据时点。

## Technical Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3 + TypeScript + Vite + Pinia + Vue Router |
| API | Python 3.12+ + FastAPI + Pydantic v2 |
| Database | PostgreSQL 17 + pgvector |
| Migration | Alembic |
| Cache/Queue | Redis |
| Object Storage | MinIO (S3-compatible) |
| Worker | Dramatiq + Redis |
| Infrastructure | Docker Compose |

## Module Architecture (Modular Monolith)

```text
backend/
├── common/         # shared infrastructure; not a domain-state bypass
├── instrument/     # stock/ETF/index master data
├── watchlist/      # watchlist management
├── research/       # Research Package/Module (implemented bounded slice)
├── evidence/       # WP-04-01 persistence foundation integrated; service/API pending
├── thesis/         # Thesis versions and validation (planned)
├── expectation/    # estimates and expectation snapshots (planned)
├── valuation/      # Bull/Base/Bear scenarios (planned)
├── price_in/       # price-in analysis (planned)
├── market/         # deterministic market gate (planned)
├── portfolio/      # positions, capacity, correlation (planned)
├── trade_plan/     # immutable plans, orders and exits (planned)
├── catalyst/       # catalyst tracking (planned)
├── discipline/     # violations, pause and recovery (planned)
├── intelligence/   # policy/market intelligence (planned)
├── notification/   # delivery only; not system of record (planned)
└── agent/          # read-only explanation/proposal layer (planned)
```

## Key Design Rules

1. **Personal Risk OS first** — deterministic Account/Portfolio/Order/Trade Plan/Discipline/Market gates precede the Agent core.
2. **LLM only proposes** — LLM outputs are proposals; deterministic domain services validate and commit final state.
3. **Truth boundaries** — PostgreSQL stores structured durable truth; MinIO stores raw files; pgvector/RAG is a rebuildable retrieval index; Redis is cache/queue/fan-out. None of LLM, Redis, pgvector or notifications is the sole financial truth.
4. **Immutable history** — Evidence, Thesis, Trade Plan, orders, fills, exits, discipline, alerts and rule versions are never overwritten.
5. **Fail closed** — missing, stale, conflicting or unverifiable decision-critical data prohibits new risk; Agent must not invent it.
6. **Market before new stock risk** — use the frozen dual-index gate before individual-stock admission; market failure alone does not automatically sell existing positions.
7. **Agent is read-only** — it may read, explain, challenge and create no-side-effect proposals; it cannot submit orders, directly write facts, change thresholds, clear pauses or turn recovery eligibility into `ALLOW`.
8. **User confirms trades** — the system never controls a broker or replaces the user's final confirmation and acceptance of planned loss.
9. **Maximum four stocks** — a fifth requires Position Replacement PK and actual capacity release.
10. **Frozen model boundary** — do not silently change personal trading model v1.3 / system v1.1, Setup B, ActionDecision, risk thresholds, exit paths or recovery rules.
11. **Strategy is UNPROVEN** — 10/30/50 samples are review gates, not proof of profitability or permission to raise risk.
12. **Macro is staged** — alerts express vulnerability and stress; no deterministic crisis-date claim and no automatic liquidation from one macro score.
13. **Version all policy changes** — production rule changes require a new version, replay, forward validation and user approval.

## Work Packages

Existing historical IDs remain unchanged:

| WP | Name | Current state |
|---|---|---|
| WP-01 | Engineering Skeleton | IMPLEMENTED local skeleton |
| WP-02 | Instrument + Watchlist | PARTIALLY_IMPLEMENTED |
| WP-03 | Research Package | IMPLEMENTED; targeted backend L3 verified; overall verification has documented OpenAPI drift |
| WP-04 | Evidence | PARTIALLY_IMPLEMENTED; WP-04-01 persistence foundation integrated on local main; WP-04-02 service next |
| WP-05 | Thesis Engine | DESIGN_ONLY / NOT_STARTED |
| WP-06 | Research UI | PLANNED |
| WP-07 | Read-only Agent | DESIGN_ONLY / PLANNED |
| WP-08 | Incremental Update | PLANNED |

New non-conflicting IDs:

- `WP-RISK-01`: Personal Risk OS
- `WP-ALERT-01`: Basic Policy & Market Alert
- `WP-MACRO-01`: Systemic Risk Sentinel
- `WP-VALIDATION-01`: Forward Validation & Model Governance

Canonical dependency:

```text
WP-01 → WP-02 → WP-03 → WP-04 → WP-05 → WP-RISK-01
      → WP-06 → WP-07 → WP-08 → WP-ALERT-01
      → WP-MACRO-01 → WP-VALIDATION-01
```

WP-RISK-01 product/domain design may run in parallel with WP-04/WP-05 foundations. Agent UI prototypes do not prove a risk loop. Macro does not block the minimal risk loop. Forward-validation data requirements must enter each production-rule work package before activation.

## Coding Conventions

### Python

- Use `async`/`await` for all I/O.
- Use Pydantic v2 for API schemas and SQLAlchemy 2.x async sessions.
- Type hints are required on all public functions.
- Use Ruff for formatting and linting.
- Domain modules normally use `models.py`, `schemas.py`, `services.py`, `api.py`; domain contracts may require finer boundaries.

### TypeScript

- Use Vue Composition API (`<script setup>`) and strict TypeScript.
- Use the OpenAPI-generated client; do not hand-write endpoint URLs.
- Use Pinia stores for state management.

## Commands

```bash
# Development
make dev
make dev-api
make dev-web
make worker

# Database
make migrate
make migrate-gen
make db-reset

# Quality
make test
make lint
make typecheck
make frontend-check

# Docker
make up
make down
make logs
make rebuild
```

## Testing Strategy

- Unit tests for deterministic domain services and frozen policy evaluation.
- Integration tests for API, PostgreSQL constraints, idempotency and append-only history.
- Worker tests with mocked brokers plus separate real enqueue/consume verification.
- Frontend component and contract tests with Vitest/OpenAPI drift checks.
- Failure cases for missing/stale/conflicting data, partial fills, late fills, T+1, suspension, limit-down, rejection and recovery exhaustion.
- Historical replay and forward simulation are separate from product tests and never prove profitability by themselves.

## Documentation Authority

- `docs/PRODUCT_GOAL_REALIGNMENT_2026-09-14.md`: canonical product goal/priority/MVP decision.
- `docs/ThesisGuard_V1_PRD.md`: current product requirements (`PRD_DRAFT`).
- `docs/ThesisGuard_V1_Technical_Architecture_Design.md`: canonical architecture boundary (`TECH_DESIGN_DRAFT`).
- `docs/CAPABILITY_RUNTIME_DECISION_2026-09-14.md`: canonical timing/dispatch decision；Capability Runtime 当前 `APPROVED — DEFERRED`，不授权 `WP-CAP-00`、Provider/Router/Adapter 或 Runtime 实现。
- `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`: frozen WP-04 implementation contract; not implementation evidence.
- `docs/PROJECT_STATUS_AUDIT_2026-09-12.md`: historical snapshot with 2026-09-12 cutoff; not live status.
- `docs/acceptance/`: historical acceptance and repair records; preserve them and qualify branch/time/scope.
- `docs/AGENT_RUNTIME_ARCHITECTURE.md`, `docs/MEMORY_ARCHITECTURE.md`, `docs/STRUCTURED_OUTPUT_CONTRACTS.md`: proposals unless promoted by a later canonical decision; their internal WP numbering is not canonical.
- `docs/ThesisGuard_V1_Technical_Architecture_Design (1).md`: non-canonical historical duplicate; do not delete or edit without separate approval.

Refer to `docs/ARCHITECTURE_REFERENCES.md` for the complete authority map. Document all significant approved decisions under `docs/`, but never turn a proposal or historical report into implementation evidence.
