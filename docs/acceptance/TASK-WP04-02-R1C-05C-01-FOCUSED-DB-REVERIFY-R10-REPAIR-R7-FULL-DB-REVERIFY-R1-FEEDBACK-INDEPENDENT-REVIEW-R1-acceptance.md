# TASK-WP04-02-R1C-05C-01 Focused DB Reverify R10 Repair R7
# Full DB Reverify R1 — Feedback Independent Review R1

**OVERALL: FAIL**

**Exact independent classification:**
`FAIL_EXECUTION_TOOLCHAIN / PYTEST_INTERPRETER_DEPENDENCY_CLOSURE_MISMATCH`

## 1. Decision

R7 does not pass independent acceptance. Its one authorized real PostgreSQL
pytest invocation collected the exact 41-node focused suite but passed no test:
the first scenario failed and its fixture teardown errored because the frozen
absolute pytest executable used Homebrew Python 3.12 under
`PYTHONNOUSERSITE=1`, while that interpreter could not import `greenlet`.

The same teardown failure prevented disposal of the async SQLAlchemy engine and
the owned temporary database was not dropped. The accepted lifecycle facts are
therefore exactly one attempt, one database create, zero drops and one cleanup
failure. The post-run catalog contains one R7-owned residual database:

- name: `tg_wp04_service_1161dc4e02604c5ba23d157af5436b71`;
- OID: `9273601`;
- owner: `thesisguard`;
- owner OID: `10`;
- active sessions at the sealed observation: `0`.

The executor correctly stopped without retry, manual cleanup, `DROP ... FORCE`,
backend termination, a second secure proof or a second pytest run. Evidence
closure, privacy controls, historical-database preservation and protected-input
hashes pass. Those facts do not cure the blocking runtime and lifecycle failures.

The independently confirmed cause is broader than a single missing import. The
Homebrew pytest process resolved SQLAlchemy `2.0.52` and asyncpg `0.31.0`, while
the repository freezes SQLAlchemy `2.0.35` and asyncpg `0.29.0`. Adding only a
mutable `greenlet` fallback would therefore not establish the deterministic
pytest runtime contract required before another database run.

This FAIL authorizes only a new Repair that builds and proves a deterministic
pytest runtime and, under a separate fail-closed maintenance phase, removes the
one exact R7-owned residual after revalidating its name, OID, owner and absence of
sessions. It does not authorize another collect-only run, another real pytest,
R11, integration, product completion or any production-readiness claim.

## 2. Metadata

| Field | Value |
|---|---|
| Review task | `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R7-FULL-DB-REVERIFY-R1-FEEDBACK-INDEPENDENT-REVIEW-R1` |
| Execution task | `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R7-FULL-DB-REVERIFY-R1` |
| Review date | 2026-09-26 Asia/Shanghai |
| Verifier | independent Codex |
| Worktree | `/Users/qianduoduo/.codex/worktrees/r10-r7-full-db-reverify/ThesisGuard` |
| Branch state | detached managed worktree, clean |
| Baseline / evidence-commit parent | `1bfc85927c6e0f6edab11c07f2fd0d77e8db385d` |
| Evidence commit / HEAD | `1613c89209f91a4bb64dab04c588250b0b5f6a85` |
| Commits after baseline | `1` |
| Changed scope | 77 added files: one report plus 76 task evidence files |
| Task type | `TESTING + DATABASE + EVIDENCE` |
| Task size | `LARGE` |
| Evidence matrix | Full |

Required acceptance tags and result:

- `L1_STATIC_REVIEWED`: achieved;
- `L2_BUILD_VERIFIED`: achieved for the sealed helpers and evidence tooling;
- `L3_CONTRACT_VERIFIED`: partial only; pre-publication contract evidence says
  29/29, while the fresh published-tree replay is 28/29 because the
  pre-publication `exact_rebinding` case expects paths that publishing creates;
- `L4_RUNTIME_VERIFIED`: failed for the focused pytest runtime;
- `L4_DATABASE_PERSISTENCE_VERIFIED`: failed for lifecycle/restoration.

## 3. Scope and attribution

Fresh Git inspection establishes that `1613c89209f91a4bb64dab04c588250b0b5f6a85`
has the exact accepted R6 evidence commit as its sole parent, is the only commit
after that baseline, and adds only the R7 report and evidence tree. The detached
worktree is clean. No application source, project test, fixture, migration,
declared dependency, main worktree, R6 worktree, candidate source worktree or
historical evidence was modified by the R7 evidence commit.

`git show --check` is clean except for three preserved trailing spaces in the two
explicitly sanitized stdout captures. Those bytes are sealed evidence and are not
treated as source-quality defects.

