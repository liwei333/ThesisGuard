# ACCEPTANCE REPORT

**OVERALL: FAIL**

## Metadata

- Task ID: `TASK-WP03-03`
- Date: `2026-09-13` (`Asia/Shanghai`)
- Verifier: Codex, independent `ai-task-governor` VERIFIER run
- Report Path: `docs/acceptance/TASK-WP03-03-acceptance.md`
- Report Path Basis: the project already uses `docs/acceptance/` for WP03 formal acceptance reports.
- Implementation Status: executor reported `IMPLEMENTATION_COMPLETE`; independent verification completed.
- Implementation Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp03-research-package`
- Branch: `codex/wp03-research-package`
- HEAD / Baseline Commit: `d9bceedf27d80c84472613868b97d7b172cacfd6`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`; supplementary backend/API/DB regressions also passed.
- Missing Acceptance: `L3_CONTRACT_VERIFIED`
- Overall Verdict: `FAIL`
- Repair Required: `YES`
- Repair Task: `TASK-WP03-03-R1`
- Next Action: repair the generated client's typed error channel and restore the `apiClient`/error-logging compatibility contract before any WP03 follow-on work.

## Executive Decision

The implementation successfully establishes deterministic OpenAPI export, generated artifacts, five callable Research operations, required idempotency headers, a non-mutating drift gate, valid base-URL composition, and green build/regression commands. Those results are real and independently reproduced.

The task nevertheless fails two Blocking contracts:

1. The generated callable client does not preserve the declared Research error response types. `ResearchService` returns typed success values, but generated failures are thrown as `ApiError` whose `body` is `any`. The compile-time smoke test manually constructs `ResearchErrorResponse | HTTPValidationError`; it is detached from the generated operation/error signature and therefore cannot prove that a real failed call has that type.
2. The public `apiClient` compatibility export changed from `AxiosInstance` to `OpenAPIConfig`. In addition, generated HTTP failures are `ApiError`, while the wrapper reads status only from `AxiosError`; consequently generated 4xx/5xx failures are logged with an undefined status instead of preserving the former status-aware behavior.

These are public frontend boundary and contract-proof failures, not cosmetic findings. Passing drift, typecheck, build, and regression tests cannot override them because the current tests do not assert the failed properties.

## Changed Files Snapshot

### Inherited accepted WP03 changes

The following cumulative worktree changes predate this task and were accepted under WP03-01/WP03-02-R2:

- `apps/api/main.py`
- `backend/common/db/models_registry.py`
- `backend/research/api.py`
- `backend/research/models.py`
- `backend/research/schemas.py`
- `backend/research/services.py`
- `docs/WP03_RESEARCH_PACKAGE_API.md` (subsequently updated by this task)
- `docs/WP03_RESEARCH_PACKAGE_PERSISTENCE.md`
- `migrations/versions/20260912_003_research_package.py`
- `tests/test_research_api.py`
- `tests/test_research_persistence.py`

### Task-attributable WP03-03 surface

- `.env.example`
- `Makefile`
- `apps/web/env.d.ts`
- `apps/web/package.json`
- `apps/web/package-lock.json`
- `apps/web/openapi.json`
- `apps/web/scripts/openapi-tools.mjs`
- `apps/web/scripts/generate-api-client.mjs`
- `apps/web/scripts/check-api-drift.mjs`
- `apps/web/scripts/hash-api-artifacts.mjs`
- `apps/web/src/api/client.ts`
- `apps/web/src/api/generated-client-smoke.ts`
- `apps/web/src/api/generated/**` (32 generated TypeScript files)
- `docker-compose.yml`
- `docs/WP03_RESEARCH_PACKAGE_CLIENT.md`
- task-attributable updates in `docs/WP03_RESEARCH_PACKAGE_API.md`
- `tests/test_frontend_openapi_client.py`

Attribution: `CERTAIN` for the frontend/generation surface; cumulative backend changes were treated as inherited baseline, not newly credited to WP03-03.

