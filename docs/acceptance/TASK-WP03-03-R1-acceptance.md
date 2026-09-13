# ACCEPTANCE REPORT

**OVERALL: FAIL**

## Metadata

- Task ID: `TASK-WP03-03-R1`
- Original Task: `TASK-WP03-03`
- Date: `2026-09-13` (`Asia/Shanghai`)
- Verifier: Codex, independent `ai-task-governor` VERIFIER run
- Report Path: `docs/acceptance/TASK-WP03-03-R1-acceptance.md`
- Report Path Basis: the project already uses `docs/acceptance/` for formal WP03 acceptance reports.
- Implementation Status: executor reported `IMPLEMENTATION_COMPLETE`; independent verification completed.
- Implementation Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp03-research-package`
- Branch: `codex/wp03-research-package`
- HEAD / Baseline Commit: `d9bceedf27d80c84472613868b97d7b172cacfd6`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`; positive transport/runtime and parent regression evidence also passed.
- Missing Acceptance: `L3_CONTRACT_VERIFIED`
- Overall Verdict: `FAIL`
- Repair Required: `YES`
- Repair Task: `TASK-WP03-03-R2`
- Next Action: repair only the unsound Research error-body runtime guards and add counterexample tests before any later WP03 task.

## Executive Decision

R1 successfully closes most of the original failure:

- `ApiError` and `ApiResult` are generic and no longer erase their complete body to `any`;
- Research façade calls expose generated-model-backed endpoint/status error mappings;
- `apiClient` is again a real `AxiosInstance`;
- generated requests use that same instance through `OpenAPI.AXIOS`;
- a real generated 409 path uses the expected URL, 30-second timeout, logs status `409`, rethrows, and can be narrowed;
- the generator is exactly pinned to `0.29.0` and the deterministic generation/drift/build/regression gates pass.

The task still fails because the exported runtime guards that turn `unknown` into `ResearchErrorResponse` or `HTTPValidationError` are unsound. Independent executable counterexamples show that they accept bodies which do not satisfy the generated models:

- an unknown Research error code is accepted;
- string `expected_version` / `current_version` fields are accepted;
- a validation location containing an object is accepted even though generated `loc` permits only strings or numbers.

The guard also rejects `{}`, even though the generated `HTTPValidationError` declares `detail` optional. The current focused tests exercise status logging but do not exercise these public narrowing functions with malformed or schema-boundary inputs. Since runtime guarding is the bridge from the generated core's `unknown` body to the typed Research error contract, false-positive narrowing is a Blocking contract defect.

## Changed Files Snapshot

### BASELINE_CHANGED_FILES

The isolated worktree already contained cumulative accepted WP03-01/WP03-02 changes and the failed WP03-03 implementation. The prior acceptance snapshot is recorded in:

- `docs/acceptance/TASK-WP03-03-acceptance.md`

### Task-attributable R1 changes

- `.env.example`
- `apps/web/package.json`
- `apps/web/package-lock.json`
- `apps/web/scripts/openapi-tools.mjs`
- `apps/web/src/api/client.ts`
- `apps/web/src/api/generated-client-smoke.ts`
- generated changes under `apps/web/src/api/generated/core/`
- `apps/web/src/api/generated/index.ts`
- `tests/test_frontend_openapi_client.py`
- `docs/WP03_RESEARCH_PACKAGE_CLIENT.md`
- task-related documentation update in `docs/WP03_RESEARCH_PACKAGE_API.md`
- regenerated `apps/web/openapi.json` and generated-client output

### FINAL_CHANGED_FILES

