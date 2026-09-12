# ThesisGuard Agent Runtime / Interrupt Design

> Status: Technical plan, not implemented
> Date: 2026-09-12
> Scope: Agent long-run orchestration, user intervention, stale result protection, checkpoint/resume, worker cancellation, API/events/UX

## 1. Current Problem

ThesisGuard V1 already defines Agent as a natural-language reasoning layer that must not directly write final business state. The missing P0 design is what happens during long-running research when the user changes direction mid-run.

Example:

```text
Run: research 强瑞技术
Completed: 公司业务, 行业
Running: 液冷订单
Pending: 半导体, 财务, 估值, 技术面

User intervention:
技术面先不要，重点深挖液冷订单、客户、利润率和订单持续性。
```

The system must preserve valid completed work, stop irrelevant future steps, prevent stale tool results from overwriting the current plan, and show the user how the plan changed.

## 2. Current Repository Reality

### Observed Implementation

- FastAPI application entry exists at `apps/api/main.py`.
- Registered API routers today are health, system, tasks, instrument, and watchlist.
- Dramatiq + Redis worker entry exists at `apps/worker/main.py`.
- Worker currently exposes test actors only: `system_health_task` and `echo_task`.
- Redis wrapper exists at `backend/common/redis_client.py`.
- Redis Stream event helper exists at `backend/common/events.py`.
- Instrument and Watchlist models/services/APIs exist.
- Migrations currently cover pgvector enablement plus instrument/watchlist tables.
- `backend/agent/` exists only as an empty package.
- Research, Evidence, Thesis, Trade Plan, Discipline, Portfolio, Market and other modules are mostly placeholder packages.
- Existing tests pass: `pytest tests/ -v` returned `41 passed, 2 warnings` on 2026-09-12.

### Documentation Claims

- PRD defines Agent as the natural-language operation and reasoning layer.
- TAD lists Agent Orchestrator, Context Builder, Policy Layer, Tool Registry, LLM, Structured Proposal, Domain Service.
- TAD states Agent must not directly update database, delete history, modify frozen plans, change market regime score, change portfolio limits, or execute trades.
- TAD lists Redis Streams and SSE as architectural directions.

### Gap

There is no implemented Agent Run model, Run Revision, intervention protocol, checkpoint/resume model, cancellation token, stale result guard, Agent SSE endpoint, or memory-aware context builder.

## 3. Design Goals

1. Preserve completed valid work when a user changes direction.
2. Prevent old tool calls from polluting a newer run revision.
3. Allow pause, resume, cancel, and replan with clear user-visible state.
4. Keep V1 small enough for a modular monolith.
5. Use PostgreSQL as durable truth for run state and audit history.
6. Use Redis for queueing, short-lived cancellation signals, event streaming, and ephemeral runtime coordination.
7. Keep final domain writes behind Policy + Domain Service.
8. Make every long-running step idempotent and retry-safe enough for worker failure.
9. Avoid Kafka, Temporal, Kubernetes, actor frameworks, CRDTs, or a custom workflow DSL in V1.

## 4. Non-Goals

- No auto-trading.
- No broker order execution.
- No complex multi-agent mesh.
- No fully distributed workflow platform.
- No global event sourcing architecture.
- No autonomous browser/runtime platform.
- No hidden background rewrite of Thesis/Trade Plan/Memory without policy gates.

## 5. Do We Need a Run Orchestrator?

Yes, but only a minimal Run Orchestrator.

The current product direction needs long-running research and thesis validation. A simple chat endpoint is not enough because research runs involve multi-step plans, worker tasks, tool calls, checkpoints, and user interventions.

V1 should introduce these objects:

| Object | P0? | Decision |
|---|---:|---|
| Run | Yes | Durable user-request execution container. |
| Run Revision | Yes | Minimal stale-result protection and intervention history. |
| Intent Epoch | Merge into Run Revision | Separate epoch is over-designed for V1. Use `revision`. |
| Plan | Yes | Current plan attached to a revision. |
| Plan Step | Yes | User-visible progress and worker scheduling unit. |
| Intervention | Yes | Records user mid-run intent, pause, cancel, or replan request. |
| Tool Call | Yes | Needed for idempotency, stale check, audit, retries. |
| Checkpoint | Yes | Needed for browser close, pause, restart, resume. |
| Pause | State + intervention | No separate top-level object required. |
| Cancel | State + intervention + cancellation token | No separate top-level object required. |
| Replan | New revision + plan | No separate top-level object required. |
| Resume | Transition + checkpoint | No separate top-level object required. |

