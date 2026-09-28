# Codex execution prompt

You are the implementation/execution Codex for one tightly governed ThesisGuard
Repair. Work autonomously until the task is complete or an explicit fail-closed
stop condition is reached. Do not self-approve your result.

## 0. Mandatory project and skill setup

1. Read the repository `AGENTS.md` completely and obey it.
2. Read and apply these available skills before task actions:
   - `using-superpowers`;
   - `systematic-debugging`;
   - `test-driven-development` for new helper/contract behavior;
   - `verification-before-completion` before any completion claim;
   - `using-git-worktrees` only as applicable to inspecting/confirming the
     managed worktree already supplied to this task.
3. Do not delegate this task to zcode. Per `AGENTS.md`, real PostgreSQL,
   execution-toolchain and lifecycle work is Codex-owned.
4. You are the executor, not the independent acceptor. Your final state must be
   `IMPLEMENTATION_COMPLETE_AWAITING_INDEPENDENT_ACCEPTANCE`,
   `EXECUTION_FAIL_AWAITING_INDEPENDENT_ACCEPTANCE`, or a precise
   `BLOCKED_*_AWAITING_INDEPENDENT_ACCEPTANCE` classification.

## 1. Task identity

Task ID:

`TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R8-PYTEST-RUNTIME-AND-RESIDUAL-RESTORE-R1`

Task type:

`REPAIR + CONFIG/TOOLCHAIN + DATABASE_MAINTENANCE + TESTING + EVIDENCE`

Task size: `MEDIUM`

Required evidence matrix: `FULL`

Executor: `Codex`

Future acceptor: a different Codex independent-review task.

Exact starting baseline and required sole parent for the final evidence commit:

`1613c89209f91a4bb64dab04c588250b0b5f6a85`

This is the R7 evidence commit. Start from this exact commit in the managed,
isolated worktree created for this task. Confirm `HEAD`, `HEAD^`, worktree state
and changed paths before doing anything else. If the supplied worktree did not
start from this exact baseline, stop as
`BLOCKED_BASELINE_MISMATCH_AWAITING_INDEPENDENT_ACCEPTANCE` without mutation.

Independent R7 review on the main worktree:

`/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R7-FULL-DB-REVERIFY-R1-FEEDBACK-INDEPENDENT-REVIEW-R1-acceptance.md`

Expected SHA-256 at dispatch time:

`36467bab05f30feb1726ffe12d93c9a5225a16d4cbd97abef1f563ff5f462667`

Read that review and independently verify its hash. Treat it as the accepted
Repair input, not as permission to broaden scope.

## 2. Accepted R7 facts you must not reinterpret

R7 independent acceptance is `FAIL` with exact classification:

`FAIL_EXECUTION_TOOLCHAIN / PYTEST_INTERPRETER_DEPENDENCY_CLOSURE_MISMATCH`

The one authorized R7 real pytest run used `/opt/homebrew/bin/pytest`, whose
shebang selected Homebrew Python 3.12. Under `PYTHONNOUSERSITE=1` it could not
import `greenlet`. The interpreter also resolved SQLAlchemy `2.0.52` and asyncpg
`0.31.0`, while `requirements-api.txt` freezes SQLAlchemy `2.0.35` and asyncpg
`0.29.0`. Therefore a greenlet-only ad hoc fallback is insufficient.

R7 runtime/lifecycle facts:

- exact focused collection: 41 nodes;
- real pytest invocations/retries: `1/0`;
- result: 41 collected, 0 passed, 1 failed, 1 teardown error;
- lifecycle attempt/create/drop/cleanup-failed: `1/1/0/1`;
- catalog count before/after: `49/50`;
- historical database count: `45`, unchanged;
- historical-state hash:
  `3b28f630bff3c1b2842e8e4b46787c588df9feaeabe3db9d356a51b4258a6f05`;
- manual cleanup/force drop/backend termination: `0/0/0`.

Exact R7-owned residual identity:

- database name: `tg_wp04_service_1161dc4e02604c5ba23d157af5436b71`;
- OID: `9273601`;
- owner: `thesisguard`;
- owner OID: `10`;
- `datistemplate=false`;
- `datallowconn=true`;
- sealed post-R7 active sessions: `0`.

