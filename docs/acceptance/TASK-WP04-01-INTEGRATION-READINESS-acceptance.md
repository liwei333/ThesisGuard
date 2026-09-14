# TASK-WP04-01 Integration Readiness Acceptance Report

**OVERALL: FAIL**

## Metadata

- Task ID: `TASK-WP04-01-INTEGRATION-READINESS`
- Date: `2026-09-14`
- Verifier: Codex independent verifier using `ai-task-governor`
- Report Path: `docs/acceptance/TASK-WP04-01-INTEGRATION-READINESS-acceptance.md`
- Path Basis: ThesisGuard persists task governance under `docs/acceptance/`.
- Implementation Status: exact WP04-01 commit exists on an unmerged branch; both the reported `bd4b1d7 + 4201ae7` candidate and the current `c38c96f + 4201ae7` candidate are invalid because merge simulation conflicts.
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`
- Missing Acceptance: `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED` for a valid `main + WP04-01` candidate tree
- Repair Required: YES
- Repair ID: `TASK-WP04-01-INTEGRATION-READINESS-R1`

## Changed Files Snapshot

- Verification-start pre-existing dirty files:
  - `AGENTS.md`
  - `README.md`
  - `docs/ARCHITECTURE_REFERENCES.md`
  - `docs/ThesisGuard_V1_PRD.md`
  - `docs/ThesisGuard_V1_Technical_Architecture_Design.md`
  - `docs/PRODUCT_GOAL_REALIGNMENT_2026-09-14.md` (untracked)
- Concurrent external state change: during verification, commit `c38c96f` committed exactly those six accepted product documents and advanced both `main` and `origin/main`; the verifier did not create or push that commit.
- Current baseline: `main@c38c96f`, with the six product documents tracked and clean.
- Task-attributable changes: this Acceptance Report and its R1 Repair Contract only
- Attribution: CERTAIN

## Classification

- Task Type: `DB_PERSISTENCE`, `MIGRATION`, `INTEGRATION_READINESS_REVIEW`
- Risk Type: database integrity, immutable version history, idempotency, migration compatibility, regression
- Touched Layers under review: model registry, ORM models, repository, migration, persistence tests
- Task Size: `MEDIUM`
- Evidence Matrix Type: Full
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G4 Test, DB Persistence, G5 Regression, G6 Evidence
- Not Applicable Gates: G3 Architecture as a separate gate; architecture boundary is covered by Scope and Contract for this persistence-only review

## Top Blocking AC Results

| Top AC | Result | Evidence |
|---|---|---|
| TOP-AC-01 — exact feature commit and target baselines are resolved | PASS | Source review used `main@bd4b1d7`; current main advanced externally to docs-only `c38c96f`. Feature remains `4201ae7`; merge base remains `a36c707`; current ahead/behind is `3 1`. |
| TOP-AC-02 — feature scope is only the six-file WP04-01 persistence slice | PASS | `git diff-tree --no-commit-id --name-status -r 4201ae7` reports one registry modification and five persistence/migration/test additions. |
| TOP-AC-03 — a conflict-free current-main candidate tree exists | FAIL | Independent merge-tree checks for both `a36c707 / bd4b1d7 / 4201ae7` and current `a36c707 / c38c96f / 4201ae7` emit conflict markers for `backend/common/db/models_registry.py`. |
| TOP-AC-04 — candidate PostgreSQL contract and migration tests pass | FAIL | No valid candidate tree exists. Running feature-only or conflict-marked tests cannot prove integration readiness. |
| TOP-AC-05 — source review preserved the user checkout and this verification introduces governance artifacts only | PASS | The source report's pre/post snapshots match. This verifier performed no code or Git mutation; only the required Acceptance Report and Repair Contract were added. The subsequent docs-only `c38c96f` commit is recorded as an external state change. |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Exact source-review baseline, current baseline, concurrent docs-only commit, refs, merge base, divergence, source report, frozen contract, and historical acceptance chain were inspected. |
| G1 Scope | PASS | Exact commit delta is limited to `models_registry.py`, Evidence models/repositories, revision 004, and two Evidence test files. |
| G2 Contract | FAIL | The dispatched readiness contract requires a valid conflict-free candidate before integration can be accepted; the candidate conflicts. |
| G4 Test | FAIL | Required candidate-tree verification cannot be run against a syntactically valid tree until TOP-AC-03 is repaired. This is a task defect, not an unavailable external environment. |
| DB Persistence | FAIL | `L4_DB_VERIFIED` is absent for the required integrated candidate. Historical feature-branch L4 results remain historical claims. |
| G5 Regression | FAIL | Candidate Research/full/OpenAPI comparison is not established because the integrated candidate does not exist. |
| G6 Evidence | PASS | Git-object and three-way merge evidence independently proves the Blocking failure; executor narrative was used only as a lead. |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary/Negative Evidence | Verdict |
|---|---|---|---|---|---|
| AC-01 [BLOCKING] | Resolve exact source-review baseline, current baseline, and reviewed commit | Git refs `bd4b1d7`, current docs-only `c38c96f`, and feature `4201ae7` | Current `rev-parse`, `merge-base`, and ahead/behind return `c38c96f`, `a36c707`, and `3 1`; commit `c38c96f` changes only the six accepted product docs | No feature-ref drift; baseline drift is explicit, not ignored | PASS |
| AC-02 [BLOCKING] | The feature commit remains persistence-only | Six-file commit patch | `git show --stat` reports 3,633 insertions, 3 deletions across exactly six files | No API, service, OpenAPI, frontend, worker, Agent, Macro, or Risk OS file appears | PASS |
| AC-03 [BLOCKING] | Candidate integration is conflict-free | Current main inherits the registry change from `bd4b1d7`; feature modifies the same file from `a36c707` | Independent merge-tree checks against both reported and current main emit a three-way conflict at the registry tail | Current main contains Chinese registry documentation and future-model comments; feature inserts Evidence imports and removes the old tail comments | FAIL |
| AC-04 [BLOCKING] | Candidate passes real PostgreSQL persistence verification | Feature contains models, migration, repositories, and tests | No valid candidate tree is available for fresh candidate DB execution | Historical R2 report records 18 focused and 85 full passes, but this cannot substitute for candidate evidence | FAIL |
| AC-05 [BLOCKING] | Candidate preserves existing Research and known baseline behavior | Current main contains WP-03 and a known OpenAPI artifact drift | Candidate regression comparison cannot be completed before conflict repair | Known OpenAPI drift must not be fixed or misattributed in this Repair | FAIL |
| AC-06 [BLOCKING] | No task-attributable code or Git mutation occurs | Current main is `c38c96f`; governance convention requires persisted acceptance artifacts | Verification used read-only Git-object commands; only two new files under `docs/acceptance/` were created | No checkout, merge, reset, stash, clean, rebase, commit, push, or PR was performed by this verifier | PASS |

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| `git status --short --untracked-files=all` | initially six pre-existing product-document changes; after external `c38c96f`, only the two new governance artifacts | Lock and re-lock baseline |
| `git branch --show-current` | `main` | Confirm checkout branch |
| `git rev-parse HEAD` and `git rev-parse main` | initially `bd4b1d7`; after external state change both `c38c96f6c6b61cd2d45f3d5af9be736d0db0f00` | Resolve source and current baselines |
| `git rev-parse codex/wp04-evidence-persistence` | `4201ae754c0cf71188965987964d2221795cb5eb` | Resolve reviewed feature |
| `git merge-base main 4201ae7` | `a36c707898452340c35bdcfbceaf7d38bb3b4fa1` | Resolve three-way base |
| `git rev-list --left-right --count main...4201ae7` | initially `2 1`; current `3 1` | Confirm and refresh divergence |
| `git show --format=fuller --stat 4201ae7` | six files, 3,633 insertions, 3 deletions | Audit exact feature scope |
| `git diff-tree --no-commit-id --name-status -r 4201ae7` | one modified and five added files | Audit changed-file allowlist |
| `git show <base/main/feature>:backend/common/db/models_registry.py` | confirms both sides changed the registry differently | Identify conflict cause |
| `git merge-tree a36c707 bd4b1d7 4201ae7` | emits conflict markers in `models_registry.py` | Reproduce the source feedback's Blocking conflict |
| `git diff-tree --no-commit-id --name-status -r c38c96f` | only the six accepted product documents | Classify concurrent baseline change |
| `git merge-tree a36c707 c38c96f 4201ae7` | emits the same registry conflict markers | Prove the Blocking conflict persists on current main |

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| An ancestry diff falsely represents removed main-only docs as feature scope | Yes | Exact single-commit diff, not `main..feature`, yields six files | PASS |
| Conflict resolution could delete main's registry explanation/comments | Yes | Main and feature blobs differ in the same tail region | REPAIR MUST PRESERVE |
| Conflict markers or unmerged index could be treated as a candidate tree | Yes | Three-way merge output contains explicit markers | FAIL |
| Historical feature-branch L4 tests could be reused as candidate L4 evidence | Yes | R2 acceptance predates the current divergent main candidate | REJECTED AS CURRENT EVIDENCE |
| Known OpenAPI drift could be blamed on WP04-01 or silently fixed | Yes | Exact feature patch has no API/OpenAPI/frontend file | REPAIR MUST BASELINE-COMPARE |

## DB Persistence Result

- Schema constraints: static implementation exists on the feature commit; integrated-candidate verification missing
- Read semantics: historical feature tests exist; integrated-candidate verification missing
- Replace/current/history semantics: historical feature tests exist; integrated-candidate verification missing
- Transaction boundary: outside the registry conflict repair; must not be redesigned
- Version/snapshot/history: frozen WP-04 contract remains authoritative
- Real persistence vs mock: original acceptance requires real PostgreSQL; no SQLite/mock substitute is allowed

## Blocking Findings

### B-01 — Model registry three-way conflict

- Failed AC/Gate: TOP-AC-03, G2 Contract
- Root evidence: merge-tree reports the same conflict for both the source-review baseline `bd4b1d7` and current baseline `c38c96f` against `4201ae7`.
- Cause: current main adds registry documentation and future-model comments while the feature commit inserts Evidence imports from the older base and removes/replaces the older tail comment block.
- Impact: no valid candidate tree exists, so candidate L3/L4 verification cannot begin.
- Minimum repair: create an isolated candidate based on exact main, apply the exact WP04-01 patch, resolve only the registry conflict by preserving main documentation/comments and adding Evidence model imports, then run the original candidate verification.

### B-02 — Required candidate L4 evidence is absent

- Failed AC/Gate: TOP-AC-04, G4 Test, DB Persistence, G5 Regression
- Root evidence: the candidate does not exist beyond a conflict state.
- Impact: feature-only historical tests cannot prove that `main + WP04-01` is safe.
- Minimum repair: after B-01, run fresh real-PostgreSQL Evidence migration/persistence tests plus Research/full/OpenAPI baseline comparison in the isolated candidate.

## Non-Blocking Findings

- The executor's isolated temp clone was left in conflict state after `git cherry-pick --abort` reported no sequencer operation. It did not alter the user checkout, but temporary-workspace cleanup should use the state-appropriate command and validate the exact temp path.
- The existing main OpenAPI artifact drift remains out of scope. It is non-blocking only if the repaired candidate produces the same failure set and no new drift.

## Regression Result

- Result: FAIL / not established for the candidate
- Preserved behavior proven: feature commit scope does not directly edit API/OpenAPI/frontend files
- Regression gaps: candidate Evidence tests, Research tests, full backend suite, and OpenAPI baseline comparison

## Repair Required

- YES
- Repair ID: `TASK-WP04-01-INTEGRATION-READINESS-R1`
- Failed AC/Gate: TOP-AC-03, TOP-AC-04, G2, G4, DB Persistence, G5

## Final Decision Rationale

`FAIL`. The execution feedback's verdict is accepted because its decisive claim was independently reproduced from immutable Git objects. The external docs-only advance from `bd4b1d7` to `c38c96f` does not touch the registry and does not remove the conflict: exact feature commit `4201ae7` still produces a three-way text conflict against current main. A blocking contract failure cannot be converted to PASS by historical feature-branch tests. This is not `BLOCKED` because the failure is known and repairable; it is not caused by unavailable credentials or infrastructure.

## Next Action

Execute `TASK-WP04-01-INTEGRATION-READINESS-R1` only. Do not begin WP04-02 or perform main integration until the Repair receives a new independent acceptance with the original required acceptance tags.
