# TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1-INDEPENDENT-REVIEW-R1

**OVERALL: FAIL**

## Metadata

- Task ID: `TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1`
- Review ID: `TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1-INDEPENDENT-REVIEW-R1`
- Date: 2026-09-21, Asia/Shanghai
- Verifier: Codex independent verification session
- Report Path:
  `docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R1-INDEPENDENT-REVIEW-R1-acceptance.md`
- Implementation Status: `IMPLEMENTATION_COMPLETE` reported by executor;
  independently not accepted
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`,
  `L3_CONTRACT_VERIFIED`, collect-only `L4_RUNTIME_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, partial
  happy-path collect-only `L4_RUNTIME_VERIFIED`
- Missing Acceptance: `L3_CONTRACT_VERIFIED`, complete collect-only
  `L4_RUNTIME_VERIFIED`
- `L4_DB_VERIFIED`: not required, not run and not authorized
- Repair Required: YES
- Repair ID: `TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R2`

## Decision

The takeover successfully repaired the previously demonstrated source
attribution, interruption closure, plugin authentication and embedded-value
redaction failures. It also preserved the exact 41-node structured collection
happy path. However, two Blocking contract failures remain:

1. the runner reads the complete inherited process environment, including
   unrelated sensitive values, before a child subprocess starts; and
2. the final outer evidence manifest omits five retained nested manifest files.

Either failure independently prevents PASS under `No Evidence, No PASS`,
`Blocking AC Failure -> Overall FAIL` and the frozen credential/evidence
requirements. No real PostgreSQL task is authorized.

## Changed Files Snapshot

### Baseline

- R5 worktree:
  `/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-verifier-harness-r5-repair`
- Branch: `codex/wp04-02-verifier-harness-r5-repair`
- HEAD: `df836cb39a1234aae967553b3783a67df9ad6672`
- Parent: `675217c3a15c0f416aa4462ca6edc491bf99f9f6`
- Main HEAD: `675217c3a15c0f416aa4462ca6edc491bf99f9f6`
- Candidate:
  `codex/wp04-02-evidence-domain-service@e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`
- Candidate parent:
  `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`
- Candidate state: clean

### Task-attributable source/test changes

Only the three authorized tracked files differ from R4 HEAD:

1. `tg_verifier_tools/verification/wp04_02_r4_runner.py`
2. `tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py`
3. `tg_verifier_tests/verification/test_wp04_02_r4_runner.py`

The takeover execution report and evidence are confined to the authorized
takeover delivery paths. Historical zcode delivery artifacts remain present
and unchanged. Attribution is `CERTAIN`.

The independent review added only this report, its independent evidence and
the R2 repair prompt under main's existing governance directories. It did not
modify the R5 implementation, candidate, historical evidence or Git history.

## Classification

- Task Type: `REPAIR / SECURITY / CLI_VERIFIER_HARNESS`
- Risk Type: credential handling, audit evidence integrity, fail-closed runtime
- Touched Layers: verifier runner, pytest plugin, verifier tests, execution evidence
- Task Size: `MEDIUM`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture,
  G4 Test, G5 Regression, G6 Evidence
- DB Persistence Gate: `NOT_APPLICABLE`; no persistence implementation changed
- Browser Gate: `NOT_APPLICABLE`

## Top Blocking AC Results

