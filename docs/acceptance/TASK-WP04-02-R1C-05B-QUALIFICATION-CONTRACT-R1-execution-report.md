# TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1 execution report

**STATUS: IMPLEMENTATION_COMPLETE**

This is an executor report for a read-only investigation and two-document policy
contract. It is not an acceptance decision. It does not approve the proposed
policy, authorize implementation, or close R1C/WP04-02.

## Task and result

- Task: `TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1`.
- Role: rule qualification/specification executor.
- Contract source:
  `docs/acceptance/TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1-task-contract.md`.
- Required acceptance: `L1_STATIC_REVIEWED` by a logically independent verifier.
- Draft authority: `PROPOSED / NOT_APPROVED`.
- Draft readiness: `NOT_READY_FOR_IMPLEMENTATION`.
- Production approved trusted correction rules: empty and unchanged.
- Positive initial direct VERIFIED import: default-denied and unchanged.

The investigation found no unique policy that can be implemented without user
authority. The frozen state table names only VERIFIED ordinary correction, while
accepted R1B verifier behavior revises a newly created UNREVIEWED exact version.
Terminal append wording, direct stale-prior replacement, latest source status,
manual ownership, derived-support eligibility, conflicts and time-window
eligibility also lack one normative answer. The draft exposes those gaps and
recommends a narrow split between VERIFIED ordinary correction and explicitly
defined UNREVIEWED draft revision, subject to approval and a versioned frozen
decision.

## Baseline and attribution

At the start of the task:

```text
main branch: main
main HEAD: 438738c543e4cae3e805d31324b068c1cd5c7059
main parent: 7d3734bc8346c16f9bbf7f7d9806309949c996de
main tracked diff: empty
main index diff: empty

candidate branch: codex/wp04-02-evidence-domain-service
candidate HEAD: 0cef44fd2ffd929b40e849e607af0bd4c44d14d2
candidate parent: bdd70edc153b6ed5def65ed99c41f325df45f066
candidate status:
 M backend/evidence/services.py
 M tests/test_evidence_services.py
```

