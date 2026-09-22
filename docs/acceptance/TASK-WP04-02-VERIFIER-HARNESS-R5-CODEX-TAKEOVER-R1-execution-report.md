# TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1 — Execution Report

`STATUS: IMPLEMENTATION_COMPLETE`

## Scope and immutable identities

- Executor: Codex takeover implementation session.
- Required independent acceptance: a different Codex session; not performed here.
- R5 worktree: `/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-verifier-harness-r5-repair`
- Branch / unchanged HEAD: `codex/wp04-02-verifier-harness-r5-repair` / `df836cb39a1234aae967553b3783a67df9ad6672`
- Main unchanged HEAD: `675217c3a15c0f416aa4462ca6edc491bf99f9f6`
- Candidate unchanged HEAD / parent: `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4` / `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`
- Candidate final state: clean.
- Historical zcode report SHA-256 remains `bc59272b2ef8e88ecb2c9e984f8527036c959e86039ecf75edeec95f2da8338b`.
- Historical zcode outer-manifest SHA-256 remains `f365f1ee253ecc7170916aa517c1c103bd3c8829bd53940857fc8a8d11d01dc3`.

Only the three authorized source/test files were modified. New files are confined to the takeover report and takeover evidence directory. No dependency, configuration, main, candidate, dirty R4 worktree, historical report or historical evidence file was changed.

## Independent finding repair map

| Finding | Code repair | Executable coverage | Retained evidence |
|---|---|---|---|
| B-01 final source attribution | `_source_hashes` records runner live/retained and plugin live/staged/recorded/retained hashes; the runner rechecks after subprocess collection and blocks on drift. Source copies are written before runtime and no source was edited after the final run. | `test_collect_only_end_to_end` asserts final equality. | `harness-run/source-hashes.json`, `final-source-hashes.json` |
| B-02 interruption leaves open bundle | `run_subprocess` preserves timeout/startup/interruption categories and return codes; `run_collect_only` closes every owned path through `_close_bundle`; `finally` removes staging. `KeyboardInterrupt` maps to return code 130 and non-success. | Timeout test, owned-bundle KeyboardInterrupt test, ordinary-failure cleanup test, missing executable test, and actual controlled-interruption CLI. | `negative/controlled-interruption/`, `negative/interruption/`, `negative-cli-summary.json` |
| B-03 public namespace and unauthenticated staging | `_stage_plugin_to_temp` copies only one plugin under a 128-bit random private namespace; pytest receives that private module; source/staged SHA-256 is checked before startup and the staged plugin authenticates its own bytes through `TG_R4_PLUGIN_SHA256`. | Private-namespace byte test, real subprocess ambient-collision test, mismatch-before-pytest test, cleanup tests on success/failure/interruption. | `negative/staged-mismatch/`, `harness-run/plugin-staging.json`, `harness-run/source-hashes.json` |
| B-04 incomplete redaction | `_redact_embedded_urls` handles URLs inside surrounding strings, including path-normalized single-slash forms; `_redact_metadata` recursively sanitizes mappings/lists/tuples and all metadata before JSON. Known sensitive literal replacement and sensitive-key classification remain. | Embedded URL tests for text, stdout, stderr and startup exceptions; recursive argv/cwd/error test; final recursive secret scan. | `negative/embedded-url-redaction/`, `negative-cli-summary.json` |
| B-05 incomplete execution evidence | Added the missing regression categories, final guarded run, closed negative bundles, baseline/final state, command records, no-DB proof and recursive outer inventory. | Focused suite now collects 80 tests; all returned exit 0. | Complete takeover evidence directory and final outer manifest |

## Implementation details

### Interruption and closure

- Once a new leaf is owned, every handled return path writes atomic `result.json` and a recursive `manifest.json`.
- Timeout retains return code 124 and category `timeout`.
- Controlled `KeyboardInterrupt` retains return code 130 and category `interrupted`.
- Executable/startup errors retain category `startup_failure`; ordinary pytest failures retain their subprocess return code.
- A pre-existing evidence leaf remains immutable and is rejected before ownership.
- Temporary plugin staging is removed in `finally` for success, pytest failure, mismatch and interruption.

### Private authenticated plugin staging

- Namespace form: `_tg_wp04_02_verifier_<128-bit random hex>.plugin`.
- Staging contains only `__init__.py` plus `plugin.py`; it no longer copies `tg_verifier_tools`.
- Only the private staging root is prepended to the child `PYTHONPATH`; ambient/candidate `tg_verifier_tools` cannot name the selected plugin.
- The runner compares current source, recorded source and staged bytes before pytest.
- The staged plugin computes its own file SHA-256 during pytest configuration and refuses a mismatch.
- After collection, live/staged/retained equality is checked again before a successful result can be published.

### Redaction and no-DB guards

- Credential-bearing URLs are redacted as complete or embedded values.
- Structured `argv`, `cwd`, `env`, nested error data, stdout and stderr are sanitized recursively.
- The child environment remains minimal while explicitly carrying only the synthetic `TG_TEST_ADMIN_DATABASE_URL` and fresh `TG_EVIDENCE_PG_LEDGER` guard values needed for the final run; the URL is redacted in metadata.
- The private plugin records `test_body_calls`; the runner requires exactly zero.

