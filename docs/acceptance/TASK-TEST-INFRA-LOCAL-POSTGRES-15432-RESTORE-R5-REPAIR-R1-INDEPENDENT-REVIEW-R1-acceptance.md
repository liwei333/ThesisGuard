# TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R5-REPAIR-R1 — Independent Acceptance R1

## 1. Verdict

**OVERALL: PASS**

The R5 repair delivery is accepted for its narrowly defined purpose: repairing the retained PostgreSQL-service evidence helpers and producing a fresh, internally bound, fail-closed proof that the existing local PostgreSQL prerequisite was healthy and quiescent during the formal observation window.

This acceptance does **not** establish focused business-test `L4_DB_VERIFIED`, does not approve WP-04-02 as a whole, and does not authorize 05C-02, R1D, WP-04-03, Git integration, source-code changes, database cleanup, or any trading capability.

## 2. Review Identity and Separation of Duties

- Repair executor: Codex operations repair executor, as recorded in the R5 repair execution report.
- Independent verifier: a separate Codex acceptance session.
- Repair task: `TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R5-REPAIR-R1`.
- Acceptance task: `TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R5-REPAIR-R1-INDEPENDENT-REVIEW-R1`.
- Review date: 2026-09-23.
- Repository branch observed by the verifier: `main`.
- Repository HEAD observed by the verifier: `5c4b930f4948815e3ad2ab26b5e7c81de8c20e5b`.
- Parent: `bd6b5b88783fd4de4d7d89787778e1b36bb4006e`.
- Grandparent: `35349b207d622872bc0025a813ff3e6af6ef7d97`.
- Local `origin/main`: `77abbe72decfe5437ffed90521b8101f1eae1153`.
- Tracked working-tree diff and index at review start: empty.

The verifier did not participate in the repair implementation and did not treat the executor's `IMPLEMENTATION_COMPLETE` declaration as acceptance evidence by itself.

## 3. Reviewed Inputs

The verifier reviewed the complete retained repair delivery, including:

- `TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R5-REPAIR-R1-execution-report.md`
- the complete `TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R5-REPAIR-R1-evidence/` tree
- retained repaired observer, supervisor, closure-helper and test sources
- all pre-window gate receipts and the gate index
- formal stability-window invocation, seven timeline samples, completion marker and outcome
- credential scan, JSON parse audit, evidence-consistency audit and root manifest
- before/after protected-untracked snapshots
- the fixed historical R5/R4 inputs referenced by the repair contract

The executor report SHA-256 independently matched:

`02adb5e4161992c3c2b467e6fd522252716b4456700fa8c221f110801a2e3a1d`

The root repair manifest SHA-256 independently matched:

`7d2209b896f959cd1f5736b42c998cb652a41bd2500c5c4540c0a4328a17f862`

## 4. Acceptance Results

### AC-R5R-01 — No-clobber durable publication

**PASS**

The retained publisher creates a task-owned temporary file with exclusive creation, writes and fsyncs it, atomically publishes it with `os.link(..., follow_symlinks=False)`, removes only its own temporary file, and fsyncs the parent directory. It does not use a replace operation that can overwrite a target created by another process.

The verifier independently injected a competitor target immediately before the publish link. The operation raised `FileExistsError`, preserved the competitor bytes, and left no task-owned temporary files. This closes the prior target-existence race.

### AC-R5R-02 — Complete pre-window gate and cryptographic binding

**PASS**

The retained gate index contains exactly 14 prerequisite receipts. Independent reconstruction confirmed, for every receipt:

- the declared relative path exists;
- byte length and SHA-256 match;
- the task and invocation identities match;
- the required success criteria are true;
- the receipt completed before the gate index;
- the gate index completed before the formal stability-window invocation.

The independently recomputed gate-index SHA-256 is:

`4fe778816bd65d81c2a9f72bd9c178b4059dcb531df0f5bcc19c17ab0f5d8464`

That same hash is bound into the invocation record, every one of the seven samples, the completion record, and the final outcome. The supervisor validates the index before publishing the formal invocation. Therefore the formal window is not merely adjacent to, but cryptographically bound to, the complete prerequisite gate.

### AC-R5R-03 — Formal PostgreSQL stability window

**PASS**

The retained formal invocation identity is:

`1F2E2619-E72E-4D65-8F30-5BB87497BB27`

Independent review confirmed:

- sample sequence is exactly `0..6`;
- scheduled offsets are `0, 5, 10, 15, 20, 25, 30` seconds;
- recorded duration is `30.009698` seconds;
- child process return code is `0`;
- completion is explicitly recorded;
- catalog count remains `49` in every sample;
- canonical catalog SHA-256 remains `5b347fab6f6a78e2fa9749bc0e0c97cd387273c31fe39495ab060ad016dc9910` and matches preflight;
- maximum external active client count is `0`;
- maximum `tg_wp04_service_%` session count is `0`.

