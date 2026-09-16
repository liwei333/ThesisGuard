# TASK-WP04-02-R1C-05B ordinary correction qualification draft

Task: `TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1`
Evidence date: 2026-09-16, Asia/Shanghai
Document status: **PROPOSED / NOT_APPROVED**
Implementation readiness: **NOT_READY_FOR_IMPLEMENTATION**

This document is a policy investigation. It does not change the frozen Evidence
contract, approve a correction policy, enable a trusted correction rule, qualify
initial direct `VERIFIED` import, or authorize a code task. The production
approved trusted correction set remains empty. The candidate facts cited below
belong to branch `codex/wp04-02-evidence-domain-service` at
`HEAD 0cef44fd2ffd929b40e849e607af0bd4c44d14d2` plus the two already accepted
modified files whose SHA-256 values are recorded in section 1.

## 0. Result and authority legend

The evidence does not yield one authority-consistent ordinary-correction
qualification rule. The frozen state table explicitly authorizes
`VERIFIED -> correct_evidence -> UNREVIEWED`, while an immutable, already
accepted R1B verifier creates a new `UNREVIEWED` exact version and immediately
calls `revise_correct_evidence` for both same-series and automatic replacement
paths. Terminal-version wording permits an append-only `N+1` after a terminal
version but does not identify which correction command, admission conditions, or
replacement-series behavior is legal. Source latest-state and time-window
admission are similarly under-specified.

The result is therefore `NOT_READY_FOR_IMPLEMENTATION`. Section 10 recommends a
narrow policy package, but adopting it requires explicit user approval and a
versioned frozen-contract decision. No follow-on code contract is emitted.

Terms used throughout:

| Label | Meaning |
| --- | --- |
| `FROZEN_REQUIREMENT` | Normative text in `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`. |
| `OBSERVED` | Behavior directly implied by the fixed candidate source at the cited symbol/line. It is not automatically approved policy. |
| `ACCEPTED_REGRESSION_BEHAVIOR` | Behavior exercised by a hash-locked verifier or accepted regression record. It proves compatibility pressure, not normative authority beyond that verifier's scope. |
| `PROPOSED` | A policy option for user approval. It is not active. |
| `CONFLICT` | Two authorities or accepted expectations cannot both be enforced without a decision or versioned amendment. |
| `UNKNOWN` | The inspected sources do not determine the rule. Unknown fails closed for a future admission implementation. |

Cell decisions in the authority matrix mean:

- `ALLOW`: the frozen contract directly authorizes the path and accepted
  behavior is compatible.
- `REJECT`: the inspected authority directly forbids the path.
- `UNRESOLVED`: current code may accept it, but the frozen contract and accepted
  regressions do not uniquely authorize either acceptance or rejection.

## 1. Investigation baseline

The read-only baseline was confirmed before this document was created:

