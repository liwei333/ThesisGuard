# TASK-WP04-02-R1B-R1 Acceptance

**OVERALL: FAIL**

## Metadata

- Task ID: `TASK-WP04-02-R1B-R1`.
- Date: 2026-09-15 (Asia/Shanghai).
- Verifier: Codex, independent source inspection and real-PostgreSQL probes.
- Report path: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1B-R1-acceptance.md`, following AGENTS.md and the existing project acceptance convention.
- Implementation status supplied by executor: `IMPLEMENTATION_COMPLETE`; used as a lead, not acceptance evidence.
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Achieved acceptance: L1, L2; positive/negative focused contract and real DB evidence exists, but complete L3/L4_DB acceptance is not achieved.
- Missing acceptance: complete production-wired exact-target validation and full repair/regression acceptance.
- Repair required: YES, `TASK-WP04-02-R1B-R2`.

## Baseline / Scope / Attribution

Candidate worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`.

Branch: `codex/wp04-02-evidence-domain-service`; HEAD remains `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`, parent `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`.

HEAD adds exactly errors.py, services.py and test_evidence_services.py; its three accepted R1A-R2 blob SHA-256 values remain unchanged. Current candidate SHA-256 matches the supplied feedback:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
2659bc4d06bd60c242a389365e96e60e4cc9bef0f31d5d924ef43e1e23da8331  backend/evidence/services.py
16784fc35abb8db4a41f7ed90307f3710edf52df98594a39b3cf707371e83681  tests/test_evidence_services.py
```

`BASELINE_CHANGED_FILES` / `FINAL_CHANGED_FILES` for this verification both contain only tracked modifications to services.py and test_evidence_services.py. errors.py is byte-identical. No candidate edits were made by this verifier.

Main remains `main@7d4e395d949d8cd050548347f31dd6b492f65834`. Six pre-existing untracked governance records were preserved. This verification creates a new acceptance report and R2 repair contract only; no business code/Git mutation.

Attribution: certain for the current full candidate versus accepted HEAD and for verifier non-mutation. A separate pre-R1 repair file snapshot was not retained by this verifier, so not every line in the cumulative diff is attributed exclusively to R1.

## Classification

- Task type: REPAIR / deterministic Evidence service.
- Task size: SMALL; one exact-version derivation boundary, two files.
- Risk: immutable history, DB integrity and pre-write graph validation.
- Touched layers: service and tests.
- Evidence matrix: Full.
- Selected gates: G0 baseline, G1 scope, G2 contract, G3 architecture/production wiring, G4 focused test, DB persistence, G5 regression and G6 evidence.
- UI/API/OpenAPI, schema/migration changes, providers, security/tenant changes: NOT_APPLICABLE.

## Top Blocking AC / Full Evidence Matrix

| AC | Requirement | Implementation evidence | Fresh verification | Boundary / negative evidence | Verdict |
|---|---|---|---|---|---|
| TOP-AC-01 | Exact graph defense wired into actual create/replacement/append writes | services.py:644 and :1551 omit exact target; :2357 gates all self/cycle checks on a non-null target | Three public-command PostgreSQL wiring probes fail | Targets are `[None]`, `[None]`, `[None, None]`; traversal targets always `[]` | FAIL |
| TOP-AC-02 | Legal historical exact support replacements, immutable snapshots/audit | tests:1226 and :1318 correct earlier series-based negative expectations; replacement routing remains active | Existing R1B verifier and focused source tests are in the fresh 21-test successful run | Both legal direct/prior multi-hop replacement cases pass; source review confirms first case complete correction tuple | PASS |
| TOP-AC-03 | True exact self/return-path defense through production helper | services.py:2324/:2376 implement exact ID traversal; tests:1345 call helper with exact target | New focused helper test passes in the 21-test run | Helper algorithm is valid, but only test callers supply a target; this evidence does not satisfy TOP-AC-01 | PASS (helper behavior only) |
| TOP-AC-04 | Preserve R1A/non-defective R1B behavior and complete regressions | Source-backed rules and non-defective R1B tests inspected | R1A 12 nodes + R1B verifier 4 nodes + R1B focused 5 nodes pass together | Full 96-service and 35-regression claims were not independently repeated after a blocking failure; no fresh full-regression acceptance claimed | Partial evidence; full assessment short-circuited |
| TOP-AC-05 | Scope and complete verification evidence, no weakening | Candidate hashes/status, contracts unchanged; exact target exists only in helper tests | Baseline/scope/static checks succeed | Complete required matrix is not green: verifier-owned wiring fails; full lower-value tests not rerun after FAIL | FAIL |

## Gate Results

- G0 Baseline: PASS; accepted HEAD/parent/file delta/base blobs/current hashes match.
- G1 Scope: PASS; two-file candidate modifications, unchanged errors.py, no candidate edits during verification.
- G2 Contract: FAIL; binding execution-contract TOP-AC-01 requires production exact-target defense, not helper-only capability.
- G3 Architecture: FAIL; optional exact-target argument makes production self/cycle traversal unreachable at all call sites.
- G4 Test: FAIL; original focused checks green, but all three independent public-write wiring probes fail.
- DB persistence: real isolated PostgreSQL exercised successfully; required pre-write graph defense is absent. This is a contract/wiring FAIL, not DB unavailability. No public true-cycle insertion was demonstrated.
- G5 Regression: focused R1A/R1B evidence green; complete suite assessment intentionally stopped after blocking failure, not promoted to PASS.
- G6 Evidence: sufficient independent evidence for FAIL; executor full-suite claims remain separately labeled historical/self-report.

## Commands Actually Executed

From candidate worktree:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service \
pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py /tmp/test_wp04_02_r1a_verifier.py tests/test_evidence_services.py -k 'r1b or verifier' -rs
```

