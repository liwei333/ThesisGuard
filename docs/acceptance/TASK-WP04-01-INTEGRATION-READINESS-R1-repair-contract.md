# TASK-WP04-01 Integration Readiness R1 Repair Contract

## A. Execution Core

- Task ID: `TASK-WP04-01-INTEGRATION-READINESS-R1`
- Original Task: `TASK-WP04-01-INTEGRATION-READINESS`
- Objective: create a conflict-free, uncommitted WP04-01 integration candidate based on exact current `main@c38c96f`, resolving only the `models_registry.py` conflict, and produce fresh candidate verification evidence.
- Why Now: integration readiness is `FAIL`; Governor invariants require Repair and re-verification before Git integration or WP04-02.
- Task Type: `REPAIR`, `DB_PERSISTENCE`, `MIGRATION`
- Task Size: `MEDIUM`
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Evidence Matrix Type: Full
- Source Acceptance Report: `docs/acceptance/TASK-WP04-01-INTEGRATION-READINESS-acceptance.md`

## Top Blocking AC

- TOP-AC-R1-01 [BLOCKING]: an isolated candidate based on exact `main@c38c96f` contains the WP04-01 six-file delta with no unmerged index entries, conflict markers, or whitespace errors.
- TOP-AC-R1-02 [BLOCKING]: `backend/common/db/models_registry.py` preserves current main's full module documentation and future-model comments while adding the exact required Evidence model imports; no other production file differs from the accepted feature implementation.
- TOP-AC-R1-03 [BLOCKING]: the candidate passes the focused Evidence migration and persistence suite against real PostgreSQL with zero skips, including revision `3 -> 4 -> 3 -> 4`, migrated constraints, initial-version state, duplicate identities, and current/tombstone semantics.
- TOP-AC-R1-04 [BLOCKING]: Research regression and project static checks remain green; full-suite/OpenAPI comparison introduces no failure beyond the exact known baseline OpenAPI artifact drift.
- TOP-AC-R1-05 [BLOCKING]: the user's current `main@c38c96f` checkout remains untouched apart from the already-present untracked governance reports created by the verifier.

## Scope

In Scope:

- Create one new isolated repair worktree/branch from exact `main@c38c96f` using the repository's existing worktree convention.
- Apply exact commit `4201ae754c0cf71188965987964d2221795cb5eb` without committing.
- Resolve only `backend/common/db/models_registry.py`.
- Leave a conflict-free, uncommitted six-file candidate for independent verification.
- Run candidate static, contract, PostgreSQL, migration, and regression checks.

Allowed candidate files:

- `backend/common/db/models_registry.py`
- `backend/evidence/models.py`
- `backend/evidence/repositories.py`
- `migrations/versions/20260914_004_evidence_persistence.py`
- `tests/test_evidence_migrations.py`
- `tests/test_evidence_persistence.py`

Out of Scope:

- WP04-02 service, WP04-03 API/OpenAPI, WP04-04 typed links
- Worker, MinIO, embedding, pgvector/RAG
- Thesis, Market, Portfolio, Trade Plan, Discipline, Agent, Macro, Risk OS
- Product/architecture document changes
- WP-04 contract or historical acceptance changes
- Existing OpenAPI drift repair
- Dependency, toolchain, configuration, API, OpenAPI, or generated-client changes
- Commit, merge into main, push, PR, rebase/force-push of the accepted feature branch

## Root Evidence

- Failing commands:
  - source-review baseline: `git merge-tree a36c707898452340c35bdcfbceaf7d38bb3b4fa1 bd4b1d7b059e9123d1466938096d0a2161ac2b44 4201ae754c0cf71188965987964d2221795cb5eb`
  - current baseline: `git merge-tree a36c707898452340c35bdcfbceaf7d38bb3b4fa1 c38c96fe6c6b61cd2d45f3d5af9be736d0db0f00 4201ae754c0cf71188965987964d2221795cb5eb`
- Failing evidence: conflict markers in `backend/common/db/models_registry.py`
- Relevant Git objects:
  - base: `a36c707898452340c35bdcfbceaf7d38bb3b4fa1`
  - source-review main: `bd4b1d7b059e9123d1466938096d0a2161ac2b44`
  - current main: `c38c96fe6c6b61cd2d45f3d5af9be736d0db0f00`
  - feature: `4201ae754c0cf71188965987964d2221795cb5eb`
- Missing evidence: a valid candidate tree plus fresh L2/L3/L4 candidate results

## Must Fix

1. Inspect `AGENTS.md`, the source Acceptance Report, this Repair Contract, the WP-04 frozen contract, current Git status, refs, worktrees, and exact three-way registry blobs before editing.
2. Create a new isolated repair worktree/branch from exact main. Do not reuse or mutate the user's current checkout and do not rewrite `codex/wp04-evidence-persistence`.
3. Apply `4201ae7` without creating a commit. If it conflicts only in the expected registry file, resolve that file and stage the resolved candidate; do not run a commit-producing continuation command.
4. Preserve the current main registry docstring and explanatory/future-model comment block.
5. Add the exact Evidence model registration imports required by the accepted feature implementation.
6. Keep the other five feature files byte-identical to their `4201ae7` blobs. If byte identity is impossible, stop and report `BLOCKED`; do not redesign them in this Repair.
7. Prove there are no unmerged index entries, conflict markers, extra files, test weakening, or out-of-scope changes.
8. Run the required verification from the isolated candidate.
9. Leave the isolated candidate available for a separate verifier; do not commit or integrate it.

