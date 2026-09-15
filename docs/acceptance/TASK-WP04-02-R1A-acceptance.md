# TASK-WP04-02-R1A Acceptance Report

**OVERALL: FAIL — REPAIR_REQUIRED**

## Metadata

- Task ID: `TASK-WP04-02-R1A`
- Date: `2026-09-15`
- Verifier: Codex independent verifier
- Report Path: `docs/acceptance/TASK-WP04-02-R1A-acceptance.md`
- Candidate worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`
- Candidate branch: `codex/wp04-02-evidence-domain-service`
- Baseline and candidate HEAD: `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`
- Implementation Status: three untracked candidate files; no candidate commit; local `main` unchanged
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`
- Missing Acceptance: `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Repair Required: `YES`
- Repair ID: `TASK-WP04-02-R1A-R1`

## Changed Files Snapshot

- `BASELINE_CHANGED_FILES`: the isolated worktree was based on exact `main@3eb494e`; the WP04-02 candidate already consisted of three untracked files before R1A.
- `FINAL_CHANGED_FILES`:
  - `?? backend/evidence/errors.py`
  - `?? backend/evidence/services.py`
  - `?? tests/test_evidence_services.py`
- Task-attributable Changes: R1A modified `services.py` and `test_evidence_services.py`; `errors.py` hash remained unchanged from the pre-R1A acceptance snapshot.
- Attribution: `CERTAIN`

Candidate SHA-256 at verification:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
c20f956f411180083a0b3dc21754beaaa5c60a957e9e97ad737caa7cc5872d62  backend/evidence/services.py
c31136b9f5398e188d4278f03492b6ccb7c8344adddbd2bd788176f91fcb4329  tests/test_evidence_services.py
```

## Classification

- Task Type: `REPAIR`, `DOMAIN_SERVICE`, `DB_PERSISTENCE`
- Risk Type: source identity, immutable version history, idempotency, concurrency, audit, fail-before-write validation
- Touched Layers: Evidence service, domain errors, real-PostgreSQL service tests
- Task Size: `MEDIUM`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, DB Persistence, G5 Regression, G6 Evidence
- Not Applicable Gates: API/OpenAPI, frontend/browser, migration/schema modification

## Top Blocking AC Results

