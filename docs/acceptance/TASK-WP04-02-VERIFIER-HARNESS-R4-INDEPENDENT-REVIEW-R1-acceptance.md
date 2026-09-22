# TASK-WP04-02-VERIFIER-HARNESS-R4-INDEPENDENT-REVIEW-R1

Verdict: **FAIL**

Independent verifier: Codex. Evidence date: 2026-09-20, Asia/Shanghai. Reviewed
object: exact commit `df836cb39a1234aae967553b3783a67df9ad6672`, parent
`675217c3a15c0f416aa4462ca6edc491bf99f9f6`. Review checkout:
`/private/tmp/tg-wp04-02-r4-review-r1.o31SWt/review`, clean detached HEAD.

This verdict is limited to the R4 verifier harness. It is not a verdict on the
41 WP-04-02 business scenarios, whose real PostgreSQL execution count remains
zero in this task. R4 is **not eligible** to be used for the separately
dispatched real-PostgreSQL revalidation task. This review does not close
05C-01, R1C, WP-04-02, or any later work package.

## Decision summary

The structured pytest plugin fixes the narrow R3 presentation-format problem:
on pytest 9.1.1 it collected exactly 41 unique parameterized node IDs with the
required 20/16/3/2 distribution while terminal output used `<Coroutine ...>`
tree formatting. A socket-denied, poisoned-DB, empty-ledger run executed no test
bodies, created no fixture ledger, attempted no Python socket connection and
made no observed CREATE attempt.

Those happy-path facts do not satisfy the fail-closed contract. The committed
runner can return `valid=true` and `PASS` when a main pin mismatches, when the
candidate is not the required Git branch/commit, when pytest exits non-zero, or
when a stale collection JSON is reused. It overwrites pre-existing evidence,
omits `collected-nodeids.json` from its manifest, retains subprocess output
without value redaction, and only redacts a small exact-key allowlist from a
complete inherited environment dump. The actual fresh run exhibited the first
defect: `baseline-pins.json` recorded a main hash mismatch but `result.json`
still said `PASS`.

## Blocking findings

### F-01 — Main baseline mismatches are recorded but ignored

In `df836cb:tg_verifier_tools/verification/wp04_02_r4_runner.py`, lines 290–300
compute and record `main_mismatches`; lines 302–318 reject only
`candidate_mismatches`. The runner's expected hash for
`TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY-acceptance.md`
also differs from the exact main-anchor file:

```text
expected daf2779bda9602a7397ffc01398b940b704091a3529014775542d5e7ad66de89
actual   daf2779bda9602a7397ffc01398b940b704091a3529015475542d5e7ad66de89
```

The retained fresh execution records this mismatch and nevertheless returns
`valid=true`, `verdict=PASS`, exit 0. This independently fails TOP-AC-03(2) and
the baseline portion of TOP-AC-01/04.

### F-02 — Candidate branch, commit, parent and cleanliness are not verified

`CANDIDATE_BRANCH` and `CANDIDATE_COMMIT` are constants, but the runner only
writes them into `baseline-pins.json`; it never asks Git for the supplied
candidate root's symbolic branch, HEAD, parent or status. The unused
`find_candidate_root()` also searches for a branch name on a `worktree` line,
although porcelain worktree output places branch information on a separate
`branch` line. A non-Git directory with mocked matching pins reached `PASS` in
the independent counterexample. This fails TOP-AC-03(3).

### F-03 — Non-zero pytest and stale collection data can become PASS

The subprocess return code is recorded at lines 403–404 but never participates
in `valid` or the returned verdict at lines 408–413. The runner does not remove
or bind `collected-nodeids.json` to the current invocation before starting.
Independent counterexamples showed both of these paths return `PASS`:

1. current pytest return code 2 plus a valid current-looking JSON;
2. current pytest return code 2, no current JSON production, plus a pre-existing
   valid `collected-nodeids.json`.

This fails TOP-AC-02 and TOP-AC-03(4–5), and permits a failed invocation to
leave a misleading successful result under TOP-AC-04.

### F-04 — Existing evidence is overwritten instead of rejected

`EvidenceBundle.__init__()` and CLI setup call `mkdir(..., exist_ok=True)`.
Every fixed-name artifact is then written with replacement semantics. A
pre-existing `result.json` was overwritten and the invocation returned PASS.
This fails TOP-AC-03(10) and TOP-AC-04's fresh-output requirement.

### F-05 — The manifest is incomplete

The plugin writes `collected-nodeids.json` directly. The bundle's `_files`
registry never receives that path, so both the committed executor bundle and
the new independent happy-path bundle omit it from `manifest.json`. The
independent manifest counterexample fails accordingly. This fails TOP-AC-04.

### F-06 — Secret safety is fail-open

