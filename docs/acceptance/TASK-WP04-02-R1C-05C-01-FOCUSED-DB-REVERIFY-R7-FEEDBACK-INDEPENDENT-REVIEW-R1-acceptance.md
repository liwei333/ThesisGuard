# TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R7 Feedback Independent Review R1

**OVERALL: FAIL**

**Reason: `FAIL_EVIDENCE_SECURITY_CONTRACT`**

## Metadata

- Task ID: `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R7`
- Review ID: `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R7-FEEDBACK-INDEPENDENT-REVIEW-R1`
- Date: 2026-09-23, Asia/Shanghai
- Verifier: Codex independent feedback verifier; not the R7 executor
- Report Path: `docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R7-FEEDBACK-INDEPENDENT-REVIEW-R1-acceptance.md`
- Required Acceptance for R7: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_RUNTIME_VERIFIED`, focused `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED` for the exact baseline; fresh collect-only contract verified
- Missing Acceptance: `L2_BUILD_VERIFIED`, task-wide `L3_CONTRACT_VERIFIED`, `L4_RUNTIME_VERIFIED`, focused `L4_DB_VERIFIED`
- Overall Verdict: `FAIL`
- Repair Required: `YES`
- Repair ID: `TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-REPAIR-R1`

## Independent Result

The R7 verdict is independently sustained as `FAIL_EVIDENCE_SECURITY_CONTRACT`.

R7 did not produce evidence of a business assertion failure, fixture lifecycle regression, PostgreSQL service outage, catalog drift, or concurrent database activity. It stopped before a successful SQL connection, catalog query, formal 120-second window, real pytest invocation, fixture ledger, or `CREATE DATABASE`. Those capabilities remain unverified rather than failed.

The blocking failure is narrower and earlier: after passwordless authentication was unavailable, the verifier reported that it displayed a tracked source excerpt containing plaintext development credential material in retained tool output while searching for the existing connection mechanism. Reproducing that disclosure would repeat the prohibited action and is neither necessary nor safe. Independent review instead confirmed, without printing a value, that exact integrated source contains a credential-bearing PostgreSQL URL literal in the focused-test path. Combined with the executor's explicit admission and immediate fail-closed stop, this is sufficient to reject the R7 invocation under its evidence-security contract. A zero-finding scan of the final report/evidence does not erase an earlier retained tool-output disclosure.

## Changed Files Snapshot

- `BASELINE_CHANGED_FILES`: main tracked diff and index were empty; R7 recorded 257 protected pre-existing untracked files.
- `FINAL_CHANGED_FILES`: main tracked diff and index remain empty; R7 added only its acceptance report and evidence directory. Its protected-input comparison records the same 257 entries before and after with zero missing, extra or changed entry.
- Task-attributable Changes: R7 acceptance report and R7 evidence directory only.
- Attribution: `CERTAIN`

## Classification

- Task Type: `SECURITY`, `DB_PERSISTENCE`, `INDEPENDENT_ACCEPTANCE`
- Risk Type: credential disclosure, retained tool output, database integrity, one-shot execution budget, evidence completeness
- Touched Layers: Git/source baselines, collect-only harness, Docker/PostgreSQL preflight, verifier evidence
- Task Size: `MEDIUM`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G4 Test, DB Persistence, G5 Regression, G6 Evidence
- Not Applicable Gates: G3 Architecture; R7 was not an implementation task

## Top Blocking AC Results

| Top AC | Result | Independent evidence |
|---|---|---|
| Exact immutable baseline and fixed inputs | PASS | Fresh refs/status agree with R7; report and manifest hashes match the delivery |
| Fresh safe 41-node collect-only | PASS | R7 bundle records 41 unique nodes, exact `20/16/3/2`, zero body/socket/ledger/CREATE; inner manifest independently reconstructs `10/10` |
| No credential is read, printed or retained outside the approved opaque channel | **FAIL** | R7 executor explicitly reports retained tool-output disclosure; safe boolean source check confirms a credential-bearing URL literal exists in the focused-test source path |
| Live PostgreSQL identity, catalog and quiescence | NOT RUN after blocking failure | successful SQL connections, catalog queries and formal window invocations are all zero |
| Exactly one complete 41-scenario real DB run and resource closure | NOT RUN after blocking failure | real pytest, CREATE, DROP and ledger counts are all zero |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | `main@5c4b930f...`, exact parent chain, candidate/harness/repair refs and fixed hashes matched |
| G1 Scope | PASS | no tracked or index change; only R7 report/evidence added; 257 protected inputs preserved |
| G2 Contract | **FAIL** | explicit evidence-security prohibition was violated before SQL preflight |
| G3 Architecture | NOT_APPLICABLE | no implementation change was authorized |
| G4 Test | FAIL / INCOMPLETE | collect-only passed; required real pytest was correctly not started after the security failure |
| DB Persistence | FAIL / NOT VERIFIED | no authenticated SQL session, catalog, ledger or real DB test exists |
| G5 Regression | NOT VERIFIED | full repaired 41-scenario behavior remains unexecuted |
| G6 Evidence | PASS for the FAIL result | final bundle is internally complete and accurately records the stop boundary; it cannot convert the failed security gate into PASS |

## Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary / Negative Evidence | Verdict |
|---|---|---|---|---|---|
| AC-01 [BLOCKING] | Preserve exact Git/source baseline | integrated main and fixed commits | fresh refs/status; fixed R7 report/manifest hashes | no source, index or ref mutation | PASS |
| AC-02 [BLOCKING] | Prove exact scenario inventory without runtime side effects | accepted harness | R7 collect-only audit and independently rebuilt inner manifest | zero body/socket/ledger/CREATE | PASS |
| AC-03 [BLOCKING] | Prevent credential disclosure in source inspection, argv, environment capture, stdout/stderr, tool output and evidence | R7 credential-handling contract | executor admission plus safe boolean confirmation of a credential-bearing literal in the focused path | final artifact scan is clean but does not cover or revoke prior retained tool output | **FAIL** |
| AC-04 [BLOCKING] | Authenticate and obtain live PostgreSQL identity/catalog safely | expected local PostgreSQL service | Docker identity and `pg_isready` were observed; SQL identity is null | successful SQL connections and catalog queries are zero | NOT ACHIEVED |
| AC-05 [BLOCKING] | Complete one real 41-node run with exact resource closure | integrated lifecycle repair | not run | pytest/CREATE/DROP/ledger budgets remain unused | NOT ACHIEVED |
| AC-06 [BLOCKING] | Preserve complete, parseable, credential-clean formal artifacts | R7 report/evidence | root manifest independently reconstructs `28/28`; all JSON parses; final credential scan has zero findings | artifact cleanliness does not repair transient retained output | PASS for FAIL delivery |

## Commands Actually Executed by This Review

| Command/check | Result | Purpose |
|---|---|---|
| Git branch/ref/parent/diff/index checks | exact baseline; tracked diff and index empty | baseline |
| SHA-256 of R7 report and manifest | `fae6114e...c4e6` / `a38739e6...35a3` | delivery identity |
| independent recursive R7 manifest rebuild | 28 actual = 28 declared; zero path/byte/hash mismatch | evidence integrity |
| independent collect-only inner-manifest rebuild | 10 actual = 10 declared; zero mismatch | collection evidence integrity |
| parse all R7 JSON files | success | evidence syntax |
| compare protected before/after entry sets | 257 = 257; canonical entry hashes equal | scope preservation |
| safe boolean scan for credential-bearing URL literal in exact test source | present; no credential value emitted | confirm disclosure risk surface without reproducing it |
| independent credential-pattern scan of final R7 report/evidence | no non-allowlisted credential URL or private-key finding | formal-artifact safety boundary |

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| Final zero-finding scan is incorrectly treated as proof that no earlier disclosure occurred | yes | R7 explicitly records earlier retained tool-output disclosure | rejected; security gate remains FAIL |
| Collect-only silently executed bodies or opened sockets | yes | body count 0, socket attempts 0, no ledger or CREATE | not observed |
| Real pytest or CREATE budget was consumed despite the stop | yes | execution budget records 0/0 | not observed |
| Historical or protected untracked inputs were modified | yes | 257 before/after entries have identical canonical hash | not observed |
| R7 result is mislabeled as a business or fixture failure | yes | no SQL identity, catalog, pytest or ledger evidence exists | rejected; those paths are unverified, not failed |

## Blocking Finding

`FAIL_EVIDENCE_SECURITY_CONTRACT`: R7 lacked a pre-approved opaque authentication/connection channel that a verifier could use without inspecting or displaying the credential-bearing test-source literal. The verifier then disclosed such material in retained tool output. This violates a blocking security condition even though the final repository evidence bundle contains no credential value.

## Regression Result

- Result: `NOT VERIFIED` for the real 41-scenario database behavior.
- Preserved behavior: exact Git/source baseline and safe 41-node collect-only contract remain intact.
- Regression gaps: live SQL identity, 49-database catalog, 45 historical identities, 120-second quiescence, 41 real scenarios, ledger closure and before/after catalog equality were not run.

## Repair Required

- `YES`
- Repair ID: `TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-REPAIR-R1`
- Failed AC/Gate: credential-handling AC; G2 Contract; prerequisite to G4/DB Persistence

The repair must establish and independently verify a narrowly scoped opaque credential channel for the focused verifier. It must allow the verifier's helper process to obtain the existing development connection material internally while preventing the value from appearing in source-inspection output, argv, retained environment snapshots, process metadata, stdout, stderr, tracebacks, reports or evidence. It must not run the 41-scenario suite or alter application behavior.

## Final Decision Rationale

`FAIL`. R7 correctly failed closed, and its final artifacts accurately preserve that result. The contract violation is a proven blocking security failure; the unused real pytest and CREATE budgets do not permit bypassing the required repair. Because no real database suite ran, this result says nothing adverse about the repaired fixture or the 41 business assertions.

## Next Action

Dispatch exactly one repair task: `TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-REPAIR-R1`, to a Codex operations/security repair executor. Do not route it to zcode. After implementation delivery, use a separate Codex session for independent repair acceptance. Only after that repair receives PASS may a new one-shot R8 focused DB verification be dispatched with new output paths.
