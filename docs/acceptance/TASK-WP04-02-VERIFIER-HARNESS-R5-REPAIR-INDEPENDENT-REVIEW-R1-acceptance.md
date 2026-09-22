# TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR-INDEPENDENT-REVIEW-R1

## Verdict

`FAIL`

The R5 working tree materially improves the R4 harness and preserves the exact
41-node structured collection path, but it still does not satisfy the frozen
fail-closed, source-attribution, credential-safety and evidence-completeness
contract. It is not eligible to authorize the separate real PostgreSQL
revalidation task.

This is an independent verifier decision. The executor's
`STATUS: IMPLEMENTATION_COMPLETE` is treated as a delivery state, not an
acceptance result.

## Reviewed Delivery

- R5 branch: `codex/wp04-02-verifier-harness-r5-repair`
- R5 worktree:
  `/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-verifier-harness-r5-repair`
- R5 HEAD: `df836cb39a1234aae967553b3783a67df9ad6672`
- Delivery form: three modified tracked files plus an untracked execution
  report and untracked evidence directory; no R5 commit was delivered
- Main HEAD: `675217c3a15c0f416aa4462ca6edc491bf99f9f6`
- Business candidate:
  `codex/wp04-02-evidence-domain-service@e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`
- Business candidate parent:
  `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`
- Business candidate state: clean during review

The review did not modify the R5 source, business candidate, dirty R4
worktree, main history or any historical acceptance artifact.

## Independent Verification Performed

### Build and quality

- Focused verifier suite: `67 passed in 1.44s`, exit 0.
- Ruff check: `All checks passed!`.
- Ruff format check: `3 files already formatted`.
- Read-only Python AST parse of runner: PASS.
- `git diff --check`: PASS.

An initial `python3 -m py_compile` attempt could not write a new `__pycache__`
file in the R5 worktree and returned `Operation not permitted`; this was an
environmental write restriction, not a syntax error. The fresh pytest import
and read-only AST parse independently established parseability.

### Fresh final-source collect-only

A new isolated run used `env -i`, synthetic loopback port-1 database URLs, a
new ledger path and a Python `sitecustomize` socket guard. It ran the final R5
working-tree source, not the stale executor bundle source.

Observed result:

- runner exit: 0;
- pytest return code: 0;
- `valid=true`, `verdict=PASS`;
- 41 unique node IDs;
- exact distribution `20 / 16 / 3 / 2`;
- missing / extra / duplicate / unclassified: all empty;
- test bodies executed: 0;
- socket guard log: absent;
- database fixture ledger: absent;
- manifest: 10 entries, all byte sizes and SHA-256 values matched;
- retained runner/plugin source hashes exactly matched the final working-tree
  bytes for this independent run.

This proves that the narrow structured collection happy path remains working.
It does not satisfy the failed negative-path and executor-evidence criteria
below.

## Blocking Findings

### B-01 — Executor success evidence is not attributable to the final runner

The final delivered runner SHA-256 is:

`201966382113a5a29e13876a36cb9ac0cd0a4efa7b9ea8d96d8924de025191fc`

The executor harness-run retained `runner.source.py` and
`source-hashes.json` with:

`944e4a61f3ea1ce2a3746f7e54303bcd4a600dba6719eef56a794506f3cb6e02`

The plugin hashes match, but the runner hashes do not. The attachment chronology
and report are consistent with the runner being edited after the retained
collect-only run. The execution report nevertheless claims that source-copy
hashes match the live source. This is a recurrence of the R4 source-attribution
failure and independently blocks `L3` and full collect-only `L4` acceptance.

### B-02 — Interruption does not produce structured closed evidence

`run_subprocess` converts `TimeoutExpired` and ordinary `Exception` instances,
but an interruption such as `KeyboardInterrupt` escapes. `run_collect_only`
cleans temporary staging in `finally`, then propagates the interruption without
writing `result.json` or `manifest.json`.

The independent synthetic counterexample observed:

- interruption escaped: yes;
- staging cleaned: yes;
- `result.json`: absent;
- `manifest.json`: absent;
- five partial evidence files remained.

The executor's SIGTERM example only established a non-zero process status
(`241`); it recorded no structured verdict or closed manifest. The added
timeout test exercises `run_subprocess` alone and does not assert closure of an
owned evidence bundle. This violates TOP-AC-02.

