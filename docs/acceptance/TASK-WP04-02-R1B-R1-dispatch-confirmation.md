# TASK-WP04-02-R1B-R1 Dispatch Confirmation

**OVERALL: FAIL**

## Metadata

- Date: 2026-09-15 (Asia/Shanghai)
- Verifier: Codex, independent local confirmation of the supplied execution feedback.
- Source task: `TASK-WP04-02-R1B-REBASELINE-REVERIFY-R1`.
- Source report: `TASK-WP04-02-R1B-REBASELINE-REVERIFY-R1-acceptance.md` in this directory; preserved unchanged.
- Source repair: `TASK-WP04-02-R1B-R1-repair-contract.md`; preserved unchanged.
- Required acceptance: L1, L2, L3, L4_DB.
- Achieved evidence: baseline/scope inspection, source-level contract analysis, and four fresh real-PostgreSQL counterexamples. Successful end-to-end replacement semantics and complete L3/L4_DB acceptance remain missing.
- Next action: dispatch only `TASK-WP04-02-R1B-R1`, using the companion execution contract.

## Baseline and Changed Files Snapshot

Main repository: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard`, branch `main`, HEAD `7d4e395d949d8cd050548347f31dd6b492f65834`.

Candidate: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`, branch `codex/wp04-02-evidence-domain-service`, HEAD `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`.

The candidate HEAD parent is `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`; HEAD adds exactly the three service candidate files. SHA-256 of the HEAD blobs matches accepted R1A-R2:

| File | Accepted HEAD blob SHA-256 | Current candidate SHA-256 |
|---|---|---|
| backend/evidence/errors.py | 3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec | 3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec |
| backend/evidence/services.py | f980f2fcbb789b08dd25982f6af2e548def71a3cba8851d79ae0155748736981 | f1c4a9b85505cb152273a246525a4b3214eaaff0847c328f1d2ed2b350fadf0c |
| tests/test_evidence_services.py | 619324318d25bc25a45941e69d0e10a1539ec9eed4d302a817d3e278e9719396 | 454f95d269b7521764409b952ba26055c473d62c93c75313b16fa2e4fa66a0ce |

`BASELINE_CHANGED_FILES` and `FINAL_CHANGED_FILES` in the candidate both contain only modifications to services.py and test_evidence_services.py. Candidate attribution is certain relative to the accepted HEAD; this verification made no candidate edits. Main's four pre-existing untracked acceptance/repair documents were preserved. This turn adds only this confirmation and the companion execution contract, without Git operations.

## Classification and Gates

- Task type: repair acceptance / Bug Fix dispatch.
- Repair size: SMALL (one semantic defect, two allowed files); DB risk is material, so use a Full evidence matrix.
- Selected gates: baseline, scope, contract, architecture truth boundary, focused test, DB persistence, regression/evidence reporting, prompt quality.
- UI, API/OpenAPI, migration-change, external-provider and security-change gates: NOT_APPLICABLE to this bounded repair.

| AC / Gate | Result | Fresh evidence | Limitation |
|---|---|---|---|
| G0 accepted rebaseline | PASS | Git parent, three-file commit stat, accepted blob hashes and current hashes checked | No fetch; remote state not independently refreshed |
| G1 candidate scope | PASS | Only services.py and test_evidence_services.py modified; errors.py unchanged | Does not accept all candidate business behavior |
| G2/G3 exact-version graph semantics | FAIL | services.py:2358-2401 uses direct series equality and a series-target graph traversal | Both must be corrected, not only the first guard |
| G4 legal replacement counterexample | FAIL | Fresh verifier: 1 failed, 3 passed; failing node named below | No successful replacement audit/child assertions reached |
| DB persistence | FAIL | Real PostgreSQL public service call rejects a valid replacement before routing | Not a missing-DB or baseline block |
| Invalid replacement / duplicate support residue checks | PASS (focused only) | Fresh verifier's three other nodes passed | Not comprehensive R1D atomicity acceptance |
| G5 full regression | NOT_RERUN | Prior report records 95 service, 12 R1A verifier, 35 regression tests and static checks green | Historical supporting evidence only; no fresh full-suite PASS claimed |
| G6 verdict evidence | PASS | Actual failure agrees with source inspection and supplied report | Original R1B remains open |

## Commands Actually Executed

- Main: `pwd`, `git status --short --branch`, `git rev-parse HEAD`, full AGENTS.md read.
- Candidate: status, HEAD, SHA-256 of all three candidate files; `git show` blob hashes; `git rev-parse f7c50ab^`; `git diff --check` (exit 0); `git diff --stat`.
- Main object database: `git show --format=fuller --stat f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`.
- Inspected frozen contract derivation-link constraints and Examples 37/38, candidate validation/routing/test code, verifier-owned test and existing repair contract.
- Fresh DB command, from the candidate worktree, with permission to access local PostgreSQL:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service \
pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs
```

Result: exit 1, `1 failed, 3 passed in 3.67s`.

## Blocking Finding BF-01

Failing node: `test_replacement_can_support_prior_exact_version_without_exact_cycle`.

Trace: `revise_correct_evidence` (853) -> `_resolve_revision_children` (1551) -> `_validate_derivation_links` (2360).

Error: `EvidenceInvalidDerivationLink: Evidence cannot derive from its own series`.

The legal graph is `new replacement exact version -> old derived exact version -> source-backed exact version`. No edge returns to the new exact version. Frozen contract lines 1314-1331 define exact EvidenceVersion FKs, no exact self-link, and cycle traversal; Example 37 requires changed supporting-ID sets to create replacement series v1.

Two implementations share the same defect:

1. Direct equality of `support.evidence_series_id` with the prior derived series ID rejects historical exact supports.
2. `_support_graph_reaches_series` traverses exact edges but terminates on series equality, not a path to the proposed derived exact version. Removing only the direct guard is insufficient.

Candidate test blocks at approximately lines 1226 and 1311 encode the wrong rule. The apparent indirect cycle `new B replacement -> old A -> old B -> source` is also acyclic on exact IDs. Correct both expectations and add genuine exact-target defense coverage; retaining these mistaken failures is not regression preservation.

## Non-Blocking Note: Representability

Public append-only create/revise commands generate a new exact version, not an edge mutation on the old version. A caller normally cannot supply that new ID in advance. Do not manufacture a series-level cycle to stand in for exact self/cycle coverage. Use an isolated real-DB graph and the production exact-target validator/helper where necessary, record the public-command limitation, and retain production validation wiring. No permission is granted to mutate historical production links or change models/repositories/migrations.

## Repair Required / Decision

`FAIL — REPAIR_REQUIRED`; repair ID `TASK-WP04-02-R1B-R1`.

The accepted baseline is not the blocker. Preserve R1A and non-defective R1B behavior, repair only exact graph validation and corresponding tests. No implementation repair, commit, merge, rebase, push, DB reset or main-branch mutation was performed. R1C cannot begin until independent acceptance closes this repair and R1B. The original WP04-02 remains unaccepted.

Companion dispatch contract: `TASK-WP04-02-R1B-R1-execution-contract.md` in this directory.
