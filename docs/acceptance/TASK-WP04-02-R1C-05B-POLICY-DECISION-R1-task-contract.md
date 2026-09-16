# TASK-WP04-02-R1C-05B-POLICY-DECISION-R1 — Narrow Ordinary Correction Policy Ratification

Status: `AWAITING_USER_POLICY_APPROVAL`.

This is a conditional docs-only successor, not a dispatch-ready business implementation task. The request for acceptance or a next prompt is not policy approval.

## Execution core

- Role: architecture policy recorder / task dispatcher.
- Size: SMALL; required acceptance `L1_STATIC_REVIEWED`.
- Objective: after explicit user approval, record a versioned narrow correction status/current-prior policy and derive only its smallest proposed implementation slice. Do not repeat the entire qualification investigation.
- Approval precondition: user explicitly approves all rules in the decision package below and creation of its companion normative addendum. If approval is missing, partial or contradictory, output `BLOCKED_POLICY_APPROVAL_REQUIRED` without writes. Do not interpret the present contract as approval.

## Proposed decision package — NOT APPROVED

1. Current VERIFIED prior permits ordinary correction. Current UNREVIEWED prior permits draft revision; this does not mean reviewed/verified evidence. Keep the existing public correction/replacement functions as compatible entry points, with command semantics derived from the actual prior status, not a caller-supplied permission flag. No new public API is required by this decision.
2. Both same-series N+1 and identity-changing replacement produce UNREVIEWED, `trusted_correction_rule=None`, complete CORRECTION provenance/audit tuple and exact predecessor references. Existing route-specific audit event kinds remain unchanged.
3. Generic correction/replacement from PENDING_REVIEW, DISPUTED, REJECTED, INVALIDATED or RETRACTED is denied with the existing domain state-transition error. Explicit review/dispute commands remain separate. No terminal rehabilitation command is approved.
4. All new correction routes must target the current-highest exact EvidenceVersion, including direct and lower predecessor-based creation; historical exact reads stay available. Definition of current-highest is within the selected prior series, not a new global cross-series head rule.
5. Previously COMMITTED exact-matching requests remain read-only replays under existing replay semantics; this decision does not repair incomplete request hashes or grant altered-input replay. R1D retains full request identity, race, reconciliation, locking/atomicity and UNKNOWN_OUTCOME design.
6. This package does not approve source-latest/ACTIVE requirements, DERIVED support eligibility, manual ownership changes, conflict propagation, effective-window eligibility, trusted success rules or initial VERIFIED import.

Record actual user confirmation text/date and the exact approved items. If the user chooses different behavior, this contract is not authorized: return to dispatcher for a revised bounded contract.

## Baseline preflight

Read main AGENTS.md, frozen `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`, 05B qualification draft/execution report/independent acceptance and 05A-R1 acceptance. Inspect relevant candidate entry points and durable R1B verifiers rather than assuming the draft is normative.

```text
main /Users/qianduoduo/Desktop/AI_app/ThesisGuard
HEAD   438738c543e4cae3e805d31324b068c1cd5c7059
parent 7d3734bc8346c16f9bbf7f7d9806309949c996de
tracked/index empty; preserve all existing untracked artifacts

candidate /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service
branch codex/wp04-02-evidence-domain-service
HEAD   0cef44fd2ffd929b40e849e607af0bd4c44d14d2
parent bdd70edc153b6ed5def65ed99c41f325df45f066
 M backend/evidence/services.py
 M tests/test_evidence_services.py

3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  errors.py
6e5c1c1c8cd83603a73c71c77993f76883f780fa773910fe3d026797e611aa69  services.py
dce8c3644441399ef443d54073c3121e8f59ebcd330c6955458c5db703056308  tests/test_evidence_services.py
```

Any mismatch: `BLOCKED_BASELINE_CHANGED`; do not move branches or adopt a changed baseline without separate authorization.

## Allowed writes after approval only

Only create these three documents in main:

- `docs/WP04_EVIDENCE_CORRECTION_POLICY_ADDENDUM_2026-09-16.md`.
- `docs/acceptance/TASK-WP04-02-R1C-05B-POLICY-DECISION-R1-execution-report.md`.
- `docs/acceptance/TASK-WP04-02-R1C-05C-01-task-contract.md`.

The addendum must cite frozen §§12–13 and accepted R1B behavior, contain a versioned decision ID, approval provenance, exact status/path matrix, interpretation of draft revision, precedence limited to this explicitly approved package, and remaining unknowns. Preserve the original frozen contract unchanged; no broad reinterpretation of terminal rules or replacement permission is allowed. A pending addendum is not normative before approval.

The 05C-01 proposed code contract must be SMALL/MEDIUM and status `PROPOSED / NOT_DISPATCHED`: first implement route-independent from-status admission only, not all qualifications. Allow only candidate `backend/evidence/services.py` and `tests/test_evidence_services.py`; retain fixed errors.py/verifiers/old tests. Preserve R1A/R1B accepted paths and COMMITTED read-only replay. Require real PostgreSQL red-to-green tests for forbidden statuses across four routes, caller commit/fresh-session no-residue checks, allowed VERIFIED/UNREVIEWED controls, full fixed-verifier and regression matrix, static checks and final hashes. Do not execute that contract in this task.

Keep current-highest direct-prior enforcement as a separately proposed follow-on slice with explicit race/atomicity interface to R1D, not a silently implemented guarantee or a claim that status-only code closes all approved rules.

## Must not

- No candidate business/test/error/model/repository/schema/migration/API/OpenAPI edits.
- No frozen contract, canonical PRD/TAD/AGENTS, old draft/acceptance/log/manifest/verifier edits.
- No DB tests, SQL, migration, fixture invocation, container actions or runtime mutation.
- No commit/merge/rebase/reset/checkout/push or branch/main tracked/index mutation.
- No enabling trusted rules, terminal rehabilitation, new data-source constraints or time/support policy.
- No R1D implementation, API/Research/Thesis/Agent, Capability Runtime or Sector Crowding.

## Blocking AC / verification

1. Explicit approval provenance matches the named narrow package and normative addendum target; no inferred approval.
2. Baselines/scope/hash match before and after; existing main untracked artifacts preserved.
3. Addendum resolves only the named authority conflict, with exact rule/version/compatibility statements and no broader source/time/support approval.
4. Proposed code contract is bounded, red-to-green, covers all public/lower routes, preserves committed replay and accepted historical behavior, and does not claim full ordinary qualification readiness.
5. Outputs pass UTF-8/LF/trailing-whitespace checks and actual content whitespace diff checks. Use `git diff --no-index --check /dev/null <new-file>` for untracked content; ordinary `git diff --check` alone does not inspect untracked files. Report baseline/final hashes and every command result.

Final status: `IMPLEMENTATION_COMPLETE` only for docs-only ratification after approval, otherwise `BLOCKED_POLICY_APPROVAL_REQUIRED` or `BLOCKED_BASELINE_CHANGED`. Completion is not business implementation, R1C/WP04-02 closure, dispatcher authorization for code, or Git integration approval.
