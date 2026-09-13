# ACCEPTANCE REPORT

**OVERALL: FAIL**

## Metadata

- Task ID: `TASK-WP03-02`
- Date: `2026-09-13` (`Asia/Shanghai`)
- Verifier: Codex, independent `ai-task-governor` VERIFIER run
- Report Path: `docs/acceptance/TASK-WP03-02-acceptance.md`
- Report Path Basis: `docs/acceptance/` was established by the prior formal acceptance.
- Implementation Status: executor reported `IMPLEMENTATION_COMPLETE`; independent verification found an incomplete public OpenAPI contract.
- Implementation Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp03-research-package`
- Branch: `codex/wp03-research-package`
- Baseline Commit: `d9bceedf27d80c84472613868b97d7b172cacfd6`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_RUNTIME_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L4_RUNTIME_VERIFIED`, `L4_DB_VERIFIED`
- Missing Acceptance: `L3_CONTRACT_VERIFIED` — the declared error and freshness contracts are not represented by restrictive Pydantic/OpenAPI schemas.
- Overall Verdict: `FAIL`
- Repair Required: `YES`
- Repair ID: `TASK-WP03-02-R1`
- Next Action: repair the public response/OpenAPI schemas and add regression assertions; do not start `TASK-WP03-03`.

## Changed Files Snapshot

- `BASELINE_CHANGED_FILES` inherited from accepted `TASK-WP03-01`:
  - `backend/common/db/models_registry.py`
  - `backend/research/models.py`
  - `backend/research/schemas.py`
  - `backend/research/services.py`
  - `docs/WP03_RESEARCH_PACKAGE_PERSISTENCE.md`
  - `migrations/versions/20260912_003_research_package.py`
  - `tests/test_research_persistence.py`
- Hash comparison against the prior verifier snapshot confirmed that `models.py`, `services.py`, the migration, persistence documentation, and persistence tests remained unchanged. `schemas.py` was intentionally changed by this task.
- `FINAL_CHANGED_FILES`:
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
- Task-attributable `TASK-WP03-02` changes:
  - `apps/api/main.py`
  - `backend/research/api.py`
  - `backend/research/schemas.py`
  - `tests/test_research_api.py`
  - `docs/WP03_RESEARCH_PACKAGE_API.md`
- Attribution: `CERTAIN`

## Classification

- Task Type: `BACKEND_API + DB_PERSISTENCE`
- Risk Type: public API contract, OpenAPI/client generation, idempotency, concurrency, versioned DB writes, error information boundary
- Touched Layers: FastAPI router, Pydantic schema, domain service integration, AsyncSession dependency, PostgreSQL integration tests, OpenAPI, docs
- Task Size: `MEDIUM`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, DB Persistence, G5 Regression, G6 Evidence
- Not Applicable Gates: browser/UI, frontend generated client, worker/queue, external provider, permission/tenant/DataScope

## Top Blocking AC Results

