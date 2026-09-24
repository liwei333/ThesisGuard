# TASK-WP04-02-R1C-05C-01-R7 Evidence Security Proof Protocol Repair R1 — Execution Report

STATUS: BLOCKED_REGRESSION_GATE_REQUIRES_PROHIBITED_SCOPE_CHANGE

## 1. Identity and scope

- Executor: Codex operations/security repair executor; single current session; no zcode, subagent, parallel agent, or prior independent verifier was used.
- Task ID: `TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R1`.
- Task type: `SECURITY + OPERATIONS_VERIFIER_TOOLING + REPAIR`.
- This executor does not independently accept or verify its own delivery.

## 2. Resolved baseline and isolation

- Resolved baseline: `origin/main@282d37055b39dde7772dfca443f814c243c43dd9`.
- Required commit `282d37055b39dde7772dfca443f814c243c43dd9` is the resolved remote main itself.
- Initial main branch/HEAD: `main@282d37055b39dde7772dfca443f814c243c43dd9`.
- Initial main tracked diff: empty. Initial index: empty.
- Existing protected untracked input: `docs/workbench.html`; only path/type/bytes/SHA-256 metadata was computed. Its body was not printed, copied, staged, edited, moved, deleted, or committed.
- Isolated branch: `codex/wp04-02-r7-proof-protocol-repair-r1`.
- Isolated worktree: `/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-r7-proof-protocol-repair-r1`.
- Implementation commit: `9ba7334` (`fix(verifier): retain secure PostgreSQL proof failure classification`).
- No merge, push, pull request, rebase, reset, clean, or stash was performed.

## 3. Changed files

Implementation commit:

1. `tg_verifier_tools/verification/wp04_02_secure_pg_proof.py`
2. `tg_verifier_tests/verification/test_wp04_02_secure_pg_proof.py`

Formal closure delivery:

3. `docs/acceptance/TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R1-execution-report.md`
4. `docs/acceptance/TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R1-evidence/`

No business code, fixture, migration, existing verifier runner/test, build configuration, Docker configuration, rule, prior acceptance report, prior evidence bundle, or protected user file was modified.

## 4. Proof protocol design

The parent generates/accepts a high-entropy invocation identifier, starts one child with fixed Python, fixed module argv, fixed allowlisted environment, fixed cwd and timeout, discards stderr, and retains at most 4097 stdout bytes in memory. It never reads or enumerates the parent environment and never reads database connection material. Nonzero children are classified from numeric return code alone. A zero child is accepted only when stdout is one exact UTF-8 JSON object with the complete allowlisted schema, no leading/trailing text, a matching invocation identifier, exact success status, exact 1/1/1 counts, safe database/user identifiers and a valid server-major integer.

The child imports only the exact existing opaque loader module, reads the exact connection-value attribute within the child, validates it without returning it, opens at most one connection, and issues one fixed read-only SELECT for current database, current user and server version number. It emits only one bounded success JSON document. Every failure path emits no application diagnostic and exits with a fixed code. Parent stderr is wired to null; raw stdout, raw stderr, exception text and tracebacks have no retained record field.

The evidence publisher uses private 0700 staging, exclusive report linking, an exclusive no-replace directory rename, rollback on publish failure, and refuses both pre-existing and raced formal outputs. The recursive manifest excludes only the exact root `manifest.json`; nested manifests remain eligible.

## 5. Child exit-code mapping

| Code | Fixed stage |
|---:|---|
| 0 | `SUCCESS` |
| 41 | `OPAQUE_LOADER_IMPORT_FAILURE` |
| 42 | `OPAQUE_VALUE_UNAVAILABLE_OR_INVALID` |
| 43 | `SQL_CONNECTION_FAILURE` |
| 44 | `FIXED_SELECT_FAILURE` |
| 45 | `RESULT_SCHEMA_FAILURE` |
| 46 | `CHILD_PROTOCOL_OR_SERIALIZATION_FAILURE` |
| 47 | `UNEXPECTED_CHILD_INTERNAL_FAILURE` |
| 124 | `TIMEOUT` |
| 130 | `INTERRUPTED` |
| any other integer | `UNKNOWN_CHILD_RETURN_CODE`, preserving the integer |

## 6. Credential and diagnostic boundary

- Parent database URL/DSN/userinfo reads: 0.
- Parent environment enumeration/copy: 0; malicious-environment tests pass.
- Connection material in argv/environment/temp file: 0.
- Raw child stdout/stderr retained in records/evidence: 0.
- Exception repr/traceback retained in records/evidence: 0.
- Container environment/log reads: 0/0.
- Prohibited source/config reads: 0.
- Synthetic canaries were assembled only in test memory and do not occur as a complete literal in source snapshots, this report, or evidence.
- Final credential scan finding count: 0.

## 7. Offline verification

