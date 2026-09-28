# TASK-WP04-02-R1C-05C-01 R7 Evidence Security Proof Protocol Repair R2 — Independent Review R1

## 1. Review identity

- Review task: `TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R2-FEEDBACK-INDEPENDENT-REVIEW-R1`
- Reviewed executor task: `TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R2`
- Reviewer: separate Codex independent verifier session
- Review mode: read-only inspection and offline verification; no PostgreSQL proof, R8, Docker mutation, database mutation, Git integration, commit, push, merge, reset, clean, or stash
- Review date: 2026-09-24 (Asia/Shanghai)
- Reviewed branch: `codex/wp04-02-r7-proof-protocol-repair-r2`
- Reviewed baseline and branch HEAD: `43df5fbf9e2b1a748ebd7ac22e8ba02c2832285b`
- Baseline parent: `9ba733448ba2941f70cc109cffb2399986ff7cc2`
- Reviewed worktree: `/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-r7-proof-protocol-repair-r2`

## 2. Verdict

`OVERALL: FAIL`

`STATUS: FAIL_OFFLINE_QUALITY_GATE`

The executor correctly stopped before the live proof when the mandatory Ruff check failed. That is a compliant execution stop, but it is not an accepted implementation. The failure is reproducible, deterministic, and repairable inside the already-authorized file scope; it is therefore an implementation/quality-gate failure rather than an unavailable external prerequisite.

No live PostgreSQL proof was run, so the R7 evidence-security repair is not runtime-verified and does not authorize R8 or the 41-scenario focused PostgreSQL suite.

## 3. Independent findings

### 3.1 Reproduced blocking defect

Independent Ruff invocation over the three changed Python files returned exit code 1 with exactly one finding:

- Code: `I001`
- File: `tg_verifier_tests/verification/test_wp04_02_r4_runner.py`
- Location: import block beginning at line 34
- Required mechanical correction: place `MAIN_HEAD` before `EvidenceBundle` in the imported-name list, as prescribed by Ruff

No broader lint defect was observed. The defect is fixable without changing production behavior or expanding scope.

### 3.2 Positive offline verification

The following were independently re-run against the uncommitted R2 worktree state:

- Combined deterministic proof and runner suites: `157 passed`, `0 failed`, `0 skipped`, exit code 0.
- Runner end-to-end path executed rather than skipped; the executor evidence records 41 unique node IDs with distribution `20 / 16 / 3 / 2`, zero test-body calls, zero socket attempts, no ledger, and zero CREATE attempts.
- Ruff format check over all three changed files: pass; all three already formatted.
- Python compilation with bytecode redirected to `/private/tmp`: pass.
- `git diff --check`: pass.
- The test-only historical-main checkout uses an isolated no-hardlink clone, detached at the runner's existing historical `MAIN_HEAD`, and asserts exact HEAD, detached state, and clean status.
- Counterexamples cover wrong historical HEAD and a dirty checkout.
- Credential scanning tests cover colonless, conventional, and percent-encoded authority userinfo plus the specified case-insensitive sensitive query-key variants; a normal URL remains a negative case.

These results support the substance of TOP-AC-01 through TOP-AC-03, but they do not override the failed mandatory Ruff gate.

### 3.3 Patch identity and worktree state

The reviewed worktree contains exactly three tracked modifications and the R2 report/evidence as untracked delivery material. There is no implementation commit.

- Binary diff SHA-256: `72f5fa9c8cf31c83dcb8aa1bd33440d171cf443a54b974d05b0f7bb1f6989a45`
- `tg_verifier_tools/verification/wp04_02_secure_pg_proof.py`: `098fb1235f3abb3e92e21fa3a0ce1ee0d8f4fd0660fec0601225d7f1b04a0a61`
- `tg_verifier_tests/verification/test_wp04_02_secure_pg_proof.py`: `d7a170a42a47782793c9c08453c48ca5b1c0e0ef0e54d053be3b40d6c6703dec`
- `tg_verifier_tests/verification/test_wp04_02_r4_runner.py`: `0b4d025b47ac599d2ad10d343d4cd7617d031c5c04e1b5345c50fb71e22927b4`

