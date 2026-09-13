# ACCEPTANCE REPORT

**OVERALL: FAIL**

## Metadata

- Task ID: `TASK-WP03-02-R1`
- Parent Task: `TASK-WP03-02`
- Date: `2026-09-13` (`Asia/Shanghai`)
- Verifier: Codex, independent `ai-task-governor` VERIFIER run
- Report Path: `docs/acceptance/TASK-WP03-02-R1-acceptance.md`
- Implementation Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp03-research-package`
- Branch: `codex/wp03-research-package`
- Baseline Commit: `d9bceedf27d80c84472613868b97d7b172cacfd6`
- Executor Claim: `IMPLEMENTATION_COMPLETE`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_RUNTIME_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L4_RUNTIME_VERIFIED`, `L4_DB_VERIFIED`
- Missing Acceptance: `L3_CONTRACT_VERIFIED`
- Overall Verdict: `FAIL`
- Repair Required: `YES`
- Repair ID: `TASK-WP03-02-R2`
- Next Action: fix only the inaccurate 422 OpenAPI contract and its regression tests; do not start `TASK-WP03-03`.

## Executive Decision

R1 correctly introduced typed Research error models and the exact four-value freshness enum. It also preserved all existing API, idempotency, concurrency, persistence, lint, type, Compose, and full-regression behavior.

However, the Blocking 422 contract requirement is still not met. The implementation declares every applicable 422 response as only `ResearchErrorResponse`, while the running FastAPI application returns both:

1. standard framework validation responses with `detail` as a list; and
2. Research domain responses with `detail` as an object containing `code` and `message`.

The new OpenAPI regression test asserts the inaccurate single-schema declaration, so it passes while the public contract disagrees with runtime behavior. Because generated-client work depends on this contract, R1 cannot pass and `TASK-WP03-03` remains blocked.

## Changed Files And Attribution

### Cumulative worktree status

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

### R1-attributable files

Hash comparison with the pre-R1 verifier snapshot identifies these R1 changes:

- `backend/research/api.py` — SHA-256 `23853af445049d1bfb9a2dcb34db7aaa1223661d7e79b20cdf40695c08843ae1`
- `backend/research/schemas.py` — SHA-256 `fbed316559da24073c5c5a03b41d17b06bfb7ee0b7f4639bbe582f48a1d7fba5`
- `tests/test_research_api.py` — SHA-256 `ef0f2492391b4132acbda31f32bbd04545b3fde0e1194a5805504e59e3eefd59`

`docs/WP03_RESEARCH_PACKAGE_API.md` remained unchanged from the pre-R1 snapshot (SHA-256 `d898e14b0166ffff1ca70ede1af1b24152736f372cc36677f8da163af028c7bb`). The document already states that framework validation retains FastAPI's standard 422 shape.

Attribution confidence: `CERTAIN`.

## Classification

- Task Type: `BACKEND_API_CONTRACT_REPAIR`
- Risk Type: public OpenAPI accuracy, generated-client compatibility, error information boundary
- Task Size: `SMALL REPAIR`
- Evidence Matrix Type: `Full` because the parent task includes API, concurrency, idempotency, and real DB persistence
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, DB Persistence, G5 Regression, G6 Evidence
- Not Applicable: frontend/UI, worker/queue, external provider, permission/tenant/DataScope

## Top Acceptance Criteria