Minimum reliable V1:

```text
agent_run
agent_run_revision
agent_plan_step
agent_intervention
agent_tool_call
agent_checkpoint
agent_event_log
```

## 6. Storage Responsibilities

### PostgreSQL

Durable truth:

- Run identity, owner, conversation/instrument binding.
- Run status and current revision.
- Plans and plan steps.
- Interventions.
- Tool call records and final disposition.
- Checkpoints.
- Audit/event log needed for later explanation.
- Idempotency records for user actions and domain proposals.

### Redis

Short-lived runtime coordination:

- Dramatiq queue/broker.
- Cancellation signal keys.
- Pause/replan request signal keys.
- SSE fan-out buffer or Redis Stream for UI progress.
- Short-lived locks where needed.
- Short-lived worker heartbeat.

Redis must not be the only store for run status, plan, checkpoint, or committed results.

### Worker

- Consumes runnable plan steps.
- Checks cancellation and revision before starting.
- Polls cancellation during long work.
- Emits progress events.
- Persists tool call results only after stale check.
- Writes checkpoints after step completion or interruption boundary.

## 7. Redis Streams, Locks, Optimistic Locking, Idempotency

### Redis Streams

Use Redis Streams in V1 for UI/event fan-out if the existing `backend/common/events.py` helper is kept. Do not make Redis Streams the durable system of record.

Recommended split:

- Domain/audit events: append to `agent_event_log` in PostgreSQL, optionally mirror to Redis Stream.
- UI progress events: Redis Stream with TTL/trimming and SSE replay cursor.
- Worker queue: Dramatiq Redis broker.

### Distributed Locks

Avoid broad distributed locking in V1. Use:

- PostgreSQL row-level updates / optimistic version checks for run transitions.
- A narrow Redis lock only to prevent duplicate worker execution of the same `plan_step_id` when necessary.

### Optimistic Locking

Required. Add `version` integer fields to:

- `agent_run`
- `agent_plan_step`
- domain proposals that may be confirmed later

All state transitions should include `WHERE id = ? AND version = ?`.

### Idempotency Keys

Required for:

- `POST /agent/runs`
- intervention submission
- pause/resume/cancel
- worker step enqueue
- tool call execution
- domain proposals
- memory write proposals
- SSE/event deduplication

## 8. Run State Machine

```text
CREATED
  -> PLANNING
  -> RUNNING
  -> PAUSE_REQUESTED -> PAUSED -> RUNNING
  -> REPLAN_REQUESTED -> PLANNING -> RUNNING
  -> CANCEL_REQUESTED -> CANCELLED
  -> COMPLETED
  -> FAILED
```

### State Semantics

| State | Meaning | User Can Intervene? | Resume? |
|---|---|---:|---:|
| CREATED | Run persisted, no plan yet | Yes | Not needed |
| PLANNING | Building initial or revised plan | Yes | No |
| RUNNING | Executing plan steps | Yes | No |
| PAUSE_REQUESTED | Pause requested, waiting for boundary | Yes | Not yet |
| PAUSED | No new work may start | Yes | Yes |
| REPLAN_REQUESTED | Direction changed, revision pending | Yes | No |
| CANCEL_REQUESTED | Cancellation requested, workers draining | Yes, only status/cancel clarification | No |
| CANCELLED | Terminal user cancel | No | No |
| COMPLETED | Terminal success | No, create follow-up run | No |
| FAILED | Terminal or resumable depending error class | Yes, if marked resumable | Conditional |

### Terminal States

`COMPLETED`, `CANCELLED`, and non-resumable `FAILED` cannot be resumed. A new request should create a new Run or a follow-up Run linked to the original.

## 9. Intervention Protocol

Recommended V1 intervention types:

| Type | Meaning | Revision Change? |
|---|---|---:|
| ADD_CONTEXT | Adds information without changing objective or constraints | Usually no |
| MODIFY_CONSTRAINT | Changes constraints such as exclude technical analysis | Yes |
| REPLAN | Changes objective or remaining work | Yes |
| PAUSE | Stop after current interruption boundary | No |
| CANCEL | Stop as soon as safely possible | No, terminal path |
| NEW_TASK | User asks unrelated task | New Run |

### Classification Rules

