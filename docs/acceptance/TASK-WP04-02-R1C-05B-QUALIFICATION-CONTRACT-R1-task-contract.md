# TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1 — Ordinary Correction Qualification Matrix

Status: READY_FOR_USER_DISPATCH. This is a read-only investigation and docs-only policy-contract task. It does not authorize business-code changes or a production rule activation.

## A. Execution Core

- Task ID: `TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1`.
- Objective: derive an approval-ready, evidence-backed ordinary-correction qualification matrix covering `from-status`, source state, exact/latest ownership, validity windows and terminal-version append behavior, while explicitly resolving or surfacing every conflict between the frozen Evidence contract, current production code and already accepted verifier behavior.
- Why now: R1C-05A-R1 closes the initial-VERIFIED replay defect. The remaining R1C implementation boundary is not safe to code because the frozen state table explicitly shows `VERIFIED -> correct_evidence -> UNREVIEWED`, while accepted R1B wiring exercises correction from a newly created `UNREVIEWED` exact version. Source-state and window admission are also not yet normative. Coding before resolving these facts risks breaking accepted behavior or silently rewriting the frozen contract.
- Role / type / size: DISPATCHER-SPEC AUTHOR / DOCUMENTATION + ARCHITECTURE POLICY / MEDIUM.
- Required acceptance: `L1_STATIC_REVIEWED`.
- Evidence matrix: Full because the resulting policy will govern append-only lifecycle, audit, eligibility and persistent mutation behavior.

### Fixed investigation baseline

```text
main: /Users/qianduoduo/Desktop/AI_app/ThesisGuard
main branch: main
main HEAD: 438738c543e4cae3e805d31324b068c1cd5c7059
main parent: 7d3734bc8346c16f9bbf7f7d9806309949c996de
main tracked/index diff: empty

candidate: /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service
candidate branch: codex/wp04-02-evidence-domain-service
candidate HEAD: 0cef44fd2ffd929b40e849e607af0bd4c44d14d2
candidate parent: bdd70edc153b6ed5def65ed99c41f325df45f066
candidate status:
 M backend/evidence/services.py
 M tests/test_evidence_services.py

3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
6e5c1c1c8cd83603a73c71c77993f76883f780fa773910fe3d026797e611aa69  backend/evidence/services.py
dce8c3644441399ef443d54073c3121e8f59ebcd330c6955458c5db703056308  tests/test_evidence_services.py
```

Read main `AGENTS.md`, `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`, `TASK-WP04-02-R1-repair-contract.md`, the R1C-01/02/03A/03B/04A/05A/R1 acceptance and task records, the actual candidate service/models/tests, and all fixed verifiers that call correction/replacement paths. Treat old reports as scoped historical evidence, not current implementation proof.

### Top Blocking AC

1. Produce a source-cited inventory of every actual ordinary-correction entry path and its current behavior: `revise_correct_evidence`, automatic identity-changing routing, direct `create_replacement_evidence_series`, and underlying creation with a predecessor. Include public signatures, validation order, target status, audit kind, exact predecessor, children, idempotency and transaction ownership. Do not infer behavior from function names.
2. Produce a complete proposed `from-status` matrix for all seven statuses (`UNREVIEWED`, `PENDING_REVIEW`, `VERIFIED`, `REJECTED`, `DISPUTED`, `INVALIDATED`, `RETRACTED`) across same-series correction and identity-changing replacement. Every cell must be `ALLOW`, `REJECT`, or `UNRESOLVED`, with frozen-contract citation, current-code evidence, accepted-test/verifier evidence, safety rationale, exact expected domain error when rejected, and required user decision when unresolved.
3. Produce equally explicit source/provenance and temporal qualification matrices: SOURCE_BACKED current/latest SourceDocumentVersion and `source_status`; grade/type compatibility; locator lineage; MANUAL/DERIVED/CROSS_INSTRUMENT rules; `period_start/end`; `effective_from/to`; `as_of`; command time; stale or expired evidence; source RETRACTED/SUPERSEDED; and conflict relationships. Separate structural validity, ordinary correction permission and downstream current-valid eligibility.
4. Identify every contract-versus-regression conflict. In particular, evaluate the frozen `VERIFIED -> correction` row against accepted R1B wiring that corrects a new `UNREVIEWED` version. Do not silently choose one side. Recommend the narrowest fail-closed policy and state whether it needs a new ADR/frozen-contract amendment, a successor verifier, a fixture correction, or no change. Existing verifier files and historical reports remain immutable.
5. Deliver an approval-ready draft plus an execution report. If and only if one unambiguous implementation boundary can be derived without changing frozen authority, include a proposed next SMALL/MEDIUM code Task Contract. Otherwise list the exact user decisions needed and stop at `NOT_READY_FOR_IMPLEMENTATION`.

### In scope

- Read-only inspection of repository instructions, frozen contract, accepted governance records, Git state, candidate service/models/tests and fixed verifier source.
- A status/path qualification matrix, source/provenance matrix, temporal/window matrix, conflict register, alternatives, recommended decision and migration/compatibility impact analysis.
- A proposed follow-on implementation contract only when the evidence yields one non-ambiguous rule set.

### Allowed changes

Only create these two main-worktree documents:

- `docs/acceptance/TASK-WP04-02-R1C-05B-ordinary-correction-qualification-draft.md`.
- `docs/acceptance/TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1-execution-report.md`.

### Must

