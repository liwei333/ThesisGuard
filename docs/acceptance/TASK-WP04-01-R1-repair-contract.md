# TASK-WP04-01-R1 Repair Contract

## A. Execution Core

- Task ID: `TASK-WP04-01-R1`
- Objective: repair the WP04 Evidence persistence foundation so the SQLAlchemy model, Alembic migration, repository surface, and real PostgreSQL tests exactly implement the accepted Evidence domain contract.
- Why Now: independent verification found direct database contract violations despite a green six-test suite. WP04-02 must not build services on incorrect database truth.
- Task Type: `REPAIR / DATABASE_PERSISTENCE / REPOSITORY / TESTS`
- Task Size: `MEDIUM`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Evidence Matrix Type: `Full`

## Top Blocking AC

- TOP-AC-R1-01 [BLOCKING]: SQLAlchemy and Alembic use the exact accepted SourceType, actor, and SourceGrade sets and reject a SourceDocument with neither stable external ID nor fallback canonical URL.
- TOP-AC-R1-02 [BLOCKING]: the authorized `repositories.py` exposes every required source/version/series/evidence lookup and preserves highest-version current semantics without premature role-eligibility logic.
- TOP-AC-R1-03 [BLOCKING]: dedicated migration and persistence tests prove the exact closed enums, identity/deduplication, immutable lifecycle, link, idempotency, registry, current/history, and upgrade/downgrade behavior on real PostgreSQL.
- TOP-AC-R1-04 [BLOCKING]: changes remain inside the repair allowlist, all 73 existing tests remain green, and no Git history or WP04-02/API/frontend/worker scope is introduced.

## Execution Context

- Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-evidence-persistence`
- Branch: `codex/wp04-evidence-persistence`
- Expected HEAD: `a36c707898452340c35bdcfbceaf7d38bb3b4fa1`
- Preserve all accumulated WP04-01 changes. Do not create another worktree, switch branches, or clean/reset/stash the worktree.
- Read before editing:
  - `AGENTS.md`
  - `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`
  - `docs/acceptance/TASK-WP04-01-acceptance.md` from the main worktree
  - every current WP04-01 implementation/test file

## Scope

In Scope:

- Exact persistence enum/check values.
- SourceDocument identity completeness and partial unique behavior.
- Repository filename and required read helpers.
- Evidence query loading needed for immutable child snapshots.
- Dedicated PostgreSQL migration-cycle tests.
- Missing positive/negative persistence tests required by the original task.
- Directly necessary imports caused by renaming `repository.py` to `repositories.py`.

Out of Scope:

- WP04-02 domain services, command handlers, domain error mapping, API routes, OpenAPI/client generation, frontend/UI, worker tasks, MinIO byte writes, embeddings, RAG, Research typed-link migration, WP05 Thesis, dependencies, Docker topology, or new product decisions.
- Redesigning already accepted Evidence identities, versioning, lifecycle, provenance, locator, link, idempotency, or storage contracts.

Allowed Changes:

- `backend/evidence/models.py`
- `backend/evidence/repositories.py`
- `backend/evidence/repository.py` only to remove it after moving its retained behavior to the authorized plural path
- `backend/evidence/__init__.py` only if required for a stable repository import
- `backend/common/db/models_registry.py` only if directly required by corrected model registration
- `migrations/versions/20260914_004_evidence_persistence.py`
- `tests/test_evidence_migrations.py`
- `tests/test_evidence_persistence.py`

## Must

1. Preserve revision ID `000000000004` and `down_revision='000000000003'`. This task has not been committed or integrated, so repair the existing revision rather than adding `000000000005`.
2. Use this exact closed `SourceType` set in both model metadata and migration checks:
   - `COMPANY_ANNOUNCEMENT`
   - `FINANCIAL_REPORT`
   - `EXCHANGE_FILING`
   - `REGULATORY_DATA`
   - `OFFICIAL_DATA`
   - `POLICY_DOCUMENT`
   - `INVESTOR_RELATIONS`
   - `INSTITUTIONAL_SURVEY`
   - `BROKER_RESEARCH`
   - `INDUSTRY_REPORT`
   - `FINANCIAL_MEDIA`
   - `SOCIAL_MEDIA`
   - `RUMOR`
   - `WEB_PAGE`
   - `USER_NOTE`
3. Remove invented/stale values such as `EXCHANGE_ANNOUNCEMENT`, `COMPANY_REPORT`, `NEWS`, `REGULATORY_FILING`, `MANUAL_NOTE`, and `OTHER`.
4. Use exact SourceGrade values `S`, `A`, `B`, `C`, `D`, `E`, `F` in model and migration checks.
5. Allow `created_by_actor` values `SYSTEM`, `USER`, `LLM_PROPOSAL`, `IMPORTER`, `ADMIN_SCRIPT`. Where the accepted contract gives a narrower actor set for a specific field, define and enforce that narrower set rather than incorrectly reusing a broad tuple.
6. Add a named matching SQLAlchemy/Alembic constraint that requires at least one of `source_document.external_document_id` or `source_document.canonical_url` to be non-null.
7. Preserve the two partial source-identity unique paths exactly:
   - `(publisher_key, source_type, external_document_id)` when external ID is non-null;
   - `(publisher_key, source_type, canonical_url)` only when external ID is null and canonical URL is non-null.
8. Move repository code to `backend/evidence/repositories.py`, update all test/import references, and leave no `backend/evidence/repository.py` file.
9. Provide typed async helpers for at least:
   - SourceDocument by exact ID;
   - SourceDocument by `(publisher_key, source_type, external_document_id)`;
   - SourceDocument by fallback `(publisher_key, source_type, canonical_url)` with `external_document_id IS NULL`;
   - SourceDocumentVersion by exact ID;
   - SourceDocumentVersion by `(source_document_id, version_fingerprint)`;
   - latest SourceDocumentVersion by highest version;
   - EvidenceSeries by `series_identity_hash`;
   - exact EvidenceVersion;
   - current EvidenceVersion as the highest version with no status filter and no older-version fallback;
   - Evidence history in ascending version order;
   - EvidenceVersions for an exact SourceDocumentVersion.
10. Remove `get_current_valid_evidence` from WP04-01. Role-specific latest-first eligibility belongs to WP04-02 and the current implementation is contract-incomplete. Do not replace it with a service layer in this repair.
11. Ensure exact/current/history reads eagerly load the immutable child rows that callers of the persistence boundary need: source locators, instrument links, corroboration links in both directions, and derivation links in both directions, without mutating history.
12. Add `tests/test_evidence_migrations.py` with a disposable real-PostgreSQL `000000000003 -> 000000000004 -> 000000000003 -> 000000000004` test. It must prove:
   - WP01-WP03 tables survive downgrade;
   - exactly the ten WP04 tables appear at revision 4;
   - `research_module_evidence_link` remains absent;
   - the corrected named checks/indexes/PKs/FKs/uniques exist.
13. Expand real-PostgreSQL persistence tests to cover at least these positive/negative contracts:
   - every exact SourceType is accepted and representative removed/unknown values are rejected;
   - SourceGrade `E` is accepted where the database grade check applies and unknown grades are rejected;
   - `LLM_PROPOSAL` is accepted for `created_by_actor`, while unknown actors are rejected;
   - external-only identity succeeds, fallback-URL-only identity succeeds, both-null identity fails;
   - duplicate external identity fails regardless of URL changes; duplicate fallback URL fails when external ID is null; external-ID rows are not incorrectly deduplicated by URL;
   - duplicate source version number and duplicate `(source_document_id, version_fingerprint)` fail;
   - repository lookup by external identity, canonical fallback, fingerprint, latest source version, and series identity hash returns the exact expected row;
   - brand-new UNREVIEWED v1 may use the all-null lifecycle tuple;
   - replacement v1 requires predecessor, `CORRECTION`, and a complete non-null audit tuple;
   - v2 requires a complete audit tuple; partial audit tuples fail;
   - initial VERIFIED requires its complete allowed audit tuple;
   - ordinary VERIFIED correction without `trusted_correction_rule` fails;
   - INVALIDATED/RETRACTED tombstones require an exact predecessor and remain full immutable snapshots;
   - source-backed/manual/derived provenance constraints reject invalid combinations;
   - locator and instrument-link uniqueness, canonical corroboration ordering/reverse duplicate, and derivation self-link/duplicate rules hold;
   - idempotency uses the declared composite identity and rejects conflicting duplicates;
   - current returns the highest version even when it is ineligible/tombstoned and never falls back; history remains ascending;
   - an identity-dimension change is represented by a new EvidenceSeries/v1 pointing to the prior exact version, while the old series and versions remain unchanged.
14. Make PostgreSQL unavailability fail/error the required focused verification rather than yielding an apparently passing result through skipped Blocking tests. If local sandbox policy blocks the socket, rerun with the smallest approved permission escalation and report both attempts; do not convert an unavailable required database into task completion.
15. Keep SQLAlchemy metadata and Alembic DDL semantically aligned. Add an automated parity assertion for the repaired high-risk constraints/enums where practical.

## Must Not

- Do not weaken or delete already-correct lifecycle, replacement, tombstone, provenance, locator, link, uniqueness, FK, idempotency, or audit constraints to make tests pass.
- Do not add `research_module_evidence_link`.
- Do not add mutable current pointers or mutable history updates.
- Do not implement WP04-02 services or role-specific eligibility in this repair.
- Do not edit dependency manifests/lockfiles, frontend files, API files, worker files, Docker/Compose, Makefile, configuration, accepted contract documentation, or prior acceptance reports.
- Do not use SQLite as proof of PostgreSQL behavior.
- Do not make tests assert only that a constraint name exists; exercise both accepted and rejected rows.
- Do not commit, push, merge, rebase, stash, reset, clean, checkout, switch branches, delete worktrees, or create a PR.
- Do not self-approve. Final executor status is only `IMPLEMENTATION_COMPLETE` or `BLOCKED`; independent verification decides PASS/FAIL/BLOCKED.

## TDD Order

1. Add focused tests that fail against the current implementation for:
   - valid `COMPANY_ANNOUNCEMENT`;
   - valid `LLM_PROPOSAL`;
   - valid SourceGrade `E`;
   - both-null SourceDocument identity;
   - each missing repository helper/import path;
   - migration round trip and current/no-fallback behavior.
2. Record the RED command, exit code, and failure reason.
3. Apply the smallest model/migration/repository changes that make those tests pass.
4. Add the remaining original high-risk negative matrix and keep it green.
5. Run the complete required verification without modifying generated artifacts or unrelated files.

## Required Verification

```bash
pwd
git status --short --branch
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git worktree list --porcelain