| Top AC | Result | Independent evidence |
|---|---|---|
| R-01 Final-source attribution | PASS | Final runner live/retained hashes match; plugin live/staged/recorded/retained hashes all match |
| R-02 Timeout/interruption closure | PASS | 80-test suite passes; controlled SIGINT evidence is non-successful and closed; staging cleanup preserved |
| R-03 Collision-resistant authenticated staging | PASS | Private random namespace, preflight staged hash validation, plugin self-authentication and collision test present |
| R-04 Complete value redaction / no credential discovery | FAIL | Embedded URL/metadata redaction works, but `run_collect_only` calls `_collect_sensitive_values(dict(os.environ))`; synthetic counterexample proves unrelated inherited sensitive value is read before pytest |
| R-05 Complete regression and execution evidence | FAIL | Required evidence exists, but outer manifest lists 55 of 60 retained files and omits five nested manifests |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Main/candidate/R5 identities independently re-read; candidate clean |
| G1 Scope | PASS | Only three authorized tracked files changed; delivery paths are authorized |
| G2 Contract | FAIL | Full inherited environment inspection violates frozen credential boundary |
| G3 Architecture | PASS | Private authenticated plugin staging and source attribution are implemented coherently |
| G4 Test | PASS | Fresh `80 passed`; Ruff, format, compileall and diff check pass |
| G5 Regression | PASS | Fresh guarded collect-only preserves 41 unique node IDs, 20/16/3/2 and zero body/socket/ledger activity |
| G6 Evidence | FAIL | Outer recursive manifest inventory is incomplete by five retained files |

## Evidence Matrix

| AC | Requirement | Implementation evidence | Verification evidence | Boundary / negative evidence | Verdict |
|---|---|---|---|---|---|
| R-01 [BLOCKING] | Final runtime evidence binds exact live/staged/retained source | `_source_hashes`; pre/post subprocess equality checks | Independent SHA-256 recomputation | Runner and plugin all equal | PASS |
| R-02 [BLOCKING] | Owned bundle closes on timeout/interruption/startup failure | `run_subprocess`, `_close_bundle`, `finally` cleanup | Fresh 80-test suite; retained controlled-interruption bundle | Non-zero, category 130, closed manifest | PASS |
| R-03 [BLOCKING] | Private collision-resistant authenticated staging | `StagedPlugin`, `_stage_plugin_to_temp`, `_verify_staged_plugin`, plugin `pytest_configure` | Fresh suite plus source inspection | Ambient collision and staged mismatch tests | PASS |
| R-04 [BLOCKING] | Redact evidence without discovering complete inherited credentials | Recursive output redaction exists, but runner inspects `dict(os.environ)` | Synthetic spy captured unrelated sensitive inherited key/value before any child process | Main identity was forced to fail; read still occurred | FAIL |
| R-05 [BLOCKING] | Final outer manifest recursively covers every retained file except itself | Outer `manifest.json` contains 55 entries | Independent filesystem/hash traversal found 60 eligible files | Five nested `manifest.json` files absent from outer inventory | FAIL |
| REG-01 [BLOCKING] | Preserve structured collect-only and zero-DB behavior | Public collection hook and exact node contract retained | Fresh isolated guarded CLI exit 0 | Socket log and ledger absent; body count 0 | PASS |

## Commands Actually Executed

| Command / check | Result | Purpose |
|---|---|---|
| Focused pytest suite with `-p no:cacheprovider` | `80 passed in 1.60s`, exit 0 | Contract and regression suite |
| `ruff check --no-cache` on three authorized files | exit 0 | Static quality |
| `ruff format --check --no-cache` on three authorized files | exit 0; 3 formatted | Formatting |
| `python3 -m compileall` with pycache redirected to `/private/tmp` | exit 0 | Parse/compile verification without worktree mutation |
| `git diff --check` | exit 0 | Diff integrity |
| Recursive outer/inner manifest audit | outer FAIL: 60 actual vs 55 listed; all listed hashes valid; all inner manifests internally valid | Evidence completeness |
| Synthetic inherited-environment spy | sensitive inherited value read before subprocess | Credential boundary counterexample |
| Fresh guarded collect-only under `env -i` | exit 0; 41 / 20 / 16 / 3 / 2 | Runtime preservation |

## Counterexample / Negative Verification