Relevant SHA-256 snapshot:

- `apps/web/openapi.json`: `821bfd18cf0b96a86d208a4b14848789b6847405fc345af3d7b156814b9b754b`
- `apps/web/package.json`: `b02fbc6ad55673788833ee1fdf5d5bdbb955834a4f6b05840afd853e8bd6e9be`
- `apps/web/package-lock.json`: `8d985cf3181fddd0bcd3dc0be38b39e304d8c474ae2a0b20c45a3a798f2d42ed`
- `apps/web/src/api/client.ts`: `a6e5735871aa034063d88b3ce4804146557bcd2bfd419be1550f3f85a64b68de`
- `apps/web/src/api/generated-client-smoke.ts`: `15f119628a0ca433d57ed44da8e5684a477aa6b4b048b7b6b88d33705f71420e`
- `apps/web/src/api/generated/core/ApiError.ts`: `ac1abaa5a3ad075d93628d6c832ec50267580258b3a1b433a14594cbda31e425`
- `apps/web/src/api/generated/services/ResearchService.ts`: `6562fd45033c8806fa456b0fdf0966edb2e227541623b1972e49e5e1deb6149a`
- `tests/test_frontend_openapi_client.py`: `6505c0f8b01e95a7861b6d6e2dc97a2e4fef9a76cfc960ca7ec6bf74d4f3791b`

## Classification

- Task Type: `FRONTEND_API_CONTRACT` + `OPENAPI_CODEGEN` + `BUILD_GATE`
- Risk Type: API schema drift, generated-client type safety, public façade compatibility, runtime error observability
- Touched Layers: FastAPI OpenAPI artifact, Node code-generation scripts, generated TypeScript client/core/models/services, frontend façade, npm/Make gates, environment configuration, tests, documentation
- Task Size: `MEDIUM`
- Evidence Matrix Type: `Full` because the client is a critical cross-layer contract and exposes Research mutation/error behavior.
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, G5 Regression, G6 Evidence
- Not Applicable Gates: browser/UI rendering, worker/queue, external provider, permission/tenant/DataScope; no new DB behavior was requested.

## Top Blocking AC Results

