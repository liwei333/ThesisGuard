# TASK-WP04-02-R1A-R1 Repair Contract

## A. Execution Core

- Repair ID: `TASK-WP04-02-R1A-R1`
- Original Task: `TASK-WP04-02-R1A`
- Objective: Close only the remaining SourceLocator contract gaps for WEB_ANCHOR optional fields, TABLE optional coordinate validation, TABLE_CELL cell-ref representation, and exact locator error details while preserving every R1A behavior already independently verified.
- Why Now: R1A cannot pass and R1B cannot start while a Top Blocking locator AC rejects legal inputs and accepts parser-bounded invalid coordinates.
- Task Type: `REPAIR`, `DOMAIN_SERVICE`, `DB_PERSISTENCE`
- Task Size: `SMALL`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Evidence Matrix Type: `Full`
- Source Acceptance: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1A-acceptance.md`
- Original R1A Contract: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1A-task-contract.md`
- Frozen Contract: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md` §15

## Root Evidence

- Independent verifier: `PYTHONPATH=<candidate> pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs`
- Result: `5 failed, 5 passed in 5.83s`.
- Root locations:
  - `backend/evidence/services.py:1715-1720`: optional WEB_ANCHOR selectors are incorrectly mandatory.
  - `backend/evidence/services.py:1666-1675`: TABLE ignores supplied row/column/cell coordinates and bounds.
  - `backend/evidence/services.py:1683-1687`: TABLE_CELL always requires numeric row and column, rejecting cell_ref-only representation.
  - `backend/evidence/services.py:1600-1603`: missing locator error lacks required details.
  - `backend/evidence/services.py:1625-1629`: missing short citation reports the wrong input path.

## Top Blocking AC

- TOP-AC-01 [BLOCKING]: `WEB_ANCHOR` accepts a nonempty `canonical_url` when all optional selector fields are absent; optional fields, when supplied, receive deterministic structural validation.
- TOP-AC-02 [BLOCKING]: `TABLE` requires valid page/table coordinates and validates any supplied row/column/cell fields against structure and available parser bounds.
- TOP-AC-03 [BLOCKING]: `TABLE_CELL` accepts either a valid nonempty `cell_ref` or a complete valid numeric row/column coordinate representation and enforces available parser bounds.
- TOP-AC-04 [BLOCKING]: Every `EVIDENCE_INVALID_SOURCE_LOCATOR` contains `source_document_version_id` and an exact command-input `locator_path`; invalid input leaves no Evidence/idempotency/audit residue.
- TOP-AC-05 [BLOCKING]: The repair preserves every previously passed R1A matrix, fingerprint, re-observation, same-byte revision, lifecycle, concurrency, static and regression result.

## Scope

In Scope:

- SourceLocator validation helpers and the call site for missing locator input.
- Focused real-PostgreSQL tests for the five root counterexamples.
- Error detail construction only where required for exact locator paths.

Allowed Changes:

- `backend/evidence/services.py`
- `backend/evidence/errors.py` only if detail typing cannot be satisfied otherwise
- `tests/test_evidence_services.py`

Out of Scope:

- Source matrix, source fingerprint, source dedup/re-observation, source lifecycle and concurrency redesign except regression preservation.
- Every R1B/R1C/R1D item.
- Models, repositories, registry, schema, migrations, API/OpenAPI, Research, frontend, worker, MinIO/parser implementation, embedding/RAG, Thesis, Agent and Capability Runtime.

## Must

1. Continue only in `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service` on branch `codex/wp04-02-evidence-domain-service` at unchanged HEAD `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`.
2. Read the source acceptance, original R1A contract and frozen §15 from the absolute paths above before editing; treat them as read-only.
3. Use TDD: add the five missing contract tests, show the expected red results, then repair and rerun green.
4. For `WEB_ANCHOR`, require a nonempty string `canonical_url`. Treat `anchor`, `css_selector` and `text_quote_hash` as optional. A payload containing only canonical_url is valid. Validate supplied optional fields as nonempty strings without inventing external fetch validation.
5. For `TABLE`, require positive integer `page_number` and `table_index`. When `row_index` or `column_index` is supplied, validate its type/range and compare it to available parser table-shape metadata. When `cell_ref` is supplied, validate it as a nonempty string. Do not require optional fields for a table-level locator.
6. For `TABLE_CELL`, require positive page/table coordinates plus either a nonempty `cell_ref` or both positive integer `row_index` and `column_index`. Apply available page/table/row/column bounds. Do not reject a valid cell_ref-only representation merely because numeric row/column fields are absent.
7. When SOURCE_BACKED Evidence has no locator, raise `EVIDENCE_INVALID_SOURCE_LOCATOR` with `source_document_version_id` and exact `locator_path='locators'` before mutation.
8. Validate `raw_locator` and `short_citation` separately so the error path identifies the actual missing field.
9. For every invalid locator test, prove EvidenceSeries, EvidenceVersion, EvidenceSourceLocator, EvidenceIdempotencyRecord and EvidenceAuditEvent counts do not change.
10. Preserve caller-owned outer transactions and service `flush`-without-`commit` behavior.

## Must Not

- Do not change AC, Required Verification, Evidence Required, the frozen contract or this Repair Contract.
- Do not weaken, delete, skip or xfail tests.
- Do not broaden into another locator schema beyond fields frozen in §15.
- Do not refactor R1B/R1C/R1D code while touching `services.py`.
- Do not add a fourth candidate file.
- Do not modify main-worktree governance files from the candidate.
- Do not commit, merge, rebase, push or mutate `main`.

## Required PostgreSQL Tests

Add explicit tests proving:

1. WEB_ANCHOR `{canonical_url: ...}` succeeds with no anchor/css/text hash.
2. WEB_ANCHOR optional selector fields, when present, must be structurally valid.
3. TABLE with no optional cell coordinate remains valid.
4. TABLE with supplied valid row/column values succeeds.
5. TABLE with supplied row or column beyond parser table shape fails with the precise path and no residue.
6. TABLE_CELL with a valid `cell_ref` and no numeric row/column succeeds.
7. TABLE_CELL with complete valid numeric row/column succeeds.
8. Partial or invalid TABLE_CELL representations fail with the precise path and no residue.
9. Missing locators include the source version ID and `locator_path='locators'`.
10. Missing `raw_locator` reports `raw_locator`; missing `short_citation` reports `short_citation`.

## Required Verification

Run from the isolated candidate worktree using real PostgreSQL:

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
  --cache-dir=/tmp/tg-wp04-r1a-r1-mypy \
  backend/evidence/errors.py \
  backend/evidence/services.py \
  tests/test_evidence_services.py

PYTHONPYCACHEPREFIX=/tmp/tg-wp04-r1a-r1-pycache \
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

The executor must not modify `/tmp/test_wp04_02_r1a_verifier.py`. If it is genuinely absent, add equivalent public-path contract tests to `tests/test_evidence_services.py`, report the absence, and leave independent reproduction to the verifier; absence does not authorize weakening the five counterexamples.

## High-Risk Counterexamples

- canonical_url-only WEB_ANCHOR must succeed.
- TABLE row 99 with parser row_count 5 must fail before any Evidence/idempotency/audit write.
- TABLE_CELL `{page_number: 12, table_index: 1, cell_ref: 'B2'}` must succeed.
- Missing locator list must include source-version ID and exact path in the stable error.
- Empty short citation must report `short_citation`, not `raw_locator`.

## Stop Conditions

Stop and report `BLOCKED` if:

- Correct behavior requires a model, schema, migration, repository or fourth candidate-file change.
- Frozen §15 cannot distinguish TABLE from TABLE_CELL without a contract decision not already stated above.
- Real PostgreSQL remains unavailable outside the sandbox.
- Passing requires changing the contract, weakening tests or entering R1B/R1C/R1D.

## Expected Evidence

- Before/after hashes and exact changed-file list.
- Five targeted red-to-green counterexamples.
- Exact before/after row counts for invalid public command cases.
- Full candidate service-suite and 35-test regression outputs.
- Matrix, fingerprint, re-observation, same-byte revision, lifecycle and concurrency preservation mapping.
- Ruff, format, mypy, compile, Alembic and Git hygiene results.
- Required Acceptance achieved/missing.

## B. Governance Appendix

- `IMPLEMENTED != PASS`; executor may report only `IMPLEMENTATION_COMPLETE` or `BLOCKED`.
- No Evidence, No PASS; verifier reruns all commands independently.
- Any Blocking AC failure keeps R1A in FAIL and blocks R1B.
- Passing this repair only closes R1A; original `TASK-WP04-02` remains FAIL until R1B/R1C/R1D and full re-verification pass.

## Executor Final Response

Return:

1. Status: `IMPLEMENTATION_COMPLETE` or `BLOCKED`.
2. Baseline/branch/worktree and unchanged HEAD.
3. Changed files and before/after hashes.
4. Exact locator implementation locations.
5. Five red-to-green results and DB row-count evidence.
6. Full service and regression test counts.
7. Ruff/format/mypy/compile/Alembic results.
8. Scope and deferred R1B/R1C/R1D confirmation.
9. Final Git status and confirmation of no commit/merge/rebase/push/main mutation.