R7 report:

`docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R7-FULL-DB-REVERIFY-R1-execution-report.md`

R7 evidence:

`docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R7-FULL-DB-REVERIFY-R1-evidence`

The R7 evidence tree is protected input. Do not edit it.

## 3. Single task objective

Close both direct consequences of the R7 failure without running the focused
suite again:

1. build and prove a new deterministic, task-local pytest runtime whose actual
   Python interpreter, executable, required package versions, distribution
   metadata and import origins are sealed and fail closed before any future
   database run; and
2. restore the accepted PostgreSQL catalog baseline by removing only the exact
   R7-owned residual database, and only after a secure, one-shot maintenance
   supervisor proves the live target still matches the frozen name/OID/owner and
   has zero sessions.

These are two phases of one causal Repair. The toolchain phase must pass before
the database-maintenance phase is permitted. This task must not run collect-only
and must not run any project pytest test node.

## 4. Hard scope

Allowed repository changes are evidence-only:

- one execution report under `docs/acceptance/` for this exact task;
- one evidence directory under `docs/acceptance/` for this exact task;
- helper source snapshots and contract tests only inside that evidence
  directory.

Allowed non-repository runtime writes:

- a task-local runtime root under
  `/private/tmp/tg-r10-r8-pytest-runtime-r1`;
- wheel downloads and installations only inside that task-local root;
- bounded sanitized temporary receipts needed by this task.

Forbidden repository changes:

- application source;
- project tests and fixtures;
- migrations;
- `requirements-api.txt`, `pyproject.toml`, lockfiles or project configuration;
- `AGENTS.md`;
- R6/R7 reports or evidence;
- historical acceptance material;
- candidate, main or any other worktree.

Forbidden host/shared changes:

- global or user-site package installation;
- modification of Homebrew, Miniconda base, the accepted R6 venv, shell startup
  files or shared caches as an installation target;
- Docker mutation, restart, recreation, image pull or volume mutation;
- arbitrary database cleanup;
- wildcard/prefix cleanup;
- `DROP DATABASE ... WITH (FORCE)`;
- `pg_terminate_backend`;
- merge, rebase, cherry-pick, push, PR or integration.

## 5. Blocking acceptance criteria

All top-level criteria are Blocking.

### TOP-AC-01 — Baseline, isolation and attribution

- Worktree starts clean at exact baseline
  `1613c89209f91a4bb64dab04c588250b0b5f6a85`.
- Protected input hashes are captured before and after and match.
- Final repository change is exactly one evidence-only commit whose sole parent
  is the exact baseline.
- Final worktree is clean.

### TOP-AC-02 — Deterministic pytest runtime closure

Create a fresh task-local virtual environment under the authorized runtime root.
It must not use system site-packages and must run with `PYTHONNOUSERSITE=1`.

The runtime contract must at minimum freeze and verify:

- base Python realpath, executable SHA-256, major/minor and implementation;
- venv Python realpath/identity and `sys.prefix`/`sys.base_prefix` relationship;
- `include-system-site-packages=false`;
- pytest entrypoint path, regular-file/executable status, SHA-256 and shebang;
- pytest `9.1.1`;
- pytest-asyncio `1.4.0`;
- SQLAlchemy `2.0.35`;
- greenlet `3.3.2`;
- asyncpg `0.29.0`;
- Alembic `1.13.0`;
- FastAPI `0.115.0`;
- Pydantic `2.9.0`;
- pydantic-settings `2.5.0`;
- every required distribution metadata path and module import origin beneath
  the new task-local venv;
- no user-site visibility;
- no import origin from `/opt/homebrew`, `/opt/miniconda3/lib/.../site-packages`,
  the accepted R6 venv, or another shared environment;
- a sealed wheel inventory with filename, normalized distribution, version,
  byte size and SHA-256;
- an exact installed-distribution inventory and dependency-consistency result;
- `python -m pip check` success;
- exact local CLI checks: `python -m pytest --version`,
  `python -m alembic --version`, and the repository migration head
  `000000000004 (head)`.

