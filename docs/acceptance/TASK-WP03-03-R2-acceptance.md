# ACCEPTANCE REPORT

**OVERALL: PASS**

## Metadata

- Task ID: `TASK-WP03-03-R2`
- Original Task Chain: `TASK-WP03-03` → `TASK-WP03-03-R1` → `TASK-WP03-03-R2`
- Date: `2026-09-13` (`Asia/Shanghai`)
- Verifier: Codex, independent `ai-task-governor` VERIFIER run
- Report Path: `docs/acceptance/TASK-WP03-03-R2-acceptance.md`
- Report Path Basis: the repository already uses `docs/acceptance/` for formal WP03 acceptance reports.
- Implementation Status: executor reported `IMPLEMENTATION_COMPLETE`; independent verification completed.
- Implementation Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp03-research-package`
- Branch: `codex/wp03-research-package`
- HEAD / Baseline Commit: `d9bceedf27d80c84472613868b97d7b172cacfd6`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`; supplementary bundled runtime evidence also achieved for the repaired guard boundary.
- Missing Acceptance: none required by this Repair Contract.
- Overall Verdict: `PASS`
- Repair Required: `NO`
- Next Action: close WP03 implementation work through an explicit branch-integration choice before dispatching WP04.

## Executive Decision

R2 closes every Blocking defect recorded in `TASK-WP03-03-R1-acceptance.md`:

- Research error codes are checked against the generated `ResearchErrorCode` runtime enum rather than accepted as arbitrary strings;
- optional version fields accept only an integer, `null`, or absence, and reject fractions, `NaN`, infinity, strings, objects, arrays, and booleans;
- generated `HTTPValidationError.detail` may be absent, and a present value must be an array of structurally valid `ValidationError` objects;
- each validation item requires array `loc`, string `msg`, string `type`, `(string | integer)[]` location entries, and an absent or object `ctx`;
- the public guards continue to enforce `ApiError` identity, exact requested status, operation/status declaration, and operation-specific 422 union behavior.

The committed regression test directly invokes both public guard APIs and covers the prior false positives and false negative. An additional verifier-owned bundled probe exercised the remaining high-risk boundaries, including non-string messages, fractional/non-finite numbers, invalid `detail`, invalid `ctx`, status mismatch, and undeclared operation status. All cases behaved according to the generated model contract.

No previously passed R1 transport, generated-client, status logging, deterministic generation, build, backend, or persistence behavior regressed. The negative drift gate still fails deliberately and restores the official artifacts afterward.

## Changed Files Snapshot

### BASELINE_CHANGED_FILES

The isolated worktree already contained cumulative WP03-01, WP03-02, WP03-03, and R1 changes. Their prior state and hashes are recorded in:

- `docs/acceptance/TASK-WP03-03-R1-acceptance.md`

### Task-attributable R2 changes

- `apps/web/src/api/client.ts`
- `tests/test_frontend_openapi_client.py`
- `docs/WP03_RESEARCH_PACKAGE_CLIENT.md`

R2 attribution is `CERTAIN`: comparison with the R1 acceptance hash snapshot shows only these three files changed for the repair. The generated OpenAPI artifact and generated core/request hashes stayed unchanged.

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

Relevant final SHA-256 snapshot:

- `apps/web/src/api/client.ts`: `3e2787395b4b91179d3be04d6de4f581a0d0c415f7bb5d889b0d96c71e2aa929`
- `tests/test_frontend_openapi_client.py`: `196293d8abbd47b09cb35ed7dc7ae368443e75b3972e895201a4865ea0b0cc0c`
- `docs/WP03_RESEARCH_PACKAGE_CLIENT.md`: `520e2c57b2981b5e2a6fb3a007ade00f9da94d72bf183d3c9201160863f4d061`
- unchanged `apps/web/openapi.json`: `821bfd18cf0b96a86d208a4b14848789b6847405fc345af3d7b156814b9b754b`
- unchanged `apps/web/src/api/generated/core/ApiError.ts`: `e047b9722dcb2a60b8272adcf3569469f659dbd01547a34aee72d30baa7f9ff8`
- unchanged `apps/web/src/api/generated/core/request.ts`: `b07777a7654e89e2c12f4536204f8ae31b4542bfd7910c8bdd5cf91bb5ce795f`

