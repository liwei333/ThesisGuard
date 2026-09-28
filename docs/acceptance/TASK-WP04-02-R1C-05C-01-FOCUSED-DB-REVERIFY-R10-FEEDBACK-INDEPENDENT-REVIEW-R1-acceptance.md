# TASK-WP04-02-R1C-05C-01 Focused DB Reverify R10
# Feedback Independent Review R1

## 1. Verdict

**OVERALL: FAIL**

**Confirmed and refined classification:**
`FAIL_EVIDENCE_PROTOCOL / SUPERVISOR_DOCKER_EXECUTABLE_RESOLUTION_FAILURE`

R10 did not reach Docker inspection, PostgreSQL readiness, TCP, secure identity,
collection, catalog observation, real pytest, or database-lifecycle verification.
The task-local supervisor attempted to launch the bare executable name `docker`
under a fixed `SAFE_ENV.PATH` that excludes `/usr/local/bin`, while the host's
Docker CLI resolves to `/usr/local/bin/docker`. The resulting
`FileNotFoundError` is a deterministic task-owned helper defect, not an
unavailable external PostgreSQL prerequisite. Therefore the correct task
verdict is `FAIL`, not `BLOCKED`.

The failed run was fail-closed and its evidence bundle is internally coherent.
That evidence integrity does not satisfy the R10 runtime or database acceptance
contract. R11 and integration remain prohibited.

## 2. Metadata

| Field | Value |
|---|---|
| Review task | `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-FEEDBACK-INDEPENDENT-REVIEW-R1` |
| Original task | `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10` |
| R10 worktree | `/Users/qianduoduo/.codex/worktrees/527d/ThesisGuard` |
| Branch state | detached HEAD |
| R10 baseline / evidence-commit parent | `6e341e7d225c5c5a34c000e0c8b41a0f18f53f42` |
| R10 evidence commit / HEAD | `3b8650ee069b6eb364520d5ae127ee205bb4345d` |
| Review date | 2026-09-26 Asia/Shanghai |
| Verifier | independent Codex |
| Report path | `docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-FEEDBACK-INDEPENDENT-REVIEW-R1-acceptance.md` |
| Task type | `OPERATIONS + TESTING + REAL_POSTGRESQL_VERIFICATION` |
| Risk type | one-shot budget, credential boundary, database lifecycle, evidence integrity |
| Task size | `MEDIUM` |
| Evidence matrix | Full |

Required acceptance:

- `L1_STATIC_REVIEWED`
- `L2_BUILD_VERIFIED`
- `L3_CONTRACT_VERIFIED`
- `L4_RUNTIME_VERIFIED`
- `L4_DB_VERIFIED`

Achieved acceptance is limited to `L1_STATIC_REVIEWED` and task-local helper
static quality checks under `L2_BUILD_VERIFIED`. The R10 contract, runtime and
database tags were not achieved.

## 3. Scope and attribution

Included in this independent review:

- exact commit ancestry, detached state and changed-file scope;
- the R10 report and complete final evidence tree;
- sealed supervisor source, fixed subprocess environment and launch shape;
- event sequence, not-run matrix and command/mutation budgets;
- protected-input and worktree before/after evidence;
- manifest, report hash, JSON/JSONL and credential-disclosure integrity; and
- classification, gate verdict and minimum Repair selection.

Explicitly excluded:

- rerunning the already-consumed R10 supervisor;
- Docker daemon inspection, socket access, credentials, SQL or proof execution;
- collect-only or real pytest execution;
- database create/drop, cleanup or historical-database mutation;
- source, test, fixture, migration or production behavior changes;
- merge, rebase, cherry-pick, push, PR or integration; and
- R11 or later WP-04 work.

The evidence commit has the exact R10 baseline as its sole parent. It adds 25
files, all under the exact R10 report/evidence paths, and `git show --check`
passes. The R10 worktree was clean at independent review time.

## 4. Decisive root evidence

The sealed supervisor defines:

```text
SAFE_ENV.PATH=/opt/homebrew/bin:/opt/homebrew/opt/postgresql@16/bin:/opt/miniconda3/bin:/usr/bin:/bin
```

Its D-stage preflight calls:

```text
run_safe(["docker", "context", "show"])
```

Fresh read-only host resolution confirmed:

```text
normal PATH: /usr/local/bin/docker
sealed SAFE_ENV.PATH: docker not resolvable
```