- `M .env.example`
- `M Makefile`
- `M apps/api/main.py`
- `M apps/web/env.d.ts`
- `M apps/web/package-lock.json`
- `M apps/web/package.json`
- `M apps/web/src/api/client.ts`
- `M backend/common/db/models_registry.py`
- `M docker-compose.yml`
- `?? apps/web/openapi.json`
- `?? apps/web/scripts/`
- `?? apps/web/src/api/generated-client-smoke.ts`
- `?? apps/web/src/api/generated/`
- `?? backend/research/`
- `?? docs/WP03_RESEARCH_PACKAGE_API.md`
- `?? docs/WP03_RESEARCH_PACKAGE_CLIENT.md`
- `?? docs/WP03_RESEARCH_PACKAGE_PERSISTENCE.md`
- `?? migrations/versions/20260912_003_research_package.py`
- `?? tests/test_frontend_openapi_client.py`
- `?? tests/test_research_api.py`
- `?? tests/test_research_persistence.py`

Attribution: `CERTAIN` for the R1 frontend/client repair surface. Backend, migration, and Research API/persistence files remain inherited cumulative changes.

Relevant final SHA-256 snapshot:

- `apps/web/openapi.json`: `821bfd18cf0b96a86d208a4b14848789b6847405fc345af3d7b156814b9b754b`
- `apps/web/package.json`: `6244dc43c384a67b9674d56f95dcf0fc97c4b92f01be733d2e72194ebb521f67`
- `apps/web/package-lock.json`: `8e49c8dbf9fbab71933d5c978a896115466babff4d431b58e07727f773ca6944`
- `apps/web/scripts/openapi-tools.mjs`: `acdbe2bc6af86614a196d3a56e779b77c2f99442eff73fd02937524f17e6ce61`
- `apps/web/src/api/client.ts`: `41b1c64e0e0b052af6b1d69e6a9b871475d9c7e4cac2a2e164f50ee80de9cc38`
- `apps/web/src/api/generated-client-smoke.ts`: `360aa64b20636c67f4f8e0005451760d466f0de24c50334845243cc77071a4c9`
- `apps/web/src/api/generated/core/ApiError.ts`: `e047b9722dcb2a60b8272adcf3569469f659dbd01547a34aee72d30baa7f9ff8`
- `apps/web/src/api/generated/core/request.ts`: `b07777a7654e89e2c12f4536204f8ae31b4542bfd7910c8bdd5cf91bb5ce795f`
- `tests/test_frontend_openapi_client.py`: `78150a9fed170452ad904ef7b6758fa405b89dc95786aeb84aaea1463bca6c3a`

## Classification

- Task Type: `REPAIR` + `FRONTEND_API_CONTRACT`
- Risk Type: unsafe runtime type narrowing, generated-client contract accuracy, façade compatibility, regression of deterministic code generation
- Touched Layers: generated TypeScript core, frontend API façade, compile-time smoke, Node runtime probe, generation script, package lock, documentation, Python contract tests
- Task Size: `MEDIUM`
- Evidence Matrix Type: `Full` because this is a critical API error boundary.
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, G5 Regression, G6 Evidence
- Not Applicable Gates: DB Persistence, browser/UI, worker/queue, external provider, permissions/tenant/DataScope

## Top Blocking AC Results

