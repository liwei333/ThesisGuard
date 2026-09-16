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
- Sector Crowding 已登记为后续需求 `BACKLOG-SECTOR-CROWDING-01`，`ADR-2026-09-15-SECTOR-01` 状态为 `APPROVED — DEFERRED`。先完成 WP-04/WP-05 核心和 WP-RISK-01 最小闭环的 Market 基础，再核验 Sector 时点成分/历史数据并重审影子 MVP；当前不得实现评分、预留空表/API 或打断 Evidence 修复。详见 `docs/SECTOR_CROWDING_DECISION_2026-09-15.md`。

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
- `docs/SECTOR_CROWDING_DECISION_2026-09-15.md`: approved Sector Crowding backlog/timing decision，`APPROVED — DEFERRED`；不授权现在实现或修改冻结交易规则。
- `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`: frozen WP-04 implementation contract; not implementation evidence.
- `docs/PROJECT_STATUS_AUDIT_2026-09-12.md`: historical snapshot with 2026-09-12 cutoff; not live status.
- `docs/acceptance/`: historical acceptance and repair records; preserve them and qualify branch/time/scope.
- `docs/AGENT_RUNTIME_ARCHITECTURE.md`, `docs/MEMORY_ARCHITECTURE.md`, `docs/STRUCTURED_OUTPUT_CONTRACTS.md`: proposals unless promoted by a later canonical decision; their internal WP numbering is not canonical.
- `docs/ThesisGuard_V1_Technical_Architecture_Design (1).md`: non-canonical historical duplicate; do not delete or edit without separate approval.

Refer to `docs/ARCHITECTURE_REFERENCES.md` for the complete authority map. Document all significant approved decisions under `docs/`, but never turn a proposal or historical report into implementation evidence.

## Coding Agent Routing and Evaluation

用户目标：让 zcode 承担大部分已明确合同的常规代码开发，以减少 Codex 用量；Codex 负责必要的任务定义、独立验收、复杂问题和失败接管。节省效果以实际执行与返修成本判断，不承诺固定 token 节省比例。

此处 `zcode` 指用户转发任务的 zcode agent 应用；用户写的 `zcodex / zodex / zcode` 暂按同一候选工具称呼处理，实际工具或模型变化必须重新记录组合身份。项目产品内的 read-only Agent 规则不禁止受授权的工程 coding agent 编辑代码；工程权限仍由具体任务范围决定。

### Current Evaluation Record

- 评估日期：2026-09-16；组合：`zcode-agent-thesisguard-d3acc1c-20260916`；模型/工具版本 `UNKNOWN`。
- Stage 2 首验整体 FAIL 的历史保留；R1 目录 `thesisguard-zcode-eval-r1-202609161835-36243` 已独立复验。R1 整份交付仍 FAIL（API 新复现的错误路径及未完整修复的交付要求），不判 FAIL_SAFETY；原 21 独立断言全部通过。B1/B3 功能通过、交付 `PASS_WITH_REQUIRED_FIXES`；允许对应领域 `L2_RESTRICTED` 指定 S 任务试用，禁止自动集成。API 维持 L1，真实 DB/迁移/worker 等 UNPROVEN。
- 已确认基础文件定位、主分支 SHA 和主分支 Evidence 文件结构；未取得完整执行日志及探针前后快照，不能证明全部历史操作只读。
- 前轮分支/WP边界/权限表述已有补正。现已独立复跑自测 `48 passed`，补充检查 `12 failed, 9 passed`；13 个源码/契约哈希吻合。基础 Python/API 编码及隔离测试执行已观察，不代表事务/幂等/真实 DB 能力通过。
- R1 独立结果：自测 68 通过；原独立断言 21 通过；另加 5 检查后 `24 passed, 2 failed`（含原 21）。核心源码 Ruff/mypy 通过；全 b1/b2（含测试）Ruff 仍 6 错误。前端类型/build、方向键焦点/Tab、双实体状态、320/1440 检查通过，截图已由 Codex 补足。13 个新文件及 13 个原文件哈希吻合；原独立脚本未改，新目录副本仅替换 ROOT。
- 剩余限制：API value=1e309/NaN 经 B1 验证在路由内抛异常，返回 500 而非 422；B3 仍 8 个源/配置文件，不能把总数 13 当作符合单任务六文件；原始命令/运行时间证据不足，报告的 Ruff 清洁只覆盖源码。下一真实任务必须明确文件范围、全改动质量检查和证据，不复用未验收基准作生产实现。
- 2026-09-16 复核时 main HEAD 为 `d3acc1c6f4a2e5ce1fe4b973d7855409c0db1da5`，存在未跟踪验收材料；候选 `codex/wp04-02-evidence-domain-service@af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8` 已有服务/测试，且有 fixture 相关未提交修改。以上为时点快照；每次任务重新检查，不得覆盖在途修改或重新从零实现服务。
- 本轮独立复核时 main 为 `0dc2c5fd016af63f4836debf6ffa9d36b41a7703` 且 clean；前条 d3acc1c/af4f2cbb 是历史评估快照，不是下一任务固定基线。
- 完整记录：`docs/ZCODE_CAPABILITY_EVALUATION_2026-09-16.md`（最新 R1 Review and Routing）；本轮派工评估已形成可用结论，后续在真实指定 S 任务中验证稳定性，不再自动派整轮 R2。候选已存在 `_ensure_source_grade_allowed`，不能重复实现。费用/token/完整耗时 UNKNOWN，实际节省尚未测得。