The host path is a symlink to the Docker Desktop CLI. No Docker CLI command was
launched by the failed supervisor because executable resolution failed before
process creation. The supervisor's generic exception handler classified the
exception in finalization as stop stage `P / FileNotFoundError`; the causal
boundary is the attempted transition into D. The sealed event chain is exactly:

```text
A NO_CLOBBER_CONFIRMED
B WORKTREE_GIT_HASH_GATES_PASSED
C FROZEN_PROOF_RESOLVED
P FINAL_AUDITS_STARTED
Q FORMAL_OUTPUT_READY_FOR_EXCLUSIVE_PUBLISH
```

There is no D-stage completion event. The offline validation covered AST,
Ruff, gate ordering, proof resolution, import side effects, sanitization,
no-overwrite publishing, manifest exclusion and a single pytest call site, but
did not verify that each external executable resolves under the exact formal
subprocess environment. This missing launch-environment preflight is the
regression the Repair must add.

## 5. Runtime and database claims rejected

The following R10 target claims are **not verified** and must not inherit values
from R9 Repair or other historical evidence:

- Docker context/container/image/health/volume/restart/port identity;
- `pg_isready` success;
- credential-free TCP reachability for this R10 run;
- secure proof parent/child execution and safe PostgreSQL identity;
- exact collection of 41 nodes with the frozen `20/16/3/2` partition;
- historical 45 database name/OID/owner protection;
- live catalog count, R5/R10 residual checks and client-session checks;
- 120-second quiescence and runtime-observer timelines;
- one real 41-node pytest invocation and its result counts;
- fixture create/drop ledger integrity and restoration; and
- 30-second post-run observation.

The correct current values are `NOT_RUN` or `UNKNOWN`, with invocation counts
zero where the sealed budget records a count. In particular, proof
parent/child/retry is `0/0/0`, collect-only is `0`, and real pytest/retry is
`0/0`. This run supplies no `L4_RUNTIME_VERIFIED` or `L4_DB_VERIFIED` result.

## 6. Preserved safe behavior

The following failure-handling boundaries are accepted and must be preserved:

- formal outputs did not exist before execution and were published once;
- the artifact records one approved escalated supervisor invocation and zero
  default-sandbox formal supervisor invocations;
- there was no supervisor retry;
- Docker CLI, readiness, TCP, proof, collect-only and real pytest invocation
  counts are zero after the executable-resolution failure;
- task database create/drop sends, manual cleanup, `DROP ... FORCE`,
  `pg_terminate_backend`, Docker mutation and historical-database mutation are
  all zero;
- 11 protected inputs match before and after;
- task-created or changed pycache entries are zero;
- the recorded main, R9 Repair, candidate and lifecycle checkout snapshots
  match before and after; and
- raw exception or credential values were not retained.

These facts establish a safe failure, not a successful R10 verification.

## 7. Fresh independent integrity checks

Fresh checks performed without Docker, network, credentials, SQL, proof,
collection or pytest execution confirmed:

- `HEAD=3b8650ee069b6eb364520d5ae127ee205bb4345d`;
- `HEAD^=6e341e7d225c5c5a34c000e0c8b41a0f18f53f42`;
- exact ancestry and changed-file scope: 25 files, out-of-scope 0;
- manifest: 23 listed files, 23 actual non-manifest files, missing/hash/byte
  mismatch `0/0/0`;
- report SHA-256:
  `c1e422393e1dbc3ef5a3a3e1aed22fbeb505f5d16a89bb90b09bc62569ebf8bc`;
- manifest SHA-256:
  `50001cbd6906ff115f2727db9504b2092be21a189c49c319040dae9c4ffe7537`;
- final JSON/JSONL: 21 files, 25 documents, invalid 0;
- final credential scan: 24 evidence files plus the report, findings 0;
- protected-input before/after diff: 0;
- worktree-snapshot before/after diff: 0;
- sealed helper Ruff result: `All checks passed!`; and
- independent AST parsing: 2 files parsed successfully.

The sealed `credential-disclosure-scan.json` reports 20 evidence files because
it was generated before the final helper snapshots and closing artifacts were
added. The independent final-tree scan covered all 24 evidence files and the
report and found no credential pattern, so this generation-order difference is
non-blocking for the failed evidence bundle.

## 8. Full evidence matrix