test ! -e backend/evidence/repository.py
test -f backend/evidence/repositories.py
test -f tests/test_evidence_migrations.py
test -f tests/test_evidence_persistence.py

rg -n 'COMPANY_ANNOUNCEMENT|FINANCIAL_REPORT|EXCHANGE_FILING|REGULATORY_DATA|OFFICIAL_DATA|POLICY_DOCUMENT|INVESTOR_RELATIONS|INSTITUTIONAL_SURVEY|BROKER_RESEARCH|INDUSTRY_REPORT|FINANCIAL_MEDIA|SOCIAL_MEDIA|RUMOR|WEB_PAGE|USER_NOTE' \
  backend/evidence/models.py migrations/versions/20260914_004_evidence_persistence.py

rg -n 'EXCHANGE_ANNOUNCEMENT|COMPANY_REPORT|\bNEWS\b|REGULATORY_FILING|MANUAL_NOTE|\bOTHER\b' \
  backend/evidence migrations/versions/20260914_004_evidence_persistence.py \
  tests/test_evidence_migrations.py tests/test_evidence_persistence.py

rg -n 'LLM_PROPOSAL|"E"' \
  backend/evidence/models.py migrations/versions/20260914_004_evidence_persistence.py \
  tests/test_evidence_migrations.py tests/test_evidence_persistence.py

