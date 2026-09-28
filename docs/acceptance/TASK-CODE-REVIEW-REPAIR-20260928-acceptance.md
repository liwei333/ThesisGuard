# TASK-CODE-REVIEW-REPAIR-20260928 Acceptance Report

## Verdict

`FAIL`

This is an independent verifier result. The executor's report is evidence to
investigate, not a PASS declaration.

## Classification

- Task type: `REPAIR`
- Risk type: runtime lifecycle, database persistence, idempotency, security,
  concurrency, API contract, frontend regression
- Touched layers: worker runtime, API, configuration, Compose, domain services,
  persistence service, migration/test quality, frontend
- Task size: `LARGE` as originally dispatched; this acceptance only closes the
  independently verifiable repair findings below
- Evidence matrix: `Full`
- Selected gates: Baseline, Scope, Contract, Architecture, Test, DB
  Persistence, Regression, Evidence
- Required acceptance: `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`,
  `L4_RUNTIME_VERIFIED`, `L4_DB_VERIFIED`; frontend changes additionally require
  `L4_BROWSER_VERIFIED` for a full UI claim

## Baseline and attribution

- Branch: `main`, behind `origin/main` by 2 commits.
- The worktree was already dirty with historical untracked acceptance materials
  and `docs/workbench.html`.
- The executor-reported modified files match the tracked diff inspected for this
  review, plus the untracked `tests/test_code_review_repairs.py`.
- Existing `docs/acceptance/` materials and `docs/workbench.html` were not
  treated as task changes.
- Attribution is high for the files listed in the executor report; the worktree
  remains uncommitted.

## Evidence executed independently

| Check | Result | Evidence |
|---|---|---|
| `ruff check backend/ apps/ migrations/ tests/` | PASS | `All checks passed!` |
| `MYPYPATH=. mypy --explicit-package-bases backend apps --ignore-missing-imports` | PASS | `Success: no issues found in 50 source files` |
| `python -m compileall -q backend apps` | PASS | exit code 0 |
| `docker compose config --quiet` | PASS | exit code 0 |
| Focused repair/instrument/watchlist/health/task tests | PASS | `33 passed, 2 warnings` |
| Frontend typecheck/build/API drift/ESLint | PASS | all commands exit 0 |
| Full `pytest -q` | FAIL/BLOCKED | `109 passed, 11 skipped, 400 errors`; DB fixture connection refused at `127.0.0.1:15432` |

## Blocking findings

### B1 — Worker lifecycle repair is semantically incorrect

Status: `FAIL`

The changed entry point is:

- `apps/worker/main.py:48-62`

It now performs `worker.start()` followed by `worker.join()`. Independent
inspection of the installed Dramatiq implementation shows that `Worker.join()`
waits for current queue work and returns when the work queue is empty. It is not
a process-lifetime loop. Therefore an idle worker can still return from
`run_worker()` and exit.

The changed code also has no `signal.signal(SIGTERM, ...)` or equivalent
shutdown handler. Catching `KeyboardInterrupt/SystemExit` does not establish
SIGTERM graceful shutdown semantics.

The focused test only uses a `MagicMock` and proves that `start()` and `join()`
were called; it does not prove that a real worker remains alive or handles
SIGTERM.

Required repair:

- Use a lifecycle mechanism compatible with the installed Dramatiq version
  that keeps the process alive while the worker is running.
- Add explicit SIGTERM/SIGINT handling or a verified equivalent.
- Keep shutdown idempotent and avoid hanging tests.
- Add a test for signal registration/shutdown behavior and a runtime smoke path
  that proves an idle worker does not immediately return.

### B2 — Unqualified instrument resolution can still choose an arbitrary market

Status: `FAIL`

The changed implementation parses qualified symbols, but the unqualified path
still calls `_search_statement(..., limit=1)` and returns the first database
match:

- `backend/instrument/services.py:161-183`
- `backend/instrument/services.py:186-213`
- `backend/instrument/services.py:241-244`

`resolve_instrument()` calls `search_instruments(..., limit=1)`, so if the same
symbol exists in multiple exchanges and the user does not specify an exchange,
the service can still return an arbitrary row. The new behavior in
`get_instrument_by_symbol()` that returns `None` for multiple matches does not
protect this path.

Required repair:

- An unqualified symbol with multiple market matches must return an explicit
  ambiguity result or `None`, never an arbitrary first row.
- A qualified symbol must continue to resolve exactly one canonical exchange.
- Add a regression test against two persisted instruments with the same symbol
  on different exchanges, including the Watchlist resolution path.

## Blocked acceptance

The following cannot be accepted until the local services are available:

- PostgreSQL migration round-trip and real transaction behavior
- Evidence repository/service idempotency and concurrent persistence
- Watchlist/Instrument database unique-constraint race handling
- Research API PostgreSQL behavior
- Redis enqueue/consume runtime
- MinIO permission and object-access behavior

The exact independently reproduced blocker is:

```text
ConnectionRefusedError: [Errno 61] Connect call failed ('127.0.0.1', 15432)
```

These are `BLOCKED_VALIDATION / UNPROVEN`, not PASS and not evidence that the
implementation itself necessarily fails.

## Non-blocking accepted evidence

The following areas have fresh static or focused evidence, but do not override
the blocking findings:

- Python source/test/migration Ruff gate passes.
- mypy passes for 50 source files.
- Frontend typecheck, build, OpenAPI drift check and ESLint pass.
- Error message redaction and MinIO AccessDenied distinction have focused tests.
- Watchlist schema rejects an unknown status in a focused test.
- Compose parsing and loopback binding assertions pass.
- Evidence request-hash code now covers substantially more inputs, but real DB
  replay/conflict behavior remains unverified.

## Next required task

Do not dispatch a new feature task. Dispatch the smallest Repair Contract for
B1 and B2 only. Re-verify B1/B2 first; after they PASS, separately schedule a
DB/Redis/MinIO environment restoration task before claiming L4/L4_DB acceptance.
