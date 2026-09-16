# WP-04 Evidence Correction Policy Addendum — 2026-09-16

Decision ID: `WP04-EVIDENCE-CORRECTION-STATUS-CURRENT-PRIOR-v1`

Policy status: `APPROVED_POLICY / CONTRACT_ONLY`.

Task: `TASK-WP04-02-R1C-05B-POLICY-DECISION-R1`.

Approval date: 2026-09-16, Asia/Shanghai. This date records the user approval
received in the current task conversation; no precise message timestamp or
external approval ID was supplied.

This companion addendum records only the explicitly approved six-item narrow
Option C package. It is normative for that package after the approval recorded
below. It does not establish implementation completion, independent acceptance,
or permission to execute a business-development task.

## 1. Approval provenance

Source: the user's explicit approval message immediately following the executor's
`BLOCKED_POLICY_APPROVAL_REQUIRED` response in this conversation. The earlier
task dispatch and specification acceptance were not treated as approval.

The actual approval text is preserved below, including Markdown escapes:

```text
我明确批准
TASK-WP04-02-R1C-05B-POLICY-DECISION-R1-task-contract.md
中“Proposed decision package”的六项完整窄 Option C 政策包：

1. 当前 VERIFIED prior 允许 ordinary correction；
   当前 UNREVIEWED prior 允许 draft revision。
   保留既有公开入口，语义由真实 prior status 决定，
   不新增调用方权限标志。

2. same-series 和 identity-changing replacement 均产生
   UNREVIEWED、trusted\_correction\_rule=None，保留完整
   CORRECTION tuple、exact predecessor 和既有 audit event kind。

3. 拒绝从 PENDING\_REVIEW、DISPUTED、REJECTED、INVALIDATED、
   RETRACTED 发起通用 correction/replacement；不批准终态恢复。

4. 四路径的新修正均须针对所选 prior series 内的
   current-highest exact version；保留历史 exact 读取。

5. 已 COMMITTED 且 exact-matching 的请求保留只读重放。
   完整 request identity、race、atomicity、reconciliation、
   UNKNOWN\_OUTCOME 仍属于 R1D。

6. 本次不批准 source-latest/ACTIVE、DERIVED support、
   manual ownership、conflict propagation、effective-window、
   trusted success rule 或 initial VERIFIED import 政策。

我同时批准创建：
docs/WP04\_EVIDENCE\_CORRECTION\_POLICY\_ADDENDUM\_2026-09-16.md

其规范优先级严格限定于上述政策包，原冻结合同保持不变。
本次仅授权原合同中的三份 docs-only 产物，
以及编排而不执行 TASK-WP04-02-R1C-05C-01。
不授权业务代码修改、数据库操作或 Git 集成。
```

All six items and the limited companion normative document were explicitly
approved together. No source/support/time/trusted-import policy or terminal
rehabilitation approval is inferred from that message.

## 2. Authority and conflict resolved

Primary frozen reference:
[Evidence Domain Contract §12](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md:443)
and [§13](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md:534).
The frozen file remains byte-for-byte unchanged:
`b179ecc6ea60ffed75f7179a2d36e47ad2b55153f6d4fa62b8be7e4926fd1288`.

The frozen lifecycle table expressly lists VERIFIED ordinary correction but
leaves replacement prior status broad. Accepted R1B probes revise a newly created
UNREVIEWED DERIVED exact through same-series and automatic replacement. See the
immutable [R1B wiring verifier](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1b_r1_wiring_20260915.py)
and [R1B reverify verifier](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1b_reverify.py).
The accepted behavior supplies compatibility evidence; user approval supplies
the authority to resolve the status omission.

Within this six-item package only, this addendum supplements §§12–13 by naming
UNREVIEWED draft revision, denying generic correction from the five other
statuses, and narrowing new replacement prior selection to the selected series'
current-highest exact. It takes precedence only over omission or ambiguity about
those approved matters. It does not replace the frozen contract or override any
other source, identity, review, history, data-validation, error, concurrency,
storage or downstream eligibility rule.

The sentence allowing a new N+1 to supersede a terminal version is not permission
to use generic correction for terminal rehabilitation. No such command is
approved. Explicit review/dispute and lifecycle commands retain their existing
separate rules. No canonical PRD/TAD/AGENTS document is amended.

The previous qualification draft stays a historical `PROPOSED / NOT_APPROVED`
investigation. Its broader unresolved matters remain unresolved. This addendum
is the later authority for the narrow package, without rewriting that draft or
its acceptance record.

## 3. Seven-status and four-path admission matrix

The matrix applies to new ordinary predecessor-based writes. Ordinary means
trusted rule omitted or explicitly None; neither path permits implicit trusted
inheritance. The actual persisted exact prior status determines command intent.

| Actual prior status | Same-series revise | Automatic replacement revise | Direct replacement | Underlying create with predecessor | Intent / result |
| --- | --- | --- | --- | --- | --- |
| `VERIFIED` | ALLOW | ALLOW | ALLOW | ALLOW | Ordinary correction → UNREVIEWED |
| `UNREVIEWED` | ALLOW | ALLOW | ALLOW | ALLOW | Draft revision → UNREVIEWED |
| `PENDING_REVIEW` | DENY | DENY | DENY | DENY | Existing state-transition domain error |
| `DISPUTED` | DENY | DENY | DENY | DENY | Existing state-transition domain error |
| `REJECTED` | DENY | DENY | DENY | DENY | Existing state-transition domain error; no recovery |
| `INVALIDATED` | DENY | DENY | DENY | DENY | Existing state-transition domain error; no recovery |
| `RETRACTED` | DENY | DENY | DENY | DENY | Existing state-transition domain error; no recovery |