## Classification

- Task Type: `REPAIR` + `FRONTEND_API_CONTRACT`
- Risk Type: runtime type-predicate soundness, generated-model conformance, operation/status narrowing, regression of the previously accepted generated transport
- Touched Layers: frontend API façade, bundled TypeScript runtime tests, client contract documentation
- Task Size: `SMALL`
- Evidence Matrix Type: `Full`, retained because the repaired predicate is a critical untrusted-response boundary.
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, G5 Regression, G6 Evidence
- Not Applicable Gates: DB Persistence, browser/UI, worker/queue, external provider, permissions/tenant/DataScope

## Top Blocking AC Results

| Top AC | Result | Evidence |
|---|---|---|
| TOP-AC-01 — Research error guards accept only generated `ResearchErrorResponse` bodies | PASS | `client.ts:102-130` uses generated enum membership, string message, and integer/null/absent version validation. Committed and independent malformed-body probes passed. |
| TOP-AC-02 — validation-error guard matches generated optionality and structure | PASS | `client.ts:132-159` allows absent `detail`, otherwise requires a valid array and strict item/location/context shapes. Positive and negative bundled probes passed. |
| TOP-AC-03 — public status/operation guards reject mismatches and preserve operation-specific 422 unions | PASS | `client.ts:161-211`; independent probe rejected status mismatch, undeclared 409 for `listHistory`, and Research body for `getVersion` 422 while accepting create 422 union alternatives. |
| TOP-AC-04 — executable regression evidence catches the original R1 defects | PASS | `tests/test_frontend_openapi_client.py:348-568` invokes both public guards and covers valid Research/validation models, optional detail, unknown enum, invalid versions, invalid loc items, missing required fields, and wrong 422 branch. |
| TOP-AC-05 — R1 pass behavior and full project regression remain green | PASS | generated artifacts unchanged; deterministic hash and drift gates, frontend type/lint/build, 66-test suite, Ruff, mypy, Compose, and diff integrity all passed. |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Correct worktree, branch, HEAD, cumulative dirty baseline, prior FAIL report, R1 hash snapshot, and final R2 hashes were independently inspected. |
| G1 Scope | PASS | R2 attribution is limited to the three authorized guard/test/documentation files. No generated core, backend, migration, dependency, UI, worker, Evidence, Thesis, or Agent change is attributable to R2. |
| G2 Contract | PASS | Every accepted value satisfies the corresponding generated body model; high-risk malformed values and operation/status mismatches are rejected. |
| G3 Architecture | PASS | Unknown transport bodies remain `unknown` in generated core and are narrowed at the frontend façade using generated model values; no second source-of-truth schema was introduced. |
| G4 Test | PASS | Focused suite reports `9 passed`; committed runtime probe covers the R1 regression, and an independent broader bundled probe passed all exercised boundary categories. |
| DB Persistence | NOT_APPLICABLE | R2 changes no schema, ORM, migration, service transaction, or persistence behavior. Existing Research persistence remains covered by the full suite. |
| G5 Regression | PASS | Frontend wrappers/build, full `66 passed` suite, Ruff, mypy, Compose validation, deterministic artifact hash, drift detection, and diff integrity are green. |
| G6 Evidence | PASS | Fresh verifier output supports every Blocking AC; the executor report was used only as a checklist and not as approval evidence. |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary / Negative Evidence | Verdict |
|---|---|---|---|---|---|
| R2-AC-01 [BLOCKING] | Code must be a generated enum member | `researchErrorCodeValues` derives from `Object.values(GeneratedResearchErrorCode)` and `isResearchErrorCode` checks membership | valid generated member accepted by committed and verifier probes | unknown string rejected | PASS |
| R2-AC-02 [BLOCKING] | Message must be a string | `typeof value.detail.message === 'string'` | valid string accepted | verifier probe rejected numeric message | PASS |
| R2-AC-03 [BLOCKING] | Version fields must be integer/null/absent | `isOptionalIntegerOrNull` uses explicit optional/null checks and `Number.isInteger` | integer, null, and absence accepted | strings, objects, fractions, `NaN`, and infinity rejected | PASS |
| R2-AC-04 [BLOCKING] | `HTTPValidationError.detail` follows generated optionality | absent detail returns true; present detail requires array | `{}` and `detail: []` accepted | `detail: null` and object rejected | PASS |
| R2-AC-05 [BLOCKING] | Validation item fields and location members are structurally valid | required `loc/msg/type`, integer/string location check, optional object `ctx` | valid loc with string/integer and object ctx accepted | missing/wrong required fields, object/array/bool/null/fractional/non-finite loc items, and string/array/null ctx rejected | PASS |
| R2-AC-06 [BLOCKING] | Status and operation mapping remain exact | public guards check `ApiError`, exact status, declared operation status, and operation-specific body branch | valid refresh 409, create 422 Research, and getVersion 422 validation accepted | status mismatch, undeclared listHistory 409, getVersion 422 Research body, and plain object rejected | PASS |
| R2-AC-07 [BLOCKING] | Original R1 failure is protected by executable tests | dedicated test bundles and runs real public exports | focused suite `9 passed` | exact R1 unknown enum, string/object versions, object/bool loc, optional detail, missing field, and wrong union cases are asserted | PASS |
| R2-AC-08 [BLOCKING] | Previously passed R1 behavior remains intact | generated artifacts not modified; R2 touches only façade guard/test/doc | frontend checks/build and full project regression pass | injected generated drift still fails and next normal check passes with same hash | PASS |

