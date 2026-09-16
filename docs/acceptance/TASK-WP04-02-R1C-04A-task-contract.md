# TASK-WP04-02-R1C-04A — Evidence Display Text Admission

Status: READY_FOR_USER_DISPATCH. This document does not start implementation or grant Git authority.

## A. Execution Core

- Task ID: TASK-WP04-02-R1C-04A.
- Objective: Reject new Evidence writes with empty/whitespace-only/non-string display_text through domain errors before persistence, preserving valid body bytes, history, ordinary routing and existing replay behavior.
- Why Now: R1C-03B specification passed with positive trusted NOT_READY; frozen D-01 requires non-empty display_text, whereas actual revision override validation only forbids None and models have NOT NULL without a nonblank check. This is a verifiable structural repair independent of positive trusted semantics.
- Role / Type / Size: EXECUTOR / REPAIR / SMALL, one payload-admission invariant across tightly coupled entry paths.
- Required Acceptance: L1_STATIC_REVIEWED, L2_BUILD_VERIFIED, L3_CONTRACT_VERIFIED, L4_DB_VERIFIED; Full Evidence Matrix due real transactions/audit/history.

### Fixed baseline / required reads

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

Read main AGENTS, this contract, TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1-acceptance.md, rule-definition draft, ORACLE-R1 acceptance/repair/execution reports, original R1 repair program, frozen D-01/sections12/13/21/22 and actual candidate services/errors/models/repositories/tests/fixtures. Preserve every existing main untracked artifact; main docs are governance inputs, not business implementation. Verify five originals and R1 oracle fixed hashes from their contracts/manifests. Unexpected candidate/HEAD/hash/tracked main drift is BLOCKED.

### Top Blocking AC

1. Prove real PostgreSQL business RED before service edits: legally prepared, committed valid fixture and stable baseline; empty display_text reaches the command and currently fails the new rejection expectation. Permission/setup failure is not RED. At minimum same-series revision and no-predecessor UNREVIEWED creation demonstrate actual baseline acceptance if present. Unexpected green stops as BLOCKED_UNEXPECTED_GREEN_BASELINE.
2. New-request validation covers no-predecessor creation, same-series revise, automatic identity-changing revise, direct replacement and underlying create with predecessor. Reject blank/non-string body before new series/version/children/idempotency/audit writes. Use existing domain errors, no silent conversion/downgrade, no database-error-only rejection. Preserve existing explicit None-clear error semantics for revise.
3. Valid body text is not normalized/trimmed; omitted revise text inherits the existing valid body, optional nullable machine fields keep R1B behavior, ordinary result remains UNREVIEWED/rule=None. Routing/exact supersedes/status audit/immutable children and all prior rows remain correct. Historical exact reads and existing successful exact request replay stay read-only; no legacy cleanup or broad replay redesign.
4. All negative commands allow caller commit followed by distinct fresh-session full-row comparisons, proving no residue/key consumption; real PG positive/history/replay controls and complete preservation matrix pass. No old verifier edits/skips or positive rule activation; production approval stays empty.
5. Only two candidate files changed, errors/models/repositories/migrations/HEAD unchanged; complete baseline/RED/GREEN/commands/hashes and missing broader qualifications reported. Executor cannot self-approve or declare whole R1C/WP04-02 done.

### Scope and exact behavior

Only edit in candidate with apply_patch:

- backend/evidence/services.py.
- tests/test_evidence_services.py.

One invariant only: display_text. Do not also validate/rewrite titles, claim keys, numeric semantics, units, effective windows or new from-status/source-state policies. A rejected body's semantics need not be inferred; no LLM/artifact connector is involved.

- A new body must be a str and must contain at least one non-whitespace character. Use whitespace examination only to determine blankness, never to alter stored valid text.
- Empty string, ASCII spaces, tabs/newlines and Unicode-whitespace-only strings fail. False,0,empty/nonempty list/dict fail with stable domain validation rather than coercion or incidental TypeError/DataError. A nonblank Unicode/financial sentence with leading/trailing spaces succeeds and remains byte-for-byte unchanged.
- For new requests, use EVIDENCE_VALIDATION_ERROR with validation_path=display_text and reason=blank_display_text or invalid_display_text_type, plus actual value/type where safely representable. Preserve existing revise(None) EVIDENCE_INVALID_PROVENANCE behavior rather than breaking its accepted R1B error expectation. Other entrypoints receiving None must reject with a deliberate domain validation error before writes. Do not change errors.py or catch any Exception as the test oracle.
- Check the effective body of the prospective new version; _UNSET means inherit, not a string value. A pre-existing invalid body can remain historically readable but is not silently propagated into a new ordinary version; supplying a valid corrected body may repair the prospective content without modifying history. This does not authorize a previously forbidden lifecycle transition.
- Keep read-only exact historical replay behavior. Place new-admission validation without turning replay into a new write or silently fixing R1D's current hash/ordering defects. Do not widen current replay guarantees. If preserving replay requires changes beyond this one invariant, BLOCKED with exact conflict evidence.
- Public entrypoints and their private write helpers must not offer an empty-body bypass. Guard before adding prospective new ORM rows/flush and idempotency/audit writes. Reads/locks/validation setup are allowed; do not commit inside the service.

