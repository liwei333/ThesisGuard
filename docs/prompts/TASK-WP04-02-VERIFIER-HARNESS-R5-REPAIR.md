# TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR

## Target Envelope — Read First

This prompt is for the **zcode agent only**.

You are the assigned `EXECUTOR` for one controlled R5 repair attempt. Codex is
the later independent `VERIFIER`; that separation is intentional and is not a
reason for you to stop. Do not re-evaluate or swap the assigned roles. If the
receiving session is not zcode, it must not implement this contract and must
route it to zcode.

Your final status may only be `IMPLEMENTATION_COMPLETE` or `BLOCKED`. You must
not declare `PASS`, `DONE`, `VERIFIED`, or authorize a real PostgreSQL run.

## A. Execution Core

- Repair ID: `TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR`
- Original implementation: `TASK-WP04-02-VERIFIER-HARNESS-R4`
- Executor: zcode, one controlled repair attempt
- Independent verifier: Codex, after this delivery
- Task type / size: `VERIFIER_HARNESS_REPAIR / MEDIUM`
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`,
  `L3_CONTRACT_VERIFIED`, and collect-only `L4_RUNTIME_VERIFIED`;
  `L4_DB_VERIFIED` is not required or authorized
- Evidence matrix: Full

### Objective

Repair only the R4 verifier harness defects proved by the independent review so
that a fresh collect-only invocation is deterministic, evidence-complete,
credential-safe and fail-closed. Preserve the already verified structured
pytest collection of exactly 41 unique node IDs with the required 20/16/3/2
distribution and zero test-body, database-fixture, socket and CREATE activity.

Do not run real PostgreSQL and do not modify the WP-04-02 business candidate.

### Why Now

R4 fixed only the narrow pytest tree-format collection problem. Its independent
review remains FAIL because nine demonstrated fail-closed, evidence-integrity
and credential-safety paths are broken. Repair-first governance blocks every
real-DB or later WP task until this smallest verifier-harness repair is
independently accepted.

### Required Context

Read before editing:

1. `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/AGENTS.md`
2. `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R4-INDEPENDENT-REVIEW-R1-acceptance.md`
3. `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R4-INDEPENDENT-REVIEW-R1-FEEDBACK-REVIEW-acceptance.md`
4. `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR-WRONG-EXECUTOR-FEEDBACK-REVIEW-acceptance.md`
5. The retained R4 negative helper and results under
   `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R4-INDEPENDENT-REVIEW-R1-evidence/`
6. Exact R4 source/tests at commit
   `df836cb39a1234aae967553b3783a67df9ad6672`

The wrong-executor stop did not begin implementation and did not consume this
zcode repair attempt.

### Fixed Baselines

Main repository:

`/Users/qianduoduo/Desktop/AI_app/ThesisGuard`

Required main HEAD:

`675217c3a15c0f416aa4462ca6edc491bf99f9f6`

R4 repair base:

`df836cb39a1234aae967553b3783a67df9ad6672`

Required R4 parent:

`675217c3a15c0f416aa4462ca6edc491bf99f9f6`

Business candidate worktree:

`/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`

Required business candidate:

- Branch: `codex/wp04-02-evidence-domain-service`
- HEAD: `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`
- Parent: `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`
- Status: completely clean

Correct main fixture-acceptance SHA-256 pin:

`daf2779bda9602a7397ffc01398b940b704091a3529015475542d5e7ad66de89`

The R4 runner contains a wrong version of that pin and a malformed candidate
commit constant; both must be corrected and validated against actual Git state.

### Worktree

Do not use, clean, restore, reset, stash or modify the existing dirty R4
worktree:

`/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-verifier-harness-r4`

Create one fresh isolated worktree from exact R4 commit:

- Branch: `codex/wp04-02-verifier-harness-r5-repair`
- Preferred path:
  `/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-verifier-harness-r5-repair`
- Base: `df836cb39a1234aae967553b3783a67df9ad6672`

If either branch or worktree path already exists, stop `BLOCKED`; do not reuse,
delete, reset or overwrite it. Creating this one local branch/worktree is
authorized. Merge, rebase, push and main mutation are not authorized.

## Top Blocking AC

### TOP-AC-01 — Exact baseline and Git identity fail closed

Before pytest starts, the runner must query and enforce:

- main is a real Git repository at exact HEAD `675217c...`;
- every main pin matches exact bytes;
- candidate is a real worktree on exact branch `codex/wp04-02-evidence-domain-service`;
- candidate HEAD is exact `e942cbcc...`;
- candidate parent is exact `af4f2cbb...`;
- candidate worktree/index/untracked state is clean;
- all five candidate pins match exact bytes.

Any mismatch must produce non-success before pytest. Writing expected constants
to JSON without querying Git is not verification.

### TOP-AC-02 — Current invocation binding and subprocess fail-closed behavior

Each run must use a new unpredictable run ID and invocation nonce. The pytest
plugin output must carry that nonce. Require pytest exit code 0 before any
successful verdict.

Missing, malformed, stale, partial, duplicate, nonce-missing or nonce-mismatched
collection output, as well as pytest non-zero, timeout or interruption, must:

- never produce PASS;
- return non-zero;
- retain the original error category/return code;
- create sanitized structured failure evidence and a closed manifest when the
  runner successfully owns a new evidence directory.

The plugin must publish completed structured output atomically. A valid-looking
old JSON must never rescue the current invocation.

### TOP-AC-03 — Immutable evidence path and complete evidence

The requested evidence leaf must not exist before the run. If it exists, even
empty, refuse before modifying any byte inside it. Preserve sentinels exactly.

For a newly and exclusively created evidence leaf:

- publish `result.json` and `manifest.json` atomically;
- generate the final manifest recursively after every other retained artifact;
- include `collected-nodeids.json` and every other retained non-manifest file;
- exclude only the manifest itself;
- record correct byte sizes and SHA-256 values;
- retain exact executing runner/plugin bytes or immutable blob identities;
- ensure retained source copies match final delivered source bytes.

Do not format or edit source after generating final runtime evidence.

### TOP-AC-04 — Minimal environment and secret-safe evidence

Do not serialize or pass through the complete inherited environment. Build an
explicit minimal child environment.

Use case-insensitive key classification for password/passwd, token, secret,
credential, API/access key, auth, cookie, session, database URL and DSN,
including prefix/suffix variants. Redact URL userinfo and credential-bearing
query components. Apply value-level redaction to stdout, stderr, JSON metadata
and exception messages before writing evidence.

Tests may use only synthetic secret values. Do not discover, read, print, copy
or retain real credential values. Collect-only must not need real database
credentials.

### TOP-AC-05 — Preserve collection/zero-DB behavior and complete regression protection

Preserve:

- pytest public structured collection hook using authoritative `session.items`;
- exactly 41 unique parameterized node IDs;
- exact distribution 20 forbidden / 16 allowed / 3 ordinary replay / 2 legacy replay;
- independence from `<Coroutine ...>` terminal tree formatting;
- zero test bodies;
- zero fixture DB creation;
- zero Python socket connections;
- zero CREATE attempts and no fixture-ledger events.

Stage the plugin under a collision-resistant verifier-only namespace, verify its
source hash, prevent candidate/ambient package shadowing and remove temporary
staging in `finally` on success and failure.

`--mode self-test` must return non-zero if its test file is absent, pytest
cannot start, or the test subprocess fails. It may not skip missing tests and
return success.

## Scope

### In Scope

- Fail-closed baseline, subprocess, nonce and evidence-path handling in the R4 runner.
- Atomic structured collection output in the R4 pytest plugin.
- Minimal environment, redaction, manifest and source-attribution repair.
- Focused verifier regression tests for the demonstrated R4 failures.
- One fresh safe collect-only run and task-scoped execution evidence.

### Allowed modified files — maximum three

1. `tg_verifier_tools/verification/wp04_02_r4_runner.py`
2. `tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py`
3. `tg_verifier_tests/verification/test_wp04_02_r4_runner.py`

Do not create parallel R5 source-module copies. Repair the existing modules.

### Allowed new delivery artifacts

4. `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR-execution-report.md`
5. `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR-evidence/`

No other project path may change. If another source/config/test file is needed,
stop `BLOCKED` instead of expanding scope.

### Must

- Record baseline and final Git/worktree state without altering unrelated state.
- Make every demonstrated R4 negative path return non-success with attributable evidence.
- Preserve all verified R4 structured-collection and zero-DB behavior.
- Add regression coverage before reporting `IMPLEMENTATION_COMPLETE`.
- Run every required focused test and quality command and report exact results.
- Keep executor evidence separate from later Codex independent acceptance.

### Forbidden

- No business-candidate edit.
- No edit to `tests/test_evidence_services.py`, `tests/evidence_pg_fixture.py`
  or `tests/test_evidence_pg_fixture_lifecycle.py`.
- No production Evidence service/model/repository/error edit.
- No real PostgreSQL connection, business test, CREATE, DROP, rename or session termination.
- No historical UNKNOWN cleanup.
- No dependency/configuration change.
- No AGENTS.md or zcode capability-record change.
- No historical R2/R3/R4 report/evidence modification.
- No main mutation, merge, rebase or push.
- No weakened/deleted/skipped tests, TODO, placeholder or hardcoded PASS.

## Required Regression Tests

Keep the useful R4 tests and add project-owned executable tests covering at
least:

1. candidate pin mismatch;
2. main pin and main HEAD mismatch;
3. wrong candidate branch, HEAD, parent and dirty state;
4. pytest non-zero with valid-looking JSON;
5. missing and malformed JSON;
6. stale JSON and missing/mismatched nonce;
7. missing/extra/duplicate/unclassified IDs and wrong distribution at count 41;
8. pre-existing empty and non-empty evidence directories with sentinel preservation;
9. recursive manifest coverage, size and SHA-256 correctness;
10. environment exclusion and case/prefix/suffix sensitive-key variants;
11. URL, stdout, stderr, JSON and exception-message value redaction;
12. plugin collision resistance and staging cleanup on success/failure;
13. timeout/interruption closed evidence;
14. missing self-test file and self-test subprocess failure;
15. exact 41/20/16/3/2 happy path;
16. zero test-body, ledger, socket and CREATE activity.

Use temporary repositories/paths and synthetic values only. Do not modify main
or the business candidate to create negative cases.

## High-Risk Counterexamples

1. Given a main pin mismatch, when collect-only is requested, then pytest must
   not start and the run must end non-success.
2. Given a non-Git or wrong-branch candidate with matching copied files, when
   baseline validation runs, then file hashes alone must not permit execution.
3. Given pytest returns non-zero while valid-looking old/current JSON exists,
   when the runner judges the invocation, then the JSON must not produce PASS.
4. Given an existing evidence directory containing a sentinel, when the runner
   starts, then it must refuse and preserve every existing byte.
5. Given synthetic credentials appear under key variants or in stdout, stderr
   or exception text, when evidence is retained, then no raw value may appear.
6. Given the expected self-test file is missing, when self-test mode runs, then
   the process must exit non-zero rather than skip successfully.

## Required Verification

Run from the isolated R5 worktree using already installed tools.

### Focused suite

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/pytest \
  -p no:cacheprovider \
  tg_verifier_tests/verification/test_wp04_02_r4_runner.py \
  -q --tb=short
```

