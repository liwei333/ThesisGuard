# TASK-WP04-02-R1B Task Contract

## A. Execution Core

- Task ID: `TASK-WP04-02-R1B`
- Objective: repair Evidence provenance-derived identity, required derivation/cross-instrument lineage, identity-changing replacement routing, nullable correction semantics, immutable child preservation and automatic-extraction provenance without entering lifecycle or idempotency finalization work.
- Why Now: R1A is independently closed. R1B is the next ordered repair leaf and is required before lifecycle eligibility (R1C), idempotency/atomicity closure (R1D), and full WP04-02 re-verification.
- Task Type: `REPAIR`, `DOMAIN_SERVICE`, `DB_PERSISTENCE`, `VERSIONED_WRITE`
- Task Size: `MEDIUM`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Evidence Matrix Type: `Full`
- Source Acceptance: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-acceptance.md`
- Parent Repair Program: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1-repair-contract.md`
- R1A Closure: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1A-R2-acceptance.md`
- Frozen Contract: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`

## Top Blocking AC

- TOP-AC-01 [BLOCKING]: MANUAL, DERIVED and CROSS_INSTRUMENT identities are computed and validated by the service from canonical inputs; caller-supplied `origin_key` or CROSS_INSTRUMENT `scope_key` cannot select durable lineage.
- TOP-AC-02 [BLOCKING]: THESIS_INFERENCE/DERIVED creation requires at least one existing exact supporting EvidenceVersion, writes immutable derivation children atomically, and rejects missing support, invalid role, duplicate edge, self-reference and any detectable direct/indirect cycle with stable details and no residue.
- TOP-AC-03 [BLOCKING]: changing an EvidenceSeries identity dimension, including CROSS_INSTRUMENT member set or DERIVED supporting-ID set, routes to a replacement EvidenceSeries v1 with exact predecessor and CORRECTION audit; metadata-only child changes for the same canonical set may append N+1 in the same series.
- TOP-AC-04 [BLOCKING]: every N+1 correction/status/tombstone keeps a complete immutable snapshot and copies or intentionally replaces mandatory SourceLocator, EvidenceInstrumentLink and EvidenceDerivationLink children without mutating historical rows; nullable fields support an explicit clear distinct from “not supplied.”
- TOP-AC-05 [BLOCKING]: provenance and automatic-extraction validation fails closed before persistence, all required real-PostgreSQL counterexamples leave no partial series/version/link/idempotency/audit rows, and all R1A plus WP04-01/WP03 regressions remain green.

## Scope

In Scope:

- Service-derived MANUAL `origin_key`.
- Service-derived DERIVED `origin_key` from the sorted unique exact support-ID set.
- Service-derived CROSS_INSTRUMENT `scope_key` from the sorted unique instrument-ID set.
- Source-less MANUAL/DERIVED validation and source-backed/manual/derived mutual exclusion.
- THESIS_INFERENCE support presence, link validation, self/cycle defense and immutable derivation rows.
- CROSS_INSTRUMENT required immutable instrument membership rows.
- Same-series versus replacement-series routing when canonical identity inputs change.
- Immutable child copy/replacement for N+1 revisions and tombstones.
- Explicit nullable-clear semantics for revision fields.
- Extractor provenance validation for an LLM/parser-proposed source-backed EvidenceVersion.
- Focused PostgreSQL tests and required R1A/WP04-01/WP03 regression.

Allowed Changes:

- `backend/evidence/services.py`
- `backend/evidence/errors.py` only when an existing stable Evidence error needs additional structured detail; do not add a new error family without a verifier-approved contract replacement.
- `tests/test_evidence_services.py`

Out of Scope:

- R1C: lifecycle state table, current-valid eligibility and trusted correction registry.
- R1D: final aggregate-scoped idempotency hashes/replay ordering, UNKNOWN_OUTCOME reconciliation, replacement transaction redesign and concurrency reconciliation.
- Models, repositories, schema, migrations, registry, API/OpenAPI, Research typed links, frontend, worker, MinIO writes, parser/extractor implementation, embedding, pgvector/RAG, Thesis, Agent or Capability Runtime.
- Performance-only N+1 query cleanup and unrelated refactoring.