ALLOW means this status requirement permits the request; it does not waive
existing identity/provenance/locator/children/display/actor/audit validation or
the separately approved current-highest prior requirement. Missing prior uses
the existing exact-not-found error; an unavailable or unrecognized persisted
status cannot grant permission. Forbidden status uses
`EvidenceInvalidStateTransition`, code `EVIDENCE_INVALID_STATE_TRANSITION`, with
traceable prior exact ID, series ID and actual prior status details.

Path ownership:

- Same-series: `revise_correct_evidence` → same-identity N+1 append helper.
- Automatic replacement: `revise_correct_evidence` detects a legal identity
  change → `create_replacement_evidence_series` → underlying create.
- Direct replacement: `create_replacement_evidence_series` with caller exact
  prior, new identity and CORRECTION metadata.
- Underlying predecessor create: `create_evidence_series_version` with non-null
  `supersedes_evidence_version_id`; it must not bypass predecessor admission.

Predecessor-free initial creation is outside this matrix. Public compatibility
is retained: no new public draft API or caller-selectable permission flag.
`draft_revision` is command intent derived from UNREVIEWED prior, not a claim of
verification and not a new `status_change_kind` enum.

## 4. Result, audit and history

For every allowed new ordinary/draft write:

- Target row is `UNREVIEWED`, with `trusted_correction_rule=None`.
- Complete row tuple is `status_changed_at`, `status_changed_by_actor`,
  `status_change_kind='CORRECTION'`, and `status_reason`, using the existing
  command's explicitly supplied metadata. Partial/null tuples remain illegal.
- `supersedes_evidence_version_id` refers to the actual admitted exact prior.
- Same identity appends N+1. Identity change creates replacement series v1;
  version 1 does not make it a predecessor-free initial import.
- Same-series version audit remains `EVIDENCE_CORRECTION`. Automatic/direct/
  underlying replacement version audit remains `EVIDENCE_VERSION_CREATED`, with
  the existing `EVIDENCE_SERIES_CREATED` companion for the new series.
- Existing audit aggregate, actor/time ownership, payload and event cardinality
  stay unchanged; no arbitrary event kind or new draft enum is authorized.
- Prior exact rows, their locators/instrument/derivation children, references
  and original audit/idempotency rows remain immutable and readable.
- UNREVIEWED results are not current-valid VERIFIED downstream support. Existing
  latest-first eligibility and explicit review commands remain separate.

Forbidden new requests must be rejected before new series/version/children/
idempotency/audit persistence, without key consumption or caller-transaction
residue. This is an acceptance requirement for implementation, not runtime
evidence generated in this docs-only task.

## 5. Current-highest prior and replay

For a new correction, resolve the actual selected exact prior and its
`evidence_series_id`. Current-highest is the EvidenceVersion with the maximum
version number inside that selected prior series. The selected prior ID must
equal that highest exact ID; selecting an older VERIFIED row when a newer
UNREVIEWED or terminal row exists is not permitted.

This is not a global cross-series replacement-head traversal rule. It does not
change historical exact reads or rewrite supersedes references. Existing revise
`expected_version` conflict behavior is preserved. No new public direct
replacement `expected_version` parameter is approved by this package.

Existing COMMITTED exact-matching replay is a read-only response, not a new
correction. Preserve the persisted response ID and rows under existing replay
semantics; new status/current-prior checks must not invalidate an already
supported historical exact replay. This package grants no altered-input replay.
It does not declare incomplete request hashes complete or redesign existing
same-series replay/expected-version ordering. Those limitations remain R1D.

The current-highest policy is approved at specification level. Direct and lower
create enforcement is not implemented here and is deliberately excluded from
the first from-status implementation slice. Separately verify sequential
stale-prior rejection in the follow-on slice; do not claim that a pre-read alone
proves concurrent currentness, race freedom or atomic replacement.

## 6. Compatibility and sequencing

No schema migration, existing-row rewrite, old verifier edit or historical
idempotency rehash is needed or authorized by this decision.

1. Proposed `TASK-WP04-02-R1C-05C-01`: four-path from-status admission only;
   preserve UNREVIEWED R1B draft behavior, VERIFIED correction, old children,
   exact graph checks and existing COMMITTED replay. Requires separate dispatch
   and independent acceptance.
2. Separately proposed `TASK-WP04-02-R1C-05C-02`: current-highest exact-prior
   enforcement on direct/lower routes, with existing revise behavior preserved.
   Needs its own bounded contract after 05C-01 acceptance, not dispatch today.
3. R1D owns aggregate-complete request identity, replay ordering, race,
   reconciliation, locking/atomicity and UNKNOWN_OUTCOME. Any inseparable race
   requirement must return to dispatcher; no opportunistic concurrency redesign.

The fixed R1A/R1B/R1C verifiers remain compatibility requirements. If a genuine
old-verifier conflict occurs during future implementation, report its exact node
and evidence and obtain a separate dispatcher repair/successor contract. Do not
rewrite expectations to force acceptance.

## 7. Explicit remaining boundaries

Not approved: new source-latest/ACTIVE rules, DERIVED support eligibility,
manual ownership changes, conflict propagation, effective-window eligibility,
positive trusted correction rules or initial VERIFIED import qualifications.
The production approved trusted correction rule set stays empty. Existing
initial VERIFIED import fail-closed behavior and historical tuple replay repair
are preserved, without asserting a positive import validator exists.

The full ordinary qualification table is not implemented or wholly settled.
R1D, final WP04-02 independent full acceptance, API/OpenAPI, Research exact
references, Thesis and Agent work remain outside this decision. Capability
Runtime and Sector Crowding remain deferred. This document authorizes neither
Git integration nor a claim that R1C/WP04-02 is complete.