`redact_env()` masks only eight exact, case-sensitive key names, while
`run_subprocess()` serializes the complete inherited environment and writes
stdout/stderr verbatim. Synthetic probes confirmed that lower-case and suffixed
database URL keys, generic password/token keys, and a secret echoed to stdout
remain verbatim. A real inherited-environment probe identified unredacted
sensitive-looking keys including `ANTHROPIC_AUTH_TOKEN` and
`CODEX_SESSION_ID`; their values were not displayed or retained. The initial
task-generated unsafe bundle was immediately removed, and the retained fresh
run was repeated under `env -i`. This fails TOP-AC-04.

### F-07 — Malformed collection JSON aborts without closed evidence

`json.loads()` at line 385 is unguarded. The malformed-JSON counterexample
raises `JSONDecodeError` before a structured failure `result.json` and final
manifest are written. Although the process itself is non-zero, it does not
produce the required reproducible closed failure evidence. This fails the
combined TOP-AC-03(5)/TOP-AC-04 requirement.

### F-08 — The committed executor bundle does not retain the committed sources

The R4 commit's actual plugin and runner hashes are respectively
`77d563...e4811` and `a9f5c5...76494`. The source copies retained in the same
commit's executor bundle hash to `d4069b...229e6` and `f9c283...288b8`; both
byte comparisons fail. The differences include pre-formatting source and a
functional `compute_distribution` implementation difference. The committed
bundle also records no immutable verifier commit/blob identity that repairs
this mismatch. The independent fresh bundle does copy the reviewed sources
exactly, but R4's submitted executor evidence is not reproducible from its own
commit. This fails TOP-AC-04.

### F-09 — The 21 committed tests do not cover the blocking behavior

The suite covers exact node-set validation, hashing helpers, two exact redaction
keys, tracked-file manifest hashes and one happy-path end-to-end run. It does
not test main-pin rejection, candidate Git identity, subprocess non-zero exit,
missing/malformed/stale current-invocation binding, pre-existing output,
complete manifest coverage, stdout/stderr secret redaction or representative
environment-key variants. In addition, CLI self-test mode returns success when
the test file is absent. The suite's `21 passed` result is valid but insufficient
for TOP-AC-03/04.

## Required, achieved and missing acceptance

### Required Acceptance

- `L1_STATIC_REVIEWED`
- `L2_BUILD_VERIFIED`
- `L3_CONTRACT_VERIFIED`
- `L4_RUNTIME_VERIFIED`, limited to collect-only and verifier self-runtime;
  `L4_DB_VERIFIED` is neither required nor authorized.

### Achieved Acceptance

- `L1_STATIC_REVIEWED`: achieved for exact `df836cb` diff, source, tests,
  executor report/evidence, required R3 context, selected candidate tests,
  fixture/import behavior and relevant frozen-contract clauses.
- `L2_BUILD_VERIFIED`: achieved for focused Ruff check, Ruff format check and
  the committed verifier self-tests (`21 passed`).
- Partial `L4_RUNTIME_VERIFIED`: one fresh pytest 9.1.1 collect-only run
  produced exactly 41 unique IDs and 20/16/3/2 distribution with zero observed
  test bodies, DB fixture ledger events, socket connections or CREATE attempts.

### Missing Acceptance

- `L3_CONTRACT_VERIFIED`: not achieved because fail-closed baseline,
  subprocess, stale-output, evidence-path, manifest and secret requirements
  fail executable counterexamples.
- Full `L4_RUNTIME_VERIFIED`: not achieved because the happy path is not safe
  under required negative runtime conditions.
- `L4_DB_VERIFIED`: intentionally not attempted and remains unauthorized.

## Full Evidence Matrix

| Top AC | Implementation evidence | Independent verification evidence | Counterexample evidence | Verdict |
| --- | --- | --- | --- | --- |
| TOP-AC-01 — exact baseline, isolation, scope | Exact commit parent verified; 20-file add-only diff enumerated; clean detached `/private/tmp` checkout; no prohibited business file changed | `baseline.txt`; initial/final Git checks; candidate exact branch/HEAD/parent clean; main anchor exact with preserved `docs/workbench.html`; dirty R4 checkout observed only | Runner itself does not verify supplied candidate Git identity; mapped primarily to TOP-AC-03 | PASS for review provenance and isolation; harness identity enforcement FAIL under AC-03 |
| TOP-AC-02 — structured collection, zero DB side effects | Public `pytest_collection_finish(session)` uses `session.items`; exact expected node set and distribution | `happy-path-safe/`; pytest 9.1.1 tree-format stdout; `no-db-side-effects.json`; poisoned port-1 URLs; absent ledger and socket-guard logs | Non-zero pytest plus valid JSON returned PASS | **FAIL** |
| TOP-AC-03 — fail closed | Exact-set validator rejects missing/extra/duplicate/wrong distribution; candidate file-pin mismatch and missing JSON reject | `counterexamples.txt`; retained helper and hashes | Main pin mismatch PASS; wrong Git identity PASS; pytest rc=2 PASS; stale JSON PASS; existing evidence overwritten; malformed JSON unstructured abort | **FAIL** |
| TOP-AC-04 — evidence integrity, secrets | Runner copies current source and records argv/cwd/times/rc; exact fresh source copies match reviewed code | `evidence-integrity-audit.txt`; safe `env -i` fresh bundle; helper secret probes; committed-vs-current source comparison | Manifest omits collection JSON; inherited env and stdout can leak secrets; existing outputs overwritten; executor source copies differ from commit | **FAIL** |
| TOP-AC-05 — quality and verdict discipline | 21 committed self-tests inspected in full | `self-tests.txt`: 21 passed; `quality-checks.txt`: Ruff and format exit 0; this report separates required/achieved/missing and gives exact FAIL | Existing tests omit the blocking scenarios; no harness repair was made | PASS for independent-review procedure; does not override failed Blocking ACs |

