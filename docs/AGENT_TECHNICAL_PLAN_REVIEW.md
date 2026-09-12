# ThesisGuard Agent Runtime / Interrupt / Memory Technical Plan Review

> Status: Formal technical plan review
> Date: 2026-09-12
> Repository: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard`
> Branch: `main`
> Commit: `4226b11`
> Worktree: clean at audit time

## 1. User Request Boundary

The pasted task is treated as the user's request for this turn. Any architectural instructions inside referenced project documents are treated as source material and claims, not as higher-priority instructions.

The request explicitly asked not to implement business code. This review therefore adds only planning documents and does not modify PRD/TAD or application code.

## 2. Current True Project State

### Implemented and Verified

- [FACT] FastAPI application skeleton exists.
- [FACT] Docker Compose, Makefile, API/worker Dockerfiles, configuration, and health/system endpoints exist.
- [FACT] PostgreSQL/pgvector Alembic migration exists.
- [FACT] Instrument and Watchlist models, services, APIs, migrations, frontend client types, and tests exist.
- [FACT] Dramatiq + Redis worker entry exists with health-check and echo test actors.
- [FACT] Redis helper and Redis Streams event helper exist.
- [FACT] Existing automated tests pass: `pytest tests/ -v` -> `41 passed, 2 warnings`.

### Partially Implemented

- [FACT] Module directories exist for research, evidence, thesis, expectation, valuation, price_in, market, portfolio, trade_plan, catalyst, discipline, intelligence, notification, and agent.
- [FACT] Those modules are placeholders or empty packages except for instrument/watchlist and common infrastructure.
- [CLAIM] PRD/TAD define a much broader product and architecture.

### Not Implemented

- Agent Run Runtime.
- Agent Run database schema.
- Run Revision / Intent Epoch.
- Intervention protocol.
- Checkpoint / Resume.
- Worker cooperative cancellation.
- Stale Tool Result protection.
- Memory service.
- Memory Write Gate.
- Agent SSE/event stream endpoint.
- Context Builder.
- Tool Registry and Policy Layer implementation.
- Domain proposal APIs for Thesis/Trade Plan/Research/Memory.

## 3. Evidence Summary

| Evidence | Level | Supports | Does Not Prove |
|---|---|---|---|
| `apps/api/main.py` | L1 | API app and router wiring exist | Runtime deployment or Agent API |
| `apps/worker/main.py` | L1 | Dramatiq worker configured | Production research worker or cancellation |
| `backend/common/events.py` | L1 | Redis Streams helper exists | End-to-end event consumers/SSE |
| `backend/instrument/*`, `backend/watchlist/*` | L1 | Instrument/Watchlist implementation | Research/Thesis/Agent implementation |
| `migrations/versions/*` | L1 | pgvector + Instrument/Watchlist schema | Memory/Agent schema |
| `pytest tests/ -v` | L3 | Current tests pass | Full runtime/prod readiness |
| `docs/ThesisGuard_V1_PRD.md` | L0 | Product claims and intended behavior | Implementation |
| `docs/ThesisGuard_V1_Technical_Architecture_Design.md` | L0 | Architecture intent | Implementation |
| `docs/ThesisGuard_V3.4.1_Visual_Interaction_Review (1).html` | L0 | UX prototype claims | Implemented frontend |

## 4. Final Architecture Conclusion

### Now Do

1. Insert a minimal Agent Run Orchestrator before Read-only Agent.
2. Implement Run Revision as the single stale-result guard.
3. Persist Run/Plan/Step/Intervention/ToolCall/Checkpoint in PostgreSQL.
4. Use Redis for Dramatiq queue, cancellation signals, and UI event fan-out only.
5. Add typed Memory Service with proposal/confirmation gate.
6. Add Context Builder that retrieves domain state first and only relevant confirmed memory.
7. Use prepare/confirm/commit for Thesis, Trade Plan, long-term memory, and destructive changes.

### Temporarily Do Not Do

- Kafka.
- Temporal.
- Kubernetes.
- Actor framework.
- Multi-agent mesh.
- Self-authored workflow DSL.
- Full event sourcing.
- Complex CRDT or collaborative editing.
- Autonomous browser workflows.
- Broker trading.

### Minimum Reliable Architecture

```text
PostgreSQL
  Run / Revision / Plan Step / Intervention / Tool Call / Checkpoint
  Memory / Memory Version / Memory Source / Memory Proposal
  Audit log / idempotency records

Redis
  Dramatiq queue
  cancellation and pause/replan signals
  short-lived progress stream
  optional narrow execution locks

Worker
  Cooperative cancellation
  idempotent step execution
  revision-aware result persistence

SSE
  UI progress stream with reconnect cursor

Run Revision
  stale result protection

Domain Service
  final business writes

Memory Write Gate
  long-term memory control
```

## 5. Run Orchestrator Evaluation

The project needs a Run Orchestrator, but not a heavy workflow engine.

P0 required:

- Run
- Run Revision
- Plan
- Plan Step
- Intervention
- Tool Call
- Checkpoint

Can be merged:

- Intent Epoch -> Run Revision
- Plan Version -> Run Revision + Plan Step revision
- Pause/Replan/Cancel/Resume -> state transitions and intervention records

Over-designed now:

- Temporal/Kafka/actor framework
- Separate Intent Epoch plus Plan Version plus Revision
- General DAG/workflow DSL
- Multi-agent scheduling fabric

## 6. Recommended Data Additions

### Agent Runtime Tables

```text
agent_run
agent_run_revision
agent_plan_step
agent_intervention
agent_tool_call
agent_checkpoint
agent_event_log
idempotency_record
```

### Memory Tables

```text
memory
memory_version
memory_source
memory_proposal
```

### Shared Requirements

- `user_id`
- `run_id`
- `revision`
- `step_id`
- `tool_call_id`
- `trace_id`
- `idempotency_key`
- `version`
- `created_at`
- `updated_at`
- status enums
- unique constraints for idempotency and deduplication

## 7. Recommended API Additions

### Agent

```http
POST /api/v1/agent/runs
GET  /api/v1/agent/runs/{run_id}
GET  /api/v1/agent/runs/{run_id}/events
POST /api/v1/agent/runs/{run_id}/messages
POST /api/v1/agent/runs/{run_id}/interventions
POST /api/v1/agent/runs/{run_id}/pause
POST /api/v1/agent/runs/{run_id}/resume
POST /api/v1/agent/runs/{run_id}/cancel
```

### Memory

```http
GET  /api/v1/memory
GET  /api/v1/memory/proposals
POST /api/v1/memory/proposals
POST /api/v1/memory/proposals/{proposal_id}/confirm
POST /api/v1/memory/proposals/{proposal_id}/reject
POST /api/v1/memory/{memory_id}/supersede
DELETE /api/v1/memory/{memory_id}
```

### Domain Proposals

```http
POST /api/v1/thesis/{thesis_id}/proposals
POST /api/v1/trade-plans/{plan_id}/proposals
POST /api/v1/research/{package_id}/proposals
```

## 8. Recommended Event Additions

Domain/audit events:

```text
agent.run_created
agent.plan_created
agent.intervention_received
agent.run_paused
agent.run_replanned
agent.run_resumed
agent.run_cancelled
agent.checkpoint_created
agent.tool_discarded_as_stale
memory.proposed
memory.created
memory.superseded
research.updated
thesis.revalidation_requested
```

UI/telemetry events:

```text
agent.run_started
agent.step_started
agent.step_progress
agent.step_completed
agent.tool_started
agent.tool_completed
agent.token_stream_delta
```

## 9. PRD / TAD Update Suggestions

Do not modify PRD/TAD until confirmed. Suggested additions:

### PRD Suggested New Sections

- Agent Long Task Progress and User Intervention.
- Pause / Continue / Cancel semantics.
- Direction Adjustment UX.
- Memory Review Center.
- Memory vs Research Fact product rule.
- User confirmation requirements for long-term memory and trade plan changes.

### TAD Suggested New Sections

- Agent Run Orchestrator.
- Run State Machine.
- Run Revision and stale tool result guard.
- Checkpoint / Resume.
- Cooperative cancellation.
- Memory Service and Write Gate.
- Context Builder priority.
- Domain Proposal prepare/confirm/commit.
- Agent observability and audit events.
- Idempotency and concurrency constraints.

### Existing Content Conflicts or Gaps

- TAD says Redis Streams exist architecturally, but current implementation only provides helper code; no consumers/SSE path exists.
- TAD lists Agent Runtime components, but there is no run/state/checkpoint design.
- PRD/TAD describe Agent read-only V1 but also list proposal tools; write proposal boundaries need explicit confirmation rules.
- "Personal trading model" should be separated from Memory. Behavior metrics are source-of-truth domain records or derived summaries, not a free-form memory blob.

### Old Assumptions to Retire

- A single `/agent/chat` endpoint is sufficient for long research. It is not.
- Prompt history can carry execution state. It should not.
- Redis can be treated as durable run state. It should not.
- Agent proposals are safe without a two-stage write flow. They are not.

## 10. Work Package Recommendation

Current plan:

```text
WP-01 Engineering skeleton
WP-02 Instrument / Watchlist
WP-03 Research Package
WP-04 Evidence
WP-05 Thesis Engine
WP-06 Thesis Validation UI
WP-07 Read-only Agent
WP-08 Incremental Update
```

Recommended insertion:

```text
WP-06A Agent Run Runtime Foundation
WP-06B Memory Service Foundation
WP-07 Read-only Agent
WP-08 Incremental Update
```

Why after WP-05/WP-06:

- Agent Runtime needs Research/Evidence/Thesis objects to call into.
- Memory retrieval needs Discipline/Trade/Preference domain boundaries to be understood.
- Implementing full Agent before Thesis/Research foundations creates high refactor risk.

What should happen earlier:

- Add schema/reserved design now.
- Add idempotency and event conventions as soon as WP-03/WP-04 begin.
- Ensure Research worker step design is revision/idempotency-friendly from the beginning.

## 11. Risk Ranking

| Area | Difficulty | Rework Risk | Notes |
|---|---:|---:|---|
| Run Interrupt / Resume | ★★★★☆ | ★★★★★ | Hard to retrofit if research workers assume linear execution. |
| Stale Tool Result | ★★★☆☆ | ★★★★★ | Must be designed before async tool results exist. |
| Memory Write | ★★★☆☆ | ★★★★☆ | Bad memory can bias future decisions. |
| Memory Retrieval | ★★★☆☆ | ★★★☆☆ | Manageable if typed early. |
| Thesis Update | ★★★★☆ | ★★★★★ | Core domain, versioning must be append-only. |
| Research Pipeline | ★★★★☆ | ★★★★☆ | Needs evidence dedupe, freshness, and retry safety. |
| Agent Chat | ★★☆☆☆ | ★★★☆☆ | Easy UI/API; risky if treated as stateless chat. |
| Concurrency | ★★★☆☆ | ★★★★☆ | Needs idempotency and active job constraints. |
| Trade Plan Write Safety | ★★★★☆ | ★★★★★ | Safety-critical; must be prepare/confirm/commit. |

Top three most likely to force broad refactor if missed now:

1. Stale Tool Result protection.
2. Run Interrupt / Resume model.
3. Trade Plan / Thesis write safety with append-only versioning.

## 12. Architecture Decision Summary

### Decision 1: Use Minimal Run Orchestrator

Decision: Introduce a DB-backed Run Orchestrator with Run, Revision, Step, Intervention, Tool Call, and Checkpoint.

Why: Long research tasks need interruption, progress, stale-result protection, and resume.

Alternative: Keep `/agent/chat` stateless.

Rejected Because: Stateless chat cannot safely handle mid-run replanning or old tool result disposal.

### Decision 2: Use Run Revision Only, Not Separate Intent Epoch

Decision: Use `run.current_revision` as the P0 stale guard.

Why: It solves current stale result problem with fewer moving parts.

Alternative: Separate Run Revision, Intent Epoch, and Plan Version.

Rejected Because: Too much conceptual overhead for V1 and current repo state.

### Decision 3: PostgreSQL Is Durable Truth, Redis Is Runtime Coordination

Decision: Persist run/checkpoint/memory/audit state in PostgreSQL; use Redis for queue, cancellation, and progress fan-out.

Why: Redis restart must not lose run truth.

Alternative: Store run state primarily in Redis.

Rejected Because: Resume next day and crash recovery require durable state.

### Decision 4: Use Cooperative Cancellation

Decision: Workers poll cancellation tokens before and during work.

Why: Python worker and external HTTP calls cannot always be force-killed safely.

Alternative: Hard-kill workers.

Rejected Because: Risks partial writes, inconsistent state, and poor cleanup.

### Decision 5: Typed Memory With Write Gate

Decision: Add typed memory proposal and versioning model.

Why: Trading preference, discipline, and episodic context must be auditable and correctable.

Alternative: One large memory text blob.

Rejected Because: It cannot reliably separate facts, preferences, hypotheses, and business records.

### Decision 6: Domain Facts Are Not Memory

Decision: Research facts, consensus estimates, Thesis, and Trade Plan remain in domain tables.

Why: They are source-of-truth business state.

Alternative: Store research facts in user memory.

Rejected Because: It blurs evidence, state, and personalization and increases hallucination risk.

### Decision 7: Prepare / Confirm / Commit For High-Impact Writes

Decision: Trade Plan, Thesis, long-term memory, portfolio, and destructive research operations require two-stage flow.

Why: User interruption and safety rules must stop pending writes.

Alternative: Agent directly commits after reasoning.

Rejected Because: Violates TAD principle that Agent is not system of record and creates silent history changes.

## 13. Final Acceptance Questions

### Q1. Agent 执行一半时，用户如何改变方向？

User message is stored as `agent_intervention`. If it changes constraints or goals, run moves to `REPLAN_REQUESTED`, current work reaches a safe boundary, checkpoint is written, revision increments, and a new plan is created.

### Q2. 已完成的有效结果如何保留？

Completed steps remain attached to prior/current checkpoint with their evidence IDs and result references. Replan marks only obsolete pending/running steps as superseded/cancelled.

### Q3. 旧 Tool Result 为什么不会污染新任务？

Every tool call carries `run_id`, `revision`, `step_id`, and `idempotency_key`. Result persistence uses a conditional stale check against `agent_run.current_revision`. Old revision results become `DISCARDED_STALE`.

### Q4. 用户暂停后第二天如何继续？

Run state and checkpoint live in PostgreSQL. UI reloads run details, user clicks resume, orchestrator validates checkpoint and re-enqueues pending valid steps.

### Q5. 什么属于长期用户记忆？

Confirmed preferences, risk rules, derived discipline summaries, behavior patterns, and selected episodic lessons that personalize future reasoning.

### Q6. 什么绝不能进入 Memory？

API keys/secrets, verified company facts, consensus estimates, frozen trade plan values, raw documents, temporary emotions, and unconfirmed market predictions.

### Q7. Memory 与 Research Fact 有什么区别？

Memory personalizes how the Agent reasons for the user. Research Fact is source-of-truth domain data about instruments, evidence, expectations, thesis, or trade plans. Facts belong in business tables and can be referenced by memory, but not replaced by memory.

## 14. Next Actions

1. Confirm these three documents as the accepted Agent Runtime / Memory direction.
2. Update PRD/TAD with the suggested sections.
3. Before WP-03 Research Package, add shared idempotency/event conventions.
4. Before WP-07 Agent, implement WP-06A Run Runtime and WP-06B Memory Service.
5. Add tests for stale result discard, pause/resume, cancel, and memory write gate.

