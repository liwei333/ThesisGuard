# TASK-WP04-00-R2 Repair Contract

- Repair ID: `TASK-WP04-00-R2`
- Original Task: `TASK-WP04-00`
- Failed AC: TOP-AC-01 through TOP-AC-05 as mapped in the R1 acceptance report
- Failed Gate: G2 Contract, G3 Architecture
- Source Acceptance Report: `docs/acceptance/TASK-WP04-00-acceptance.md`
- Required Acceptance: `L1_STATIC_REVIEWED`
- Evidence Matrix Type: expanded static matrix

## Execution Context

- Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-evidence-contract`
- Branch: `codex/wp04-evidence-contract`
- Expected HEAD: `a5c7863c905792439f657b26aaaff62c70483251`
- Allowed implementation file: `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`
- Do not create another worktree or switch branches.
- Do not commit, push, merge, rebase, stash, reset, or clean.

## Root Evidence

1. EvidenceSeries identity mismatch:
   - `series_identity_hash` includes CROSS_INSTRUMENT `scope_key`, whose value hashes the sorted instrument IDs, but replacing membership is described as appending inside the same series.
   - DERIVED `origin_key` hashes the supporting EvidenceVersion IDs, but changing that support set is described as appending inside the same series.
2. Lifecycle audit mismatch:
   - Ordinary correction appends `UNREVIEWED`, while the database rule only requires lifecycle audit metadata for non-default statuses.
   - The described retraction tombstone field list omits required non-null EvidenceVersion snapshot fields.
3. Independent regression suite is green: 67 passed, 4 existing warnings. This is preservation evidence, not proof of the documentation contract.

## Objective

Close only the two remaining R1 blocking contradictions so WP04-01 can implement the contract without inventing EvidenceSeries lineage or lifecycle audit semantics.

## Must Fix

### 1. Freeze identity-dimension change semantics

- Choose and state one canonical rule for each `series_identity_hash` dimension.
- Recommended rule: if any identity dimension changes (`scope_type`, `scope_key`, `information_type`, `claim_key`, `metric_key`, `period_start`, `period_end`, `provenance_kind`, `primary_source_document_id`, or `origin_key`), create a new EvidenceSeries; relate it to the prior exact EvidenceVersion with `supersedes_evidence_version_id` or the existing audit relation.
- Under that rule, changing CROSS_INSTRUMENT membership creates a new CROSS_INSTRUMENT EvidenceSeries because the member hash changes.
- Under that rule, changing the identity-defining DERIVED support set creates a new DERIVED EvidenceSeries because `origin_key` changes.
- Ordinary content/value/status/locator corrections that do not change an identity dimension append EvidenceVersion N+1 in the same EvidenceSeries.
- Synchronize sections 6-8, 13-18, 20-25, 27-28 and all affected examples/table constraints. Remove every contradictory “same series append” statement.

### 2. Make lifecycle audit and tombstone persistence enforceable

- Require `status_changed_at`, `status_changed_by_actor`, `status_change_kind`, and `status_reason` for every post-creation lifecycle/status append, including ordinary correction from an eligible state to `UNREVIEWED`.
- Allow those fields to be null only for the initial version-1 default UNREVIEWED creation when no lifecycle transition occurred.
- Freeze the allowed `status_change_kind` mapping for review request/decision, dispute, invalidation, retraction, ordinary correction, and trusted correction.
- Define a retraction/invalidation tombstone persistence shape that satisfies every non-null `evidence_version` constraint. Recommended: copy forward the complete required claim, provenance, source, grade, display, time, and locator snapshot while changing lifecycle fields and linking `supersedes_evidence_version_id`.
- Synchronize state-machine prose, correction/retraction sections, database field notes and constraints, commands, examples, and D-06/D-07.

## Preserve

- All R1 fixes for `version_fingerprint`, source re-observation, grade/metadata correction, and MinIO object reuse.
- All R1 Evidence scope/provenance/link-table fields and no-fake-source rules.
- Latest-first current-valid semantics with no fallback.
- Complete SourceType/SourceGrade matrix.
- ResearchPackage N+1 atomic typed-link model and prohibition on post-hoc historical module mutation.
- PostgreSQL/MinIO/pgvector/Redis/LLM system-of-record boundaries.
- Existing 29-section structure, traceability, and follow-up task boundaries.
- All WP01-WP03 code, tests, migrations, configuration, dependencies, generated client, and public contracts.

## Forbidden

- Do not expand into WP04-01 implementation.
- Do not edit code, tests, migrations, configuration, package definitions, generated clients, or any file other than the existing contract document.
- Do not weaken, delete, skip, or rewrite tests.
- Do not add TODO/TBD/placeholder decisions.
- Do not modify original AC, DoD, required verification, or evidence requirements.
- Do not introduce post-hoc Research link mutation or fallback-to-old-version validity.

## Required Verification

1. Prove the same `series_identity_hash` rule appears in identity, deduplication, table, command, examples, and decision records.
2. Explicitly check these counterexamples:
   - CROSS_INSTRUMENT membership A+B changes to A+C.
   - DERIVED support IDs V1+V2 change to V1+V3.
   - `metric_key` or period identity changes.
   - VERIFIED N corrected to UNREVIEWED N+1.
   - RETRACTED N+1 satisfies every non-null EvidenceVersion field and locator/provenance rule.
3. Run:
   - `test -s docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`
   - `rg -n '^## ' docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`
   - placeholder and trailing-whitespace scans
   - `git diff --check`
   - `pytest -q -rs -p no:cacheprovider`
4. Show final `git status --short --branch` and prove no tracked path outside the contract changed.

## Executor Final Response

Return only `IMPLEMENTATION_COMPLETE` or `BLOCKED`, with exact worktree/branch/HEAD, changed files, section-level fix evidence, counterexample results, commands and exit codes, test count/warnings, and final Git status. Do not self-approve the repair.
