# WP-03 Research Package API

Status: implemented for `TASK-WP03-02`

## Scope

This slice exposes the accepted WP03-01 Research Package persistence service through a FastAPI router. It does not implement frontend client generation, Research UI, workers, Evidence, Thesis, Agent Runtime, or any external data provider.

All paths are registered under `/api/v1`.

## Endpoints

`POST /api/v1/research/instruments/{instrument_id}/packages`

- Creates initial Research Package version `1`.
- Requires `Idempotency-Key` header, length `1..128`.
- Does not accept client `as_of` or client `request_hash`.
- Returns `201` with the created or idempotently replayed package.

`GET /api/v1/research/instruments/{instrument_id}/packages/current`

- Returns the current package, defined as the highest persisted version.
- Returns `404 RESEARCH_PACKAGE_NOT_FOUND` when there is no package.

`GET /api/v1/research/instruments/{instrument_id}/packages`

- Returns package history in ascending version order.
- Returns `200 []` when no package exists.

`GET /api/v1/research/instruments/{instrument_id}/packages/versions/{version}`

- Returns one package version.
- `version` must be greater than or equal to `1`.
- Returns `404 RESEARCH_PACKAGE_NOT_FOUND` when that version does not exist.

`POST /api/v1/research/instruments/{instrument_id}/packages/refresh`

- Creates an append-only incremental version.
- Requires `Idempotency-Key` header, length `1..128`.
- Body:

```json
{
  "expected_version": 1,
  "module_types": ["FINANCIAL", "RISK"]
}
```

- `expected_version` must be greater than or equal to `1`.
- `module_types` must contain `1..11` unique supported module types.
- Module type order is canonicalized for request hashing.

## Public Response

Package response fields include:

- `id`
- `instrument_id`
- `version`
- `previous_version_id`
- `trigger_type`
- `status`
- `expected_version`
- `as_of`
- `started_at`
- `completed_at`
- `last_verified_at`
- `created_at`
- `modules`

Module response fields include:

- `id`
- `research_package_id`
- `origin_module_id`
- `module_type`
- `module_version`
- `status`
- `freshness`
- `summary`
- `source_refs`
- `as_of`
- `last_verified_at`
- `stale_after`
- `created_at`

The public response intentionally excludes `request_hash` and `idempotency_key`.

## Status And Freshness

Package `status` is a build lifecycle state, currently one of the WP03-01 persistence values such as `PENDING`, `BUILDING`, `READY`, or `FAILED`.

Module `freshness` is derived by deterministic service logic at serialization time:

- `UNVERIFIED`: no verification timestamp exists.
- `FRESH`: verified and not beyond `stale_after`.
- `STALE`: verified but beyond `stale_after`.
- `FAILED`: module status is failed.

`PENDING`, `UNVERIFIED`, or `STALE` must not be displayed or interpreted as verified active research.

## Request Hashing

The server computes `request_hash` from:

- operation type,
- `instrument_id`,
- canonical semantic request body.

`Idempotency-Key` is not part of the request hash. Clients cannot provide or override `request_hash`.

For refresh, `module_types` are sorted before hashing, so `["FINANCIAL", "RISK"]` and `["RISK", "FINANCIAL"]` are the same semantic request.

## Error Envelope

Research domain errors use:

```json
{
  "detail": {
    "code": "STABLE_MACHINE_CODE",
    "message": "Human-readable message"
  }
}
```

Mapped codes:

- `INSTRUMENT_NOT_FOUND`: `404`
- `RESEARCH_PACKAGE_NOT_FOUND`: `404`
- `RESEARCH_PACKAGE_ALREADY_EXISTS`: `409`
- `RESEARCH_VERSION_CONFLICT`: `409`, also includes `expected_version` and `current_version`
- `IDEMPOTENCY_CONFLICT`: `409`
- `RESEARCH_VALIDATION_ERROR`: `422`
- `RESEARCH_PERSISTENCE_CONFLICT`: `409`, without database internals

Pydantic/FastAPI request validation errors keep FastAPI's standard `422` shape.

## Fact Boundary

The API surfaces persisted package/module snapshots only. It does not generate research summaries, source references, financial data, order claims, valuation, Thesis, or investment conclusions.

## Generated Client

The frontend TypeScript client is generated from the current worktree's
`apps.api.main.create_app().openapi()` output.

- Canonical artifact: `apps/web/openapi.json`
- Generated client: `apps/web/src/api/generated/`
- Generate: `cd apps/web && npm run api:generate`
- Drift check: `cd apps/web && npm run api:check`
- Make targets: `make frontend-api-generate`, `make frontend-api-check`
- Typed Research failure bodies are exposed by the frontend facade through
  generated models such as `ResearchErrorResponse` and `HTTPValidationError`;
  create/refresh 422 keeps the documented two-branch error shape, while version
  422 remains `HTTPValidationError` only.

Because all OpenAPI paths are registered under `/api/v1`, frontend base URL
configuration must provide only the server origin/base. `VITE_API_VERSION` is not
used by the generated client.
