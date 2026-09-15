# TASK-WP04-02-R1 Repair Program

## Status

`TASK_TOO_LARGE -> SPLIT_REQUIRED`

## Source

- Original task: `TASK-WP04-02 Evidence Domain Service`
- Source acceptance: `docs/acceptance/TASK-WP04-02-acceptance.md`
- Overall verdict: `FAIL — REPAIR_REQUIRED`
- Candidate branch: `codex/wp04-02-evidence-domain-service`
- Candidate baseline/HEAD: `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`
- Required final acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`, `L5_REGRESSION_VERIFIED`
- Evidence matrix type: `Full`

## Why Split

The failed implementation contains independently verifiable defects in four coupled but separable areas: source/version/locator rules; Evidence provenance-derived identity and immutable children; lifecycle/eligibility/trusted verification; and idempotency/transaction/final regression. Reissuing all findings as one large prompt would repeat the oversized dispatch that produced eight green tests while leaving most of the frozen contract unimplemented.

The repair is therefore an ordered program. Passing a leaf closes only that leaf; it does not change the original `TASK-WP04-02` verdict. WP04-03 remains blocked until all leaves are complete and the original task receives a new full independent `PASS` acceptance.

## Ordered Repair Leaves

1. `TASK-WP04-02-R1A` — Source policy, SourceDocumentVersion identity/dedup and SourceLocator repair.
   - Closes: AC-01 through AC-04, related mypy errors, and source/locator portions of AC-18/AC-19.
   - Verification boundary: exact grade matrix; deterministic fingerprint; unchanged re-observation; same-byte grade/metadata/status revisions; all locator types; no partial writes.

2. `TASK-WP04-02-R1B` — Evidence provenance-derived identity and immutable child repair.
   - Closes: AC-08 through AC-10, AC-16, AC-17 and related error/test gaps.
   - Verification boundary: MANUAL/DERIVED/CROSS_INSTRUMENT identity derivation, self/cycle rejection, replacement routing, nullable-clear semantics, mandatory child preservation and rollback.

3. `TASK-WP04-02-R1C` — Lifecycle, current-valid and trusted verification repair.
   - Closes: AC-05 through AC-07 and remaining lifecycle/tombstone errors.
   - Verification boundary: exact state table, fail-closed latest-first eligibility, explicit deterministic trusted-rule registry, complete lifecycle matrix tests.

4. `TASK-WP04-02-R1D` — Idempotency, replacement atomicity and final contract closure.
   - Closes: AC-11 through AC-15 and remaining AC-18 through AC-20.
   - Verification boundary: aggregate-scoped complete hashes, replay ordering, UNKNOWN_OUTCOME reconciliation, single-transaction replacement, concurrent reconciliation, full contract matrix, mypy and full regression.

5. `TASK-WP04-02-REVERIFY` — Full independent re-verification of the original task.
   - No implementation changes.
   - Re-runs every original blocking gate and the complete real-PostgreSQL Evidence matrix.

## Must Preserve Across Every Leaf

- Exact branch/worktree and three candidate-file boundary unless a later verifier explicitly authorizes a smaller supporting module.
- Existing WP04-01 models, repositories, migration and registry.
- No migration or schema change.
- Async SQLAlchemy and caller-owned outer transaction; service does not commit.
- Append-only SourceDocumentVersion/EvidenceVersion/history behavior.
- Existing WP04-01 and WP03 accepted behavior.
- Alembic single head `000000000004`.
- No API/OpenAPI, Research typed links, frontend, worker, MinIO writes, parser/extractor pipeline, embedding, RAG, Thesis, Agent or Capability Runtime work.
- No commit, merge, rebase, push or `main` mutation.
- Main-worktree verifier reports remain untouched and outside the candidate.

## Standard Forbidden Changes

- Do not change the frozen contract, original AC, DoD, required verification or evidence standard to fit the implementation.
- Do not weaken, delete, skip or xfail tests.
- Do not preserve a currently green assertion when that assertion contradicts the frozen contract; replace it with the correct positive/negative contract test and demonstrate the intended red-to-green cycle.
- Do not introduce Mock/Fake/InMemory persistence as L4 evidence.
- Do not use TODO, placeholder or arbitrary trusted strings as production capability.
- Do not refactor unrelated code or upgrade dependencies.

## Current Dispatch

Dispatch only `TASK-WP04-02-R1A`. Do not begin R1B/R1C/R1D in the same execution turn.
