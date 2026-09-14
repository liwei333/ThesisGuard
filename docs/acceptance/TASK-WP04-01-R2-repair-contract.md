# TASK-WP04-01-R2 Repair Contract

## A. Execution Core

- Task ID: `TASK-WP04-01-R2`
- Original Task: `TASK-WP04-01`
- Objective: close the remaining no-predecessor EvidenceVersion v1 state-machine hole and add the missing permanent PostgreSQL regression proof.
- Why Now: R1 fixed the enum, source identity, repository, migration, and skip failures, but independent PostgreSQL verification committed four initial v1 states that the accepted contract forbids.
- Task Type: `SMALL REPAIR / DB_PERSISTENCE / TESTS`
- Task Size: `SMALL`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Evidence Matrix Type: `Full` because immutable history and database state are involved

## Top Blocking AC

- TOP-AC-R2-01 [BLOCKING]: a no-predecessor EvidenceVersion v1 has exactly two legal forms: all-null-audit `UNREVIEWED`, or fully audited `VERIFIED` with `INITIAL_VERIFICATION`.
- TOP-AC-R2-02 [BLOCKING]: PostgreSQL rejects no-predecessor v1 PENDING_REVIEW, REJECTED, DISPUTED, INVALIDATED, RETRACTED, and VERIFIED with any non-initial transition kind.
- TOP-AC-R2-03 [BLOCKING]: model and migration remain semantically aligned, and permanent real-PostgreSQL tests prove both allowed forms, all prohibited forms, INVALIDATED tombstone behavior, and true derivation duplicate rejection.
- TOP-AC-R2-04 [BLOCKING]: all R1 PASS behavior and full regressions remain intact; no repository, API, service, frontend, worker, dependency, or Git-history scope is introduced.

## Execution Context

- Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-evidence-persistence`
- Branch: `codex/wp04-evidence-persistence`
- Expected HEAD: `a36c707898452340c35bdcfbceaf7d38bb3b4fa1`
- Preserve all accumulated WP04-01/R1 changes.
- Read before editing:
  - `AGENTS.md`
  - `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`, especially sections 12, 13, and 21
  - `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-01-R1-acceptance.md`
  - `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-01-R2-repair-contract.md`
  - current Evidence model, migration, and both Evidence test files

## Root Evidence

The current database accepts each row below with `version=1` and `supersedes_evidence_version_id=NULL`:

| Illegal status | Illegal kind | Observed result |
|---|---|---|
| `PENDING_REVIEW` | `REVIEW_REQUEST` | committed |
| `REJECTED` | `REVIEW_DECISION` | committed |
| `DISPUTED` | `DISPUTE` | committed |
| `VERIFIED` | `REVIEW_DECISION` | committed |

Relevant implementation:

- `backend/evidence/models.py:412-492`
- `migrations/versions/20260914_004_evidence_persistence.py:398-478`

The existing checks are primarily `kind -> allowed status`; they do not encode the inverse initial-state boundary.

## Scope

In Scope:

- One named initial-state check in SQLAlchemy and revision `000000000004`.
- Direct positive/negative PostgreSQL tests for the check.
- Tightening the existing migration test to prove the exact WP04 table delta.
- Adding the previously requested INVALIDATED tombstone and true derivation duplicate regression cases while the Evidence persistence tests are already in scope.

Out of Scope:

- New Evidence service/command logic, expected-version concurrency implementation, API/schema/frontend/worker/MinIO/RAG/Research links, any new domain decision, or broader migration redesign.
- Reworking enums, source identity, repository helpers, eager loading, table names, idempotency schema, provenance, or already-correct constraints.

Allowed Changes:

- `backend/evidence/models.py`
- `migrations/versions/20260914_004_evidence_persistence.py`
- `tests/test_evidence_migrations.py`
- `tests/test_evidence_persistence.py`

No other file may change.

## Must Fix

1. Keep revision `000000000004` and `down_revision='000000000003'`; do not create a new revision.
2. Add the same named CheckConstraint to model and migration. Its observable semantics must be:
   - if `version=1` and `supersedes_evidence_version_id IS NULL`, then exactly one of these is true:
     - `verification_status='UNREVIEWED'` and all four lifecycle audit fields are null;
     - `verification_status='VERIFIED'`, all four lifecycle audit fields are non-null, and `status_change_kind='INITIAL_VERIFICATION'`.
   - replacement v1 with a non-null predecessor remains governed by the existing CORRECTION constraints and is not classified as brand-new initial evidence.
   - versions greater than 1 remain governed by existing audit/status constraints; do not broaden or redesign their semantics in R2.
3. Prefer a precise name such as `ck_evidence_version_initial_state` and assert that the same name/expression semantics exist in SQLAlchemy metadata and migrated PostgreSQL.
4. Add RED-before-fix PostgreSQL tests that reproduce at least the four verifier rows: no-predecessor v1 PENDING_REVIEW, REJECTED, DISPUTED, and VERIFIED with REVIEW_DECISION.
5. Add positive PostgreSQL tests proving:
   - brand-new v1 UNREVIEWED with all-null audit tuple succeeds;
   - brand-new v1 VERIFIED with complete audit tuple and INITIAL_VERIFICATION succeeds;
   - replacement v1 with predecessor, complete audit tuple, CORRECTION, and ordinary UNREVIEWED status still succeeds.
6. Add negative PostgreSQL tests proving no-predecessor v1 rejects:
   - PENDING_REVIEW/REVIEW_REQUEST;
   - REJECTED/REVIEW_DECISION;
   - DISPUTED/DISPUTE;
   - INVALIDATED/INVALIDATION;
   - RETRACTED/RETRACTION;
   - VERIFIED/REVIEW_DECISION;
   - VERIFIED/DISPUTE;
   - VERIFIED with INITIAL_VERIFICATION but a partial/null audit tuple.
7. Add the missing INVALIDATED tombstone regression:
   - a complete N+1 INVALIDATED snapshot with exact predecessor, complete audit tuple, and INVALIDATION succeeds;
   - missing predecessor or partial tuple fails;
   - current returns the INVALIDATED N+1 and never falls back to the older VERIFIED version.
8. Add a true derivation duplicate test: two different link row IDs with the same non-self `(derived_evidence_version_id, supporting_evidence_version_id, role)` must violate `uq_evidence_derivation_link_identity`. Keep the existing self-link test.
9. Tighten the migration round-trip test to assert the revision-4 table delta equals the ten planned WP04 tables, not only that those tables are a subset. Continue proving `research_module_evidence_link` is absent and WP01-WP03 survive downgrade.
10. Keep required PostgreSQL tests zero-skip. Sandbox socket denial may error first, but the identical command must be rerun with the smallest approved access and execute all cases.

## Must Preserve

- Exact fifteen SourceTypes.
- SourceGrade `S` through `F`, including `E`.
- Broad created/lifecycle actor set and narrower source-status actor set.
- `ck_source_document_identity_present` and both partial source identity indexes.
- Plural `backend/evidence/repositories.py`; singular repository remains absent.
- All eleven repository helpers and no `get_current_valid_evidence`.
- Current highest-version, no-status-filter, no-fallback semantics.
- Child eager-loading in both corroboration and derivation directions.
- Ten-table WP04 boundary and absence of `research_module_evidence_link`.
- Existing replacement-v1, correction predecessor, trusted correction, tombstone, provenance, child-link, idempotency, uniqueness, FK, and audit constraints.
- Migration `000000000003 -> 000000000004 -> 000000000003 -> 000000000004` behavior.
- All 83 existing regression tests and zero-skip focused PostgreSQL behavior.

## Must Not

- Do not edit `backend/evidence/repositories.py`, model registry, `__init__.py`, any prior acceptance/contract document, dependency/configuration file, API, frontend, worker, Research, Instrument, Watchlist, or other migration.
- Do not weaken or delete existing checks to accommodate illegal rows.
- Do not implement service-layer state transition logic in this DB repair.
- Do not add mutable current pointers or update/delete history behavior.
- Do not use SQLite, mocks, skipped tests, or name-only assertions as L4 proof.
- Do not commit, push, merge, rebase, stash, reset, clean, checkout, switch branches, create/delete a worktree, or create a PR.
- Do not self-approve. Executor status is only `IMPLEMENTATION_COMPLETE` or `BLOCKED`.

## TDD Order

1. Add the direct initial-state PostgreSQL regression test first.
2. Run the focused test and record RED showing at least the four illegal rows are currently accepted.
3. Add the smallest model/migration-aligned constraint.
4. Re-run the same focused test and record GREEN.
5. Add/confirm valid initial forms, replacement v1 preservation, INVALIDATED tombstone, true derivation duplicate, and exact migration delta tests.
6. Run the complete focused and full verification.

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

rg -n 'ck_evidence_version_initial_state|INITIAL_VERIFICATION|PENDING_REVIEW|REVIEW_DECISION|DISPUTED|INVALIDATED|RETRACTED' \
  backend/evidence/models.py \
  migrations/versions/20260914_004_evidence_persistence.py \
  tests/test_evidence_migrations.py \
  tests/test_evidence_persistence.py

PYTHONDONTWRITEBYTECODE=1 pytest -q \
  tests/test_evidence_migrations.py \
  tests/test_evidence_persistence.py \
  -p no:cacheprovider -rs

PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider -rs

RUFF_CACHE_DIR=/tmp/thesisguard-wp04-r2-ruff ruff check backend/ apps/
MYPY_CACHE_DIR=/tmp/thesisguard-wp04-r2-mypy MYPYPATH=. \
  mypy --explicit-package-bases backend apps --ignore-missing-imports

alembic -c migrations/alembic.ini heads
PYTHONPYCACHEPREFIX=/tmp/thesisguard-wp04-r2-pycache \
  python -m compileall -q \
  backend/evidence/models.py \
  migrations/versions/20260914_004_evidence_persistence.py \
  tests/test_evidence_migrations.py \
  tests/test_evidence_persistence.py

git diff --check
git diff --exit-code -- \
  backend/evidence/repositories.py \
  backend/common/db/models_registry.py \
  backend/evidence/__init__.py \
  backend/instrument backend/research backend/watchlist apps \
  apps/web/package.json apps/web/package-lock.json \
  Makefile docker-compose.yml pyproject.toml AGENTS.md README.md \
  docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md

git status --short --branch
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git worktree list --porcelain
```

