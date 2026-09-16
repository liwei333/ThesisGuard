# TASK-WP04-02-R1C-02 — Independent Acceptance

Date: 2026-09-15 (Asia/Shanghai)

OVERALL: `PASS`

Task: `TASK-WP04-02-R1C-02 — Lifecycle Command Matrix Repair`.

Required / Achieved: `L1_STATIC_REVIEWED / L2_BUILD_VERIFIED / L3_CONTRACT_VERIFIED / L4_DB_VERIFIED`, Full verification matrix.

This decision closes only R1C-02. It does not close all of R1C, R1D, WP04-02, or WP-04, and does not authorize Git integration or activation of trusted correction rules.

## 1. Context and baseline

Input feedback: `/Users/qianduoduo/.codex/attachments/772f8ff8-671f-436a-86ac-315a1a9a10fa/pasted-text.txt`.

Authority: main AGENTS.md, frozen `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`, original R1 repair program, and `docs/acceptance/TASK-WP04-02-R1C-02-task-contract.md`. Historical PASS records are regression context, not substitutes for fresh commands.

Main repository: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard`, HEAD `7d3734bc8346c16f9bbf7f7d9806309949c996de` at inspection.

Candidate: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`.

```text
branch: codex/wp04-02-evidence-domain-service
HEAD:   bdd70edc153b6ed5def65ed99c41f325df45f066
parent: f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af
 M backend/evidence/services.py
 M tests/test_evidence_services.py
```

The two modified files are the expected cumulative, uncommitted R1C-01/R1C-02 candidate. This is not a clean-baseline task. No candidate file was changed during this acceptance.

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
5419448d3b73c0c0e2c1144d7615cdbe399266be5b9dd70281d91cf1a485d632  backend/evidence/services.py
b4a03614a02629efbfe46428778b54c2539c2ce897af7499cba439a99f7d7c59  tests/test_evidence_services.py
909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786  /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
0f7cea4d14735bd165b75d756444259a64483a97e6a338227bc09af806490cc9  /tmp/test_wp04_02_r1b_reverify.py
66be45f354d1df34370eedd9811b3bc68cf29852d45027ea576a67975b18ddfe  /tmp/test_wp04_02_r1a_verifier.py
857914f073c552be98f895a456d2f0ec486452e1c9aed06a87176c6e7fefd48a  /tmp/test_wp04_02_r1c_01_independent_20260915.py
```

The cumulative diff against HEAD contains only the two expected files: 655 insertions, 16 deletions. It includes previously accepted R1C-01 work; these totals are not attributed entirely to R1C-02.

## 2. Contract and architecture review

The public lifecycle commands now implement the frozen status matrix, not a broad nonterminal-state shortcut:

| Command / decision | Allowed prior states | New state | Status-change kind |
| --- | --- | --- | --- |
| request_review | UNREVIEWED | PENDING_REVIEW | REVIEW_REQUEST |
| verify_or_reject / VERIFIED | PENDING_REVIEW | VERIFIED | REVIEW_DECISION |
| verify_or_reject / VERIFIED | DISPUTED | VERIFIED | DISPUTE |
| verify_or_reject / REJECTED | UNREVIEWED, PENDING_REVIEW | REJECTED | REVIEW_DECISION |
| verify_or_reject / REJECTED | DISPUTED | REJECTED | DISPUTE |
| mark_disputed | VERIFIED | DISPUTED | DISPUTE |
| retract_or_invalidate / INVALIDATED | VERIFIED | INVALIDATED | INVALIDATION |
| retract_or_invalidate / RETRACTED | VERIFIED, DISPUTED | RETRACTED | RETRACTION |

All other combinations of the seven statuses and six command/decision variants are rejected with the stable lifecycle error. DISPUTED → INVALIDATED is prohibited; DISPUTED → RETRACTED and DISPUTED → review resolution remain legitimate.

The private status-command helper selects a from-state-aware audit kind only after normal replay, expected-version and transition checks. It does not introduce a second bypassing write path or commit caller transactions. New status versions remain append-only and copy immutable children to distinct IDs. Existing replay ordering is retained.

Test changes to prior lifecycle and R1B replacement fixtures are legitimate contract corrections: disputed invalidation was replaced by disputed retraction, and a replacement is reviewed/verified before invalidation. Exact-target, routing, historical children and append-only assertions remain tested. Prior R1C-01 latest-first current-valid behavior remains unchanged.

## 3. Blocking AC evidence matrix

| Blocking requirement | Independent evidence | Result |
| --- | --- | --- |
| Exact lifecycle command matrix | Own 7-state × 6-command verifier: 42 cases, 10 legal and 32 illegal | PASS |
| Correct audit tuple including disputed review resolution | Legal cases commit, read fresh session, inspect exact persisted audit and status fields: kind/from/to/actor/time/reason | PASS |
| Append-only historical versions and immutable children | Fresh-session version/history/status, content/link/locator equality and distinct child IDs | PASS |
| Illegal-input no-residue, replay and caller transaction ownership | Illegal cases commit after rejection then compare persisted row counts/current version; legal cross-session replay adds no rows; separate caller rollback case restores prior state | PASS |
| Previous repairs and bounded scope | Fresh R1C-01, R1A/R1B verifiers, full services/regressions/statics; candidate HEAD, errors and verifier hashes unchanged | PASS |

Own verifier: `/tmp/test_wp04_02_r1c_02_independent_20260915.py`.

Final SHA-256: `64162c0aafc3ad620ee0cab5e4d8d0ed10e6d61ab8dc21322f4364144c442a05`.

It defines its own legal-transition oracle rather than deriving expectations from production allowed sets. It reuses the candidate PostgreSQL fixture and state-construction helper; assertions, matrix, persisted audit checks, cross-session replay and rollback are verifier-owned. This shared fixture dependency is disclosed, not presented as a wholly independent infrastructure implementation.

## 4. Fresh verification results

DB commands were run from the candidate worktree through the normal escalated permission mechanism against the existing local disposable PostgreSQL fixture route. Common prefix:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q
```