The main worktree already contained unrelated untracked historical acceptance
reports and `docs/workbench.html`. This verifier preserved them and adds only
this independent-acceptance report.

Included in this review:

- Git ancestry, changed scope and clean state;
- R7 report and the complete sealed evidence bundle;
- supervisor ordering, invocation budgets and stop behavior;
- Docker/readiness/TCP/secure-identity/collection receipts;
- exact pytest stdout, interpreter identity and package provenance;
- lifecycle ledger and before/after PostgreSQL catalog evidence;
- protected-input, historical-state, JSON/JSONL, manifest and privacy checks;
- fresh helper Ruff/AST/hash verification; and
- fresh local, non-database Python import probes.

Excluded from this review:

- a second secure proof, collection or real pytest invocation;
- database cleanup or any database mutation;
- Docker mutation or container restart;
- source, fixture, migration or dependency changes;
- merge, rebase, cherry-pick, push, PR, R11 or integration.

## 4. Selected gates

| Gate | Result | Independent evidence |
|---|---|---|
| G0 Baseline | PASS | exact parent, one task commit, clean detached worktree |
| G1 Scope | PASS | changed paths are report/evidence only; protected inputs mismatch `0` |
| G2 Contract | FAIL | R7 gate proves Alembic, but not the pytest interpreter's dependency/version closure |
| G4 Test | FAIL | real pytest: 41 collected, 0 passed, 1 failed, 1 teardown error |
| L4 Runtime | FAIL | Homebrew pytest Python cannot import `greenlet`; runtime packages drift from frozen requirements |
| DB persistence | FAIL | one create, zero drops, one cleanup failure; catalog not restored |
| G5 Regression | PASS WITH BLOCKER | 45 historical databases and historical hash preserved, but one new R7 residual exists |
| G6 Evidence | PASS | manifest, strict JSON/JSONL, helper hashes, report checksum and privacy scan close |

Because G2, G4, runtime and database-persistence gates are Blocking for this
full-DB task, the overall result is FAIL even though the evidence package itself
is internally complete.

## 5. Top Blocking AC results

| Top AC | Result | Independent evidence |
|---|---|---|
| TOP-AC-01 exact baseline, isolated clean worktree and evidence-only commit | PASS | fresh Git checks confirm `HEAD`, `HEAD^`, one-commit count, changed paths and clean status |
| TOP-AC-02 all offline/pre-runtime gates must prove the actual pytest child | FAIL | Alembic resolves from R6 venv, but `/opt/homebrew/bin/pytest` uses a different interpreter without `greenlet` and with dependency-version drift |
| TOP-AC-03 exactly one ordered formal supervisor run, with no retry or bypass | PASS | one escalated supervisor; proof/collect/pytest each at most one; retry `0`; no default-sandbox formal run |
| TOP-AC-04 exact 41-node suite must pass and every current-run lifecycle must pair create/drop | FAIL | 41 collected, 0 passed; ledger records attempt/create `1/1`, drop `0`, cleanup-failed `1` |
| TOP-AC-05 post-run catalog must equal the accepted pre-run state | FAIL | catalog count `49 -> 50`; exact R7 residual remains; 45 historical entries are unchanged |
| TOP-AC-06 evidence closure and secret-safety | PASS | manifest `75/75`, strict JSON/JSONL 121 documents valid, privacy findings `0`, report checksum passes |

## 6. Independently confirmed runtime cause

The sealed pytest stdout shows:

- executable: `/opt/homebrew/bin/pytest`;
- shebang: `/opt/homebrew/opt/python@3.12/bin/python3.12`;
- Python: `3.12.9`;
- pytest: `9.1.1`;
- failure: SQLAlchemy async execution raises `ValueError` because
  `No module named 'greenlet'`;
- teardown: rollback/close and engine disposal encounter the same missing
  dependency condition.

A fresh read-only import probe under the same isolation confirms:

- user site disabled;
- `greenlet` is not importable;
- SQLAlchemy `2.0.52` loads from Homebrew site-packages;
- asyncpg `0.31.0` loads from Homebrew site-packages.

The repository instead freezes:

- `sqlalchemy[asyncio]==2.0.35`;
- `asyncpg==0.29.0`;
- `alembic==1.13.0`.

The accepted R6 task-local venv contains SQLAlchemy `2.0.35`, greenlet `3.3.2`
and Alembic `1.13.0`, but it is a system-site-packages environment: pytest,
pytest-asyncio, asyncpg, FastAPI and Pydantic resolve from the Miniconda base.
Its current asyncpg is also `0.31.0`. It is therefore useful evidence and a
possible input to a Repair, but it is not by itself an exact project pytest
runtime closure.

## 7. Database and historical-state result

Accepted lifecycle facts:

