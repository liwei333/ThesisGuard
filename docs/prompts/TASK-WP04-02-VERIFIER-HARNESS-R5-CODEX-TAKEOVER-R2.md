# TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R2

## Target Envelope

This prompt is for a **new Codex implementation session**. The session that
performed `TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1-INDEPENDENT-REVIEW-R1`
is the verifier and must not implement this repair.

- Executor: new Codex implementation session
- Independent verifier: another Codex session after delivery
- Task type / size: `SECURITY_AND_EVIDENCE_REPAIR / SMALL`
- Original task:
  `TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1`
- Failed AC: R-04 credential non-discovery; R-05 outer evidence completeness
- Failed gates: G2 Contract, G6 Evidence
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`,
  `L3_CONTRACT_VERIFIED`, collect-only `L4_RUNTIME_VERIFIED`
- `L4_DB_VERIFIED`: not required and not authorized
- Final executor status may only be `IMPLEMENTATION_COMPLETE` or `BLOCKED`

Do not declare `PASS`, `DONE`, `VERIFIED` or approve your own work.

## Required Context

Read completely before editing:

1. `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/AGENTS.md`
2. `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/prompts/TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1.md`
3. `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1-INDEPENDENT-REVIEW-R1-acceptance.md`
4. Its independent evidence directory.
5. The current full diff, tests, R1 execution report and R1 evidence in the R5
   worktree.

Do not use the R1 executor's `IMPLEMENTATION_COMPLETE` as acceptance evidence.

## Exact Working State

Continue the existing worktree without reset, clean, stash or replacement:

- Worktree:
  `/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-verifier-harness-r5-repair`
- Branch: `codex/wp04-02-verifier-harness-r5-repair`
- HEAD: `df836cb39a1234aae967553b3783a67df9ad6672`
- Parent: `675217c3a15c0f416aa4462ca6edc491bf99f9f6`

Immutable external baselines:

- Main:
  `/Users/qianduoduo/Desktop/AI_app/ThesisGuard@675217c3a15c0f416aa4462ca6edc491bf99f9f6`
- Candidate worktree:
  `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`
- Candidate branch: `codex/wp04-02-evidence-domain-service`
- Candidate HEAD: `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`
- Candidate parent: `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`
- Candidate must remain clean.

If any identity has changed, stop `BLOCKED` before mutation.

Preserve the failed R1 execution report and R1 evidence byte-for-byte. Do not
rewrite them to manufacture a pass.

## Objective

Close only the two remaining Blocking failures:

1. eliminate complete inherited-environment inspection and prove unrelated
   sensitive inherited values are never read, copied, serialized or passed to
   the child; and
2. generate a new R2 evidence bundle whose outer manifest recursively includes
   every retained file except the outer manifest itself, including every nested
   `manifest.json`.

Preserve every R1 behavior that independently passed.

## Allowed Source/Test Scope — Maximum Two Files

You may modify only:

1. `tg_verifier_tools/verification/wp04_02_r4_runner.py`
2. `tg_verifier_tests/verification/test_wp04_02_r4_runner.py`

The plugin already passed independent acceptance and must not change. Do not
modify configuration, dependencies, production code, business tests or
fixtures.

You may add only:

3. `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R2-execution-report.md`
4. `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R2-evidence/`

If another source/test/config file is required, stop `BLOCKED`.

## Must Fix

### AC-R2-01 — No complete inherited credential discovery

The runner must not copy, enumerate or inspect the complete inherited
`os.environ` to build a redaction set. In particular, remove the behavior
represented by:

```python
_collect_sensitive_values(dict(os.environ))
```

Requirements:

- Before the minimal child environment exists, use no inherited credential
  values for redaction.
- Build child environment only from a fixed allowlist of process basics and
  verifier-owned safe values.
- Do not inherit arbitrary `PASSWORD`, `TOKEN`, `SECRET`, `CREDENTIAL`,
  `DATABASE_URL`, `DSN`, auth, cookie or session variables.
- Collect redaction literals only from the explicit minimal child environment
  or other verifier-owned synthetic values.
- Collect-only must never require or inspect real database credentials.
- If database guard values are needed, generate verifier-owned synthetic
  loopback port-1 values and a fresh verifier-owned ledger path, or validate an
  explicitly allowed guard input without enumerating unrelated environment.
- Preserve recursive stdout/stderr/exception/metadata URL redaction.

Add a regression test that installs a synthetic unrelated sensitive inherited
variable and fails if its value is accessed or passed to
`_collect_sensitive_values`, the child environment or retained evidence. The
test must exercise `run_collect_only`, including an early baseline-failure
path, not only `_build_minimal_env` in isolation.

### AC-R2-02 — Complete outer evidence manifest

The new R2 outer manifest must recursively include every retained file except
the outer root `manifest.json` itself.

Nested files named `manifest.json` are ordinary retained artifacts from the
outer bundle's perspective and must be included with correct byte size and
SHA-256. Do not exclude files merely because their basename is
`manifest.json`.

Add a mechanical manifest verification step that compares:

- actual recursive retained-file paths, excluding only the exact outer
  manifest path; and
- manifest entry paths.

Require set equality, byte equality and SHA-256 equality. Generate the outer
manifest last and do not modify any R2 evidence file afterward.

## Must Preserve

- Main/candidate Git identity and pin fail-closed checks.
- Immutable rejection of pre-existing evidence leaves.
- Pytest non-zero, stale/missing nonce and malformed/schema-invalid collection
  fail-closed behavior.
- Random private staged-plugin namespace.
- Preflight staged-byte verification and plugin self-authentication.
- Staging cleanup on success, mismatch, ordinary failure and interruption.
- Timeout/startup/KeyboardInterrupt structured closure.
- Recursive output and metadata redaction for embedded credential URLs.
- Exact 41 unique node IDs and distribution `20 / 16 / 3 / 2`.
- `test_body_calls == 0`.
- Zero fixture-ledger events, socket attempts and CREATE activity.
- Final live/staged/recorded/retained source equality.
- All 80 existing focused tests; tests may be strengthened but not weakened,
  deleted or skipped.
- Historical zcode, R1 takeover and independent-review artifacts remain
  unchanged.

## High-Risk Counterexamples

1. Given an unrelated inherited variable such as
   `UNRELATED_PASSWORD_BACKUP=<synthetic>`, when `run_collect_only` fails before
   pytest, then the value must never be read by the sensitive-value collector,
   copied to a dictionary, passed to child env or retained in evidence.
2. Given nested successful and failed harness bundles each containing their own
   `manifest.json`, when the R2 outer manifest is built, then every nested
   manifest must be listed and hash/size verified; only the exact outer
   manifest path is excluded.
3. Given the normal guarded happy path, when environment handling is narrowed,
   then collection must still return exactly 41 / 20 / 16 / 3 / 2 with zero
   body, ledger, socket and CREATE activity.
4. Given controlled interruption and staged mismatch, when evidence is closed,
   then the negative inner manifests and outer references to those manifests
   must both verify.

## Required Verification

Run from the existing R5 worktree using installed tools only:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/pytest \
  -p no:cacheprovider \
  tg_verifier_tests/verification/test_wp04_02_r4_runner.py \
  -q --tb=short

ruff check --no-cache \
  tg_verifier_tools/verification/wp04_02_r4_runner.py \
  tg_verifier_tests/verification/test_wp04_02_r4_runner.py

ruff format --check --no-cache \
  tg_verifier_tools/verification/wp04_02_r4_runner.py \
  tg_verifier_tests/verification/test_wp04_02_r4_runner.py

python -m compileall \
  tg_verifier_tools/verification/wp04_02_r4_runner.py \
  tg_verifier_tests/verification/test_wp04_02_r4_runner.py

git diff --check
```

