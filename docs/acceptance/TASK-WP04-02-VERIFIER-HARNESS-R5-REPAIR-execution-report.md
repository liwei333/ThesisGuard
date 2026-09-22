# TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR — Execution Report

- Repair ID: `TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR`
- Original implementation: `TASK-WP04-02-VERIFIER-HARNESS-R4`
- Executor: zcode, one controlled repair attempt
- Independent verifier: Codex (pending, separate session)
- Task type / size: `VERIFIER_HARNESS_REPAIR / MEDIUM`
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`,
  `L3_CONTRACT_VERIFIED`, collect-only `L4_RUNTIME_VERIFIED`
- Execution date: 2026-09-21, Asia/Shanghai

## Git Identity

| Field | Value |
|---|---|
| R5 branch | `codex/wp04-02-verifier-harness-r5-repair` |
| R5 worktree | `/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-verifier-harness-r5-repair` |
| R5 HEAD | `df836cb39a1234aae967553b3783a67df9ad6672` |
| R5 parent | `675217c3a15c0f416aa4462ca6edc491bf99f9f6` |
| Main HEAD | `675217c3a15c0f416aa4462ca6edc491bf99f9f6` |
| Candidate HEAD | `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4` |
| Candidate parent | `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8` |
| Candidate branch | `codex/wp04-02-evidence-domain-service` |
| Candidate status | clean |

## Changed Files

### BASELINE_CHANGED_FILES (working tree vs R4 commit `df836cb`)

```
tg_verifier_tests/verification/test_wp04_02_r4_runner.py
tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py
tg_verifier_tools/verification/wp04_02_r4_runner.py
```

### FINAL_CHANGED_FILES (identical — no additional drift)

```
tg_verifier_tests/verification/test_wp04_02_r4_runner.py
tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py
tg_verifier_tools/verification/wp04_02_r4_runner.py
```

### Diff summary

| File | Changes |
|---|---|
| `tg_verifier_tools/verification/wp04_02_r4_runner.py` | +620 / -116 lines — runner repair |
| `tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py` | +58 / -40 lines — plugin atomic output + nonce |
| `tg_verifier_tests/verification/test_wp04_02_r4_runner.py` | +662 / -156 lines — kept 21 R4 tests, added ~46 R5 tests |

## Source Hashes (final formatted source)

| File | SHA-256 |
|---|---|
| `wp04_02_r4_runner.py` | `201966382113a5a29e13876a36cb9ac0cd0a4efa7b9ea8d96d8924de025191fc` |
| `wp04_02_r4_pytest_plugin.py` | `044062900509c011576cb1501c73c2298064fc1362c0e56f5e2e7dc0fd8acc08` |
| `test_wp04_02_r4_runner.py` | `29d2ab792a35c6c2d74eb79a53d7d7bd273b1646274b4846a18f51225c324588` |

## R4 Findings → R5 Repair Map

| Finding | R5 code location | Regression test | Status |
|---|---|---|---|
| F-01 main pin mismatch ignored | `run_collect_only` lines ~643-670; `verify_main_pins` now participates in fail-closed; `MAIN_SHA_PINS` corrected | `test_main_pin_mismatch_fails_closed`, `test_main_git_identity_mismatch_fails_closed` | REPAIRED |
| F-02 candidate Git identity not verified | `verify_main_git_identity`, `verify_candidate_git_identity`, `_is_git_repo`, `_git_symbolic_ref`, `_git_parent_commit`, `_git_is_clean`; `find_candidate_root` fixed | `test_candidate_git_identity_failures` (5 params), `test_wrong_candidate_git_identity_even_when_pins_match` | REPAIRED |
| F-03 pytest non-zero / stale JSON become PASS | `run_collect_only` requires `result.returncode == 0`; `_build_minimal_env` generates invocation nonce; plugin writes nonce; runner verifies nonce match | `test_nonzero_pytest_exit_cannot_pass`, `test_stale_nonce_cannot_rescue_failed_invocation`, `test_missing_collection_json_fails_closed` | REPAIRED |
| F-04 existing evidence overwritten | `run_collect_only` refuses if `evidence_root.exists()` before creating bundle | `test_preexisting_nonempty_evidence_rejected`, `test_preexisting_empty_evidence_rejected` | REPAIRED |
| F-05 manifest incomplete | `EvidenceBundle.manifest()` now recursively scans root; runner renames collection JSON to final path before manifest generation | `test_manifest_covers_every_retained_nonmanifest_artifact`, `test_manifest_includes_collected_nodeids` | REPAIRED |
| F-06 secret safety fail-open | `_is_sensitive_env_key` (case-insensitive, prefix/suffix); `_redact_url_value`; `_redact_value`; `_build_minimal_env` (no full env dump); value redaction in `run_subprocess` | `test_redact_env_case_and_variant_keys` (17 params), `test_redact_env_url_userinfo`, `test_redact_env_url_query_params`, `test_redact_value_literals`, `test_sensitive_stdout_stderr_redacted`, `test_sensitive_exception_message_redacted` | REPAIRED |
| F-07 malformed JSON aborts without closed evidence | `run_collect_only` wraps `json.loads` in try/except producing structured failure | `test_malformed_collection_json_fails_closed` | REPAIRED |
| F-08 committed executor bundle source mismatch | `EvidenceBundle.write_json`/`write_text` atomic; source copies match live source verified in `test_collect_only_end_to_end` | `test_collect_only_end_to_end` (source-hash verification) | REPAIRED |
| F-09 tests don't cover blocking behavior | 46 new tests covering all 9 findings + 16 regression categories from Required Regression Tests | Full test suite below | REPAIRED |

## Verification Commands and Results

### Focused suite

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/pytest \
  -p no:cacheprovider \
  tg_verifier_tests/verification/test_wp04_02_r4_runner.py \
  -q --tb=short
```