- If user adds evidence or preference for the same goal: `ADD_CONTEXT`.
- If user changes scope, priority, exclusions, output format, or risk constraints: `MODIFY_CONSTRAINT`.
- If user changes the goal or the remaining plan materially: `REPLAN`.
- If user says wait, pause, hold, stop after this: `PAUSE`.
- If user says stop/cancel/do not continue: `CANCEL`.
- If user asks an unrelated question: create a separate Run by default and leave current Run running unless the user explicitly asks to interrupt it.

### Three Consecutive User Updates

When multiple interventions arrive while the run is in `RUNNING`, `PAUSE_REQUESTED`, `REPLAN_REQUESTED`, or `PLANNING`:

1. Append every message as an `agent_intervention`.
2. Debounce replanning for a short server-side window, e.g. 1-3 seconds.
3. Combine all still-pending interventions into one revision.
4. Preserve each raw intervention for audit.
5. Show the user one consolidated plan change.

## 10. Soft Interrupt

Soft interrupt is the default for direction changes.

Process:

1. Persist intervention.
2. Move run to `REPLAN_REQUESTED` or `PAUSE_REQUESTED`.
3. Set Redis signal: `agent:run:{run_id}:interrupt = revision_target`.
4. Current tool/step continues until its minimum safe boundary.
5. Worker creates checkpoint.
6. Orchestrator increments `agent_run.current_revision`.
7. New plan is generated from checkpoint + interventions.
8. Remaining old pending steps are marked `SUPERSEDED`.
9. New steps are enqueued.

Use this for downloading/parsing a financial report, summarizing a document, or finishing a single API response where forced termination would cause more inconsistency than value.

## 11. Hard Cancel

Hard cancel is for explicit stop requests or expensive runaway work.

Process:

1. Persist `CANCEL` intervention.
2. Transition run to `CANCEL_REQUESTED`.
3. Set Redis cancellation token: `agent:run:{run_id}:cancelled = true`.
4. Mark pending steps `CANCELLED`.
5. Workers poll token before and during long operations.
6. Tool calls that support `cancel()` receive cancellation.
7. Tool calls that do not support cancellation are allowed to finish, but their results are discarded unless they belong to a still-valid revision and non-cancelled step.
8. Transition to `CANCELLED` after active workers acknowledge or after timeout with best-effort draining.

## 12. Cancellation Token

Redis key:

```text
agent:run:{run_id}:cancelled = {
  "requested_at": "...",
  "reason": "...",
  "requested_by": "user_id",
  "revision": 2
}
TTL: 24h after terminal state
```

Worker checks:

- Before starting a step.
- Before each tool call.
- Between pagination/batch chunks.
- After external HTTP response returns and before persisting result.

For batch jobs such as 5000 news items, chunk work into small pages, e.g. 50-100 items, and check token between chunks.

## 13. Run Revision and Stale Result Protection

V1 should use **Run Revision** as the single stale-protection primitive. Do not add separate Intent Epoch and Plan Version until a real need appears.

### Required Fields

`agent_run`

```text
id
user_id
conversation_id
instrument_id nullable
status
current_revision
version
created_at
updated_at
completed_at nullable
```

`agent_run_revision`

```text
id
run_id
revision_number
base_checkpoint_id nullable
reason
user_intent_summary
plan_summary
created_at
created_by
```

`agent_plan_step`

```text
id
run_id
revision
step_key
title
status
input
output_ref nullable
depends_on_step_ids
idempotency_key
version
started_at nullable
completed_at nullable
```

`agent_tool_call`

```text
id
run_id
revision
step_id
tool_name
tool_input
status
idempotency_key
result_ref nullable
error nullable
started_at
completed_at nullable
```

### Stale Check

Tool result persistence must be conditional:

```sql
UPDATE agent_tool_call
SET status = 'COMPLETED', result_ref = :result_ref, completed_at = now()
WHERE id = :tool_call_id
  AND run_id = :run_id
  AND revision = (
    SELECT current_revision FROM agent_run WHERE id = :run_id
  )
  AND status IN ('RUNNING', 'STARTED');
```

If zero rows are updated:

- Mark tool call `DISCARDED_STALE` in a separate best-effort update.
- Emit `agent.tool_discarded_as_stale`.
- Do not attach output to current plan, current summary, current research package, Thesis, or memory.

## 14. Checkpoint

Checkpoint is durable, compact, and resumable.

Recommended fields:

```text
id
run_id
revision
checkpoint_type
current_goal
current_plan_snapshot
completed_step_ids
pending_step_ids
cancelled_step_ids
superseded_step_ids
collected_evidence_ids
tool_result_refs
current_context_summary
run_state_snapshot
created_at
```

