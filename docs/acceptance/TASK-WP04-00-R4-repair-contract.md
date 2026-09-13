# TASK-WP04-00-R4 Repair Contract

## A. Execution Core

- Task ID: `TASK-WP04-00-R4`
- Objective: remove the remaining alternative replacement-lineage wording and make the replacement command plus Example 42 exactly match the already-correct R3 database/lifecycle rule.
- Why Now: R3 closed the audit-null database loophole, but two stale passages, one command row, and one incomplete example still force WP04-01/WP04-02 to invent behavior.
- Task Type: `REPAIR / DOCUMENTATION / CONTRACT_CONSISTENCY`
- Task Size: `SMALL`
- Required Acceptance: `L1_STATIC_REVIEWED`
- Evidence Matrix Type: `Full`

## Top Blocking AC

- TOP-AC-R4-01 [BLOCKING]: every identity-changing replacement path uses non-null `supersedes_evidence_version_id` pointing to the replaced exact EvidenceVersion; no alternative audit relation remains.
- TOP-AC-R4-02 [BLOCKING]: `create_replacement_evidence_series` explicitly names the canonical status audit inputs, status rules, trusted-rule input, predecessor FK, and transaction effect; `replacement reason` is replaced by `status_reason`.
- TOP-AC-R4-03 [BLOCKING]: Example 42 states the complete ordinary identity-changing correction behavior and rejection boundary required by R3.
- TOP-AC-R4-04 [BLOCKING]: only the existing Evidence contract document changes, all R1-R3 accepted rules remain intact, and all existing regression tests pass.

## Execution Context

- Worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-evidence-contract`
- Branch: `codex/wp04-evidence-contract`
- Expected HEAD: `a5c7863c905792439f657b26aaaff62c70483251`
- Allowed file: `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`
- Preserve the accumulated uncommitted document. Do not create a worktree, switch branch, or perform any Git history/state cleanup operation.

## Scope

In Scope:

- InformationType reclassification wording around current lines 345-349.
- Optimistic concurrency replacement wording around current lines 901-904.
- `create_replacement_evidence_series` command row around current line 1402.
- Example 42 around current lines 1900-1914.
- Only directly necessary line wrapping or traceability wording if one of those four edits requires it.

Out of Scope:

- Any new domain decision, enum, entity, table, migration, model, repository, service, API, frontend, worker, dependency, test, configuration, or generated artifact.
- Reopening identity dimensions, lifecycle enum, DB audit predicate, source fingerprint, provenance, tombstone, Research link, idempotency, concurrency, or WP04 follow-up boundaries.

Allowed Changes:

- `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md` only.

## Must

1. Replace both residual replacement phrases:
   - reclassification through `supersedes_evidence_version_id or audit event relation`;
   - replacement through `supersedes_evidence_version_id or audit relation`.
2. Both passages must instead require non-null `supersedes_evidence_version_id` pointing to the replaced exact EvidenceVersion. Do not retain any alternative relation/link/event path for replacement lineage.
3. Rewrite the `create_replacement_evidence_series` input column to explicitly name:
   - `prior_evidence_version_id`;
   - new identity dimensions;
   - replacement payload;
   - `status_changed_at`;
   - `status_changed_by_actor`;
   - canonical `status_reason`;
   - conditional `trusted_correction_rule` for a trusted VERIFIED replacement;
   - idempotency key.
4. Remove `replacement reason`; `status_reason` is the single canonical persisted reason.
5. Make the command row explicitly state:
   - ordinary replacement v1 is `UNREVIEWED`;
   - trusted deterministic replacement v1 may be `VERIFIED` only with a validated non-null `trusted_correction_rule`;
   - both use `status_change_kind='CORRECTION'` and the complete non-null audit tuple;
   - the new v1 sets `supersedes_evidence_version_id=prior_evidence_version_id` in the same transaction;
   - the prior EvidenceSeries/EvidenceVersion is not mutated.
6. Rewrite Example 42 so its Given/When/Then explicitly includes:
   - a current VERIFIED EvidenceVersion V3 in EvidenceSeries S1;
   - `metric_key='revenue_qoq'` changing to `metric_key='revenue_yoy'`;
   - creation of EvidenceSeries S2 and its EvidenceVersion v1 rather than S1 V4;
   - S2 v1 `verification_status='UNREVIEWED'` for the ordinary correction path;
   - `supersedes_evidence_version_id=V3`;
   - non-null `status_changed_at`, `status_changed_by_actor`, and `status_reason`;
   - `status_change_kind='CORRECTION'`;
   - rejection if the audit tuple is all-null or partial;
   - S1 and V3 remain unchanged.
7. Preserve the separate command-A brand-new initial v1 contrast: it has no predecessor and may use the all-null audit tuple only when UNREVIEWED with no lifecycle transition.

## Must Not

- Do not modify the R4 contract, original AC, DoD, required verification, or evidence requirements.
- Do not edit any file except the allowed contract document.
- Do not leave `replacement reason`, generic `status audit fields` in the replacement command input, `or audit relation`, `or audit event relation`, or an equivalent undefined replacement-lineage alternative.
- Do not add TODO/TBD/placeholder wording or “implementation may choose.”
- Do not change tests, dependencies, config, generated code, enums, schema decisions, or implementation.
- Do not broaden the task into WP04-01.
- Do not commit, push, merge, rebase, stash, reset, clean, checkout, switch branches, or create another worktree.
- Do not self-approve; executor status may only be `IMPLEMENTATION_COMPLETE` or `BLOCKED`.

## Required Verification

```bash
pwd
git status --short --branch
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git worktree list --porcelain

