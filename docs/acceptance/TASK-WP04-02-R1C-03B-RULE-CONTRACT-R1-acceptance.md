# TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1 — Independent Specification Acceptance

**OVERALL: PASS**

## Metadata and scope

- Date: 2026-09-16, Asia/Shanghai.
- Task ID: TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1.
- Verifier: Codex, independent VERIFIER; executor completion is input, not approval.
- Report path: docs/acceptance/TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1-acceptance.md; chosen from AGENTS and existing docs/acceptance convention.
- Implementation Status: IMPLEMENTATION_COMPLETE for read-only investigation and two documents.
- Classification: DOCUMENTATION / bounded rule specification, SMALL; policy/semantic-evidence risks; Compact Evidence Matrix.
- Required / Achieved Acceptance: L1_STATIC_REVIEWED.
- Missing Acceptance within this docs-only task: NONE.
- Repair Required: NO.

PASS accepts the specification investigation, including its permitted NOT_READY outcome. It does not approve tg.tc.display-title-ascii-tail.v1, supply missing original evidence, certify a semantic validator, enable production rules or close whole R1C/WP04-02. No L2/L3/L4 behavior is claimed in this turn.

## Baseline and actual changes

```text
main: /Users/qianduoduo/Desktop/AI_app/ThesisGuard
HEAD: 438738c543e4cae3e805d31324b068c1cd5c7059
parent: 7d3734bc8346c16f9bbf7f7d9806309949c996de
candidate: /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service
branch: codex/wp04-02-evidence-domain-service
HEAD: 0cef44fd2ffd929b40e849e607af0bd4c44d14d2
parent: bdd70edc153b6ed5def65ed99c41f325df45f066
candidate status: clean
main and candidate tracked/index diff: empty
```

