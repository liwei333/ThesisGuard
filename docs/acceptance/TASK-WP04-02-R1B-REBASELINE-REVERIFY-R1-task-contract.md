# TASK-WP04-02-R1B-REBASELINE-REVERIFY-R1 — Proposed Contract

**Status: PENDING_USER_AUTHORIZATION — NOT_DISPATCHED**

This file records a proposed next verification task. Its existence does not authorize changing the effective R1B baseline. Explicit user approval or user dispatch of the complete authorization-bearing prompt is required.

## A. Execution Core

- Task ID: `TASK-WP04-02-R1B-REBASELINE-REVERIFY-R1`
- Role: `VERIFIER`, not implementation executor.
- Objective: after explicit approval, substitute only the content-equivalent candidate baseline/commit-state facts and independently verify all unchanged R1B semantic AC.
- Why Now: R1B acceptance is BLOCKED by the old exact-HEAD constraint; f7c50ab base blobs match accepted R1A-R2.
- Type: baseline reconciliation and independent domain-service/DB verification.
- Size: `MEDIUM` — one R1B acceptance boundary; no implementation.
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Evidence Matrix: `Full`.

## Exact Proposed Authorization

Accept `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af` as the replacement R1B Git baseline only if its parent remains `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`, its delta is exactly three files, and its blobs match the R1A-R2 acceptance hashes.

The effective candidate state becomes two tracked modifications instead of three untracked files. This substitution does not authorize any business-contract/AC change, new commit, merge, reset, rebase, checkout, push, main mutation or retrospective attribution of previous Git actions.

Candidate worktree/branch remains:

`/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`

`codex/wp04-02-evidence-domain-service`

Candidate snapshot to verify:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
f1c4a9b85505cb152273a246525a4b3214eaaff0847c328f1d2ed2b350fadf0c  backend/evidence/services.py
454f95d269b7521764409b952ba26055c473d62c93c75313b16fa2e4fa66a0ce  tests/test_evidence_services.py
```

## Top Blocking AC

1. Exact authorization exists; old/new parent, file delta, base blobs and current candidate hashes are independently checked without Git mutation.
2. Every original R1B semantic Top Blocking AC is independently reviewed and verified without changing its business meaning.
3. Real PostgreSQL tests prove canonical identities, no-support/missing-support/duplicate/cycle rejection, same-series versus replacement routing, immutable child snapshots, nullable clear, extractor provenance and no-residue behavior.
4. Full service suite (currently 95 tests), original R1A 12-case verifier if available, 35-case regression and all static/type/build/migration checks pass. No weaker test standard is accepted.
5. Candidate/main code/history remains unchanged during verification; formal report is persisted and unresolved failures result in Repair before R1C.

## Scope / Must

- Read current AGENTS.md, frozen WP04 contract, original WP04-02 acceptance, R1 repair program, R1A-R2 acceptance, original R1B contract and baseline-limited R1B acceptance from the main worktree.
- Preserve historical reports/contracts. Record the authorization and exact replaced baseline clauses in a new report; do not rewrite history as if the original contract had always used f7c50ab.
- Only the exact HEAD and tracked/untracked baseline clauses are superseded. All original R1B semantic AC, scope, architecture, negative tests and deferrals remain binding.
- Use requesting-code-review and verification-before-completion for fresh independent review; the reviewer must not rely on executor conclusions.
- The verifier may add independent temporary tests under a newly allocated `/tmp` path. It must not modify candidate files, original tests, existing verifier artifacts or frozen requirements to manufacture PASS.
- Reproduce the executor's four selected, complete 95-case service and 35-case regression claims, but also independently test counterexamples. Test count alone is not sufficient.

## High-Risk Counterexamples

- Caller-controlled origin/scope keys or order/duplicate inputs change durable lineage.
- Support/member-ID set changes append inside the old series; metadata-only changes wrongly create replacement.
- N+1 status/tombstone loses derivation/instrument/locator children or mutates old rows.
- Explicit None is treated as omitted; invalid non-nullable clear is accepted.
- Cycle defense silently promotes exact-version graph rules to series-level rules; report any frozen-contract inconsistency rather than silently expanding semantics.
- Extractor-provenance and failure-after-validation paths leave partial rows.

## Required Verification

Run from candidate worktree with real PostgreSQL and proper sandbox approval:

```bash
git status --short --branch --untracked-files=all
git rev-parse HEAD
git diff --name-status
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py

pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1b -rs
pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs

ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1b-reverify-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1b-reverify-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
git diff --check
```

If `/tmp/test_wp04_02_r1a_verifier.py` exists, run with explicit candidate PYTHONPATH without editing it. If missing, reconstruct its relevant independent contract coverage in a fresh verifier-owned artifact and record provenance; do not treat a missing temporary file as evidence that behavior passes.

## Must Not / Stop Conditions

- No business-code/test edit, commit/merge/rebase/reset/checkout/pull/push, main mutation, branch/worktree creation or implementation of R1C/R1D/API.
- Persist only a new acceptance/re-verification report in main-worktree `docs/acceptance/` and, on FAIL, a proposed minimal Repair Contract. Do not commit them.
- Stop with BLOCKED if explicit baseline approval is absent, baseline/snapshot changes again, required evidence/environment is unavailable, or frozen semantic contradictions require a new dispatcher decision.
- On proven Blocking AC failure, return FAIL and create a minimal repair; do not proceed to R1C.

## Expected Evidence / Final Response

- Exact user authorization, baseline/content equivalence matrix, before/after candidate and main snapshots.
- Original five Top AC mapped to code locations, independent test nodes and positive/negative DB evidence.
- Fresh complete command results, row counts, child snapshot comparison, stable error details, achieved/missing acceptance and persisted report path.
- Verifier final verdict: exactly `PASS`, `FAIL` or `BLOCKED`.
- PASS closes R1B only and selects R1C; FAIL repairs R1B first; BLOCKED records owner/input/unblock criteria.

## B. Governance Appendix

No Evidence, No PASS; executor cannot self-approve; full suite green cannot override a Blocking AC; scope and semantic standards cannot be weakened. This proposal is not an approval of earlier commit/push actions and does not change original WP04-02's FAIL status.
