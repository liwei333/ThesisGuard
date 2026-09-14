# TASK-WP04-01-R1 Acceptance Report

**OVERALL: FAIL**

## Metadata

- Task ID: `TASK-WP04-01-R1`
- Original Task: `TASK-WP04-01`
- Date: `2026-09-14` (`Asia/Shanghai`)
- Verifier: Codex (independent `ai-task-governor` verifier run)
- Report Path: `docs/acceptance/TASK-WP04-01-R1-acceptance.md`
- Path Basis: the project uses `docs/acceptance/` for persisted task-governance artifacts
- Implementation Status: executor reported `IMPLEMENTATION_COMPLETE`; independent verification completed
- Implementation Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-evidence-persistence`
- Branch: `codex/wp04-evidence-persistence`
- HEAD / Baseline Commit: `a36c707898452340c35bdcfbceaf7d38bb3b4fa1`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`
- Missing Acceptance: `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Overall Verdict: `FAIL`
- Repair Required: `YES`
- Repair Task: `TASK-WP04-01-R2`
- Next Action: repair the no-predecessor EvidenceVersion v1 state constraint and close the directly related persistence-test gaps before WP04-02.

## Executive Decision

R1 successfully repairs the previously identified SourceType, SourceGrade, actor, SourceDocument identity, repository path, repository helper, child-loading, migration-cycle, and PostgreSQL skip deficiencies. The focused suite now executes 16 tests with zero skips on accessible PostgreSQL, the full suite passes 83 tests, and lint/type checking is clean.

R1 nevertheless cannot pass because a direct PostgreSQL counterexample violates the accepted initial-state machine. The current checks constrain what a `status_change_kind` may target, but do not constrain which states a no-predecessor version 1 may start in. PostgreSQL accepted all four of these contract-illegal rows:

- no-predecessor v1 `PENDING_REVIEW` with `REVIEW_REQUEST`;
- no-predecessor v1 `REJECTED` with `REVIEW_DECISION`;
- no-predecessor v1 `DISPUTED` with `DISPUTE`;
- no-predecessor v1 `VERIFIED` with `REVIEW_DECISION`.

The accepted contract permits exactly two brand-new no-predecessor v1 forms: `UNREVIEWED` with the all-null lifecycle audit tuple, or trusted direct `VERIFIED` with a complete audit tuple and `status_change_kind='INITIAL_VERIFICATION'`. The current 16-test suite contains no positive or negative initial-VERIFIED test, so the database hole is not regression-protected.

## Changed Files Snapshot

- `BASELINE_CHANGED_FILES`:
  - `backend/common/db/models_registry.py`
  - `backend/evidence/models.py`
  - `backend/evidence/repository.py`
  - `migrations/versions/20260914_004_evidence_persistence.py`
  - `tests/test_evidence_persistence.py`
- `FINAL_CHANGED_FILES`:
  - `backend/common/db/models_registry.py`
  - `backend/evidence/models.py`
  - `backend/evidence/repositories.py`
  - `migrations/versions/20260914_004_evidence_persistence.py`
  - `tests/test_evidence_migrations.py`
  - `tests/test_evidence_persistence.py`
- `backend/evidence/repository.py` no longer exists.
- Task-attributable Changes: all six final files are attributable to accumulated WP04-01 plus R1.
- Attribution: `CERTAIN`.

Relevant SHA-256 snapshot:

- `backend/evidence/models.py`: `c7a411121833c056245ca8f57138abf8321cc3e9e2c514ad5d01eb255234b488`
- `backend/evidence/repositories.py`: `c043abb0b8c0f4872b7802558bc3815ad40d951206ef3a448ffd19afaad39f01`
- `migrations/versions/20260914_004_evidence_persistence.py`: `05b1fd608f7439b811c27f31b7adfd0900eeacb0e400c3b4d68922b938211884`
- `backend/common/db/models_registry.py`: `56a6d416716f9ee1f3418a7942a41db0cf9a52d36f33d384c027623e9e54260c`
- `tests/test_evidence_migrations.py`: `3fa145b25415a32ccee814426d45a618605533784252abb3e3e99100c5f1e530`
- `tests/test_evidence_persistence.py`: `8c592d0962377bbb41d741dd2d411c483d88242182237ba6f63f58529dec381c`

## Classification

- Task Type: `REPAIR / DB_PERSISTENCE / MIGRATION / REPOSITORY / TESTS`
- Risk Type: authoritative enum/identity truth, immutable Evidence lifecycle, latest-version reads, migration reversibility
- Touched Layers: SQLAlchemy model, Alembic migration, model registry, async repository, PostgreSQL tests
- Task Size: `MEDIUM`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, G5 Regression, G6 Evidence, DB Persistence Gate
- Not Applicable Gates: API, browser/UI, worker/queue, MinIO byte I/O, embeddings/RAG, external provider

## Top Blocking AC Results

| Top AC | Result | Independent evidence |
|---|---|---|
| TOP-AC-R1-01 — exact enums and SourceDocument identity | PASS | Model and migration use the exact fifteen SourceTypes, S-F grades including E, the broad actor set plus narrow source-status actors, and the named non-empty identity check. Real PostgreSQL positive/negative tests pass. |
| TOP-AC-R1-02 — authorized repository and current semantics | PASS | Singular module is gone; plural repository exposes all required identity/version/current/history helpers. Current orders by descending version without status filtering, and exact reads load all six child-link directions/collections. |
| TOP-AC-R1-03 — PostgreSQL tests prove the persistence contract | **FAIL** | Migration round trip and 16 focused tests are real and zero-skip, but the suite omits the required initial-VERIFIED/initial-state boundary. Direct PostgreSQL inserted four illegal no-predecessor v1 states. |
| TOP-AC-R1-04 — scope and regressions | PASS | Only allowlisted WP04-01/R1 files changed; full 83-test suite, Ruff, mypy, compileall, Alembic head, and diff integrity pass. |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Exact worktree, branch, unchanged HEAD, accumulated file set, R1 contract, prior FAIL report, accepted domain contract, and executor report were inspected. |
| G1 Scope | PASS | Final changes are inside the R1 allowlist; repository rename is complete; no API/frontend/service/worker/dependency/config drift was found. |
| G2 Contract | **FAIL** | No-predecessor v1 rows can start in PENDING_REVIEW, REJECTED, DISPUTED, or VERIFIED with REVIEW_DECISION, contradicting contract sections 12 and 21. |
| G3 Architecture | PASS | Canonical source identities, plural repository boundary, exact-version/current/history reads, and immutable child eager-loading now match the intended persistence architecture. |
| G4 Test | **FAIL** | Existing tests do not exercise brand-new trusted VERIFIED or illegal no-predecessor initial states, so 16/16 and 83/83 are false-negative for this Blocking boundary. |
| G5 Regression | PASS | Full suite: `83 passed, 4 warnings`; Ruff and mypy pass; warnings are pre-existing dependency deprecations. |
| G6 Evidence | **FAIL** | Executor evidence is accurate for executed commands but claims contract completion without the missing initial-state counterexample. Direct DB evidence overrides the self-report. |
| DB Persistence Gate | **FAIL** | Real PostgreSQL accepts state rows that require a prior exact EvidenceVersion even though `supersedes_evidence_version_id` is null. |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary/Negative Evidence | Verdict |
|---|---|---|---|---|---|
| R1-AC-01 [BLOCKING] | Exact SourceType, grade, and actor checks | `models.py:25-44`; migration constants mirror them | Focused enum tests pass against PostgreSQL | Removed/unknown types, actor, grade rejected; valid values accepted | PASS |
| R1-AC-02 [BLOCKING] | SourceDocument always has external or URL identity | Named check in model and migration | Positive external-only/URL-only/both plus negative neither tests pass | Duplicate external/fallback and URL precedence cases pass | PASS |
| R1-AC-03 [BLOCKING] | Required repository surface and plural path | `repositories.py:47-191`; singular path absent | Repository tests execute real ORM reads | URL fallback explicitly requires null external ID; current has no status filter | PASS |
| R1-AC-04 [BLOCKING] | Brand-new no-predecessor v1 has only two allowed initial forms | Existing checks at `models.py:412-492` and migration lines 398-478 are one-directional | No persisted test covers valid initial VERIFIED or illegal initial states | Four illegal rows inserted successfully in disposable PostgreSQL | **FAIL** |
| R1-AC-05 [BLOCKING] | Replacement v1, correction, audit tuple, and tombstones remain constrained | Existing and R1 constraints present | Focused replacement/tombstone tests pass | Wrong replacement kind, null/partial audit, missing correction predecessor, missing trusted rule rejected | PASS |
| R1-AC-06 [BLOCKING] | Migration is reversible and preserves WP01-WP03 | Dedicated migration test performs 3→4→3→4 | Test passes on disposable PostgreSQL | WP01-WP03 tables remain; WP04 tables disappear/reappear; Research link absent | PASS |
| R1-AC-07 [BLOCKING] | Required tests cannot pass by skipping PostgreSQL | Fixtures connect directly with no skip conversion | Sandbox run fails with 14 DB errors rather than passing; escalated run executes 16/16 | Zero skips on accessible PostgreSQL | PASS |
| R1-AC-08 [BLOCKING] | Existing project behavior remains green | No out-of-scope runtime code changed | Full pytest 83/83, Ruff, mypy, compileall, Alembic head, diff check pass | No dependency or external module drift | PASS |

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| worktree status/branch/HEAD/list and file inventories | expected worktree/branch/HEAD; six final files | Baseline, scope, attribution |
| focused pytest in sandbox | exit 1; `2 passed, 14 errors`, all errors from local PostgreSQL socket policy; no skips | Prove required DB tests do not manufacture a passing result |
| identical focused pytest with local PostgreSQL access | exit 0; `16 passed, 2 warnings`, zero skips | Focused R1 regression |
| full pytest with local PostgreSQL access | exit 0; `83 passed, 4 warnings` | Full regression |
| Ruff over `backend/ apps/` | exit 0 | Lint |
| mypy over `backend apps` | exit 0; 48 source files | Type check |
| compileall over repaired code/tests | exit 0 | Syntax/import verification |
| `alembic -c migrations/alembic.ini heads` | `000000000004 (head)` | Migration topology |
| `git diff --check` and scope scans | exit 0 for integrity; no forbidden implementation references | Scope/static verification |
| disposable PostgreSQL migration to head | exit 0 | Build real schema for negative probe |
| insert no-predecessor v1 VERIFIED with REVIEW_DECISION | exit 0; row returned | Illegal initial VERIFIED counterexample |
| insert no-predecessor v1 PENDING_REVIEW, REJECTED, DISPUTED | exit 0; all three rows returned | Illegal initial-state counterexamples |

The disposable database `tg_wp04_r1_acceptance_probe_20260914` was dropped after verification. No project or user database was modified.

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| Valid contract enum rejected or stale enum accepted | Yes | R1 PostgreSQL tests exercise all exact values and removed/unknown values | PASS |
| Null/null source identity bypasses partial indexes | Yes | Named identity check and DB test reject it | PASS |
| URL fallback resolves an external-ID row | Yes | Repository query requires external ID null; regression returns none | PASS |
| Current skips a newest tombstone | Yes | Tombstone test returns v2 RETRACTED as current | PASS |
| No-predecessor v1 enters a post-creation state | Yes | PENDING_REVIEW, REJECTED, and DISPUTED rows all committed | **FAIL** |
| Initial trusted VERIFIED uses a review/dispute transition kind | Yes | v1 VERIFIED with REVIEW_DECISION committed | **FAIL** |
| PostgreSQL unavailability is hidden by skip | Yes | Sandbox run errors; accessible run has zero skips | PASS |

## DB Persistence Result

- Schema constraints: enum, identity, version, provenance, child-link, idempotency, replacement, and tombstone constraints largely pass; initial-state constraint remains incomplete.
- Read semantics: required identity/exact/current/history paths pass; current returns the highest version without status fallback.
- Replace semantics: replacement v1 requires predecessor, CORRECTION, and complete audit tuple.
- Active/inactive/deleted/status: newest RETRACTED stays current, but illegal initial lifecycle statuses can be persisted.
- Transaction boundary: this persistence-only task does not implement multi-table command services; PostgreSQL tests use isolated transactions/disposable databases.
- Version/snapshot/history: ascending history and exact/current reads pass; the failing rows demonstrate invalid initial history can still be created.
- Real persistence vs InMemory/Fake/Mock: all decisive evidence used real PostgreSQL.

## Blocking Findings

### B-R1-01 — No-predecessor v1 initial-state constraint is not bidirectional

- Locations: `backend/evidence/models.py:412-492`; `migrations/versions/20260914_004_evidence_persistence.py:398-478`
- Contract: `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md:457-509`, especially lines 495-496; database blueprint lines 1210-1229
- Failed AC/Gates: TOP-AC-R1-03, R1-AC-04, G2, G4, G6, DB Persistence Gate
- Root cause: checks such as `status_change_kind <> 'REVIEW_DECISION' OR verification_status IN (...)` validate kind-to-status, but do not require a prior version for post-creation kinds or restrict a no-predecessor v1 to the two legal initial forms.
- Direct evidence: four contract-illegal rows with `version=1` and null `supersedes_evidence_version_id` committed successfully.
- Required repair: add one model/migration-aligned named check limiting no-predecessor v1 to either all-null UNREVIEWED or fully audited VERIFIED with INITIAL_VERIFICATION, plus permanent positive/negative PostgreSQL tests.

## Non-Blocking Findings

- `tests/test_evidence_migrations.py` uses `WP04_TABLES.issubset(upgraded_tables)` instead of proving the revision-4 table delta equals exactly `WP04_TABLES`. R2 should tighten this while already touching the migration test.
- The R1 contract asked for both INVALIDATED and RETRACTED tombstone coverage and a true derivation duplicate case. Current tests directly cover RETRACTED and derivation self-link, but not a positive/negative INVALIDATED pair or a duplicate non-self derivation edge. R2 should add these regression cases without changing unrelated implementation.
- Existing Starlette/httpx/AnyIO/FastAPI warnings are unrelated to WP04.

## Regression Result

- Result: `PASS`
- Preserved behavior: all current WP01-WP03 tests, exact enum/source identity behavior, repository reads, migration round trip, replacement/tombstone paths, and frontend/config checks
- Regression gap: initial no-predecessor EvidenceVersion state legality is not covered and is currently incorrect.

## Repair Required

- Repair Required: `YES`
- Repair ID: `TASK-WP04-01-R2`
- Failed AC/Gates: TOP-AC-R1-03, R1-AC-04; G2, G4, G6, DB Persistence Gate
- Repair policy: add the missing initial-state check and focused regression cases only; preserve every R1 PASS result and the six-file scope.

## Final Decision Rationale

`FAIL`. R1 closes the originally observed enum, identity, repository, migration, and skip gaps, but PostgreSQL still accepts impossible initial lifecycle histories. Because Evidence history is authoritative and immutable, permitting illegal history creation is a Blocking L3/L4 failure even though all current tests pass.

## Next Action

Execute `TASK-WP04-01-R2` in the same isolated worktree. Do not begin WP04-02 or perform Git integration until R2 receives independent L1-L4 PASS.