## Must

1. Work only in `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`, branch `codex/wp04-02-evidence-domain-service`, with unchanged Git HEAD `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`.
2. Before editing, record the current three candidate hashes and read the source acceptance, repair program, R1A closure and frozen contract sections 6-9, 13-17, 22-24 and 27. Governance files are read-only inputs from the main worktree.
3. Use TDD: first add focused failing PostgreSQL tests for each Top Blocking AC, record the expected red result, implement the smallest coherent repair, and rerun green.
4. Preserve R1A exactly. In particular, do not change the SourceType/SourceGrade matrix, SourceDocumentVersion fingerprint/re-observation rules or seven SourceLocator validators except where immutable child copying invokes them unchanged.
5. Compute canonical lineage before `series_identity_hash`:
   - SOURCE_BACKED: non-null `primary_source_document_id`, null `origin_key`, and exact source version/locator rules remain required.
   - MANUAL: null source document/version/grade/locator and service-derived `origin_key = manual:{created_by_actor}:{normalized manual subject}`. For this service slice, use the normalized nonblank `claim_key` as the canonical manual subject; trim surrounding whitespace without inventing a new persisted field. A conflicting caller `origin_key` must be rejected rather than trusted.
   - DERIVED: null source document/version/grade/locator and service-derived `origin_key = derived:{stable hash of sorted unique supporting EvidenceVersion IDs}`. A conflicting caller `origin_key` must be rejected rather than trusted.
   - CROSS_INSTRUMENT: compute `scope_key` from the sorted unique instrument IDs in immutable child inputs. Caller ordering, duplicates, role, link order and link metadata must not change this key; a conflicting caller key must be rejected rather than trusted.
6. Enforce InformationType/provenance combinations before mutation:
   - FACT remains SOURCE_BACKED only.
   - Source-backed external ESTIMATE keeps exact source version and locator requirements.
   - MANUAL ESTIMATE requires `created_by_actor='USER'`, nonblank `manual_entry_reason` and `manual_observed_at`.
   - USER_HYPOTHESIS requires MANUAL, `created_by_actor='USER'`, nonblank manual reason and observed time.
   - THESIS_INFERENCE requires DERIVED and a nonempty support set.
7. Validate every exact derivation support in the same transaction: support exists, role is in the frozen enum, `(supporting ID, role)` is not duplicated, self-reference is rejected, and a graph traversal prevents any detectable direct or indirect cycle before children are flushed. Errors use `EVIDENCE_INVALID_DERIVATION_LINK` with the relevant derived/supporting IDs when available.
8. Keep derivation and corroboration separate. Corroboration must not satisfy the required DERIVED support set and must not affect DERIVED `origin_key`.
9. Require CROSS_INSTRUMENT membership links and validate every instrument before persistence. Canonical identity uses only the distinct member-ID set; child role/order/metadata remains version metadata, not series identity.
10. Extend correction/revision input semantics only as needed for this leaf:
    - provide a private typed UNSET sentinel so omitted nullable fields retain the prior value while an explicit `None` clears a nullable field;
    - do not use `None` for both meanings;
    - non-nullable fields must reject explicit clear;
    - resulting rows must still satisfy PostgreSQL constraints.
11. Route identity changes rather than appending them inside the old series. At minimum, metric/period/provenance/source lineage, DERIVED support-ID set and CROSS_INSTRUMENT member-ID set changes create replacement v1 with `supersedes_evidence_version_id` and complete CORRECTION audit. Keep the old series/version/children immutable.
12. When the canonical DERIVED support-ID set or CROSS_INSTRUMENT member set is unchanged, role/order/weight/link-metadata or derived-expression changes may append N+1 in the same series and must create a fresh complete immutable child snapshot.
13. Every N+1 status/correction/tombstone copies the mandatory children for its provenance:
    - SOURCE_BACKED copies SourceLocator rows;
    - DERIVED copies EvidenceDerivationLink rows;
    - CROSS_INSTRUMENT copies EvidenceInstrumentLink rows;
    - unchanged historical children remain byte-for-byte and row-for-row intact.