After source is final and formatted, run exactly one new R2 guarded
collect-only against the immutable candidate using `env -i`, a verifier-owned
synthetic loopback port-1 URL, a fresh empty ledger path and a fail-closed
Python socket guard. Require:

- CLI exit 0 and pytest return 0;
- current nonce match;
- 41 unique node IDs, exact 20/16/3/2;
- zero body calls;
- absent/empty ledger and socket logs;
- zero CREATE activity;
- live/staged/recorded/retained source hashes equal;
- complete inner manifest.

Regenerate controlled interruption, staged mismatch and embedded-URL negative
bundles under the new R2 evidence directory. Every negative path must be
non-successful, sanitized and closed.

Finally generate the R2 outer manifest and independently recompute its exact
inventory. A valid result must report all retained files except one: the outer
manifest itself. Explicitly list the nested manifest paths in the report.

## Evidence and Deliverables

The R2 evidence directory must contain:

- baseline identities and starting hashes;
- focused tests and quality command outputs;
- inherited-environment non-access counterexample result;
- guarded no-DB proof;
- final source hashes;
- final state and changed-file inventory;
- final positive harness bundle;
- representative negative bundles;
- an outer manifest that includes every nested manifest;
- a post-generation manifest audit proving inventory, size and hash equality.

The R2 execution report must map AC-R2-01 and AC-R2-02 to exact code, tests,
commands and evidence. Record execution time, repair count and visible
token/cost (`UNKNOWN` if unavailable).

## Forbidden

- No complete inherited-environment copy or enumeration.
- No reading real credential values.
- No deletion, rewrite or repair-in-place of failed R1 evidence.
- No plugin modification.
- No weakening/deleting/skipping existing tests.
- No business-candidate, main, dirty R4 worktree, production code, business
  test, fixture, dependency or configuration change.
- No real PostgreSQL connection or database operation.
- No commit, merge, rebase, push, reset, clean or stash.
- No WP-04-03, 05C-02/R1D, Capability Runtime or Sector Crowding work.

## Completion Rule

Return `STATUS: IMPLEMENTATION_COMPLETE` only after both failed ACs and every
preserved regression have complete evidence. Otherwise return
`STATUS: BLOCKED` with the exact unmet condition. Do not self-approve.

End with:

`Awaiting a separate Codex independent acceptance. No real PostgreSQL task, merge, push, 05C-02/R1D or WP-04-03 work is authorized by this delivery.`