| Top AC | Result | Evidence |
|---|---|---|
| TOP-AC-01 — deterministic live OpenAPI export and generated artifact workflow | PASS | `api:check` passed; canonical artifact matched `create_app().openapi()`; two independent artifact hashes were identical: `1f68386a...2e81`. |
| TOP-AC-02 — generated Research client preserves all five operations, required headers, success and endpoint-specific error contracts without `any` degradation | **FAIL** | Five operations and headers exist, but `generated/core/ApiError.ts:12` declares `body: any`; service methods expose only success returns and string error labels. Independent type probe rejected the required non-`any` assertion. |
| TOP-AC-03 — non-mutating drift gate is wired and fails on negative drift | PASS | Normal `npm run api:check` passed; injected temporary drift exited `1` with `generated client file list differs`; official artifacts remained unchanged. |
| TOP-AC-04 — thin façade preserves existing exports, timeout/error logging, base URL behavior, and avoids handwritten URLs/models | **FAIL** | Business URLs/models are generated and base URL is valid, but `client.ts:179` exports `OpenAPIConfig` as `apiClient` instead of the prior `AxiosInstance`; generated `ApiError` is not recognized by the Axios-only status logging at `client.ts:47-49`. |
| TOP-AC-05 — tests provide direct compile/runtime proof for the claimed contract and regressions stay green | **FAIL** | All current tests/builds pass, but `generated-client-smoke.ts:45-105` constructs a detached union and never proves the type of a real operation failure; no test asserts `apiClient` compatibility or generated `ApiError.status` logging. The verifier's counterexample catches both omissions. |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Correct isolated worktree, branch, baseline HEAD, cumulative status, prior acceptance reports, and task-attributable files were inspected. |
| G1 Scope | PASS | Changes are confined to the OpenAPI/client/gate/docs/test slice plus the required version-prefix configuration removal. The unrelated `.env.example` wording edit is minor and should be reverted in R1. |
| G2 Contract | **FAIL** | Canonical OpenAPI is accurate, but the TypeScript failure channel erases the response schema to `any`; the required contract is not preserved at the callable client/application boundary. |
| G3 Architecture | **FAIL** | Generated paths/models are correctly owned, but a configuration object is presented as the former raw client and generated errors bypass status-aware logging. This violates the compatibility façade boundary. |
| G4 Test | **FAIL** | Six focused contract tests pass, yet the test suite gives a false-positive on typed error preservation and does not cover raw-client compatibility/status logging. Test adequacy for Blocking ACs is insufficient. |
| G5 Regression | PASS | Frontend typecheck/lint/build, Research API/persistence, backend lint/typecheck, Compose, and the full 63-test suite passed. |
| G6 Evidence | **FAIL** | Executor evidence claimed the required generated error contract, but direct type evidence disproves it. Full Evidence Matrix cannot close with contradictory Blocking evidence. |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary / Negative Evidence | Verdict |
|---|---|---|---|---|---|
| WP03-03-AC-01 [BLOCKING] | Canonical artifact comes from current `create_app().openapi()` | `openapi-tools.mjs` exports and canonicalizes live schema | Focused Python test and `api:check` passed | No remote/copy-only source observed | PASS |
| WP03-03-AC-02 [BLOCKING] | Generation is deterministic and official artifacts are reviewable | committed `openapi.json`, generated directory, hash script | repeated hash `1f68386a...2e81`; 32 generated TS files | negative temp drift did not overwrite official output | PASS |
| WP03-03-AC-03 [BLOCKING] | Five Research operations and required mutation headers are generated | `ResearchService.ts` has list/create/current/refresh/version and required `idempotencyKey` inputs | typecheck and existing smoke passed | missing-header `@ts-expect-error` checks are tied to actual operation parameter types | PASS |
| WP03-03-AC-04 [BLOCKING] | Research success/error/freshness contracts survive generation without broad types | model files exist; OpenAPI has exact response schemas | OpenAPI schema assertions pass | `ApiError.body` is `any`; a verifier assertion that it must not be `any` failed with TS2344 | **FAIL** |
| WP03-03-AC-05 [BLOCKING] | Existing façade exports remain source/type compatible | old function/type names are preserved through aliases/wrappers | current Vue typecheck/build pass | verifier assignment `const compatible: AxiosInstance = apiClient` failed with TS2740 because export is `OpenAPIConfig` | **FAIL** |
| WP03-03-AC-06 [BLOCKING] | 30-second timeout and error logging behavior remain equivalent | `axios.defaults.timeout = 30000`; wrapper logs/rethrows | static inspection confirms timeout and rethrow | generated core throws `ApiError`; wrapper reads status only when `axios.isAxiosError(error)`, so generated HTTP error status is logged as `undefined` | **FAIL** |
| WP03-03-AC-07 [BLOCKING] | No handwritten business URLs or duplicate OpenAPI schemas in façade | generated services/models; thin manual wrapper | focused static test passed | no business URL literal or duplicate model interface found in `client.ts` | PASS |
| WP03-03-AC-08 [BLOCKING] | Drift check is non-mutating, wired into npm/Make, and fails on mismatch | `api:generate`, `api:check`, Make targets and temp comparison | normal check passed; injected drift exited 1 | no temp generated directory remained; official status unchanged | PASS |
| WP03-03-AC-09 [BLOCKING] | Base URL cannot produce `/api/v1/api/v1` | generated paths own `/api/v1`; version env removed | focused test and build passed | empty/origin/trailing-slash cases covered | PASS |
| WP03-03-AC-10 [BLOCKING] | Tests prove, rather than merely mention, required generated contracts | Python and TypeScript smoke modules exist | current suites pass | detached manual error union compiles independently of `ApiError.body`; no compatibility/logging counterexample existed | **FAIL** |