### PostgreSQL

Persist:

- `current_goal`
- `current_plan_snapshot`
- step statuses
- evidence IDs
- result references
- context summary
- revision
- timestamps

### Redis

Keep only:

- currently active worker heartbeat
- in-flight progress counters
- transient cancellation/pause/replan signals
- recent event fan-out buffer

### Tool Results

Permanent if they created durable Evidence, Research, Thesis proposal, Trade Plan proposal, or audit-relevant artifact.

Temporary if they are only intermediate prompts, ranking scratchpads, or LLM chain-of-thought-like scratch content. Store summaries, not hidden reasoning.

## 15. Resume

Resume uses PostgreSQL checkpoint, not frontend local state.

Flow:

1. User opens run page or clicks continue.
2. API loads latest non-stale checkpoint for `run_id`.
3. Orchestrator verifies run is `PAUSED` or resumable `FAILED`.
4. Orchestrator increments revision only if user adds new intent; otherwise keeps current revision.
5. Pending valid steps are re-enqueued using idempotency keys.
6. UI subscribes to `/events?cursor=...`.

Browser local state may cache UI selection only. It must not be source of truth for run status.

## 16. Worker Cancel and External Tools

Tool contract should include:

```text
supports_cancel: bool
idempotency_required: bool
side_effect_level: NONE | READ_ONLY | PROPOSAL | WRITE
timeout_seconds
```

If a tool cannot cancel an external HTTP call:

1. Set local cancellation token.
2. Let call return or timeout.
3. Run stale/cancel check before persistence.
4. If stale/cancelled, discard result and log.

Write-side external tools should be avoided in V1. If unavoidable, they require prepare/confirm/commit and idempotency key.

## 17. API

Minimal V1:

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

`/messages` can be sugar over `/interventions` for chat-like UX. Internally every mid-run message becomes an intervention with classification.

Run creation request:

```json
{
  "conversation_id": "conv_...",
  "instrument_id": "optional",
  "goal": "研究强瑞技术...",
  "constraints": {
    "exclude": [],
    "focus": []
  },
  "idempotency_key": "client-generated"
}
```

Intervention request:

```json
{
  "message": "技术面先不要，重点深挖液冷订单、客户、利润率和订单持续性。",
  "intervention_type": "REPLAN",
  "idempotency_key": "client-generated"
}
```

## 18. Events

### Domain / Audit Events

Persist in PostgreSQL audit/event log:

- `agent.run_created`
- `agent.plan_created`
- `agent.intervention_received`
- `agent.run_replanned`
- `agent.run_paused`
- `agent.run_resumed`
- `agent.run_cancelled`
- `agent.checkpoint_created`
- `agent.tool_discarded_as_stale`
- `research.updated`
- `thesis.revalidation_requested`

### UI / Telemetry Events

Redis Stream + optional log:

- `agent.run_started`
- `agent.step_started`
- `agent.step_progress`
- `agent.step_completed`
- `agent.tool_started`
- `agent.tool_completed`
- `agent.token_stream_delta`

### Event Envelope

```json
{
  "event_id": "uuid",
  "event_type": "agent.step_completed",
  "run_id": "run_...",
  "revision": 2,
  "step_id": "step_...",
  "tool_call_id": null,
  "trace_id": "trace_...",
  "occurred_at": "2026-09-12T...",
  "payload": {}
}
```

## 19. Error Recovery

| Case | Handling |
|---|---|
| LLM timeout | Mark planning/step attempt failed, retry with bounded retries, preserve checkpoint, show resumable failure if exhausted. |
| Tool timeout | Mark tool call `FAILED_TIMEOUT`, decide retry from tool policy, keep step pending or failed. |
| Worker crash | In-flight steps detected by heartbeat timeout; requeue if idempotent and run revision still current. |
| Redis restart | Queue/progress may be interrupted; PostgreSQL run/checkpoint state remains durable; reconciler requeues runnable steps. |
| Postgres unavailable | Do not commit tool result; retry persistence; if prolonged, fail/pause run because durable state cannot be updated. |
| User cancels but tool already sent externally | Set cancellation token; if tool returns, stale/cancel check discards local result; external side effect must be handled by tool-specific compensating note. |
| Old revision result returns | Conditional update fails; mark `DISCARDED_STALE`; emit stale event. |
| Consecutive direction changes | Append interventions; debounce; produce one new revision and plan. |
| Browser closed, resume next day | Load PostgreSQL run + latest checkpoint; rehydrate UI and enqueue pending steps. |
| Bad long-term memory proposal | Store as proposal only; require user confirmation or reject; record policy reason. |

