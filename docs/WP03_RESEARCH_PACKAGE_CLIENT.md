# WP-03 OpenAPI TypeScript Client

Status: implemented for `TASK-WP03-03`

## Scope

The frontend API boundary is generated from the live FastAPI application contract:

```bash
cd apps/web
npm run api:generate
```

The source of truth is `apps.api.main.create_app().openapi()` in the current worktree.
No remote OpenAPI URL, copied JSON, or hand-written Research schema is used.

## Generator

- Package: `openapi-typescript-codegen`
- Version: exact `0.29.0`
- Client: generated Axios-based services
- Output: `apps/web/src/api/generated/`
- Canonical artifact: `apps/web/openapi.json`

The generator produces:

- reusable TypeScript models in `src/api/generated/models/`;
- callable service operations in `src/api/generated/services/`;
- shared request/runtime core in `src/api/generated/core/`.

The generated directory is committed source for this worktree and must not be
manually edited. Regenerate it from OpenAPI instead.

`api:generate` also applies a deterministic post-generation patch from
`apps/web/scripts/openapi-tools.mjs`. That patch keeps the selected generator but
adds the frontend contracts it does not emit on its own:

- `ApiError<TBody = unknown>` and `ApiResult<TBody = unknown>` so failed
  response bodies are not erased to `any`;
- `OpenAPI.AXIOS`, allowing the generated request runtime to use the public
  Axios instance exported by the facade;
- an `ApiResult` export for compile-time probes and runtime logging tests.

## Drift Gate

```bash
cd apps/web
npm run api:check
```

`api:check` exports a fresh OpenAPI artifact and generated client into a
temporary directory, compares that output with the committed artifact and client,
and exits non-zero on drift. It does not overwrite the official generated files.

Make targets:

```bash
make frontend-api-generate
make frontend-api-check
make frontend-check
```

`make frontend-check` runs the API drift gate before typecheck and lint.

## Frontend Boundary

`apps/web/src/api/client.ts` is the hand-maintained facade. It owns:

- generated client base URL configuration;
- request timeout and error logging behavior;
- compatibility exports used by current Vue views;
- stable Research facade function names for future UI work.

It must not contain business endpoint URL strings or duplicate OpenAPI response
interfaces. Endpoint paths and schema models live in generated files only.

The public `apiClient` export is a real `AxiosInstance` with a 30-second
timeout. `openApiConfig` is the separate generated configuration object. The
facade assigns `openApiConfig.AXIOS = apiClient`, so generated service requests
and callers using `apiClient` share the same transport instance.

Generated HTTP failures are thrown as `ApiError<TBody>`. The facade logs both
Axios errors and generated `ApiError` instances through the same path, preserving
the real HTTP status before rethrowing the original error.

Because generated OpenAPI paths already include `/api/v1`, `VITE_API_BASE_URL`
must be the server origin/base only, for example:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

When `VITE_API_BASE_URL` is empty, generated requests use paths such as
`/api/v1/health`. When it is `http://localhost:8000`, generated requests target
`http://localhost:8000/api/v1/health`.

`VITE_API_VERSION` is intentionally removed because keeping it would invite a
duplicated `/api/v1/api/v1` prefix.

## Research Operations

Generated callable operations are in:

`apps/web/src/api/generated/services/ResearchService.ts`

Facade helpers are exported from:

`apps/web/src/api/client.ts`

- `createInitialResearchPackage`
- `getCurrentResearchPackage`
- `listResearchPackageHistory`
- `getResearchPackageVersion`
- `refreshResearchPackage`

Create and refresh require a caller-provided `Idempotency-Key` value. The
frontend client does not generate, trim, replace, or hide that value.

Research error contracts are exposed at the facade boundary with generated
models only:

- `ResearchApiErrorBodyForStatus<'createInitial', 422>` is
  `ResearchErrorResponse | HTTPValidationError`;
- `ResearchApiErrorBodyForStatus<'refresh', 422>` is
  `ResearchErrorResponse | HTTPValidationError`;
- `ResearchApiErrorBodyForStatus<'getVersion', 422>` is
  `HTTPValidationError`;
- `isResearchApiErrorForStatus(error, operation, status)` narrows caught
  generated errors by endpoint and HTTP status after checking the runtime body
  shape.

The public Research error guards validate the generated/OpenAPI error schemas
before narrowing an unknown generated `ApiError` body. Research error codes must
be members of the generated `ResearchErrorCode` enum; optional
`expected_version` and `current_version` fields must be integers, `null`, or
absent; `HTTPValidationError.detail` may be absent, but when present each
validation item must include `loc`, `msg`, and `type`, and every `loc` element
must be a string or integer.

## Contract Tests

`tests/test_frontend_openapi_client.py` checks the canonical artifact, generated
Research models and operations, typed generated error core, facade transport
compatibility, status-aware generated-error logging, drift gate declarations,
base URL behavior, and that manual facade code does not reintroduce business
endpoint URLs.

`apps/web/src/api/generated-client-smoke.ts` is compiled by `vue-tsc` and proves
that generated Research operations are callable, mutation idempotency headers
are required, refresh payloads use `ResearchRefreshRequest`, success payloads use
`ResearchPackageRead`, endpoint-specific generated error bodies are not `any`,
create/refresh/version error contracts match OpenAPI, `apiClient` is assignable
to `AxiosInstance`, generated status logging rethrows typed errors, and
`ResearchFreshness` rejects invalid values at compile time.