| Top AC | Result | Evidence |
|---|---|---|
| TOP-AC-01 — actual Research error channel is generated-model-backed, non-`any`, endpoint/status accurate, and safely narrowed at runtime | **FAIL** | Static types and positive narrowing exist, but verifier runtime counterexamples showed three false positives and one schema-boundary false negative in `client.ts:105-142`. |
| TOP-AC-02 — `apiClient` remains an actual compatible Axios transport used by generated requests with correct timeout/base URL | PASS | Independent compile probe assigned it to `AxiosInstance`; real adapter probe observed one call, `/api/v1/research/.../packages`, and timeout `30000`. |
| TOP-AC-03 — generated and Axios errors retain real status logging and propagation | PASS | Real generated 409 path logged `409`, rethrew the same generated error, and narrowed correctly. Existing focused logging test also passed. |
| TOP-AC-04 — deterministic generation, exact dependency pin, canonical OpenAPI, and positive/negative drift gates remain intact | PASS | `npm ci`, normal `api:check`, exact `0.29.0`, repeated hash `985634...3492`, injected drift exit `1`, and post-injection normal check exit `0`. |
| TOP-AC-05 — tests directly prevent recurrence of all repaired Blocking behavior while full regression stays green | **FAIL** | 8 focused and 65 full tests pass, but none invokes the public guard with invalid enum/version/loc bodies; current suite therefore misses the Blocking false-positive narrowing behavior. |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Correct worktree, branch, HEAD, cumulative status, previous FAIL report, implementation diff, and final hashes were independently inspected. |
| G1 Scope | PASS | R1 changes are concentrated in the generated-client/error/transport/test/documentation repair; no backend business, migration, UI, Evidence, Thesis, Agent, or dependency upgrade drift was found. |
| G2 Contract | **FAIL** | Exported type predicates claim generated model types for malformed bodies. The runtime error contract is therefore not trustworthy. |
| G3 Architecture | PASS | Generated core owns unknown transport bodies; the façade owns endpoint/status mapping and runtime narrowing; public Axios transport and generated request runtime are connected through one instance. |
| G4 Test | **FAIL** | Existing tests prove positive transport/logging/type behavior but omit malformed-body and schema-boundary guard cases. A verifier-created executable probe disproved the claimed guard safety. |
| DB Persistence | NOT_APPLICABLE | R1 does not change DB schema, ORM, service transaction, or persistence semantics. Parent DB/API behavior is covered by the full regression only. |
| G5 Regression | PASS | Frontend typecheck/lint/build, focused suite `8 passed`, full suite `65 passed`, Ruff, mypy, Compose, and diff integrity all passed. |
| G6 Evidence | **FAIL** | Executor evidence states there are no unresolved R1 items, but fresh counterexample evidence contradicts that claim for the core narrowing boundary. |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary / Negative Evidence | Verdict |
|---|---|---|---|---|---|
| R1-AC-01 [BLOCKING] | Generated core body is not `any` | generic `ApiError<TBody = unknown>` and `ApiResult<TBody = unknown>` generated by deterministic patch | verifier type probe compiled; `IsAny<ApiError['body']>` is false | transport stays `unknown` until façade guard | PASS |
| R1-AC-02 [BLOCKING] | Endpoint/status Research errors use generated models | `ResearchErrorContract`, `ResearchApiErrorBodyForStatus`, `ResearchApiPromise` | compile-time type probe derived create error body from the actual façade return and accepted both generated error alternatives | mapping is manually maintained but generated-model-backed as permitted by the Repair Contract | PASS |
| R1-AC-03 [BLOCKING] | Unknown transport body is safely narrowed before model use | `isResearchApiErrorForStatus`, `isResearchApiError`, body guard helpers | valid real 409 error narrowed successfully | unknown code, invalid version field types, and invalid validation `loc` item all incorrectly narrowed | **FAIL** |
| R1-AC-04 [BLOCKING] | Runtime guard agrees with generated body schema boundary | `isHTTPValidationError` checks array detail and selected fields | normal FastAPI-style validation body is accepted | generated schema makes `detail` optional, yet `{}` is rejected; validation loc element types are not checked | **FAIL** |
| R1-AC-05 [BLOCKING] | `apiClient` remains a real AxiosInstance and is the generated request transport | `axios.create`, `OpenAPI.AXIOS`, patched request default | compile assignment passed; adapter probe observed exactly one request using the exported instance | no decorative/disconnected compatibility object | PASS |
| R1-AC-06 [BLOCKING] | Timeout/base URL remain correct | `apiClient` config plus generated path ownership | adapter probe saw timeout 30000 and exact `/api/v1/research/.../packages`; focused tests passed | no duplicate `/api/v1` in observed URL | PASS |
| R1-AC-07 [BLOCKING] | Generated HTTP status logs and error propagates | `reportApiErrorAndRethrow` handles Axios and generated error classes | real façade/generated 409 path logged `409`; focused executable probe passed | same error was propagated to the caller | PASS |
| R1-AC-08 [BLOCKING] | Dependency/generation/drift gates are reproducible | exact generator pin and deterministic post-generation patch | `npm ci`, `api:check`, two identical hashes, build/typecheck passed | injected drift exited 1; normal check then returned 0 | PASS |
| R1-AC-09 [BLOCKING] | Tests fail if public guard becomes unsound | compile smoke and status logging test | all current tests pass | independent invalid-body probe passes through guard, proving the suite cannot detect this regression | **FAIL** |
| R1-AC-10 [BLOCKING] | Parent functionality remains green | no backend behavior change attributable to R1 | full suite `65 passed`; Ruff/mypy/Compose passed | zero test skips reported | PASS |