All existing and added R5 cases must pass. Do not report only a subset.

### Quality

```bash
ruff check \
  tg_verifier_tools/verification/wp04_02_r4_runner.py \
  tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py \
  tg_verifier_tests/verification/test_wp04_02_r4_runner.py

ruff format --check \
  tg_verifier_tools/verification/wp04_02_r4_runner.py \
  tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py \
  tg_verifier_tests/verification/test_wp04_02_r4_runner.py

python -m compileall \
  tg_verifier_tools/verification \
  tg_verifier_tests/verification/test_wp04_02_r4_runner.py

git diff --check
```

Resolve installed executable paths without installing or upgrading tools.

### Fresh safe collect-only

After source formatting is final, run exactly one fresh safe collect-only CLI
invocation against the exact business candidate using:

- a new non-existent evidence leaf at
  `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR-evidence/harness-run/`;
- an explicit minimal environment (`env -i` or equivalent);
- synthetic port-1 DB URLs only;
- a new empty ledger path;
- a Python socket guard that raises on any connection attempt;
- no real database credential or service.

Require exit 0, current nonce match, exact 41/20/16/3/2, pytest return 0,
absent/empty ledger, no socket event, no CREATE, complete manifest and exact
source-copy hashes.

### Representative negative CLI runs

With only temporary repositories, subprocess stubs and synthetic values,
exercise at least:

- main mismatch;
- wrong candidate identity;
- pytest non-zero;
- stale/nonce-mismatched JSON;
- pre-existing evidence path;
- malformed JSON;
- timeout/interruption;
- sensitive stdout/stderr.

Each must return non-zero without a misleading PASS or evidence overwrite.

## Expected Evidence and Execution Report

Use:

- `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR-execution-report.md`
- `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR-evidence/`

The evidence directory must include baseline, tests, quality checks,
counterexamples, no-DB proof, source hashes, final state, the harness-run bundle
and a final recursive outer manifest. Generate the outer manifest last and do
not edit evidence afterward.

The execution report must map R4 findings F-01 through F-09 to R5 code
locations, regression tests and command results. Record `BASELINE_CHANGED_FILES`,
`FINAL_CHANGED_FILES`, exact command exits/counts, 41/20/16/3/2 results,
manifest inventory, source-copy equality, zero-DB evidence, secret-leak scan,
execution time, repair count and visible cost/token (`UNKNOWN` if unavailable).

## Stop Conditions

Stop `BLOCKED` if:

- exact baselines cannot be resolved;
- the R5 branch/worktree already exists;
- the business candidate is dirty or has moved;
- required installed tooling is unavailable;
- a real credential or database connection would be required;
- satisfying the contract requires a fourth source/test file, dependency
  change, business-code edit or changed acceptance standard.

A code defect inside the three allowed files is the repair objective, not a
reason to change scope.

## Executor Final Response

Use exactly one status:

- `STATUS: IMPLEMENTATION_COMPLETE`, after the scoped implementation and
  executor-side verification/evidence are delivered; or
- `STATUS: BLOCKED`, only with the exact unmet stop condition and evidence.

Do not declare PASS. End with:

`Awaiting Codex independent acceptance. No real PostgreSQL task, merge, push, 05C-02/R1D or WP-04-03 work is authorized by this delivery.`

## B. Governance Appendix

- `IMPLEMENTED != PASS`
- `No Evidence, No PASS`
- `Executor Cannot Self-Approve`
- `FAIL -> Repair First`
- `Out of Scope Blocks Drift`
- `Verifier Must Independently Verify`
- `Repair Must Not Break Passed AC`

This is zcode's one controlled R5 repair attempt. If the later Codex review
still finds a Blocking failure, do not automatically dispatch another zcode
round; Codex takes over under a separately amended executor/verifier arrangement.