### B-03 — Staged plugin integrity is not enforced

The runner copies the original `tg_verifier_tools` package to a temporary
directory and imports the plugin under the same public package name. It does
not use a collision-resistant verifier-only namespace and does not verify the
staged plugin bytes before starting pytest.

In an independent synthetic counterexample, the staged plugin was replaced by
tampered bytes. A nonce-matched 41-node result was then supplied by the
subprocess stub. The runner returned `valid=true` and `verdict=PASS` because it
never authenticated the staged plugin. The only staging test in the delivered
suite checks cleanup on success; it does not test collision resistance,
staging cleanup on failure or staged-source authentication. This violates
TOP-AC-05.

### B-04 — Credential redaction is incomplete

The implementation replaces sensitive literals known from environment keys and
parses a value as a URL only when the entire string is URL-shaped. It does not
sanitize credential-bearing URLs embedded inside ordinary stdout/stderr text.
It also writes structured metadata fields such as `argv` and `cwd` without
recursive value redaction.

Using only synthetic values, the independent counterexample retained both URL
userinfo and a credential-bearing query value in:

- a surrounding stdout-style string; and
- `probe.meta.json` argv metadata.

No real credential was read, printed or retained during this review. The
counterexample violates TOP-AC-04.

### B-05 — Required executor evidence is missing

The R5 evidence directory contains only the harness-run bundle and an outer
manifest: 12 files total. The outer manifest is internally consistent for the
files that exist, but the contract required retained evidence for baseline,
tests, quality checks, counterexamples, no-DB proof, final state, source hashes,
negative CLI runs, the harness bundle and a final recursive manifest.

The following required evidence is absent from the executor directory:

- baseline state;
- focused test output;
- Ruff / format / compile / diff-check output;
- retained negative counterexample output;
- socket-guard and empty-ledger no-DB proof;
- final Git/worktree state;
- an outer source-hash record for the final delivered bytes.

The execution report expressly says a socket guard was “not needed,” while the
frozen contract required a guarded fresh run. It also claims all 16 regression
categories are covered, but the delivered tests omit executable coverage for
at least staged-plugin collision/authentication, staging cleanup on failure,
owned-bundle interruption closure, self-test subprocess startup failure and
the required guarded zero-activity path.

## Passed / Preserved Behavior

The FAIL result does not erase the verified improvements:

- correct main and candidate identity constants are present;
- main/candidate Git identity and pin mismatches are fail-closed before pytest;
- existing evidence leaves are rejected;
- pytest non-zero is rejected;
- invocation nonce binding and atomic collection publication are present;
- malformed JSON produces a structured failure;
- the harness manifest includes `collected-nodeids.json` and verifies cleanly;
- 67 delivered tests pass;
- the final-source fresh happy path produces exactly 41 / 20 / 16 / 3 / 2;
- no test body, fixture ledger event or Python socket connection was observed
  in the independent guarded happy-path run.

These passed areas must remain protected during the next repair.

## Required Acceptance Result

| Level | Result | Reason |
|---|---|---|
| `L1_STATIC_REVIEWED` | ACHIEVED | Full scoped diff, runner/plugin/tests and delivery artifacts reviewed |
| `L2_BUILD_VERIFIED` | ACHIEVED | Fresh 67-test suite, Ruff, format, AST and diff checks passed |
| `L3_CONTRACT_VERIFIED` | NOT ACHIEVED | B-01 through B-05 violate frozen source, interruption, plugin, redaction and evidence contracts |
| collect-only `L4_RUNTIME_VERIFIED` | PARTIAL ONLY | Final-source guarded happy path passed; negative paths and delivered evidence failed |
| `L4_DB_VERIFIED` | NOT RUN / NOT AUTHORIZED | No real PostgreSQL work was performed |

Overall task result: `FAIL`.

## Governance Disposition

The one controlled zcode R5 repair attempt has been consumed. Per the frozen
R5 governance appendix, do not automatically dispatch another zcode repair.
The next task is a Codex takeover in a new implementation session, followed by
a different independent verification session. This reviewing session must not
become the implementation author.

No real PostgreSQL validation, merge, rebase, push, WP-04-03 work or later
business task is authorized by this review.

## Independent Evidence

- `verification-summary.json`
- `source-attribution.json`
- `counterexamples.json`
- `fresh-collect-only-summary.json`
- `manifest.json`

