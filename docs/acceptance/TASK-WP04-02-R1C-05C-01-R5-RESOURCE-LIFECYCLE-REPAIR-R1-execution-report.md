# TASK-WP04-02-R1C-05C-01-R5-RESOURCE-LIFECYCLE-REPAIR-R1 Execution Report

## Executor boundary

- Role: Codex repair executor; not the R5 verifier and not the independent verifier for this repair.
- Branch: `codex/wp04-02-r5-resource-lifecycle-repair-r1`
- Worktree: `/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-r5-resource-lifecycle-repair-r1`
- Baseline and current branch HEAD: `77abbe72decfe5437ffed90521b8101f1eae1153`
- This report records implementation evidence only. It does not grant `L1`, `L2`, `L3`, focused `L4_DB_VERIFIED`, full R5, Git integration, or any later work package.

## Scope

Only the following tracked files changed:

1. `tests/evidence_pg_fixture.py`
2. `tests/test_evidence_pg_fixture_lifecycle.py`

Only this report and its sibling repair evidence directory were added. Evidence business services, the 41-scenario suite, `tests/conftest.py`, verifier tools/harnesses, migrations, Docker configuration, dependencies, frozen contracts and the original R5 report/evidence were not modified.

## Exact residual recovery

The user explicitly authorized one ordinary, non-FORCE DROP for the exact R5 residual identity. Immediately before the operation, the executor observed:

- name: `tg_wp04_service_53ea9a765404436e8fc6a6ecf2f51187`
- OID: `9268698`
- owner: `thesisguard`
- owner OID: `10`
- client backends: `0`
- identity equal to the R5 ledger's confirmed-created identity: true
- current full catalog equal to the R5 after catalog: true

The operation returned `DROP DATABASE`. The immediate post-operation catalog differed only by removal of that exact name. There were no additions or changed identities; the exact name was absent; OID `9268698` no longer mapped to it; all 45 fixed historical UNKNOWN name/OID/owner/owner_oid identities remained exact. No backend termination, FORCE DROP, other DROP, ownership change, Docker change or historical UNKNOWN connection/cleanup was performed. Full details are in `residual-recovery.json`.

## Root cause and repair

R5 recorded `engine_disposed` and then, approximately 19 ms later, one client backend. The fixture made only that single observation and immediately converted any nonzero count into `EvidencePGCleanupError`. Later R5 evidence showed no task-prefix client session while the database itself remained. Fixture dependency order and the failing test's explicit session context show that ordinary session teardown had already run, but R5 did not retain enough backend metadata to assign the transient connection uniquely to SQLAlchemy, asyncpg, pytest-asyncio or an external client.

The repair therefore addresses only the demonstrated lifecycle defect:

- use a monotonic deadline;
- cap the drain window at 1.0 second, below the five-second contract maximum;
- recheck at intervals no longer than 0.05 second and only after a nonzero client count;
- record check index, elapsed time, exact identity match and client count on every observation;
- treat identity drift and query failure as structured cleanup failures;
- after count reaches zero, re-read and compare exact OID/owner/owner_oid before recording `drop_sent`;
- retain ordinary exact DROP without FORCE or connection termination.

Initial zero takes the direct path with one observation and no sleep. Persistent nonzero connections remain fail closed at the deadline.

## TDD red and green

The deterministic transient sequence `[1, 0]` was added before fixture implementation changed.

- Red command: `/opt/homebrew/bin/pytest -p no:cacheprovider tests/test_evidence_pg_fixture_lifecycle.py::test_transient_client_backend_drains_before_exact_drop -q`
- Red result: exit `1`; one collected, one failed with `EvidencePGCleanupError`; no DROP was sent because the baseline stopped at the first `1`.
- Green command: the same selector after the minimal fixture change.
- Green result: exit `0`; one collected, one passed. Ledger assertions observed counts `[1, 0]`, check indices `[1, 2]`, exact identity reconfirmation and exact DROP after disposal.

## Deterministic counterexamples

The final non-real lifecycle command selected 43 tests and deselected the four real cases. It exited `0` with `43 passed` and two pre-existing deprecation warnings. The exercised behaviors include:

- transient `[1, 0]` drains, exact identity is reconfirmed and exact DROP follows;
- persistent `[1, 1, ...]` reaches the bounded deadline, records cleanup failure and sends no DROP;
- OID, owner and owner_oid drift after count reaches zero each forbid DROP;
- count-query failure records `cleanup_check_failed`, ends in cleanup failure and sends no DROP;
- body primary exceptions remain primary and receive the cleanup note;
- initial zero adds no retry wait;
- internal/autovacuum-only activity is not counted as a client backend;
- disposal failure, direct identity drift, setup/migration/create uncertainty and all previously covered fail-closed behaviors remain exercised;
- fake SQL rejects a non-exact DROP and assertions exclude `pg_terminate_backend` and `WITH (FORCE)`.