Use exact binary wheels. Do not install from an sdist. You may reuse an existing
wheel only after hashing it and proving its filename/tag is compatible. If an
exact required wheel is not locally available, you are authorized to request
the normal sandbox/network approval and download only exact public PyPI wheels
into the task-local wheelhouse. Do not use a private index, credentials or an
unversioned/latest requirement. Record the index host and downloaded filenames,
but never retain raw network output if it can contain environment information.

Installation must occur from the sealed local wheelhouse with network disabled
or `--no-index --find-links`. Do not install anything globally or into the R6
environment.

The future target suite may require additional packages. Determine the necessary
runtime closure from frozen repository requirements and static imports; pin,
download and seal every package you actually install. Do not run test collection
to discover imports. Direct project/test module import that could execute fixture
or DB setup is forbidden. Safe stdlib/importlib metadata probes and the exact CLI
version/head checks above are allowed.

Produce a reusable fail-closed gate. It must reject at least:

1. missing venv;
2. system-site-packages enabled;
3. user-site visible;
4. Python path/hash/version drift;
5. pytest path/hash/shebang drift;
6. missing wheel;
7. extra unexpected wheel;
8. wheel byte/hash drift;
9. sdist or incompatible wheel;
10. missing required distribution;
11. distribution version drift;
12. distribution metadata outside the venv;
13. module origin outside the venv;
14. `pip check` failure;
15. pytest/Alembic CLI nonzero or version drift;
16. no, multiple or wrong Alembic heads;
17. timeout; and
18. forbidden environment/database connection names present.

The positive receipt must be `READY` and explicitly authorize only the later
maintenance phase of this R8 task. Negative receipts must set
`next_actions_authorized=false`, retain no raw child output or traceback, and
prove zero Docker, credential, socket, SQL, proof, collect-only, pytest-test,
database or supervisor activity.

### TOP-AC-03 — Test-driven helper/contract proof

Before implementation, create a RED contract test inside the R8 evidence tree
that reproduces the old unsafe condition: the previous executable/interpreter
binding cannot satisfy the new closure contract. Capture the nonzero result and
precise safe category without a database connection.

Then implement the R8 gate/helpers and obtain GREEN across the positive case and
all required negative cases. The test suite must be offline, deterministic and
must not import or execute application tests. Run Ruff with `--no-cache`, AST
parse checks and source-hash comparison on every R8 helper snapshot.

### TOP-AC-04 — Exact fail-closed maintenance preconditions

Only after TOP-AC-02 and TOP-AC-03 are GREEN may you perform one formal
maintenance supervisor invocation with `require_escalated`.

Before any mutation, the formal supervisor must, in this order:

1. validate the sealed R8 runtime gate receipt;
2. perform at most one selective read-only Docker preflight for the accepted
   `desktop-linux` / `thesisguard-postgres` / PostgreSQL 17 runtime;
3. perform at most one unauthenticated `pg_isready` check;
4. perform at most one credential-free TCP check of `127.0.0.1:15432`;
5. invoke the already accepted frozen secure identity proof once, through a
   parent/child boundary where the parent never reads, receives, logs or writes
   the connection value;
6. require the safe identity result to equal
   `current_database=postgres`, `current_user=thesisguard`,
   `postgres_server_major=17`;
7. read a sanitized catalog snapshot and compare it to the complete accepted R7
   post-run catalog, including the 45 historical entries and historical hash;
8. prove the exact target name/OID/owner/owner-OID/template/allow-connections
   tuple still matches; and
9. prove `pg_stat_activity` has zero sessions for the exact target.

Credential handling must retain only safe result fields. The connection value
must not appear in argv, parent environment, report, evidence, temp files or raw
child output. Raw exceptions and tracebacks must not be retained.

If Docker/readiness/TCP/identity/catalog/target/session state differs, stop before
mutation with a precise `BLOCKED_*` result. Do not retry and do not broaden the
target.

### TOP-AC-05 — Exact residual restoration

There are only two valid live-state branches:

1. **Target still present and exact.** Execute exactly one quoted
   `DROP DATABASE` statement for
   `tg_wp04_service_1161dc4e02604c5ba23d157af5436b71`, without `FORCE`, after
   all TOP-AC-04 checks pass. Then verify the target is absent.
