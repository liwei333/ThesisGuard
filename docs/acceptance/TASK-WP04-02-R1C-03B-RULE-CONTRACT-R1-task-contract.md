# TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1 — Draft Named Trusted Correction Rule

Status: READY_FOR_USER_DISPATCH; docs-only proposal, not approval or implementation authorization.

## A. Execution Core

- Task ID: TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1.
- Objective: Produce one precisely reviewable deterministic trusted-correction rule definition and its later implementation acceptance, without enabling the rule or implementing a registry.
- Why Now: R1C-03A admission/no-inheritance and ORACLE-R1 repair passed. Production approval is empty. Frozen sections12/13/examples25/26 require a named rule and complete checks but do not authorize a concrete rule predicate.
- Role / Type / Size: specification EXECUTOR / DOCUMENTATION + bounded rule-design investigation / SMALL.
- Required Acceptance: L1_STATIC_REVIEWED; Compact Evidence Matrix. No DB execution or production readiness claim.

### Baseline and required reads

Read main AGENTS.md, docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md, docs/acceptance/TASK-WP04-02-R1-repair-contract.md, TASK-WP04-02-R1C-03A-task-contract.md, TASK-WP04-02-R1C-03A-ORACLE-R1-acceptance.md and execution report, actual candidate services/errors/models/repositories and correction/review tests. Canonical PRD/TAD may inform boundaries, not certify implementation. Read-only code inspection must verify the data required by a proposed predicate actually exists and has a trustworthy source.

```text
main: /Users/qianduoduo/Desktop/AI_app/ThesisGuard
main HEAD: 438738c543e4cae3e805d31324b068c1cd5c7059
main parent: 7d3734bc8346c16f9bbf7f7d9806309949c996de
candidate: /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service
branch: codex/wp04-02-evidence-domain-service
HEAD: 0cef44fd2ffd929b40e849e607af0bd4c44d14d2
parent: bdd70edc153b6ed5def65ed99c41f325df45f066
candidate status: clean
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
43b548232df4267f377c5e144222c9278c3cc478f6800720240c4618b689ebe3  backend/evidence/services.py
47ff645c0f782af67e9f6ee64520105febdb28c6547a43bf89b435bead6c5108  tests/test_evidence_services.py
```

Main has preserved untracked prior contracts/reports/oracle/evidence plus this dispatch contract and latest acceptance. Record exact initial paths; do not clean, commit, move or overwrite them. Unexpected candidate drift or tracked main drift is BLOCKED.

### Top Blocking AC

1. Draft clearly remains PROPOSED / NOT_APPROVED, production approved set remains empty, and no business/Git/DB/verifier mutation occurs. Preserve all baseline hashes and existing artifacts.
2. Define at most one candidate named rule: exact versioned ID, intended user value, accepted command routes, prior qualification, allowed changed fields, all required unchanged fields, exact source/version/locator/provenance/support requirements, deterministic transformation/predicate, semantic proof and fail-closed behavior. A rule name/actor/extractor version/hash/SourceGrade alone never proves semantics.
3. Provide a field→trusted source→predicate→failure→test-example mapping. Distinguish existing authoritative data from missing source text/object bytes/parser outputs or unavailable verification evidence. If no useful rule can be fully specified on current data, deliver an explicit NOT_READY recommendation and missing prerequisites, not an invented successful predicate.
4. Draft at least three concrete counterexamples and a later small real-PG implementation test plan. Distinguish new trusted correction from ordinary review, initial VERIFIED import and ordinary correction from-status qualification. All rule approval, source-state expansions or frozen-contract conflicts require explicit user decisions; do not silently resolve them into permissions.
5. Produce only the two authorized new docs, check their actual untracked whitespace/hashes and before/after scope, then report IMPLEMENTATION_COMPLETE or BLOCKED with approval questions and next implementation boundary. Do not self-approve the rule or declare R1C/WP04-02 complete.

### Scope / allowed changes

Create only in main:

- docs/acceptance/TASK-WP04-02-R1C-03B-rule-definition-draft.md.
- docs/acceptance/TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1-execution-report.md.