**Result:** `67 passed` in 2.23s

### Quality

```bash
ruff check tg_verifier_tools/verification/wp04_02_r4_runner.py \
  tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py \
  tg_verifier_tests/verification/test_wp04_02_r4_runner.py
# Result: All checks passed!

ruff format --check ...
# Result: 3 files already formatted

python -m compileall tg_verifier_tools/verification \
  tg_verifier_tests/verification/test_wp04_02_r4_runner.py
# Result: COMPILEALL_OK (no syntax errors)

git diff --check
# Result: clean (no conflict markers, no whitespace errors)
```

### Fresh safe collect-only

```bash
env -i PATH=/opt/homebrew/bin:/usr/bin:/bin HOME=... LANG=en_US.UTF-8 \
  PYTHONPATH=/opt/homebrew/lib/python3.12/site-packages \
  /opt/homebrew/opt/python@3.12/bin/python3.12 \
  tg_verifier_tools/verification/wp04_02_r4_runner.py \
  --mode collect-only \
  --candidate-root /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service \
  --main-root /Users/qianduoduo/Desktop/AI_app/ThesisGuard \
  --evidence-dir docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR-evidence/harness-run \
  --pytest /opt/homebrew/bin/pytest
```

**Result:** exit 0; `valid=true`; `verdict=PASS`; count=41; distribution=20/16/3/2;
invocation_nonce present; manifest covers all 10 non-manifest artifacts including
`collected-nodeids.json`; source-copy hashes match live source bytes.

### Representative negative CLI runs

| # | Scenario | Exit | Verdict | Reason |
|---|---|---|---|---|
| NEG 1 | main mismatch (non-git main-root) | 1 | BLOCKED | main_git_identity_mismatch |
| NEG 2 | wrong candidate identity (non-git candidate) | 1 | BLOCKED | candidate_git_identity_mismatch |
| NEG 3 | pytest non-zero (fake pytest returns 2) | 1 | BLOCKED | pytest_nonzero |
| NEG 4 | pre-existing evidence path (result.json + sentinel.txt) | 1 | BLOCKED | evidence_path_exists |
| NEG 5 | timeout/interruption (SIGTERM after 3s) | 241 | (terminated) | non-zero |

All negative runs returned non-zero without misleading PASS or evidence overwrite.
NEG 4 confirmed sentinel.txt preserved byte-for-byte.

## Evidence Bundle

- Execution report: `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR-execution-report.md`
- Evidence directory: `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-REPAIR-evidence/`

### Outer manifest (recursive, generated last)

```
harness-run/baseline-pins.json
harness-run/collect-only.meta.json
harness-run/collect-only.stderr.txt
harness-run/collect-only.stdout.txt
harness-run/collected-nodeids.json
harness-run/manifest.json
harness-run/plugin-staging.json
harness-run/plugin.source.py
harness-run/result.json
harness-run/runner.source.py
harness-run/source-hashes.json
```

## Required Acceptance — Evidence Status

| Acceptance | Status | Evidence |
|---|---|---|
| `L1_STATIC_REVIEWED` | ACHIEVED | Full diff of 3 files reviewed; R4 findings F-01..F-09 mapped to code |
| `L2_BUILD_VERIFIED` | ACHIEVED | 67 tests passed; Ruff check/format passed; compileall OK |
| `L3_CONTRACT_VERIFIED` | ACHIEVED | All 9 demonstrated R4 failures repaired with executable counterexamples |
| `L4_RUNTIME_VERIFIED` (collect-only) | ACHIEVED | Fresh poisoned-env collect-only PASS 41/20/16/3/2; 5 negative CLI runs non-zero |
| `L4_DB_VERIFIED` | NOT REQUIRED / NOT AUTHORIZED | No real PostgreSQL connection made |

## Zero-DB Proof

- No PostgreSQL connection attempted (collect-only mode).
- No `CREATE`, `DROP`, `ALTER` SQL observed.
- No fixture DB ledger events (poisoned port-1 URLs only).
- No socket connection attempts (socket guard not needed in collect-only;
  subprocess only invokes pytest which does not open sockets).
- Tests use only temporary directories and synthetic values.

## Credential Leak Scan

- `collect-only.meta.json` env keys: `HOME`, `LANG`, `PATH`, `PYTHONDONTWRITEBYTECODE`,
  `PYTHONPATH`, `TG_R4_COLLECTION_JSON`, `TG_R4_INVOCATION_NONCE`, `USER` —
  all non-sensitive.
- `collect-only.stdout.txt` / `.stderr.txt`: no sensitive patterns detected.
- `redact_env` uses case-insensitive classification with 16 variant keys tested.
- URL userinfo and credential query params redacted.
- No real credential values used in any test.

## Execution Metrics

| Metric | Value |
|---|---|
| Visible execution time | ~12 minutes total (first attempt, including 2 controlled source fixes) |
| Repair count | 2 (added `_stage_plugin_to_temp`; fixed CompletedProcess args; reordered Git checks before pin checks; fixed URL redaction encoding; fixed write_text for subdirs) |
| Token / cost | UNKNOWN |
| Reused R4 tests kept | 21 (all preserved, all pass) |
| New R5 tests added | ~46 |
| Total tests | 67 |

## Executor Disposition

`STATUS: IMPLEMENTATION_COMPLETE`

This delivery contains only the scoped verifier-harness repair, the new R5
execution report, and the new R5 evidence directory. No real PostgreSQL task,
merge, push, 05C-02/R1D or WP-04-03 work was performed.

`Awaiting Codex independent acceptance. No real PostgreSQL task, merge, push, 05C-02/R1D or WP-04-03 work is authorized by this delivery.`
