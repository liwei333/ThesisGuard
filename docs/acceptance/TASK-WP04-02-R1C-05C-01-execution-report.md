# TASK-WP04-02-R1C-05C-01 execution report

Status: `IMPLEMENTATION_COMPLETE` — bounded repair executor result; independent acceptance is pending.
Evidence date: 2026-09-16 (Asia/Shanghai). This is the separately dispatched 05C-01 candidate, not approval of the entire R1C/WP04-02 or Git integration.

## Authorization and frozen start

The user's explicit 05C-01 dispatch activates the proposed development contract and limits business changes to candidate `backend/evidence/services.py` and `tests/test_evidence_services.py`. The narrow Option C policy is recorded in `WP04-EVIDENCE-CORRECTION-STATUS-CURRENT-PRIOR-v1`; this slice implements only from-status admission.

| Repository | Branch | HEAD | Parent | Initial and final tracked scope |
| --- | --- | --- | --- | --- |
| Main | main | 438738c543e4cae3e805d31324b068c1cd5c7059 | 7d3734bc8346c16f9bbf7f7d9806309949c996de | Empty worktree tracked diff and index diff |
| Candidate | codex/wp04-02-evidence-domain-service | 0cef44fd2ffd929b40e849e607af0bd4c44d14d2 | bdd70edc153b6ed5def65ed99c41f325df45f066 | Exactly services.py and tests/test_evidence_services.py modified |

The candidate was intentionally dirty at the frozen start. All cumulative changes were retained. The initial protected snapshot contains all 283 existing main documentation/evidence files and 65 candidate code/configuration files. Every original main file and all 63 candidate files outside the authorized pair remain byte-identical. The complete original test-file prefix reconstructs the initial test SHA; no old test node or existing assertion was edited. All seven durable verifiers remain at their contract hashes.

| Business file | Initial SHA-256 | Final SHA-256 |
| --- | --- | --- |
| backend/evidence/errors.py | 3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec | 3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec |
| backend/evidence/services.py | 6e5c1c1c8cd83603a73c71c77993f76883f780fa773910fe3d026797e611aa69 | 7ce76b02928019347625048e7d0acb523d74168cd6bbbdf03184163ac277f959 |
| tests/test_evidence_services.py | dce8c3644441399ef443d54073c3121e8f59ebcd330c6955458c5db703056308 | b5bfcdeb2db6753c71fd146b935dd26229daae0d73da5bda68af437db137b950 |

Read/investigated: main AGENTS, full development contract and dispatch, approved policy addendum/final acceptance, 05B draft and qualification acceptance, 05A-R1 acceptance, frozen Evidence status/history/idempotency sections, actual services/helpers/models/tests/fixtures, and durable verifier code. Applied ai-task-governor boundaries, systematic-debugging, test-driven-development and verification-before-completion. No independent acceptance verdict is issued here.

## Genuine tests-only RED

Only appended `r1c05c01` tests were added first. The command runner asserted the unchanged services SHA `6e5c1c1c8cd83603a73c71c77993f76883f780fa773910fe3d026797e611aa69` before each RED run.

- `red-two`: same-series and underlying predecessor-create from PENDING_REVIEW, **2 failed**, exit 1. Both public-service calls accepted the forbidden write; the exact failure was `DID NOT RAISE EvidenceInvalidStateTransition`.
- `red-all20`: five forbidden statuses × four routes, **20 failed**, exit 1, the same missing required domain rejection.
- Both runs completed lawful public setup and commit against PostgreSQL 17.11 before invocation. No permission, setup, assembly or cleanup error was counted as RED.

The complete logs preserve every failing parametrized node. The forbidden test base node is `test_r1c05c01_forbidden_status_commit_fresh_no_residue[STATUS-ROUTE]`, with STATUS ∈ PENDING_REVIEW, DISPUTED, REJECTED, INVALIDATED, RETRACTED and ROUTE ∈ same, automatic, direct, underlying.

## Minimal production change and four-path mapping

