# TASK-WP04-02 R7 Evidence Security Proof Protocol Repair R1 — Independent Review R1

**OVERALL: BLOCKED**

**Reason: `BLOCKED_REGRESSION_GATE_CONTRACT_CONFLICT`**

## Metadata

- Task ID: `TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R1`
- Review ID: `TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R1-FEEDBACK-INDEPENDENT-REVIEW-R1`
- Date: 2026-09-24, Asia/Shanghai
- Verifier: Codex independent verifier; separate from the reported repair executor
- Report Path: `docs/acceptance/TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R1-FEEDBACK-INDEPENDENT-REVIEW-R1-acceptance.md`
- Implementation Status: delivered at implementation commit `9ba733448ba2941f70cc109cffb2399986ff7cc2`; evidence commit `43df5fbf9e2b1a748ebd7ac22e8ba02c2832285b`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, narrowly scoped `L4_RUNTIME_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`; `L2_BUILD_VERIFIED` for the two new files; substantial but incomplete `L3_CONTRACT_VERIFIED`
- Missing Acceptance: task-wide all-green regression gate; complete credential-scanner negative coverage; narrowly scoped `L4_RUNTIME_VERIFIED`
- Repair Required: `YES`
- Next Repair ID: `TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R2`

## Independent conclusion

The executor's fail-closed stop is sustained. The live PostgreSQL proof was correctly not invoked after the contract's offline regression gate returned nonzero. This result is not evidence of a business-service failure, PostgreSQL outage, fixture-lifecycle failure, or failed 41-scenario suite.

The new parent/child proof protocol itself is materially implemented and independently passes its 56 deterministic tests. It retains numeric child return codes, maps fixed failure stages, rejects malformed or contradictory success documents, uses a fixed child environment, drops stderr, bounds stdout, and excludes raw diagnostic fields from failure records.

The blocking regression failure is caused by a contract/test-context conflict outside the R1 allowed modification scope. `wp04_02_r4_runner.py` intentionally pins historical main commit `675217c3a15c0f416aa4462ca6edc491bf99f9f6`, while `test_collect_only_end_to_end` passes the moving main checkout at `/Users/qianduoduo/Desktop/AI_app/ThesisGuard`. At R1 execution time that checkout was `282d37055b39dde7772dfca443f814c243c43dd9`; it can never satisfy the runner's historical identity check. The existing runner and test were byte-for-byte outside the R1 implementation commit, and the same failure is independently reproduced.

The correct successor is not to weaken or move the historical runner pin. It is to make the end-to-end regression test create an isolated local detached checkout at the runner's pinned `MAIN_HEAD`, then pass that checkout to the runner. R2 must explicitly authorize this narrow existing-test change.

## Changed Files Snapshot

- `BASELINE_CHANGED_FILES`: protected main had no tracked/index change; `docs/workbench.html` was pre-existing untracked input.
- Implementation changes: `tg_verifier_tools/verification/wp04_02_secure_pg_proof.py` and `tg_verifier_tests/verification/test_wp04_02_secure_pg_proof.py`.
- Closure changes: the R1 execution report and its evidence directory.
- Existing `wp04_02_r4_runner.py` and `test_wp04_02_r4_runner.py`: unchanged between `282d3705...` and implementation commit `9ba7334...`.
- Current observed remote state: `origin/main@43df5fbf9e2b1a748ebd7ac22e8ba02c2832285b`, which now contains the R1 implementation and evidence commits. The original execution report says its executor did not push or merge; this later integration is observed but not attributed by this review.
- Task-attributable Changes: certain for commits `9ba7334...` and `43df5fb...`; later integration actor is unknown.
- Attribution: `CERTAIN` for content, `ATTRIBUTION_UNCERTAIN` for the later move of `origin/main`.

## Classification

- Task Type: `SECURITY`, `REPAIR`, `OPERATIONS_VERIFIER_TOOLING`
- Risk Type: credential disclosure, subprocess isolation, evidence integrity, one-shot PostgreSQL proof
- Touched Layers: verifier CLI, deterministic tests, evidence/reporting; no business code or database mutation
- Task Size: `MEDIUM`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G4 Test, G5 Regression, G6 Evidence
- Not Applicable Gates: DB Persistence for this review because no live proof or persistence operation ran

## Top Blocking AC Results

