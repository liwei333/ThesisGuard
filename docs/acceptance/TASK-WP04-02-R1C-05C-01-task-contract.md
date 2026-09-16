# TASK-WP04-02-R1C-05C-01 — Four-Path Ordinary Correction From-Status Admission

Status: `PROPOSED / NOT_DISPATCHED`.

This contract is compiled under the user's docs-only policy authorization. It
must not be executed until separately dispatched. Policy approval does not
authorize business-code changes or database operations in the present task.

## A. Execution Core

- Role: bounded business repair executor, not independent verifier.
- Objective: reject new ordinary correction/draft writes from five forbidden
  actual prior statuses across all four paths before persistence; preserve
  VERIFIED ordinary correction and UNREVIEWED draft revision compatibility.
- Why now: user-approved narrow Option C resolves the frozen VERIFIED row versus
  accepted R1B UNREVIEWED draft behavior. Candidate currently lacks this guard.
- Type: backend domain service / PostgreSQL persistence.
- Size: `MEDIUM`, one from-status admission boundary across two candidate files.
- Required acceptance: independent `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`,
  `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Evidence matrix: Full.
- Normative prerequisite:
  [policy addendum](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/WP04_EVIDENCE_CORRECTION_POLICY_ADDENDUM_2026-09-16.md),
  decision `WP04-EVIDENCE-CORRECTION-STATUS-CURRENT-PRIOR-v1`.

### Top Blocking AC

1. Add only `r1c05c01` focused tests first. On unchanged services, obtain genuine
   PostgreSQL business RED for forbidden-status same-series and predecessor
   create, then all four-path negatives. Permissions/setup/cleanup are not RED.
2. New writes from PENDING_REVIEW, DISPUTED, REJECTED, INVALIDATED, RETRACTED
   raise exactly `EvidenceInvalidStateTransition` /
   `EVIDENCE_INVALID_STATE_TRANSITION` with traceable prior exact/series/status
   details on all four paths. No runtime bypass flag or trusted rule.
3. Every negative has legal, committed setup and a pre-command full-row baseline;
   caller commit after rejection followed by a distinct fresh session proves
   all-nine-table equality, no consumed keys, immutable prior and children.
4. Legal VERIFIED and UNREVIEWED controls preserve routing, UNREVIEWED/rule None,
   complete CORRECTION tuple, exact predecessor, strict path audit and history;
   supported COMMITTED exact-matching replays remain read-only.
5. Fixed verifiers, focused preservation suites, full service/regression/static
   matrix succeed at final hashes; scope and protected bytes stay fixed.

### Fixed baseline and scope

```text
main /Users/qianduoduo/Desktop/AI_app/ThesisGuard
branch main
HEAD   438738c543e4cae3e805d31324b068c1cd5c7059
parent 7d3734bc8346c16f9bbf7f7d9806309949c996de
tracked/index empty; preserve all existing untracked documents/evidence

candidate /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service
branch codex/wp04-02-evidence-domain-service
HEAD   0cef44fd2ffd929b40e849e607af0bd4c44d14d2
parent bdd70edc153b6ed5def65ed99c41f325df45f066
 M backend/evidence/services.py
 M tests/test_evidence_services.py