| Top AC | Result | Evidence |
|---|---|---|
| TOP-AC-01 — five endpoints, Pydantic request/response contracts, and complete OpenAPI response structures | **FAIL** | Five routes and success schemas exist, but `backend/research/api.py:166-283` declares 404/409/422 responses with descriptions only. Actual OpenAPI showed no `content`/schema for 404 or 409. `ResearchModuleRead.freshness` is plain `str`, so OpenAPI permits any string instead of the required four values. |
| TOP-AC-02 — server-side canonical request hashing and HTTP idempotency | PASS | `backend/research/api.py:39-90`; real API tests proved required header, normalized module ordering, cross-operation conflict, same-key replay, and different-request conflict. |
| TOP-AC-03 — stable HTTP error semantics represented by API contracts | **FAIL** | Runtime error bodies/status codes pass, but errors are constructed as untyped dictionaries in `research_http_exception` and no Pydantic error response model appears in OpenAPI. This violates the explicit requirement that requests/responses use Pydantic v2 schemas and that response structure be visible in OpenAPI. |
| TOP-AC-04 — real ASGI-to-PostgreSQL behavior | PASS | Fresh verifier run: `tests/test_research_api.py` reported `8 passed, 0 skipped`; real AsyncClient/ASGITransport, actual app/router/service, Alembic-migrated PostgreSQL, concurrent refresh, and new-client/session persistence were exercised. |
| TOP-AC-05 — quality and regression gates | PASS | `make lint`, `make typecheck`, Compose config, WP03-01 persistence suite, WP03-02 API suite, and full 57-test regression all passed. |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Prior acceptance report, baseline commit, worktree status, cumulative diff, and file hashes were inspected; task attribution is certain. |
| G1 Scope | PASS | Only router registration, Research API/schema/tests/docs changed beyond the accepted WP03-01 baseline. No migration, model, dependency, frontend, worker, Evidence, Thesis, or Agent expansion occurred. |
| G2 Contract | **FAIL** | Blocking OpenAPI/Pydantic response requirements are not satisfied. |
| G3 Architecture | **FAIL** | The runtime error mapper bypasses the declared typed public contract boundary by emitting raw dictionaries while OpenAPI documents only descriptions. This would generate an incomplete client contract. |
| G4 Test | **FAIL** | All existing tests pass, but the OpenAPI test only checks paths, success schemas, and header presence. It does not enforce error response schemas or the exact freshness enum; an explicit verifier assertion failed. |
| DB Persistence | PASS | Real PostgreSQL API and persistence suites passed with no skips; current/history/version/concurrency/idempotency semantics remain intact. |
| G5 Regression | PASS | Full suite: `57 passed, 2 warnings`; accepted WP03-01 suite remained `8 passed`. |
| G6 Evidence | **FAIL** | Fresh evidence proves a Blocking contract gap. Passing runtime tests cannot override the missing OpenAPI/Pydantic contract. |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary/Negative Evidence | Verdict |
|---|---|---|---|---|---|
| TOP-AC-01 [BLOCKING] | Complete typed HTTP/OpenAPI contract | Five router functions, public success schemas, router registration | Actual `app.openapi()` output contained all paths and success schemas | 404/409 responses had only `description`; `freshness` had `type: string` and no enum | FAIL |
| TOP-AC-02 [BLOCKING] | Server-derived request hash and safe idempotency | `build_request_hash`, `build_initial_request_hash`, `build_refresh_request_hash`, header dependency | Focused real API suite passed | Missing/blank/long header, reordered modules, same/different semantic request, and cross-operation reuse were checked | PASS |
| TOP-AC-03 [BLOCKING] | Stable typed error envelope | Runtime `research_http_exception` mapping | Runtime tests observed the expected status/code values | No `ResearchErrorResponse`/equivalent schema exists; clients cannot derive the promised envelope or version-conflict fields from OpenAPI | FAIL |
| TOP-AC-04 [BLOCKING] | Real API and DB path | AsyncClient + ASGITransport + actual app/router + real AsyncSession override | `8 passed` API tests and `8 passed` persistence tests | Concurrent requests produced one 201 and one 409; a fresh client/session read persisted rows | PASS |
| TOP-AC-05 [BLOCKING] | Quality and regression | New API tests and unchanged project commands | lint/typecheck/Compose/focused/full test commands exited 0 | Temporary database count was 0; no test skips or generated artifacts were found | PASS |

### Acceptance Level Evidence