### Acceptance Level Evidence

- `L1_STATIC_REVIEWED`: achieved. The prior failure, generated models, public guard implementation, committed runtime test, documentation, hashes, and scope attribution were inspected.
- `L2_BUILD_VERIFIED`: achieved. TypeScript/Vue typecheck, ESLint, production build, Ruff, mypy, Compose validation, and diff integrity passed.
- `L3_CONTRACT_VERIFIED`: achieved. Committed and independent executable probes establish generated-schema, operation, and status behavior for valid, invalid, and boundary inputs.
- `L4_RUNTIME_VERIFIED`: supplementary evidence achieved for the bundled frontend guard boundary; no browser or deployed-environment claim is made.
- `L4_DB_VERIFIED`: not required or claimed for this frontend-only repair.

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| Git status, HEAD, worktree, diff, and hash inspection | PASS | Confirm baseline, branch, scope attribution, final state, and unchanged generated core |
| `pytest -q tests/test_frontend_openapi_client.py -rs` | PASS — `9 passed, 2 warnings` | Focused generated-client and public-guard regression |
| verifier-owned TypeScript guard probe bundled with worktree `esbuild` and executed with Node | PASS — exit `0` | Exercise additional valid, invalid, boundary, status-mismatch, and operation-mismatch cases against real exports |
| `npm run api:check` | PASS | Confirm canonical/generated artifacts are current |
| `npm run api:hash` twice across fresh checks | PASS — `985634bdb5ec3516883a666fc555525a7656480771d324aa08ef99c2a14b3492` both times | Deterministic API artifact content |
| `npm run typecheck` | PASS | Strict TypeScript/Vue contract |
| `npm exec eslint -- . --ext .vue,.ts,.tsx` | PASS | Non-fixing frontend lint check |
| `npm run build` | PASS | Production frontend build |
| `make frontend-check` | PASS | Project frontend check wrapper; post-command hashes confirm no implementation mutation |
| `make frontend-build` | PASS | Project frontend production-build wrapper |
| `THESISGUARD_API_CHECK_INJECT_DRIFT=1 npm run api:check` | EXPECTED FAIL — exit `1`, generated file-list drift detected | Negative drift proof |
| normal `npm run api:check` after negative probe | PASS | Confirm the probe restored official artifacts |
| `pytest -q -rs` | PASS — `66 passed, 4 warnings`, no skips | Full project regression |
| `make lint` | PASS — Ruff reports all checks passed | Python lint |
| `make typecheck` | PASS — 46 source files | Python type checking |
| `docker compose config --quiet` | PASS | Compose configuration validity |
| `git diff --check` | PASS | Diff integrity |

