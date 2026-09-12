# ThesisGuard Memory Architecture

> Status: Proposed / Review Baseline, not implemented
> Date: 2026-09-12
> Scope: User memory, memory write gate, retrieval/context builder, memory vs source-of-truth boundary
> Authority: Runtime/session state follows [Agent Runtime Architecture](./AGENT_RUNTIME_ARCHITECTURE.md); writes follow [Tool Runtime & Approval](./TOOL_RUNTIME_AND_APPROVAL.md); `MemoryWriteProposal` follows [Structured Output Contracts](./STRUCTURED_OUTPUT_CONTRACTS.md)

Implementation priority decision: **Session Memory and Working Memory are P0 runtime concerns; Preference, Discipline, Behavior and Episodic long-term memory are P1.** This document defines their contracts now but does not authorize implementing long-term memory before Research/Evidence/Thesis and the minimal Agent Runtime are reliable.

## 1. Memory vs Source of Truth

ThesisGuard should not use one large "User Memory" text blob. The product needs structured, typed, auditable memory with clear boundaries.

Core rule:

```text
Memory helps personalize reasoning.
Source of Truth determines business state.
```

Memory must never override:

- System/domain policy.
- Current explicit user instruction.
- Verified facts.
- Frozen Trade Plan.
- Thesis/Trade Plan/Evidence domain records.

Domain and Research facts should not be called Memory in V1. They belong to business database objects:

- Evidence
- Research Package
- Thesis / Thesis Version
- Expectation Snapshot
- Valuation Scenario
- Price-In Analysis
- Trade Plan / Trade Plan Version
- Discipline Records

Memory references those objects; it does not replace them.

## 2. Current Repository Reality

- No memory tables exist in current migrations.
- No `backend/memory` package exists.
- PRD/TAD mention personal trading model, behavior metrics, and Agent default context.
- V3.4.1 prototype includes "Agent 记忆策略" with Preference Memory and Discipline Memory, and explicitly rejects opinion mirroring.
- Current implementation only has Instrument/Watchlist plus infrastructure skeleton.

Therefore this document is a forward design, not a description of implemented code.

## 3. Memory Layers

| Layer | Purpose | Durable? | Source of Truth? |
|---|---|---:|---:|
| Session Memory | Current conversation turns, short-lived context | Optional transcript | No |
| Working Memory | Current run constraints, current plan, scratch summary | Yes, as run/checkpoint | No |
| Preference Memory | User preferences, trading style, default constraints | Yes | No |
| Discipline Memory | Summaries of behavior patterns derived from confirmed trade records | Yes | No, discipline records are source |
| Episodic Memory | Notable user decisions or past episodes useful for personalization | Yes, selective | No |
| Domain / Research Memory | Should be renamed Domain State / Research Facts | Yes, in business tables | Yes |

## 4. Memory Types

Recommended V1 enum:

```text
PREFERENCE
RISK_RULE
DISCIPLINE_SUMMARY
BEHAVIOR_PATTERN
EPISODIC
RUN_CONSTRAINT
USER_HYPOTHESIS
```

Do not store these as long-term memory:

- Verified financial facts.
- Consensus estimates.
- Trade Plan stop-loss values.
- Thesis versions.
- Raw research source documents.
- API keys/secrets.
- Temporary emotional statements without user confirmation.
- Agent guesses about the user.

## 5. Lifecycle Examples

| Example | Classification | Store Where | Duration | Who Can Modify | Versioned? |
|---|---|---|---|---|---:|
| 用户默认最多持仓 4 只 | RISK_RULE / Preference | `memory` after confirmation, also domain rule if product-level | Until superseded | User confirm; domain service | Yes |
| 用户偏好科技成长、产业逻辑、右侧确认 | PREFERENCE | `memory` | Until superseded or decays | User confirm or auto-propose + confirm | Yes |
| 用户过去 20 笔有 6 次止损延迟 | DISCIPLINE_SUMMARY | Derived from discipline/trade records; summary in memory allowed | Recomputed per period | Domain service from records | Yes |
| 用户今天认为强瑞明天一定涨 | USER_HYPOTHESIS | Current run / conversation, not long-term by default | Short-lived | User | No long-term unless confirmed as notable episode |
| 本次研究强瑞重点看液冷，不看技术面 | RUN_CONSTRAINT | `agent_intervention` + checkpoint | Run lifetime | User | Run revision history |
| 强瑞 2027E 一致预期当前为 4.35 亿 | VERIFIED_FACT / Expectation | Expectation domain table | Until new snapshot | Domain service | Snapshot versioned |
| 强瑞 Trade Plan v1 止损是 96 | DOMAIN_STATE | Trade Plan version table | Immutable | Domain service via confirm flow | Append-only |

## 6. Memory Write Gate

Flow:

```text
Candidate Memory
  ↓
Classify
  ↓
Should Persist?
  ↓
Conflict Check
  ↓
Version / Supersede
  ↓
Persist
```

### Candidate Memory

Created from:

- User explicit preference statements.
- Confirmed settings.
- Repeated observed behavior.
- Confirmed post-trade reviews.
- User correction of existing memory.

Not created from:

- One-off strong opinions.
- Market predictions.
- Raw facts about companies.
- Tool outputs that belong in Research/Evidence.
- Sensitive secrets.
- Hidden chain-of-thought.

### What Can Be Auto-Written?

V1 should auto-write only low-risk operational memory:

- Recently used UI defaults.
- Non-sensitive formatting preferences.
- Confirmed run constraints scoped to the run.

Long-term trading preferences should be proposed, not silently written.

### What Requires Explicit Confirmation?

- Risk limits.
- Portfolio constraints.
- Trading style preferences.
- Discipline conclusions.
- Behavioral summaries that could influence future advice.
- Any memory that changes future risk gating.

### What Must Not Enter Long-Term Memory?

- API keys, secrets, access tokens.
- Unverified financial facts.
- Temporary emotions or pressure statements.
- "User is bullish, therefore raise score" style opinion mirroring.
- Raw personal sensitive data unrelated to trading.
- Full documents or large source excerpts.

## 7. Conflict and Versioning

Memory conflicts are normal. Do not overwrite in place.

Use:

```text
ACTIVE
SUPERSEDED
REJECTED
EXPIRED
PENDING_CONFIRMATION
```

If user changes trading style:

1. Create new memory version.
2. Supersede old active version.
3. Keep `valid_from` / `valid_to`.
4. Store source intervention or confirmation.
5. Context Builder retrieves only active/current versions unless asked for history.

Confidence is useful but not enough. Use both:

- `confidence` for extraction/derivation reliability.
- `confirmation_status` for whether user accepted it.

`valid_from` and `valid_to` are necessary for trading preferences and discipline summaries because trading style changes over time.

## 8. V1 Data Model

Minimal tables:

```text
memory
memory_version
memory_source
memory_proposal
```

### memory

```text
id
user_id
memory_type
subject
status
active_version_id
created_at
updated_at
```

### memory_version

```text
id
memory_id
version
content
structured_value jsonb
confidence numeric nullable
valid_from timestamptz nullable
valid_to timestamptz nullable
confirmation_status
created_at
created_by
supersedes_version_id nullable
```

### memory_source

```text
id
memory_version_id
source_type
source_id
quote_or_summary
created_at
```

### memory_proposal

```text
id
user_id
memory_type
subject
proposed_content
structured_value jsonb
source_type
source_id
policy_decision
status
idempotency_key
created_at
resolved_at nullable
```

Possible simplification: combine `memory_proposal` into `memory_version` with `PENDING_CONFIRMATION`. Keep it separate if UI needs a review inbox.

## 9. API

Minimal V1:

```http
GET  /api/v1/memory
GET  /api/v1/memory/proposals
POST /api/v1/memory/proposals
POST /api/v1/memory/proposals/{proposal_id}/confirm
POST /api/v1/memory/proposals/{proposal_id}/reject
POST /api/v1/memory/{memory_id}/supersede
DELETE /api/v1/memory/{memory_id}
```

Request for proposal:

```json
{
  "memory_type": "PREFERENCE",
  "subject": "trading_style",
  "content": "偏好科技成长、产业逻辑、右侧确认",
  "structured_value": {
    "sectors": ["科技成长"],
    "style": ["产业逻辑", "右侧确认"]
  },
  "source_type": "user_message",
  "source_id": "intervention_...",
  "idempotency_key": "client-generated"
}
```

## 10. Retrieval and Context Builder

Question:

```text
强瑞现在可以买了吗？
```

Do not load all memory. Build context by priority and token budget.

### Recommended Context Inputs

```text
Current Request
Current Run State
Market Regime
Portfolio
Research Package
Current Thesis
Trade Plan
Relevant Preference Memory
Relevant Discipline Memory
Recent Relevant Episodic Memory
```

### Retrieval Priority

1. Current user instruction.
2. Active run constraints/interventions.
3. Domain rules.
4. Frozen Trade Plan and active Thesis.
5. Verified facts and latest source timestamps.
6. Market regime and portfolio risk.
7. Relevant confirmed preference memory.
8. Relevant discipline memory.
9. Recent episodic memory.
10. LLM inference.

### Token Budget Example

For a 16k context budget:

| Context | Budget |
|---|---:|
| Current instruction + run state | 10% |
| Domain rules and safety constraints | 10% |
| Market/portfolio/trade plan | 20% |
| Current thesis/research facts | 35% |
| Evidence summaries | 15% |
| Relevant memory | 8% |
| Reserved | 2% |

Memory should generally remain below 10-15% of prompt context unless the task is specifically about user profile or review.