- current-run attempt IDs: `1`;
- create events: `1`;
- successful drops: `0`;
- cleanup failures: `1`;
- duplicate/missing lifecycle pairs: `1`;
- manual cleanup: `0`;
- force drop: `0`;
- `pg_terminate_backend`: `0`.

Accepted catalog facts:

- before count: `49`;
- after count: `50`;
- historical count: `45`, unchanged;
- historical-state hash before/after:
  `3b28f630bff3c1b2842e8e4b46787c588df9feaeabe3db9d356a51b4258a6f05`;
- current R7 residual count: `1`;
- residual active-session count at sealed observation: `0`.

The residual must not be generalized into a wildcard cleanup. A future Repair
may remove only the exact name/OID/owner tuple recorded above, only after a fresh
secure identity check and a new no-session check, using a single non-FORCE
`DROP DATABASE` attempt. Any identity, ownership, OID, session or catalog drift
must fail closed without mutation.

## 8. Evidence integrity

Fresh independent verification establishes:

- manifest: 75 declared and 75 actual non-manifest files;
- missing/extra/hash mismatch: `0/0/0`;
- strict JSON/JSONL: 121 parsed documents, invalid/non-finite `0`;
- credential/raw-secret findings: `0` across final report/evidence files;
- helper sources: all eight declared hashes match;
- Ruff `--no-cache`: all eight helper sources pass;
- AST parsing: all eight helper sources pass;
- report checksum: passes from `docs/acceptance`;
- repository `__pycache__`: `0` in the sealed worktree.

The sealed pre-publication R7 contract result is 29/29. A fresh replay from the
published evidence tree is 28/29 because `exact_rebinding` is intentionally
state-dependent and expects the final report/evidence paths to be absent before
publication. The remaining 28 cases, including behavioral fail-closed cases,
pass. This is a non-blocking evidence-design limitation, not the cause of the
formal pytest failure; future evidence finalizers should nevertheless separate
pre-publication-only assertions from replayable post-publication checks.

## 9. Commands actually executed by the verifier

| Command family | Result | Purpose |
|---|---|---|
| Git status/rev-parse/rev-list/show/diff/show-check | PASS | ancestry, scope, clean state and attribution |
| report/evidence/ledger/catalog/pytest capture inspection | PASS | reconstruct the formal result and failure sequence |
| Homebrew isolated Python import/provenance probe | reproduced missing `greenlet` and version drift | independently confirm root cause |
| R6 task-local venv import/provenance probe | SQLAlchemy/greenlet/Alembic local; other packages inherited | determine whether R6 venv alone closes pytest runtime |
| R7 contract replay | 28/29 post-publication | behavior and known publication-state limitation |
| Ruff `--no-cache` and AST parse on eight helpers | PASS | fresh static verification |
| helper SHA-256 comparison | PASS | source identity |
| independent manifest/hash/byte audit | PASS | final evidence closure |
| strict JSON/JSONL parse and non-finite rejection | PASS | machine-readable evidence validity |
| privacy/credential scan and report checksum | PASS | secret-safety and report identity |

No verifier command connected to PostgreSQL, read credentials, opened a socket,
ran SQL, invoked Docker, performed secure proof, collected project tests or ran
project pytest. The exact residual database remains untouched pending an
explicitly governed Repair.

## 10. Routing and next action

Per `AGENTS.md`, this is a real PostgreSQL/toolchain/lifecycle task and remains a
Codex responsibility. zcode is not authorized for ORM/repository, migration,
real PostgreSQL or execution-toolchain repair.

Dispatch record:

- Executor: `Codex`.
- Task: establish a deterministic, fail-closed pytest runtime and restore only
  the exact R7-owned residual database to the accepted catalog baseline.
- Basis: real DB and execution-toolchain domains are Codex-owned; R7 failed a
  blocking runtime/lifecycle condition.
- Scope: evidence/toolchain helper work and one exact guarded residual cleanup;
  no application source/test/fixture/migration changes and no real pytest.
- Acceptor: a different Codex independent review with fresh local and database
  evidence checks.
- Failure takeover: stop fail-closed; do not retry, broaden cleanup or proceed to
  full DB verification.

Authorized next task:

`TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R8-PYTEST-RUNTIME-AND-RESIDUAL-RESTORE-R1`

Current authority remains:

- `R8 Repair allowed = YES`, under its own explicit prompt and approvals;
- `another collect-only or real pytest = NO`;
- `next full DB reverify = NO`, pending independent R8 acceptance;
- `R11 allowed = NO`;
- `integration allowed = NO`;
- WP-04-02 and WP-04 remain `PARTIALLY_IMPLEMENTED`;
- production readiness is not established;
- strategy status remains `UNPROVEN`.