2. **Target already absent.** Execute no mutation. This branch may be successful
   only if the complete live catalog already exactly equals the accepted R7
   pre-run catalog and the historical hash still matches. Classify it
   `SUCCESS_ALREADY_RESTORED_NO_MUTATION`.

For branch 1, the post-mutation catalog must equal the accepted R7 pre-run
catalog exactly:

- total count `49`;
- target absent;
- every non-target database identity unchanged;
- historical database count `45`;
- historical-state hash exactly
  `3b28f630bff3c1b2842e8e4b46787c588df9feaeabe3db9d356a51b4258a6f05`;
- no sessions for the removed target;
- no other mutation.

Budgets for the formal maintenance phase:

- escalated supervisor: at most `1`;
- supervisor retry: `0`;
- secure-proof parent/child/retry: at most `1/1/0`;
- authenticated identity connections/queries/schema-valid results: at most
  `1/1/1`;
- catalog/target read-only queries: only the minimum explicitly accounted for;
- target drop attempts: at most `1`;
- successful database mutations: at most `1`;
- `DROP ... FORCE`: `0`;
- `pg_terminate_backend`: `0`;
- Docker mutations: `0`;
- manual or wildcard cleanup: `0`;
- new database creates: `0`;
- migration runs: `0`;
- collect-only: `0`;
- real project pytest test invocations: `0`.

### TOP-AC-06 — Evidence closure

Publish a strict, privacy-safe evidence package containing at least:

- task context and baseline Git identity;
- changed-path scope and protected-input before/after hashes;
- independent-review path/hash verification;
- RED and GREEN contract results;
- sealed runtime contract;
- base Python, venv, entrypoint, wheel and installed-distribution inventories;
- wheel hashes/bytes/tags and acquisition provenance;
- safe import/version/origin receipt;
- `pip check`, pytest version, Alembic version and Alembic head receipts;
- positive gate receipt and every negative-case result;
- Ruff, AST and helper-hash results;
- command/mutation budget;
- selective Docker/readiness/TCP safe receipts if reached;
- secure-identity invocation audit and safe result if reached;
- sanitized catalog-before, exact-target and zero-session receipts if reached;
- exact drop receipt or already-restored receipt;
- sanitized catalog-after and exact restoration audit;
- execution event ledger and finalization order;
- strict JSON/JSONL audit;
- credential/raw-secret/raw-exception scan;
- repository `__pycache__` audit;
- evidence manifest with SHA-256 and byte size for every final evidence file;
- execution report checksum.

All JSON must reject duplicate keys and non-finite numbers. JSONL must validate
each nonblank line independently. The final evidence scanner must report zero
credential findings and zero raw exception/traceback retention. Do not place a
secret-shaped example token in the final scanner source or evidence.

The finalizer may repair only evidence formatting/manifest/checksum issues after
the formal phase. It must never rerun the runtime gate, Docker, proof, SQL,
database mutation, collection or pytest.

## 6. Ordered execution protocol

Use this exact high-level ordering and fail closed at each boundary:

### Stage A — baseline and frozen inputs

- Confirm exact baseline and clean isolated worktree.
- Read R7 report/evidence and the independent review.
- Hash all protected inputs and capture the complete accepted R7 before/after
  catalog snapshots.
- Define explicit task paths and zeroed command/mutation budgets.

### Stage B — RED without external side effects

- Write contract tests first inside the R8 evidence tree.
- Demonstrate that the old Homebrew pytest binding fails the new closure
  contract, using safe local metadata/import probes only.
- Store only sanitized classification and hashes; no raw traceback.

### Stage C — build and seal task-local runtime

- Create a fresh no-system-site-packages venv in the authorized `/private/tmp`
  root.
- Acquire exact binary wheels if necessary, seal their inventory, and install
  only from the local wheelhouse.
- Seal the runtime contract before GREEN validation.
- Never modify the accepted R6 runtime.

### Stage D — GREEN and local gate

- Run all positive/negative contract cases.
- Run Ruff, AST, source-hash, `pip check`, import/provenance, pytest-version,
  Alembic-version and exact-head checks.
- Produce the positive `READY` receipt.
- If any required check fails, stop before Docker and before credentials.

### Stage E — one escalated maintenance supervisor