## 20. Concurrency

### Can One Conversation Have Multiple Active Runs?

V1 recommendation: allow one foreground active run per conversation, plus background system jobs. If user asks unrelated work, create a new run but show both clearly. Avoid hidden parallel foreground agent runs in one conversation.

### Can One Instrument Have Multiple Active Jobs?

Allow different job types with constraints:

- Research Refresh: at most one active per instrument and freshness scope.
- Thesis Revalidation: can run while report ingestion runs, but consumes committed Evidence snapshots only.
- Report Ingestion: multiple files allowed; dedupe by source hash and idempotency key.

### Two Reports Arrive Together

Store each as separate Evidence source with content hash unique constraint. A downstream research refresh can batch both into one new Research Package revision.

### User Double-Clicks Refresh

Same idempotency key returns same run. If key differs, unique active-job constraint for `(instrument_id, job_type, scope, status in active)` prevents duplicate work.

### Worker Retry and Evidence

Evidence writes require source hash, external source ID, and idempotency key unique constraints. Retry updates existing attempt or no-ops, never duplicates facts.

### SSE Reconnect

Events carry monotonic event IDs or Redis Stream IDs. Client reconnects with cursor and dedupes by `event_id`.

## 21. Data Consistency

Strong consistency required:

- Trade Plan freeze/revision.
- Thesis version creation.
- Memory version/supersede.
- Run revision transition.
- Domain proposal confirm/commit.
- Evidence identity/deduplication.

Eventual consistency acceptable:

- Research worker intermediate progress.
- UI progress display.
- Derived summaries.
- RAG/vector indexing after Evidence commit.
- Notification delivery.

Thesis/Trade Plan/Memory version writes should be transactionally committed with their audit record and idempotency record.

## 22. Observability

Minimum fields everywhere:

```text
run_id
revision
trace_id
step_id
tool_call_id
idempotency_key
user_id
instrument_id
event_type
status_before
status_after
policy_decision
error_code
```

Questions this must answer:

- Why did this run fail?
- When did the user change target?
- Which plan was active?
- Which tool result was discarded and why?
- Why did Thesis change?
- Which memory was proposed, confirmed, superseded, or rejected?

## 23. Frontend UX

Use server run state as source of truth.

Required UI:

```text
正在执行 3 / 7

✓ 公司业务
✓ 行业
● 液冷订单
○ 财务
○ 估值
○ 技术结构
```

After intervention:

```text
收到方向调整

已保留：
公司业务
产业背景

已取消：
技术结构

新增：
液冷客户
订单持续性
毛利率

从当前 Checkpoint 继续
```

Controls:

- Pause: sends soft interrupt.
- Resume: resumes latest checkpoint.
- Cancel: hard cancel.
- Adjust direction: sends intervention message.
- Tool progress: show high-level tool name/status only; avoid raw internal logs unless user expands details.

Page close and return:

- UI loads `/agent/runs/{run_id}`.
- Events resume from cursor.
- No durable local frontend state required.

## 24. P0 Implementation Scope

P0:

- Run, revision, step, intervention, tool call, checkpoint tables.
- Minimal orchestrator service.
- Worker cooperative cancellation.
- Stale result guard.
- SSE or Redis Stream-backed event endpoint.
- Basic frontend run progress panel.
- Prepare/confirm proposal envelope for domain writes.

Not P0:

- Temporal.
- Kafka.
- Multi-agent orchestration.
- General workflow DSL.
- Cross-device collaborative editing.
- Complex DAG UI.
- Full observability platform.

## 25. Acceptance Criteria

1. User starts a multi-step research run and can see plan progress.
2. User changes direction mid-run; existing completed steps remain visible.
3. Pending obsolete steps become `SUPERSEDED` or `CANCELLED`.
4. New revision is created with a revised plan.
5. Tool results from older revision are marked `DISCARDED_STALE` and cannot update current output.
6. Pause creates a checkpoint and stops new work.
7. Resume continues from checkpoint after page refresh or service restart.
8. Cancel sets token and worker stops at next cooperative boundary.
9. Duplicate intervention requests with the same idempotency key do not create duplicate revisions.
10. SSE reconnect does not duplicate user-visible events.

