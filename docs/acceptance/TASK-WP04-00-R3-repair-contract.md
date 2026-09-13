# TASK-WP04-00-R3 Repair Contract

## A. Execution Core

- Task ID: `TASK-WP04-00-R3`
- Objective: make replacement-series version 1 lifecycle audit semantics fully enforceable and consistent across the Evidence domain contract.
- Why Now: R2 closed every other known WP04-00 blocker, but WP04-01 cannot safely encode the migration while a replacement v1 can still fall through the brand-new-initial-v1 audit exception.
- Task Type: `REPAIR / DOCUMENTATION / ARCHITECTURE_CONTRACT`
- Task Size: `SMALL`
- Required Acceptance: `L1_STATIC_REVIEWED`
- Evidence Matrix Type: `Full`

## Top Blocking AC

- TOP-AC-R3-01 [BLOCKING]: the contract distinguishes a genuinely new initial EvidenceSeries v1 from a replacement EvidenceSeries v1 and gives each exactly one audit rule.
- TOP-AC-R3-02 [BLOCKING]: database constraints, field notes, and service invariants prohibit all-null lifecycle audit metadata whenever `supersedes_evidence_version_id` is non-null.
- TOP-AC-R3-03 [BLOCKING]: the replacement command, correction rules, examples, and decision records require the same status, audit tuple, change kind, and lineage link without contradiction.
- TOP-AC-R3-04 [BLOCKING]: only the existing Evidence domain-contract document changes, and all existing WP01-WP03 tests remain green.

## Execution Context

- Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-evidence-contract`
- Branch: `codex/wp04-evidence-contract`
- Expected HEAD: `a5c7863c905792439f657b26aaaff62c70483251`
- Allowed file: `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`
- Preserve the current uncommitted WP04 document; do not recreate, clean, stash, or discard it.

## In Scope

- Lifecycle/status metadata rules for the first EvidenceVersion of a replacement EvidenceSeries.
- The related database constraint/field notes, replacement command, correction prose, identity-change examples, D-02/D-06/D-07/D-15 as applicable, and traceability.
- One explicit Given/When/Then example for an identity-changing correction.

## Out of Scope

- WP04-01 models, migrations, repositories, services, APIs, frontend, workers, or runtime implementation.
- Reopening the settled identity dimensions, source fingerprint, provenance model, tombstone design, Research N+1 link model, enums, or follow-up package boundaries.
- Any code, test, migration, configuration, dependency, generated client, or file other than the existing contract document.

## Must

- Define `brand-new initial v1` as an EvidenceVersion created without a predecessor: `version=1`, `verification_status='UNREVIEWED'`, and `supersedes_evidence_version_id IS NULL`. Only this case may store the four status audit fields as all-null.
- Define `replacement v1` as the first EvidenceVersion of a new EvidenceSeries that replaces an exact prior EvidenceVersion. It must set `supersedes_evidence_version_id` to that exact prior ID and must not use a separate unspecified “or audit relation” alternative.
- For an ordinary identity-changing correction, require replacement v1 to be `UNREVIEWED` with all four fields non-null: `status_changed_at`, `status_changed_by_actor`, `status_change_kind='CORRECTION'`, and `status_reason`.
- If the existing trusted deterministic correction path is retained for identity-changing replacement, require replacement v1 to be `VERIFIED`, keep the same complete audit tuple with `status_change_kind='CORRECTION'`, and require a non-null validated `trusted_correction_rule`. Do not invent another change-kind enum.
- Make the database blueprint enforce the bidirectional boundary: all-null requires the brand-new initial-v1 predicate; any non-null `supersedes_evidence_version_id`, replacement operation, or correction requires all four audit fields.
- Change `create_replacement_evidence_series` so its inputs and transaction effects explicitly persist the status audit tuple, exact predecessor link, and trusted rule when applicable. Map/rename `replacement reason` to canonical `status_reason`; do not leave two unsynchronized reasons.
- Add a Given/When/Then counterexample: a VERIFIED row corrected by changing `metric_key` creates a new series/v1; that v1 links the prior exact ID, is UNREVIEWED for ordinary correction, has complete CORRECTION audit metadata, and is rejected if the tuple is all-null.
- Synchronize all affected prose, schema/table constraints, commands, examples, decisions, and traceability while preserving the current 29-section structure.

## Must Not

- Do not change any original AC, DoD, required verification, or evidence requirement.
- Do not edit any file except `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md` in the specified worktree.
- Do not add a new enum merely to avoid choosing the existing correction semantics.
- Do not leave “or audit relation,” “implementation may choose,” TODO, TBD, placeholder, or another undefined persistence alternative for replacement lineage/audit.
- Do not weaken/delete/skip tests, change dependencies, broaden scope, or start WP04-01.
- Do not commit, push, merge, rebase, stash, reset, clean, switch branches, or create another worktree.
- The executor may report implementation completion but may not self-approve or claim PASS/VERIFIED/DONE.

## Required Verification

```bash
pwd
git status --short --branch
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
test -s docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md
rg -n '^## ' docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md
rg -n "supersedes_evidence_version_id|create_replacement_evidence_series|status_change_kind|CORRECTION|initial version 1|replacement" docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md
rg -n 'TODO|TBD|placeholder|implementation may choose|or audit relation' docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md
rg -n '[[:blank:]]+$' docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md
git diff --check
git diff --exit-code -- apps/web/package.json apps/web/package-lock.json backend tests migrations apps/web/src Makefile docker-compose.yml pyproject.toml
PYTHONDONTWRITEBYTECODE=1 pytest -q -rs -p no:cacheprovider
git status --short --branch
```

The placeholder/ambiguity and trailing-whitespace scans pass only when they produce no matches. If sandbox restrictions deny the local PostgreSQL connection, rerun the same pytest command with the smallest required permission escalation and report both results.

## High-Risk Counterexamples

- A brand-new unreviewed series v1 has no predecessor and may have an all-null audit tuple.
- A replacement unreviewed series v1 has `supersedes_evidence_version_id` and must have the all-non-null CORRECTION audit tuple despite also being version 1.
- A trusted deterministic replacement v1 cannot be VERIFIED without the full audit tuple and a validated `trusted_correction_rule`.
- A same-series ordinary correction remains N+1 UNREVIEWED with complete CORRECTION audit metadata.
- An identity-changing request cannot append N+1 in the old series or use an unspecified alternative audit relation.

## Stop Conditions

Stop and report `BLOCKED` if:

- The required worktree, branch, HEAD, or accumulated contract document does not match the execution context.
- Another process has changed the contract or any forbidden path since baseline capture.
- Closing the ambiguity would require a new enum, implementation change, migration, API change, or any file outside the allowed document.
- A project fact conflicts with this repair contract, or the required test environment cannot be made available without modifying project state.
- Any verification standard would need to be weakened or skipped.

## Expected Evidence

- Exact worktree, branch, HEAD, `BASELINE_CHANGED_FILES`, and `FINAL_CHANGED_FILES`.
- TOP-AC-R3-01 through TOP-AC-R3-04 mapped to exact sections/lines and verification results.
- Before/after evidence that the old all-null replacement counterexample is eliminated.
- Exact DB predicate and replacement-command inputs/effects.
- Results for every high-risk counterexample.
- Every required command with exit code, final test count/warnings, and final Git status.

## B. Governance Appendix

- Preserve immutable-history, anti-drift, evidence-based acceptance, and separation-of-duties rules.
- This is a repair task, not a new design phase: do not revisit already accepted R2 decisions.
- The executor final status can only be `IMPLEMENTATION_COMPLETE` or `BLOCKED`; independent verification decides PASS/FAIL/BLOCKED.
