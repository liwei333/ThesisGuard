# TASK-WP04-02-R1C-05A — Independent Acceptance

**OVERALL: FAIL**

## Metadata

- Task ID: `TASK-WP04-02-R1C-05A`.
- Date: 2026-09-16, Asia/Shanghai.
- Verifier: Codex, independent verifier role using `ai-task-governor`.
- Report path: `docs/acceptance/TASK-WP04-02-R1C-05A-acceptance.md`, following the repository's existing `docs/acceptance` convention.
- Implementation status received: `IMPLEMENTATION_COMPLETE`; treated as evidence input, not approval.
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Achieved acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, and partial L3/L4 evidence for new-request denial, exact matching replay, ordinary lifecycle and no-residue behavior.
- Missing acceptance: complete `L3_CONTRACT_VERIFIED` and `L4_DB_VERIFIED` for changed initial-verification audit-tuple replay conflicts.
- Repair required: YES.
- Repair ID: `TASK-WP04-02-R1C-05A-R1`.

This FAIL does not reject the new-request default-deny rule or the disclosed historical fixture separation. It rejects the task as a whole because a blocking replay counterexample required by the contract remains fail-open. R1D, final WP04-02 re-verification and Git integration remain unauthorized.

## Changed-files snapshot and classification

The authorized starting baseline was already dirty with the accepted R1C-04A changes in exactly two files. The independently observed final candidate remains on branch `codex/wp04-02-evidence-domain-service`, HEAD `0cef44fd2ffd929b40e849e607af0bd4c44d14d2`, parent `bdd70edc153b6ed5def65ed99c41f325df45f066`, with exactly:

```text
 M backend/evidence/services.py
 M tests/test_evidence_services.py
```

Final SHA-256 values match the execution feedback:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
cd4fd5a32a6cebe123e76e0a668cafc6f19e4455863af1a954c7f06bff511207  backend/evidence/services.py
f8c36c6e2efdc549f0d36da5cb7575cf60892b188c4926350fa658bbcb8f1386  tests/test_evidence_services.py
```

Main remains at `438738c543e4cae3e805d31324b068c1cd5c7059`, parent `7d3734bc8346c16f9bbf7f7d9806309949c996de`, with empty tracked/index diff. Existing untracked governance evidence was preserved. This verification adds this acceptance, a durable verifier and the R1 Repair Contract. Attribution is CERTAIN from the fixed R1C-04A input hashes and final two-file hashes.

- Task type: REPAIR / backend domain service.
- Risk: eligibility, DB persistence, audit identity, idempotent replay and historical compatibility.
- Touched layers: service and PostgreSQL tests.
- Task size: MEDIUM.
- Evidence matrix: Full.
- Selected gates: G0, G1, G2, G3, G4, DB Persistence, G5 and G6.

## Top Blocking AC results

| Top AC | Result | Evidence |
|---|---|---|
| Genuine pre-fix business RED | PASS | Executor log hash was recomputed and records two business assertion failures on the fixed R1C-04A service hash, not an environment failure. |
| New no-predecessor initial VERIFIED request fails closed before writes | PASS | `services.py:698-704` rejects after exact replay lookup and before series/version construction. Candidate focused test and fresh PostgreSQL run pass. |
| Exact historical replay only for the same request; changed status tuple conflicts | **FAIL** | Verifier-owned four-case PostgreSQL test changes exactly one of `status_changed_at`, actor, kind or reason while retaining the same key and all hash-covered fields. All four unexpectedly return the historical response: `4 failed`, each `DID NOT RAISE EvidenceIdempotencyConflict`. |
| Ordinary UNREVIEWED/review/verify and accepted R1C/R1B/R1A regression remain green | PASS | Executor hash-bound logs record 87 R1C-04A, 58 oracle, 70 fixed verifiers, 333 full service and 35 regression passes. Fresh candidate R1C-05A focused run is 7 passed. |
| Historical test fixture is disclosed and separate from production capability | PASS | Static review confirms the helper creates constraint-legal ORM history only in the test module; there is no production monkeypatch, environment switch, public bypass or approved positive rule. |

## Gate results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Contract, fixed input/output hashes, branch/HEAD/status, execution logs and diff are accessible and attributable. |
| G1 Scope | PASS | Candidate remains within the two authorized files; no schema/API/dependency/Git-history change occurred. |
| G2 Contract | **FAIL** | Required changed-status-tuple replay conflict is not implemented; the candidate test changes the status enum at the same time and therefore does not isolate the four audit fields. |
| G3 Architecture | **FAIL** | Idempotent replay treats four materially different lifecycle audit requests as identical, weakening audit ownership and request identity at a production service boundary. |
| G4 Test | **FAIL** | Candidate's seven focused tests pass, but the verifier-owned contract counterexample fails all four parameters. Coverage was insufficient to prove the blocking replay condition. |
| DB Persistence | **FAIL** | Real PostgreSQL execution shows the service returns an existing eligible exact version for a request with a changed audit tuple. It does not write residue, but its durable replay semantics are incorrect. |
| G5 Regression | PASS | Previously accepted paths remain green in executor logs; the failure is localized to the missing replay distinction. |
| G6 Evidence | PASS | Evidence is sufficient for a definitive FAIL: code location, task-contract wording, fresh DB counterexample and candidate-focused control are all available. |

## Full evidence matrix

| AC | Requirement | Implementation evidence | Verification evidence | Boundary/negative evidence | Verdict |
|---|---|---|---|---|---|
| AC-01 | New unqualified initial VERIFIED requests reject before writes | Fail-closed guard at `services.py:698-704` | Candidate focused `7 passed`; static order review | New key and lawful setup no-residue case | PASS |
| AC-02 | Matching committed historical request replays read-only | Replay branch at `services.py:681-694`; seeded COMMITTED record | Candidate focused matching replay passes | Same payload/new key rejects | PASS |
| AC-03 | Changed display/source/locator/status tuple cannot borrow replay | Hash payload at `services.py:667-679`; candidate test at `tests/test_evidence_services.py:4700-4756` | Durable verifier `test_wp04_02_r1c05a_audit_tuple_replay_r1_20260916.py`: `4 failed` | Isolated changes to time, actor, kind and reason all return old response | **FAIL** |
| AC-04 | Ordinary lifecycle and prior accepted behavior remain legal | Existing commands and disclosed historical seed | Executor regression logs plus fresh 7-case focused run | Initial UNREVIEWED then review/verify remains green | PASS |
| AC-05 | No fake positive validator or production test bypass | Production diff contains only the denial guard; fixture seed is test-only | Static review, fixed approved set remains empty | No monkeypatch/env flag/public registry | PASS |

## Root evidence

The production request hash for `create_evidence_series_version` is built from the mapping at `backend/evidence/services.py:667-679`. It includes `verification_status` but omits all four lifecycle audit fields:

```text
status_changed_at
status_changed_by_actor
status_change_kind
status_reason
```

The production replay branch at `services.py:681-694` returns the previous exact response immediately after the hash match; it performs no post-replay comparison of those four fields.

The candidate negative test labelled `changed_part="status"` at `tests/test_evidence_services.py:4732-4738` changes `verification_status` from `VERIFIED` to `UNREVIEWED` at the same time as clearing the audit tuple. Because `verification_status` is already hash-covered, this test passes without proving that an isolated audit-tuple change conflicts.

Fresh verifier command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<candidate>:<existing-libraries> \
pytest -p no:cacheprovider -q \
  docs/acceptance/verifiers/test_wp04_02_r1c05a_audit_tuple_replay_r1_20260916.py -rs
```

