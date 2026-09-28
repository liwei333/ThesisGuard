# R3 Proof Protocol Repair — Feedback Independent Review R1

**OVERALL: FAIL**

**Reason: the live proof failure is caused by a deterministic default-loader implementation defect, not by an unavailable external credential or PostgreSQL environment.**

## Metadata

- Task ID: `TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R3`
- Review ID: `TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R3-FEEDBACK-INDEPENDENT-REVIEW-R1`
- Date: 2026-09-25, Asia/Shanghai
- Verifier: Codex independent verifier; not the R3 executor
- Executor branch: `codex/wp04-02-r7-proof-protocol-repair-r3`
- Executor baseline: `43df5fbf9e2b1a748ebd7ac22e8ba02c2832285b`
- Implementation commit: `af6d6909b0c10a3e703e3d601c85568b22c58014`
- Evidence commit / reviewed HEAD: `0cafd2828062c6b9fc583bfad428f0620e8aa67d`
- Report path: `docs/acceptance/TASK-WP04-02-R1C-05C-01-R7-EVIDENCE-SECURITY-PROOF-PROTOCOL-REPAIR-R3-FEEDBACK-INDEPENDENT-REVIEW-R1-acceptance.md`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, narrowly scoped `L4_RUNTIME_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, partial `L3_CONTRACT_VERIFIED`
- Missing Acceptance: end-to-end default-loader `L3_CONTRACT_VERIFIED`; successful read-only `L4_RUNTIME_VERIFIED`
- Evidence Matrix Type: Full
- Repair Required: YES

## Changed Files Snapshot

- Main-workspace baseline before this report: three pre-existing untracked files; tracked and index diffs empty.
- R3 implementation commit: exactly three authorized Python files.
- R3 evidence commit: the R3 execution report plus its new evidence directory.
- R3 worktree at verification: clean at `0cafd2828062c6b9fc583bfad428f0620e8aa67d`.
- Task attribution: CERTAIN for the two R3 commits; pre-existing main-workspace untracked files are not attributed to R3 and were not modified.

## Classification

- Task Type: `SECURITY + OPERATIONS_VERIFIER_TOOLING + REPAIR`
- Risk Type: credential handling, one-shot runtime proof, evidence integrity
- Touched Layers: verifier helper, verifier tests, evidence bundle
- Task Size: SMALL, high risk
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, G5 Regression, G6 Evidence
- DB Persistence Gate: NOT_APPLICABLE for this repair; the authorized runtime action was one fixed read-only identity query, not persistence verification.

## Independent Root-Cause Finding

The helper fixes `OPAQUE_LOADER_MODULE` to `tests.evidence_pg_fixture` and `OPAQUE_VALUE_ATTRIBUTE` to `DEFAULT_ADMIN_DATABASE_URL`. `_load_opaque_value()` imports that module and returns `getattr(..., None)`.

Static inspection confirms that `tests/evidence_pg_fixture.py` does not define `DEFAULT_ADMIN_DATABASE_URL`. The actual WP-04-02 service test module defines that constant and passes it to `disposable_sessionmaker`. A fresh non-network reproduction returned:

```text
DEFAULT_ADMIN_DATABASE_URL_present= False
loader_result_type= NoneType
loader_result_is_none= True
```

Therefore the default child path deterministically returns child code `42` before attempting a connection. This exactly explains the sealed live proof result:

```text
parent_return_code=1
child_return_code=42
stage=OPAQUE_VALUE_UNAVAILABLE_OR_INVALID
connection_count=0
query_count=0
schema_valid_result_count=0
```

This is not an external environment blocker: Docker/PostgreSQL preflight was healthy and accepting connections, while the code-selected module/attribute pair cannot produce a value.

The deterministic test suite did not catch the defect because its success and failure tests inject synthetic `loader=` callables into `child_main`; no test exercises `_load_opaque_value()` against the configured default module and attribute.

## Top Blocking AC Results

| Top AC | Result | Evidence |
|---|---|---|
| Credential-safe parent/child protocol preserves fixed failure classification and no raw credential channel | PASS | Source review; sealed failure JSON; fresh 157-test regression |
| Configured default opaque loader resolves the real WP-04-02 admin connection source without parent exposure | FAIL | Configured module lacks the configured attribute; fresh default-loader reproduction returns `None` |
| Exactly one authorized live proof returns a schema-valid `SUCCESS` record with 1/1/1 connection/query/result counters | FAIL | Sealed proof is `FAILURE`, code 42, with 0/0/0 counters |
| Evidence is sealed, parseable, manifest-complete and credential-scan clean | PASS | Fresh manifest rebuild: 21 files, missing/extra/mismatch all zero; executor bundle records zero findings |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Exact R3 baseline, two-commit chain, implementation/evidence commit identities and clean final worktree reproduced |
| G1 Scope | PASS | Implementation commit contains exactly the three declared Python files; evidence commit contains report/evidence only |
| G2 Contract | FAIL | Default loader cannot resolve its configured attribute; successful one-shot proof AC is unsatisfied |
| G3 Architecture | FAIL | Helper couples the production proof path to an attribute that does not exist in the selected module |
| G4 Test | FAIL | Commands pass, but tests omit the real default-loader path and therefore do not prove the blocking runtime behavior |
| G5 Regression | PASS | Fresh combined verifier regression: 157 collected, 157 passed |
| G6 Evidence | PASS for the failed outcome | Failure and bundle integrity are independently traceable; the evidence proves failure, not runtime success |

Any Blocking Gate failure makes `OVERALL = FAIL`.

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary / Negative Evidence | Verdict |
|---|---|---|---|---|---|
| TOP-AC-01 | Preserve credential-safe transport and deterministic failure records | `wp04_02_secure_pg_proof.py`; R3 proof audit | Fresh source review and 157/157 tests | No retry; no raw stdout/stderr; parent did not read the value | PASS |
| TOP-AC-02 | Real default loader must resolve a valid connection string inside the child | loader constants and `_load_opaque_value()` | Fresh AST/import reproduction returns `None` | Configured module has no configured attribute | FAIL |
| TOP-AC-03 | One live read-only proof must yield success with exact 1/1/1 counters | parent/child proof path | Sealed proof JSON returns code 42 and 0/0/0 | PostgreSQL preflight was healthy; failure occurred before connection | FAIL |
| TOP-AC-04 | Seal complete credential-safe evidence | R3 evidence commit and manifest | Fresh manifest rebuild matches all 21 eligible files | Root manifest excludes only itself | PASS |

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| `git status/branch/rev-parse/log/diff-tree` against the R3 worktree | clean; exact two-commit chain and file scopes reproduced | Baseline and scope |
| `pytest -p no:cacheprovider -q` for both verifier test modules | 157 passed in 2.04s | Fresh regression |
| `ruff check --no-cache` on the three implementation files | exit 0, all checks passed | Static quality |
| `ruff format --check --no-cache` on the three implementation files | exit 0, three files formatted | Formatting |
| `git diff --check 43df5fb..af6d690` | exit 0 | Patch integrity |
| AST check for `DEFAULT_ADMIN_DATABASE_URL` in `tests/evidence_pg_fixture.py` | absent | Root-cause confirmation |
| `_load_opaque_value()` non-network reproduction | returns `None` | Root-cause reproduction |
| Independent manifest bytes/SHA-256 rebuild | 21 files; missing 0; extra 0; mismatch 0 | Evidence integrity |

The PostgreSQL proof was not retried. The original one-shot budget remains consumed for R3.

## Blocking Findings

1. `G2 / TOP-AC-02`: the configured default loader points to a missing attribute and deterministically returns `None`.
2. `G3`: the runtime proof path contains a broken module/attribute dependency that the deterministic tests replace with injected fakes.
3. `G4 / TOP-AC-03`: all 157 tests pass but do not cover the default loader; the only live proof failed before connection and cannot establish runtime success.

## Non-Blocking Findings

- The R3 credential scanner expansion, historical-main checkout isolation, evidence manifest and no-retry discipline are supported by static and automated evidence.
- The first Ruff attempt during independent verification was unable to create a cache in the read-only isolated worktree. The required check was immediately rerun with `--no-cache` and passed; this is not a source finding.

## Final Decision Rationale

`FAIL`. The execution report's `BLOCKED_PROOF_PROTOCOL` label is not sustained as an external blocker. The proof failed because the implementation selected a module that lacks the requested attribute. The defect is deterministically reproducible without credentials or PostgreSQL, and the passing tests do not exercise that path. R8, the 41-scenario focused PostgreSQL suite, Git integration, 05C-02, R1D and WP-04-03 remain unauthorized.

## Next Action

Dispatch the minimum default-loader Repair Contract. It must start from R3 HEAD, change only the secure proof helper and its deterministic tests unless static investigation proves an additional file is indispensable, add a regression that exercises the real configured default loader without printing or retaining the value, rerun all offline gates, commit the implementation, and use a new output path plus a new one-shot read-only proof budget. A successful repair still requires separate independent re-verification before R8.