## Counterexample / Negative Verification

The verifier bundled the actual generated runtime and `apps/web/src/api/client.ts`, instantiated real generic `ApiError<unknown>` objects, and checked these categories:

| Risk | Expected | Result |
|---|---|---|
| unknown Research error code | reject | PASS |
| non-string Research message | reject | PASS |
| string/object/fractional/`NaN`/infinite version fields | reject | PASS |
| missing validation detail | accept | PASS |
| empty validation detail array | accept | PASS |
| null/object validation detail | reject | PASS |
| missing or wrong `loc`/`msg`/`type` | reject | PASS |
| object/array/boolean/null/fractional/non-finite `loc` members | reject | PASS |
| valid object `ctx` | accept | PASS |
| string/array/null `ctx` | reject | PASS |
| actual status differs from requested status | reject | PASS |
| status not declared for operation | reject | PASS |
| Research response used where version 422 permits validation only | reject | PASS |
| plain object imitating an error | reject | PASS |
| injected generated-client file-list drift | fail the gate | PASS — command exited `1` and normal recheck returned `0` |

## DB Persistence Result

`NOT_APPLICABLE` to R2. Full regression includes the previously accepted Research persistence/API tests, but this Repair Contract neither changes nor re-claims DB behavior.

## Blocking Findings

None.

## Non-Blocking Findings

1. The committed guard probe covers the original defects and representative valid/invalid/boundary branches. The independent verifier probe additionally covered non-finite values, invalid `detail`/`ctx`, and explicit status/operation mismatch. Expanding every verifier case into the committed suite would improve diagnostic granularity, but is not required to establish this repair's current contract and does not block PASS.
2. The local npm environment continues to emit pre-existing unknown-config warnings. They are unrelated to the guard contract.
3. Existing Starlette TestClient, AnyIO, and FastAPI/Starlette 422 deprecation warnings remain unrelated to R2.
4. The WP03 worktree is intentionally cumulative and uncommitted. This does not invalidate R2, but it must be resolved through an explicit integration choice before WP04 so the accepted WP03 baseline remains attributable and recoverable.

## Regression Result

- Result: `PASS`
- Preserved behavior: exact OpenAPI artifact, five Research operations, generated success/error types, non-`any` generated core, compatible Axios transport, 30-second timeout, status logging/rethrow, deterministic generation/hash, positive and negative drift gates, Research API/persistence behavior, frontend build, and all project tests.
- New verified behavior: schema-sound runtime guards for generated Research and validation error bodies.

## Repair Required

- `NO`
- `TASK-WP03-03-R2` closes the Blocking findings from `TASK-WP03-03-R1`.
- No R3 is authorized or needed.

## Final Decision Rationale

`PASS`. The implementation now makes every runtime narrowing claim only after the corresponding generated schema constraints, exact HTTP status, and operation/status declaration are satisfied. Fresh focused tests, a broader independent executable probe, deterministic generation and negative-drift evidence, frontend build checks, full project regression, and static quality gates all support the result. No Blocking scope, contract, architecture, test, regression, or evidence defect remains.

## Next Action

WP03 implementation is technically accepted, but the branch still contains all WP03 work as uncommitted cumulative changes. Use the development-branch finishing workflow and make an explicit choice to merge locally, push/create a PR, keep the branch, or discard it. Do not begin WP04 in this dirty WP03 worktree before that choice, because doing so would erase the accepted WP03 attribution boundary.
