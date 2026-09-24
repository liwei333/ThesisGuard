# TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R5 Wrong-Session Feedback Review

**OVERALL: BLOCKED**

## Metadata

- Task ID: `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R5`
- Review ID: `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R5-WRONG-SESSION-FEEDBACK-REVIEW`
- Date: 2026-09-22, Asia/Shanghai
- Verifier: Codex feedback-review session
- Report Path: `docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R5-WRONG-SESSION-FEEDBACK-REVIEW-acceptance.md`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, focused `L4_DB_VERIFIED`
- Achieved Acceptance: none for the R5 database-verification task; correct phase-0 fail-closed stop independently accepted
- Missing Acceptance: all R5 required levels
- Repair Required: no source, fixture, harness or database repair established
- Unblock Required: dispatch the replacement R5 contract to a genuinely new Codex task/session

## Decision

The reported `BLOCKED_BASELINE_DRIFT` outcome is correct. The receiving session
was the same Codex operations session that performed
`TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R1`; it therefore did not satisfy
the replacement contract's independent-verifier identity precondition. The
session could not make itself independent by assertion and correctly stopped
before any R5 verification or database-writing step.

This is an executor/session-identity precondition block, not a candidate
failure, harness failure, PostgreSQL failure or R5 business-test result. No
repair task is justified. The correct next action is to re-dispatch the R5
verification to a separate, newly created Codex task with an updated Git
baseline.

## Classification

- Task Type: `DB_PERSISTENCE_INDEPENDENT_VERIFICATION`
- Risk Type: verifier independence, database integrity, resource attribution, audit evidence
- Touched Layers: none; phase 0 stopped before runtime work
- Task Size: `MEDIUM`
- Evidence Matrix Type: Full for the intended R5 task; compact blocker review for this feedback
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G6 Evidence
- DB Persistence Gate: `BLOCKED_NOT_REACHED`
- Test and runtime gates: `BLOCKED_NOT_REACHED`

## Top Blocking AC Results

| Top AC | Result | Evidence |
|---|---|---|
| TOP-AC-01 verifier is a new session independent of restore execution | BLOCKED | Feedback identifies the same session as the restore operations executor and cites its existing restore report/evidence |
| TOP-AC-02 R5 reserved paths remain fresh | PASS | Independent filesystem check: both R5 report and evidence paths are absent |
| TOP-AC-03 stop before any R5 runtime or DB write when identity gate fails | PASS for stop behavior | No R5 output bundle exists; candidate and harness remain at their fixed clean identities; reported invocation/CREATE counts are zero |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | BLOCKED | Executor/session identity does not satisfy the contract; repository main also advanced after the previous contract was issued |
| G1 Scope | PASS for reached scope | No R5 report/evidence was created and no candidate/harness change is present |
| G2 Contract | BLOCKED | Independent-session precondition is mandatory and unavailable in the receiving session |
| G4 Test | BLOCKED_NOT_REACHED | Collect-only and real pytest invocation counts are zero |
| DB Persistence | BLOCKED_NOT_REACHED | No R5 PostgreSQL observer, fixture, CREATE or business execution ran |
| G6 Evidence | PASS for the blocker | The feedback is sufficient to establish session ineligibility and fresh R5 output paths; it is intentionally not R5 DB evidence |

## Compact Evidence Matrix

| AC | Evidence | Verification | Verdict |
|---|---|---|---|
| AC-01 [BLOCKING] | Restore execution report identifies the receiving session's prior operations role | The feedback explicitly refuses the independent-verifier role for that reason | BLOCKED |
| AC-02 [BLOCKING] | R5 output paths reported absent | Fresh filesystem check found both paths absent | PASS |
| AC-03 [BLOCKING] | No R5 runtime artifacts should exist after phase-0 stop | No report/evidence directory exists; candidate `e942cbcc` and harness `f9a41ea` are clean | PASS |
| AC-04 [BLOCKING] | Replacement contract must use current Git state | Fresh Git check found current `main@77abbe72`, not the previous prompt's `cc551623` | BLOCKED in old contract; replacement required |

## Commands Actually Executed by This Review

| Check | Result | Purpose |
|---|---|---|
| Existence check for R5 report/evidence paths | both absent | Prove the disqualified session preserved the one-use paths |
| Main branch/HEAD/diff/index/status | `main@77abbe72`; tracked diff and index empty; only `docs/workbench.html` untracked | Establish replacement-contract baseline |
| Candidate branch/HEAD/status | `codex/wp04-02-evidence-domain-service@e942cbcc`; clean | Confirm no candidate mutation |
| Harness branch/HEAD/status | `codex/wp04-02-verifier-harness-r5-repair@f9a41ea`; clean | Confirm no harness mutation |
| Main ancestry checks | candidate and harness commits are ancestors of current main | Qualify current integrated state without treating it as DB acceptance |
| Current main commit inspection | `77abbe72` adds only the accepted PostgreSQL restore review on top of `cc551623` | Explain why the replacement prompt needs a new main pin |

## High-Risk Counterexamples

1. **Same session self-declares independence:** correctly rejected. Session
   history, not a label in the prompt, determines eligibility.
2. **Disqualified session consumes the reserved evidence path:** not observed;
   both paths remain absent.
3. **Disqualified session performs a harmless collect-only before stopping:**
   not reported and no R5 bundle exists; the stop occurred before collect-only.
4. **Old prompt is resent unchanged after main advances:** now prevented by
   this review. Current main is `77abbe72`, so the previous `cc551623` pin is
   stale.
5. **Block is mislabeled as a business FAIL:** avoided. No business test or
   database-writing path ran.

## Current Replacement Baseline

- Main: `main@77abbe72decfe5437ffed90521b8101f1eae1153`
- Main parent: `cc55162341fd99653b4ac6cd8f81da043cf7484c`
- Candidate: `codex/wp04-02-evidence-domain-service@e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`, clean
- Harness: `codex/wp04-02-verifier-harness-r5-repair@f9a41ea045d3ab8ad18db32d65a8484d6c96ec25`, clean
- Restore independent review SHA-256: `0c67fad09162f903fe1f8d086dcc4986c4a73d49e448823174fc6477aca3fb8a`
- R5 report path: absent
- R5 evidence path: absent

The only visible main worktree untracked path is the pre-existing
`docs/workbench.html`. This review report becomes an additional authorized
untracked governance artifact after it is written.

## Final Decision Rationale

`BLOCKED` is mandatory because an independent DB verifier cannot be the same
session that executed the infrastructure restoration on which the DB
verification relies. The session stopped at the correct boundary and did not
consume the R5 report/evidence path or CREATE budget. There is no evidence of
a business or harness defect from this attempt.

The prior R5 contract also became stale after dispatch because main advanced
from `cc551623` to `77abbe72` through a documentation-only acceptance commit.
A replacement contract must preserve the same business and database standards
while pinning the new current main and retaining the historical detached
`675217c3` snapshot required by the accepted harness.

## Next Action

Create a genuinely new Codex task/session and paste the replacement
`TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R5` contract into that new task.
Do not send it back to the restore operations task and do not route it to
zcode. The new task must fail closed if it can see that it previously executed
the restore task or any WP-04-02 implementation/harness work.

The replacement task may use the original fresh R5 report/evidence paths and
the original one-invocation/41-CREATE budget because neither was consumed.