```text
main branch: main
main HEAD: 438738c543e4cae3e805d31324b068c1cd5c7059
main parent: 7d3734bc8346c16f9bbf7f7d9806309949c996de
main tracked/index diff: empty

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

The two candidate modifications are the cumulative accepted R1C candidate, not
changes made by this docs-only task. The main worktree already contained
untracked governance and verifier evidence. It is preserved as historical input,
not promoted to tracked authority by this document.

## 2. Current implementation inventory

### 2.1 Shared facts

- `OBSERVED`: the module declares an immutable empty approved trusted-rule set at
  [`services.py:157`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:157>).
  Ordinary correction therefore means omitted or explicit `None`; it creates
  `UNREVIEWED` and stores `trusted_correction_rule=None`.
- `OBSERVED`: the service has no ordinary-correction from-status predicate. The
  only current status matrix belongs to `_status_command`, not correction, at
  [`services.py:1353`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:1353>).
- `OBSERVED`: database constraints permit a `CORRECTION` row with target
  `UNREVIEWED` or `VERIFIED` and require a predecessor, but do not constrain the
  predecessor's status at
  [`models.py:490`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/models.py:490>).
- `OBSERVED`: mutations use nested savepoints and flush, while the caller owns
  the outer commit. The module states this boundary at
  [`services.py:1`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:1>).

### 2.2 Entry-path inventory

| Entry path | Actual validation and selection order | Target/lineage | Children and audit | Idempotency and transaction | Qualification gaps |
| --- | --- | --- | --- | --- | --- |
| Same-series `revise_correct_evidence` | Locks highest version; checks `expected_version`; validates nullable overrides and replacement child sets; decides routing; calls `_append_status_or_revision`. See [`services.py:851-981`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:851>). | Omitted/`None` rule selects `UNREVIEWED`; creates `N+1`; exact predecessor is locked current. | Copies locators, creates new immutable instrument/derivation children, emits `EVIDENCE_CORRECTION`; complete row tuple has `CORRECTION`, actor, time and reason at [`services.py:1475-1551`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:1475>). | Replay is checked inside append only after current lock and expected-version check. It flushes and records one operation key in the caller transaction. | No from-status check. Same-series signature cannot replace source version or locators despite the frozen correction contract allowing those changes. Provenance, manual ownership, source latest/status and windows are not requalified. |
| Automatic identity-changing route | The same public revise path detects only DERIVED support-ID set or CROSS_INSTRUMENT member-ID set changes at [`services.py:1699-1718`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:1699>), then calls direct replacement with the locked current exact at [`services.py:920-964`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:920>). | Ordinary result is a new series version 1, `UNREVIEWED`, exact `supersedes` current. | New version gets new children. Accepted route taxonomy records `EVIDENCE_VERSION_CREATED` for the version plus `EVIDENCE_SERIES_CREATED`, while the row retains a complete `CORRECTION` tuple. | Uses an inner create key and an outer replacement key in one caller transaction. | Inherits revise's absent from-status rule. It cannot route changes to other identity dimensions because revise does not expose them. Qualification of new supports is existence/cycle based, not current-valid based. |
| Direct `create_replacement_evidence_series` | Reads caller-supplied exact prior without locking or latest check; loads its series; derives new identity and requires it differ; checks replay; validates display/trusted input; calls lower create. See [`services.py:1103-1255`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:1103>). | Ordinary result is replacement series v1, `UNREVIEWED`, `supersedes=prior exact`. | Lower create builds new children and emits `EVIDENCE_SERIES_CREATED` plus `EVIDENCE_VERSION_CREATED`. | Direct request hash includes prior ID, new identity, title, text and three audit values, but omits many value/provenance/window/child fields. Outer and inner keys are recorded in the caller transaction. | No prior-current, prior-status or expected-version check. A terminal or stale exact prior can currently be replaced. Qualification-field changes omitted from the request hash may borrow a committed replay; that broader defect is R1D. |
| Underlying `create_evidence_series_version` with predecessor | Validates identity/provenance/children, computes a series hash and checks replay; then trusted/display and initial-import gates; ordinary predecessor forces `UNREVIEWED`; constructs the new series/version. See [`services.py:565-845`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:565>). | Can create a replacement-like v1 with any supplied predecessor FK. Ordinary predecessor is `UNREVIEWED` and retains the supplied complete tuple. | Creates all submitted children and emits series/version-created events. | Records one lower-create key; request hash omits several machine, effective-window, audit and actor fields. Caller commits. | Does not load, lock, require latest, inspect status or prove ownership of the predecessor. It does not prove that the new identity differs from the predecessor's series. It is therefore a public bypass for any future from-status rule unless guarded too. |

### 2.3 Current source, provenance and time behavior

- `OBSERVED`: `_validate_provenance` checks information/provenance compatibility,
  exact source-version existence and lineage, SourceType/SourceGrade compatibility,
  at least one locator, and locator structure at
  [`services.py:2028-2112`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:2028>).
  It does not require the exact source version to be latest or `ACTIVE`.
- `OBSERVED`: latest source lookup is not used by correction admission. Source
  version identity deliberately changes for same bytes plus grade, metadata,
  parser output, or lifecycle changes under frozen §8.
- `OBSERVED`: `get_current_valid_evidence` accepts only `VERIFIED` Evidence and
  excludes an exact source version whose status is `RETRACTED`; it does not check
  `SUPERSEDED`, source-lineage latest, grade, `effective_from`, or `effective_to`
  at [`services.py:1316-1329`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:1316>).
- `OBSERVED`: period and effective ordering are database constraints at
  [`models.py:384-390`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/models.py:384>).
  The service does not reject invalid ordering explicitly before ORM construction
  or flush. `as_of` is required but has no relation to command time. Correction
  accepts arbitrary supplied `status_changed_at` and also stores it as
  `created_at`.
- `OBSERVED`: DERIVED support validation proves exact IDs exist, roles are valid,
  duplicates/self/cycles are absent, at
  [`services.py:2457-2528`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:2457>).
  It does not require supports to be latest, `VERIFIED`, current-valid, unexpired,
  or backed by an active latest source.
- `OBSERVED`: corroboration/conflict relations are exact-version links created by
  a separate command at
  [`services.py:1278-1313`](</Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service/backend/evidence/services.py:1278>).
  Correction does not copy or evaluate them.

## 3. Frozen requirement map

| Frozen section | Requirement | Consequence for this draft |
| --- | --- | --- |
| §6 and §8, lines 121-160 and 229-314 | Exact immutable source/evidence versions; ten series identity dimensions; same-lineage newer source version can remain in one series; identity change creates a new series; current-valid reads latest first. | Same-series and replacement differ structurally but must share exact predecessor and append-only rules. Source exact and source latest are distinct concepts. |
| §9-§11 | FACT is SOURCE_BACKED; external ESTIMATE is source-backed; THESIS_INFERENCE is DERIVED; USER_HYPOTHESIS is user MANUAL; complete SourceType/SourceGrade pairs apply. | Correction cannot erase the provenance-specific qualification. Grade/type labels are structural checks, not semantic proof. |
| §12 state table, lines 447-516 | Only `VERIFIED -> correct_evidence -> UNREVIEWED` is explicitly listed. Replacement uses a prior exact and may target UNREVIEWED/VERIFIED. Terminal rows are immutable; a new version may supersede a terminal row only by appending `N+1`. | `VERIFIED` ordinary correction is authoritative. UNREVIEWED regression and terminal append wording create unresolved command semantics. The replacement row omits a from-status rule. |
| §12 audit, lines 468-489 | Every correction/replacement has an all-non-null four-field tuple and `CORRECTION`. | Preserve this across all paths. It does not itself authorize a from-status. |
| §13 correction, lines 536-560 | Ordinary correction is `UNREVIEWED`; same identity appends; changed identity creates replacement v1; old exact references remain. | Target and lineage are settled. Admission of non-VERIFIED states is not. |
| §13 source retraction, lines 587-616 | Source withdrawal is represented by source lifecycle state and an Evidence retraction is a separate append. | A source notice must not silently rewrite exact history. Whether an ordinary correction may proceed while latest source is non-ACTIVE remains unstated. |
| §14-§16 | `as_of` is claim truth/evaluation time; exact source/locator lineage; same bytes plus metadata/grade/status yields a new SourceDocumentVersion; DERIVED support-set and CROSS_INSTRUMENT member-set changes are identity changes. | Hash equality is not source-version equality. Structural source and child rules must be rechecked on every new row. |
| §21 model constraints, lines 1193-1238 | Period/effective ordering, provenance constraints, full correction tuple, immutable rows. | Invalid ordering is always rejectable. Expired/future windows and monotonic command time are not decided here. |
| §22 command blueprint, lines 1403-1432 | Revise requires expected version and routes identity changes; direct replacement requires an exact prior and full tuple; old row/series/children stay immutable. | Blueprint does not state direct prior must be latest or identify its allowed status. |
| §23 error blueprint | Stale expected version uses `EVIDENCE_VERSION_CONFLICT`; illegal status uses `EVIDENCE_INVALID_STATE_TRANSITION`; structural provenance/locator/grade errors have stable codes. | A future policy should reuse these codes with precise details rather than introduce free-form errors. |
| Examples 25, 37-42 | Examples start correction/replacement from current `VERIFIED`; DERIVED support-set change routes replacement; old history/children stay intact. | Examples support VERIFIED positive behavior but do not resolve other states. |

## 4. Accepted verifier and regression behavior map

| Evidence | Accepted behavior | Limit |
| --- | --- | --- |
| [`test_wp04_02_r1b_r1_wiring_20260915.py:41-79`](</Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1b_r1_wiring_20260915.py:41>) | Creates a default `UNREVIEWED` DERIVED v1, then calls revise for same-series and changed-support replacement. This is the known conflict. | It verifies exact-target derivation validation wiring. It never states a correction from-status policy. |
| [`test_wp04_02_r1b_reverify.py:30-99`](</Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1b_reverify.py:30>) | Changes the support set of a default `UNREVIEWED` DERIVED v1 and expects a replacement v1. | It tests exact graph semantics and routing, not lifecycle authorization. |
| [`test_wp04_02_r1c_01_independent_20260915.py:27-94`](</Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c_01_independent_20260915.py:27>) | Ordinary correction from a historical `VERIFIED` row produces `UNREVIEWED`; latest-first read does not fall back. | Other from-status corrections are not exercised. |
| [`test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py:126-205`](</Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py:126>) | Builds a lawful alternate VERIFIED support through ordinary correction, review and verification; no self/cycle. | Setup correction starts from VERIFIED. |
| [`test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py:420-503`](</Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py:420>) | Ordinary omitted/None from a VERIFIED legacy exact works on same, automatic, direct and underlying predecessor routes; result is UNREVIEWED/rule None with exact predecessor/history/children and strict route-owned audit. | It does not authorize terminal, disputed, pending, rejected or stale-prior correction. |
| R1C-02 acceptance §2 | Four status commands implement their explicit state table and use `EVIDENCE_INVALID_STATE_TRANSITION` elsewhere. | R1C-02 explicitly excludes ordinary-correction qualification. |
| R1C-03B acceptance, “Findings and next selection” | Warns against immediately enforcing global VERIFIED-only because the R1B UNREVIEWED fixture would fail. | It accepts the need for this decision; it does not make the decision. |
| R1C-04A acceptance | Preserves body admission, five route families, exact history and replay. | It explicitly leaves ordinary source/from-status/window policy open. |
| R1C-05A-R1 acceptance, “Findings” | Initial direct VERIFIED is fail closed; replay tuple conflicts are closed. | It explicitly names ordinary from-status/source-state/window policy as unresolved. |

Accepted audit mapping to preserve is path-specific: same-series exact version event
`EVIDENCE_CORRECTION`; automatic, direct, and underlying replacement exact version
event `EVIDENCE_VERSION_CREATED`, with a new-series event where applicable. In all
cases the persisted version tuple remains `CORRECTION` with exact predecessor,
actor, time and reason. This mapping comes from the R1C-03A oracle and is not a
license to accept arbitrary event types.

## 5. Seven-status by correction-path authority matrix

This table states what can be concluded **before** user approval. Replacement
means both automatic and direct/underlying identity-changing correction. Direct
replacement also has a separate latest-prior gap in section 8.

| Current prior status | Same-series | Replacement series | Frozen basis | Current code | Accepted behavior | Risk and stable reject behavior | Decision required |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `UNREVIEWED` | **UNRESOLVED** | **UNRESOLVED** | §12 does not list correction from UNREVIEWED; §13 only says result is UNREVIEWED. | All routes accept it because no from-status check exists. | R1B fixed wiring accepts same-series and automatic replacement from a new UNREVIEWED exact. | Allowing it supports draft repair but conflates `correct_evidence` with draft revision and can churn unreviewed versions. Rejecting should use `EVIDENCE_INVALID_STATE_TRANSITION` with `from_status=UNREVIEWED`, `requested_status=UNREVIEWED`, and `command=ordinary_correction`. | Decide whether this is a legitimate “draft revision,” a faulty R1B fixture, or a frozen-contract amendment. Decide whether originals remain mandatory and add a successor verifier. |
| `PENDING_REVIEW` | **UNRESOLVED** | **UNRESOLVED** | State table permits review decision, not correction. No text says whether editing cancels an active review. | Accepted today. | No fixed correction verifier starts here. | Acceptance can invalidate the review target and reviewer intent. Conservative rejection uses `EVIDENCE_INVALID_STATE_TRANSITION` with from/requested/command. | Decide whether correction cancels review, requires explicit cancellation, or is prohibited. |
| `VERIFIED` | **ALLOW** | **ALLOW** | §12 explicitly lists ordinary correction from VERIFIED; §13 and examples 25/40/42 specify same/replacement results. | Accepted today. | R1C-01, R1C-03A oracle and R1C-04A exercise it. | Still subject to current/latest prior, provenance, source, children, time, complete tuple and idempotency rules. | No from-status decision needed; remaining qualification dimensions still need approval. |
| `REJECTED` | **UNRESOLVED** | **UNRESOLVED** | Terminal row cannot be changed; §12 says a new version may supersede terminal only by N+1, but the transition table has no correction command from REJECTED and replacement is v1 in a new series. | Same-series, direct and underlying currently accept. | No accepted correction verifier starts here. | A generic correction could bypass review rejection and create endless rehabilitation attempts. Conservative rejection uses `EVIDENCE_INVALID_STATE_TRANSITION`. | Decide whether terminal rehabilitation exists, whether it is same-series only, and which actor/reason/evidence are required. |
| `DISPUTED` | **UNRESOLVED** | **UNRESOLVED** | §12 provides explicit dispute resolution to VERIFIED/REJECTED and retraction; no ordinary correction row. | Accepted today. | No accepted correction verifier starts here. | Ordinary correction could bypass dispute resolution/audit ownership. Conservative rejection uses `EVIDENCE_INVALID_STATE_TRANSITION`. | Decide whether corrected content is only legal through `resolve_dispute_*`, and whether identity change needs a dedicated disputed-replacement command. |
| `INVALIDATED` | **UNRESOLVED** | **UNRESOLVED** | Terminal; append-only supersession wording exists, but no correction transition is named. | Accepted today. | No accepted correction verifier starts here. | Could revive expired/disproved evidence without a distinct rehabilitation decision. Conservative rejection uses `EVIDENCE_INVALID_STATE_TRANSITION`. | Decide whether correction of an invalidated claim is allowed, or must be a new observation/series with explicit rehabilitation policy. |
| `RETRACTED` | **UNRESOLVED** | **UNRESOLVED** | Terminal; exact history remains, but no correction transition is named. | Accepted today. | No accepted correction verifier starts here. | Could reintroduce withdrawn evidence while its source remains retracted. Conservative rejection uses `EVIDENCE_INVALID_STATE_TRANSITION`. | Decide whether any source/domain retraction can be superseded, and require source-reactivation evidence if so. |

There is no authority-backed `REJECT` cell because the terminal clause forbids
in-place promotion while also allowing some append-only supersession, and the
contract does not bind that permission to a command. Treating omission from the
transition table as an unconditional rejection is a plausible policy option, not
a fact this executor may approve.

### Known VERIFIED-only conflict

Classifying only `VERIFIED` as allowed follows the literal transition row and the
frozen examples. It would make these accepted fixed verifier nodes fail before
their exact-target assertions:

- R1B wiring `same_series_revision`;
- R1B wiring `replacement`;
- R1B reverify `test_replacement_can_support_prior_exact_version_without_exact_cycle`.

The fixed files cannot be edited. If the user approves VERIFIED-only, the policy
decision must state whether those cases were fixture defects and issue a
successor verifier that constructs a legitimately VERIFIED prior while preserving
the original exact-target, routing and cycle assertions. The original verifier
would remain historical evidence and would no longer be part of the new policy's
green matrix only through an explicit versioned verifier contract.

If the user approves UNREVIEWED, the frozen contract must define this as a draft
revision: it remains UNREVIEWED, cannot become current-valid, retains complete
`CORRECTION` audit, uses the current highest exact version, and cannot use a
trusted rule. That addition needs a frozen-contract amendment or ADR and a
successor verifier that tests the full state boundary, not only derivation wiring.

## 6. Source and provenance qualification matrix

The table separates structural admission, ordinary-correction admission,
current-valid eligibility, and trusted-only semantics. “Proposed” entries are
not active.

| Dimension | Authoritative data | Structural rule already frozen/observed | Proposed ordinary admission | Current-valid boundary | Trusted-only boundary | Failure and test example |
| --- | --- | --- | --- | --- | --- | --- |
| `SOURCE_BACKED` exact source version | Evidence prior/new payload, SourceDocumentVersion FK, primary SourceDocument lineage | Exact version must exist, belong to primary lineage, have a legal type/grade pair, and have locator(s). | Require the selected exact source version to equal the lineage's latest version at command time and be `ACTIVE`; a source change must be explicit and revalidate locators. This proposal exceeds current same-series signature. | Latest Evidence must be VERIFIED; recommended query also evaluates source-lineage latest state. | Trusted additionally needs byte-bound semantic proof; grade/hash/parser labels are insufficient. | Old exact ACTIVE but a newer source version exists: proposed stable `EVIDENCE_INVALID_PROVENANCE`, `validation_path=source_document_version_id`, `reason=source_version_not_latest`. |
| Latest source `ACTIVE` | Latest SourceDocumentVersion in primary lineage | Lifecycle tuple must be all-null. | Proposed prerequisite for a new correction row. | Eligible subject to Evidence status/time/role. | Necessary, never sufficient. | Exact old v1 is ACTIVE, latest v2 ACTIVE: require v2 and its locator, not v1. |
| Latest source `RETRACTED` | Latest source row and its complete lifecycle tuple | Retraction remains exact history; affected Evidence lifecycle append is separate. | Proposed reject; ordinary correction cannot reactivate a withdrawn source. | Unavailable. Current code only checks the exact cited source's status and can miss a later retraction. | Reject. | Latest v2 RETRACTED while prior cites v1 ACTIVE; expect provenance/retracted-reference error before writes. Exact old reads still work. |
| Latest source `SUPERSEDED` | Latest source row | Valid source lifecycle value but no ordinary-correction rule is frozen. | Proposed reject until an ACTIVE successor exact is selected and re-located. | Proposed unavailable for new downstream use. Current code does not exclude it. | Reject unless a future rule explicitly validates the successor. | Latest v2 SUPERSEDED; old v1 correction must not create a new row. |
| Same bytes, new SourceDocumentVersion | `content_hash`, `version_fingerprint`, all fingerprint fields | Same bytes plus grade/metadata/parser/status changes create a distinct exact version under §8/§16. | Treat as a real version change. Require the latest exact and do not collapse by `content_hash`. | Query may expose changed grade/status; proposed eligibility uses latest state. | Revalidate byte/artifact and semantics. | v1/v2 share bytes but v2 has grade/status/metadata change; correction citing v1 fails latest check. |
| SourceType/SourceGrade | SourceDocument type and exact source-version grade; §11 matrix | Pair must be listed; new Evidence snapshots exact grade. | Preserve/recompute exact snapshot. Do not use grade as proof of fact. F-grade remains unverified intelligence only under §10. | Role policy must reject F as core support; generic current-valid grade policy remains incompletely implemented. | Trusted cannot infer truth from S/A grade. | Legal S report with wrong extracted value still needs ordinary review; illegal pair uses `EVIDENCE_INVALID_SOURCE_GRADE`. |
| Locator lineage | New exact source version plus locator rows/parser metadata | Locator version must equal Evidence source exact and lineage; coordinates checked where metadata exists. | Revalidate all prospective locator children. Copying is allowed only if source exact is unchanged and latest-active policy passes. | Exact history keeps old locators; current-valid examines the latest Evidence row. | Trusted must bind locator to source bytes and claim semantics. | Source v2 selected but locator still points to v1: `EVIDENCE_INVALID_SOURCE_LOCATOR`, no residue. |
| `MANUAL` | Series origin, prior/new Evidence fields, actor, reason, observed time | No SourceDocumentVersion, grade or locator. USER_HYPOTHESIS and manual ESTIMATE have user/manual metadata rules. | Revalidate information type, actor ownership, nonblank reason and observed time on every new row; do not let correction actor silently change semantic authorship. Whether non-USER may correct user manual evidence requires approval. | VERIFIED-only plus role/time policy; no fabricated grade. | A future trusted correction requires a separate manual semantic authority; none exists. | USER_HYPOTHESIS corrected by IMPORTER currently reaches DB constraints rather than a clear admission error; proposed `EVIDENCE_INVALID_PROVENANCE`. |
| `DERIVED` | Exact support IDs and immutable derivation links | At least one exact support; valid roles; no duplicate/self/cycle. Support-set change changes `origin_key` and routes replacement; metadata-only changes stay same series. | Preserve those rules. Whether every support must be latest/current-valid at command time is **UNRESOLVED** and needs user approval. Conservative option requires all supports current-valid; historical-analysis option permits exact historical supports but keeps result unreviewed. | Derived row itself must be latest VERIFIED; downstream role may also need support health, not currently implemented. | Trusted requires deterministic derivation and semantic proof for every support. | V1+V2 -> V1+V3 must route replacement. A support latest RETRACTED is a separate unresolved admission counterexample. |
| `CROSS_INSTRUMENT` | Instrument table, exact instrument children, canonical sorted member hash | At least one member; IDs exist; member-set change changes scope and routes replacement; role/order/metadata-only changes may append. | Revalidate all members and primary-scope semantics. From-status policy must be identical for same and replacement. | Latest VERIFIED/time/source policy; no member-set fallback. | No trusted policy is approved. | A+B -> A+C routes replacement; stale/unknown instrument rejects before writes. |
| Corroboration/conflict links | Exact `EvidenceCorroborationLink` rows and relation types | Links are immutable exact-version relations; self/duplicate invalid. | **UNRESOLVED**: current correction neither copies nor evaluates links. Recommended fail closed when prior has `CONFLICTS_WITH`; do not treat `CORROBORATES` as truth. Decide whether relations must be reasserted for the new exact version. | Query should surface conflicts; generic current-valid conflict policy is absent. | Trusted must resolve rather than ignore conflicts. | Prior exact has CONFLICTS_WITH then gets corrected; current code creates a new row with no relation. Policy must decide whether reject or require explicit new links. |

The proposed latest-`ACTIVE` rule is the narrowest protection against reviving a
retracted or superseded source, but it is not uniquely compelled by the frozen
text. It also exposes a real implementation gap: same-series revise cannot submit
a newer source version or a new locator. Approval should therefore separate
policy from the later signature/implementation slice.

## 7. Time qualification matrix

| Field/condition | Frozen meaning | Current behavior | Proposed correction admission | Current-valid behavior | Error/test |
| --- | --- | --- | --- | --- | --- |
| `period_start <= period_end` | Series identity and Evidence snapshot ordering constraint. Changing either is an identity change. | Database check only; direct/lower create may construct rows before flush failure. Revise cannot change period. | Reject explicitly before prospective ORM attachment. Route any permitted period change to replacement. | Exact history unaffected. | `EVIDENCE_VALIDATION_ERROR`, `validation_path=period`, `reason=invalid_period_order`; caller commit/fresh no-residue. |
| `effective_from <= effective_to` | Evidence validity ordering constraint; not a series identity dimension. | Database check only. Revise can override either. | Reject explicitly before construction. A legal change remains ordinary and therefore UNREVIEWED. | Query should evaluate window separately. | `EVIDENCE_VALIDATION_ERROR`, `validation_path=effective_window`, `reason=invalid_effective_order`. |
| `effective_to` already passed at command time | Frozen §13 describes expiry through INVALIDATED, but does not state ordinary correction admission. | Correction accepts; current-valid still returns VERIFIED if exact source is not retracted. | Permit storage correction only as UNREVIEWED if from-status policy permits; do not regain eligibility by omission or inherited VERIFIED. Whether the prior should first be invalidated is a user decision. | Proposed unavailable when evaluation time is after `effective_to`. | Test correction preserves history but current-valid returns none at explicit query time. Query API currently lacks evaluation-time input. |
| `effective_from` in future | Valid future-dated evidence is representable. | Correction accepts; current-valid ignores the future boundary. | Permit UNREVIEWED correction; do not treat it as currently eligible. | Proposed unavailable until the boundary. | Future window test needs a deterministic evaluation time, not wall-clock sleep. |
| `as_of` | Claim truth/evaluation time, required and distinct from observed/fetched/command times. | Required non-null; revise may inherit or replace; no relative checks. | Preserve exact value when omitted. Explicit changes require ordinary review and provenance support but are not automatically invalid because they differ from command time. | Role freshness policy is separate and unresolved. | Same source with `as_of` changed must not borrow same key; current request hashes do not fully protect all paths. |
| `status_changed_at` | Required for every correction tuple. | Caller supplies any datetime; it is also assigned to new row `created_at`. No timezone, monotonic or future check. | Require aware UTC-normalizable input, non-null, not before the predecessor's append time. Allowable clock skew/future bound needs user approval. | Audit/exact read uses recorded value; it does not establish claim validity. | Proposed `EVIDENCE_VALIDATION_ERROR`, `validation_path=status_changed_at`. Backdated and naive timestamps are counterexamples. |
| Correction command time | Domain event/commit context, distinct from claim `as_of` and effective window. | No explicit parameter besides `status_changed_at`; actual DB commit may happen later. | Define command time as validated `status_changed_at` for deterministic policy, while retaining caller-owned commit. Decide acceptable skew. | Used as the eligibility evaluation point only if API explicitly requests it; otherwise query needs its own evaluation time. | User must approve time ownership and skew. |
| Prior exact is not latest | Exact old rows remain readable. Revise uses current plus expected version; direct replacement blueprint only says “prior exact.” | Revise rejects stale `expected_version`; direct and lower create accept an old exact prior. | Require prior exact to be current highest for both paths. Use `EVIDENCE_VERSION_CONFLICT` with expected/current versions. Historical correction requires a separately named command if desired. | Exact old reads remain available; no fallback. | Direct replacement of v1 after v2 exists must fail before new series/key/audit. |
| Exact historical read | Exact version returns its committed snapshot forever. | Implemented by exact ID. | Never mutate or hide historical rows because current admission changes. | Does not apply current-valid filters. | After any rejection/success, old exact and children compare all columns unchanged. |
| Current-valid read | Highest Evidence version first; no fallback. | VERIFIED-only and exact-source RETRACTED check. No window/latest-source/SUPERSEDED check. | Separate from ordinary storage permission. | Proposed evaluate Evidence status, requested role, effective window, latest source state, and unresolved grade/conflict/support policy. | This requires a later read-eligibility slice, not silent addition to correction admission. |

## 8. Contract-versus-regression conflict register

| ID | Conflict | Classification | Required resolution |
| --- | --- | --- | --- |
| C-01 | Frozen `VERIFIED -> correct_evidence -> UNREVIEWED` versus accepted R1B revise from new UNREVIEWED exact. | `CONFLICT`: contract omission plus accepted fixture/compatibility behavior. | User chooses fixture defect/VERIFIED-only or adds explicit UNREVIEWED draft-revision semantics through ADR/frozen amendment. Successor verifier required either way; old verifier remains immutable. |
| C-02 | Terminal append clause permits `N+1`, but no ordinary correction transition from REJECTED/INVALIDATED/RETRACTED; replacement is a different series v1. | `CONFLICT`/`UNKNOWN`. | Specify a dedicated rehabilitation command and paths, or explicitly reject generic correction from terminal states. |
| C-03 | Direct replacement accepts any exact prior; revise requires locked current/expected version. | `OBSERVED` divergence; frozen blueprint is ambiguous. | Approve one consistent ownership rule. Recommendation: current-highest exact for both; historical replacement is a distinct future command. |
| C-04 | Frozen correction permits newer SourceDocumentVersion/locator changes in the same series, but revise exposes neither input. | Implementation gap, not policy authority. | After source/latest policy approval, dispatch a separate signature/validation slice. Do not overload support-set replacement. |
| C-05 | Exact source version is required, while source-lineage latest/status admission is unspecified; current-valid checks only exact RETRACTED and misses SUPERSEDED/later notices. | Contract gap plus partial implementation. | User approves latest-`ACTIVE` admission/query policy or explicitly permits historical source correction. |
| C-06 | Effective windows are stored and ordered, but current-valid ignores expiry/future. | Accepted R1C-01 scope intentionally deferred freshness. | Define deterministic query evaluation time and role policy in a later slice. Do not conflate it with exact reads. |
| C-07 | `_validate_provenance` runs for lower create/direct replacement, but same-series append copies fields without revalidation. | Observed asymmetric enforcement. | Future implementation must requalify the prospective complete snapshot through shared validation before writes. |
| C-08 | Manual initial admission validates actor/reason/time; same-series correction can change row actor without calling that validator. | Observed bypass. | Define manual correction ownership and revalidate on every append. |
| C-09 | DERIVED validation checks exact graph structure but not support eligibility/source state/time; correction policy is silent. | `UNKNOWN`. | Approve current-valid supports versus exact historical supports for each use case. |
| C-10 | Conflict/corroboration links stay attached to old exact versions and are neither copied nor evaluated for the new version. | `UNKNOWN`. | Define relationship carry-forward/reassertion and conflict blocking semantics. |
| C-11 | Same/direct/lower-create request hashes omit different qualification-relevant fields; direct/lower replay can return an old response when an omitted field changes. | Known R1D boundary. | Preserve as a disclosed blocker; fix only under R1D aggregate-complete hash/replay contract. Qualification enforcement must run before unsafe replay or have versioned hash compatibility. |
| C-12 | Underlying create with predecessor does not validate predecessor existence/current/status/identity ownership in service code. | Public bypass. | Any future policy must guard this entry or make it private under a separate authorized API contract. |
| C-13 | Frozen D-15 says the domain service “owns validation and commits”; accepted architecture and current module use caller-owned commit. | Wording ambiguity resolved operationally by cumulative accepted behavior. | Preserve caller-owned outer transaction unless a separate architecture change is approved. Do not alter it in qualification work. |

## 9. Required counterexamples

| Counterexample | Current observed result | Authority-consistent expected result today | Policy evidence needed |
| --- | --- | --- | --- |
| Ordinary correction from each of seven statuses | Code accepts all if other fields/constraints pass. | VERIFIED is allowed; other six are unresolved and must fail closed in any implementation until approved. | C-01/C-02 decisions and successor matrix verifier. |
| Stale `expected_version` on revise | `EVIDENCE_VERSION_CONFLICT` before append. | Preserve. | None. |
| Direct `prior_evidence_version_id` is not latest | Accepted if exact exists and new identity differs. | Proposed reject with `EVIDENCE_VERSION_CONFLICT`. | Approve current-highest ownership for direct replacement and add expected/current detail semantics. |
| Latest source version is RETRACTED | Old exact ACTIVE source can still pass correction admission; generic current-valid may miss later retraction. | Proposed reject new correction; exact history remains readable. | Approve latest-source admission/query rule. |
| Latest source version is SUPERSEDED | Admission and current-valid can accept the old exact. | Proposed reject until an ACTIVE successor exact is selected and located. | Approve SUPERSEDED meaning for Evidence use. |
| Same bytes but SourceDocumentVersion changed | `content_hash` may match while fingerprint/version differs; same-series revise cannot select the newer version. | Never collapse by bytes; proposed latest exact is required. | Source correction signature and validator contract. |
| `effective_to` expired | Correction accepted; current-valid ignores expiry. | Storage correction may remain UNREVIEWED; current-valid should be unavailable. | Approve query evaluation time and whether invalidation is mandatory first. |
| `effective_from` is future | Correction accepted; current-valid ignores future boundary. | Store only under ordinary policy; unavailable until effective. | Same time/query decision. |
| Period/effective order is invalid | Database constraint eventually fails, commonly surfaced as persistence conflict. | Explicit validation error before prospective write construction/key/audit. | Stable details and focused no-residue verifier. |
| DERIVED support set changes | Automatic replacement by changed `origin_key`; exact graph checks run. | Preserve routing. Support eligibility at command time remains unresolved. | Approve historical versus current-valid support policy. |
| Terminal exact is direct replacement prior | Accepted today. | Fail closed pending terminal rehabilitation decision. | C-02 plus path-specific command and audit decision. |
| Same idempotency key, qualification field changes | Depending on path and field, conflict, expected-version failure, or old response replay; hashes are incomplete. | Never let changed source/window/status qualification borrow a response. | R1D versioned hash and replay-order contract; do not patch ad hoc here. |

## 10. Policy alternatives and recommendation

### Option A — literal VERIFIED-only ordinary correction

Rules:

1. Same-series and all replacement paths allow only a current-highest VERIFIED
   prior.
2. All other statuses reject with `EVIDENCE_INVALID_STATE_TRANSITION`.
3. Terminal rehabilitation, draft revision and disputed correction are separate
   future commands.

Benefits: closest to the explicit frozen transition row; small admission
predicate; strongly fail closed. Costs: breaks three accepted R1B verifier nodes;
forces users to request review and verify a draft before correcting it; requires
an explicit successor-verifier contract or a frozen statement that those old
fixtures no longer define expected behavior.

### Option B — all nonterminal statuses can be ordinarily corrected

Rules:

1. UNREVIEWED, PENDING_REVIEW, VERIFIED and DISPUTED may append an ordinary
   UNREVIEWED correction or replacement.
2. REJECTED, INVALIDATED and RETRACTED reject.
3. A correction implicitly cancels an active review/dispute.

Benefits: preserves R1B and supports iterative drafting. Costs: the implicit
review/dispute cancellation has no frozen audit command; it weakens the explicit
state machine, makes reviewer ownership ambiguous, and can bypass dispute
resolution. This option is not recommended.

### Option C — split ordinary correction from explicit draft revision

Proposed rules:

| Prior | Same-series | Replacement | Meaning |
| --- | --- | --- | --- |
| VERIFIED | ALLOW ordinary correction | ALLOW ordinary replacement | Frozen `correct_evidence`; target UNREVIEWED. |
| UNREVIEWED | ALLOW only as `draft_revision` semantics | ALLOW only as draft identity replacement | Preserves R1B; target remains UNREVIEWED; no trusted rule; complete CORRECTION audit; current-highest exact required. |
| PENDING_REVIEW | REJECT | REJECT | An active review target cannot be silently replaced; an explicit cancel/reject command is needed first. |
| DISPUTED | REJECT | REJECT | Use dispute resolution or a future dedicated corrected-dispute command. |
| REJECTED | REJECT | REJECT | Terminal rehabilitation requires a separately approved command. |
| INVALIDATED | REJECT | REJECT | Do not revive expired/disproved evidence through generic correction. |
| RETRACTED | REJECT | REJECT | Do not revive withdrawn evidence through generic correction. |

This is the recommended policy package **for user consideration**. It is narrow,
preserves the legitimate R1B need to refine an unreviewed derived graph, and does
not let pending/disputed/terminal states bypass their explicit lifecycle
commands. It must use the same status rule for same-series and replacement so
identity changes cannot increase permission. Direct and underlying replacement
must additionally require that the exact prior is the current highest version.

Option C is not ready to implement because it adds `draft_revision` semantics
absent from the frozen contract, needs a decision on public command naming versus
temporary compatibility through `revise_correct_evidence`, and still depends on
the source/latest, manual ownership, derived-support, relationship and time
decisions below.

## 11. Proposed qualification layers if Option C is approved

The following order prevents a lower-level route from bypassing policy. It is a
design proposal, not current behavior:

1. Resolve operation and exact prior. For every correction route, require a
   current-highest predecessor and compare expected/current versions.
2. Apply the approved from-status/command-intent matrix. Fail with
   `EVIDENCE_INVALID_STATE_TRANSITION` before prospective row construction.
3. Build the complete prospective snapshot in memory without attaching it to the
   session.
4. Validate identity and route. Same identity means N+1; changed identity means
   replacement v1 with exact predecessor. Permission cannot differ by route.
5. Revalidate provenance and all mandatory children for the prospective row.
6. Apply approved latest-source/status and manual/derived/cross-instrument rules.
7. Validate period/effective ordering and approved command-time semantics.
8. Apply display-text and empty trusted-rule rules already accepted. Ordinary
   always targets `UNREVIEWED` with rule `None`.
9. Perform idempotency under the separately approved R1D hash/replay policy.
10. Construct/attach rows, flush, write operation-owned idempotency/audit, and
    leave the outer commit to the caller.

Admission, read eligibility and trusted verification remain distinct:

- Ordinary admission decides whether an append-only unreviewed correction may be
  stored.
- Current-valid decides whether the latest exact version is eligible at an
  evaluation time and role. Ordinary correction is never current-valid until a
  legal review produces VERIFIED.
- Trusted admission would additionally prove source/locator/semantic truth in one
  transaction. No such positive rule is approved.

## 12. Compatibility and migration impact

- Existing rows need no rewrite or backfill. Exact historical reads, old rules,
  source snapshots, locators and children remain immutable.
- Enforcing any from-status rule changes currently fail-open command behavior.
  Clients that correct PENDING_REVIEW, DISPUTED or terminal evidence would begin
  receiving stable domain errors.
- Option A breaks the named R1B verifier nodes. Option C preserves their intended
  graph/routing behavior but requires the frozen contract to name draft-revision
  semantics and a successor verifier to assert the full state boundary.
- Direct replacement would gain a current/latest requirement and probably an
  expected-version argument or equivalent locked comparison. That is a public
  domain signature decision for a later contract.
- A latest-`ACTIVE` source rule makes same-series source correction impossible
  with the current revise signature when a newer source version exists. A later
  bounded signature/validator slice is necessary; it must not mutate the schema.
- Window-aware current-valid needs a deterministic evaluation-time input or
  policy; this belongs to a read-eligibility slice, not a hidden correction
  change.
- Existing idempotency records and hashes must remain readable. New
  qualification-relevant fields cannot simply be added to old hashes without a
  versioned R1D compatibility plan. No hash migration is approved here.
- Fixed historical verifiers remain byte-identical. Any changed normative policy
  uses an independently named successor verifier; it never rewrites old evidence.

## 13. User approvals required

Implementation remains blocked until the user explicitly approves all decisions
that affect the intended first code slice:

1. Choose Option A, B, C, or a precise alternative.
2. If Option C, approve `UNREVIEWED` draft-revision semantics, its audit kind,
   target status, current-highest requirement, and whether it stays behind the
   existing public function or gets a distinct command.
3. Decide whether same-series and replacement always share one from-status rule.
   Recommendation: yes.
4. Decide terminal rehabilitation policy. Recommendation: generic ordinary
   correction rejects; a later named command is required.
5. Decide whether direct/underlying replacement must target the current-highest
   exact prior. Recommendation: yes.
6. Approve or reject latest-`ACTIVE` SourceDocumentVersion as ordinary admission.
   Specify RETRACTED and SUPERSEDED handling and same-bytes/new-version behavior.
7. Define MANUAL correction actor/ownership semantics.
8. Define DERIVED support qualification: exact historical structural support or
   current-valid support at command time.
9. Define how `CONFLICTS_WITH`, corroboration and incoming derivation relations
   affect admission and whether links are reasserted for the new exact version.
10. Define command-time ownership, timezone/monotonic/skew rules, and whether an
    expired prior must be invalidated before correction.
11. Approve a versioned successor verifier strategy for the R1B conflict and a
    frozen-contract amendment or ADR. Task dispatch alone is not approval.
12. Decide sequencing with R1D, because incomplete request hashes and replay
    ordering can undermine qualification-field checks.

## 14. Follow-on task boundary and preserved scope

No code task is supplied because the policy is not unambiguous. After explicit
approval and independent acceptance of this draft, the dispatcher should split
work rather than issue one broad repair:

1. a from-status/current-prior admission slice with a successor verifier;
2. a source/latest/provenance prospective-snapshot validation slice;
3. a time-aware current-valid slice if approved;
4. R1D idempotency/replay/atomicity/concurrency under its existing program.

This document preserves these boundaries:

- production approved trusted correction rules remain empty;
- positive trusted registry/semantic validator remains `NOT_READY`;
- positive initial direct VERIFIED import remains default-denied;
- no code, tests, models, repositories, schema, migration, API/OpenAPI, verifier,
  frozen contract, old report, log or manifest is changed;
- no DB, SQL, pytest, migration or Docker operation is authorized or run;
- no R1D `UNKNOWN_OUTCOME`, concurrency or replacement atomicity work is entered;
- no WP04-03/04, Research, Thesis, Agent, Capability Runtime or Sector Crowding
  work is authorized;
- no commit, merge, rebase, reset, checkout, push or Git integration is
  authorized;
- this proposal does not close R1C, WP04-02 or WP-04.