The cumulative diff from candidate HEAD is 1,723 insertions / 34 deletions across the authorized pair (including retained earlier work); this task's delta from the accepted dirty start is 21 service additions and 557 appended test lines, with zero old-prefix deletions.

This task adds exactly 21 service lines: one private shared validator and three call sites. It reads the actual loaded prior status and admits only VERIFIED or UNREVIEWED for new ordinary writes. A rejected status raises the existing `EvidenceInvalidStateTransition`, stable code `EVIDENCE_INVALID_STATE_TRANSITION`, and details `prior_evidence_version_id`, `evidence_series_id`, `from_status`.

| Path | Production coverage | Guard placement and preserved behavior |
| --- | --- | --- |
| Same-series | revise_correct_evidence → _append_status_or_revision | CORRECTION branch only, after supported replay resolution, before append persistence |
| Automatic replacement | revise_correct_evidence → create_replacement_evidence_series → create_evidence_series_version | Identity routing reaches direct/underlying guards; identity changes grant no additional status permission |
| Direct replacement | create_replacement_evidence_series | Actual caller-selected exact prior, after existing COMMITTED replay resolution, before lower create |
| Underlying create with predecessor | create_evidence_series_version | Loads actual supersedes exact prior, preserves missing-exact error, validates before any new series/version/children/key/audit |

The shared helper is `_validate_ordinary_correction_prior`. Predecessor-free initial create and non-correction lifecycle appends retain their previous behavior. Existing invalid non-None trusted-rule validation remains fail-closed; production approved rule collection remains empty. No caller permission flag, rule registration, terminal restoration, latest-prior enforcement or new support policy was added.

## PostgreSQL persistence, history, routing and replay proofs

Final focused suite has **41 scenarios**:

| Node family | Scenarios | Evidence |
| --- | --- | --- |
| test_r1c05c01_forbidden_status_commit_fresh_no_residue | 20 | Five forbidden actual statuses × four paths; exact domain class/code/details; clean pending ORM state; caller commit; distinct fresh-session nine-table complete equality |
| test_r1c05c01_allowed_routing_history_audit | 16 | VERIFIED/UNREVIEWED × four paths × omitted/explicit None rule; persisted tuple, routing, children, status, strict audit and lawful review |
| test_r1c05c01_committed_exact_replay_read_only | 3 | automatic/direct/underlying exact response ID; caller commit; fresh-session all-nine-table equality |
| test_r1c05c01_legacy_forbidden_prior_committed_replay | 2 | Disclosed test-owned ORM COMMITTED history seed for direct/underlying PENDING_REVIEW prior; matching replay reads historical response; fresh new key denied with no residue |

Every negative uses lawful public status transitions and commits setup before the baseline. The nine models are SourceDocument, SourceDocumentVersion, EvidenceSeries, EvidenceVersion, EvidenceSourceLocator, EvidenceInstrumentLink, EvidenceDerivationLink, EvidenceIdempotencyRecord and EvidenceAuditEvent. Snapshot helper `r1c05c01_rows` selects every column of all nine fixture-domain tables in primary-key order. It compares full row dictionaries, not counts. Rejection is followed by caller commit, then an independent session compares the entire snapshot, old exact version/immutable children/current prior and audit. Both attempted outer and `:inner` keys are absent. `final2-focused-proof.json` records all 20 equal before/fresh hashes; the source test asserts full equality before printing hashes.

Automatic setup constructs alternate support via ordinary correction → request_review → verify_or_reject(VERIFIED), using each actual returned exact ID. Initial support and alternate support are distinct; neither has derived links. The DERIVED prior uses original support, and correction changes to alternate exact support. Positive persisted series identity hash and origin key differ, result is a new series version 1, exact supersedes is the selected prior, and derived support is exactly the returned alternate ID, with no exact self/cycle. All support setup completes and commits before no-residue baseline. Exact IDs are retained in the focused log and proof artifact.

