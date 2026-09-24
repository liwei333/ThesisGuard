# TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R4 — Independent Review R1

## 1. Verdict

**Overall: FAIL**

R4 correctly stopped without claiming `L4_RUNTIME_VERIFIED`, preserved the historical evidence, and retained a coherent failure bundle. However, the missing 30-second stability evidence is not an external prerequisite that was unavailable before execution. The task-owned PostgreSQL observer accumulated all seven samples only in memory and emitted the complete result to stdout after the window ended. It had no incremental durable sample log, no flush/fsync boundary, no atomic completion marker, and no independent exit-status record. Loss of the orchestration output channel therefore erased the only evidence for the required gate.

The executor's `STATUS: BLOCKED` is an honest runtime report, but the independent acceptance result is `FAIL` because the evidence-collection design did not satisfy the task's fail-closed and evidence-retention requirements. R4 does not establish PostgreSQL-service-scope `L4_RUNTIME_VERIFIED` and does not authorize R7 or any focused business/database verification.

## 2. Scope and independence

- Verifier: a separate Codex independent-review session; not the R4 operations executor.
- Review mode: read-only inspection plus this acceptance report only.
- Reviewed delivery:
  - `docs/acceptance/TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R4-execution-report.md`
  - `docs/acceptance/TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R4-evidence/`
- No Docker or PostgreSQL operation was run by this review.
- No R4 command was rerun and no R4 artifact was modified.
- No pytest, fixture, migration, database mutation, cleanup, container mutation, Git mutation, R7 run, or market-provider spike was performed.

## 3. Independent checks

### 3.1 Git and output boundaries

- Current repository identity independently resolves to:
  - `HEAD`: `5c4b930f4948815e3ad2ab26b5e7c81de8c20e5b`
  - parent: `bd6b5b88783fd4de4d7d89787778e1b36bb4006e`
  - grandparent: `35349b207d622872bc0025a813ff3e6af6ef7d97`
  - local `origin/main`: `77abbe72decfe5437ffed90521b8101f1eae1153`
- Tracked worktree diff and index diff are empty.
- The pre-existing untracked state was not treated as clean or as implementation evidence.
- The R4 report and evidence paths are occupied and must remain immutable.

### 3.2 Evidence integrity

- R4 execution report SHA-256: `2548b15ff329b8c04138da359cd398b1e76e8cc8aad24328dc6a7aec045deb0a`.
- R4 root manifest SHA-256: `9ef897b67e9ae418ac92762b1c01841e58c55cb258baa172f425872714f50e03`.
- Independent recursive manifest rebuild, applying the declared exclusions `manifest.json` and `final-credential-scan.json`:
  - declared eligible files: 29
  - actual eligible files: 29
  - missing: 0
  - extra: 0
  - byte-size mismatch: 0
  - SHA-256 mismatch: 0
- All 27 JSON files in the R4 evidence directory parse successfully.
- The protected-untracked before/after snapshots contain 145 entries each and their entry arrays are byte-for-value identical; the declared canonical SHA-256 matches on both sides.
- The 49-row catalog canonical SHA-256 was independently recomputed as `5b347fab6f6a78e2fa9749bc0e0c97cd387273c31fe39495ab060ad016dc9910`, matching the retained preflight JSON.

These checks establish internal integrity of the retained bundle. They do not prove facts that the bundle never retained.

## 4. Acceptance matrix

| Gate | Result | Independent basis |
|---|---|---|
| Fixed Git and input baseline | PASS | Retained values are consistent; current refs match; tracked diff and index are empty. |
| R3 Docker-inspect parser repair | PASS within R4 scope | Retained source is syntactically valid; self-test reports 18/18 synthetic cases; dry run reports zero Docker calls; formal identity JSON is structurally complete. |
| Docker/container point-in-time identity | PASS as retained point-in-time evidence | Exact image, image ID, volume, mount, restart policy, port, running and healthy state are retained. This is not a 30-second stability proof. |
| PostgreSQL point-in-time preflight | PASS as retained point-in-time evidence | Readiness, role/database/version, 49-row catalog, 45/45 protected identities, absent R5 residual, and zero point-in-time external/task-prefix sessions are retained. |
| 30-second stability window | **FAIL** | Zero samples, zero duration, no completion result, and no reliable exit status were retained. |
| Stability evidence durability | **FAIL** | Samples are held only in memory and printed once after completion; there is no incremental durable log or completion record. |
| Historical artifacts preserved | PASS | Protected snapshot comparison is exact and R4 uses fresh paths. |
| Evidence manifest and JSON closure | PASS | Independent rebuild and parse audit succeeded. |
| Credential hygiene | PASS for retained R4 bundle | Retained scans report zero findings; independent review found no credential-bearing URL in the reviewed result fields. |
| PostgreSQL-service-scope `L4_RUNTIME_VERIFIED` | **NOT ACHIEVED** | Required stability gate is absent. |
| Focused `L4_DB_VERIFIED` / WP-04-02 business verdict | NOT RUN / NOT AUTHORIZED | R4 was infrastructure-only. |

