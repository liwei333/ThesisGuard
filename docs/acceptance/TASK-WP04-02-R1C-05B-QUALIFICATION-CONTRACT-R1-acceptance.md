# TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1 — Independent Specification Acceptance

OVERALL: PASS

## Metadata and authority

- Date: 2026-09-16, Asia/Shanghai.
- Verifier: Codex, independent static specification reviewer.
- Required / achieved acceptance: `L1_STATIC_REVIEWED` / `L1_STATIC_REVIEWED`.
- Accepted delivery: ordinary-correction qualification investigation and proposed policy draft, not business implementation or policy activation.
- Policy status remains `PROPOSED / NOT_APPROVED`.
- Implementation readiness remains `NOT_READY_FOR_IMPLEMENTATION`.
- Skills used: `ai-task-governor`, `ai-task-prompt-architect`, `verification-before-completion`, with `using-superpowers` workflow entry.
- No database tests, SQL, migrations, runtime mutation, candidate edits or Git writes were performed in this acceptance turn.

## Baseline and changed-files snapshot

Main repository: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard`.

```text
branch main
HEAD   438738c543e4cae3e805d31324b068c1cd5c7059
parent 7d3734bc8346c16f9bbf7f7d9806309949c996de
tracked/index diff empty
```

Candidate: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`.

```text
branch codex/wp04-02-evidence-domain-service
HEAD   0cef44fd2ffd929b40e849e607af0bd4c44d14d2
parent bdd70edc153b6ed5def65ed99c41f325df45f066
 M backend/evidence/services.py
 M tests/test_evidence_services.py
```