Positive same-series results are N+1; the other three routes create new series v1. All persisted results are UNREVIEWED with trusted_correction_rule=None and full CORRECTION tuple (known timestamp, USER status actor, CORRECTION, known reason), exact predecessor and independently cloned children. Original rows and children remain unchanged. Current-valid query returns None for these UNREVIEWED results under existing behavior; no new DERIVED support-status admission predicate was introduced. Explicit request_review and verify_or_reject remain legal.

Audit assertions keep exact aggregate, event count, actor, timestamp and complete canonical payload: same-series EVIDENCE_CORRECTION; replacement EVIDENCE_VERSION_CREATED plus EVIDENCE_SERIES_CREATED. Distinct known creator inputs verify command ownership: same USER; automatic USER for reviewed VERIFIED prior and IMPORTER for untouched UNREVIEWED prior; direct SYSTEM; underlying ADMIN_SCRIPT. Underlying created_at is independently distinct from status_changed_at. Persisted row status and existing request payload semantics are both checked.

Legacy ORM setup is explicitly historical compatibility data, not a production bypass or positive new write from a forbidden status. No validator monkeypatch, positive trusted rule or runtime hook is used. Same-series stale expected-version replay behavior is retained without expanding its guarantee.

## Intermediate diagnostics retained

The first post-fix focused run had 39 passed and 2 failures in new automatic VERIFIED positive audit expectations: lawful public review makes the prior creator USER, and automatic replacement preserves that actor. The new oracle had incorrectly expected IMPORTER. Only the appended test expectation was corrected to the actual known command ownership; audit class/count/payload/history assertions remain strict, services stayed unchanged. `focused-green.log` preserves this diagnostic run. Subsequent `focused-final-green` had 41 passed.

The first complete matrix reached mypy after all DB suites succeeded and reported 38 arg-type errors, all in the newly appended command helper's expanded dictionaries. Explicit dict[str, Any] annotations were added for its rule/audit/children arguments; no command input, expected assertion, old test or service line changed. Final static checks succeeded and the full DB matrix was then repeated at the final test hash. The original mypy.log is retained. A hash-guarded edit attempt stopped without writing because its prefix calculation included the two newly added separator blank lines; the guard was corrected to hash only the original prefix, which matched the frozen original SHA.

Ruff initially identified C408 in a newly appended test's dict constructor; it was replaced with a dict literal. Ruff format touched only the appended tests; original test prefix remains byte-identical. Final matrix was rerun at the final business hashes after these edits. Neither intermediate issue is represented as a business-code RED or hidden by changing an old test.

## Environment, permissions and cleanup

Existing tools were inspected, not installed/upgraded:

| Tool | Actual executable | Version |
| --- | --- | --- |
| Python | /opt/homebrew/bin/python3.12 | 3.12.9 |
| pytest | /opt/homebrew/bin/pytest (Python 3.12 shebang) | 9.1.1 |
| Ruff | /opt/miniconda3/bin/ruff | 0.16.1 |
| mypy | /opt/miniconda3/bin/mypy | 2.3.0 |
| Alembic | /opt/miniconda3/bin/alembic | 1.18.5 |

Libraries: pytest-asyncio 1.4.0, asyncpg 0.31.0, SQLAlchemy 2.0.52, boto3 1.43.93. The unused default Python 3.14.6 probe lacked pytest metadata (exit 1); existing Python 3.12 was located instead. This probe was not test RED.

DB runs used normal require_escalated approval for the authorized existing local disposable fixture, unchanged 127.0.0.1:15432; observed server 17.11. No substitute instance, host/port override, proxy, container operation, extra SQL, manual cleanup or standalone migration command was executed. Existing fixture bootstrap/teardown ran unchanged for its disposable test database; the regression matrix includes migration tests under their existing fixtures. Alembic heads was an inspection only.

The runner asserts TG_TEST_ADMIN_DATABASE_URL, TG_R1C_REPLAY_BASELINE and TG_R1C02_REPLAY_PRIOR absent on every normal command. PYTHONDONTWRITEBYTECODE=1; candidate PYTHONPATH plus inspected existing Homebrew site-packages; mypy MYPYPATH=.; temporary mypy/compile caches are outside candidate. Complete effective environment and UTC start/end are in each command metadata. All completed test runs, including RED, have no pytest setup/teardown ERROR or cleanup failure, and final suites report no skips/xfails. Existing FastAPI/Starlette deprecation warnings remain where reported.