### Acceptance Level Evidence

- `L1_STATIC_REVIEWED`: achieved. Scripts, manifests, generated code, canonical OpenAPI, façade, tests, docs, diffs, and previous client implementation were inspected.
- `L2_BUILD_VERIFIED`: achieved. Frontend typecheck, non-fixing ESLint invocation, production build, backend lint/typecheck, Compose validation, and diff integrity passed.
- `L3_CONTRACT_VERIFIED`: **not achieved**. OpenAPI schema is correct, but generated/application TypeScript error contracts and compatibility export do not satisfy the task.
- Supplementary regression: Research API and persistence tests passed against the existing real test setup; these do not cure the frontend L3 failure.

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| `git status --short --branch` | PASS | Confirm branch and cumulative dirty baseline |
| `git rev-parse HEAD` | PASS — `d9bceedf...` | Confirm baseline commit |
| `git worktree list --porcelain` | PASS | Confirm main and isolated WP03 worktrees |
| `git diff --check` | PASS | Diff integrity |
| `cd apps/web && npm run api:check` | PASS | Fresh non-mutating live OpenAPI/generated-client drift check |
| `cd apps/web && npm run typecheck` | PASS | Normal project TypeScript check |
| `cd apps/web && npm exec eslint -- . --ext .vue,.ts,.tsx` | PASS | Non-fixing ESLint check |
| `cd apps/web && npm run build` | PASS | Production frontend build |
| `pytest -q tests/test_frontend_openapi_client.py -rs` | PASS — `6 passed, 2 warnings` | Existing focused client-generation tests |
| `pytest -q tests/test_research_api.py tests/test_research_persistence.py -rs` | PASS — `16 passed, 4 warnings` | Parent WP03 API/DB regression |
| `pytest -q -rs` | PASS — `63 passed, 4 warnings` | Full regression |
| `make lint` | PASS — `All checks passed!` | Ruff |
| `make typecheck` | PASS — 46 source files | Mypy |
| `docker compose config --quiet` | PASS | Compose validity |
| `cd apps/web && npm run api:hash` twice | PASS — same `1f68386a...2e81` twice | Deterministic official artifact content |
| `THESISGUARD_API_CHECK_INJECT_DRIFT=1 npm run api:check` | EXPECTED FAIL — exit `1` | Negative drift proof |
| Independent temporary TypeScript contract probe | EXPECTED CONTRACT FAILURE — exit `2`, TS2740 + TS2344 | Prove `apiClient` is not `AxiosInstance` and `ApiError.body` is `any` |

An initial frontend command batch was mistakenly invoked from the repository root and reported missing npm scripts; it was rejected as evidence and rerun from `apps/web`, where all normal frontend commands passed. No repository source file was changed by that procedural retry.

The four project warnings are existing framework deprecations involving Starlette TestClient, AnyIO's BlockingPortal alias, and `HTTP_422_UNPROCESSABLE_ENTITY`. They are unrelated to this verdict.

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| A generated operation advertises models but throws an untyped body | Yes | `ResearchService` uses textual `errors`; `ApiError.body: any`; `IsAny<ApiError['body']>` evaluates to `true` | **FAIL** |
| A detached smoke union creates false confidence | Yes | smoke accepts manually imported union literals but never derives an error type from a service/facade signature | **FAIL** |
| Existing `apiClient` consumers retain type compatibility | Yes | independent `AxiosInstance = apiClient` probe fails with missing Axios methods | **FAIL** |
| Generated HTTP errors preserve status logging | Yes | generated core throws `ApiError`; Axios-only guard does not read its `.status` | **FAIL** |
| Missing idempotency header remains a compile-time error | Yes | smoke derives actual operation parameter type and expected TS error is consumed | PASS |
| Invalid freshness remains rejected | Yes | exact generated enum and `@ts-expect-error` compile proof | PASS |
| Canonical/generated drift is detected without source mutation | Yes | injected temp file caused exit 1; official artifacts/hash/status stayed stable | PASS |
| `/api/v1` is duplicated | Yes | config and focused test cover empty/base/trailing slash cases | PASS |