- Cite exact file/symbol/line or contract section for every normative claim.
- Distinguish `OBSERVED`, `FROZEN_REQUIREMENT`, `ACCEPTED_REGRESSION_BEHAVIOR`, `PROPOSED`, `CONFLICT` and `UNKNOWN`.
- Explain what an Evidence terminal status prevents on the current row versus whether a new append-only correction lineage may supersede that exact row.
- Distinguish same-series N+1 from replacement-series v1 and direct replacement from automatic routing.
- Keep ordinary correction target `UNREVIEWED`, `trusted_correction_rule=None`, complete `CORRECTION` audit tuple and caller-owned transaction as protected facts unless a conflict is explicitly escalated.
- State whether source/current/window checks belong at correction admission, current-valid query, trusted-only admission, or more than one boundary; do not conflate them.
- Preserve production approved trusted rules as empty and initial direct VERIFIED as default-denied.
- Include at least these counterexamples: correction from each of seven statuses; stale `expected_version`; prior exact is not latest; latest source version is RETRACTED or SUPERSEDED; same bytes but new source version; expired `effective_to`; future `effective_from`; invalid period/window ordering; DERIVED support changes; direct replacement of a terminal exact version; same key replay with a qualification-relevant field changed.

### Must not

- Do not modify candidate business code, tests, verifier/oracle files, frozen contract, canonical PRD/TAD, old acceptance/report/manifest/log files, database schema/migrations, API/OpenAPI or Git history.
- Do not run PostgreSQL tests, SQL, migrations or runtime mutation. This task proves policy readiness, not implementation.
- Do not approve a positive trusted correction or initial-import rule, invent source bytes/parser artifacts, or treat grade/hash/actor/reason as semantic truth.
- Do not declare a frozen-contract change approved. Mark any proposed change as requiring explicit user approval and a separate versioned decision.
- Do not enter R1D, `UNKNOWN_OUTCOME`, concurrency, replacement atomicity, WP04-03/04, Research/Thesis/Agent, Capability Runtime or Sector Crowding.
- Do not commit, merge, rebase, reset, checkout, push, move branches or mutate main tracked/index state.

### Required document shape

The qualification draft must contain:

1. Status and authority (`PROPOSED`, not approved; `READY` or `NOT_READY_FOR_IMPLEMENTATION`).
2. Current implementation inventory by entry path.
3. Frozen requirement map.
4. Accepted verifier/regression behavior map.
5. Seven-status x correction-path matrix.
6. Source/provenance qualification matrix.
7. Period/effective-window/as-of/command-time matrix.
8. Contract-versus-regression conflict register.
9. At least two viable policy alternatives and tradeoffs.
10. One recommended narrow policy with explicit rationale, or an explicit no-decision result if authority is insufficient.
11. Compatibility and migration impact, including whether old hashes/rows/verifiers are affected.
12. Required user approvals.
13. Proposed next implementation task boundary only if ready.
14. Remaining R1C/R1D/WP04-02 boundaries.

### Required verification

```bash
# Read-only baseline and scope
git -C /Users/qianduoduo/Desktop/AI_app/ThesisGuard status --short --branch --untracked-files=all
git -C /Users/qianduoduo/Desktop/AI_app/ThesisGuard rev-parse HEAD HEAD^
git -C /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service status --short --branch --untracked-files=all
git -C /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service rev-parse HEAD HEAD^
shasum -a 256 \
  /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/errors.py \
  /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py \
  /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/tests/test_evidence_services.py

# Required evidence searches; expand with exact symbol inspection as needed
rg -n "revise_correct_evidence|create_replacement_evidence_series|verification_status|trusted_correction_rule|source_status|effective_from|effective_to|period_start|period_end" \
  docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md \
  docs/acceptance/TASK-WP04-02-R1*.md \
  /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence \
  /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/tests \
  /tmp/test_wp04_02_*.py \
  docs/acceptance/verifiers

# Final docs-only checks
git -C /Users/qianduoduo/Desktop/AI_app/ThesisGuard diff --check -- \
  docs/acceptance/TASK-WP04-02-R1C-05B-ordinary-correction-qualification-draft.md \
  docs/acceptance/TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1-execution-report.md
shasum -a 256 \
  docs/acceptance/TASK-WP04-02-R1C-05B-ordinary-correction-qualification-draft.md \
  docs/acceptance/TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1-execution-report.md
```

Also verify by exact before/after path inventory that no candidate byte, fixed verifier, old governance artifact or main tracked/index file changed. Because the two authorized documents are untracked, `git diff --check` alone is insufficient: inspect CR, trailing whitespace and final newline directly.

### Stop conditions

Stop and report `BLOCKED` if the fixed candidate identity/hashes/status differ; main tracked/index is not clean; required fixed verifier source is missing; an exact policy claim cannot be resolved without user authority; existing accepted behavior can only be preserved by changing the frozen contract; or any business/test/verifier/runtime mutation would be required.

### Expected evidence and executor response

Final status can only be `IMPLEMENTATION_COMPLETE` or `BLOCKED`; the executor cannot self-approve. Report baseline and final Git/hash state, files inspected, source-to-matrix traceability, all conflicts, recommended policy, readiness status, user decisions required, two output hashes and exact scope. Do not report `PASS`, `DONE`, `VERIFIED` or whole-R1C/WP04-02 completion.

## B. Governance Appendix

Apply the repository `AGENTS.md`, `ai-task-governor` core invariants/anti-drift/evidence rules and `ai-task-prompt-architect` minimum-sufficient-prompt principles. This task exists because implementation authority is currently ambiguous; documentation must expose that ambiguity rather than laundering it into code. Independent acceptance of these two documents and explicit approval of any policy/frozen-contract decision are required before a code task may be dispatched.