### Current Routing

| Task | Current executor | zcode evidence / condition |
|---|---|---|
| 文件定位、单模块结构梳理、文档/测试场景草稿 | zcode；Codex 核验关键事实 | L1，只读 XS/S，注意基线及证据一致性 |
| 合同与代码对应检查、任务拆分初稿 | zcode；Codex 复核 | L1，每次一个明确约束，不独立宣布业务 PASS |
| Python 纯函数和对应单元测试 | 优先 zcode；Codex 独立验收 | L2 指定 S，已冻结输入/输出，不涉及 DB/事务/真实风险规则决策；源码及测试全量质量检查 |
| FastAPI/Pydantic/OpenAPI | 当前 Codex；zcode 可给草稿 | L1；ASGI 常规测试已过，非法 JSON 数值仍 500，不授予完整 API L2 |
| Vue/TypeScript 组件和双实体状态 | 优先 zcode；Codex 独立验收 | L2 指定 S，先限独立组件/局部状态；不据此推导跨页面/client/auth 集成已验证，桌面/移动及键盘检查必需 |
| 对已授权纯函数/组件的测试编写和隔离执行 | zcode；Codex 独立验收 | L2 随该任务范围；未知领域测试只给草稿，不能独立宣布合同 PASS |
| ORM/repository、迁移、真实 PostgreSQL/worker/MinIO 集成 | 当前 Codex | 需单独真实环境测试；模拟/内存验证不算通过 |
| 单函数/组件内明确反馈修复 | zcode 在对应 L2 任务内；Codex 复验 | 已观察受控返修；跨模块调试、事务恢复、行为保留重构仍 Codex/UNPROVEN |
| 产品/架构决策、冻结风险规则解释与修改决策、最终独立验收、Git 集成 | Codex；产品规则仍按用户批准流程 | zcode 可提供候选材料，不能自批授权或验收自己 |

### Dispatch Protocol

每次提出或派发工程任务，明确向用户给出以下字段（可用短段落，不必另建合同文件）：

```text
执行者：zcode / Codex
任务：单一可验收目标
依据：当前该能力域的验证记录、任务规模和风险
范围：允许修改文件、必要禁止范围、明确验收标准
验收者：Codex；列出必要独立检查
失败接管：zcode 一次受控返修，仍失败由 Codex 接管
```

- 尚未验证的常规开发能力优先进入隔离 XS/S 基准，不直接派主线完整 WP。用户已授权准备评估；本次基准提示词仅授权其指定临时目录中的开发测试，不扩展到候选 worktree、项目文件或数据库操作。
- 同能力域隔离 S 功能基准独立通过，可试用 `L2_RESTRICTED` 的明确 S 任务；非业务阻断的 lint/文件数/报告遗留须披露并列入新任务交付门槛，原基准不能作为整份已验收交付。首次必须隔离且指定最多 2-6 文件；完整 source/test/配置检查不过不得集成。一次成功不足以授予 L3。
- 当前下一步可派 zcode 做上述已验证域的一个真实指定 S 任务；API 和其他未过域由 Codex 主责。一次受控返修已用，不自动追加整轮 R2；根据必要真实任务接管或收窄范围。通过哪个能力域就试用哪个域，不重做无关全项目评估。
- 同类至少三个明确任务独立验收通过，或一个基准重复两次并完成一次受监督真实任务；无越界/虚报，返修成本可接受，才考虑该域 `L3_SINGLE_TASK` 和 M 规模。不默认授予 L4。
- 达到 L2/L3 的能力域，常规已冻结合同的任务优先派 zcode；Codex 只读必要事实源、完整相关 diff 和独立验证结果，按风险检查，不重复整套开发。
- 无法运行必要验证时标记 `BLOCKED_VALIDATION / UNPROVEN`；可交付草稿，但不能作为已验收实现集成。独立验收方可执行缺失验证并单独记录。
- 不委托候选 zcode 更新自身评级、`AGENTS.md` 或历史验收材料。Codex 根据用户转发的源码/diff/执行证据更新能力表；自评分不作为授权依据。
- 虚报测试或只读越界：暂停项目写入；模型/工具/权限/上下文发生实质变化：保留旧记录并重测相关能力。评估结论不授权 Capability Runtime、Sector Crowding 或其他延后需求。
- 每个试用任务尽量记录执行时间、首验结论、返修次数、Codex 修复量及双方可见 token/费用；不可见写 `UNKNOWN`。若 Codex 返修量超过候选改动量的 50%，暂停该域主开发路由并复评。