## Must Not

- Do not change this Repair Contract, its AC, required verification, evidence requirements, or stop conditions.
- Do not weaken, delete, skip, rename, or rewrite tests to manufacture a pass.
- Do not edit any candidate file outside the six-file allowlist.
- Do not edit the five non-registry feature files; they must remain byte-identical to `4201ae7`.
- Do not refactor unrelated code, upgrade dependencies, change configuration, or introduce mocks, TODOs, placeholders, hardcoded data, or test-only behavior.
- Do not modify the user's current main checkout or its accepted product-document changes.
- Do not commit, merge into main, push, create a PR, or rewrite the accepted feature branch.

## Preserve

- Already PASS: exact commit identity, six-file feature scope, no API/OpenAPI/frontend/service/worker expansion, user-checkout integrity
- Main behavior: full `models_registry.py` documentation/comments inherited by current `c38c96f` from `bd4b1d7`
- Feature behavior: all accepted WP04-01 models, repositories, migration, constraints, and tests from `4201ae7`
- Public contracts: frozen `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`
- Historical records: all existing WP04 acceptance and repair reports
- Known baseline: current OpenAPI artifact drift remains separately reported and must not be fixed here
- Test strength: real PostgreSQL, zero skip for focused Evidence tests; no SQLite/mock substitute

## Required Verification

Resolve exact repo commands from the Makefile, pyproject, and the R2 acceptance report. At minimum execute and report:

```bash
git status --short --untracked-files=all
git rev-parse HEAD
git ls-files -u
git diff --check
git diff --name-status HEAD
git diff -- backend/common/db/models_registry.py
git diff -- backend/evidence migrations/versions/20260914_004_evidence_persistence.py tests/test_evidence_migrations.py tests/test_evidence_persistence.py
pytest -q tests/test_evidence_migrations.py tests/test_evidence_persistence.py
pytest -q tests/test_research_api.py tests/test_research_persistence.py
PYTHONDONTWRITEBYTECODE=1 pytest -p no:cacheprovider tests/test_frontend_openapi_client.py -q -rs
```

Also run the relevant Ruff, mypy/typecheck, compile/import, Alembic-head, and full backend test commands recorded by the repository and R2 acceptance. Compare the full-suite and OpenAPI failure set with exact current-main baseline evidence. A known baseline failure is non-repair scope only when the candidate introduces no additional failure.

For the five non-registry feature files, compare their blob hashes or byte content against `4201ae7` and report the result.

## High-Risk Counterexamples

1. The repair adds Evidence imports but silently drops main's Chinese registry documentation or future-model comment block.
2. Conflict markers disappear from the working file but unmerged index stages remain in `git ls-files -u`.
3. The executor changes Evidence models, migration, repositories, or tests to make candidate tests pass instead of resolving only the registry conflict.
4. Focused Evidence tests pass through SQLite, mocks, skips, or unavailable-DB fallback rather than real PostgreSQL.
5. The known baseline OpenAPI drift is either incorrectly blamed on WP04-01, silently repaired, or used to hide a new candidate regression.

## Stop Conditions

Stop and report `BLOCKED` if:

- the user checkout, `main@c38c96f`, exact feature commit, or accepted product-document baseline changes during execution;
- the conflict is not limited to `backend/common/db/models_registry.py`;
- resolving the candidate requires changing any non-registry feature file;
- an allowed feature file cannot remain byte-identical to `4201ae7`;
- a contract, migration, model, or test defect beyond the merge conflict is discovered;
- real PostgreSQL or other required verification infrastructure remains unavailable after the permitted access path is exhausted;
- completing the task requires a commit, merge, push, PR, dependency change, OpenAPI regeneration, or scope expansion.

## Expected Evidence

- Candidate worktree path and branch name
- `BASELINE_CHANGED_FILES` and `FINAL_CHANGED_FILES` for both the user checkout and isolated candidate
- Before/after hashes for the user checkout's six accepted product-document changes
- Exact candidate six-file list
- Registry three-way resolution explanation and diff
- `git ls-files -u` empty result
- Conflict-marker search result
- Five non-registry file hash comparisons with `4201ae7`
- Top Blocking AC to file/command/result mapping
- Exact test/static/migration commands, exit codes, pass/fail/skip/warning counts
- Baseline versus candidate OpenAPI/full-suite failure comparison
- Required Acceptance achieved and missing

## B. Governance Appendix

- Core invariants: `IMPLEMENTED != PASS`, `No Evidence, No PASS`, `Executor Cannot Self-Approve`, `FAIL -> Repair First`, `Repair Must Not Break Passed AC`.
- Anti-drift: do not change this contract, AC, required verification, test strength, frozen contract, or allowed scope.
- DB evidence: real PostgreSQL is required for `L4_DB_VERIFIED`.
- Independent re-verification is required after executor completion.

## Executor Final Response

Status may only be:

- `IMPLEMENTATION_COMPLETE`
- `BLOCKED`

The executor must not output `PASS`, `DONE`, `VERIFIED`, `完成验收`, or `已通过`. A separate verifier must re-run the full acceptance workflow.