Each table row below was actually executed in this acceptance, not copied from execution feedback. Test commands include `-rs`.

| Target / command | Fresh result | Exit |
| --- | --- | --- |
| tests/test_evidence_services.py -k "r1c or current_valid or lifecycle or state_transition" | 55 passed, 97 deselected, 2 warnings; 45.83s | 0 |
| /tmp/test_wp04_02_r1c_02_independent_20260915.py, final normal run | 43 passed; 32.34s | 0 |
| /tmp/test_wp04_02_r1c_01_independent_20260915.py | 8 passed; 6.34s | 0 |
| /tmp/test_wp04_02_r1b_r1_wiring_20260915.py | 3 passed; 2.81s | 0 |
| /tmp/test_wp04_02_r1b_reverify.py | 4 passed; 3.43s | 0 |
| /tmp/test_wp04_02_r1a_verifier.py | 12 passed; 6.47s | 0 |
| tests/test_evidence_services.py | 152 passed, 2 warnings; 110.76s | 0 |
| tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py | 35 passed, 4 warnings; 21.89s | 0 |
| ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py | All checks passed | 0 |
| ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py | 3 files already formatted | 0 |
| MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c-02-independent-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py | No issues in 3 source files; existing unused configuration-section note | 0 |
| PYTHONPYCACHEPREFIX=/tmp/tg-r1c-02-independent-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py | Passed | 0 |
| alembic -c migrations/alembic.ini heads | 000000000004 (head) | 0 |
| git diff --check | No output | 0 |

### Red-to-green evidence qualification

The executor's historical test-before-repair RED is input evidence, not a newly observed original worktree run. Acceptance additionally ran its own controlled prior-behavior diagnostic:

```bash
TG_R1C02_REPLAY_PRIOR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1c_02_independent_20260915.py -rs
```

Expected RED: **12 failed, 31 passed, exit 1, 32.31s**. These were semantic assertion/domain-error failures, not DB setup or permission failures. The diagnostic reconstructs the old broader allowed-from sets and old audit-kind behavior using an in-process wrapper around the production status helper. It does not restore original source blobs or prove the executor's chronological actions. No candidate file or old verifier was edited.

The 12 deltas cover unreviewed rejection, disallowed dispute/invalidation/retraction transitions, and disputed review-resolution audit classification. The final ordinary command, with diagnostic disabled, passed **43/43** on real PostgreSQL.

## 5. Persistence and permission limits

Fixture/default route inspection confirms local `127.0.0.1:15432`; no provider/host/port substitution, Docker/proxy workaround, arbitrary SQL or broad DB cleanup was performed. `printenv TG_TEST_ADMIN_DATABASE_URL TG_R1C_REPLAY_BASELINE TG_R1C02_REPLAY_PRIOR` returned no values at final environment inspection. The diagnostic variable was scoped only to the explicitly identified diagnostic command.

No fixture setup/cleanup exception was observed in these completed runs. There is no known temporary-database residual report. This is not a claim that a separate comprehensive cluster-residue scan was performed.

## 6. Files and remaining boundaries

This acceptance created this report, the next `TASK-WP04-02-R1C-03A-task-contract.md`, and the new `/tmp` verifier. It preserved all ten pre-existing main-worktree untracked documentation files. No candidate business file, previous report/contract/verifier, models, repository, schema, migration, API, or Git history was changed. No commit, merge, rebase, reset, checkout, fetch or push was performed.

Remaining work is explicit:

- Trusted correction admission and implicit prior-rule inheritance remain unsafe; R1C-03A is the next minimal repair.
- No concrete production trusted correction rule predicate has been approved by the documents inspected. R1C-03A therefore enables no positive rule; it rejects unapproved requests and makes ordinary correction UNREVIEWED with rule=None, without rewriting history. This is a bounded fail-closed policy repair, not a complete trusted registry/validator implementation.
- Positive named-rule activation and semantic validators, initial import qualifications and the complete ordinary-correction eligibility matrix need subsequent precise contracts and evidence.
- R1D idempotency/replacement atomicity/concurrency/UNKNOWN_OUTCOME and final independent WP04-02 reverification are not closed.
- Evidence API/OpenAPI and Research exact Evidence references remain later work. Sector Crowding and Capability Runtime are not unlocked by this PASS.

Next dispatch authority: `docs/acceptance/TASK-WP04-02-R1C-03A-task-contract.md`; execution still waits for user dispatch and normal permissions.