### Acceptance Level Evidence

- `L1_STATIC_REVIEWED`: achieved. Repair files, generated patching, public façade, guards, tests, models, docs, Git attribution, and previous acceptance report were inspected.
- `L2_BUILD_VERIFIED`: achieved. `npm ci`, frontend typecheck/ESLint/build, Ruff, mypy, Compose, and diff integrity passed.
- `L3_CONTRACT_VERIFIED`: **not achieved** because public error-body type predicates are unsound and their negative contract is untested.
- `L4_RUNTIME_VERIFIED`: supplementary positive runtime evidence exists for actual generated transport, timeout, URL, status logging, propagation, and valid narrowing; negative runtime evidence is the reason for FAIL.

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| `git status --short --branch` | PASS | Confirm cumulative dirty baseline and branch |
| `git rev-parse HEAD` | PASS — `d9bceedf...` | Confirm baseline HEAD |
| `git worktree list --porcelain` | PASS | Confirm isolated worktree |
| `git diff --check` | PASS | Diff integrity |
| verifier TypeScript contract probe | PASS — exit `0` | Prove actual façade error phantom type is non-`any` and `apiClient` is `AxiosInstance` |
| verifier bundled runtime transport/guard probe | COMMAND PASS — exit `0`; CONTRACT COUNTEREXAMPLE FOUND | Exercise real façade/generated request and public guards |
| `npm ci` | PASS | Reinstall exact lockfile dependency graph |
| `npm run api:check` | PASS | Fresh generated/canonical drift gate |
| `npm run api:hash` twice | PASS — `985634bdb5ec3516883a666fc555525a7656480771d324aa08ef99c2a14b3492` twice | Deterministic artifact content |
| `npm run typecheck` | PASS | TypeScript/Vue compile check |
| `npm exec eslint -- . --ext .vue,.ts,.tsx` | PASS | Non-fixing frontend lint check |
| `npm run build` | PASS | Production frontend build |
| `THESISGUARD_API_CHECK_INJECT_DRIFT=1 npm run api:check` | EXPECTED FAIL — exit `1` | Negative drift proof |
| normal `npm run api:check` after negative probe | PASS | Prove official artifacts remained clean |
| `pytest -q tests/test_frontend_openapi_client.py -rs` | PASS — `8 passed, 2 warnings` | Existing focused generation/client contract suite |
| `pytest -q -rs` | PASS — `65 passed, 4 warnings`, no skips | Full project regression |
| `make lint` | PASS — `All checks passed!` | Ruff |
| `make typecheck` | PASS — 46 source files | Mypy |
| `docker compose config --quiet` | PASS | Compose validity |

## Counterexample / Negative Verification

The independent probe executed the actual bundled TypeScript façade and generated runtime. Positive results:

```json
{
  "transportCalls": 1,
  "observedUrl": "/api/v1/research/instruments/11111111-1111-4111-8111-111111111111/packages",
  "observedTimeout": 30000,
  "loggedStatus": 409,
  "actualCallNarrowed": true
}
```

Blocking counterexamples:

```json
{
  "invalidCodeAccepted": true,
  "invalidVersionFieldsAccepted": true,
  "invalidValidationLocationAccepted": true,
  "schemaValidEmptyValidationAccepted": false
}
```

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| Unknown Research code narrows to `ResearchErrorCode` | Yes | `NOT_A_RESEARCH_ERROR_CODE` returned `true` | **FAIL** |
| Invalid optional version fields narrow to numbers/null | Yes | string `expected_version` and `current_version` returned `true` | **FAIL** |
| Invalid validation location narrows to `(string | number)[]` | Yes | `loc: [{}]` returned `true` | **FAIL** |
| OpenAPI-permitted missing validation detail is recognized | Yes | `{}` at version 422 returned `false` | **FAIL** |
| Valid generated 409 uses common transport/logging/narrowing | Yes | one call, correct URL/timeout/status, valid guard | PASS |
| Negative generated drift is detected and cleaned | Yes | injected file-list drift exit 1; next normal check exit 0 | PASS |

## DB Persistence Result

`NOT_APPLICABLE` for this repair. The full suite ran the existing Research API/persistence paths without skips, but R1 made no DB change and no new L4 DB claim is needed.

## Blocking Findings

### B-01 — Public Research error type guards are unsound

- Location: `apps/web/src/api/client.ts:105-142`
- Public predicates: `apps/web/src/api/client.ts:152-179`
- Failed AC/Gates: TOP-AC-01, TOP-AC-05, R1-AC-03, R1-AC-04, R1-AC-09, G2, G4, G6
- Severity: Blocking
- Root cause:
  - `isResearchErrorResponse` checks that `detail.code` is a string, but not membership in generated `ResearchErrorCode`;
  - it does not validate `expected_version` or `current_version` when present;
  - `isHTTPValidationError` checks that `loc` is an array but not that every item is a string or number;
  - it requires `detail` to be an array even though the generated property is optional.
- Effect: an `unknown` response can be falsely claimed to be a generated model; downstream code may rely on enum/number/location types that are not actually present.
- Test gap: the runtime test checks only a valid 409 and logging. No malformed-body or optional-field boundary case invokes either public predicate.
- Required repair: make both body guards structurally sound against the generated schemas and add executable positive/negative tests using the public predicates.

## Non-Blocking Findings

1. The local npm environment emits numerous unknown-config warnings, and the current dependency graph emits known deprecation warnings. They do not change the contract verdict.
2. Existing framework deprecation warnings from Starlette TestClient, AnyIO, and `HTTP_422_UNPROCESSABLE_ENTITY` remain unrelated to R1.
3. The R1 automated generator patch is string-anchor based. Its fail-fast behavior and `api:check` currently make generator drift observable, so no additional repair is required in R2.

## Regression Result

- Result: `PASS`
- Preserved behavior: exact OpenAPI artifact, five Research operations, required idempotency headers, exact freshness enum, typed success models, non-`any` generated core, compatible Axios export, common transport, 30-second timeout, URL composition, status logging, deterministic generation, positive/negative drift, parent Research API/persistence, and full project tests.
- Regression gap: runtime guard soundness is not covered by the committed suite.

## Repair Required

- `YES`
- Repair ID: `TASK-WP03-03-R2`
- Failed AC/Gate: R1-AC-03, R1-AC-04, R1-AC-09; G2, G4, G6
- Repair policy: change only the Research error-body guards, their executable tests, and directly corresponding client documentation. Preserve every R1 item already proven PASS.

## Final Decision Rationale

`FAIL`. R1 fixes the original `any`, raw-client, transport, timeout, and logging problems, and the broad regression evidence is green. However, its exported type predicates are not safe: concrete malformed values are accepted as generated models. Because those predicates are the runtime justification for narrowing a transport `unknown` body, this is a direct failure of the repaired contract rather than an advisory validation preference.

## Next Action

Dispatch `TASK-WP03-03-R2` as a small, test-first Repair Contract. Do not begin Research UI or another WP03 feature until R2 receives an independent PASS.