Required Acceptance summary:

- `L1_STATIC_REVIEWED`: achieved for the R4 collector and retained evidence.
- PostgreSQL-service-scope `L4_RUNTIME_VERIFIED`: not achieved.
- Focused `L4_DB_VERIFIED`: not run and not authorized.

## 5. Blocking finding

### [P0] The stability observer is not interruption-durable

The retained observer builds `samples` in memory during offsets 0, 5, 10, 15, 20, 25, and 30 seconds (`postgres-observer.source.py`, lines 295–307). It returns the aggregate only after the loop (`lines 308–315`), and the CLI prints the aggregate only after `stability_window` returns (`lines 333–335`). There is no output path argument for a durable timeline, no append-and-flush step after each observation, no `fsync`, and no atomic success marker.

Consequently, the execution channel can lose the entire gate even if some or all observations occurred. The R4 evidence confirms exactly this failure mode: `stability-window.json` retains `sample_count_retained: 0`, `duration_seconds_retained: null`, and `completed: null`; `failure-observation.json` retains no subprocess result beyond the executor's classification. Because the observation was intentionally one-shot, no second invocation could repair the missing record.

This is a task-owned evidence-harness defect. Classifying it only as `ORCHESTRATION_OUTPUT_CAPTURE_LOSS` understates the cause. The orchestration event may have triggered the loss, but a compliant collector must make each completed sample independently recoverable without depending on the final stdout response.

## 6. Positive findings preserved

- R4 did not promote unknown stability facts into a PASS.
- R4 did not rerun the one-shot stability window after losing its output.
- The Docker selective-inspect parser defect that blocked R3 is repaired within the retained R4 helper, with targeted synthetic coverage.
- Docker and PostgreSQL point-in-time observations are internally coherent.
- The fixed 45 historical database identities are reported as exact, and the former R5 residual is reported absent at the preflight observation point.
- Prohibited mutation counters are zero and the evidence bundle is mechanically closed.

These findings may inform the successor contract, but time-sensitive Docker/PostgreSQL state must be observed again. They cannot be copied forward as current runtime proof.

## 7. Required repair and re-verification contract

The successor must use a new task ID and new output paths. Before any real 30-second window, it must replace the stdout-only stability evidence path with an interruption-durable mechanism that:

1. writes one canonical JSONL record immediately after every successful sample;
2. flushes and `fsync`s every appended record;
3. records invocation identity, sequence number, monotonic elapsed time, wall-clock timestamp, catalog count/hash, active-client count, and task-prefix session count in every sample;
4. writes a separate atomic completion/result JSON only after all acceptance checks pass or fail deterministically;
5. writes a structured failure JSON for connection/query/serialization/timeout failures while preserving every prior sample;
6. never treats stdout, terminal transcript, elapsed wall time, or process disappearance as proof of completion;
7. rejects truncated, duplicate, reordered, cross-invocation, too-short, stale, malformed, drifting, or activity-bearing timelines;
8. validates those conditions with synthetic self-tests and a no-Docker/no-PostgreSQL dry run before consuming the single real-window budget.

After the helper passes those gates, the successor must perform a fresh Docker/PostgreSQL preflight and exactly one fresh real 30-second stability window. It must not reuse R4's point-in-time results as current proof.

## 8. Merge and dispatch decision

- R4 acceptance: **FAIL**.
- R4 artifacts: preserve; do not overwrite, rename, delete, or amend.
- R7 focused PostgreSQL re-verification: **NOT AUTHORIZED**.
- 05C-02, R1D, WP-04-03, Git integration, database cleanup, and market-provider work: **NOT AUTHORIZED**.
- Authorized next task type: a narrowly scoped R5 operations-evidence repair and fresh PostgreSQL service re-verification, executed by a new Codex operations executor and independently reviewed by another Codex session.
- zcode is not an eligible executor for this task because the work involves local Docker/PostgreSQL runtime observation and high-integrity evidence handling.