Fixed candidate hashes matched:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
6e5c1c1c8cd83603a73c71c77993f76883f780fa773910fe3d026797e611aa69  backend/evidence/services.py
dce8c3644441399ef443d54073c3121e8f59ebcd330c6955458c5db703056308  tests/test_evidence_services.py
```

`BASELINE_CHANGED_FILES` in the candidate were exactly the two modified files
above. They are the cumulative accepted R1C candidate and were not modified by
this task. The two authorized output documents were absent at baseline. Main had
pre-existing untracked governance/verifier evidence; no existing path was moved,
cleaned, overwritten or staged.

Before document creation, the deterministic inventory excluding the two target
paths reported:

```text
old_governance_count=250
old_governance_digest=23e8514b881515f8ea1c91598fc84f5b77a783abecdf0901bbedf360139fec10
fixed_verifier_count=8
fixed_verifier_digest=766275aaa39e0badba3216bed1f24a7eb96906f2fa0a2606a1590f1dce12d575
```

The digest is SHA-256 over each sorted relative path plus the SHA-256 bytes of
that file. It is a scope-preservation fingerprint, not a semantic acceptance
result.

## Materials inspected

The investigation read the repository `AGENTS.md`, full frozen Evidence contract,
original R1 repair program, current 05B contract, R1C-01/02/03A/03B/04A/05A task,
repair, execution and acceptance records relevant to correction qualification,
and R1C-05A-R1 acceptance. Historical reports were treated as scoped evidence,
not current implementation proof.

The fixed candidate source was inspected at symbol level:

- `create_evidence_series_version`;
- `revise_correct_evidence`;
- automatic `_revision_identity_changed` replacement routing;
- `create_replacement_evidence_series`;
- `_append_status_or_revision`;
- `_validate_provenance`, locator, derivation, instrument, identity, idempotency
  and audit helpers;
- Evidence and SourceDocumentVersion model constraints;
- current-valid query behavior;
- candidate correction/replacement/display/trusted/import tests.

Every fixed verifier found by exact source search that calls
`revise_correct_evidence` or `create_replacement_evidence_series` was read:

```text
docs/acceptance/verifiers/test_wp04_02_r1b_r1_wiring_20260915.py
docs/acceptance/verifiers/test_wp04_02_r1b_reverify.py
docs/acceptance/verifiers/test_wp04_02_r1c_01_independent_20260915.py
docs/acceptance/verifiers/test_wp04_02_r1c03a_prerequisites_boundary_20260916.py
docs/acceptance/verifiers/test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py
```

The `/tmp` R1B and R1C-01 copies matched the durable verifier bytes. No verifier
was executed or modified.

## Source-to-matrix evidence

| Draft section | Primary evidence | Result |
| --- | --- | --- |
| Current implementation inventory | Candidate service entrypoints/private helpers and models | Four write paths mapped by actual order, target status, predecessor, children, audit, replay and caller transaction ownership. |
| Frozen requirement map | Frozen §§6, 8-16, 21-23, examples 25 and 37-42 | VERIFIED positive path, ordinary UNREVIEWED target, identity routing, full tuple and immutable history identified; omissions are not converted into permission. |
| Accepted regression map | R1B wiring/reverify, R1C-01, R1C-03A oracle, R1C-04A and R1C-05A-R1 records | Exact conflict between frozen VERIFIED row and accepted UNREVIEWED revise is cited to immutable verifier lines. |
| Seven-status matrix | Frozen transition/terminal wording, absent candidate predicate, fixed verifier coverage | VERIFIED is ALLOW; the other six statuses are UNRESOLVED under current authority. Conservative error behavior and required user decision are recorded cell by cell. |
| Source/provenance matrix | Frozen exact source identity, source type/grade, locator, manual, derivation and cross-instrument rules; actual validators | Structural admission, proposed ordinary admission, current-valid and trusted-only requirements are separated. Latest/ACTIVE and relation policies remain proposed or unresolved. |
| Time matrix | Model constraints, frozen `as_of`/effective meaning, current service/query | Ordering, expired/future, `as_of`, status time, command time, stale exact, exact reads and current-valid are separated. |
| Conflict register | Contract versus current code versus accepted verifiers | Thirteen explicit conflicts/gaps recorded with required resolution. |
| Options | Literal VERIFIED-only, all nonterminal, split draft revision | Option C recommended for consideration, but no option is approved or implementation-ready. |

## Material findings

1. Same-series revise locks the highest exact and rejects stale
   `expected_version`, but it never checks the current verification status.
2. Automatic replacement inherits that absent status policy.
3. Direct replacement accepts any existing exact prior, including a stale or
   terminal exact, because it has no expected/current check.
4. Lower create with a predecessor does not load or qualify the predecessor and
   can bypass any policy added only to public revise/replacement.
5. Ordinary omitted/None correctly creates UNREVIEWED with rule None and does not
   inherit a prior rule. Complete CORRECTION tuple, exact predecessor, immutable
   children and path-owned audit behavior are accepted facts to preserve.
6. SOURCE_BACKED structural checks validate exact lineage, legal grade/type and
   locator shape, but not source latest or ACTIVE state. Same-series revise cannot
   submit a new exact source version or locator.
7. MANUAL initial ownership rules and DERIVED exact graph rules are not fully
   requalified on same-series append. Derived supports are not checked for
   current-valid eligibility.
8. Current-valid is latest-first and VERIFIED-only, but ignores SUPERSEDED source
   state and effective windows.
9. Period/effective ordering relies on database constraints rather than explicit
   pre-write domain admission.
10. Qualification-relevant fields are not consistently included in request
    hashes. Replay closure belongs to R1D and prevents a safe ad hoc policy patch.

## Proposed decision and counterexamples

The draft recommends Option C only for user consideration:

- VERIFIED may use ordinary same-series or replacement correction and becomes
  UNREVIEWED.
- UNREVIEWED may be revised only under newly approved `draft_revision` semantics,
  retaining UNREVIEWED and full CORRECTION audit.
- PENDING_REVIEW, DISPUTED, REJECTED, INVALIDATED and RETRACTED reject generic
  ordinary correction.
- Same-series and replacement share one from-status rule.
- All paths require the current-highest exact predecessor.

This recommendation requires a frozen amendment or ADR and a successor verifier.
It is not implemented. The draft analyzes all required counterexamples: all seven
statuses, stale expected version, non-latest direct prior, latest source
RETRACTED/SUPERSEDED, same bytes with a new source version, expired/future
effective windows, invalid ordering, DERIVED support-set change, terminal direct
replacement and same-key changes to qualification fields.

## Required user decisions

The draft lists twelve explicit approvals. The blocking decisions are the policy
option, UNREVIEWED draft semantics, consistent route permission, terminal
rehabilitation, current-highest direct prior, latest/ACTIVE source policy, MANUAL
ownership, DERIVED support eligibility, conflict-link handling, command-time
rules, successor-verifier/frozen amendment strategy, and sequencing with R1D.

Because these are product/domain policy decisions, this executor did not infer
approval from task dispatch or from historical green tests. No next code Task
Contract was generated.

## Changes and prohibited operations

Task-attributable files are exactly:

- `docs/acceptance/TASK-WP04-02-R1C-05B-ordinary-correction-qualification-draft.md`;
- `docs/acceptance/TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1-execution-report.md`.

No candidate code/test byte, fixed verifier, old governance artifact, frozen
contract, schema, migration, model, repository, API/OpenAPI file or Git history
was modified. No PostgreSQL connection, SQL, pytest, migration, Docker, MinIO,
dependency installation or runtime mutation was performed. No commit, merge,
rebase, reset, checkout, push, stage operation or branch movement was performed.

## Commands and checks

| Command/check | Exit/result | Purpose |
| --- | --- | --- |
| `git branch --show-current`, `git rev-parse HEAD`, `git rev-parse HEAD^` in both trees | exit 0; fixed identities matched | Baseline gate. |
| `git status --short`, tracked-only status and cached diff in both trees | exit 0; main tracked/index empty; candidate exactly two modified files | Scope and attribution. |
| `shasum -a 256` on fixed candidate files and correction-calling verifiers | exit 0; required hashes matched | Protected input integrity. |
| `rg`/`nl`/`sed`/`cat` over contracts, records, candidate source/tests and fixed verifiers | exit 0 | Read-only source-level investigation and exact citations. |
| Deterministic old-governance and verifier path/hash inventory | exit 0; counts/digests recorded above | Before snapshot for final comparison. |

Final byte, whitespace, CR, terminal-newline, SHA-256, Git scope, protected-hash
and candidate-baseline checks are recorded in the final executor response from
fresh commands. They are intentionally not represented by `git diff --check`
alone because both allowed documents are untracked.

## Unverified and deferred items

- No runtime behavior is newly accepted by a docs-only task.
- The proposed policy awaits independent document acceptance and explicit user
  approval.
- Positive trusted registry/validator and positive initial import qualification
  remain unimplemented.
- Complete source/current/window/current-valid behavior remains unimplemented.
- R1D aggregate-complete hashing, replay ordering, `UNKNOWN_OUTCOME`, replacement
  atomicity and concurrency remain open.
- Final WP04-02 independent re-verification, WP04-03, WP04-04 and Git integration
  remain unauthorized.

The executor now waits for independent acceptance of these documents and user
policy decisions. It does not self-approve the proposal.