| Top Blocking AC | Result | Independent evidence |
|---|---|---|
| TOP-AC-01 Exact SourceType/SourceGrade closed matrix | `PASS` | Static equality and fresh real-PostgreSQL allowed/forbidden parameterization pass |
| TOP-AC-02 Exact deterministic SourceDocumentVersion fingerprint | `PASS` | Field-by-field static review plus independent exact-projection test pass |
| TOP-AC-03 Identical-fingerprint re-observation and same-byte revisions | `PASS` | Fresh PostgreSQL candidate suite plus independent re-observation and B→C grade-reclassification tests pass |
| TOP-AC-04 All locator types, parser bounds, stable details and fail-before-write | `FAIL` | Independent public service-path verifier reports five locator contract failures |
| TOP-AC-05 Static, DB and regression evidence | `FAIL` | Ruff/mypy/compile/regression pass, but blocking locator contract/DB behavior fails |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | `PASS` | Correct branch/worktree; HEAD and `main` both resolve to exact `3eb494e...` |
| G1 Scope | `PASS` | Exactly the three authorized untracked candidate files; no schema/model/repository/API/docs/Research/runtime change |
| G2 Contract | `FAIL` | WEB_ANCHOR optional fields, TABLE optional coordinate bounds, TABLE_CELL cell-ref form and required locator error details contradict frozen §15/R1A contract |
| G3 Architecture | `FAIL` | The public service validation boundary permits an out-of-bounds TABLE coordinate to continue toward persistence and rejects contract-valid locator forms |
| G4 Test | `FAIL` | Candidate `62 passed`, but the suite omits the five independent failing locator counterexamples |
| DB Persistence | `FAIL` | Real PostgreSQL public-path verifier demonstrates the wrong locator decisions; invalid TABLE row bounds are accepted instead of failing before write |
| G5 Regression | `PASS` | Fresh combined WP04-01/migration/WP03 run: `35 passed, 4 warnings` |
| G6 Evidence | `FAIL` | Self-authored green suite does not cover all Blocking AC; independent verifier is `5 failed, 5 passed` |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary/Negative Evidence | Verdict |
|---|---|---|---|---|---|
| AC-01 [BLOCKING] | Exact 15-entry SourceType/Grade matrix | `services.py:84-100` | Candidate matrix tests and independent equality test pass | Representative forbidden pairs reject | `PASS` |
| AC-02 [BLOCKING] | Fingerprint uses exactly frozen §8 fields and canonical normalization | `services.py:101-117,224-231,397-414` | Candidate deterministic test and independent exact-projection test pass | Observation/storage/idempotency fields excluded | `PASS` |
| AC-03 [BLOCKING] | Identical fingerprint + new key re-observes without new version | `services.py:443-474,1435-1465` | Real PostgreSQL candidate and independent tests preserve one version, two idempotency references and one new audit | Different observation/object key does not append | `PASS` |
| AC-04 [BLOCKING] | Same bytes may append grade/metadata/retraction versions | `services.py:458-551` | Candidate PostgreSQL sequence and independent B→C test pass | Four distinct fingerprints with reusable object key | `PASS` |
| AC-05 [BLOCKING] | Source lifecycle tuple validates before persistence | `services.py:1396-1432` | Candidate rollback/count test passes | Partial tuple leaves counts unchanged | `PASS` |
| AC-06 [BLOCKING] | WEB_ANCHOR requires canonical_url; anchor/css/text hash are optional | `services.py:1708-1720` | Independent real-PostgreSQL public-path test fails | canonical_url-only locator is wrongly rejected | `FAIL` |
| AC-07 [BLOCKING] | TABLE optional coordinates honor parser bounds | `services.py:1666-1675` | Independent real-PostgreSQL public-path test fails | `row_index=99` is accepted despite parser `row_count=5` | `FAIL` |
| AC-08 [BLOCKING] | TABLE_CELL supports a nonempty `cell_ref` representation | `services.py:1676-1707` | Independent real-PostgreSQL public-path test fails | cell_ref-only locator is wrongly rejected for missing numeric row/column | `FAIL` |
| AC-09 [BLOCKING] | Every locator error has source-version ID and exact input path | `services.py:1600-1603,1625-1629,1755-1764` | Two independent detail tests fail | Missing-locator error has no details; missing short citation reports `raw_locator` | `FAIL` |
| AC-10 [BLOCKING] | Invalid locators leave no committable Evidence/idempotency/audit residue | `services.py:602-613` validates before nested write | Candidate covered negative cases pass | Out-of-bounds optional TABLE coordinate is not classified invalid and proceeds into mutation path | `FAIL` |
| AC-11 [BLOCKING] | Concurrent identical fingerprint import reconciles to at most one version | Source row lock, duplicate reread and unique constraint handling in `services.py:389,458-474,510-550` | Fresh candidate real-PostgreSQL concurrent test passes | One version ID and two idempotency references asserted | `PASS` |
| AC-12 [BLOCKING] | Required static/type gates pass | Three candidate files | Ruff, format, mypy and compile all exit 0 | No skip/mock/TODO drift found | `PASS` |

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| Git branch/HEAD/main/status/hash/line-count checks | exact branch and `3eb494e...`; exactly three untracked files; hashes match execution report | Baseline, attribution and scope |
| `pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs` inside sandbox | `2 passed, 60 errors`; all errors are localhost `PermissionError` | Confirm environment restriction; not product evidence |
| Same focused pytest outside sandbox | `62 passed, 2 warnings in 44.00s` | Reproduce executor focused claim against real PostgreSQL |
| Combined WP04-01/migration/WP03 pytest outside sandbox | `35 passed, 4 warnings in 22.15s` | Regression evidence |
| Independent `/tmp/test_wp04_02_r1a_verifier.py` initial contract set | `5 passed` | Matrix, exact fingerprint, grade reclassification, re-observation and PAGE behavior |
| Independent verifier after locator counterexamples | `5 failed, 5 passed in 5.83s` | Prove uncovered locator contract defects on public service/real PostgreSQL paths |
| Ruff check and format check | `All checks passed`; `3 files already formatted` | Static gate |
| Fresh mypy with explicit package bases | `Success: no issues found in 3 source files` | Type gate |
| Compileall for three files | exit 0 | Compilation |
| `alembic -c migrations/alembic.ini heads` | `000000000004 (head)` | Migration graph unchanged |
| `git diff --check` and anti-drift scan | no whitespace errors; no TODO/FIXME/skip/xfail/mock/fake branch hits | Scope/evidence hygiene |

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| Forbidden grade accepted | Yes | Complete candidate matrix parameterization plus independent exact equality | `PASS` |
| Fingerprint includes excluded field or omits required field | Yes | Independent exact projection and code field tuple | `PASS` |
| Same-byte grade correction rejected | Yes | Independent PostgreSQL B→C append produces version 2 | `PASS` |
| New key + same fingerprint creates duplicate | Yes | Independent PostgreSQL counts: one version, two idempotency references, one additional audit | `PASS` |
| canonical_url-only WEB_ANCHOR rejected | Yes | Independent public-path test raises `EVIDENCE_INVALID_SOURCE_LOCATOR` | `FAIL` |
| TABLE optional coordinate bypasses parser bound | Yes | row 99 with row_count 5 creates instead of rejecting | `FAIL` |
| TABLE_CELL cell_ref representation rejected | Yes | cell_ref-only public-path input fails on required row_index | `FAIL` |
| Missing locator lacks stable details | Yes | `details` lacks source_document_version_id and locator_path | `FAIL` |
| Missing short citation points to wrong field | Yes | error path is `raw_locator`, not `short_citation` | `FAIL` |