One rule definition, not a general strategy engine or multi-rule registry. Prefer a conservative correction class where semantic invariance can actually be proven. Investigate meaning-preserving formatting/representation changes first; any proposed numeric, unit, source, locator, time-period, scope or support change must have independently checkable evidence. Do not present a cosmetic rule as validated factual extraction. If restricted scope offers no meaningful benefit, say so instead of forcing a positive rule.

The draft must include:

- Current default-deny baseline and immutable-history ownership.
- One candidate rule, or documented reason no defensible candidate is ready.
- Supported/unsupported route matrix: same-series, automatic replacement, direct replacement and underlying create. A narrow rule may reject identity-changing routes; do not generalize authorization from one route to another.
- Complete schema/source/locator/semantic/audit/status predicates, None/unknown ID behavior, exact version lineage and validation-before-flush requirements.
- Conceptual immutable versioned definition→validator ownership, no runtime caller registration or arbitrary configuration bypass; no implementation/schema/API.
- Later real-PG positive/negative/no-residue/history test vectors with explicit inputs and expected results, and preservation of the existing independent verification matrix.
- Separate user approval block: scope, predicate, whether/when to enable, unsupported data prerequisites. Draft approval is not inferred from this task dispatch.

### High-risk examples

- Given a verified old fact and a new parser rule string, When no independent value/locator/source semantic proof exists, Then rule remains unapproved; parser label does not authorize VERIFIED.
- Given a supposedly formatting-only rule, When digits/sign/unit/period/source exact ID/locator/support set changes, Then it cannot qualify under formatting-only authorization; no implicit replacement extension.
- Given a retracted/conflicting/missing source or unqualified prior, When correction requests direct VERIFIED, Then specify rejection with auditable reasons, not inheritance from prior status/grade.
- Given initial import or ordinary review, Then do not apply a correction rule as a shortcut to cover their unfinished qualification contracts.

### Must / Must Not

Use ai-task-governor for scope/evidence discipline and ai-task-prompt-architect for the later implementation prompt. If using a design skill, follow its approval boundary without starting implementation.

No code/tests/errors/models/repositories/schema/migration/API edits; no DB commands, pytest, SQL, Docker startup/exec, MinIO/parser/model work, production activation, old verifier/log/manifest/contract edits or Git writes. No dependencies upgrade, arbitrary trusted strings or LLM semantic judgment. Do not implement other R1C leaves or R1D.

### Required Verification

Read-only Git and hash checks before and after:

```bash
git status --short --branch --untracked-files=all
git rev-parse HEAD HEAD^
git diff --name-only
git diff --cached --name-only
git diff --check
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

Run business file checks in candidate; run main scope checks separately in main. The two new untracked docs require actual whitespace checks and SHA256; git diff alone omits them. Verify every draft assumption against exact code/contract references, every positive test vector against the written predicate, and every missing prerequisite as NOT_READY rather than IMPLEMENTED. No DB suite is required or authorized in this docs-only task.

### Stop Conditions / expected evidence

BLOCKED on baseline drift, inaccessible governing files, writes outside two docs, existing destination conflict, or a requirement to alter frozen contract/production state to complete the specification. Lack of sufficient semantic evidence can be a valid complete NOT_READY draft; it is not permission to invent data or a reason to change code.

Deliver initial/final scope and hashes, source/field/predicate matrix, one proposed rule or NOT_READY result, concrete test vectors, source discrepancies/unknowns, exact user decisions and a single later implementation slice contingent on approval. Status only IMPLEMENTATION_COMPLETE or BLOCKED; independent verifier accepts the docs, user separately approves policy. No implementation is automatically dispatched.

## B. Governance Appendix

Follow ai-task-governor core invariants, anti-drift, evidence-based acceptance and acceptance levels. Historical acceptance is time/branch/scope-specific; this specification task cannot promote a PROPOSED rule or reinterpret empty approval as a full positive trusted engine.

Initial-import qualification, ordinary-correction full source-state qualification, R1D/final WP04-02 reverify, Git integration, API/Research references, Sector Crowding and Capability Runtime remain separate/deferred. No unfinished leaf is closed by the rule definition alone.