| Risk | Checked | Evidence | Verdict |
|---|---|---|---|
| Unrelated inherited sensitive variable is inspected | Yes | Collector received `UNRELATED_PASSWORD_BACKUP` and its synthetic value even though baseline failed before pytest | FAIL |
| Outer manifest silently omits retained files | Yes | Five nested manifests absent; no hash mismatch among listed entries | FAIL |
| Staged plugin bytes differ from final source | Yes | Independent hashes equal; mismatch test blocks before pytest | PASS |
| Embedded credential URL leaks in evidence | Yes | Delivered negative bundle and fresh tests retain no configured synthetic URL secrets | PASS |
| Controlled SIGINT leaves open evidence | Yes | Delivered bundle has result and valid inner manifest | PASS |
| Happy path opens DB/socket or runs bodies | Yes | Fresh guard and ledger absent; `test_body_calls=0` | PASS |

## Blocking Findings

### B-06 — Complete inherited environment is read before minimalization

At `run_collect_only`, the implementation executes:

```python
sensitive_values = _collect_sensitive_values(dict(os.environ))
```

This copies and inspects the complete inherited process environment. The
operation happens before Git/pin failure returns and before `_build_minimal_env`
constructs the child environment.

An independent test used only synthetic values and forced main identity failure
so no child process could start. A spy around `_collect_sensitive_values`
observed the unrelated key `UNRELATED_PASSWORD_BACKUP` and confirmed its
synthetic sensitive value had been read.

The frozen R5 contract requires an explicit minimal environment and states that
the verifier must not discover or read real credential values. Reading all
inherited credentials merely to redact possible later output does not satisfy
that boundary. Output redaction is improved, but credential non-discovery is
still false.

### B-07 — Outer manifest omits five retained nested manifests

The takeover evidence directory contains 61 files total. Excluding only the
outer root `manifest.json` leaves 60 files that the final outer manifest must
cover. The outer manifest lists 55.

Missing entries:

1. `harness-run/manifest.json`
2. `negative/controlled-interruption/manifest.json`
3. `negative/embedded-url-redaction/manifest.json`
4. `negative/interruption/manifest.json`
5. `negative/staged-mismatch/manifest.json`

All 55 listed entries have correct byte sizes and SHA-256 values, and every
inner manifest is internally valid. The failure is specifically outer
inventory completeness. From the outer bundle's perspective, nested manifests
are retained files; the original R5 contract says to exclude only the manifest
itself, meaning the outer root manifest, not every file named `manifest.json`.

## Passed / Preserved Behavior

The FAIL result does not invalidate the following independently verified
improvements:

- final runner source matches retained runner source;
- final plugin source matches staged, recorded and retained plugin bytes;
- staged plugin uses a random private namespace rather than the public package;
- staged mismatch blocks before pytest;
- embedded URL userinfo/query credentials and nested metadata are redacted;
- controlled interruption and startup failure produce non-successful closed bundles;
- pre-existing evidence paths remain immutable;
- main/candidate Git identity and pin mismatches fail closed;
- 80 focused tests pass;
- Ruff, formatting, compileall and diff checks pass;
- independent final-source collect-only returns exactly 41 unique node IDs and
  distribution 20/16/3/2;
- test body count is zero;
- independent socket guard and DB ledger remain absent;
- the fresh inner harness manifest is complete and all hashes match.

The R2 repair must preserve every item above.

## Final Decision Rationale

`FAIL` is required because R-04 and R-05 are Blocking acceptance criteria.
The implementation is functional on the isolated happy path but still violates
the credential non-discovery contract and delivers an incomplete outer evidence
inventory. Passing tests and valid listed hashes cannot override either failure.

## Next Action

Dispatch only
`TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R2` to a new Codex
implementation session. It must remove complete inherited-environment
inspection and regenerate a complete, immutable R2 evidence bundle whose outer
manifest includes nested manifests. A different Codex session must then perform
full independent re-verification.

No real PostgreSQL validation, merge, rebase, push, WP-04-03, 05C-02/R1D or
later feature work is authorized.

## Independent Evidence

- `verification-summary.json`
- `inherited-environment-counterexample.json`
- `outer-manifest-audit.json`
- `fresh-collect-only-summary.json`
- `source-attribution.json`
- `manifest.json`

