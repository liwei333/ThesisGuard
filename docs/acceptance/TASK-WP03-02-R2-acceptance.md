# ACCEPTANCE REPORT

**OVERALL: PASS**

## Metadata

- Task ID: `TASK-WP03-02-R2`
- Original Task: `TASK-WP03-02`
- Date: `2026-09-13` (`Asia/Shanghai`)
- Verifier: Codex, independent `ai-task-governor` VERIFIER run
- Report Path: `docs/acceptance/TASK-WP03-02-R2-acceptance.md`
- Report Path Basis: the project already uses `docs/acceptance/` for WP03 formal acceptance reports.
- Implementation Status: executor reported `IMPLEMENTATION_COMPLETE`; independent verification completed.
- Implementation Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp03-research-package`
- Branch: `codex/wp03-research-package`
- HEAD / Baseline Commit: `d9bceedf27d80c84472613868b97d7b172cacfd6`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_RUNTIME_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_RUNTIME_VERIFIED`, `L4_DB_VERIFIED`
- Missing Acceptance: none
- Overall Verdict: `PASS`
- Repair Required: `NO`
- Next Action: close `TASK-WP03-02` and proceed to the next smallest WP03 dependency, `TASK-WP03-03` — establish the OpenAPI-generated TypeScript client and drift gate before Research UI work.

## Executive Decision

R2 closes the remaining Blocking 422 contract defect. The generated OpenAPI now accurately distinguishes FastAPI/Pydantic request-validation responses from the stable Research error envelope:

- initial-create and refresh 422 responses use an exact two-branch `oneOf`;
- specified-version read uses only `HTTPValidationError`;
- 404 and 409 responses remain `ResearchErrorResponse`;
- every referenced component resolves;
- runtime invalid-input responses match the declared alternatives.

The tests were strengthened rather than weakened: they now inspect both response bodies and exact OpenAPI schema structure. All parent API, idempotency, concurrency, append-only history, persistence, and quality checks remain green.

## Changed Files Snapshot

### BASELINE_CHANGED_FILES

Inherited cumulative WP03 changes before R2:

- `apps/api/main.py`
- `backend/common/db/models_registry.py`
- `backend/research/api.py`
- `backend/research/models.py`
- `backend/research/schemas.py`
- `backend/research/services.py`
- `docs/WP03_RESEARCH_PACKAGE_API.md`
- `docs/WP03_RESEARCH_PACKAGE_PERSISTENCE.md`
- `migrations/versions/20260912_003_research_package.py`
- `tests/test_research_api.py`
- `tests/test_research_persistence.py`

### FINAL_CHANGED_FILES

- `M apps/api/main.py`
- `M backend/common/db/models_registry.py`
- `?? backend/research/api.py`
- `?? backend/research/models.py`
- `?? backend/research/schemas.py`
- `?? backend/research/services.py`
- `?? docs/WP03_RESEARCH_PACKAGE_API.md`
- `?? docs/WP03_RESEARCH_PACKAGE_PERSISTENCE.md`
- `?? migrations/versions/20260912_003_research_package.py`
- `?? tests/test_research_api.py`
- `?? tests/test_research_persistence.py`

### Task-attributable R2 changes

- `backend/research/api.py`
  - R1 SHA-256: `23853af445049d1bfb9a2dcb34db7aaa1223661d7e79b20cdf40695c08843ae1`
  - R2 SHA-256: `e2f721dbcbd37d3c164aabc66f00138f289b6d1d1c11ef1a146ab943621b789e`
- `tests/test_research_api.py`
  - R1 SHA-256: `ef0f2492391b4132acbda31f32bbd04545b3fde0e1194a5805504e59e3eefd59`
  - R2 SHA-256: `eb6148bee0cb073dc88c9621141de68cdd200521d0e618cf0b54f1214ee762ad`

Unchanged from R1:

- `backend/research/schemas.py` — SHA-256 `fbed316559da24073c5c5a03b41d17b06bfb7ee0b7f4639bbe582f48a1d7fba5`
- `docs/WP03_RESEARCH_PACKAGE_API.md` — SHA-256 `d898e14b0166ffff1ca70ede1af1b24152736f372cc36677f8da163af028c7bb`

Attribution: `CERTAIN`. No new migration, model, service, router-registration, frontend, dependency, worker, or infrastructure change is attributable to R2.

## Classification

- Task Type: `REPAIR + BACKEND_API_CONTRACT`
- Risk Type: public OpenAPI accuracy, generated-client compatibility, regression of idempotent/versioned DB API behavior
- Touched Layers: FastAPI response metadata, API contract tests, ASGI runtime validation tests
- Task Size: `SMALL`
- Evidence Matrix Type: `Full` because the repaired contract belongs to a critical API with idempotency, concurrency, and real DB behavior
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, DB Persistence, G5 Regression, G6 Evidence
- Not Applicable Gates: browser/UI, worker/queue, external provider, permission/tenant/DataScope