| Top AC | Result | Evidence |
|---|---|---|
| Retain numeric child return code and fixed safe stage without raw diagnostics | PASS | source review plus independent 56/56 deterministic suite |
| Reject malformed, contradictory, oversized and cross-invocation child output | PASS | independent deterministic suite; strict schema at `validate_success_stdout` |
| Preserve credential isolation across argv, environment, stdout/stderr and evidence | PARTIAL | fixed argv/environment and strict output paths pass; scanner counterexamples below remain uncovered |
| Complete all required offline regression gates | BLOCKED | independent combined run is 137/138; only historical main-pin mismatch fails |
| Execute exactly one schema-valid read-only PostgreSQL proof after offline gates | NOT RUN | invocation, connection, SELECT and retry counts are all zero |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS with post-delivery drift note | required `282d3705...` is an ancestor; reviewed commits and hashes exist; current remote is now `43df5fb...` |
| G1 Scope | PASS | implementation commit changes only the two authorized new proof files; closure commit adds report/evidence |
| G2 Contract | BLOCKED | historical runner requires `675217c3...` but required test supplies moving main; R1 forbade changing either existing runner or test |
| G3 Architecture | PASS | parent/child boundary, fixed exit map, bounded transport and no-clobber publisher are coherent for the stated repair |
| G4 Test | BLOCKED task-wide | 56/56 new tests pass; combined gate is 137/138 |
| DB Persistence | NOT_APPLICABLE | no SQL session or live proof was executed |
| G5 Regression | BLOCKED | 81/82 existing runner tests; the single failure is independently attributable to the historical pin/live-main mismatch |
| G6 Evidence | PASS for the blocked delivery | 29 declared files = 29 actual, zero byte/hash mismatch; source snapshots match live files |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary / Negative Evidence | Verdict |
|---|---|---|---|---|---|
| AC-01 [BLOCKING] | Credential-safe deterministic parent/child protocol | `wp04_02_secure_pg_proof.py` fixed environment, exit map and strict JSON schema | 56/56 independent deterministic tests | malformed, multiple, trailing, oversized, contradictory and unknown-return-code cases exercised | PASS |
| AC-02 [BLOCKING] | Existing runner behavior remains valid | R1 does not modify runner/test | 81/82 runner tests; combined 137/138 | failure is `expected 675217c3... got 282d3705...`; same files unchanged in implementation commit | BLOCKED |
| AC-03 [BLOCKING] | Credential scanner supports final evidence safety | scanner detects conventional `scheme://user:password@...` and quoted sensitive assignments | existing scanner self-tests pass | independent memory-only cases for colonless URL userinfo and unquoted password query both return zero findings | PARTIAL; must harden before live proof |
| AC-04 [BLOCKING] | One real read-only identity proof | child contains one fixed SELECT path | not run | proof budget unconsumed; SQL connection and query counts zero | NOT ACHIEVED |
| AC-05 [BLOCKING] | Complete, parseable, no-clobber evidence | R1 report, source snapshots, audits and manifest | independent manifest rebuild: 29/29, mismatch 0; source hashes match | `git-final-state.json` still says evidence commit pending, so final commit identity is supplied by Git rather than that sealed inner field | PASS for blocked delivery; final-state field is advisory inconsistency |

## Commands Actually Executed

| Command/check | Result | Purpose |
|---|---|---|
| `pytest ... test_wp04_02_secure_pg_proof.py` | 56 passed | independent proof-protocol verification |
| `pytest ... test_wp04_02_r4_runner.py` | 81 passed, 1 failed | reproduce existing runner gate |
| combined two-file pytest command | 137 passed, 1 failed | reproduce exact blocking regression result |
| Python compileall with `/private/tmp` pycache | exit 0 | syntax/build verification |
| Ruff check / format check with `/private/tmp` cache | exit 0 / exit 0 | static and formatting verification |
| `git diff --check 282d3705..43df5fb` | exit 0 | patch integrity |
| implementation-scope diff | existing runner and existing runner test unchanged | regression attribution |
| source/evidence SHA-256 comparison | exact matches for both new source snapshots | evidence attribution |
| independent recursive manifest audit | 29 declared, 29 actual, mismatches 0 | evidence integrity |
| memory-only scanner counterexamples | 0 findings for both tested credential shapes | identify pre-proof scanner gap without reading real credentials |

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| New proof code introduced the runner failure | yes | runner and runner test have no implementation-commit diff; same failure reason is deterministic | rejected |
| Changing `MAIN_HEAD` to current main is the correct repair | yes | runner pins historical source hashes and historical commit identity | rejected; would weaken reproducibility |
| Using moving main in a historical end-to-end test is stable | yes | exact mismatch reproduced after main advanced | rejected |
| Final scanner detects every relevant URL credential shape | yes | two synthetic, memory-only forms produce no finding | rejected; add focused regression coverage before proof |
| Live proof, R8 or DB mutation occurred | yes | formal counters and report are zero; no contrary artifact observed | not observed |

## Blocking Findings

1. **Regression gate contract conflict.** The old end-to-end test uses a moving checkout while the runner intentionally requires a historical immutable checkout. R1 correctly stopped because fixing that test was prohibited.
2. **Pre-proof scanner hardening required.** The scanner's current regular expressions do not flag colonless URL userinfo or unquoted sensitive URL query values. No real credential was found in R1 artifacts, but a zero-finding scan is not a sufficient future safety gate until these negative cases are covered.

## Non-Blocking Findings

1. `git-final-state.json` records the evidence commit as pending even though Git now shows `43df5fb...` as the evidence commit. This is understandable for a manifest-sealed bundle but should be represented as a pre-commit state explicitly in future evidence.
2. `origin/main` now contains a delivery whose own report states `BLOCKED`. This review does not infer who integrated it; future governance should require independent acceptance before merging subsequent high-risk verifier changes.

## Regression Result

- Result: `BLOCKED` by test-context mismatch, not by a newly introduced functional regression.
- Preserved behavior: all 56 proof-protocol tests; 81 non-end-to-end runner tests; source and evidence hashes.
- Regression gaps: isolated historical-main checkout and scanner edge cases must be added; live proof remains unexecuted.

## Repair Required

- YES
- Repair ID: `TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R2`
- Failed AC/Gate: task-wide regression gate, scanner negative coverage, narrowly scoped runtime proof.

## Final Decision Rationale

`BLOCKED`. The implementation is sufficiently present for static/build review and its primary deterministic protocol behavior passes, but the immutable contract did not allow the only necessary regression-test context repair. The executor correctly withheld the one-shot proof. Because no live PostgreSQL result exists and the scanner has uncovered negative-case gaps, the complete repair cannot receive PASS.

## Next Action

Dispatch one combined R2 to a new Codex operations/security repair executor. In one session it should: isolate the historical main checkout in the existing end-to-end test; harden scanner coverage; rerun all offline gates; and, only if all gates pass, consume exactly one read-only proof and publish a new no-clobber R2 bundle. zcode is not eligible. A separate fresh Codex verifier remains required only after that single combined execution finishes.