Expected semantics:

- Focused PostgreSQL tests execute all cases, zero skips, exit 0.
- Full pytest exits 0 with at least the existing 83 tests plus the new R2 regression coverage.
- Ruff, mypy, compileall, and `git diff --check` exit 0.
- Alembic reports exactly `000000000004 (head)`.
- Forbidden-path diff exits 0.
- Final HEAD remains `a36c707898452340c35bdcfbceaf7d38bb3b4fa1`.
- Final Git-visible files remain the accumulated six WP04-01 files; R2 modifies only the four-file allowlist.

## High-Risk Counterexamples

- A complete audit tuple alone must not make a no-predecessor post-creation state legal.
- Kind-to-status checks must not be mistaken for a bidirectional state machine.
- Initial trusted VERIFIED must not masquerade as REVIEW_DECISION or DISPUTE.
- Replacement v1 must not be blocked by the new brand-new-initial constraint.
- INVALIDATED current must not fall back to an older VERIFIED row.
- A derivation duplicate must not bypass uniqueness merely by using a different row ID.

## Stop Conditions

Stop and report `BLOCKED` if:

- Worktree, branch, HEAD, or accumulated file set differs from the stated baseline.
- Another process changes an R2 allowlisted file during execution.
- Fixing the hole requires a new domain decision rather than the already accepted two-form initial contract.
- The constraint cannot be represented consistently in model and migration without editing prior revisions.
- Required real PostgreSQL verification remains unavailable after the smallest appropriate access remedy.
- Passing requires weakening an already passing R1 constraint or changing a forbidden file.

## Expected Evidence

- Exact worktree, branch, HEAD, `BASELINE_CHANGED_FILES`, and `FINAL_CHANGED_FILES`.
- TOP-AC-R2-01 through TOP-AC-R2-04 mapped to exact final lines and command evidence.
- RED output proving the four verifier rows were accepted before the fix.
- GREEN output proving all allowed/forbidden no-predecessor v1 forms after the fix.
- Model/migration constraint parity evidence.
- INVALIDATED no-fallback, derivation duplicate, and exact migration table-delta evidence.
- Focused/full test counts, zero skips, warnings, Ruff, mypy, compileall, Alembic, diff, and final Git state.
- Explicit statement that no commit, push, merge, rebase, stash, reset, clean, checkout, branch/worktree, or PR operation occurred.

## B. Governance Appendix

- `IMPLEMENTED != PASS`; executor cannot self-approve.
- No Evidence, No PASS.
- R2 must preserve every R1 PASS AC and existing regression path.
- R2 closes only the remaining persistence-state hole and directly missing regression proof. It does not authorize WP04-02.
- Independent verification alone decides whether WP04-01 may close.