## Top Blocking AC Results

| Top AC | Result | Evidence |
|---|---|---|
| TOP-AC-01 — create and refresh 422 schemas are an exact, resolvable `oneOf` of standard and Research errors | PASS | `backend/research/api.py:59-71`, route bindings at lines 215 and 304; independent OpenAPI assertion passed. |
| TOP-AC-02 — version-read 422 declares only the standard FastAPI validation response | PASS | `backend/research/api.py:51-58`, binding at line 274; independent OpenAPI assertion returned only `#/components/schemas/HTTPValidationError`. |
| TOP-AC-03 — runtime response bodies match the declared alternatives | PASS | Independent ASGI probe covered missing/empty/long headers, whitespace-only headers, version zero, invalid refresh body, and whitespace refresh header. |
| TOP-AC-04 — tests enforce exact contract structure without weakening earlier checks | PASS | `tests/test_research_api.py:112-127`, `325-404`, and `407-516`; previous error/freshness/path/header assertions remain and new exact refs/body-shape assertions pass. |
| TOP-AC-05 — parent API, idempotency, concurrency, DB history, and quality behavior remain green | PASS | API 8/8, persistence 8/8, full 57/57, Ruff, mypy, Compose, diff integrity, and temporary DB cleanup all passed. |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Worktree, branch, HEAD, worktree list, prior acceptance reports, cumulative status, and pre/post-R2 hashes were inspected. |
| G1 Scope | PASS | Only the two permitted R2 files changed relative to the R1 snapshot. No dependency, schema, documentation, service, migration, frontend, or global handler expansion occurred. |
| G2 Contract | PASS | OpenAPI expresses the exact endpoint-specific 422 alternatives, preserves typed 404/409, exact error-code enum, and exact freshness enum. |
| G3 Architecture | PASS | Framework validation keeps FastAPI's native list envelope; Research validation keeps its typed domain envelope; no global exception handler or cross-module semantic change was introduced. |
| G4 Test | PASS | Focused contract test, full API suite, runtime probe, and full project suite all passed; changed tests strengthen the contract. |
| DB Persistence | PASS | The unchanged real PostgreSQL API/persistence paths passed; no fake/in-memory substitute and no temporary database leakage. |
| G5 Regression | PASS | `57 passed, 4 warnings`; idempotency, concurrency, version history, and earlier application tests remain green. |
| G6 Evidence | PASS | Static locations, generated OpenAPI, real ASGI results, automated suites, quality checks, and cleanup evidence agree. |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary / Negative Evidence | Verdict |
|---|---|---|---|---|---|
| R2-AC-01 [BLOCKING] | Create 422 is exact two-branch `oneOf` | `RESEARCH_OR_HTTP_VALIDATION_RESPONSE`; create route binding | Fresh OpenAPI script asserted exact key, two refs, cardinality, and resolvability | Missing, empty, and long header use list; whitespace-only header uses Research object | PASS |
| R2-AC-02 [BLOCKING] | Refresh 422 is exact two-branch `oneOf` | Shared response metadata; refresh route binding | Fresh OpenAPI script asserted exact refs and resolution | Invalid body uses list; valid body plus whitespace-only header uses Research object | PASS |
| R2-AC-03 [BLOCKING] | Version-read 422 is only `HTTPValidationError` | `HTTP_VALIDATION_RESPONSE`; version route binding | Fresh OpenAPI script asserted exact single `$ref` | `versions/0` returned list and no Research envelope | PASS |
| R2-AC-04 [BLOCKING] | 404/409 and R1 schemas remain stable | Existing Research response models and metadata | OpenAPI probe checked all six applicable 404/409 responses, error components, and four-value freshness enum | No untyped/missing refs; no enum broadening | PASS |
| R2-AC-05 [BLOCKING] | Runtime tests distinguish both 422 bodies | Validation helper assertions and expanded negative cases | API suite `8 passed`; direct ASGI probe passed | Tests check list/object type, field location, stable code, and non-empty message rather than status only | PASS |
| R2-AC-06 [BLOCKING] | Passed parent behavior is preserved | No service/model/migration changes | API 8/8, persistence 8/8, full 57/57 | Concurrent refresh, replay/conflict, history, and cleanup remain covered | PASS |

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| `git status --short --branch` | PASS | Confirm branch and cumulative dirty baseline |
| `git rev-parse HEAD` | PASS — `d9bceedf...` | Confirm baseline commit |
| `git worktree list --porcelain` | PASS | Confirm main and isolated WP03 worktrees |
| SHA-256 comparison of R1/R2 files | PASS | Establish exact task attribution |
| `git diff --check` | PASS | Diff integrity |
| Independent `create_app().openapi()` plus ASGI counterexample script | PASS — `openapi_contract`, `runtime_422_shapes`, `freshness_enum`, and `refs_resolve` | Direct L3/L4 contract/runtime verification |
| `pytest -q tests/test_research_api.py::test_openapi_contains_research_contract -rs` | PASS — `1 passed, 2 warnings` | Focused R2 contract regression |
| `pytest -q tests/test_research_api.py -rs` | PASS — `8 passed, 4 warnings`, zero skipped | Real ASGI/PostgreSQL API, error, idempotency, concurrency regression |
| `pytest -q tests/test_research_persistence.py -rs` | PASS — `8 passed, 2 warnings`, zero skipped | Preserve WP03-01 real PostgreSQL behavior |
| `pytest -q -rs` | PASS — `57 passed, 4 warnings`, zero skipped | Full regression |
| `make lint` | PASS — `All checks passed!` | Ruff |
| `make typecheck` | PASS — `46 source files` | Mypy |
| `docker compose config --quiet` | PASS | Compose validity |
| PostgreSQL query for `tg_wp03_%` databases | PASS — `0` | Cleanup verification |