### Recency and Relevance

Use filters:

- same user
- active status
- relevant memory type
- subject match
- instrument/sector/model relation
- valid time range
- confirmed or high-confidence derived summary

Conflict resolution:

- Current explicit instruction beats memory.
- Domain source-of-truth beats memory.
- Newer active version beats older superseded memory.
- Confirmed memory beats inferred memory.
- If conflict remains, include both and ask or apply conservative risk policy.

## 11. Information Priority

The proposed priority should be adjusted:

```text
System / Security Policy
>
ThesisGuard Domain Rules
>
Current Explicit User Instruction
>
Confirmed Safety / Risk Constraints
>
Frozen Trade Plan
>
Verified Facts / Source-of-Truth Domain State
>
Current Run Context
>
Confirmed Long-Term Memory
>
Unconfirmed Memory Proposals
>
LLM Inference
```

Why this differs:

- Frozen Trade Plan should beat casual current intent for safety-critical execution, but the current user can ask to prepare a revision; it still cannot silently rewrite the frozen plan.
- Verified facts should beat memory.
- Memory never overrides current explicit instruction.
- Unconfirmed proposals should be visible as pending, not silently applied.

## 12. Agent Write Boundary

Formal write flow:

```text
LLM
  ↓
Structured Proposal
  ↓
Policy
  ↓
Domain Service
  ↓
Validation
  ↓
Persist
```

### propose_thesis_update

- Agent may draft proposal.
- Requires evidence references.
- Domain service validates versioning and rules.
- User confirmation required for material thesis change in V1.

### propose_memory_write

- Agent may propose.
- Low-risk UI preferences may auto-commit.
- Trading preferences, discipline, risk rules require confirmation.

### propose_trade_plan_revision

- Always prepare/confirm/commit.
- Never modify frozen plan in place.
- Creates new version after confirmation.

### propose_research_update

- Evidence ingestion can auto-commit verified source metadata.
- Interpretive research summary should create a new research package/module version.
- Material thesis impact remains proposal unless deterministic rules allow classification.

## 13. Prepare / Confirm / Commit

Required for:

| Operation | PREPARE | CONFIRM | COMMIT |
|---|---:|---:|---:|
| Trade Plan | Required | User | Domain service creates new version |
| Thesis | Required | User for material changes | Domain service creates new version |
| Long-term Memory | Required | User except low-risk prefs | Memory service creates/supersedes |
| Delete Research | Required | User/admin | Prefer archive, not hard delete |
| Portfolio | Required | User | Domain service |
| Watchlist | Optional for add/remove; required for destructive bulk actions | User | Domain service |
| User Preference | Required for trading/risk prefs | User | Memory service |

If user interrupts with "等一下，别改" while a proposal is in `PREPARE` or `CONFIRM`, the proposal becomes `CANCELLED_BY_USER` and cannot commit.

## 14. Privacy and User Control

V1 requirements:

- User can view all long-term memory.
- User can delete, correct, or supersede memory.
- Sensitive information is blocked by policy before memory write.
- API keys must never enter prompt context or memory.
- Agent may send only relevant memory to tools and LLM calls.
- All memory rows must be scoped by `user_id`.
- Multi-user V1 should assume logical isolation in queries; if deployed beyond local personal use, add row-level security or strict service-level tenant checks.
- Encryption at rest can rely on managed disk/database in local V1, but secrets should use environment/secret manager, not memory tables.

## 15. Delivery Scope

### P0: Runtime Memory Only

- Durable conversation/session projection.
- Working Memory inside versioned Run checkpoint: current goal, constraints, plan pointer and budget.
- Explicit run constraints recorded as Intervention; no automatic cross-run promotion.
- Context Builder that retrieves authoritative domain state plus current Run/Session state.
- Policy blocklist for secrets and unverified market facts.

### P1: Long-Term User Memory

- Typed `memory` and `memory_version` tables.
- Memory proposal/write gate and structured `MemoryWriteProposal`.
- Confirmation/reject/supersede/delete API.
- User-facing memory review list and provenance explanation.
- Relevant active-memory retrieval with conflict handling.

### Explicitly Not P0/P1

- Embedding every memory item.
- Complex decay models before real usage data.
- Automatic personality inference.
- Cross-user memory.
- Multi-agent memory negotiation.
- Treating conversation summaries as durable facts.

## 16. Acceptance Criteria

1. Verified research facts are stored in domain tables, not memory.
2. User preference can be proposed, confirmed, retrieved, superseded, and deleted.
3. Memory retrieval for a stock question includes only relevant active memories.
4. Current instruction overrides conflicting memory.
5. A trade plan stop-loss is never stored as memory; it remains Trade Plan domain state.
6. Discipline memory is derived from discipline/trade records and references sources.
7. Agent cannot write high-impact long-term memory without user confirmation.
8. User can inspect why a memory was written and from which source.