## DB Persistence Result

- Schema constraints: existing migration head remains `000000000004`; no schema change occurred.
- Source version history: grade, metadata and retraction revisions append in the covered scenarios.
- Re-observation: same fingerprint reuses the existing version and adds idempotency/audit evidence.
- Concurrency: candidate PostgreSQL test proves one version and reconciled IDs for the covered race.
- Locator validation: `FAIL`; public real-PostgreSQL paths reject legal inputs and accept an invalid parser-bounded TABLE coordinate.
- Transaction boundary: covered invalid locator cases fail before writes, but the omitted optional-coordinate case is misclassified as valid and therefore cannot satisfy fail-before-write.
- Real persistence vs InMemory/Fake/Mock: all DB evidence cited above used disposable real PostgreSQL databases; no fake repository was used.

## Blocking Findings

### BF-01 — WEB_ANCHOR optional fields are made mandatory

Frozen §15 says `canonical_url` is required while `anchor`, `css_selector` and `text_quote_hash` are optional. `services.py:1715-1720` requires at least one optional field, so a contract-valid canonical-url-only locator fails.

### BF-02 — TABLE optional coordinates bypass parser bounds

`services.py:1666-1675` validates page and table indexes, then returns without validating supplied `row_index`, `column_index` or `cell_ref`. The independent public-path PostgreSQL test supplies `row_index=99` with `row_count=5`; the command does not raise and proceeds into the mutation path.

### BF-03 — TABLE_CELL rejects the contract cell_ref form

`services.py:1683-1687` always requires numeric row and column indexes. Frozen §15 permits `cell_ref`; a locator using `page_number`, `table_index` and nonempty `cell_ref` is rejected before it can persist.

### BF-04 — Locator error details are incomplete or point at the wrong field

`services.py:1600-1603` raises the stable code without `source_document_version_id` or `locator_path` when locators are missing. `services.py:1625-1629` combines raw-locator and short-citation validation but always reports `raw_locator`, violating the exact-path requirement.

## Non-Blocking Findings

- None recorded for this leaf; unresolved R1B/R1C/R1D defects remain explicit deferrals and are not reclassified as R1A findings.

## Regression Result

- Result: `PASS` for the required affected regressions.
- Preserved behavior: WP04-01 persistence, general migrations, Evidence migration 0004, WP03 Research API and persistence all pass in the fresh combined 35-test run.
- Regression gaps: the original WP04-02 remains `FAIL`; this leaf cannot authorize WP04-03 or integration.

## Repair Required

- `YES`
- Repair ID: `TASK-WP04-02-R1A-R1`
- Failed AC/Gate: AC-06 through AC-10; G2 Contract, G3 Architecture, G4 Test, DB Persistence, G6 Evidence.
- Must preserve: passed matrix, fingerprint, re-observation, same-byte revision, lifecycle, concurrency, static and regression evidence.

## Final Decision Rationale

`FAIL`。R1A substantially improves the original candidate and independently passes source-grade, fingerprint, re-observation, same-byte revision, lifecycle, concurrency and static gates. However, locator behavior is a Top Blocking AC. Five fresh independent counterexamples show that the candidate tests omit contract-valid optional forms, omit parser-bound validation for supplied TABLE coordinates, and do not enforce required error detail paths. A Blocking AC failure prevents R1A PASS regardless of the self-authored `62 passed` result.

## Next Action

Execute only `TASK-WP04-02-R1A-R1`, a small locator-only repair in the same isolated worktree. Do not proceed to R1B until R1A-R1 receives an independent PASS; do not commit, merge or enter WP04-03.