## Verification results

| Check | Result |
| --- | --- |
| Exact R4 commit / parent | PASS |
| Fresh detached review checkout clean | PASS |
| Candidate exact branch / HEAD / parent / clean | PASS as reviewer baseline |
| `git diff --check` | PASS |
| Focused Ruff check | PASS |
| Focused Ruff format check | PASS |
| Committed verifier suite | `21 passed` |
| Fresh collect-only | subprocess 0; 41 collected; exact 20/16/3/2 |
| Test bodies / DB fixture ledger / socket guard / CREATE | 0 / absent / absent / 0 observed |
| Independent contract counterexamples | `9 failed, 3 passed`; failures are harness defects, not review-infrastructure failures |
| Real PostgreSQL | NOT RUN / NOT AUTHORIZED |

## Minimal Repair Contract — R5 harness only

Task ID: `TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR`

Executor: zcode, one controlled repair attempt; Codex performs independent
acceptance. If the controlled repair still fails a Blocking AC, Codex takes
over. This contract does not dispatch the task automatically.

Objective: repair only the verifier runner/plugin/self-tests so an exact,
fresh, collect-only invocation is deterministic, secret-safe and fail-closed.
Do not execute real PostgreSQL and do not modify WP-04-02 business code/tests,
fixtures, migration, frozen contracts or historical acceptance artifacts.

Allowed source scope:

1. `tg_verifier_tools/verification/wp04_02_r4_runner.py` (or a narrowly named
   R5 successor),
2. `tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py` only if needed
   for invocation binding/atomic output (or a narrowly named R5 successor),
3. `tg_verifier_tests/verification/test_wp04_02_r4_runner.py` (or R5 successor),
4. a new R5 executor report and newly allocated R5 evidence directory.

Required repair behavior:

- Correct every main pin and fail before collection on any candidate or main
  pin mismatch.
- Resolve and enforce exact main HEAD, candidate symbolic branch, candidate
  HEAD, candidate parent and clean status; constants printed into JSON are not
  verification.
- Reject a pre-existing output path without changing it. Use a unique run ID,
  an invocation nonce in plugin output and atomic final-result publication so
  stale/partial artifacts cannot become PASS.
- Require pytest return code 0 before collection validity can produce PASS.
  Missing, malformed, stale or nonce-mismatched JSON must create a structured
  non-success result and complete failure evidence.
- Build the manifest from a recursive filesystem inventory after all artifacts
  except the manifest exist; cover every retained non-manifest file including
  `collected-nodeids.json`, with correct size/hash, and exclude only the
  manifest itself.
- Replace full inherited-environment dumping with a minimal relevant-field
  whitelist. Redact credential-bearing URL components and representative
  case/suffix password, token, secret, key and credential variants. Apply
  value-level redaction to retained stdout/stderr/JSON. Never store a real
  sensitive value in tests.
- Stage the plugin under a collision-resistant verifier-only module namespace,
  verify its source hash, avoid shadowing candidate business packages and clean
  temporary staging on success/failure.
- Retain exact executing source bytes or immutable blob identities. Make
  `--mode self-test` non-zero if tests are absent.

Required R5 tests and independent gates:

- Keep exact 41/20/16/3/2 happy-path coverage.
- Add executable tests for all ten TOP-AC-03 cases and the TOP-AC-04 manifest,
  source identity, environment/stdout/stderr redaction, plugin-shadowing and
  interrupted-run cases.
- Focused Ruff check and format check must pass on every changed Python source
  and test.
- Run one fresh poisoned-DB/socket-denied collect-only invocation with an empty
  new ledger and new evidence path; prove zero test bodies, fixture DB creates,
  connections and CREATE attempts.
- A new independent review must issue PASS before any real-DB task is eligible.

## Scope and preservation statement

No production or harness repair was made. No commit, merge, rebase, push,
stage, dependency change or real database operation was performed. Existing
R2/R3 evidence and historical UNKNOWN database records were not touched. The
only main-repository additions are this report and its task-specific evidence
directory. The existing dirty R4 checkout was not used as trusted execution
state and was not modified. `docs/workbench.html` remains untracked and was not
edited, staged, moved, deleted or included in task-attributable output.