14. Validate automatic extraction provenance without creating a parser implementation. `created_by_actor='LLM_PROPOSAL'` requires SOURCE_BACKED provenance, nonblank `extractor_name`, nonblank `extractor_version` and nonblank `prompt_template_version`. If any extractor field is supplied for another source-backed actor, name and version must be a complete nonblank pair. Do not infer that every IMPORTER action is automatic extraction.
15. Preserve caller-owned transaction semantics: service methods may flush but must not commit. Invalid inputs and failed link validation must leave no committable partial EvidenceSeries, EvidenceVersion, child-link, idempotency or audit rows.

## Must Not

- Do not modify the frozen contract, acceptance reports, repair program or task contract from the candidate worktree.
- Do not change WP04-01 models/repositories/migration/registry or add a fourth candidate file.
- Do not implement R1C lifecycle/current-valid/trusted-rule changes.
- Do not implement R1D idempotency scope/hash/replay/UNKNOWN_OUTCOME or replacement-atomicity finalization. If R1B correctness cannot be implemented without changing that boundary, stop and report `BLOCKED`.
- Do not weaken/delete/skip/xfail tests, modify test expectations to preserve known-wrong behavior, or use Mock/Fake/InMemory persistence as L4 evidence.
- Do not add TODO, placeholder, test-only production branches or arbitrary trusted strings.
- Do not commit, merge, rebase, push or mutate `main`.

## Required PostgreSQL Tests

Add meaningful public-service tests proving at least:

1. USER_HYPOTHESIS and user-authored MANUAL ESTIMATE derive the same deterministic manual origin from equivalent normalized claim keys; wrong caller origin is rejected with zero residue.
2. Source-less FACT, MANUAL without reason/time, MANUAL with source/locator, and DERIVED with source/locator are rejected before persistence.
3. THESIS_INFERENCE with zero supports is rejected; valid exact supports create DERIVED with null source fields and exact immutable derivation rows.
4. Derived support input ordering does not change origin; a changed distinct support-ID set changes origin and routes to replacement v1.
5. Invalid role, missing support, duplicate `(support ID, role)`, direct self-reference where representable, and an indirect cycle fixture are rejected with `EVIDENCE_INVALID_DERIVATION_LINK` and no residue.
6. CROSS_INSTRUMENT ordering and duplicate input IDs canonicalize to one member-set scope key; a changed member set routes to replacement v1; metadata-only child changes stay in the series.
7. Identity-changing replacement v1 has version 1, exact predecessor and complete CORRECTION audit; the old series, version and child rows are unchanged.
8. Same-support DERIVED child metadata changes append N+1 with new complete child rows; historical derivation rows remain unchanged.
9. Status/tombstone append for DERIVED and CROSS_INSTRUMENT preserves mandatory child rows on the new version without mutating the prior version.
10. Omitted nullable correction values retain old values, while explicit null clears each allowed nullable value/unit/currency/effective field; non-nullable clear is rejected.
11. `LLM_PROPOSAL` without complete extractor/prompt provenance is rejected; complete provenance persists exactly; partial extractor pairs are rejected.
12. Every failure above compares exact before/after counts for all relevant series, version, child-link, idempotency and audit tables.

## High-Risk Counterexamples

- Caller supplies a convenient MANUAL or DERIVED `origin_key` that does not match canonical inputs.
- CROSS_INSTRUMENT caller changes only input order or repeats an instrument to force a different `scope_key`.
- DERIVED THESIS_INFERENCE uses zero supports, a missing exact version, duplicate edges, itself, or an indirect descendant as support.
- Changed support/member set is appended as N+1 in the old series instead of routed to replacement v1.
- Same support/member set with metadata-only child changes is incorrectly routed to a new series.
- A DERIVED or CROSS_INSTRUMENT tombstone loses mandatory children and becomes an incomplete historical snapshot.
- Explicit `None` silently retains the prior nullable value rather than clearing it.
- An LLM proposal commits without extractor name/version/prompt provenance.

