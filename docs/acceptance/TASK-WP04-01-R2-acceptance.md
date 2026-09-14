# TASK-WP04-01-R2 Acceptance Report

**OVERALL: PASS**

## Metadata

- Task ID: `TASK-WP04-01-R2`
- Original Task: `TASK-WP04-01`
- Date: `2026-09-14` (`Asia/Shanghai`)
- Verifier: Codex (independent `ai-task-governor` verifier run)
- Report Path: `docs/acceptance/TASK-WP04-01-R2-acceptance.md`
- Path Basis: the project already uses `docs/acceptance/` for task-governance artifacts
- Implementation Status: executor reported `IMPLEMENTATION_COMPLETE`; independent verification completed
- Implementation Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-evidence-persistence`
- Branch: `codex/wp04-evidence-persistence`
- HEAD / Baseline Commit: `a36c707898452340c35bdcfbceaf7d38bb3b4fa1`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Missing Acceptance: none
- Overall Verdict: `PASS`
- Repair Required: `NO`
- Next Action: close WP04-01 and perform a separately authorized local Git integration before starting the next feature task

## Executive Decision

R2 closes the no-predecessor EvidenceVersion v1 state-machine hole found by the R1 verifier. The SQLAlchemy model and Alembic revision now carry the same named `ck_evidence_version_initial_state` expression. A brand-new no-predecessor v1 is limited to exactly one of the two accepted forms: `UNREVIEWED` with a fully null lifecycle audit tuple, or trusted direct `VERIFIED` with a complete tuple and `INITIAL_VERIFICATION`.

The independent focused suite exercised real local PostgreSQL and passed 18/18 tests with zero skips. The full project suite passed 85/85. The tests also preserve replacement-v1 behavior, prove an `INVALIDATED` N+1 tombstone remains current without fallback, reject a true non-self derivation duplicate, and prove the revision-4 table delta is exactly the planned ten WP04 tables.

One required scope command returns exit 1 because the repair contract incorrectly includes `backend/common/db/models_registry.py` in a `git diff --exit-code` forbidden-path set even though that same file is explicitly part of the declared accumulated R1 baseline. This is a command-design contradiction, not R2 drift. The R1 acceptance report recorded the file's SHA-256 as `56a6d416716f9ee1f3418a7942a41db0cf9a52d36f33d384c027623e9e54260c`; the fresh R2 verification produced the identical hash. The R1 repository hash is also unchanged. Scope attribution is therefore established with a stronger before/after content check, while the invalid raw command result is retained below rather than hidden.

## Changed Files Snapshot

- `BASELINE_CHANGED_FILES`:
  - `backend/common/db/models_registry.py`
  - `backend/evidence/models.py`
  - `backend/evidence/repositories.py`
  - `migrations/versions/20260914_004_evidence_persistence.py`
  - `tests/test_evidence_migrations.py`
  - `tests/test_evidence_persistence.py`
- `FINAL_CHANGED_FILES`: the same six accumulated WP04-01 files
- R2-attributable final changes:
  - `backend/evidence/models.py`
  - `migrations/versions/20260914_004_evidence_persistence.py`
  - `tests/test_evidence_migrations.py`
  - `tests/test_evidence_persistence.py`
- R1 accumulated files proven unchanged by SHA-256:
  - `backend/common/db/models_registry.py`: `56a6d416716f9ee1f3418a7942a41db0cf9a52d36f33d384c027623e9e54260c`
  - `backend/evidence/repositories.py`: `c043abb0b8c0f4872b7802558bc3815ad40d951206ef3a448ffd19afaad39f01`
- Attribution: `CERTAIN`

## Classification

- Task Type: `SMALL REPAIR / DB_PERSISTENCE / MIGRATION / TESTS`
- Risk Type: immutable Evidence history, lifecycle integrity, migration consistency, current-version reads
- Touched Layers: SQLAlchemy model, Alembic migration, PostgreSQL persistence tests
- Task Size: `SMALL`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, G5 Regression, G6 Evidence, DB Persistence Gate
- Not Applicable Gates: API, browser/UI, frontend, worker/queue, MinIO object I/O, embeddings/RAG, external provider

## Top Blocking AC Results

| Top AC | Result | Independent evidence |
|---|---|---|
| TOP-AC-R2-01 — exact two-form brand-new v1 boundary | PASS | Model lines 121-126 and migration lines 103-108 define the same expression; real PostgreSQL positive/negative test passes. |
| TOP-AC-R2-02 — reject illegal no-predecessor v1 states | PASS | Test lines 815-871 exercise PENDING_REVIEW, REJECTED, DISPUTED, INVALIDATED, RETRACTED, non-initial VERIFIED kinds, null audit, and partial audit; focused PostgreSQL suite passes. |
| TOP-AC-R2-03 — model/migration parity and missing regressions | PASS | Migrated constraint inspection, exact table delta, replacement v1, INVALIDATED no-fallback, and non-self derivation duplicate cases all run in the 18-test PostgreSQL suite. |
| TOP-AC-R2-04 — preserve R1 and full regression | PASS | R1 forbidden-file hashes are unchanged; 85/85 full tests, Ruff, mypy, compileall, Alembic head, and diff integrity pass. |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Exact worktree, branch, HEAD, worktree list, accumulated six-file state, R1 report, R2 contract, and executor report were inspected. |
| G1 Scope | PASS | Final file set is unchanged; R1 registry/repository hashes are unchanged; R2 implementation remains within the four-file allowlist. The contradictory raw diff command is documented rather than treated as attribution evidence. |
| G2 Contract | PASS | The named check encodes exactly the accepted two-form initial-state contract without applying the branch to predecessor-bearing replacement v1 rows. |
| G3 Architecture | PASS | Constraint remains in persistence model and migration; no service/API/Agent/runtime boundary was introduced. |
| G4 Test | PASS | Focused PostgreSQL suite: 18/18; no skips. Tests contain positive, negative, migration, current-read, duplicate, and preservation cases. |
| DB Persistence Gate | PASS | Real PostgreSQL migration, constraint enforcement, ORM persistence, and repository current-read semantics were executed. No SQLite/mock/skip evidence was used for the verdict. |
| G5 Regression | PASS | Full suite 85/85; Ruff, mypy, compileall, Alembic head, and whitespace checks pass. |
| G6 Evidence | PASS | All decisive evidence was freshly produced by the verifier; executor self-report was used only as a navigation aid. |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary/Negative Evidence | Verdict |
|---|---|---|---|---|---|
| R2-AC-01 [BLOCKING] | Brand-new no-predecessor v1 allows only null-audit UNREVIEWED or fully audited VERIFIED/INITIAL_VERIFICATION | `backend/evidence/models.py:121-126,446-447`; migration `:103-108,428-430` | `test_initial_v1_without_predecessor_has_only_two_legal_forms`; focused DB suite 18/18 | Both positive forms persist; post-creation states and malformed VERIFIED forms are rejected | PASS |
| R2-AC-02 [BLOCKING] | Model, migration source, and migrated PostgreSQL share the constraint | Shared expression constants and named check | Runtime test reads SQLAlchemy constraint, migration source, and `pg_constraint`; focused suite passes | Name-only evidence is not used; the expression and actual database definition are inspected | PASS |
| R2-AC-03 [BLOCKING] | Replacement v1 remains legal under existing CORRECTION rules | Initial check excludes rows with non-null predecessor | Existing replacement test passes in focused suite | Null-audit replacement is rejected; complete audited replacement succeeds | PASS |
| R2-AC-04 [BLOCKING] | INVALIDATED N+1 is a complete current tombstone | Existing tombstone checks plus repository current ordering | `test_invalidated_tombstone_is_current_and_requires_complete_audit` passes on PostgreSQL | Missing predecessor and partial audit fail; current returns INVALIDATED rather than older VERIFIED | PASS |
| R2-AC-05 [BLOCKING] | True derivation duplicate is rejected | `uq_evidence_derivation_link_identity` preserved | Two different row IDs with identical non-self edge/role raise `IntegrityError` | Existing self-link rejection also remains covered | PASS |
| R2-AC-06 [BLOCKING] | Revision 4 creates exactly ten WP04 tables and preserves earlier revisions | Migration remains `000000000004` over `000000000003` | Migration test asserts `upgraded_tables - pre_tables == WP04_TABLES` and performs 3→4→3→4 | `research_module_evidence_link` remains absent; WP01-WP03 tables survive downgrade | PASS |
| R2-AC-07 [BLOCKING] | R1 behavior and project regression remain intact | R1 non-R2 files unchanged by hash | Full suite 85/85, Ruff, mypy, compileall, Alembic head | PostgreSQL denial in sandbox produces errors rather than false skips; identical escalated test has zero skips | PASS |

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| worktree `pwd`, status, branch, HEAD, and list | expected worktree/branch; HEAD unchanged; six accumulated files | Baseline and attribution |
| focused Evidence tests in sandbox | exit 1; `2 passed, 16 errors`; all 16 errors are local PostgreSQL socket permission denials; zero skips | Prove PostgreSQL absence is not hidden by skip |
| identical focused Evidence tests with local PostgreSQL access | exit 0; `18 passed, 2 warnings`; zero skips | L4 DB and repair regression |
| full pytest with local PostgreSQL access | exit 0; `85 passed, 4 warnings`; zero skips | Full regression |
| `ruff check backend/ apps/` | exit 0; all checks passed | Lint |
| `mypy --explicit-package-bases backend apps --ignore-missing-imports` | exit 0; 48 source files | Type check |
| `alembic -c migrations/alembic.ini heads` | exit 0; `000000000004 (head)` | Migration topology |
| targeted `compileall` | exit 0 | Syntax/import validation |
| `git diff --check` | exit 0 | Diff integrity |
| required existence checks | exit 0 | Canonical plural repository and tests |
| required forbidden-path `git diff --exit-code` | exit 1 solely on accumulated `backend/common/db/models_registry.py` | Contract-command defect; the file was already in baseline and its R1/R2 hash is identical |
| SHA-256 comparison with R1 report | registry and repositories hashes identical to R1 | Prove no R2 change in the two accumulated forbidden files |
| final status/branch/HEAD | six accumulated files; branch and HEAD unchanged | Final state |

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| Complete audit tuple makes any initial post-creation status legal | Yes | PENDING_REVIEW, REJECTED, DISPUTED, INVALIDATED, and RETRACTED cases are rejected | PASS |
| VERIFIED starts through review or dispute rather than trusted initial verification | Yes | VERIFIED/REVIEW_DECISION and VERIFIED/DISPUTE are rejected | PASS |
| VERIFIED/INITIAL_VERIFICATION bypasses null/partial audit requirements | Yes | null-audit and partial-audit cases raise `IntegrityError` | PASS |
| Initial check accidentally blocks identity-changing replacement v1 | Yes | predecessor-bearing UNREVIEWED/CORRECTION replacement succeeds | PASS |
| Current read falls back from INVALIDATED to older VERIFIED | Yes | repository returns the version-3 INVALIDATED row | PASS |
| Unique derivation edge is bypassed with a different row ID | Yes | duplicate non-self edge with different IDs raises `IntegrityError` | PASS |
| Revision 4 silently creates an extra table | Yes | exact set difference equals the ten-table `WP04_TABLES` set | PASS |

## DB Persistence Result

- Schema constraints: the new initial-state constraint, existing lifecycle/audit, predecessor, uniqueness, FK, provenance, and child-link constraints pass their focused database cases.
- Read semantics: current returns the highest version, including INVALIDATED/RETRACTED tombstones, with no status fallback.
- Replace semantics: replacement v1 requires an exact predecessor, a full audit tuple, and CORRECTION; R2 does not classify it as brand-new evidence.
- Active/inactive/deleted/status: no generic active filter exists; immutable current-version status semantics are preserved as contracted.
- Transaction boundary: command-layer multi-table mutation remains out of scope for WP04-01; test transactions and disposable migration databases isolate verification writes.
- Version/snapshot/history: version uniqueness, predecessor lineage, current, exact, history, tombstone, and initial-history boundaries are database enforced/tested.
- Real persistence vs InMemory/Fake/Mock: decisive behavior was verified against PostgreSQL and migrated constraints.

## Blocking Findings

None.

## Non-Blocking Findings

1. The R2 contract's forbidden-path diff command is inconsistent with its own declared dirty baseline because it includes the already-modified registry file. Future cumulative-worktree contracts should compare per-task before/after hashes or use a saved baseline diff, not plain `git diff HEAD` for files intentionally dirty before the repair.
2. The four dependency deprecation warnings are pre-existing and unrelated to R2: Starlette/httpx, AnyIO aliasing, and FastAPI's HTTP 422 constant naming.

## Regression Result

- Result: `PASS`
- Preserved behavior: R1 enums, source identity, repository path/surface, current/history reads, child loading, replacement and tombstone semantics, migration round trip, and all WP01-WP03/project tests
- Regression gaps: Evidence command services, concurrency/idempotency mutations, public API, and frontend remain future work and are not claimed by this persistence task

## Repair Required

- Repair Required: `NO`
- Repair ID: not applicable
- Failed AC/Gate: none

## Final Decision Rationale

`PASS`. Fresh static, contract, migration, real-PostgreSQL, and full-regression evidence proves the original R1 database hole is closed without breaking the accepted Evidence persistence boundary. The one exit-1 scope command is an internally inconsistent measurement against a known dirty baseline; exact prior/current hashes establish the intended no-R2-drift requirement without weakening it.

## Next Action

Close `TASK-WP04-01`. With explicit Git authorization, commit the six accumulated WP04-01 implementation files plus the accepted governance artifacts in an appropriate integration flow, then merge locally to `main`. Do not claim Evidence service/API or an Agent capability from this persistence PASS.