## Actual commands and results

All test/static commands ran in candidate cwd. The command manifest contains exact executable argv (including durable main verifier paths), environment, UTC times, exit codes and complete stdout SHA-256. Individual .log files preserve raw combined stdout/stderr; .json files preserve command metadata. The final matrix results follow.

| Final run | Result | Exit | Complete log |
| --- | --- | --- | --- |
| final2-focused-final-hash | 41 passed, 337 deselected, 2 warnings in 42.25s | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-focused-final-hash.log) |
| final2-preserve-r1c05a | 11 passed, 367 deselected, 2 warnings in 8.03s | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-preserve-r1c05a.log) |
| final2-preserve-r1c04a | 87 passed, 291 deselected, 2 warnings in 73.78s (0:01:13) | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-preserve-r1c04a.log) |
| final2-verifier-tuple | 4 passed in 3.54s | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-verifier-tuple.log) |
| final2-verifier-oracle | 58 passed in 50.10s | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-verifier-oracle.log) |
| final2-verifier-five | 70 passed in 60.11s (0:01:00) | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-verifier-five.log) |
| final2-full-service | 378 passed, 2 warnings in 317.28s (0:05:17) | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-full-service.log) |
| final2-regression | 35 passed, 4 warnings in 23.29s | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-regression.log) |
| final2-ruff | All checks passed! | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-ruff.log) |
| final2-format | 3 files already formatted | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-format.log) |
| final2-mypy | Success: no issues found in 3 source files | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-mypy.log) |
| final2-compileall | No output; successful exit | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-compileall.log) |
| final2-alembic-heads | 000000000004 (head) | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-alembic-heads.log) |
| final2-diff-check | No output; successful exit | 0 | [log](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-diff-check.log) |

The original five-verifier run covers R1C-02 43, R1C-01 8, R1B wiring 3, R1B reverify 4 and R1A 12 actual nodes. These totals supplement the preserved raw results and hashes.

All actual logged command results, including RED and intermediate diagnostics:

| Run | Exit | Metadata |
| --- | --- | --- |
| red-two | 1 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/red-two.json) |
| red-all20 | 1 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/red-all20.json) |
| focused-green | 1 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/focused-green.json) |
| focused-final-green | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/focused-final-green.json) |
| focused-final-hash | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/focused-final-hash.json) |
| preserve-r1c05a | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/preserve-r1c05a.json) |
| preserve-r1c04a | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/preserve-r1c04a.json) |
| verifier-tuple | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/verifier-tuple.json) |
| verifier-oracle | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/verifier-oracle.json) |
| verifier-five | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/verifier-five.json) |
| full-service | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/full-service.json) |
| regression | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/regression.json) |
| ruff | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/ruff.json) |
| format | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/format.json) |
| mypy | 1 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/mypy.json) |
| final2-ruff | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-ruff.json) |
| final2-format | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-format.json) |
| final2-mypy | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-mypy.json) |
| final2-compileall | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-compileall.json) |
| final2-alembic-heads | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-alembic-heads.json) |
| final2-diff-check | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-diff-check.json) |
| final2-focused-final-hash | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-focused-final-hash.json) |
| final2-preserve-r1c05a | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-preserve-r1c05a.json) |
| final2-preserve-r1c04a | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-preserve-r1c04a.json) |
| final-candidate-branch | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final-candidate-branch.json) |
| final-candidate-head-parent | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final-candidate-head-parent.json) |
| final-candidate-status | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final-candidate-status.json) |
| final-candidate-diff-stat | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final-candidate-diff-stat.json) |
| final-candidate-index | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final-candidate-index.json) |
| final-candidate-hashes | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final-candidate-hashes.json) |
| final2-verifier-tuple | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-verifier-tuple.json) |
| final2-verifier-oracle | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-verifier-oracle.json) |
| final2-verifier-five | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-verifier-five.json) |
| final2-full-service | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-full-service.json) |
| final2-regression | 0 | [argv/env/time/hash](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-regression.json) |

