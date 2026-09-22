# TASK-WP04-02-VERIFIER-HARNESS-R4 Execution Report

Task: `TASK-WP04-02-VERIFIER-HARNESS-R4`
Executor: zcode
Evidence date: 2026-09-18
Verdict: **READY_FOR_INDEPENDENT_REVIEW**

## Objective

Fix the R3 verifier's test-case collection and evidence-saving failure by
building a version-controlled, self-testing verification tool that uses pytest
public hooks (`pytest_collection_finish`) for structured node-ID collection.
No terminal-output parsing, no `<Coroutine ...>` string matching.

## Baseline

- Branch: `codex/wp04-02-verifier-harness-r4`
- Worktree: `/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-verifier-harness-r4`
- Origin main: `675217c3a15c0f416aa4462ca6edc491bf99f9f6`
- Candidate: `codex/wp04-02-evidence-domain-service@e942cbcc9e0b595a6c7ee46d4d74ee90ff03ad4`

All five candidate SHA256 pins and all four main SHA256 pins verified intact.
Candidate worktree is clean (no modifications).  Main is clean.

## Delivered Files

```text
tg_verifier_tools/__init__.py
tg_verifier_tools/verification/__init__.py
tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py
tg_verifier_tools/verification/wp04_02_r4_runner.py
tg_verifier_tests/__init__.py
tg_verifier_tests/verification/__init__.py
tg_verifier_tests/verification/test_wp04_02_r4_runner.py
docs/development/BRANCH_WORKFLOW.md
docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R4-acceptance.md
docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R4-evidence/
```

## Test Results

### Tool Self-Tests

```text
$ PYTHONPATH="/tmp/tg_vft_test:tg_verifier_tests" pytest tg_verifier_tests/ -v
======================= 21 passed in 2.70s =======================
```

Coverage:
- `validate_collection`: correct 41, missing, extra, duplicates, wrong distribution, empty
- `_classify_nodeid`: known prefixes and unknown input (6 parametrize cases)
- `compute_distribution`: correct and empty
- `sha256_text` / `sha256_file`: deterministic hashing
- `redact_env`: sensitive key masking
- `EvidenceBundle`: write, manifest, self-exclusion
- `test_collect_only_end_to_end`: full collect-only run against candidate worktree

### Collect-Only End-to-End

```text
$ python3 tg_verifier_tools/verification/wp04_02_r4_runner.py \
    --mode collect-only \
    --candidate-root <candidate> --main-root <main> ...
{
  "valid": true,
  "verdict": "PASS",
  "count": 41,
  "distribution": {
    "forbidden_status_commit_fresh_no_residue": 20,
    "allowed_routing_history_audit": 16,
    "committed_exact_replay_read_only": 3,
    "legacy_forbidden_prior_committed_replay": 2
  }
}
```

- Real DB execution count: **0**
- CREATE attempts: **0 / 41**
- All baseline pins matched.

### Quality

```text
$ ruff check tg_verifier_tools/ tg_verifier_tests/verification/test_wp04_02_r4_runner.py
All checks passed!

$ ruff format --check tg_verifier_tools/ tg_verifier_tests/verification/test_wp04_02_r4_runner.py
5 files already formatted
```

## What This Task Does NOT Do

- Does NOT run any real PostgreSQL business tests (0 real executions, 0 CREATEs).
- Does NOT modify the candidate branch, assertions, or fixtures.
- Does NOT close WP-04-02 or the full 05C-01 matrix.
- Does NOT merge into `main`.

## Boundary

This is a verifier harness correction and self-test deliverable.  The tool
can now be used by a subsequent independent session to run the real focused
DB verification.  Even focused PASS does not close WP-04-02.