- Required: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_RUNTIME_VERIFIED`, `L4_DB_VERIFIED`
- Achieved:
  - `L1_STATIC_REVIEWED`
  - `L2_BUILD_VERIFIED`
  - `L4_RUNTIME_VERIFIED`
  - `L4_DB_VERIFIED`
- Missing:
  - `L3_CONTRACT_VERIFIED` because the public error and freshness contracts are broader/absent in generated OpenAPI.

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| `git status --short --branch`, `git worktree list --porcelain`, `git rev-parse HEAD`, `git merge-base ...` | PASS | Baseline and attribution |
| SHA-256 comparison of accepted and current WP03 files | PASS | Separate WP03-01 baseline from WP03-02 changes |
| `git diff --check` | PASS | Diff integrity |
| `make lint` | PASS — `All checks passed!` | Ruff |
| `make typecheck` | PASS — `46 source files` | Mypy |
| `docker compose config --quiet` | PASS | Compose validity |
| `pytest -q tests/test_research_api.py -rs` | PASS — `8 passed, 2 warnings`, zero skipped | Real API/PostgreSQL behavior |
| `pytest -q tests/test_research_persistence.py -rs` | PASS — `8 passed, 2 warnings`, zero skipped | Preserve WP03-01 |
| `pytest -q` | PASS — `57 passed, 2 warnings` | Full regression |
| Direct `create_app().openapi()` inspection | **FAIL contract check** — 404/409 have descriptions only; freshness is unrestricted string | Inspect generated public contract |
| Explicit OpenAPI assertion command | **Exit 1** — `error_responses_typed=False`, `freshness_enum_exact=False` | Reproduce Blocking gap |
| PostgreSQL temporary DB query | PASS — `0` | Cleanup verification |

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| Missing/blank/long idempotency header | Yes | Real API tests return 422 | PASS |
| Same key, same semantic request reordered | Yes | Same package returned | PASS |
| Same key, different request or operation | Yes | 409 `IDEMPOTENCY_CONFLICT` | PASS |
| Stale expected version | Yes | 409 with expected/current values | PASS |
| Two concurrent refreshes | Yes | One 201, one 409; history `[1, 2]` | PASS |
| Empty/duplicate/unknown modules and illegal read version | Yes | Real API tests return 422 | PASS |
| Persistence across new client/session | Yes | Same package read from PostgreSQL | PASS |
| Internal request hash exposure | Yes | Absent from runtime response and success schema | PASS |
| Client generation from error contract | Yes | OpenAPI has no error response schema | **FAIL** |
| Client restriction to four freshness values | Yes | OpenAPI exposes unrestricted string | **FAIL** |

## DB Persistence Result

- Schema constraints: unchanged from accepted WP03-01.
- Read semantics: current, history, and specified version passed through HTTP and real PostgreSQL.
- Replace semantics: not applicable; append-only copy-on-write remains.
- Active/inactive/deleted/status: lifecycle/freshness runtime behavior is preserved.
- Transaction boundary: HTTP dependency commits/rolls back real AsyncSession operations.
- Version/snapshot/history: version 1 remains addressable after version 2; concurrent version 2 duplication is prevented.
- Real persistence vs InMemory/Fake/Mock: all L4 claims use Alembic-migrated PostgreSQL; no fake repository/service was accepted.

## Blocking Findings

1. **[TOP-AC-01 / G2 / G3] Error responses are not Pydantic/OpenAPI contracts.**
   - `backend/research/api.py:166-174`, `194-198`, `227-233`, and `255-263` declare error responses using descriptions only.
   - `backend/research/api.py:93-120` builds raw dictionary details for `HTTPException`.
   - Generated OpenAPI for initial-create 404 and 409 contains only `{"description": ...}`, with no response content/schema.
   - No Research error schema exists in `components.schemas`.

2. **[TOP-AC-01 / G2 / G4] Freshness is not restricted in the public schema.**
   - `backend/research/schemas.py:54-60` declares `freshness: str`.
   - Generated OpenAPI is `{"type":"string", ...}` with no enum.
   - The original contract requires only `UNVERIFIED / FRESH / STALE / FAILED`, especially because the next task is generated-client work.

3. **[TOP-AC-03 / G4 / G6] Tests do not guard these contract requirements.**
   - `tests/test_research_api.py:367-401` checks paths, header, success fields, and required request fields, but not error response models or exact freshness values.
   - Therefore all 57 tests can pass while the public contract remains incomplete.

## Non-Blocking Findings

1. The 11 module types are now duplicated across model constants, service constants, and a Pydantic enum. Consolidation may reduce drift but is outside this Repair and must not be mixed into it.
2. Existing FastAPI/Starlette deprecation warnings remain unchanged and are not caused by this task.

## Regression Result

- Result: `PASS`
- Preserved behavior: all 57 tests pass; WP03-01 persistence behavior and all earlier project tests remain intact.
- Regression gap: tests do not currently fail when OpenAPI error/freshness schemas regress.

## Repair Required

- `YES`
- Repair ID: `TASK-WP03-02-R1`
- Failed AC/Gate: TOP-AC-01, TOP-AC-03; G2 Contract, G3 Architecture, G4 Test, G6 Evidence

## Final Decision Rationale

`FAIL`. The real API and PostgreSQL behavior is strong and independently verified, but the task explicitly required typed Pydantic request/response contracts and visible OpenAPI response structures. Generated OpenAPI cannot describe the stable Research error envelope or constrain freshness to the promised four values. Because this is a Blocking public-contract requirement and the next planned task depends on OpenAPI client generation, passing runtime tests cannot justify PASS.

## Next Action

Execute only `TASK-WP03-02-R1`: add typed Research error/freshness schemas, attach the error models to all applicable OpenAPI responses, build runtime error payloads through those schemas, and add focused contract regression tests. Preserve all already-passing API, idempotency, concurrency, persistence, cleanup, and full-regression behavior. Re-run the complete verification workflow before considering `TASK-WP03-03`.