## Required commands and exact outcomes

```text
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/pytest -p no:cacheprovider tg_verifier_tests/verification/test_wp04_02_r4_runner.py -q --tb=short
exit 0; collected 80; 80 passed in 1.48s

ruff check --no-cache <three authorized files>
exit 0; All checks passed!

ruff format --check --no-cache <three authorized files>
exit 0; 3 files already formatted

python -m compileall tg_verifier_tools/verification tg_verifier_tests/verification/test_wp04_02_r4_runner.py
exit 0; all authorized Python files compiled

git diff --check
exit 0; no output
```

The first sandboxed quality invocation could not create Ruff cache or bytecode outside the writable root. It made no source change. The same required checks were rerun with scoped filesystem approval; the results above are those completed runs.

## Pre-repair counterexamples

- Embedded URL and recursive metadata selection: exit 1, two targeted failures.
- Owned-bundle KeyboardInterrupt selection: exit 2 with escaping `KeyboardInterrupt`.
- Old staging copied the whole public package; focused probes reached approximately 0.8–0.9 GiB RSS and were stopped.
- Old final live runner SHA-256 `201966382113a5a29e13876a36cb9ac0cd0a4efa7b9ea8d96d8924de025191fc` differed from historical retained runner SHA-256 `944e4a61f3ea1ce2a3746f7e54303bcd4a600dba6719eef56a794506f3cb6e02`.

Exact observations are retained in `independent-counterexample-reproduction.txt`.

## Retained negative CLI evidence

| Case | CLI exit | Preserved category / code | Closed bundle |
|---|---:|---|---|
| Controlled SIGINT | 1 | `interrupted` / subprocess 130 | result + 9-artifact manifest |
| Missing relative synthetic executable | 1 | `startup_failure` / subprocess 1 | result + 9-artifact manifest |
| Tampered staged plugin | 1 | `staged_plugin_mismatch`; pytest not started | result + 6-artifact manifest |
| Embedded synthetic credential URL in executable path | 1 | `startup_failure` / subprocess 1 | result + 9-artifact manifest; zero secret-literal matches |

All negative leaves were new, non-successful, sanitized, recursively manifested and left immutable.

## Final guarded collect-only

The sole final guarded CLI run after formatting used `env -i`, an explicit minimal parent environment, only a synthetic `127.0.0.1:1` PostgreSQL URL, a fresh ledger path, and a `sitecustomize` socket guard that logs then raises on all connection attempts.

Observed outcome:

- CLI exit: `0`
- runner `valid`: `true`
- pytest return code: `0`
- invocation nonce: `b8a912a4646974d5a7af91d571e8029d`
- node IDs: `41`, unique `41`
- distribution: `20 / 16 / 3 / 2`
- test-body calls: `0`
- fixture ledger: absent/empty
- socket-attempt log: absent/empty
- CREATE SQL matches: `0`
- real credentials/services: none
- inner recursive manifest: 10 non-manifest artifacts; all sizes and SHA-256 values independently recomputed successfully

Final source attribution:

| Source | Final SHA-256 | Equality |
|---|---|---|
| runner live / retained | `3ee2be0614c9ba6ebc9b2f305ec8e26e49c5d11adc0fc72ddecbc05e9e92e537` | equal |
| plugin live / staged / recorded / retained | `3ab4b45feb356fcecdaa5363f09d3256dc0c6a2b8f2bb067d32da8438f3bdbc4` | all equal |
| focused test file | `506e038c9159cf2846f2a3a90e9386817399d1c4918a8312de2a07aadeb8e99f` | final formatted bytes |

## Changed-file and delivery inventory

Tracked source/test diff versus unchanged R5 HEAD:

| File | Insertions | Deletions |
|---|---:|---:|
| `tg_verifier_tests/verification/test_wp04_02_r4_runner.py` | 904 | 35 |
| `tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py` | 54 | 22 |
| `tg_verifier_tools/verification/wp04_02_r4_runner.py` | 781 | 212 |

New takeover delivery paths:

- `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1-execution-report.md`
- `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1-evidence/`

The larger diff totals include the intentionally uncommitted zcode R5 delivery that this takeover repaired in place. No commit, merge, rebase, reset, clean, stash, push or worktree replacement was performed.

## Metrics and disposition

- Takeover repair cycles: 3 focused implementation cycles (core closure/staging/redaction; missing contract regressions; explicit port-1/ledger guard propagation).
- Focused regression runtime: 1.48 seconds.
- Final guarded CLI runtime: 6.6 seconds.
- Overall visible wall time: approximately 50 minutes; exact session-wide timer was not instrumented.
- Visible token usage: UNKNOWN.
- Visible cost: UNKNOWN.
- Executor disposition: `IMPLEMENTATION_COMPLETE`.
- Independent acceptance disposition: pending a separate Codex session.

Awaiting a separate Codex independent acceptance. No real PostgreSQL task, merge, push, 05C-02/R1D or WP-04-03 work is authorized by this delivery.
