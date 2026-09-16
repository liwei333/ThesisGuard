# TASK-WP04-02-R1C-03A — Independent Acceptance

## Metadata

- OVERALL: `BLOCKED`.
- Task: `TASK-WP04-02-R1C-03A — Trusted Correction Admission / No Implicit Inheritance`.
- Date: 2026-09-16 (Asia/Shanghai).
- Verifier: Codex, independent VERIFIER role; executor feedback treated as clues only.
- Report path: `docs/acceptance/TASK-WP04-02-R1C-03A-acceptance.md`, following the project's existing docs/acceptance convention and AGENTS authority map.
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`.
- Missing Acceptance: `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`; real DB and mandatory historical verifier regression could not be completed.
- Implementation status: executor reports `IMPLEMENTATION_COMPLETE`; this report does not approve it or close R1C-03A.
- Repair Required: no business repair proven in this inspection; verification prerequisites require restoration and independent reverify.

## Baseline and attribution

Input: `/Users/qianduoduo/.codex/attachments/5f39c044-4806-4bfe-8c98-02fec3f384e2/pasted-text.txt`.

Main: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard`, HEAD `7d3734bc8346c16f9bbf7f7d9806309949c996de` at inspection.

Candidate: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`.

```text
branch: codex/wp04-02-evidence-domain-service
HEAD: bdd70edc153b6ed5def65ed99c41f325df45f066
parent: f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af
 M backend/evidence/services.py
 M tests/test_evidence_services.py
```

BASELINE_CHANGED_FILES and FINAL_CHANGED_FILES are those same two modified candidate files. Task-attributable candidate changes in this verification: NONE. Main initially had twelve untracked documentation files; all were preserved. This verification adds only this report and the next prerequisite/reverify contract. No Git or database-environment mutation was performed.

Fresh hashes match the executor's final candidate:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
43b548232df4267f377c5e144222c9278c3cc478f6800720240c4618b689ebe3  backend/evidence/services.py
47ff645c0f782af67e9f6ee64520105febdb28c6547a43bf89b435bead6c5108  tests/test_evidence_services.py
```

Cumulative diff vs candidate HEAD: services 78 insertions/11 deletions, tests 1058 insertions/14 deletions, exactly two files. This includes R1C-01 and R1C-02, not just R1C-03A. Executor's claimed per-turn 58/6 and 423/3 are not independently certified from an available pre-turn file snapshot. Review identifies the R1C-03A changes by symbols and test section; chronological execution and historical RED remain source-reported evidence.

## Classification and gates

Task Type: REPAIR. Risk: evidence eligibility, DB integrity, audit, transaction, replay. Layers: service and tests. Size: SMALL single admission boundary, with high-risk Full Evidence Matrix.

| Gate | Verdict | Evidence / limit |
| --- | --- | --- |
| G0 Baseline | BLOCKED | Candidate HEAD/files match; five mandatory verifier artifacts are absent |
| G1 Scope | PASS | Only the two authorized candidate files differ; static inspection found no production rule activation/config/registry injection |
| G2 Contract | BLOCKED | Implementation and test assertions inspected; full real-persistence AC proof unavailable |
| G3 Architecture | PASS | Empty immutable allowlist; no caller commit; normal service ownership and old status paths retained, by static review only |
| G4 Test | BLOCKED | Static checks complete; DB suites stop in fixture connection; fixed verifiers missing |
| DB Persistence | BLOCKED | No successful real-PostgreSQL mutation/replay/no-residue verification in this turn |
| G5 Regression | BLOCKED | Service/regression DB tests not exercised; five prior independent verifiers unavailable |
| G6 Evidence | BLOCKED | L3/L4 evidence cannot be collected under current prerequisites |

UI/browser, worker, API implementation and migration-change gates are not applicable to this two-file service repair.

## Full Top Blocking AC Matrix

| AC | Requirement | Implementation evidence | Fresh verification | Boundary / negative evidence | Verdict |
| --- | --- | --- | --- | --- | --- |
| 1 | All correction/create entrances reject unapproved rules | services.py:691/694 create; :1178/1181 replacement; :1402-1428 append; :1530 validator | Pure helper check rejects 12 illegal input samples with stable error/details | Five entry-point candidate tests inspected; DB fixture unavailable, so helper check is not route/transaction proof | BLOCKED |
| 2 | Ordinary correction is UNREVIEWED with rule=None, no inheritance; routing/audit retained | services.py:877 fallback None; :695 predecessor handling; :1428 status; :1478 rule copy boundary | Candidate eight omitted/None tests statically inspected | Legacy prior is a complete append-only seed; historical fields asserted intact, but not freshly proved in PG | BLOCKED |
| 3 | Rejected requests leave no series/version/children/idempotency/audit residue after caller commit | Validator precedes service write/savepoint on new requests | Candidate seventy-five negative nodes explicitly commit after error and read fresh session | Connection refused before test assertions; no-residue cannot be inferred from test presence | BLOCKED |
| 4 | Real RED/GREEN and prior Full verification matrix | Test fixtures adjusted according to explicit contract; replay guard prevents a new rule borrowing ordinary key | Ruff/mypy/compile/head checks pass; no HEAD test function removed | Executor's chronological RED and 239/35 green results are historical input only; this turn's PG matrix unavailable | BLOCKED |
| 5 | Two-file scope, errors/HEAD fixed, no fake positive trusted capability | Empty frozenset, no production named rule enabled, no public injection introduced | Fresh hashes/status/HEAD and diff; errors unchanged | Five /tmp artifacts cannot be rehashed because absent; overall R1C/WP04-02 not closed | BLOCKED |