3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
6e5c1c1c8cd83603a73c71c77993f76883f780fa773910fe3d026797e611aa69  backend/evidence/services.py
dce8c3644441399ef443d54073c3121e8f59ebcd330c6955458c5db703056308  tests/test_evidence_services.py
```

Before any test edits, verify identities, exact dirty scope and hashes. Do not
require clean, overwrite cumulative changes or adopt a new baseline silently.

Only business/test changes: candidate `backend/evidence/services.py` and
`tests/test_evidence_services.py`. Retain all cumulative R1A/R1B/R1C content and
old test nodes. On separate dispatch, evidence-only additions may use uniquely
named `TASK-WP04-02-R1C-05C-01-execution-report.md` and task-specific logs under
main `docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/`; never rewrite old evidence.
This proposed permission is inactive until dispatch.

### Required investigation and minimal implementation

Read main AGENTS, frozen §§12–13/17–18, policy addendum, 05B draft/acceptance,
05A-R1 acceptance, actual candidate helpers/tests/models and durable R1B wiring/
reverify. Use systematic-debugging, test-driven-development,
verification-before-completion and ai-task-governor boundaries.

| Path | Actual production entry/helper | Status source | Scope |
| --- | --- | --- | --- |
| Same-series | revise → append helper | Actual selected current row | New CORRECTION only |
| Automatic | revise → replacement → underlying create | Actual selected prior row | Identity route receives same guard |
| Direct | create_replacement_evidence_series | Loaded caller exact prior | Do not trust a caller status |
| Underlying | create_evidence_series_version with predecessor | Loaded supersedes exact prior | Must not bypass guard |

Admit `{VERIFIED, UNREVIEWED}` only for new ordinary writes, meaning omitted or
None trusted rule. Keep invalid trusted-rule behavior unchanged; non-None does
not create permission. Keep predecessor-free initial creation outside this
guard. Other lifecycle appends must retain their existing status tables.
The underlying path may load the predecessor to validate its actual status;
this does not authorize latest/current enforcement in this slice.

Resolve replay under existing semantics before applying the new-write admission
where the path already supports COMMITTED replay. Do not move unrelated replay/
expected-version ordering, rewrite request hashes, add migrations or fix R1D.
Preserve existing missing-exact errors and supported legacy replay. If the guard
cannot preserve a supported replay without a broader redesign, BLOCKED.

Rejection must precede db.add/flush of new series/version/children/idempotency/
audit. Use existing domain error, not DB IntegrityError or arbitrary exception.
No generic terminal recovery, new enum, public API, caller flag, registration,
configuration or injection permission. Helpers may be added only within services.

### Genuine RED → GREEN and PostgreSQL proof plan

First add tests only; record services SHA unchanged. Obtain real assertions
showing a forbidden write was accepted on the baseline. If baseline is
unexpectedly green, stop `BLOCKED_UNEXPECTED_GREEN_BASELINE`; do not manufacture
failures. After RED, make the smallest service-only status guard and obtain GREEN.

For each of 5 forbidden statuses × 4 routes, build otherwise valid inputs:

- Create UNREVIEWED through public create. Use request_review for PENDING_REVIEW;
  verify_or_reject(REJECTED) for REJECTED; request_review then
  verify_or_reject(VERIFIED) for VERIFIED; mark_disputed for DISPUTED; legal
  retract_or_invalidate for INVALIDATED/RETRACTED. Do not mutate old status rows.
- For automatic routing, establish a legal alternate exact support or valid
  CROSS_INSTRUMENT membership change. Preserve returned exact IDs. Never assume
  initial FACT support has a predecessor or count fixture failure as rejection.
  Support setup/review must finish and commit before no-residue baseline.
- Commit every setup, take a complete nine-table row/column snapshot ordered by
  primary key, and preserve prior exact/children snapshots. See existing
  `R1C04A_MODELS`/`r1c04a_rows`; do not reduce assertions to row counts.
- Invoke the real public production service, catch only the required error,
  verify code/details and clean pending ORM state, then caller commit without
  using outer rollback as proof. Fresh independent session must equal baseline
  for every row/column. Confirm both direct outer and underlying `:inner` keys
  absent where applicable; history, children and audit are unchanged.

For 2 allowed statuses × 4 routes, commit and fresh-read positive controls.
Assert same-series N+1 versus new series v1, exact supersedes, target
UNREVIEWED/rule None (omitted and explicit None), complete tuple and no inherited
trusted rule. Verify strict event aggregate/count/actor/time/payload:
same-series `EVIDENCE_CORRECTION`; replacements `EVIDENCE_VERSION_CREATED` plus
the existing series event. Retain old exact and immutable children snapshots.
Verify legal review still works and UNREVIEWED is not eligible VERIFIED support.

COMMITTED replay controls must cover existing supported direct, automatic and
underlying paths plus all fixed historical replay fixtures, with fresh-session
all-nine-table equality and exact response ID. Also seed a disclosed legacy
COMMITTED correction from a now-forbidden exact status through test-owned ORM
history/idempotency fixture before baseline, without altering production rules;
the unchanged exact request must replay read-only and a new key must be denied.
This is historical compatibility setup, not a new production positive write.
Existing same-series stale expected-version behavior is preserved, not expanded
into a new replay guarantee. Do not accept altered-input replay or fake a
COMMITTED record with pending status.

### High-risk examples

1. Given current PENDING_REVIEW and valid text/children, when same-series or
   identity-changing correction is called with a new key, then exact state error
   and caller-commit/fresh-session no-residue; no review cancellation.
2. Given RETRACTED exact prior, when direct or underlying replacement is called
   with valid identity and complete tuple, then no terminal rehabilitation, no
   new series or outer/inner key. Tested prior is highest for this status slice.
3. Given UNREVIEWED DERIVED prior and legal changed support set, when revise is
   called, then replacement v1 UNREVIEWED/rule None and full audit/history; fixed
   R1B wiring assertions still execute against the real new exact target.
4. Given historical COMMITTED exact request from a forbidden status, when the
   unchanged request is replayed, then the existing response is returned with no
   writes; a new-key request is denied. Incomplete hashes remain R1D.

### Required verification matrix — execute only after dispatch

Use the existing environment; first identify actual python/pytest/Ruff/mypy/
Alembic executable paths and versions. No dependency install/upgrade. DB only
through normal permissions and the existing disposable local fixture at
127.0.0.1:15432. No host/port change, substitute/shared/external instance,
proxy/Docker bypass, arbitrary SQL or broad cleanup. Use fixture teardown and
report its actual cleanup result.

`TG_TEST_ADMIN_DATABASE_URL`, `TG_R1C_REPLAY_BASELINE` and
`TG_R1C02_REPLAY_PRIOR` must be unset on all normal runs. Inventory and hash-check
all fixed verifier bytes first. Run from candidate cwd with main durable paths
below; these are authoritative recovered originals, not rewritten substitutes.

Fixed SHA-256 values under main `docs/acceptance/verifiers/`:

```text
64162c0aafc3ad620ee0cab5e4d8d0ed10e6d61ab8dc21322f4364144c442a05  test_wp04_02_r1c_02_independent_20260915.py
857914f073c552be98f895a456d2f0ec486452e1c9aed06a87176c6e7fefd48a  test_wp04_02_r1c_01_independent_20260915.py
909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786  test_wp04_02_r1b_r1_wiring_20260915.py
0f7cea4d14735bd165b75d756444259a64483a97e6a338227bc09af806490cc9  test_wp04_02_r1b_reverify.py
66be45f354d1df34370eedd9811b3bc68cf29852d45027ea576a67975b18ddfe  test_wp04_02_r1a_verifier.py
0ae19f9103b328afc3f7b5b017390569ead2a5239f18765d8c82f369d8818b0b  test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py
be68779f161c5983fce265bafe0b8237ae881feea7900a446c07ff03433ffb60  test_wp04_02_r1c05a_audit_tuple_replay_r1_20260916.py
```

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1c05c01 -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1c05a -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1c04a -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c05a_audit_tuple_replay_r1_20260916.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q \
  /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c_02_independent_20260915.py \
  /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c_01_independent_20260915.py \
  /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1b_r1_wiring_20260915.py \
  /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1b_reverify.py \
  /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1a_verifier.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c05c01-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1c05c01-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
git diff --check
git diff --stat
git status --short
git rev-parse HEAD HEAD^
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

Resolve executables to inspected existing paths; the command names do not permit
installation. Alembic heads must remain `000000000004`; no migration execution.
Oracle retains 58 scenes, five original verifiers retain all their nodes. Prior
suite counts are historical reference, not numbers to fabricate or acceptance
by count alone. Report every real node/result, skip/xfail and cleanup diagnostic;
do not skip a failing old node or weaken expectations.

### Stop conditions and evidence

BLOCKED on baseline/protected hash drift, unavailable normal DB permissions or
fixture, setup/cleanup error, missing original verifier, unexpected baseline
green, business regression, existing-verifier conflict, or required third file/
error/schema/API/hash/concurrency change. Use normal approval mechanism for local
fixture permission; denial is not RED. Never clean/reset/move a baseline.

Map each AC to exact test node and production helper, genuine RED/GREEN logs,
all-nine-table fresh-read evidence, exact IDs, row tuple/audit/history/replay,
cleanup, environment/version, complete command output/exit and initial/final
HEAD/status/file/verifier hashes. Executor reports IMPLEMENTATION_COMPLETE or
BLOCKED, never self-approves independent acceptance.

## B. Governance Appendix and separate follow-on

Consider baseline/scope/contract/architecture/test/DB-persistence/regression/
evidence gates. Core invariants and anti-drift remain those of ai-task-governor;
do not alter this contract or standards to accommodate implementation.

Separate planned slice `TASK-WP04-02-R1C-05C-02` is `PROPOSED / NOT_DISPATCHED`:
after 05C-01 independent acceptance, separately freeze a baseline and contract
for current-highest exact-prior enforcement on direct and underlying paths.
Sequential tests: highest allowed prior succeeds; older VERIFIED exact with
newer UNREVIEWED/terminal highest fails with no residue; exact history and
COMMITTED replay remain. Currentness is selected-series-local, not global
replacement head; no public expected-version parameter is added by assumption.
Error details/selection strategy belong to that bounded contract. Interface to
R1D must state what the sequential check proves and what race/locking/atomicity
it does not prove; inseparable concurrency changes require dispatcher split.
Do not implement it in 05C-01.

Standard deferrals: new source/support/manual/conflict/time admission, terminal
rehabilitation, trusted registry/positive rules, initial import qualification,
R1D request hash/order/race/atomicity/UNKNOWN_OUTCOME, API/OpenAPI, Research,
Thesis, Agent, Capability Runtime and Sector Crowding. No models/repositories/
schema/migration/errors/verifier/frozen contract/old report/log/manifest changes.
No Git add/commit/merge/rebase/reset/checkout/push or integration. Status-only
completion is not all approved current-prior enforcement, complete ordinary
qualification, R1C/WP04-02 closure or Git authorization.
