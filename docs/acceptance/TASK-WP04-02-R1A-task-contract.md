# TASK-WP04-02-R1A Task Contract

## A. Execution Core

- Task ID: `TASK-WP04-02-R1A`
- Objective: Repair the frozen SourceType/SourceGrade policy, SourceDocumentVersion fingerprint/dedup/re-observation semantics, SourceLocator validation, and their executable PostgreSQL tests without touching later Evidence lifecycle/provenance/idempotency-replacement leaves.
- Why Now: These rules are the source/provenance foundation for every later Evidence mutation. The current candidate accepts forbidden grades, rejects legal same-byte source revisions, and rejects contract-valid locator payloads.
- Task Type: `REPAIR`, `DOMAIN_SERVICE`, `DB_PERSISTENCE`
- Task Size: `MEDIUM`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Evidence Matrix Type: `Full`
- Source Acceptance: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-acceptance.md`
- Parent Repair Program: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1-repair-contract.md`
- Frozen Contract: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`

## Top Blocking AC

- TOP-AC-01 [BLOCKING]: `SOURCE_TYPE_ALLOWED_GRADES` must equal the exact 15-entry closed matrix in frozen contract §11; every allowed and forbidden pair must have parameterized evidence.
- TOP-AC-02 [BLOCKING]: SourceDocumentVersion fingerprint must use exactly the §8 fields, remain unaffected by observation/fetch time and storage object-key changes, and change for grade/metadata/status/language/parser/content changes as specified.
- TOP-AC-03 [BLOCKING]: Identical fingerprints must return/reconcile to the existing source version with idempotency/audit evidence, while same bytes with a changed grade, versioned metadata or lifecycle notice must append a new version and may reuse the object key.
- TOP-AC-04 [BLOCKING]: Every locator type must validate the frozen §15 field names and available parser bounds; valid payloads commit, invalid payloads return `EVIDENCE_INVALID_SOURCE_LOCATOR`, and failures leave no series/version/idempotency/audit residue.
- TOP-AC-05 [BLOCKING]: R1A must pass focused real-PostgreSQL tests, Ruff, format, mypy and compile checks while preserving the already-green WP04-01 tests and the untouched R1B/R1C/R1D candidate behavior.

## Scope

In Scope:

- Exact SourceType/SourceGrade matrix.
- Canonical source-version fingerprint helper separated from command request hashing.
- Source command aggregate-specific idempotency scope only where needed for register/append/re-observation.
- Identical-fingerprint re-observation behavior and audit/idempotency handling.
- Removal of the incorrect content-hash duplicate rejection.
- Source lifecycle field validation needed to compute the correct fingerprint.
- Locator validators for `PAGE`, `PAGE_PARAGRAPH`, `SECTION`, `TABLE`, `TABLE_CELL`, `WEB_ANCHOR`, and `TIME_RANGE`.
- Correcting candidate tests and fixtures that currently encode forbidden grade or locator semantics.
- Fixing mypy errors in canonicalization/error construction touched by this leaf.

Out of Scope:

- Current-valid eligibility and lifecycle state transitions: R1C.
- Trusted correction registry: R1C.
- MANUAL/DERIVED/CROSS_INSTRUMENT identity and cycle handling: R1B.
- N+1 derivation child copy, replacement routing and nullable-clear semantics: R1B.
- Evidence mutation idempotency, replacement transaction atomicity and UNKNOWN_OUTCOME finalization: R1D.
- API/OpenAPI, Research typed links, schema/migration/model changes, frontend, worker, MinIO writes, parser/extractor implementation, embedding, RAG, Thesis, Agent or Capability Runtime.

Allowed Changes:

- `backend/evidence/services.py`
- `backend/evidence/errors.py` only if source/locator error detail typing requires it
- `tests/test_evidence_services.py`

No other candidate file may be added or changed.

## Must

1. Work only in the existing isolated worktree and branch:
   - `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`
   - `codex/wp04-02-evidence-domain-service`
   - HEAD remains `3eb494e6613cf3952ffbaaf4166b8cf3ea801555` because candidate files are uncommitted.
2. Before editing, read the source acceptance and repair program from the absolute main-worktree paths above, then read frozen contract §§8, 11, 14, 15, 16, 17, 22-24 and 27 from the absolute `Frozen Contract` path. These are read-only verifier/governance inputs; do not copy, move or edit them from the candidate worktree.
3. Use test-driven development. First add/correct tests and show that each targeted counterexample fails for the expected contract reason; then repair the implementation and rerun green.
4. Use the exact grade matrix:
   - COMPANY_ANNOUNCEMENT: S
   - FINANCIAL_REPORT: S
   - EXCHANGE_FILING: A
   - REGULATORY_DATA: A
   - OFFICIAL_DATA: A
   - POLICY_DOCUMENT: A
   - INVESTOR_RELATIONS: B
   - INSTITUTIONAL_SURVEY: B,C
   - BROKER_RESEARCH: C
   - INDUSTRY_REPORT: C,D
   - FINANCIAL_MEDIA: D
   - SOCIAL_MEDIA: E,F
   - RUMOR: F
   - WEB_PAGE: D,E,F
   - USER_NOTE: F
5. Implement a dedicated deterministic source-version fingerprint over exactly:
   - content_hash
   - media_type
   - source_grade
   - published_at
   - source_version_label
   - source_revision_id
   - document_language
   - parser_name
   - parser_version
   - text_object_hash
   - source_status
   - source_status_changed_at
   - source_status_reason
   - source_status_actor
   - versioned_metadata
6. Exclude source_document_id, version_reason, observed_at, fetched_at, object_key, text_object_key and idempotency_key from the fingerprint. They may belong to request/audit payloads but not version identity.
7. Do not reject a new source version merely because `content_hash` and `media_type` match. Same bytes plus grade/metadata/status differences must append a new version with a different fingerprint.
8. For a new idempotency key and an already-existing identical fingerprint, return/reconcile to the existing SourceDocumentVersion and create the required new idempotency/audit observation evidence without creating a second version.
9. Validate source lifecycle audit tuples before persistence. ACTIVE requires the source-status audit fields to be null; RETRACTED/SUPERSEDED require all required fields and a valid actor.
10. Use contract locator names such as `page_number` and `paragraph_index`; do not retain the candidate-only `page` field as the canonical input.
11. Validate all locator types deterministically. When parser metadata exposes bounds, enforce them; when it does not, validate the locator's required structural fields without inventing unavailable bounds.
12. Include `source_document_version_id` and an exact locator path in `EVIDENCE_INVALID_SOURCE_LOCATOR` details.
13. Ensure locator validation occurs before any series/version/idempotency/audit row can remain committable.

## Must Not

- Do not modify the frozen contract, models, repositories, registry, migration or `tests/conftest.py`.
- Do not fix or refactor R1B/R1C/R1D behavior in this leaf.
- Do not retain `COMPANY_ANNOUNCEMENT + A` as a successful test fixture.
- Do not use content hash as SourceDocumentVersion identity.
- Do not change AC, DoD, Required Verification, Evidence Required or this contract.
- Do not weaken/delete/skip/xfail tests.
- Do not introduce mocks, TODOs, placeholders or test-only production branches.
- Do not commit, merge, rebase, push, move `main`, or touch main-worktree acceptance files.

## Required PostgreSQL Tests

Add focused, meaningful assertions for:

1. Parameterized allowed and rejected pair coverage across every SourceType.
2. Fingerprint determinism across JSON order and timestamp-offset equivalents.
3. observed_at/fetched_at/object-key changes do not change the fingerprint.
4. content, grade, versioned metadata, source status, language, parser or required identity metadata changes do change the fingerprint.
5. New key + identical fingerprint returns the same SourceDocumentVersion ID, creates no second version, and records non-duplicated observation/idempotency/audit semantics.
6. Same bytes + valid grade reclassification appends N+1 and may reuse object key.
7. Same bytes + metadata correction appends N+1.
8. Same bytes + retraction notice appends N+1 with complete source lifecycle audit.
9. Two concurrent identical fingerprint imports create at most one row and the loser safely rereads/reconciles.
10. Positive and negative cases for all seven locator types.
11. `{page_number: 12}` is accepted when within parser `page_count`; legacy `{page: 12}` alone is rejected.
12. Invalid locator commits no EvidenceSeries, EvidenceVersion, locator, idempotency or audit record.

## High-Risk Counterexamples

- Same bytes with SourceGrade B→C on `INSTITUTIONAL_SURVEY` must create a new source version, not a duplicate error.
- Same fingerprint with a new idempotency key must reuse the old version rather than append or conflict.
- `COMPANY_ANNOUNCEMENT + A`, `FINANCIAL_REPORT + B`, `POLICY_DOCUMENT + C`, and `USER_NOTE + E` must all be rejected.
- A valid PAGE locator using `page_number` must not be rejected merely because `page` is absent.
- A PAGE/PARAGRAPH/TABLE/CELL coordinate beyond available parser metadata must fail without leaving partial durable rows.
- Source lifecycle audit fields that are partial or inconsistent with ACTIVE/RETRACTED/SUPERSEDED must fail before persistence.

## Required Verification

Run from the isolated worktree using the real PostgreSQL fixture:

```bash
git status --short --branch
git rev-parse HEAD

pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs

pytest -p no:cacheprovider -q \
  tests/test_evidence_persistence.py \
  tests/test_evidence_migrations.py -rs

pytest -p no:cacheprovider -q \
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

mypy --cache-dir=/tmp/tg-wp04-02-r1a-mypy \
  --explicit-package-bases \
  backend/evidence/errors.py \
  backend/evidence/services.py \
  --ignore-missing-imports

PYTHONPYCACHEPREFIX=/tmp/tg-wp04-02-r1a-pyc \
  python -m compileall -q backend apps migrations tests

alembic -c migrations/alembic.ini heads

git diff --check
git status --short
git diff --stat
git diff --name-status
```

The real PostgreSQL tests must not be skipped. If sandbox networking blocks localhost, use the already authorized unsandboxed test path and report that fact.

Verifier regression nodes that must become green after repair:

```text
/tmp/test_wp04_02_verifier.py::test_source_type_grade_matrix_matches_frozen_contract
/tmp/test_wp04_02_verifier.py::test_same_bytes_can_append_grade_reclassification
/tmp/test_wp04_02_verifier.py::test_contract_page_number_locator_is_accepted
```

Do not modify `/tmp/test_wp04_02_verifier.py`. The full verifier file will still contain expected failures belonging to later R1B/R1C/R1D leaves and must not be misreported as an R1A failure.

## Stop Conditions

Stop and report `BLOCKED` if:

- Correct source/version/locator semantics require changing WP04-01 models or migration.
- The exact frozen fingerprint fields cannot be represented with current persisted data.
- Correct locator validation requires a new parser schema rather than consuming optional existing metadata.
- A fix requires a fourth candidate file, API/schema change or another forbidden scope.
- Real PostgreSQL cannot be reached outside the sandbox.
- The task would require changing this contract or weakening a test.

## Expected Evidence

- Before/after candidate file hashes and exact changed-file list.
- Red-to-green output for each targeted contract counterexample.
- Exact count of SourceDocumentVersion rows in replay/reclassification/concurrency cases.
- Idempotency and audit row counts for unchanged re-observation and validation failure.
- Top Blocking AC → code location → test node → result mapping.
- Required Acceptance achieved/missing.
- Exact Ruff, format, mypy, compile, Alembic, WP04-01 and WP03 outputs.
- Confirmation that later R1B/R1C/R1D issues remain deferred and were not declared fixed.

## B. Governance Appendix

- Executor may report only `IMPLEMENTATION_COMPLETE` or `BLOCKED`; it cannot self-approve or use PASS/DONE/VERIFIED.
- `IMPLEMENTATION_COMPLETE` means only the R1A leaf is ready for independent verification, not that `TASK-WP04-02` has passed.
- No Evidence, No PASS; verifier independently reruns the tests.
- A R1A failure produces a narrower repair before R1B.
- A R1A pass proceeds to R1B but leaves the original WP04-02 acceptance as FAIL until final re-verification.

## Executor Final Response

Return:

1. Status: `IMPLEMENTATION_COMPLETE` or `BLOCKED`
2. Baseline/branch/worktree
3. Changed files and hashes
4. Source matrix/fingerprint/dedup/locator implementation locations
5. Red-to-green evidence
6. Real PostgreSQL focused results with pass/fail/skip counts
7. WP04-01 and WP03 regression results
8. Ruff/format/mypy/compile/Alembic results
9. Scope confirmation
10. Remaining deferred R1B/R1C/R1D findings
11. Final Git status; no commit/merge/push/main mutation