| Top AC | Result | Evidence |
|---|---|---|
| TOP-AC-R1-01 — typed Research error contract exists and runtime domain errors use it | PASS | `ResearchErrorCode`, `ResearchErrorDetail`, and `ResearchErrorResponse` exist; `research_http_exception()` serializes `ResearchErrorDetail`, including version fields. |
| TOP-AC-R1-02 — freshness is exactly `UNVERIFIED/FRESH/STALE/FAILED` in Pydantic/OpenAPI | PASS | `ResearchFreshness` is a `StrEnum`; generated OpenAPI exposes the exact four values. |
| TOP-AC-R1-03 — 404/409/422 OpenAPI schemas accurately match runtime response structures | **FAIL** | 404/409 are typed correctly, but all three Research 422 declarations are a single `$ref` to `ResearchErrorResponse`; real framework-validation responses have `detail` as an array. |
| TOP-AC-R1-04 — regression tests detect contract drift | **FAIL** | `tests/test_research_api.py:428-443` requires every 422 to equal only `ResearchErrorResponse`, encoding the mismatch instead of detecting it; runtime assertions at lines 323-364 check only status codes for framework 422 cases. |
| TOP-AC-R1-05 — parent API/DB behavior and quality gates remain green | PASS | API 8/8, persistence 8/8, full suite 57/57, Ruff, mypy, Compose, diff integrity, and DB cleanup all passed. |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Correct worktree, branch, baseline commit, cumulative status, pre-R1 acceptance report, and file hashes were inspected. |
| G1 Scope | PASS | R1-attributable changes are limited to the permitted schema, API, and API-test files. No migration, service, model, frontend, worker, dependency, or architecture expansion occurred. |
| G2 Contract | **FAIL** | The generated 422 schemas do not represent actual FastAPI request-validation payloads. |
| G3 Architecture | **FAIL** | The runtime retains two local error shapes as intended, but the public OpenAPI boundary collapses them into one inaccurate model, making generated clients unsound. |
| G4 Test | **FAIL** | The new contract test asserts the wrong single `$ref` and does not assert actual framework/domain response shapes. |
| DB Persistence | PASS | Both real PostgreSQL suites passed with zero skips; temporary database count after verification was zero. |
| G5 Regression | PASS | Full suite passed: `57 passed, 2 warnings`. |
| G6 Evidence | **FAIL** | Fresh runtime and OpenAPI evidence directly contradict the claimed complete 422 contract. |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary / Negative Evidence | Verdict |
|---|---|---|---|---|---|
| R1-AC-01 [BLOCKING] | Public Research error models and stable error code enum | `backend/research/schemas.py:34-66` | Generated components contain all three Research error schemas and exact code enum | No raw DB internals observed; unknown domain errors map to stable fallback | PASS |
| R1-AC-02 [BLOCKING] | Runtime domain-error payloads built through Pydantic | `backend/research/api.py:110-145`; blank header uses `ResearchErrorDetail` at lines 67-78 | Blank header returned `detail: {code, message}`; version-conflict regression passed | Framework validation deliberately retains its native shape | PASS |
| R1-AC-03 [BLOCKING] | 404/409/422 OpenAPI accurately describes runtime | Response metadata at `backend/research/api.py:43-54` | 404/409 schema coverage exists | 422 checker exited 1 for create, version read, and refresh; runtime returned `detail: []` where OpenAPI promised `detail: {}` | **FAIL** |
| R1-AC-04 [BLOCKING] | Exact freshness enum | `ResearchFreshness` and `ResearchModuleRead.freshness` | Explicit OpenAPI inspection returned exactly four values | No unrestricted string remains for freshness | PASS |
| R1-AC-05 [BLOCKING] | Tests guard both declared and runtime contracts | OpenAPI test added | Existing focused test passes | It asserts every 422 is only `ResearchErrorResponse`; validation tests assert status only, so incompatible bodies escape detection | **FAIL** |
| R1-AC-06 [BLOCKING] | Preserve parent behavior and DB semantics | No R1 changes to models, migration, services, or persistence tests | API 8/8, persistence 8/8, full 57/57 | Concurrent refresh, history, idempotency, and temporary DB cleanup remain green | PASS |

## Fresh Runtime Counterexamples

Generated OpenAPI declares the following for all three 422 responses:

```json
{"$ref":"#/components/schemas/ResearchErrorResponse"}
```