## Required Verification

Run from the isolated candidate worktree against real PostgreSQL:

```bash
git status --short --branch
git rev-parse HEAD

pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs

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
  --cache-dir=/tmp/tg-wp04-r1b-mypy \
  backend/evidence/errors.py \
  backend/evidence/services.py \
  tests/test_evidence_services.py

PYTHONPYCACHEPREFIX=/tmp/tg-wp04-r1b-pycache \
  python -m compileall -q \
  backend/evidence/errors.py \
  backend/evidence/services.py \
  tests/test_evidence_services.py

DATABASE_URL=postgresql+asyncpg://thesisguard:thesisguard_dev_password@127.0.0.1:15432/thesisguard \
  alembic -c migrations/alembic.ini heads

git diff --check
git status --short --branch
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

Real PostgreSQL tests must not skip. If sandbox networking blocks localhost, request authorization to run the tests outside the sandbox; do not replace them with SQLite or mocks.

The independent acceptance verifier is verifier-owned. If `/tmp/test_wp04_02_r1b_verifier.py` exists, the executor must run but never edit it. If it is absent, report that fact; absence does not authorize inventing or weakening acceptance evidence.

## Stop Conditions

Stop and report `BLOCKED` if:

- Correct behavior requires a model/repository/schema/migration change or a fourth candidate file.
- The frozen contract and existing command inputs cannot support a deterministic identity without inventing a new public contract.
- A correct cycle check cannot be exercised through the immutable exact-version graph without changing the frozen contract; report the precise graph/command contradiction instead of faking a cycle test.
- R1B routing cannot be separated safely from the explicitly deferred R1D transaction/idempotency redesign.
- Real PostgreSQL is unavailable outside the sandbox.
- Passing requires modifying a verifier, weakening a test, changing the frozen contract or entering R1C/R1D.

## Expected Evidence

- Before/after hashes and exact changed-file list.
- Red-to-green evidence mapped to all five Top Blocking AC.
- Exact derived manual origin, derived-support origin and cross-instrument scope-key examples.
- Exact old/new series IDs, version numbers, predecessor IDs and immutable child-row sets for same-series and replacement cases.
- Failure no-residue table counts and stable error details.
- Full service and 35-test regression results with pass/fail/skip counts.
- Ruff, format, mypy, compileall, Alembic and Git-scope results.
- Explicit statement that R1C/R1D, WP04-03 and all deferred modules remain untouched.

## B. Governance Appendix

- Executor may return only `IMPLEMENTATION_COMPLETE` or `BLOCKED`; it cannot self-approve.
- `IMPLEMENTATION_COMPLETE` means only that R1B is ready for independent verification.
- `No Evidence, No PASS`; the verifier will inspect implementation, add adversarial counterexamples and rerun all evidence.
- Any Blocking failure produces a narrower R1B Repair before R1C.
- R1B PASS proceeds to R1C but leaves the original WP04-02 acceptance as FAIL until R1D and full re-verification pass.

## Executor Final Response

Return:

1. Status: `IMPLEMENTATION_COMPLETE` or `BLOCKED`.
2. Worktree, branch, unchanged HEAD and baseline hashes.
3. Exact changed files and after hashes.
4. Top Blocking AC to implementation location to test mapping.
5. MANUAL/DERIVED/CROSS_INSTRUMENT canonical identity examples.
6. Same-series versus replacement-series evidence and immutable-child snapshots.
7. Nullable-clear and extractor-provenance evidence.
8. Real PostgreSQL results with pass/fail/skip counts.
9. Regression and static/type/build/Alembic results.
10. Final Git status and confirmation of no commit/merge/rebase/push/main mutation.
11. Remaining deferred R1C/R1D findings.

Do not use `PASS`, `DONE`, `VERIFIED`, `完成验收` or `已通过` as the executor verdict.