Fresh candidate hashes match the fixed contract:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
43b548232df4267f377c5e144222c9278c3cc478f6800720240c4618b689ebe3  backend/evidence/services.py
47ff645c0f782af67e9f6ee64520105febdb28c6547a43bf89b435bead6c5108  tests/test_evidence_services.py
```

Executor-attributable delivered files, independently rehashed and checked from actual UTF8 bytes:

| File | Bytes / lines | SHA256 |
| --- | --- | --- |
| TASK-WP04-02-R1C-03B-rule-definition-draft.md |39992 /272 |546db6d21ff450186d5bdf206a158141f81aa9e6ac394c7aca522a113156d193 |
| TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1-execution-report.md |16546 /170 |3e5decf65c81b6aac93f02029a11fb2da0a80150faa42249cc470d0ffa5886f1 |

At independent review start main has18 untracked paths, agreeing with the executor's preserved16+two allowed additions. Candidate has no changes. BASELINE_CHANGED_FILES are these18 preserved governance/oracle paths, not business code. This review adds only this acceptance and TASK-WP04-02-R1C-04A-task-contract.md. FINAL_CHANGED_FILES include those two further untracked docs; no candidate changes. Attribution of current additions is CERTAIN from exact allowed paths. No old reports or policy files are overwritten.

Recomputed every path in the previous ORACLE before-manifest's82 protected hash entries and all48 indexed ORACLE artifacts (size+hash): no mismatch. Governing/current candidate hashes and existing untracked artifacts therefore have direct preservation evidence. The executor's broader341-main/184-candidate historical before-map is retained in its session rather than a project artifact; this verifier does not claim independently re-proving all525 historical comparisons. Current clean candidate, tracked/index diffs and durable protected/indexed artifacts are independently verified. This limit is non-blocking for the two-document contract and is not concealed.

## Compact Blocking AC Matrix

| AC | Inspected evidence | Independent check / boundary | Result |
| --- | --- | --- | --- |
|1 | Draft status PROPOSED/NOT_APPROVED, NOT_READY; actual empty frozenset in candidate service | Fresh Git/three hashes,82 protections/48 artifacts, two allowed docs; no activation |PASS |
|2 | Draft sections2–5 define only one investigation ID, exact trailing U+0020 transform, unchanged fields/prior/route/status/audit and missing gates | No executable successful predicate; rule name/actor/hash/grade explicitly insufficient; exactness proof distinguished from prior factual truth |PASS |
|3 | Draft field→source→constraint→failure→example matrices, source/object/quote/parser gaps | Actual service saves metadata and exact refs, _validate_provenance validates structure; no independent object/quote/claim semantic verification observed |PASS |
|4 | Nine concrete counterexamples; conditional PG vectors; review/import/from-state/R1D distinction | Future tests clearly not executed; four routes currently refuse candidate rule; no replacement authorization inherited from narrow same-series proposal |PASS |
|5 | Only two new docs, explicit user policy questions and contingent later prompt | Actual byte/whitespace/hash checks; no CR/trailing whitespace, LF ending; local link targets exist; executor does not self-approve |PASS |

## Gates

| Gate | Result | Evidence |
| --- | --- | --- |
|G0 Baseline |PASS | Fixed main/candidate/parent/status and readable immutable contract |
|G1 Scope |PASS | Two-document delivery, no business/old-evidence differences |
|G2 Contract |PASS | NOT_READY is explicitly allowed by AC3; all five AC supplied |
|G6 Evidence |PASS | Actual draft, code/contract references, fresh hashes/scope and counterexample review |

Runtime Test, DB Persistence, Browser, Worker and behavioral Regression gates: NOT_APPLICABLE for this docs-only verification. Policy/architecture boundaries were inspected within Scope/Contract; no architecture implementation is accepted.

## Source review and rationale

Read AGENTS, immutable dispatch contract, full draft/report, frozen lifecycle/correction/D-01 requirements and relevant candidate create/revise/append/provenance/locator/model paths. The draft does not mistake a common StorageClient.get_object helper for its use in Evidence admission. Object references, quote_hash and review status do not establish independent byte-bound source semantics.

The proposed title transform can show representation invariance only under a yet-unapproved title semantics convention. Q(new)=Q(prior) alone preserves even an erroneous prior. The document correctly stops short of asserting factual verification, and does not import synthetic fixture hashes or a legacy VERIFIED seed as production proof. Narrow source-grade/prior/relations/window proposals remain unapproved, not new ordinary-correction policy.

Relevant negative examples independently reviewed: unit scaling without value conversion, negation/title meaning changes, same declared hash with different exact source/locator, changed periods/window, unsupported support/path changes, and stale/retracted/conflicting prior source. All remain outside the investigated rule's permission. Its conditional prompt is not currently executable authorization.

## Commands actually executed in this turn

| Command/check | Actual result |
| --- | --- |
| git status --short --branch --untracked-files=all, main; candidate status |18 main untracked paths at start; candidate clean |
| git rev-parse HEAD HEAD^, both trees | Fixed values above, exit0 |
| git diff --name-only; git diff --cached --name-only; git diff --check, both trees |Empty, each exit0 |
| Actual two-doc bytes/SHA/UTF8/whitespace validation |Expected hashes/size/lines; no CR/trailing whitespace; final LF, exit0 |
| JSON/hash validation of82 protected and48 prior indexed files |No mismatches, exit0 |
| Candidate AST/source and draft local-link inspection |Empty immutable approval set; model columns and relationship policy inspected; no missing local link targets |

No pytest, DB connection/SQL/migration, Docker/MinIO operation, positive semantic validator, dependency install or Git write was performed. Historical run results are not relabeled as this turn's tests.

## Findings and next selection

- BLOCKING: NONE for this specification delivery.
- NON-BLOCKING: full historical525-path map not independently available as a durable project snapshot; verified scope/protection limits above are explicit. No need to create a third artifact retroactively to pass this two-doc task.
- Candidate readiness stays NOT_READY / NOT_APPROVED. Policy approval and deferral are not inferred from this acceptance. Recommendation is to stop investing in a low-evidence title-cleanup success rule for now; keep approval empty, retain the draft for later re-review. This is not an approved change to the frozen overall acceptance scope.

Next smallest useful implementation task: TASK-WP04-02-R1C-04A — Evidence display_text nonblank admission and no-residue repair. Frozen D-01 explicitly requires non-empty display_text; actual revision override validation only forbids clearing display_text to None, and current create/append/model paths have no nonblank body validation. This is a statically identified gap, **not a fresh PostgreSQL counterexample or a FAIL attributed to the docs executor**. The next executor must first prove actual business RED on unchanged0cef bytes.

Do not immediately enforce a global VERIFIED-only ordinary-correction from-state policy: frozen table/replacement/terminal wording and existing fixed wiring verifier's UNREVIEWED same-series setup need a separate contract decision. The selected payload-admission slice avoids that unresolved policy and does not close it. No positive trusted/source artifact infrastructure, initial VERIFIED semantic qualification or broad state-table change is bundled.

Repair Required for this task: NO. Whole R1C/R1D/final WP04-02 reverify remain open; no API/Git integration/Sector Crowding/Capability Runtime authorization is implied.