Actual missing-header response from initial create:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["header", "Idempotency-Key"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

Actual invalid-version response from the version endpoint likewise returns a standard validation-error list. Actual invalid refresh body returns a list containing the `expected_version` and `module_types` validation errors.

By contrast, a blank-but-present idempotency key returns the intended Research domain envelope:

```json
{
  "detail": {
    "code": "RESEARCH_VALIDATION_ERROR",
    "message": "Idempotency-Key must not be blank"
  }
}
```

Therefore:

- initial-create 422 can return both standard `HTTPValidationError` and `ResearchErrorResponse`;
- version-read 422 currently returns standard `HTTPValidationError` only;
- refresh 422 can return both standard `HTTPValidationError` and `ResearchErrorResponse` because the shared blank-header dependency can raise the domain envelope.

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| `git status --short --branch`, `git rev-parse`, prior report and file-hash inspection | PASS | Baseline, scope, attribution |
| `git diff --check` | PASS | Diff integrity |
| Direct `create_app().openapi()` plus ASGI invalid-request probe | **Contract mismatch reproduced** | Compare declared 422 schemas with four actual validation paths |
| Explicit oneOf/OpenAPI assertion | **Exit 1** — all three `accurate_422_oneOf=False`; freshness enum true | Blocking contract checker |
| `pytest -q tests/test_research_api.py -rs` | PASS — `8 passed, 2 warnings`, zero skipped | API/idempotency/concurrency/runtime regression |
| `pytest -q tests/test_research_persistence.py -rs` | PASS — `8 passed, 2 warnings`, zero skipped | WP03-01 real PostgreSQL preservation |
| `pytest -q -rs` | PASS — `57 passed, 2 warnings`, zero skipped | Full regression |
| `make lint` | PASS — `All checks passed!` | Ruff |
| `make typecheck` | PASS — `46 source files` | Mypy |
| `docker compose config --quiet` | PASS | Compose validity |
| PostgreSQL query for `tg_wp03_%` databases | PASS — `0` | Test cleanup |

The two warnings are existing FastAPI/Starlette/AnyIO deprecation warnings and are not introduced by R1.

## Blocking Findings

1. **[G2 / TOP-AC-R1-03] 422 OpenAPI is narrower than runtime.**
   - `backend/research/api.py:51-54` defines `RESEARCH_VALIDATION_RESPONSE` as only `ResearchErrorResponse`.
   - That declaration is attached at lines 198, 257, and 287.
   - FastAPI request/path/header/body validation still returns `HTTPValidationError`, exactly as the API documentation says it should.

2. **[G4 / TOP-AC-R1-04] The regression test locks in the wrong contract.**
   - `tests/test_research_api.py:428-443` puts 404, 409, and 422 into one set and requires every schema to be exactly the Research error `$ref`.
   - `tests/test_research_api.py:323-364` checks only status codes for framework validation failures and never checks their bodies.

## Non-Blocking Findings

1. The typed error code and freshness schemas are correctly implemented and must be preserved.
2. Five endpoints, status codes, idempotency behavior, concurrency control, append-only history, and real PostgreSQL semantics remain intact.
3. Existing third-party deprecation warnings may be handled separately; they are outside this repair.

## Repair Required

- Required: `YES`
- Repair ID: `TASK-WP03-02-R2`
- Failed AC/Gates: R1-AC-03, R1-AC-05; G2 Contract, G3 Architecture, G4 Test, G6 Evidence
- Repair scope: only the 422 response-schema declaration and focused contract/runtime regression assertions.

## Final Decision Rationale

`FAIL`. R1 resolves the original missing-model and freshness-enum defects, but it does not satisfy the repair's explicit rule that OpenAPI must match actual 422 behavior and use an accurate `oneOf` when a single endpoint can emit both framework and Research domain validation envelopes. This is a Blocking consumer-facing contract defect, so passing tests and persistence checks cannot override it.

## Next Action

Execute `TASK-WP03-02-R2` only. After R2 is independently accepted, re-evaluate and generate `TASK-WP03-03`; do not begin frontend client generation before that acceptance.