- Request escalation exactly once with a clear justification that this will
  perform read-only identity/catalog checks and, only on exact match, one
  non-FORCE drop of the single R7-owned temporary database.
- Run the ordered preconditions and the exact restoration branch from TOP-AC-04
  and TOP-AC-05.
- Do not retry on any failure.

### Stage F — postconditions and evidence closure

- Verify the exact catalog restoration and protected inputs.
- Close all handles before finalization.
- Generate strict evidence, report, manifest and checksum.
- Run verify-only finalizer checks.
- Create exactly one evidence-only Git commit.
- Recheck sole-parent ancestry, scope, clean status and no repository pycache.

## 7. Formal statuses and stop classifications

Use `IMPLEMENTATION_COMPLETE_AWAITING_INDEPENDENT_ACCEPTANCE` only when:

- the deterministic runtime is fully GREEN and `READY`;
- the exact R7 residual is absent;
- the entire catalog equals the accepted R7 pre-run catalog;
- every historical identity/hash is preserved;
- all evidence closure checks pass; and
- the evidence-only commit/worktree conditions pass.

Otherwise use `EXECUTION_FAIL_AWAITING_INDEPENDENT_ACCEPTANCE` or a precise
`BLOCKED_*_AWAITING_INDEPENDENT_ACCEPTANCE`, including the first failed stage and
safe category. Examples include:

- `BLOCKED_BASELINE_MISMATCH`;
- `BLOCKED_TOOLCHAIN_WHEEL_ACQUISITION`;
- `FAIL_PYTEST_RUNTIME_CONTRACT`;
- `BLOCKED_DOCKER_PREFLIGHT`;
- `BLOCKED_SECURE_IDENTITY`;
- `BLOCKED_CATALOG_DRIFT`;
- `BLOCKED_RESIDUAL_IDENTITY_MISMATCH`;
- `BLOCKED_RESIDUAL_HAS_SESSIONS`;
- `FAIL_EXACT_DROP`;
- `FAIL_CATALOG_RESTORATION`;
- `FAIL_EVIDENCE_PROTOCOL`.

Do not convert a failure into PASS by narrowing the contract after execution.
Do not attempt a second formal supervisor or second drop.

## 8. Required final report

Create:

`docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R8-PYTEST-RUNTIME-AND-RESIDUAL-RESTORE-R1-execution-report.md`

Create evidence at:

`docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R8-PYTEST-RUNTIME-AND-RESIDUAL-RESTORE-R1-evidence/`

Your final response and report must state, at minimum:

- exact status and first failure classification, if any;
- worktree path and branch/detached state;
- baseline, full HEAD/evidence commit and commit parent;
- changed-file count, out-of-scope count and final clean state;
- independent-review path/hash result;
- RED/GREEN/negative-case counts;
- task-local runtime root;
- Python/pytest/pytest-asyncio/SQLAlchemy/greenlet/asyncpg/Alembic/
  FastAPI/Pydantic versions and proven origins;
- wheel count, hash mismatch count, sdist count, pip-check result;
- user-site/system-site status;
- pytest CLI and Alembic CLI/head results;
- package download/install counts and locations;
- default-sandbox and escalated supervisor counts;
- Docker/readiness/TCP/proof counts and safe results;
- target name/OID/owner/session preconditions;
- exact drop attempted/succeeded or already-restored branch;
- database mutation/force-drop/backend-termination/manual-cleanup counts;
- catalog and historical counts/hashes before/after;
- collect-only and real pytest test counts, both required to be `0`;
- application source/test/fixture/migration/config modification counts;
- protected-input mismatches;
- repository pycache count;
- credential/raw-exception findings;
- strict JSON/JSONL totals and invalid count;
- manifest missing/extra/hash/byte mismatch counts;
- report and evidence paths;
- `next full DB reverify allowed=NO — awaiting independent acceptance`;
- `R11 allowed=NO`;
- `integration allowed=NO`.

Do not claim WP-04-02 or WP-04 complete. Both remain
`PARTIALLY_IMPLEMENTED`. Do not claim production readiness. Strategy status
remains `UNPROVEN`.

Begin now. Do not ask the user to restate information already supplied. Request
only the tool approvals actually required by the exact public-wheel acquisition
or one formal PostgreSQL maintenance supervisor.
