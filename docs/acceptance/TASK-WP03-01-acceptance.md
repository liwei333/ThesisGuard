# ACCEPTANCE REPORT

**OVERALL: PASS**

## Metadata

- Task ID: `TASK-WP03-01`
- Date: `2026-09-13` (`Asia/Shanghai`)
- Verifier: Codex, independent `ai-task-governor` VERIFIER pass
- Report Path: `docs/acceptance/TASK-WP03-01-acceptance.md`
- Path Basis: the project had no existing acceptance/governance directory or configured report path, so the project-local `docs/acceptance/` convention was selected.
- Implementation Status: `IMPLEMENTATION_COMPLETE`; implementation remains intentionally uncommitted in the isolated worktree.
- Implementation Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp03-research-package`
- Branch: `codex/wp03-research-package`
- Baseline Commit: `d9bceedf27d80c84472613868b97d7b172cacfd6`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Missing Acceptance: none
- Repair Required: `NO`
- Next Action: close `TASK-WP03-01`; dispatch the smallest next slice, `TASK-WP03-02` Research Package HTTP API contract and real API-to-PostgreSQL verification.

## Changed Files Snapshot

- `BASELINE_CHANGED_FILES`: none; the isolated worktree was created from the baseline commit before implementation.
- `FINAL_CHANGED_FILES`:
  - `M backend/common/db/models_registry.py`
  - `?? backend/research/models.py`
  - `?? backend/research/schemas.py`
  - `?? backend/research/services.py`
  - `?? docs/WP03_RESEARCH_PACKAGE_PERSISTENCE.md`
  - `?? migrations/versions/20260912_003_research_package.py`
  - `?? tests/test_research_persistence.py`
- Task-attributable Changes: all seven files above implement or verify the bounded WP-03 persistence slice.
- Attribution: `CERTAIN`
- Main Worktree: remained clean at `d9bceedf27d80c84472613868b97d7b172cacfd6` before this acceptance report was added.

## Classification

- Task Type: `DB_PERSISTENCE` + `MIGRATION` + backend domain service
- Risk Type: append-only history, DB integrity, optimistic concurrency, idempotency, transaction rollback, freshness semantics
- Touched Layers: SQLAlchemy entity/model, domain service, Pydantic read schema, Alembic migration, model registry, PostgreSQL integration tests, implementation documentation
- Task Size: `MEDIUM`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, DB Persistence, G5 Regression, G6 Evidence
- Not Applicable Gates: API/runtime HTTP, browser/UI, permission/tenant/DataScope, queue/worker, external provider, Evidence/Thesis/Agent Runtime

## Top Blocking AC Results

| Top AC | Result | Evidence |
|---|---|---|
| TOP-AC-01 — real PostgreSQL models and migration enforce package/module identity, version, lineage, allowed values, foreign keys, unique constraints, and timezone-aware timestamp columns | PASS | `backend/research/models.py:43-169`; `migrations/versions/20260912_003_research_package.py:21-144`; independent `upgrade head`; PostgreSQL catalog output showed revision `000000000003`, all named CHECK/FK/UNIQUE constraints, and every required temporal column as `timestamp with time zone`. |
| TOP-AC-02 — services create version 1, read current/history/specific version, and create transactional append-only N+1 copy-on-write refreshes without mutating history | PASS | `backend/research/services.py:102-242`, `245-378`; real PostgreSQL tests `test_initial_package_persists_version_modules_and_unverified_freshness` and `test_refresh_creates_lineage_and_copy_on_write_without_mutating_history` passed. |
| TOP-AC-03 — duplicate, expected-version, concurrency, idempotency, DB-unique, and rollback behavior are safe and deterministic | PASS | `backend/research/services.py:255-378`; focused PostgreSQL suite passed duplicate initial/same-key/different-hash/stale expected-version/concurrent refresh/unique-constraint/rollback cases; final history after concurrent refresh was `[1, 2]`. |
| TOP-AC-04 — eleven module types, lifecycle/freshness states, timestamps, source references, and fact boundary are explicit; empty modules are not represented as verified research | PASS | `backend/research/models.py:20-36`; `backend/research/services.py:89-99`, `290-316`; initial DB rows contained 11 `UNVERIFIED` modules with `summary IS NULL` and empty `source_refs`; deterministic freshness test passed. |
| TOP-AC-05 — static quality, full regression, migration, and real PostgreSQL evidence satisfy the declared acceptance levels | PASS | `make lint` passed; `make typecheck` passed; focused PostgreSQL suite `8 passed`; full suite `49 passed`; Compose config passed; real migration upgrade/downgrade and schema inspection passed. |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Worktree and branch resolve to baseline `d9bceed...`; main is unchanged; current seven-file delta is attributable to `TASK-WP03-01`; execution report used only as a clue. |
| G1 Scope | PASS | Diff is limited to Research persistence/service/schema/tests/docs and one model-registry import. No API/router, frontend, worker, Evidence, Thesis, Agent, dependency-file, old-migration, or unrelated refactor change was found. |
| G2 Contract | PASS | All five Top Blocking AC have implementation, runtime/DB, negative, and regression evidence. |
| G3 Architecture | PASS | Uses the modular-monolith ownership boundary, async SQLAlchemy 2.x sessions, Pydantic v2 schemas, Alembic, DB-backed CAS/unique constraints, append-only service methods, and no LLM/system-of-record bypass. |
| G4 Test | PASS | Fresh verifier runs passed lint, typecheck, focused DB tests, full regression, Compose validation, migration upgrade, catalog inspection, and migration downgrade. |
| DB Persistence | PASS | Production-equivalent PostgreSQL/asyncpg/Alembic/SQLAlchemy path was executed; unique, FK, CHECK, timezone, current/latest/history, version lineage, copy-on-write, concurrency, and rollback behavior were verified at the appropriate evidence level. |
| G5 Regression | PASS | Full existing suite plus WP-03 tests: `49 passed, 2 warnings`; no existing test was deleted, skipped, or weakened in the diff. |
| G6 Evidence | PASS | Full Evidence Matrix is complete. Executor self-report was not used as sole proof. L4 was based on fresh verifier-controlled PostgreSQL execution, not Mock/Fake/InMemory behavior. |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary/Negative Evidence | Verdict |
|---|---|---|---|---|---|
| TOP-AC-01 [BLOCKING] | Durable schema and constraints | Model and migration definitions listed above | Fresh Alembic upgrade on `tg_wp03_acceptance_20260913`; direct `pg_constraint` and `information_schema.columns` inspection | Duplicate package version and duplicate module type raised real PostgreSQL `IntegrityError`; migration downgrade removed both tables | PASS |
| TOP-AC-02 [BLOCKING] | Append-only versioned service behavior | Creation/read/refresh/select-for-update/copy-on-write code | Real DB initial, current, history, specified-version, and refresh tests | Version 1 remained readable and unchanged after version 2 was created; no partial mutation path observed | PASS |
| TOP-AC-03 [BLOCKING] | Concurrency and idempotency safety | Idempotency lookup/hash check, row lock, unique constraints, savepoint conflict translation | Real concurrent `asyncio.gather` refresh test produced exactly one create and one conflict | Same key/same hash returned the existing package; same key/different hash, stale version, duplicate DB keys, and multitable failure were rejected | PASS |
| TOP-AC-04 [BLOCKING] | Status/freshness/fact boundary | Allowed-value constraints, `calculate_module_freshness`, empty module constructor | Real persisted initial package plus deterministic freshness unit test | Empty module summaries/source refs were not fabricated; failed, unverified, fresh, and stale branches were checked | PASS |
| TOP-AC-05 [BLOCKING] | Required quality and regression evidence | New focused tests and unchanged project quality commands | Lint/typecheck/focused/full tests/Compose/Alembic commands all passed in a verifier-controlled run | The initial sandbox run produced seven PostgreSQL skips and was explicitly rejected as L4 evidence; the same suite was rerun with DB access and produced 8/8 passes | PASS |

### Acceptance Level Evidence

- `L1_STATIC_REVIEWED`: all seven changed files, related project architecture/status docs, existing model/session/API patterns, migration chain, and tests were inspected.
- `L2_BUILD_VERIFIED`: `make lint`, `make typecheck`, `docker compose config --quiet`, and `git diff --check` passed.
- `L3_CONTRACT_VERIFIED`: focused contract suite passed 8 tests; complete regression suite passed 49 tests.
- `L4_DB_VERIFIED`: disposable real PostgreSQL databases were migrated and exercised through the async service; a separate verifier database was upgraded, inspected through PostgreSQL catalogs, downgraded, checked for table removal, and deleted.
- Missing: none.

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| `git status --short --branch` in main and isolated worktree | PASS | Baseline, branch, changed-file inventory, and main isolation |
| `git worktree list --porcelain` / `git merge-base` / `git rev-parse HEAD` | PASS | Worktree and baseline attribution |
| `git diff --check` | PASS | Whitespace/diff integrity |
| `make lint` | PASS — `All checks passed!` | Ruff project lint gate |
| `make typecheck` | PASS — `Success: no issues found in 45 source files` | Mypy gate; rerun outside sandbox after cache-permission-only internal error |
| `docker compose config --quiet` | PASS | Compose configuration validity |
| `pytest -q tests/test_research_persistence.py -rs` | PASS — `8 passed, 2 warnings` | Focused real PostgreSQL contract and persistence verification |
| `pytest -q` | PASS — `49 passed, 2 warnings` | Complete regression suite |
| `alembic -c migrations/alembic.ini upgrade head` against `tg_wp03_acceptance_20260913` | PASS | Fresh real PostgreSQL migration to revision `000000000003` |
| PostgreSQL catalog query for constraints, temporal types, and Alembic revision | PASS | Real schema constraint and timezone evidence |
| `alembic ... downgrade 000000000002` plus `to_regclass` checks | PASS | Reversible migration; both WP-03 tables absent after downgrade |
| Temporary DB count and cleanup checks | PASS — `0` test DBs remained; dedicated acceptance DB deleted | Cleanup and no leaked test state |

The first focused test run inside the filesystem/network sandbox reported `1 passed, 7 skipped` because local PostgreSQL access was denied. It was not counted as evidence. The verifier reran the command with approved local DB access and obtained `8 passed`; this distinction is material to the PASS verdict.

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| Duplicate initial creation | Yes | Same request replay returned same row; a different initial request was rejected | PASS |
| Same idempotency key with different payload hash | Yes | `IdempotencyConflict` test passed | PASS |
| Stale `expected_version` | Yes | Expected 1/current 2 conflict fields asserted | PASS |
| Two concurrent refreshes targeting the same version | Yes | Exactly one version 2 committed; the peer returned a version conflict | PASS |
| Duplicate package version/module type at DB boundary | Yes | Real PostgreSQL `IntegrityError` assertions passed | PASS |
| Multi-table partial write | Yes | Forced duplicate modules caused domain persistence conflict; package and module counts remained zero | PASS |
| Stale history leaking into current read | Yes | Current selects highest version; explicit history returned `[1, 2]`; version 1 remained separately addressable | PASS |
| Fabricated research facts | Yes | Initial/refreshed empty modules stayed `UNVERIFIED`, `summary=None`, `source_refs=[]` | PASS |

## DB Persistence Result

- Schema constraints: real PostgreSQL catalog confirmed PK, FK, UNIQUE, CHECK, positive version, lineage, allowed status/type, and idempotency constraints.
- Read semantics: current is highest package version for one instrument; history is ascending; specified version is constrained by instrument and version.
- Replace semantics: not applicable; this task is append-only and uses copy-on-write.
- Active/inactive/deleted/status: active/deleted/tenant semantics are not part of this bounded task; lifecycle and freshness status constraints were verified.
- Transaction boundary: nested transaction/savepoint plus outer session transaction prevented partial package/module rows in the forced-failure case.
- Version/snapshot/history: version 1 remained accessible after version 2; new package and module IDs were created; lineage and module origins were preserved.
- Real persistence vs InMemory/Fake/Mock: all L4 claims come from PostgreSQL 17-compatible behavior through asyncpg/SQLAlchemy/Alembic; no Fake or InMemory repository was accepted as DB evidence.

## Blocking Findings

None.

## Non-Blocking Findings

1. The focused DB fixture skips when PostgreSQL is unavailable, so a green `pytest -q` alone does not prove L4. CI or future task runners should additionally assert that the PostgreSQL-marked suite reports zero skips. This verification explicitly reran with DB access, so it does not block this verdict.
2. The older PRD/TAD uses product-facing Research states `ACTIVE / STALE / UPDATING / FAILED`, while this slice defines package lifecycle states and derives module freshness separately. The HTTP contract task must expose and document the mapping so clients cannot silently treat stale or unverified content as active. This is an API-contract concern, not a failure of the accepted persistence behavior.
3. The eleven module-type values are duplicated in `models.py` and `services.py`. Consolidation may reduce future drift but is not required for this task and must not trigger unrelated refactoring.
4. The executor installed `greenlet` into the local interpreter user site to satisfy the already-declared `sqlalchemy[asyncio]` runtime expectation. No repository dependency file changed. Reproducible environment installation should continue to use the pinned project requirements.

## Regression Result

- Result: `PASS`
- Preserved behavior: all pre-existing compose/config/frontend-config/health/instrument/watchlist/migration/system/task tests passed.
- Regression gaps: no public Research HTTP or browser flow exists in this task by design; those are deferred, not claimed.

## Repair Required

- `NO`
- Repair ID: not applicable
- Failed AC/Gate: none

## Final Decision Rationale

`PASS`. Every Top Blocking AC and selected Blocking Gate has fresh non-self-report evidence. The verifier exercised the real PostgreSQL persistence path, observed all eight focused tests passing without skips, independently inspected the installed database constraints and timezone types, proved migration downgrade behavior, and ran the complete 49-test regression suite. The implementation stayed within the dispatched persistence slice and did not fabricate Research/Evidence/Thesis capability.

## Next Action

Close `TASK-WP03-01`. Dispatch `TASK-WP03-02` as a separate, medium-sized task: define and implement the Research Package HTTP API over the accepted service, register the router, map stable domain errors, expose explicit lifecycle plus freshness semantics, and prove the real ASGI-to-PostgreSQL path. Keep frontend client generation/UI, worker/Redis, Evidence, Thesis, and Agent Runtime out of scope.