- Test-first RED was observed when the target module did not yet exist.
- Secure proof deterministic suite: 56 collected, 56 passed, 0 failed; real database connections 0.
- Covered contract scenarios: at least 45, including every fixed exit code, timeout, interruption, unknown code preservation, malformed/multiple/trailing/empty/whitespace/oversized stdout, cross-invocation/contradictory schemas, malicious environment, argv/environment/temp-file isolation, raw-stream exclusion, no-clobber, publisher race, manifest recursion, JSON/JSONL parsing, scanner self-test, failure closure, and exact success counters.
- Dry run: synthetic success `SUCCESS`; synthetic failure `SQL_CONNECTION_FAILURE` with child return code 43; raw-stream fields 0.
- Python compile: exit 0 with bytecode redirected under `/private/tmp`.
- Ruff check: exit 0, all checks passed.
- Ruff format check: exit 0, both files formatted.
- `git diff --check`: exit 0.

## 8. Blocking regression gate

The required combined command collected 138 tests and produced 137 passed / 1 failed. The only failure was the pre-existing `test_collect_only_end_to_end`: the historical runner constant expects main `675217c3a15c0f41…`, while this task's resolved baseline and protected main are `282d37055b39dde7…`.

The same original runner test file was independently executed from the unchanged protected main workspace and reproduced the same result: 82 collected, 81 passed, the identical single failure and mismatch reason. Therefore the new proof implementation introduced no runner regression, but the literal gate “existing runner regression tests pass” remains unsatisfied. Making it pass requires changing the existing `wp04_02_r4_runner.py` pin, changing its existing test, or altering the protected main execution context. All are outside or contrary to this task's allowed modification scope.

The contract explicitly forbids live proof until this gate passes and separately permits stopping when completion requires modifying prohibited scope. For that reason the proof budget was not consumed.

## 9. Docker/PostgreSQL read-only preflight

- Docker context: `desktop-linux`; daemon available; server version 29.7.2.
- Exact container: `thesisguard-postgres`; running and healthy.
- Image: `pgvector/pgvector:pg17`; image ID matches the task's expected ID.
- Volume: `thesisguard-postgres-data`; driver `local`; destination `/var/lib/postgresql/data`.
- Restart policy: `unless-stopped`.
- Port mapping: host 15432 to container 5432/tcp.
- `pg_isready`: accepting connections.
- Docker open actions: 0. Container start actions: 0. Recovery actions: 0.
- SQL executed during preflight: 0.

## 10. Live proof and mutation counters

- Live proof invocation count: 0.
- Proof budget consumed: no.
- Invocation identifier generated: no; generation was intentionally deferred until all blocking gates closed.
- Parent return code: `NOT_RUN`.
- Child return code: `NOT_RUN`.
- Stage: `REGRESSION_GATE_REQUIRES_PROHIBITED_SCOPE_CHANGE`.
- Connection count: 0.
- Fixed SELECT count: 0.
- Schema-valid result count: 0.
- Retry count: 0.
- Database mutation count: 0.
- Docker mutation count: 0.
- CREATE/DROP/ALTER/migration/fixture/schema DDL/business DML/terminate/cleanup counts: all 0.

## 11. Explicitly not run

- R8: not run and not authorized.
- 41-scenario real PostgreSQL suite: not run and not authorized.
- Business pytest, migrations, fixtures, cleanup, Git integration, merge, push and PR: not run.
- No downstream work package is authorized by this delivery.

## 12. Evidence closure

- Staging root: private 0700 directory under `/private/tmp`.
- Formal output preflight: report absent; evidence path absent.
- JSON/JSONL audit: all documents parse; invalid count 0.
- Recursive manifest audit: missing 0, extra 0, byte mismatch 0, hash mismatch 0.
- Root manifest excludes only itself and includes all other evidence files, including credential scan and any nested manifest.
- Credential scan: 0 findings across source snapshots, report and evidence; scanner reports only type/path/count and never matched values.
- Main protected file comparison: path/type/bytes/SHA-256 all unchanged; body not included in evidence.
- Publication: no-clobber and exclusive directory rename; final paths are never overwritten.

## 13. Required Acceptance

| Level | Result | Basis |
|---|---|---|
| `L1_STATIC_REVIEWED` | ACHIEVED for implementation scope | direct source review, fixed mappings, strict schema and boundary tests |
| `L2_BUILD_VERIFIED` | MISSING as a complete task gate | new files build/lint/test clean, but required existing runner command is not all-green |
| `L3_CONTRACT_VERIFIED` | PARTIAL / MISSING overall | deterministic proof protocol contract passes; blocking regression prerequisite does not |
| narrowly scoped `L4_RUNTIME_VERIFIED` | MISSING | live proof correctly not invoked before all offline gates passed |
| one read-only PostgreSQL proof | NOT RUN | budget remains unconsumed |

## 14. Remaining risk and stop rationale

The secure proof implementation is available for independent review, but no live PostgreSQL behavior has been established. A later authorized task must resolve the stale existing-runner main pin within an expressly allowed scope, rerun the complete offline gate, and only then decide whether a fresh one-shot proof budget is authorized. This current session cannot continue to live proof without violating the explicit pre-proof gate, and cannot make the regression command all-green without editing prohibited existing verifier scope.

This is a blocked implementation delivery, not PASS, VERIFIED, DONE, acceptance, or authorization for R8, the 41-scenario suite, 05C-02, R1D, WP-04-03, Git integration, merge, push, or PR.