Exit 0: `21 passed, 91 deselected, 2 warnings in 19.42s` (4 existing R1B verifier nodes, 12 R1A verifier nodes and 5 candidate R1B nodes). Warnings concern existing Starlette/httpx and anyio deprecations; no dependency changes made.

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service \
pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_r1_wiring_20260915.py -rs
```

Exit 1: `3 failed in 4.59s`. Verifier artifact SHA-256: `909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786`.

The new verifier-owned artifact parameterizes `test_public_derived_write_validates_its_new_exact_target` with create, same_series_revision, replacement. Observer wrappers forward all arguments to the unmodified real validator and reachability helper; they neither stub results nor replace DB behavior. Disposable migrated PostgreSQL fixtures execute genuine service writes. This is instrumentation for the explicit production-wiring contract, not evidence that a true cycle can be expressed through the current public API.

Also executed:

- Git status/HEAD/parent/name-only commit delta and SHA-256 checks; source/contract/verifier reads.
- `ruff check --no-cache` on the three files: All checks passed.
- `ruff format --check --no-cache`: three files already formatted.
- `MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1b-r1-acceptance-mypy` on the three files: success, no issues. Advisory note for unused existing mypy configuration sections.
- `PYTHONPYCACHEPREFIX=/tmp/tg-r1b-r1-acceptance-pycache python -m compileall -q` on the three files: independently repeated, exit 0, no error output.
- `alembic -c migrations/alembic.ini heads`: `000000000004 (head)`.
- `git diff --check`: no errors.

Full service suite and 35-case regression suite were not independently rerun in this turn after a proven blocking AC failure, following the governor's early-FAIL rule. Their executor-reported green results cannot override the observed contract failure.

## Blocking Finding BF-01: Helper-Only Exact Graph Defense

Severity: Important / P1, blocking this repair's acceptance.

`_validate_derivation_links` performs self-link and exact-target graph checks only inside `if proposed_derived_evidence_version_id is not None` (services.py:2357). Its two production call sites, create (:644) and revision child resolution (:1551), never pass that argument. `_append_status_or_revision` constructs/flushes a new version without a target-aware validation call. Replacement delegates to create and likewise receives no target.

Fresh observed values:

| Public write | Validator exact targets | Reachability targets |
|---|---|---|
| create | `[None]` | `[]` |
| same-series revision | `[None]` | `[]` |
| replacement | `[None, None]` | `[]` |

The repair removed the overbroad series prohibition correctly, and the exact reachability algorithm itself is present. However, production still checks only role, existence, duplicates and provenance; the target-aware defense is used only by directly invoking the helper in tests.

The current public API does not expose a future version ID, and append-only exact graphs structurally limit ordinary cycle construction. This observation is acknowledged and is not the failure. The binding R1 execution contract already allowed helper tests for unrepresentable negative inputs while separately requiring production validation wiring. That second requirement remains unmet.

Minimal repair: assign the actual new immutable EvidenceVersion ID in the service before persistence and invoke exact-target validation for new DERIVED writes in the existing transaction. Do not change the public API, frozen contract, models/repositories/schema, prior-version links or R1C/R1D behavior. Add production-path wiring/timing evidence while preserving all now-green legal historical-support cases.

## Final Decision / Next Action

Independent code-review sidecar, dispatched under `requesting-code-review` with requirements and candidate paths only (no session-history fork), independently confirms one Important blocking issue: production callers omit the exact target and the common append path does not invoke target-aware validation. Reviewer `/root/r1b_r1_wiring_review` also confirms helper correctness, legal DAG test expectations, matching candidate hashes and the structural public-cycle limitation. The recommendation is FAIL / NOT_ACCEPTED for TOP-AC-01; no claim of currently reachable public-cycle corruption is made. Review was read-only and did not expand into R1C/R1D.

`FAIL — REPAIR_REQUIRED`. Baseline is accepted, legal historical-support semantics improved, but TOP-AC-01 fails. R1B-R1 and R1B remain open; R1C cannot start. Original WP04-02 remains unaccepted.

Next dispatch: `TASK-WP04-02-R1B-R2-repair-contract.md` in this directory. No commit, merge, rebase, reset, checkout, push or main/candidate business change was performed by this verifier. Existing reports/contracts/verifier artifacts are preserved.