### High-risk examples / implementation strategy

- Given valid VERIFIED prior, When same-series ordinary correction provides empty/blank text, Then stable domain rejection, caller commit and fresh nine-table equality; original body/children/current remain unchanged.
- Given identity-changing automatic support/member set, When body is blank, Then no replacement seriesv1/children/key/audit residue. Use real returned exact IDs and legal setup; commit setup before baseline, never assume initial support has a predecessor.
- Given direct/underlying replacement with valid identity change and complete CORRECTION tuple, When body is blank/non-string, Then reject before writes; no transaction poisoning or cleanup-as-proof.
- Given valid nonblank text with surrounding whitespace or revise text omitted, Then preserve the exact body, N+1/new-series routing, UNREVIEWED/rule=None and known actor/time audit.
- Given already committed exact request replay/history, Then no new rows or history mutation; do not reclassify the old read as a new admission. Existing same-series expected-version replay limitations remain R1D.

First add focused r1c04a tests and run unchanged services to obtain genuine RED. Then implement a minimal shared/private check at appropriate new-write boundaries, keep signatures/errors/transaction ownership, and demonstrate GREEN. Do not change the immutable contract or tests to match an accidental implementation.

### Required Verification

Use the existing local127.0.0.1:15432 disposable PostgreSQL fixture through normal permissions; never set TG_TEST_ADMIN_DATABASE_URL, TG_R1C_REPLAY_BASELINE or TG_R1C02_REPLAY_PRIOR. Primary runtime/library resolution follows the verified existing ORACLE runtime records; no installation/upgrade or host/port substitution.

From candidate with the recorded existing Python/PYTHONPATH/primary PATH, run and retain argv/cwd/env/start/end/exit/full log hash:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1c04a -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1c_02_independent_20260915.py /tmp/test_wp04_02_r1c_01_independent_20260915.py /tmp/test_wp04_02_r1b_r1_wiring_20260915.py /tmp/test_wp04_02_r1b_reverify.py /tmp/test_wp04_02_r1a_verifier.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c04a-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1c04a-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
git diff --check
git status --short --branch --untracked-files=all
git rev-parse HEAD HEAD^
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

If the shell's bare names cannot resolve the existing primary tools, use the recorded absolute /opt/miniconda3/bin paths and existing library paths, recording the actual command; do not install or switch runtime silently. Missing /tmp originals may only be restored byte-exact to absent paths from verified durable copies if required; mismatching files are not overwritten. Old flawed supplemental is historical RED, not a required GREEN target; corrected R1 oracle remains58 scenarios.

All negative fixtures complete lawful setup+commit before baseline. Compare all columns/all rows in nine persistence tables after caller commit via fresh session, plus any corroboration rows used by setup. Also verify exact versions/children, no pending ORM writes, stable domain details and key not consumed. Full equality, not just counts/hashes or rollback, is required. Positive fresh readers prove valid-body preservation, ordinary status/audit/exact lineage and all old rows unchanged. Record precise fixture teardown outcome; no broad cleanup.

### Must Not / stop conditions

No errors/model/repository/schema/migration/API/main tracked document/old verifier/log/manifest edits; no title rule/positive registry, no new import semantic or source-state/from-status policy, no R1D/refactor/dependencies/MinIO/parser/Agent/Sector work. No Git add/commit/merge/rebase/reset/checkout/push or branch movement. Do not weaken existing suites to accommodate the new guard.

BLOCKED on baseline/artifact drift, unavailable normal DB permission/fixture/runtime, no genuine baseline RED, fixture cleanup failure, forbidden scope or existing accepted contract conflict. Do not convert setup failure to business RED or ignore an old verifier failure. Any unexpected old-fixture conflict needs dispatcher evidence, not unilateral expectation changes.

### Expected Evidence / final response

Report IMPLEMENTATION_COMPLETE or BLOCKED only. Supply fixed baseline and initial/final scope, new tests vs unchanged services RED and repaired GREEN, each route→validation→real PG proof, effective/omitted/None/type cases, caller-commit/fresh-session no-residue/history/replay, complete command outputs/exits, before/after file/verifier hashes and cleanup. New task-specific logs/execution report may be kept under main docs/acceptance with unique r1c04a names; never alter old evidence. Services remain flush-only and errors.py hash fixed.

## B. Governance Appendix

Use systematic-debugging, test-driven-development and verification-before-completion; obey ai-task-governor core invariants, anti-drift, evidence-based acceptance and Full evidence mapping. This is a new separately dispatched structural repair, not a failure repair attributed to the passed rule-spec executor.

Positive trusted remains unapproved/NOT_READY and its current empty approval set is preserved. This task does not waive original overall WP04-02 requirements or close its R1C qualifications. Ordinary complete from-status/source/window qualifications, initial VERIFIED semantic qualification, R1D and final independent reverify remain open. Do not require unrelated positive title-rule work before proving this independent structural invariant.