## Static and build evidence

Fresh commands after the final source/test edits produced:

- Ruff check: exit `0`, `All checks passed!`
- Ruff format check: exit `0`, `2 files already formatted`
- Python 3.12 compileall: exit `0`
- `git diff --check`: exit `0`

The named temporary locations used were:

- `/private/tmp/tg-r5-resource-lifecycle-repair-ruff`
- `/private/tmp/tg-r5-resource-lifecycle-repair-pyc`
- `/private/tmp/tg-r5-resource-lifecycle-repair-real-pyc`
- `/private/tmp/tg-r5-resource-lifecycle-repair-final-ruff-check`
- `/private/tmp/tg-r5-resource-lifecycle-repair-final-ruff-format`
- `/private/tmp/tg-r5-resource-lifecycle-repair-final-pyc`
- pytest-managed ephemeral directories under the system temporary root

No temporary file contains a database URL, password, token or complete environment dump.

## One focused real PostgreSQL lifecycle invocation

Exactly one real pytest invocation was made:

`/opt/homebrew/bin/pytest -p no:cacheprovider tests/test_evidence_pg_fixture_lifecycle.py -k real_postgres -q`

Observed result:

- collected: 47
- selected: 4 lifecycle-only cases
- deselected: 43 deterministic cases
- result: `4 passed`, two pre-existing deprecation warnings, exit `0`
- real pytest invocation count: 1
- run ID: `a085753a6d144ae98b287d6a98547621`
- CREATE sent / confirmed created: `4 / 4`
- DROP sent / confirmed dropped: `4 / 4`
- created/dropped run_id, attempt_id, node, name, OID, owner and owner_oid: exact for every resource
- cleanup_failed / create_failed / current-run UNKNOWN / current-run residual: `0 / 0 / 0 / 0`
- task-wide CREATE budget: `4 / 5`
- business test nodes executed: `0`
- full catalog before and after: 49 exact identities, no additions/removals/changes
- fixed historical UNKNOWN identities: `45 / 45` exact before and after
- task-prefix client backends before and after: `0 / 0`

This focused lifecycle run is not the original 41-scenario focused DB reverify and does not establish that suite's result.

## Evidence matrix

| Requirement | Executor evidence | Acceptance boundary |
|---|---|---|
| Baseline and immutable inputs | `baseline-and-scope.json`, fixed hashes matched | Independent reviewer must re-read Git and hashes |
| TOP-AC-01 exact recovery | `residual-recovery.json` | Exact one-target operation only |
| TOP-AC-02 red/green | `tdd-red.json`, `tdd-red-output.txt`, `tdd-green.json` | Red preceded fixture implementation |
| TOP-AC-03 fail closed | deterministic lifecycle output and test diff | Persistent/query/drift/body-primary cases covered |
| TOP-AC-04 focused real lifecycle | `real-pytest.*`, `resources.jsonl`, `ledger-audit.json`, real catalog pair | Four lifecycle cases only; not the 41 business scenarios |
| TOP-AC-05 scope and credentials | Git closure, source hashes, credential scan, manifest | Independent reconstruction still required |
| L1 static review requested | Source diff and root-cause evidence supplied | Not self-granted |
| L2 build requested | Ruff, format and compileall exit `0` | Not self-granted |
| L3 contract requested | 43 deterministic lifecycle cases exit `0` | Not self-granted |
| Focused L4 repair requested | One four-case real lifecycle invocation and exact catalog restoration | Not self-granted; limited to fixture repair |

## Git and protected-material closure

- main remained `77abbe72decfe5437ffed90521b8101f1eae1153`, with tracked diff and index empty;
- candidate remained `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`, clean;
- R5 harness remained `f9a41ea045d3ab8ad18db32d65a8484d6c96ec25`, clean;
- original R5 acceptance SHA-256 remained `7a76be1fa3dbc8daf18e3d50699a17eb357b67579eb110aff822694ace026d75`;
- original R5 manifest SHA-256 remained `a10316c137050a9af53292f5043dd30129c9f10213094dd6fafd683967ebb014`;
- no add, commit, merge, rebase, push, reset, clean, stash, PR or worktree prune was performed.

## Handoff

Implementation evidence is ready for a new Codex independent verifier. That verifier must independently review the source diff, reproduce or audit red/green ordering, inspect the one real lifecycle run, rebuild catalog/ledger conclusions, run a fresh credential scan and reconstruct the evidence manifest. Only after that separate acceptance and a separate Git integration may another new verifier rerun the original 41-scenario focused DB task.
