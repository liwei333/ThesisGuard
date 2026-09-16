# TASK-WP04-02-R1C-04A — Independent Acceptance

**OVERALL: PASS**

## Metadata

- Task ID: `TASK-WP04-02-R1C-04A`.
- Date: 2026-09-16, Asia/Shanghai.
- Verifier: Codex, independent verifier role using `ai-task-governor`.
- Report path: `docs/acceptance/TASK-WP04-02-R1C-04A-acceptance.md`, following the repository's existing `docs/acceptance` convention.
- Implementation status received: `IMPLEMENTATION_COMPLETE`; this status was treated only as a verification lead and not as approval.
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Achieved acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED` for the R1C-04A display-text admission slice.
- Missing acceptance for this slice: none.
- Repair required: NO.

This PASS closes only `TASK-WP04-02-R1C-04A`. It does not approve a positive trusted correction rule, qualify initial direct `VERIFIED` import, close all R1C/R1D, approve Git integration, or change the original whole-task `TASK-WP04-02` status.

## Baseline and changed-files snapshot

The dispatched candidate baseline was branch `codex/wp04-02-evidence-domain-service`, HEAD `0cef44fd2ffd929b40e849e607af0bd4c44d14d2`, parent `bdd70edc153b6ed5def65ed99c41f325df45f066`, initially clean. The independently inspected final candidate remains on the same HEAD/parent and has exactly:

```text
 M backend/evidence/services.py
 M tests/test_evidence_services.py
```

There are no staged or candidate-untracked files. The final SHA-256 values independently matched the execution report:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
94bb12823690a07ef323323cffacbd756081f23b2edd7de04fc25884e5e612a6  backend/evidence/services.py
3c7da5f9405990ca047957b46a25ff0d8cde736152ec7d472c5535b2ed0d67d0  tests/test_evidence_services.py
```

Main remains at `438738c543e4cae3e805d31324b068c1cd5c7059`, parent `7d3734bc8346c16f9bbf7f7d9806309949c996de`; its tracked/index diff is empty. Existing untracked governance/verifier evidence was preserved. This verification adds this acceptance and the separately dispatched next-task contract only. Attribution is CERTAIN from the fixed baseline hashes, two-file candidate diff and task-specific artifact paths.

## Classification and selected gates

- Task type: `REPAIR` / backend domain service.
- Risk types: DB integrity, append-only history, transaction residue, idempotency, audit, exact-version lineage and replay compatibility.
- Touched layers: Evidence service and real-PostgreSQL tests.
- Task size: SMALL by one admission invariant, with a deliberately broad boundary matrix.
- Evidence matrix: Full.
- Selected gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, DB Persistence, G5 Regression and G6 Evidence.
- Not applicable: browser/UI, API/OpenAPI, migration/schema-change and deployment gates.

## Top Blocking AC results

| Top AC | Result | Independent evidence |
|---|---|---|
| Genuine pre-fix business RED | PASS | The retained `empty-body-red.log` records unchanged-services SHA and two real PostgreSQL assertion failures (`DID NOT RAISE`), not permission/setup/cleanup failure. Manifest/log hashes were independently recomputed. |
| Five write routes reject blank/non-string bodies before writes | PASS | Code review found deliberate guards in `create_evidence_series_version`, `create_replacement_evidence_series` and `_append_status_or_revision`; automatic and underlying paths flow through those boundaries. Fresh focused run: `87 passed, 239 deselected`. |
| Preserve valid bytes, omitted-body inheritance, explicit revise-None semantics, lineage and replay | PASS | Shared validator uses `strip()` only as a blankness predicate and never returns or assigns normalized text. Focused positive/history/replay tests passed on real PostgreSQL; code preserves the existing `EvidenceInvalidProvenance` path for revise `None`. |
| Caller-commit plus fresh-session no-residue/history proof | PASS | Sixty-seven negative scenarios compare all columns/all rows in nine tables after caller commit in a distinct session; keys, current row, exact history and children remain unchanged. The focused run and persistence-proof manifest agree. |
| Scope, protected artifacts and full regression preserved | PASS | Candidate diff contains exactly two authorized files; errors/models/repositories/migrations and fixed verifiers have expected hashes. Independent R1 oracle + five fixed verifiers + persistence/migration/Research run: `163 passed, 2 warnings`. |

## Gate results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Contract, execution report, fixed HEAD/parent, before/after manifests, two-file diff and initial/final hashes are available and mutually consistent. |
| G1 Scope | PASS | Service diff is 27 lines and tests add the authorized R1C-04A matrix. No dependency, schema, migration, API, frozen contract, old verifier or Git-history change occurred. |
| G2 Contract | PASS | All five routes, type/blank cases, effective-body behavior, valid-byte preservation, history, exact replay and ordinary routing map to observable tests and passed. |
| G3 Architecture | PASS | Validation is private/shared, service remains flush-only with caller-owned commit, append-only history and exact lineage remain intact, and no test-only production branch or positive trusted rule was introduced. |
| G4 Test | PASS | Independent focused real-PostgreSQL run passed all 87 selected tests. Executor's full-service log is hash-verified and records `326 passed`. |
| DB Persistence | PASS | Real PostgreSQL 17.11 disposable fixtures exercised writes and rejection boundaries; caller commit/fresh-session full-row equality proves no residue rather than relying on rollback or mocks. |
| G5 Regression | PASS | Independent combined run passed the 58-scenario R1 oracle, 70 fixed verifier tests and 35 persistence/migration/Research tests: `163 passed, 2 existing warnings`. |
| G6 Evidence | PASS | All 58 indexed files plus the self-excluded artifact manifest are present; every indexed artifact/log size and SHA-256 was recomputed successfully. Logs bind final candidate hashes to focused, oracle, verifier, full-suite and static runs. |