test -s docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md
test "$(rg -c '^## ' docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md)" = "29"

rg -ni 'supersedes_evidence_version_id.{0,100}\bor\b.{0,100}audit|through .{0,100}audit (event )?relation' \
  docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md

rg -n 'create_replacement_evidence_series.*(replacement reason|status audit fields)' \
  docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md

rg -n 'create_replacement_evidence_series.*status_changed_at.*status_changed_by_actor.*status_reason.*trusted_correction_rule' \
  docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md

sed -n '/### Example 42/,/## 25/p' docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md

rg -n '\b(TODO|TBD|FIXME|PLACEHOLDER)\b|implementation may choose' \
  docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md

rg -n '[[:blank:]]+$' docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md

git diff --check

git diff --exit-code -- \
  backend tests migrations apps/web/src \
  apps/web/package.json apps/web/package-lock.json \
  Makefile docker-compose.yml pyproject.toml AGENTS.md README.md

PYTHONDONTWRITEBYTECODE=1 pytest -q -rs -p no:cacheprovider

git status --short --branch
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git worktree list --porcelain
```

Expected command semantics:

- The first residual-alternative search must return no matches (`rg` exit 1).
- The second replacement-command ambiguity search must return no matches (`rg` exit 1).
- The explicit replacement-command search must match the final command row (`rg` exit 0).
- The placeholder and trailing-whitespace searches must return no matches (`rg` exit 1).
- Static and forbidden-path diff checks must exit 0.
- Full pytest must exit 0. If sandbox policy denies the local PostgreSQL connection, rerun the identical pytest command with the smallest necessary permission escalation and report both outcomes.

## High-Risk Counterexamples

- InformationType reclassification cannot choose an audit-event relation instead of the predecessor FK.
- Concurrent identity-changing replacement cannot omit the predecessor FK.
- Ordinary replacement command cannot omit one of the three input audit values or use a second reason name.
- Trusted VERIFIED replacement cannot omit `trusted_correction_rule`.
- Example 42 cannot append S1 V4, retain VERIFIED by default, omit predecessor/audit fields, or mutate V3.
- Brand-new command A must remain distinct from predecessor-bearing replacement command B.

## Stop Conditions

Stop and report `BLOCKED` if:

- Worktree, branch, HEAD, or accumulated document differs from the stated baseline.
- Another process changes the contract or a forbidden path during execution.
- The repair requires any file other than the allowed document or requires a new design decision.
- A required check cannot run without modifying tests, dependencies, configuration, or project state.
- Any existing R1-R3 accepted rule or verification standard would need to be weakened.

## Expected Evidence

- Exact worktree, branch, HEAD, `BASELINE_CHANGED_FILES`, and `FINAL_CHANGED_FILES`.
- TOP-AC-R4-01 through TOP-AC-R4-04 mapped to exact final lines and command results.
- Before/after evidence for both removed alternative-relation phrases.
- Final replacement command row with every explicit input and transaction invariant.
- Complete Example 42 Given/When/Then and each negative boundary.
- Every Required Verification command with exit code, test count/warnings, and final Git status.

## B. Governance Appendix

- Preserve immutable history, auditability, anti-drift, evidence-based acceptance, and separation of duties.
- This is a surgical consistency repair. Do not revisit accepted architecture or implement the next work package.
- Independent verification alone decides `PASS`, `FAIL`, or `BLOCKED`.
