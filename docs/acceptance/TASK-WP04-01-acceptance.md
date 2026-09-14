# TASK-WP04-01 Acceptance Report

**OVERALL: FAIL**

## Metadata

- Task ID: `TASK-WP04-01`
- Date: `2026-09-14` (`Asia/Shanghai`)
- Verifier: Codex (independent `ai-task-governor` verifier run)
- Report Path: `docs/acceptance/TASK-WP04-01-acceptance.md`
- Path Basis: the project uses `docs/acceptance/` for persisted task-governance artifacts
- Implementation Status: executor reported `IMPLEMENTATION_COMPLETE`; independent verification completed
- Implementation Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-evidence-persistence`
- Branch: `codex/wp04-evidence-persistence`
- HEAD / Baseline Commit: `a36c707898452340c35bdcfbceaf7d38bb3b4fa1`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`
- Missing Acceptance: `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Repair Required: `YES`
- Repair Task: `TASK-WP04-01-R1`

## Executive Decision

The implementation establishes a substantial Evidence persistence skeleton: all ten planned WP04 tables are registered, Alembic revision `000000000004` upgrades and downgrades on a disposable PostgreSQL database, the current automated suite passes, and lint/type checking is clean. Those results are independently reproduced and should be preserved.

The task cannot be accepted because the persisted schema does not match the frozen Evidence contract, the required repository surface is incomplete and placed at a disallowed path, and the tests do not exercise many Blocking database/query boundaries. Three direct PostgreSQL counterexamples prove that the green suite is a false positive for contract completion:

1. A contract-valid `COMPANY_ANNOUNCEMENT` SourceDocument is rejected by `ck_source_document_source_type`.
2. A contract-valid `created_by_actor='LLM_PROPOSAL'` SourceDocument is rejected by `ck_source_document_created_by_actor`.
3. A SourceDocument with both `external_document_id` and `canonical_url` null is accepted, although it has no stable source identity.

The migration and SQLAlchemy model also omit SourceGrade `E`, while the accepted contract freezes `S`, `A`, `B`, `C`, `D`, `E`, `F`. These are database truth errors, not naming preferences.

## Changed Files Snapshot

- `backend/common/db/models_registry.py`
- `backend/evidence/models.py`
- `backend/evidence/repository.py`
- `migrations/versions/20260914_004_evidence_persistence.py`
- `tests/test_evidence_persistence.py`
- Executor worktree status remained the five accumulated files above; no commit or history operation was observed.
- `apps/web/node_modules/` exists locally, is ignored, and is not Git-visible.
- The main worktree's pre-existing `docs/acceptance/TASK-WP04-00-INTEGRATION-acceptance.md` remained outside the implementation worktree and was not attributed to WP04-01.
- Attribution: `CERTAIN`.

Relevant SHA-256 snapshot:

- `backend/evidence/models.py`: `2d582d22bfc7d6d14e980253b884f22d3dfac70506e7bea2e03181afc1855fa2`
- `backend/evidence/repository.py`: `f1be69f38b6375d0e81b518e34fcd4995983c31cca5c388b48ec64d29fa2d3c0`
- `migrations/versions/20260914_004_evidence_persistence.py`: `42d6057a6bd4b4a2951783f431b8e33d364c9719697117ad035f245aecc07ea1`
- `backend/common/db/models_registry.py`: `56a6d416716f9ee1f3418a7942a41db0cf9a52d36f33d384c027623e9e54260c`
- `tests/test_evidence_persistence.py`: `cc0fbb780b74fe49cc10e104916b6b7a12260ed53acbfccd86447c792b3baed3`

## Classification

- Task Type: `DATABASE_PERSISTENCE / ALEMBIC / REPOSITORY / TESTS`
- Risk Type: authoritative schema drift, immutable-history constraints, source identity, latest-version semantics, migration reversibility
- Touched Layers: SQLAlchemy models, Alembic migration, model registry, async repository, PostgreSQL-backed tests
- Task Size: `MEDIUM`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, G5 Regression, G6 Evidence, DB Persistence Gate
- Not Applicable Gates: API, frontend behavior, worker/queue, MinIO byte I/O, RAG/embedding, external provider

## Top Blocking AC Results

| Top AC | Result | Independent evidence |
|---|---|---|
| TOP-AC-01 — models and migration implement the frozen Evidence schema | **FAIL** | SourceType, actor, and SourceGrade sets diverge from the accepted contract; SourceDocument lacks the required non-empty identity check. Real PostgreSQL probes reproduce the first three failures. |
| TOP-AC-02 — migration creates only the ten WP04 persistence tables and is reversible | PASS | Metadata contains exactly the ten intended Evidence/source tables and excludes `research_module_evidence_link`; disposable DB upgrade to `000000000004`, downgrade to `000000000003`, preservation of Instrument/Research tables, and re-upgrade all pass. |
| TOP-AC-03 — repository exposes the required identity/version/current/history reads | **FAIL** | The file is `repository.py` instead of the allowed `repositories.py`; external-ID, canonical-URL, source-fingerprint, and series-identity-hash lookups are absent. A premature `get_current_valid_evidence` implements an incomplete eligibility rule. |
| TOP-AC-04 — PostgreSQL tests prove positive and negative persistence contracts | **FAIL** | Only six tests exist, five are silently skipped when PostgreSQL is inaccessible, and the suite omits migration-cycle, exact-enum, identity, dedupe, current/no-fallback, idempotency, and several immutable-lifecycle counterexamples required by the task. |
| TOP-AC-05 — scope and regressions remain controlled | **FAIL** | Generic regression is green, but an unapproved singular repository path was added and the required migration-test file was omitted. G1 cannot close until file scope matches the task contract. |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Exact worktree, branch, HEAD, status, accepted domain contract, task report, and predecessor migration were inspected. |
| G1 Scope | **FAIL** | `backend/evidence/repository.py` is outside the exact allowed path; required `backend/evidence/repositories.py` and `tests/test_evidence_migrations.py` are absent. |
| G2 Contract | **FAIL** | Frozen enum values and source identity invariant are not represented by model/migration truth; required repository lookups are missing. |
| G3 Architecture | **FAIL** | Persistence queries cannot resolve the canonical external/fallback identities or EvidenceSeries identity key. The premature current-valid helper conflicts with the accepted eligibility contract and belongs to WP04-02. |
| G4 Test | **FAIL** | The existing six tests pass on accessible PostgreSQL, but do not detect the observed schema/query violations and silently skip five DB tests when the database is inaccessible. |
| G5 Regression | PASS | Independent full suite: `73 passed, 4 warnings`; Ruff and mypy pass; `git diff --check` passes. |
| G6 Evidence | **FAIL** | Executor evidence supports build health but not full contract closure; direct database counterexamples contradict `IMPLEMENTATION_COMPLETE`. |
| DB Persistence Gate | **FAIL** | Mechanical upgrade/downgrade passes, but authoritative enum/identity behavior fails and required high-risk DB counterexamples are absent. |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Independent Verification / Negative Evidence | Verdict |
|---|---|---|---|---|
| WP04-01-AC-01 [BLOCKING] | Exact ten-table Evidence persistence boundary | Ten SQLAlchemy models, migration tables, registry imports | `Base.metadata` lists exactly ten relevant tables; `research_module_evidence_link` is absent | PASS |
| WP04-01-AC-02 [BLOCKING] | Closed SourceType contract | Model lines 25-34 and migration lines 20-29 define eight different values | Contract lines 401-423 define fifteen values. PostgreSQL rejects valid `COMPANY_ANNOUNCEMENT`; the project test fixture uses invalid `EXCHANGE_ANNOUNCEMENT` and passes | **FAIL** |
| WP04-01-AC-03 [BLOCKING] | Actor and SourceGrade contracts | Shared `ACTORS` omits `LLM_PROPOSAL`; `SOURCE_GRADES` omits `E` in model and migration | Contract lines 137, 360-372, and 686-691 require both. PostgreSQL rejects `LLM_PROPOSAL` | **FAIL** |
| WP04-01-AC-04 [BLOCKING] | Every SourceDocument has external identity or canonical-URL fallback | Partial unique indexes exist, but no all-null rejection check exists | PostgreSQL accepted `probe-missing-identity` with both identity values null | **FAIL** |
| WP04-01-AC-05 [BLOCKING] | Source version and Evidence immutable/lifecycle constraints | Many named checks and uniqueness constraints are implemented | Existing tests prove selected replacement-v1, tombstone, provenance, locator, and self-link cases; many required inverse/partial/current/idempotency cases are untested | **FAIL** |
| WP04-01-AC-06 [BLOCKING] | Repository can resolve source and series identities | ID, latest-version, exact Evidence, current, history, and source-version listing helpers exist | Missing external identity, fallback URL identity, version fingerprint, and `series_identity_hash` helpers; file path differs from contract | **FAIL** |
| WP04-01-AC-07 [BLOCKING] | `current` means highest version without status fallback | `get_current_evidence` orders by version descending | Positive tombstone case confirms the highest version is returned; however `get_current_valid_evidence` incorrectly treats REJECTED, DISPUTED, UNREVIEWED, and other role-ineligible statuses as valid | **FAIL** |
| WP04-01-AC-08 [BLOCKING] | Migration upgrade/downgrade/re-upgrade preserves WP01-WP03 | Alembic `000000000004` has a reverse-order downgrade | Independent disposable DB cycle passed; after downgrade Instrument/Research remained while SourceDocument/EvidenceVersion were absent | PASS |
| WP04-01-AC-09 [BLOCKING] | Tests exercise real PostgreSQL and cannot pass through skips | Fixture creates a disposable DB and runs Alembic | Accessible run: 6 passed. Sandboxed run: 1 passed, 5 skipped, exit 0. Required migration and negative matrices are absent | **FAIL** |
| WP04-01-AC-10 [BLOCKING] | Existing project behavior remains green | No API/frontend/service change | Full suite 73 passed; Ruff and mypy clean; warnings are pre-existing deprecations | PASS |

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| worktree `pwd`, status, branch, HEAD, worktree list, recent Git history | Correct isolated worktree, branch, and unchanged HEAD; five implementation files visible | Baseline and attribution |
| `PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_evidence_persistence.py -p no:cacheprovider -rs` in sandbox | exit 0, but `1 passed, 5 skipped` due denied PostgreSQL access | Detect false-green skip behavior |
| Identical focused pytest with local PostgreSQL access | exit 0, `6 passed, 2 warnings` | Reproduce executor's positive suite |
| `PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider -rs` with local PostgreSQL access | exit 0, `73 passed, 4 warnings` | Full regression |
| Ruff over `backend/ apps/` | exit 0 | Static lint |
| mypy over `backend apps` | exit 0, 48 source files | Type check |
| `git diff --check` | exit 0 | Diff integrity |
| `alembic -c migrations/alembic.ini heads` | `000000000004 (head)` | Migration topology |
| Disposable DB upgrade to head | exit 0 | Migration apply |
| Disposable DB downgrade to `000000000003` | exit 0 | Migration reversibility |
| DB catalog query after downgrade | version `000000000003`; Instrument and Research tables present; SourceDocument/EvidenceVersion absent | Preservation of WP01-WP03 |
| Disposable DB re-upgrade to head | exit 0 | Round-trip migration |
| Valid `COMPANY_ANNOUNCEMENT` insert | exit 1, `ck_source_document_source_type` violation | Closed-enum counterexample |
| Valid `LLM_PROPOSAL` actor insert | exit 1, `ck_source_document_created_by_actor` violation | Actor counterexample |
| All-null source identity insert | exit 0 and returned inserted ID | Missing-identity counterexample |
| Metadata inventory | exactly ten WP04 source/evidence tables; Research link absent | Registry/table boundary |

The disposable database `tg_wp04_acceptance_probe_20260914` was dropped after verification. No project or user database was modified.

## Blocking Findings

### B-01 — Frozen SourceType, actor, and SourceGrade values are wrong in database truth

- Locations: `backend/evidence/models.py:25`, `backend/evidence/models.py:35`, `backend/evidence/models.py:36`, `migrations/versions/20260914_004_evidence_persistence.py:20`, `migrations/versions/20260914_004_evidence_persistence.py:30`, `migrations/versions/20260914_004_evidence_persistence.py:31`
- Contract: `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md:137`, `:401`, `:405`, `:686`
- Severity: Blocking
- Direct evidence: valid contract rows are rejected by PostgreSQL; SourceGrade `E` is not an allowed database value; several invented SourceType values are accepted and used by the tests.
- Required repair: use the exact accepted enums in both SQLAlchemy and Alembic, distinguish actor sets if a field has a narrower contract, and add positive/negative PostgreSQL tests for every closed-set boundary.

### B-02 — SourceDocument permits an identity-less authoritative row

- Locations: `backend/evidence/models.py:123-153`, `migrations/versions/20260914_004_evidence_persistence.py:117-151`
- Contract: SourceDocument identity at `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md:191-197` and the original WP04-01 acceptance contract
- Severity: Blocking
- Direct evidence: PostgreSQL accepted a row with both `external_document_id` and `canonical_url` null.
- Required repair: add matching named model/migration checks requiring at least one identity value and test external-only, URL-only, and neither-present cases together with both partial unique paths.

### B-03 — Repository contract is incomplete and one extra helper is semantically wrong

- Location: `backend/evidence/repository.py:1-126`
- Severity: Blocking
- Missing: external source identity lookup, fallback canonical-URL lookup, source-version fingerprint lookup, and EvidenceSeries identity-hash lookup.
- Scope issue: the task authorized `backend/evidence/repositories.py`, not `repository.py`.
- Semantic issue: `get_current_valid_evidence` excludes only INVALIDATED and RETRACTED, contrary to the accepted latest-first eligibility rules; WP04-02 owns role-specific eligibility.
- Required repair: move to the authorized plural path, implement the four missing reads, preserve highest-version `current`, and remove the premature current-valid helper from WP04-01.

### B-04 — The test suite does not prove the required persistence contract

- Location: `tests/test_evidence_persistence.py:38-81`, `:280-546`
- Severity: Blocking
- Direct evidence: current suite has six tests, silently skips five DB tests on connection errors, and uses the invalid source type `EXCHANGE_ANNOUNCEMENT` at line 118.
- Missing proof includes: migration round trip, exact closed enums, non-empty source identity, both partial unique identities, fingerprint and series-hash reads, idempotency composite identity, exact registry exclusion, current/no-fallback semantics, and the full requested immutable lifecycle/correction negative matrix.
- Required repair: add the dedicated migration test file and contract-driven PostgreSQL regression cases; the required focused command must fail or error when PostgreSQL is unavailable instead of reporting a passing task through skips.

## Non-Blocking Findings

- The ten-table structure, registry imports, Alembic dependency order, and selected lifecycle checks are useful work and should be preserved rather than rewritten wholesale.
- Existing Starlette/httpx/AnyIO/FastAPI deprecation warnings are unrelated to WP04-01.
- Installing ignored frontend dependencies did not alter package definitions or Git-visible scope.

## Regression Result

- Result: `PASS`
- Preserved behavior: all 73 current tests, existing WP01-WP03 APIs/persistence, lint, and mypy
- Important limitation: regression success does not establish the missing L3/L4 Evidence contract because the relevant counterexamples are absent from the suite.

## Repair Required

- Repair Required: `YES`
- Repair ID: `TASK-WP04-01-R1`
- Failed AC/Gates: WP04-01-AC-02 through AC-07 and AC-09; G1, G2, G3, G4, G6, DB Persistence Gate
- Repair policy: preserve the passing table boundary, migration topology, existing constraints, and green regressions; change only the failed schema/query/test surfaces.

## Final Decision Rationale

`FAIL`. This task defines PostgreSQL as the Evidence system of record. A system-of-record schema that rejects valid frozen values, accepts an identity-less source, and lacks required identity-resolution queries cannot receive L3 or L4 acceptance. Generic test and build success is necessary but not sufficient when direct PostgreSQL probes contradict the contract.

## Next Action

Execute `TASK-WP04-01-R1` in the same isolated worktree. Do not begin WP04-02, commit, merge, or push until the repair receives an independent PASS at `L1` through `L4`.