Candidate SHA-256 matches the investigation contract:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
6e5c1c1c8cd83603a73c71c77993f76883f780fa773910fe3d026797e611aa69  backend/evidence/services.py
dce8c3644441399ef443d54073c3121e8f59ebcd330c6955458c5db703056308  tests/test_evidence_services.py
```

`BASELINE_CHANGED_FILES`: the two candidate modifications above and existing main untracked governance artifacts. Main tracked/index diff is empty.

Execution-task attributable files: exactly the qualification draft and execution report. Attribution: `CERTAIN` for those new named outputs; chronological protection of every pre-existing untracked file is qualified below.

Acceptance-turn additions: this report and `TASK-WP04-02-R1C-05B-POLICY-DECISION-R1-task-contract.md`. No existing deliverable is rewritten. `FINAL_CHANGED_FILES`: candidate modifications unchanged; main tracked/index remains empty, with the two acceptance-turn documents additionally untracked.

## Classification and selected gates

- Type: documentation / architecture policy specification.
- Risk: append-only lifecycle policy and authority drift; no runtime execution.
- Size: MEDIUM; Full evidence matrix.
- Selected: baseline, scope, contract, architecture, evidence, task-size and prompt-quality gates.
- Test, DB persistence, runtime and regression execution gates: `NOT_APPLICABLE` for this read-only specification task. Historical test results are not fresh verification.

## Top blocking acceptance criteria

| AC | Result | Independently reviewed evidence |
| --- | --- | --- |
| AC1: actual entry-path inventory | PASS | Draft §2 maps revise, automatic routing, direct replacement and predecessor-based lower creation. Candidate public functions and validation order corroborate the main observations. |
| AC2: seven-status/path authority matrix | PASS | Draft §5 covers all seven statuses across same-series/replacement, distinguishes observed acceptance from authority, and gives rejection codes and required decisions. |
| AC3: provenance/source/time qualification | PASS | Draft §§6–7 separate structural validity, correction admission, current-valid and trusted admission; unknown source-latest/support/window policies remain explicit. |
| AC4: contract/regression conflicts | PASS | Draft §§4,8,10 identifies the VERIFIED-only table versus accepted UNREVIEWED R1B behavior; alternatives A/B/C do not silently amend frozen authority. |
| AC5: honest readiness and deliverables | PASS | Both required outputs exist. `NOT_READY_FOR_IMPLEMENTATION` correctly invokes the contract's permitted no-unambiguous-boundary outcome; no executable business contract or approval was fabricated. |

## Gate results and evidence matrix

| Gate / claim | Result | Evidence and limitation |
| --- | --- | --- |
| Baseline | PASS | Fresh main/candidate branch, HEAD/parent/status and three candidate SHA-256 values match fixed investigation baseline. |
| Scope | PASS | Both outputs are new untracked main documents; main tracked/index diff empty; candidate scope/hash unchanged. No candidate or protected document writes by this reviewer. |
| Contract | PASS | Required matrices, counterexamples, alternatives, conflict register and approvals are present. No readiness claim exceeds the task. |
| Architecture | PASS | Ordinary admission, read eligibility and trusted semantic proof are separate; identity-changing routing cannot be presumed to grant greater permission; caller transaction and immutable exact history remain protected. |
| Evidence | PASS | Document hashes match feedback; code/frozen/verifier source corroborates the central conflict. Eight durable verifier hashes and prior 05A-R1 acceptance hash match fixed values. |
| File integrity | PASS | Both outputs decode as UTF-8; no CR or trailing whitespace; final LF present. Exact referenced symbols/sections central to this decision were inspected. |
| Task-size / next prompt | PASS | Follow-on is a bounded policy decision, conditional on explicit approval; not a bundled implementation of all twelve outstanding decisions. |

Fresh output hashes:

```text
229e95c52b62d40c9a065ab67d76cd406ca706c0e4ac1e2123d9d9cde9dcd9c8  qualification draft
5510cbfdb3fc13fbaf20f172bd614edbf07ec47983f480b90202ad69eb8158bc  execution report
```

## Counterexample review

| Risk | Static evidence | Verdict |
| --- | --- | --- |
| VERIFIED-only implemented as an alleged existing requirement breaks accepted draft revision | Frozen §12 table lists VERIFIED correction, while durable R1B wiring directly revises newly created UNREVIEWED evidence. Draft explicitly records this conflict. | PASS: conflict not hidden; user decision required. |
| Identity replacement bypasses from-status/latest-prior policy | Candidate revise locks current version but direct replacement loads exact prior without equivalent status/latest checks. Draft documents four paths and proposes route-independent permission. | PASS: unsafe behavior identified, not falsely repaired. |
| Valid metadata/hash is claimed to prove source semantics or freshness | Source/provenance/time matrices explicitly retain raw-byte, source-latest, support-health and time eligibility gaps. | PASS: no invented semantic proof. |
| Terminal exact immutability conflated with automatic rehabilitation permission | Draft distinguishes immutable terminal row from separately approved new-version supersession commands. | PASS: no generic revival authorization. |
| Specification acceptance becomes policy approval | Draft remains NOT_APPROVED; this report accepts only the investigation. | PASS: authority boundary retained. |

## Commands actually executed by this reviewer

- `git status --short --branch` on main/candidate; `git rev-parse HEAD HEAD^` on both; `git diff --exit-code` and `git diff --cached --exit-code` on main: expected baseline and empty tracked/index changes.
- `shasum -a 256` on candidate three files, two outputs, input task contract, prior 05A-R1 acceptance and eight durable verifiers: fixed values match.
- Complete reads of input attachment, task contract, draft and execution report; `rg -n` and targeted `sed -n` on frozen §12/13, candidate correction/replacement/current-valid/provenance/derivation implementations and R1B verifier setup: central observations corroborated.
- Node read-only byte checks on both outputs: UTF-8, LF termination and whitespace checks passed. No absolute Markdown links were present, so this check does not imply exhaustive link validation.
- Final checks on the two new acceptance-turn documents: UTF-8/whitespace/LF and Git tracked/index/scope checks, recorded in the acceptance response.

Final check detail: Node UTF-8/LF/trailing-whitespace checks exited 0 for both new documents. `git diff --no-index --check /dev/null <new-file>` emitted no diagnostics and exited 1 for each (no-index reports differing files; this is not a reported whitespace error). Main `git diff --exit-code` and cached equivalent exited 0. Original two output hashes were rechecked unchanged after these additions.

## Non-blocking findings and verification limits

1. The executor reports chronological protection of 250 governance files via an aggregate digest. This reviewer did not reconstruct an independent before-state list or its serialization. Acceptance relies on independently checked named baseline/protected hashes and current Git scope, not an assertion that all 250 historical paths were independently re-proven.
2. The investigation legitimately remains NOT_READY. More investigation is not a substitute for user policy authority. Narrow the first decision to status/command intent and exact-current prior; do not bundle approval of source, support, windows, conflicts or twelve unrelated choices.
3. No new PostgreSQL result is claimed. Prior 05A-R1 and R1B PASS boundaries stay historical, scoped evidence; this task closes neither implementation qualifications nor R1C.

## Blocking findings / repair

- Blocking specification findings: none.
- Repair required: NO.
- Policy approval required before implementation: YES; this is not a failed delivery.

## Final rationale and next action

PASS closes only `TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1` specification delivery. Its approved scope permits a complete investigation with NOT_READY when authority conflicts remain. The outputs meet that boundary and do not pretend to resolve it.

Recommend Option C for explicit user consideration, narrowed to a first decision package: VERIFIED ordinary correction; UNREVIEWED draft revision; both produce UNREVIEWED with rule None and full CORRECTION tuple; generic pending/disputed/terminal correction rejected; current-highest exact prior across routes; immutable historical reads and existing COMMITTED read-only replay preserved. Public compatibility via existing functions is a proposal, not approval.

Next: `TASK-WP04-02-R1C-05B-POLICY-DECISION-R1`, status `AWAITING_USER_POLICY_APPROVAL`. Only explicit approval of the named package and companion normative document can authorize its docs-only ratification. No business development task is dispatch-ready yet.

Still open: ordinary source/support/window/conflict qualifications, positive trusted rules/registry, R1D request identity/replay/atomicity/concurrency and UNKNOWN_OUTCOME, final WP04-02 independent verification, API/OpenAPI and Research exact references. Sector Crowding and Capability Runtime stay deferred. No Git integration is authorized.