## Commands actually executed

DB commands used this exact prefix from the candidate:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q
```

| Command / target | Actual result | Exit |
| --- | --- | --- |
| Focused service, -k "r1c or trusted or current_valid or lifecycle or state_transition" -rs, sandbox attempt | 142 fixture errors, 97 deselected, 2 warnings; PermissionError before assertions | 1 |
| Same focused command, normal approved escalation | 142 fixture errors, 97 deselected, 2 warnings; ConnectionRefusedError at 127.0.0.1:15432; 15.16s | 1 |
| tests/test_evidence_services.py -rs, normal approved escalation | 2 passed, 237 fixture errors, 2 warnings; ConnectionRefusedError; 26.67s | 1 |
| tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs, normal approved escalation | 4 passed, 7 skipped, 24 fixture errors, 2 warnings; ConnectionRefusedError; 2.36s | 1 |
| shasum -a 256, three candidate and five fixed verifier files | Three candidate hashes match; all five verifier paths report No such file | 1 |
| rg --files -g '*verif*' -g '*r1c*' -g '*r1b*', /private/tmp, main and candidate | No matching recoverable verifier artifacts found in these scoped roots | 1 |
| /usr/sbin/lsof -nP -iTCP:15432 -sTCP:LISTEN | No listener output in this inspection | 1 |
| /opt/miniconda3/bin/ruff check --no-cache, three files | All checks passed | 0 |
| /opt/miniconda3/bin/ruff format --check --no-cache, three files | 3 files already formatted | 0 |
| MYPYPATH=. /opt/miniconda3/bin/mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c03a-independent-mypy, three files | No issues in 3 source files; existing unused-section note | 0 |
| PYTHONPYCACHEPREFIX=/tmp/tg-r1c03a-independent-pycache /opt/miniconda3/bin/python -m compileall -q, three files | No errors | 0 |
| /opt/miniconda3/bin/alembic -c migrations/alembic.ini heads | 000000000004 (head); metadata inspection, not a DB migration/runtime proof | 0 |
| git diff --check; git status; git rev-parse HEAD HEAD^; git diff --numstat | Scope and fixed candidate baseline confirmed | 0 |
| Pure Python check of validator: empty/blank/unknown/two old fixture strings, integer, boolean, list, mapping, bytes, set, object; None | 12 unapproved inputs rejected; None accepted; allowlist empty | 0 |
| AST comparison of HEAD/current test function names | No HEAD test function removed | 0 |
| printenv TG_TEST_ADMIN_DATABASE_URL TG_R1C_REPLAY_BASELINE TG_R1C02_REPLAY_PRIOR | No values returned in inspected environment | 1 |

Three static-file arguments are backend/evidence/errors.py, backend/evidence/services.py, tests/test_evidence_services.py. Bare ruff/mypy/python/alembic first returned command-not-found in candidate shell resolution; existing absolute /opt/miniconda3/bin tools were then used successfully. No installation or dependency upgrade occurred. DB pytest resolved the existing Homebrew Python 3.12 environment; this runtime difference must be recorded during resumed verification.

Large repeated connection-error outputs were truncated by output limits; root connection stack, exit codes and complete terminal summaries were available. No errors are treated as successful assertions. Seven Research skips are missing DB coverage, not passed regression.

## Blocking prerequisites

1. Existing local fixture PostgreSQL endpoint refuses connection after normal escalation. Permission approval was not rejected. Fixture stops at asyncpg.connect before CREATE DATABASE; these failed attempts did not reach fixture temporary database creation. The reason the endpoint is down was not established; do not assume data deletion or a specific container failure.
2. These original fixed verifiers are absent:

```text
909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786  /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
0f7cea4d14735bd165b75d756444259a64483a97e6a338227bc09af806490cc9  /tmp/test_wp04_02_r1b_reverify.py
66be45f354d1df34370eedd9811b3bc68cf29852d45027ea576a67975b18ddfe  /tmp/test_wp04_02_r1a_verifier.py
857914f073c552be98f895a456d2f0ec486452e1c9aed06a87176c6e7fefd48a  /tmp/test_wp04_02_r1c_01_independent_20260915.py
64162c0aafc3ad620ee0cab5e4d8d0ed10e6d61ab8dc21322f4364144c442a05  /tmp/test_wp04_02_r1c_02_independent_20260915.py
```

The missing originals were not regenerated, edited or substituted with candidate tests. Historical R1A/R1B/R1C-01/R1C-02 PASS remains historical and unchanged. Missing /tmp files do not prove the executor deleted them or invalidate historical runs.

## Decision and next action

No blocking business defect was independently demonstrated in the static/pure-helper inspection. This is **BLOCKED**, not a semantic FAIL and not a conditional PASS. Current persistence, no-residue, replay and regression behavior remain unverified at the required levels.

Next task: `TASK-WP04-02-R1C-03A-VERIFY-PREREQUISITES-R1`, restore the existing verification endpoint and original hash-locked verifier artifacts, then reverify the unchanged candidate. If authoritative originals cannot be recovered, dispatcher/user must authorize a separately versioned replacement-verifier contract; do not weaken the old task or silently recreate its fixed artifacts.

R1C-03B/positive rule activation, initial import qualification, ordinary correction full eligibility, R1D, final WP04-02 closure and Git integration remain unstarted by this report. Sector Crowding and Capability Runtime remain deferred.