Exact final matrix argv follows (effective environment is preserved in metadata):


final2-focused-final-hash:

```bash
/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1c05c01 -s -rs
```

final2-preserve-r1c05a:

```bash
/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1c05a -rs
```

final2-preserve-r1c04a:

```bash
/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1c04a -rs
```

final2-verifier-tuple:

```bash
/opt/homebrew/bin/pytest -p no:cacheprovider -q /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c05a_audit_tuple_replay_r1_20260916.py -rs
```

final2-verifier-oracle:

```bash
/opt/homebrew/bin/pytest -p no:cacheprovider -q /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py -rs
```

final2-verifier-five:

```bash
/opt/homebrew/bin/pytest -p no:cacheprovider -q /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c_02_independent_20260915.py /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c_01_independent_20260915.py /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1b_r1_wiring_20260915.py /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1b_reverify.py /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1a_verifier.py -rs
```

final2-full-service:

```bash
/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
```

final2-regression:

```bash
/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
```

final2-ruff:

```bash
/opt/miniconda3/bin/ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

final2-format:

```bash
/opt/miniconda3/bin/ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

final2-mypy:

```bash
/opt/miniconda3/bin/mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c05c01-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

final2-compileall:

```bash
/opt/homebrew/bin/python3.12 -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

final2-alembic-heads:

```bash
/opt/miniconda3/bin/alembic -c migrations/alembic.ini heads
```

final2-diff-check:

```bash
git diff --check
```

## Protected verifier hashes

| Original durable verifier | Unchanged SHA-256 |
| --- | --- |
| test_wp04_02_r1c_02_independent_20260915.py | 64162c0aafc3ad620ee0cab5e4d8d0ed10e6d61ab8dc21322f4364144c442a05 |
| test_wp04_02_r1c_01_independent_20260915.py | 857914f073c552be98f895a456d2f0ec486452e1c9aed06a87176c6e7fefd48a |
| test_wp04_02_r1b_r1_wiring_20260915.py | 909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786 |
| test_wp04_02_r1b_reverify.py | 0f7cea4d14735bd165b75d756444259a64483a97e6a338227bc09af806490cc9 |
| test_wp04_02_r1a_verifier.py | 66be45f354d1df34370eedd9811b3bc68cf29852d45027ea576a67975b18ddfe |
| test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py | 0ae19f9103b328afc3f7b5b017390569ead2a5239f18765d8c82f369d8818b0b |
| test_wp04_02_r1c05a_audit_tuple_replay_r1_20260916.py | be68779f161c5983fce265bafe0b8237ae881feea7900a446c07ff03433ffb60 |

## Artifacts and final boundary

- [Initial protected snapshot](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/baseline-protected.json)
- [Environment inspection](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/environment.json)
- [Final command manifest](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/command-manifest.json)
- [Final focused persistence/routing proofs](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-focused-proof.json)
- [Final task-only scope/prefix evidence](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final2-task-scope.json)
- [Task-only service diff](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/service-task-diff.patch)
- [Final scope/identity/protection and whitespace gate](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/final-protection.json)
- [Complete new-artifact hash inventory](/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-evidence/artifact-manifest.json)

New persistent artifacts are limited to this execution report and its dedicated evidence directory; the artifact manifest enumerates every file and SHA-256, excluding its own bytes to avoid a circular hash. It also records the report SHA. No previous evidence was replaced. Final document UTF-8/LF/trailing-whitespace checks and git diff whitespace checks are recorded in final-protection.json.

Only the 05C-01 from-status admission candidate is implemented. 05C-02 current-highest exact-prior enforcement, remaining qualification policies and trusted success rules, R1D request identity/replay ordering/race/atomicity/reconciliation/UNKNOWN_OUTCOME, and final independent full WP04-02 acceptance remain incomplete. Production approved trusted-rule collection is empty. No whole R1C/WP04-02 completion, terminal restoration, Git integration, API or Agent authorization is claimed. Await independent acceptance.
