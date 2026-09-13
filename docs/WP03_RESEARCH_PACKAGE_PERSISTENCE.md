# WP-03 Research Package Persistence

Status: implemented for `TASK-WP03-01`

## Scope

This slice implements only the durable Research Package container and its minimum domain service. It does not expose an API, start a worker, generate an OpenAPI client, ingest Evidence, create Thesis records, call an LLM, or connect external research providers.

## Tables

`research_package` stores one append-only version for one `instrument`.

Key fields:

- `instrument_id`
- `version`
- `previous_version_id`
- `trigger_type`
- `status`
- `idempotency_key`
- `request_hash`
- `expected_version`
- `as_of`
- `started_at`
- `completed_at`
- `last_verified_at`
- `created_at`

`research_module` stores one module snapshot inside one package version.

Key fields:

- `research_package_id`
- `origin_module_id`
- `module_type`
- `module_version`
- `status`
- `summary`
- `source_refs`
- `as_of`
- `last_verified_at`
- `stale_after`
- `created_at`

## Versioning

The invariant is append-only:

- `(instrument_id, version)` is unique.
- Version `1` has no `previous_version_id`.
- Versions greater than `1` must point to the previous package version.
- Refresh creates version `N+1`; it never updates version `N`.
- Current version is derived by highest `version` for the instrument.

## Modules

The supported module types are:

`COMPANY`, `BUSINESS`, `INDUSTRY`, `ORDER`, `FINANCIAL`, `EXPECTATION`, `VALUATION`, `RISK`, `CATALYST`, `COMPETITOR`, `MANAGEMENT`.

Within one package version, `(research_package_id, module_type)` is unique.

Refresh supports copy-on-write. Modules not requested for refresh are copied into the new package with `origin_module_id` pointing at the previous module snapshot. Requested modules are recreated as unverified empty snapshots because WP-04 Evidence and external providers are not implemented yet.

## Status And Freshness

Package status is lifecycle state: `PENDING`, `BUILDING`, `READY`, or `FAILED`.

Module status is snapshot state: `UNVERIFIED`, `PENDING`, `REFRESHING`, `READY`, or `FAILED`.

Freshness is a deterministic derived value:

- `FAILED` when module status is `FAILED`.
- `UNVERIFIED` when `last_verified_at` is absent.
- `FRESH` when verified and `now <= stale_after`.
- `STALE` when verified and `now > stale_after`.

Empty packages and modules are not marked as verified facts.

## Expected Version And Idempotency

`create_incremental_refresh` requires `expected_version`.

- If `expected_version` equals current version, the service creates the next version.
- If it does not match, the service raises `ResearchVersionConflict`.
- `(instrument_id, idempotency_key)` is unique.
- Repeating the same key with the same `request_hash` returns the existing package.
- Repeating the same key with a different `request_hash` raises `IdempotencyConflict`.

The service also catches database `IntegrityError` and converts it into stable Research domain errors.

## Fact Boundary

Because WP-04 Evidence is not implemented:

- `source_refs` defaults to an empty list.
- `summary` is left empty.
- No order, financial, valuation, industry, Thesis, or investment conclusion is synthesized.
- Instrument data is only used to validate that the target exists.

## Deferred

Deferred to later work packages:

- Research API and router registration.
- Generated frontend API client.
- Evidence tables and source grading.
- Research worker and provider ingestion.
- Thesis, validation, and score ledger.
- Structured Output Gateway and Agent Runtime.