The retained `source-snapshots/allowed-files.diff` is byte-identical to the live tracked diff.

### 3.4 Evidence integrity and safety

- Execution report SHA-256: `491de2921da58a3324a439c1f51810ef31607e52f1825023fd530a5ef1bcac68`.
- Root manifest SHA-256: `d7b7d5675b66549846707654f972ad1101f834ae25ff0345bdd5cb1d3f2dcfd5`.
- Independent recursive manifest rebuild, excluding only the root `manifest.json`: 29 declared, 29 actual, 0 missing, 0 extra, 0 byte/hash mismatch.
- JSON parse audit: 29 JSON files parsed successfully.
- Independent bounded pattern scan of the report plus the complete evidence bundle: 31 files, zero file-level matches for URL userinfo or the covered quoted sensitive assignments.
- Proof invocation count: 0; retry count: 0.
- Database, Docker, R8, 41-scenario suite, and SQL mutation counters remain zero.

The blocked evidence bundle is internally coherent and accurately reports the failed Ruff gate. Passing evidence integrity does not make the implementation pass.

## 4. Acceptance levels and gates

| Item | Result | Reason |
|---|---|---|
| G0 Baseline identity | PASS | Branch and baseline match the R2 delivery; the diff is pinned by SHA-256. |
| G1 Scope | PASS | Tracked modifications are limited to the three authorized Python files. |
| G2 Static review | PASS | The complete tracked diff and relevant implementation/tests were reviewed. |
| G3 Build/static quality | FAIL | Ruff `I001` is reproducible. Format, compilation, and diff-check pass. |
| G4 Deterministic tests | PASS | Independent combined run: 157/157 passed with zero skips. |
| G5 Evidence closure | PASS for blocked delivery | Manifest, JSON, patch snapshot, and credential-oriented checks close correctly. |
| G6 Live PostgreSQL proof | NOT_RUN | Correctly withheld after the offline blocking gate failed. |

Required Acceptance:

- `L1_STATIC_REVIEWED`: achieved.
- `L2_BUILD_VERIFIED`: not achieved because the required Ruff check fails.
- `L3_CONTRACT_VERIFIED`: partially supported for TOP-AC-01 through TOP-AC-03, but not awarded task-wide while a mandatory offline gate fails.
- Narrow live `L4_RUNTIME_VERIFIED`: not achieved; proof invocation count is zero.
- Focused `L4_DB_VERIFIED`: not requested and not achieved.

## 5. Required repair disposition

A new R3 task is required. It must not overwrite or repurpose the R2 report/evidence. To avoid losing the already-reviewed implementation, R3 may import only the exact R2 tracked diff identified above into a fresh worktree at baseline `43df5fbf9e2b1a748ebd7ac22e8ba02c2832285b`, verify its hash before application, mechanically correct the single import-order issue, and then run the complete offline gate chain.

To reduce unnecessary task churn, the R3 executor may perform up to two controlled pre-proof repair/re-run cycles, but only inside the same three authorized Python files. Any failure requiring another file, any baseline drift, any credential exposure, or any proof failure remains fail-closed. The one-shot live proof may run only after every offline gate is green; the R2 proof budget was not consumed.

## 6. Prohibitions and non-authorizations

This review does not authorize:

- treating R2 as accepted or implementation-complete;
- modifying the runner's historical `MAIN_HEAD` pin;
- running R8 or the 41-scenario focused PostgreSQL suite;
- migrations, fixtures, DDL, DML, database cleanup, or backend termination;
- Git integration into `main`, push, PR, merge, 05C-02, R1D, or WP-04-03;
- deleting, overwriting, renaming, or repurposing R1/R2 historical reports or evidence.

The next authorized action is the bounded R3 repair-and-proof task described in the user-facing dispatch prompt.
