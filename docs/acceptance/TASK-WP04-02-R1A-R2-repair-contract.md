# TASK-WP04-02-R1A-R2 Repair Contract

## A. Execution Core

- Task ID: `TASK-WP04-02-R1A-R2`
- Objective: Repair only two remaining SourceLocator fail-closed boundary cases: whitespace-only WEB_ANCHOR canonical URLs and TABLE_CELL payloads that combine cell_ref with an incomplete numeric coordinate pair.
- Why Now: Both cases are explicitly implied by the R1A-R1 contract, fail in the expanded real-PostgreSQL verifier, and block R1A closure/R1B dispatch.
- Task Type: `REPAIR`, `DOMAIN_SERVICE`, `DB_PERSISTENCE`
- Task Size: `SMALL`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Evidence Matrix Type: `Full`
- Source Acceptance: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1A-R1-acceptance.md`
- Parent Repair Contract: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1A-R1-repair-contract.md`
- Frozen Contract: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md` §15

## Top Blocking AC

- TOP-AC-01 [BLOCKING]: WEB_ANCHOR `canonical_url` must contain at least one non-whitespace character; empty, whitespace-only and non-string values return `EVIDENCE_INVALID_SOURCE_LOCATOR` at `locator_payload.canonical_url` with no residue.
- TOP-AC-02 [BLOCKING]: TABLE_CELL numeric coordinates are optional only as a complete pair; if either `row_index` or `column_index` is supplied, both must be present and valid even when `cell_ref` is also present.
- TOP-AC-03 [BLOCKING]: Every new invalid public command leaves EvidenceSeries, EvidenceVersion, EvidenceSourceLocator, EvidenceIdempotencyRecord and EvidenceAuditEvent counts unchanged.
- TOP-AC-04 [BLOCKING]: All ten previously passing independent verifier cases and every prior R1A/R1A-R1 behavior remain green.

## Scope

In Scope:

- The two exact validation branches above.
- Focused public-path real-PostgreSQL regression tests for both branches and symmetric coordinate cases.

Allowed Changes:

- `backend/evidence/services.py`
- `tests/test_evidence_services.py`

Out of Scope:

- `backend/evidence/errors.py` unless the executor stops and requests a replacement contract; no error type change is currently needed.
- All other SourceLocator redesign, source/version behavior, R1B/R1C/R1D, models/repositories/schema/migrations/API/docs/Research/frontend/runtime work.

## Must

1. Continue only in `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`, branch `codex/wp04-02-evidence-domain-service`, unchanged HEAD `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`.
2. Read the source acceptance, parent Repair Contract and frozen §15 before editing; do not modify them from the candidate.
3. Use TDD: add the new failures first, record red, implement the smallest change, rerun green.
4. Validate WEB_ANCHOR canonical_url with nonempty-string semantics equivalent to `isinstance(value, str) and value.strip()`; do not transform, fetch or rewrite the URL in this Repair.
5. For TABLE_CELL, determine numeric-pair presence independently of cell_ref. If exactly one of `row_index` and `column_index` is supplied, reject the missing counterpart with the precise path. If neither is supplied, a valid cell_ref is sufficient. If both are supplied, validate both and all available bounds whether or not cell_ref is also present.
6. Preserve exact `source_document_version_id` and `locator_path` details and validate before mutation.
7. Prove no-residue behavior using exact before/after counts for all five mutable Evidence tables in the Repair Contract.

## Must Not

- Do not modify `backend/evidence/errors.py`, models, repositories, schema, migration, registry, API/OpenAPI, Research, frontend or runtime code.
- Do not change other locator semantics or refactor unrelated helpers.
- Do not change matrix, fingerprint, dedup/re-observation, source lifecycle, concurrency or R1B/R1C/R1D behavior.
- Do not modify `/tmp/test_wp04_02_r1a_verifier.py`.
- Do not weaken/delete/skip/xfail tests or change the contract to fit implementation.
- Do not add a fourth candidate file.
- Do not commit, merge, rebase, push or mutate `main`.

## Required PostgreSQL Tests

Add and run tests proving:

1. WEB_ANCHOR canonical_url `''`, `'   '` and non-string values fail at `locator_payload.canonical_url` with no residue.
2. A normal non-whitespace canonical URL still succeeds without selector fields.
3. TABLE_CELL cell_ref-only remains valid.
4. TABLE_CELL complete numeric row/column remains valid.
5. TABLE_CELL cell_ref + row-only fails at `locator_payload.column_index` with no residue.
6. TABLE_CELL cell_ref + column-only fails at `locator_payload.row_index` with no residue.
7. TABLE_CELL cell_ref + complete numeric pair succeeds when all values and bounds are valid.
8. TABLE_CELL cell_ref + complete but out-of-bounds pair fails at the exact offending coordinate and leaves no residue.

## High-Risk Counterexamples

- `{'canonical_url': '   '}` must fail; truthiness alone is insufficient.
- `{'page_number': 12, 'table_index': 1, 'cell_ref': 'B2', 'row_index': 2}` must fail for missing column.
- The symmetric cell_ref + column-only form must fail for missing row.
- A valid cell_ref-only payload must remain green.

## Required Verification

Run from the candidate worktree with real PostgreSQL:

```bash
git status --short --branch
git rev-parse HEAD

pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs

PYTHONPATH=/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service \
  pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs

pytest -p no:cacheprovider -q \
  tests/test_evidence_persistence.py \
  tests/test_migrations.py \
  tests/test_evidence_migrations.py \
  tests/test_research_api.py \
  tests/test_research_persistence.py -rs

ruff check --no-cache \
  backend/evidence/errors.py \
  backend/evidence/services.py \
  tests/test_evidence_services.py

ruff format --check --no-cache \
  backend/evidence/errors.py \
  backend/evidence/services.py \
  tests/test_evidence_services.py

MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports \
  --cache-dir=/tmp/tg-wp04-r1a-r2-mypy \
  backend/evidence/errors.py \
  backend/evidence/services.py \
  tests/test_evidence_services.py

PYTHONPYCACHEPREFIX=/tmp/tg-wp04-r1a-r2-pycache \
  python -m compileall -q \
  backend/evidence/errors.py \
  backend/evidence/services.py \
  tests/test_evidence_services.py

alembic -c migrations/alembic.ini heads
git diff --check
git status --short
git diff --stat
git diff --name-status
```

The independent verifier now contains 12 tests. It is a verifier-owned temporary artifact and must not be edited by the executor. Current expected pre-repair result is `2 failed, 10 passed`; post-repair all 12 must pass.

## Stop Conditions

Stop and report `BLOCKED` if:

- Either fix requires a model/repository/schema/migration/error-contract change.
- Correctness requires changing another SourceLocator rule or entering R1B/R1C/R1D.
- Real PostgreSQL cannot be reached outside the sandbox.
- Passing requires editing the verifier, weakening tests or changing this contract.

## Expected Evidence

- Before/after hashes and exact changed-file list.
- Red-to-green evidence for whitespace URL and both asymmetric partial-coordinate forms.
- All 12 independent verifier results.
- Five-table no-residue counts for invalid commands.
- Full service suite and 35-test regression results.
- Ruff, format, mypy, compile, Alembic and Git hygiene results.
- Explicit preservation of all prior R1A/R1A-R1 PASS evidence.

## B. Governance Appendix

- Executor may return only `IMPLEMENTATION_COMPLETE` or `BLOCKED`; it cannot self-approve.
- `No Evidence, No PASS`; verifier reruns all evidence.
- Any Blocking AC failure keeps R1A open and blocks R1B.
- R1A-R2 PASS will close the R1A repair chain, not the original WP04-02; R1B/R1C/R1D and final re-verification remain required.

## Executor Final Response

Return:

1. Status, worktree, branch and unchanged HEAD.
2. Before/after hashes and exact changed-file list.
3. Two implementation locations and focused red-to-green evidence.
4. All 12 verifier results and invalid-case table counts.
5. Full service suite and 35-test regression results.
6. Ruff/format/mypy/compile/Alembic results.
7. Scope/deferred-work confirmation.
8. Final Git status and confirmation of no commit/merge/rebase/push/main mutation.
