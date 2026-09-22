# TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1

## Target Envelope — Read First

This prompt is for a **new Codex implementation session**. The Codex session
that produced the R5 independent FAIL remains the verifier and must not perform
this implementation.

- Executor: Codex, controlled takeover repair
- Independent verifier: a different Codex session after delivery
- Task type / size: `BUG_FIX / MEDIUM`
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`,
  `L3_CONTRACT_VERIFIED`, collect-only `L4_RUNTIME_VERIFIED`
- `L4_DB_VERIFIED`: not required and not authorized
- Allowed final executor status: `IMPLEMENTATION_COMPLETE` or `BLOCKED`

Do not declare `PASS`, `VERIFIED`, `DONE`, authorize PostgreSQL, or approve your
own implementation.

## Objective

Repair only the five blocking findings in
`TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR-INDEPENDENT-REVIEW-R1` while preserving
all R5 behavior that independently passed: Git/pin fail-closed checks,
immutable evidence leaves, pytest return-code enforcement, nonce binding,
malformed-JSON closure, recursive manifest integrity and exact structured
collection of 41 unique node IDs with distribution `20 / 16 / 3 / 2` and zero
test-body/database/socket activity.

Do not run real PostgreSQL and do not modify the business candidate.

## Required Context

Read completely before editing:

1. `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/AGENTS.md`
2. `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/prompts/TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR.md`
3. `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR-INDEPENDENT-REVIEW-R1-acceptance.md`
4. Its independent evidence directory.
5. The current full diff and untracked delivery artifacts in the R5 worktree.

Do not infer correctness from the executor report or the 67 passing tests.
Reproduce the independent counterexamples before changing code.

## Exact Working State

Continue the existing takeover target; do not create, delete, reset or replace
it:

- Worktree:
  `/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-verifier-harness-r5-repair`
- Branch: `codex/wp04-02-verifier-harness-r5-repair`
- Current HEAD: `df836cb39a1234aae967553b3783a67df9ad6672`
- R4 parent: `675217c3a15c0f416aa4462ca6edc491bf99f9f6`
- Current delivery is intentionally uncommitted.

Before editing, record exact status, diff, file hashes and untracked artifact
inventory. Preserve the zcode R5 executor report/evidence as historical failed
delivery evidence; do not delete or rewrite it.

Immutable baselines:

- Main:
  `/Users/qianduoduo/Desktop/AI_app/ThesisGuard@675217c3a15c0f416aa4462ca6edc491bf99f9f6`
- Candidate worktree:
  `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`
- Candidate branch: `codex/wp04-02-evidence-domain-service`
- Candidate HEAD: `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`
- Candidate parent: `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`
- Candidate must remain completely clean.

If these identities differ, stop `BLOCKED` without mutation.

## Allowed Source/Test Scope — Maximum Three Files

You may modify only:

1. `tg_verifier_tools/verification/wp04_02_r4_runner.py`
2. `tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py`
3. `tg_verifier_tests/verification/test_wp04_02_r4_runner.py`

Do not create parallel source modules. If a fourth source/test/config file is
required, stop `BLOCKED`.

You may add only these new takeover delivery artifacts:

4. `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1-execution-report.md`
5. `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1-evidence/`

## Required Repairs

### R-01 — Final-source attribution

- Never edit or format source after generating final runtime evidence.
- The final harness bundle must retain the exact runner/plugin bytes used by
  the subprocess path.
- Verify and record equality between live final source, staged source and
  retained source copies.
- The final outer manifest must be generated last and cover every retained
  non-manifest file.

### R-02 — Timeout and interruption closure

Once the runner exclusively owns a new evidence leaf, timeout, subprocess
startup failure, `KeyboardInterrupt` and supported termination/interruption
paths must never leave a misleading or open bundle.

They must:

- return or exit non-zero;
- preserve the original category and return/signal information;
- write sanitized structured `result.json`;
- write a closed recursive `manifest.json`;
- clean staging in `finally`;
- never publish `PASS`.

Do not weaken immutable-evidence behavior: a pre-existing leaf must still be
rejected without modifying any byte.

### R-03 — Collision-resistant authenticated plugin staging

- Stage only the verifier plugin under a collision-resistant verifier-only
  namespace; do not reuse the ambient public `tg_verifier_tools` package name.
- Put only the isolated verifier namespace ahead of ambient paths.
- Hash the staged plugin bytes and compare them to the intended final plugin
  bytes before pytest starts.
- Fail closed on any staged-byte mismatch.
- Prove candidate/ambient package shadowing cannot select another plugin.
- Remove temporary staging on success and every failure/interruption path.

### R-04 — Complete value redaction

Use only synthetic values in tests. Redact credential-bearing URLs and known
sensitive literals wherever they occur, including when a URL is embedded in
surrounding stdout/stderr/exception text. Recursively sanitize structured
metadata before serialization, including `argv`, `cwd`, environment metadata
and error details.

Case-insensitive prefix/suffix sensitive-key classification and URL userinfo /
credential-query redaction must remain. A recursive scan of final evidence must
find none of the synthetic secret literals.

### R-05 — Complete regression and execution evidence

Add executable tests for every missing path, including:

- owned-bundle timeout and interruption closure;
- actual non-zero CLI behavior for controlled interruption;
- staged-plugin byte mismatch;
- ambient/candidate plugin collision resistance;
- staging cleanup on success, ordinary failure and interruption;
- embedded credential URL redaction in stdout/stderr/exception text;
- recursive redaction of JSON metadata such as argv/cwd;
- self-test missing executable/startup failure and non-zero subprocess return;
- exact guarded zero-body/ledger/socket/CREATE behavior;
- final source-copy and staged-source hash equality.

Keep all useful existing R4/R5 tests. Do not weaken, delete, skip or replace
them with mocks that cannot exercise the contract boundary.

## Required Verification

Use already installed tools only. Run at minimum:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/pytest \
  -p no:cacheprovider \
  tg_verifier_tests/verification/test_wp04_02_r4_runner.py \
  -q --tb=short

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

After all source formatting is final, run exactly one new guarded collect-only
against the immutable business candidate using:

- a non-existent takeover evidence leaf;
- `env -i` or equivalent explicit minimal parent environment;
- synthetic port-1 database URLs only;
- a new empty fixture-ledger path;
- a Python socket guard that logs and raises on every connection attempt;
- no real credentials or services.

Require exit 0, pytest return 0, current nonce match, exactly 41 unique IDs,
distribution `20 / 16 / 3 / 2`, zero bodies, absent/empty ledger, absent/empty
socket log, zero CREATE activity, complete manifest, and live/staged/retained
source-hash equality.

Run and retain representative negative CLI/counterexample evidence for all
R-02 through R-04 paths. Each must be non-success, sanitized and closed.

## Evidence Contract

The takeover evidence directory must include at least:

- baseline Git/worktree state and initial file hashes;
- focused test output;
- Ruff, format, compile and diff-check output;
- independent-counterexample reproduction before repair and passing regression
  output after repair;
- retained negative CLI results;
- guarded no-DB/socket/ledger proof;
- final source, staged-source and retained-source hashes;
- final Git/worktree status and changed-file inventory;
- the final harness-run bundle;
- a final recursive outer manifest generated last.

The execution report must map independent findings B-01 through B-05 to code,
tests and retained evidence. Record exact commands, exits, counts, hashes,
execution time, repair count and visible token/cost (`UNKNOWN` if unavailable).

## Forbidden

- No real PostgreSQL connection or database operation.
- No edit to the business candidate, main, dirty R4 worktree, historical
  reports/evidence, AGENTS.md, dependencies or configuration.
- No edit to production Evidence code or business tests/fixtures.
- No merge, rebase, push, reset, clean or stash.
- No new feature, WP-04-03, 05C-02/R1D, capability runtime or Sector Crowding
  work.
- No hardcoded PASS, skipped failure, TODO or acceptance-standard weakening.

## Acceptance Criteria

Implementation may be reported `IMPLEMENTATION_COMPLETE` only when:

1. every independent counterexample first reproduces and then passes as an
   executable regression;
2. all preserved and new verifier tests pass;
3. quality checks pass;
4. the final guarded 41 / 20 / 16 / 3 / 2 run passes with zero DB/socket/body
   activity;
5. every negative run is closed, sanitized and non-success;
6. staged/live/retained source hashes match;
7. the complete evidence inventory and final outer manifest verify;
8. only the three allowed source/test files and two new takeover delivery
   artifact paths changed.

If any criterion cannot be met within scope, return `STATUS: BLOCKED` with the
exact evidence. Do not self-approve.

End with:

`Awaiting a separate Codex independent acceptance. No real PostgreSQL task, merge, push, 05C-02/R1D or WP-04-03 work is authorized by this delivery.`