## Blocking Findings

### B-01 — Required Research error types are erased at the callable boundary

- Location: `apps/web/src/api/generated/core/ApiError.ts:8-23`
- Related service: `apps/web/src/api/generated/services/ResearchService.ts:39-63`, `94-122`, `130-148`
- Test gap: `apps/web/src/api/generated-client-smoke.ts:45-105`
- Severity: Blocking
- Failed AC/Gates: TOP-AC-02, TOP-AC-05, G2, G4, G6
- Direct evidence: `ApiError.body` is `any`; generated service methods do not associate 404/409/422 with `ResearchErrorResponse` or `HTTPValidationError`. The verifier's type-level non-`any` assertion failed.
- Why current tests are insufficient: they prove only that generated model files can be manually unioned, not that a failed generated request exposes that union.
- Required repair: expose an actual generated or generated-backed, endpoint-accurate typed failure contract using the generated schema models; no handwritten duplicate DTOs and no `any`/unconstrained `unknown`/string substitution.

### B-02 — `apiClient` and status-aware error logging regress compatibility

- Location: `apps/web/src/api/client.ts:40-49`, `179`
- Generated throw path: `apps/web/src/api/generated/core/request.ts:252-320`
- Severity: Blocking
- Failed AC/Gates: TOP-AC-04, TOP-AC-05, G3, G4, G6
- Direct evidence: exported `apiClient` is `OpenAPIConfig`, not `AxiosInstance`; generated errors are `ApiError`, not Axios errors, so `.status` is ignored by the logging wrapper.
- Required repair: preserve a genuinely type-compatible raw client export (or a replacement explicitly allowed by the original contract without reusing the name incompatibly), and make generated failures log their real HTTP status while rethrowing the original error.

## Non-Blocking Findings

1. `apps/web/package.json` declares `openapi-typescript-codegen` as `^0.29.0`, although the lockfile resolves `0.29.0`. R1 should use an exact direct version if the generator is retained, so “pinned” is true in both manifest and lockfile.
2. `.env.example` changes the unrelated comment `External Services (placeholder for future WPs)` to `External Services (future WPs)`. Revert this wording-only scope noise in R1 while keeping the required `VITE_API_VERSION` removal.
3. The recurring npm “Unknown user config” warnings come from the local npm environment, not repository implementation. They do not affect this verdict.

## Regression Result

- Result: `PASS`
- Preserved behavior: canonical OpenAPI equality, deterministic artifacts, five generated Research methods, required mutation headers, exact freshness enum, base URL composition, normal frontend build, parent Research API/persistence behavior, and the full project suite.
- Contract gaps: typed failed-response channel, raw-client export compatibility, generated-error status logging, and tests capable of detecting those regressions.

## Repair Required

- `YES`
- Repair ID: `TASK-WP03-03-R1`
- Failed AC/Gates: WP03-03-AC-04, AC-05, AC-06, AC-10; G2, G3, G4, G6
- Repair policy: repair only these failed/weak contracts and their tests/docs; preserve all passed deterministic generation, drift, base URL, five-operation, idempotency, backend API, DB, and regression behavior.

## Final Decision Rationale

`FAIL`. The implementation is close and operationally green, but this task was explicitly about a generated contract boundary. The actual error path remains untyped and the public raw-client export is not compatible with what it replaces. The verifier produced compile-time counterexamples for both. Under the Full Evidence Matrix, any Blocking contract failure requires repair before closure, regardless of the number of green generic tests.

## Next Action

Dispatch `TASK-WP03-03-R1`. Do not begin Research UI or another WP03 work package until R1 receives an independent PASS.