Actual result:

```text
FFFF
4 failed in 3.66s
```

Every failure is `Failed: DID NOT RAISE EvidenceIdempotencyConflict`. The verifier SHA-256 is recorded below and must not be edited by the repair executor.

```text
be68779f161c5983fce265bafe0b8237ae881feea7900a446c07ff03433ffb60  docs/acceptance/verifiers/test_wp04_02_r1c05a_audit_tuple_replay_r1_20260916.py
```

Candidate-owned focused control executed independently:

```text
7 passed, 326 deselected in 5.33s
```

This contrast proves a contract-coverage gap rather than a PostgreSQL or fixture outage.

## Commands actually executed by this verifier

| Command | Result | Purpose |
|---|---|---|
| Candidate `pytest ... -k r1c05a -rs` | `7 passed, 326 deselected` | Confirm candidate's advertised focused behavior and environment health |
| Verifier-owned isolated audit-tuple PostgreSQL test | `4 failed`; all expected conflicts absent | Test the missing blocking counterexample |
| Ruff check and format check for the three files | pass | Fresh L2 verification |
| mypy for the three files | success, no issues | Fresh L2 verification |
| Git status/HEAD/diff/hash inspection | expected two-file scope; hashes match | Baseline and attribution |
| Executor manifest/log SHA and byte-size recomputation | all declared result logs match | Confirm submitted evidence was not altered |

## Findings

### Blocking

1. **Changed initial-verification audit tuple is incorrectly treated as exact replay.** The service returns the previously committed eligible exact version when only time, actor, kind or reason changes under the same key. This violates Top AC 3, the explicit high-risk counterexample, audit request identity and fail-closed replay semantics.
2. **Candidate test does not isolate the claimed condition.** Its `status` vector also changes the already-hashed `verification_status`; it therefore cannot prove any one of the four omitted audit fields participates in conflict detection.

### Non-blocking / preserved

- New unqualified initial VERIFIED requests are denied before writes.
- Matching historical exact replay remains read-only.
- The test-only historical seed is disclosed and does not add a production success path.
- Production positive initial import and positive trusted correction remain unimplemented, as required.
- Static quality and previously accepted regressions remain green according to fresh/static checks and hash-verified execution logs.

## Final decision and next action

One blocking AC fails on a fresh real-PostgreSQL counterexample; therefore `OVERALL = FAIL`. The fact that the candidate's seven focused tests pass cannot override the missing audit-tuple distinction.

Execute `TASK-WP04-02-R1C-05A-R1` next. The repair must add isolated coverage for all four audit fields and make mismatching historical replay raise `EvidenceIdempotencyConflict` without expanding the whole R1D hash program or breaking exact legacy replay. No later feature task may begin until R1 is independently re-verified.