PYTHONDONTWRITEBYTECODE=1 pytest -q \
  tests/test_evidence_migrations.py \
  tests/test_evidence_persistence.py \
  -p no:cacheprovider -rs

PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider -rs

RUFF_CACHE_DIR=/tmp/thesisguard-wp04-r1-ruff ruff check backend/ apps/
MYPY_CACHE_DIR=/tmp/thesisguard-wp04-r1-mypy MYPYPATH=. \
  mypy --explicit-package-bases backend apps --ignore-missing-imports

alembic -c migrations/alembic.ini heads
PYTHONPYCACHEPREFIX=/tmp/thesisguard-wp04-r1-pycache \
  python -m compileall -q \
  backend/evidence backend/common/db/models_registry.py \
  migrations/versions/20260914_004_evidence_persistence.py \
  tests/test_evidence_migrations.py tests/test_evidence_persistence.py

git diff --check
git diff --exit-code -- \
  apps backend/instrument backend/research backend/watchlist \
  tests/test_research_api.py tests/test_research_persistence.py \
  apps/web/package.json apps/web/package-lock.json \
  Makefile docker-compose.yml pyproject.toml AGENTS.md README.md \
  docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md

git status --short --branch
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git worktree list --porcelain
```

Expected command semantics:

- The stale/invented enum search must return no matches (`rg` exit 1).
- Focused tests must execute all migration/persistence cases against PostgreSQL with zero skips and exit 0.
- Full pytest, Ruff, mypy, compileall, and `git diff --check` must exit 0.
- Alembic must report exactly `000000000004 (head)`.
- The forbidden-path diff must exit 0.
- HEAD remains `a36c707898452340c35bdcfbceaf7d38bb3b4fa1`; the worktree contains only the accumulated WP04-01/R1 allowlisted changes.

## High-Risk Counterexamples

- A contract-valid value must not be rejected because a test fixture invented a near-synonym.
- An unknown/stale SourceType must not enter PostgreSQL merely because it is uppercase text.
- An identity-less SourceDocument must not bypass both partial indexes through SQL null semantics.
- External-ID identity must take precedence over canonical URL; fallback URL identity applies only when external ID is absent.
- A source-version fingerprint lookup must not accidentally use `content_hash` as identity.
- Current Evidence must not skip a newest tombstone/ineligible row to return an older row.
- Replacement v1 must not use the brand-new-v1 all-null audit exception.
- A reverse-order corroboration duplicate must not bypass canonical pair uniqueness.
- Passing tests must not mean five Blocking database tests were skipped.

## Stop Conditions

Stop and report `BLOCKED` if:

- Worktree, branch, HEAD, or accumulated WP04-01 files differ from the stated baseline before editing.
- Another process changes an allowlisted implementation file during execution.
- Repair requires a new domain decision not fixed by the accepted WP04 contract.
- Migration repair would require changing already-integrated revisions `000000000001` through `000000000003`.
- Required PostgreSQL verification cannot run after the smallest appropriate permission/environment remedy.
- Passing requires weakening an accepted invariant or expanding into WP04-02/API/frontend/worker scope.

## Expected Evidence

- Exact worktree, branch, HEAD, `BASELINE_CHANGED_FILES`, and `FINAL_CHANGED_FILES`.
- TOP-AC-R1-01 through TOP-AC-R1-04 mapped to exact file lines and command results.
- RED then GREEN evidence for each direct verifier counterexample.
- Exact final enum sets from model and migration.
- Disposable PostgreSQL migration-cycle evidence, including preserved WP01-WP03 tables and zero DB-test skips.
- Repository helper inventory and executed query assertions.
- Full positive/negative persistence matrix with test names and counts.
- All Required Verification commands with exit codes, test counts, warnings, and final Git state.

## B. Governance Appendix

- Preserve immutable history, auditability, anti-drift, evidence-based acceptance, and separation of duties.
- This repair closes only failed WP04-01 persistence contracts. It does not authorize the next feature.
- Independent verification alone decides whether WP04-01 may close and WP04-02 may begin.