## Full evidence matrix

| AC | Requirement | Implementation evidence | Verification evidence | Boundary/negative evidence | Verdict |
|---|---|---|---|---|---|
| AC-01 | New body must be a nonblank string | `_validate_display_text` at `backend/evidence/services.py:1540`; pre-hash type guards and post-replay blank guards at create/replacement/append boundaries | Independent `pytest ... -k r1c04a`: `87 passed` | Empty, ASCII/Unicode whitespace, bool, integer, list, dict, `None`, bytes and set across all five routes | PASS |
| AC-02 | No new durable residue or key consumption on rejection | Guards execute before ORM row construction/attachment; tests snapshot nine ORM tables | Same fresh focused run; persistence-proof manifest reports 67 caller-commit/fresh-session equalities | Full rows/all columns, current/exact/children and failed key prefixes checked | PASS |
| AC-03 | Preserve valid display bytes and correction routing | Validator does not transform value; same/automatic/direct/initial/underlying production commands are exercised | Twelve positive cases in focused run | Leading/trailing Unicode/financial text remains byte-equal; omitted revise body inherits; nullable machine fields still clear | PASS |
| AC-04 | Preserve historical exact reads and committed replay | Validation deliberately occurs after successful exact replay for blank strings; historical rows are never mutated | Four committed replay and four historical controls passed | Omitted propagation/review from a legacy blank latest row rejects; valid repair appends; historical blank exact and seeded committed replay remain readable | PASS |
| AC-05 | Preserve accepted R1A/R1B/R1C behavior and repository regressions | Fixed verifier files and oracle hashes are unchanged | Independent combined run `163 passed, 2 warnings`; executor hash-bound full service `326 passed` | Exact graph, status/current-valid, persistence/migration and Research paths retained | PASS |
| AC-06 | Static quality and exact scope | Two-file diff; fixed `errors.py` hash | Independent Ruff/format/mypy all exit 0; `git diff --check` exit 0 | No staged/untracked candidate file, no main tracked/index mutation | PASS |

## Commands actually executed by this verifier

| Command | Result | Purpose |
|---|---|---|
| `pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1c04a -rs` with candidate-first `PYTHONPATH` and normal local DB permission | `87 passed, 239 deselected in 66.27s` | Independent focused L3/L4_DB verification |
| One combined pytest invocation over the R1 oracle, five fixed verifiers, persistence/migration and Research suites | `163 passed, 2 warnings in 112.57s` | Independent regression and prior-acceptance preservation |
| `ruff check` and `ruff format --check` for the three business/test files | pass; three files formatted | L2 static quality |
| `mypy --explicit-package-bases --ignore-missing-imports ...` | success, no issues in three source files | L2 type verification |
| `git diff --check`, status, HEAD/parent and SHA-256 inspection | pass; exact two-file scope and expected hashes | Baseline/scope integrity |
| Artifact and command-log manifest recomputation using `jq`, `shasum`, `stat` | all indexed files/logs matched declared hashes and sizes | Evidence authenticity/integrity |

The executor's hash-bound final evidence additionally records `326 passed` for the full Evidence service suite, `35 passed, 2 warnings` for the regression subset, Ruff/format/mypy/compileall success and Alembic single head `000000000004`. Those records were not treated as self-report alone: their files and hashes were recomputed, and the overlapping focused/oracle/fixed/regression/static paths were independently rerun.

## Counterexample and negative review

| Risk | Evidence | Verdict |
|---|---|---|
| A non-string reaches stable hashing and throws incidental serialization errors | Pre-hash type guards plus bytes/set/dict/list/bool/int cases passed | PASS |
| Whitespace validation trims valid persisted content | Code returns without transformation; byte-preservation positives passed | PASS |
| Automatic/direct/underlying route bypasses the shared guard | Each route has negative and positive production-command coverage; no-residue equality passed | PASS |
| Rejection flushes partial series/version/children/key/audit rows | Caller commits after the domain error; a distinct session compares every row/column in nine tables | PASS |
| New validation rewrites or makes old blank history unreadable | Exact historical reads and committed replay controls passed; no old row is updated | PASS |
| Tests manufacture success by editing old verifiers or enabling a trusted rule | Six verifier hashes match; production approved trusted set remains empty | PASS |

## Findings and regression result

Blocking findings: none.

Non-blocking/open program boundaries:

- The public creation path still needs separate qualification for a no-predecessor initial `VERIFIED` import. This task did not prove source/locator/semantic admission for that path.
- Positive trusted correction remains `NOT_READY`; the production approved rule collection remains empty.
- Complete ordinary-correction source/from-status/window policy, R1D idempotency/atomicity/concurrency and final whole-task re-verification remain open.
- The two existing HTTP 422 deprecation warnings are unrelated to this repair.

Regression result: PASS for this slice. R1A, R1B, R1C-01/02/03A boundaries, persistence, migration and Research regression paths remain green at the final hashes.

## Final decision rationale and next action

The implementation satisfies every blocking R1C-04A criterion with independent code review, fresh real-PostgreSQL execution, negative/no-residue evidence, fixed-verifier regression and artifact integrity checks. Therefore the only valid verdict is `PASS`.

Next action: dispatch `TASK-WP04-02-R1C-05A — Initial VERIFIED Import Fail-Closed Admission`. It must close the currently unsafe unqualified public initial-`VERIFIED` path without inventing a positive semantic validator or weakening fixed lifecycle/oracle tests. R1D and WP04-03 must not start yet.