| Blocking acceptance condition | Result | Independent evidence |
|---|---|---|
| Exact baseline, clean isolation and no out-of-scope source mutation | PASS | parent/HEAD, detached state, 25-path scope and snapshots verified |
| No-clobber, fixed hashes and frozen proof identity | PASS | events A-C, 11 protected hashes and proof hash evidence are consistent |
| Every formal external executable is resolvable before runtime budget consumption | FAIL | `docker` is absent from sealed PATH; actual CLI is `/usr/local/bin/docker` |
| Selective Docker/readiness/TCP preflight succeeds | FAIL | all are `NOT_RUN`; no D completion event |
| One secure identity proof succeeds within budget | FAIL | parent/child/retry `0/0/0` |
| Exact 41-node collection contract is verified | FAIL | collect-only invocation 0; observed collection unknown |
| Historical catalog and quiescence are protected | FAIL | catalog/quiescence/observer are `NOT_RUN` |
| One real focused pytest run passes all 41 nodes | FAIL | invocation/retry `0/0`; result counts unknown |
| Fixture lifecycle and final catalog restoration are verified | FAIL | no ledger or live before/after/post-run evidence |
| Failure preserves credentials, protected inputs and mutation boundaries | PASS | final scan 0, mismatch 0, mutation counts 0 |
| Evidence is parseable, complete and tamper-evident | PASS | manifest, report hash and JSON/JSONL checks independently pass |

## 9. Acceptance gates

| Gate | Result | Reason |
|---|---|---|
| G0 Baseline | PASS | Exact parent, detached HEAD, clean status and ancestry verified |
| G1 Scope | PASS | Evidence-only 25-file commit; out-of-scope paths 0 |
| G2 Contract | FAIL | Mandatory D-O runtime/database acceptance path never executed |
| G3 Architecture | NOT_APPLICABLE | No production architecture change |
| G4 Test/runtime | FAIL | External executable launch precondition failed before all target checks |
| DB Persistence | FAIL | Required real PostgreSQL and lifecycle verification was not reached |
| G5 Regression | FAIL | Offline suite omitted exact formal executable-resolution coverage |
| G6 Evidence | PASS | Failed attempt is coherently sealed and independently reproducible statically |

Because blocking G2, G4, DB Persistence and G5 fail, `OVERALL=FAIL`.

## 10. Counterexamples

| Risk | Result |
|---|---|
| Treat a sealed evidence bundle as proof the target runtime ran | Rejected: events and budgets show no D-O execution |
| Treat R9's identity PASS as R10 identity evidence | Rejected: R10 proof count is zero |
| Treat actual Docker installation as proof the helper can launch it | Rejected: the helper's own fixed PATH cannot resolve it |
| Treat `P / FileNotFoundError` as a PostgreSQL environment blocker | Rejected: causal failure is the task-owned D-stage launcher configuration |
| Retry or edit the helper inside the consumed R10 attempt | Preserved: retry 0 and original artifacts are sealed |
| Leak secrets while diagnosing | Preserved: independent final scan findings 0 |

## 11. Repair decision

**Repair required: YES**

Repair ID:

`TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R10-REPAIR-R1`

The next task must be a new isolated Repair based on the exact sealed R10
evidence commit `3b8650ee069b6eb364520d5ae127ee205bb4345d`. It must not modify, overwrite,
clean, or continue the failed R10 worktree or its formal outputs.

The Repair must:

1. add an offline RED/GREEN regression for exact external-executable
   resolution under the formal subprocess environment;
2. resolve and pin every required executable before any Docker/network/SQL/
   proof/collect/pytest budget is consumed, using validated absolute paths or an
   equivalently deterministic mechanism;
3. preserve the frozen proof identity, one-shot/no-retry rules, credential
   boundary, historical catalog protections and all previously passed R10
   evidence boundaries;
4. publish to new Repair-specific no-clobber report/evidence paths; and
5. only after all offline/preflight gates pass, consume one new explicitly
   authorized Repair runtime budget for the complete original R10 D-O sequence.

The Repair executor may report only `IMPLEMENTATION_COMPLETE_AWAITING_INDEPENDENT_ACCEPTANCE`,
`EXECUTION_FAIL_AWAITING_INDEPENDENT_ACCEPTANCE`, or
`BLOCKED_AWAITING_INDEPENDENT_ACCEPTANCE`. It cannot self-approve.

Until this Repair independently passes:

- R11 allowed: **NO**
- Integration allowed: **NO**
- Candidate accepted: **NO**
- WP-04-02 / WP-04 status: **`PARTIALLY_IMPLEMENTED`**
- Production readiness: **not established**
- Strategy status: **`UNPROVEN`**