The prerequisite receipts also retain the exact existing Docker/PostgreSQL identity, accepting `pg_isready`, PostgreSQL identity, exact 45/45 historical UNKNOWN comparison, absence of the historical R5 residual database, and absence of extra databases at the gate boundary.

The verifier did not open a new PostgreSQL session or rerun the one-shot formal window. Acceptance is based on the independently authenticated, internally bound runtime artifacts plus source and test verification; it does not consume or replace the later focused DB verification budget.

### AC-R5R-04 — Fail-closed evidence closure

**PASS**

The retained closure state machine enforces the order:

`PAYLOADS_FINAL -> CREDENTIAL_SCAN_FINAL -> JSON_PARSE_AUDIT_FINAL -> MANIFEST_FINAL`

Independent review confirmed:

- final credential scan precedes the final JSON parse audit;
- the credential-scan SHA-256 embedded in the JSON audit matches the retained scan file;
- the JSON-audit SHA-256 is included in the root manifest;
- the root manifest includes the final credential scan and JSON audit and excludes only itself;
- manifest actual/declared eligible files are exactly `38 / 38`;
- paths, types, byte lengths and SHA-256 values all match;
- all 34 JSON files and all seven JSONL records parse;
- no `__pycache__` or `.pyc` artifact is retained;
- `manifest.json` is the final evidence file by modification order.

The independent credential-pattern scan found no credential-bearing PostgreSQL URL, URL userinfo, or private-key marker in the report and retained evidence scope.

### AC-R5R-05 — Regression and negative-path verification

**PASS**

The verifier copied the retained repaired sources to a fresh `/private/tmp` directory and ran the complete retained test module with bytecode writing disabled.

Result:

- tests run: `65`
- passed: `65`
- failures: `0`
- errors: `0`

The suite preserves all 26 earlier tests and adds 39 tests covering no-clobber publication, prerequisite-gate validation and ordering, gate binding, bytecode suppression, closure sequencing, and evidence-finalization failures.

### AC-R5R-06 — Repository and protected-state preservation

**PASS**

The repair's before and after protected-untracked snapshots contain the same 216 protected entries. The verifier independently reconstructed the current untracked state while excluding only the repair's own allowed report/evidence outputs and obtained the same 216 paths, types, byte lengths and SHA-256 values.

No evidence was found of repair-attributable source changes, Git staging, commit, merge, rebase, reset, clean, stash, push, migration, fixture execution, database creation/deletion, database cleanup, backend termination, Docker object mutation, or focused pytest execution.

## 5. Evidence Matrix

| Requirement | Independent evidence | Result |
|---|---|---|
| Safe publication cannot overwrite a competing target | retained source review, retained tests, independently injected race | PASS |
| Complete prerequisite gate exists before formal invocation | 14 receipts, gate index, timestamps, independent byte/hash reconstruction | PASS |
| Formal window is bound to the validated gate | independently recomputed gate-index hash in invocation, all samples, completion and outcome | PASS |
| Stability observation is complete and quiescent | seven samples over 30.009698 seconds, stable catalog/count, zero observed activity | PASS |
| Closure is ordered and fail-closed | closure state machine, credential scan, JSON audit, manifest order and hashes | PASS |
| Evidence bundle is complete and reproducible | 38 actual = 38 declared; zero path/byte/hash mismatches | PASS |
| Existing protected untracked state is preserved | 216 before = 216 after = independent current reconstruction | PASS |
| Prior helper behavior is not weakened | 26 prior tests retained; 65/65 complete suite passed | PASS |

## 6. Required Acceptance Levels

- `L1_STATIC_REVIEWED`: **ACHIEVED** for the R5 repair source and retained delivery.
- `L2_BUILD_VERIFIED`: **ACHIEVED** for the retained helper source through a fresh isolated 65-test run.
- `L3_CONTRACT_VERIFIED`: **ACHIEVED** for the four repair acceptance conditions and their fail-closed negative paths.
- PostgreSQL-service-scope `L4_RUNTIME_VERIFIED`: **ACHIEVED** for the specific retained R5 repair observation and its bound 30-second quiescence window.
- Focused business-suite `L4_DB_VERIFIED`: **NOT ESTABLISHED / OUT OF SCOPE**.

## 7. Findings

No blocking finding remains within the repair contract.

The repaired helpers are retained evidence tooling for this controlled operation; this acceptance does not promote them into application runtime code or authorize an unrelated generalized framework.

## 8. Final Decision and Next Gate

The repair task is accepted and may be closed as **PASS**. No further repair round is required for `TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R5-REPAIR-R1`.

The only justified next task is a new, one-shot focused PostgreSQL verification under a fresh task ID and fresh output paths. It must be executed by a **new Codex independent DB verifier** that did not perform the R5 repair or this acceptance. It must re-check the live service and catalog immediately before execution and must not infer current runtime health solely from this historical acceptance.

Recommended next task ID:

`TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R7`

No zcode dispatch is appropriate because the next task requires real PostgreSQL observation, destructive test-fixture lifecycle controls, and final independent verification.