The four warnings are framework deprecations involving Starlette TestClient, AnyIO's BlockingPortal alias, and `HTTP_422_UNPROCESSABLE_ENTITY`. They do not change this verdict and are outside the R2 contract.

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| Missing idempotency header incorrectly documented as Research error | Yes | Runtime returned standard list; create OpenAPI includes `HTTPValidationError` | PASS |
| Empty idempotency header confused with whitespace-only header | Yes | Empty string returned standard list; whitespace-only returned Research object/code | PASS |
| Header longer than 128 bypasses framework validation | Yes | Runtime returned standard header validation list | PASS |
| Version zero incorrectly advertises Research error | Yes | Runtime list and exact single standard `$ref` | PASS |
| Invalid refresh body omitted from OpenAPI | Yes | Runtime body-validation list and refresh `oneOf` includes standard schema | PASS |
| Custom refresh validation omitted from OpenAPI | Yes | Valid body plus whitespace-only header returned Research envelope; `oneOf` includes it | PASS |
| Dangling component refs | Yes | Every 404/409/422 `$ref` resolved in `components.schemas` | PASS |
| R1 freshness/error contract regresses | Yes | Exact enum/components and focused test passed | PASS |
| Parent idempotency/concurrency/history regresses | Yes | Real API and persistence suites plus full regression passed | PASS |

## DB Persistence Result

- Schema constraints: unchanged from accepted WP03-01.
- Read semantics: current/history/specific-version paths remain covered through real PostgreSQL.
- Replace semantics: not applicable; append-only copy-on-write remains the verified behavior.
- Active/inactive/deleted/status: lifecycle/freshness behavior remains unchanged.
- Transaction boundary: real AsyncSession commit/rollback behavior remains covered.
- Version/snapshot/history: version conflict, concurrent version creation, and old-version readability remain covered.
- Real persistence vs InMemory/Fake/Mock: API and persistence suites create Alembic-migrated disposable PostgreSQL databases; no fake persistence was used for L4 claims.
- Cleanup: `0` databases matching `tg_wp03_%` remained after verification.

## Blocking Findings

None.

## Non-Blocking Findings

1. Existing framework deprecation warnings remain. They are unrelated to R2 and should not be mixed into the accepted repair.
2. The worktree intentionally remains uncommitted with cumulative WP03 changes; branch integration is a separate user-authorized action.

## Regression Result

- Result: `PASS`
- Preserved behavior: five Research endpoints, success/error status semantics, typed errors, exact freshness values, server-side request hashing, idempotent replay/conflict, expected-version conflict, concurrent refresh exclusion, append-only history, and real DB persistence.
- Regression gaps: none within the R2 contract. Browser/UI behavior was not applicable.

## Repair Required

- `NO`
- Repair ID: none
- Failed AC/Gate: none

## Final Decision Rationale

`PASS`. The exact prior failure is now closed by implementation, generated-contract evidence, endpoint-specific runtime counterexamples, and regression tests that would fail against the former single-`$ref` schema. All previously passed parent behaviors were independently re-verified.

## Next Action

Close `TASK-WP03-02` and dispatch `TASK-WP03-03`: establish a deterministic OpenAPI-generated TypeScript API client and drift check, preserving existing frontend behavior and excluding Research UI implementation.
