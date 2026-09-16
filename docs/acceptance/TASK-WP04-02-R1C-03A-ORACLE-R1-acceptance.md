# TASK-WP04-02-R1C-03A-ORACLE-R1 — Independent Acceptance

**OVERALL: PASS**

## Metadata and decision boundary

- Task ID: TASK-WP04-02-R1C-03A-ORACLE-R1.
- Date: 2026-09-16, Asia/Shanghai.
- Verifier: Codex, logically separate independent VERIFIER; executor narrative used as investigative input, not a verdict.
- Report path: docs/acceptance/TASK-WP04-02-R1C-03A-ORACLE-R1-acceptance.md, following AGENTS and the existing project acceptance convention.
- Implementation status received: IMPLEMENTATION_COMPLETE.
- Required / Achieved Acceptance: L1_STATIC_REVIEWED, L2_BUILD_VERIFIED, L3_CONTRACT_VERIFIED, L4_DB_VERIFIED.
- Missing Acceptance within this verifier-repair task: NONE.
- Repair Required: NO.
- Classification: VERIFIER_REPAIR, MEDIUM; audit, exact-version lineage, idempotency and real persistence risks; tests/documentation touched; Full Evidence Matrix.

This PASS closes VF-01/VF-02 and the verifier-only repair/reverify boundary. The restored prerequisites and independent tests now also support accepting R1C-03A's **empty production approval / reject unapproved requests / no implicit correction inheritance** slice on the explicitly adopted clean candidate. It does not certify positive trusted correction, initial import qualification, every ordinary-correction source-state qualification, whole R1C, R1D or whole WP04-02. It grants no Git integration authority.

The old BLOCKED and FAIL reports remain immutable historical records. This report supplies the later resolution; it does not rewrite them or reinterpret old verifier RED as a business defect.

## Baseline and changed-file snapshot

```text
main path: /Users/qianduoduo/Desktop/AI_app/ThesisGuard
main HEAD: 438738c543e4cae3e805d31324b068c1cd5c7059
main parent: 7d3734bc8346c16f9bbf7f7d9806309949c996de
candidate path: /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service
candidate branch: codex/wp04-02-evidence-domain-service
candidate HEAD: 0cef44fd2ffd929b40e849e607af0bd4c44d14d2
candidate parent: bdd70edc153b6ed5def65ed99c41f325df45f066
candidate status: clean before and after independent DB tests
```

The adopted pre-existing candidate commit contains services.py and tests/test_evidence_services.py only. This task did not create it. Main tracked/index differences remain empty; project additions are untracked governance/verifier artifacts, not business changes.

Freshly checked before/after independent tests:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
43b548232df4267f377c5e144222c9278c3cc478f6800720240c4618b689ebe3  backend/evidence/services.py
47ff645c0f782af67e9f6ee64520105febdb28c6547a43bf89b435bead6c5108  tests/test_evidence_services.py
0ae19f9103b328afc3f7b5b017390569ead2a5239f18765d8c82f369d8818b0b  new R1 oracle
976d1fa24a92fe40180fd7ff7582a29ebb5450bced74c1127c93c82fed9370d5  submitted evidence-manifest.json
```

- BASELINE_CHANGED_FILES at verifier start: untracked original repair contract, prerequisite acceptance, R1 execution report, new R1 oracle and R1 evidence directory. Candidate NONE.
- Executor attributable changes: new R1 oracle plus its execution report and task-specific evidence. Protection snapshots and actual current hashes agree on all 82 protected paths.
- FINAL_CHANGED_FILES for this independent review: the above preserved artifacts, this new acceptance and next draft-rule task contract. Candidate NONE.
- Independent review attributable changes: two new governance documents only. No old evidence edits, business edits or Git writes.
- Attribution of this task's additions: CERTAIN from allowed paths and before/after evidence; no claim to reconstruct all historical terminal/Git activity.

## Contract, source and oracle review

Read the immutable R1 repair contract, execution report, original R1C-03A contract and historical acceptance, R1 repair program, frozen sections12/13/21/22 and relevant actual service/fixture code.

VF-01: new oracle prepare() builds four distinct real support IDs using public ordinary correction, request_review and verify_or_reject. Initial FACT v1 legitimately has no predecessor. Assertions check v1→v2→v3→v4 exact predecessor chain, immutable initial snapshot, latest support eligibility, old DERIVED origin versus independent origin_for(new exact support), source-backed leaf support and a graph traversal detecting exact cycles. The setup commits before no-residue snapshots. command() supplies the actual new VERIFIED support ID to production revise; no production function/rule monkeypatch is used.

VF-02: assert_audit() uses the approved repair contract's fixed route map, not an arbitrary accepted string: same-series EVIDENCE_CORRECTION; automatic/direct/underlying replacement EVIDENCE_VERSION_CREATED. This is the current command event map allowed by the generic frozen audit schema, not a newly frozen universal taxonomy. Exact aggregate/type/count, ownership actor/time against explicit inputs, payload values and complete row CORRECTION tuple remain checked. The create payload's requested status and the committed ordinary result status are distinguished; no claim that a requested VERIFIED payload independently qualifies a result.

Shared helpers are disclosed disposable fixtures and a constraint-legal complete append-only legacy seed. Expectations, nine-table full row comparisons, exact/history snapshots, graph/origin and audit assertions are owned by the new oracle. Legacy seed/initial VERIFIED fixture are test setup, not proof of positive production trusted rules or full import semantic qualification.

Fresh AST inspection finds the same four test functions, no skip/xfail decorators, and 104 assertions versus old39. Assertion count alone is not a correctness oracle. The collection records independently compare all58 exact test/parameter names and preserve 1 environment,45 negative,8 ordinary,4 replay logical scenarios.

## Full Top Blocking AC Evidence Matrix

| AC | Requirement | Implementation evidence | Independent verification evidence | Boundary / negative evidence | Result |
| --- | --- | --- | --- | --- | --- |
| 1 | Adopted clean baseline and all protected bytes unchanged; new artifacts only | before/after manifests; current Git/three-file hashes | All82 protected paths and48 new indexed files recomputed;37 command log hashes checked; repeat after DB runs | Candidate clean, unchanged HEAD/parent, old six verifiers/logs/manifest untouched | PASS |
| 2 | Legal automatic setup and actual service calls after committed setup | oracle prepare(), command(), origin_for(), assert_acyclic() | Fresh58-case R1 oracle completed; actual public support commands and exact-ID assertions exercised | Nine automatic domain rejection nodes, two ordinary automatic replacements; no initial-predecessor assumption | PASS |
| 3 | CORRECTION row tuple/history/children and strict command-owned exact audit | oracle ordinary test and assert_audit(); actual append/create audit code; frozen12/13/21 | Fresh R1 oracle success checks event/count/actor/time/payload and row history | Explicit actor inputs differ across paths; all old rows preserved; current-valid result remains unavailable before review | PASS |
| 4 | Old verifier RED, repaired58 GREEN, complete original matrix and regression preserved | submitted37-command manifest and actual logs; identical58 collection record | Fresh independent old RED15/43, new GREEN58, five fixed originals + regression105; submitted focused142 and full239 logs independently hash-verified | No skipped R1 nodes or fresh regression skips; old RED exclusively11 setup +4 event-literal failures; no fixture errors | PASS |
| 5 | Durable truthful lineage/no-residue/replay evidence and no broader capability claim | raw new GREEN JSON proof records, proof manifest, execution report | All232 JSON proof records reconstructed from raw log equal manifest;45 rejection/fresh and4 replay hash pairs equal | Production approval empty, no fake positive registry/validator; observed fixture finalizer success, not broad cluster inspection | PASS |

## Gate results

| Gate | Result | Basis |
| --- | --- | --- |
| G0 Baseline | PASS | Adopted0cef/438 baseline unchanged, current scope/hashes readable |
| G1 Scope | PASS | Only allowed new oracle and evidence; business/old artifacts protected |
| G2 Contract | PASS | Five AC proven; two permitted oracle corrections do not weaken business requirements |
| G3 Architecture | PASS | Public domain commands and caller-owned transactions preserved; no production rule activation |
| G4 Test | PASS | Required executor matrix verified from actual hash-checked outputs; new independent key matrix executed below |
| DB Persistence | PASS | Fresh real disposable PostgreSQL paths; commit/fresh-session all-row/history/audit/replay assertions |
| G5 Regression | PASS | Fresh five fixed originals and persistence/migration/Research tests105 passed; no business byte changes |
| G6 Evidence | PASS | Full AC mapping, source review, verified indexed logs, fresh independent runs and explicit limits |

Browser, API implementation, worker and schema-change gates: NOT_APPLICABLE. Persistence gate does apply because the new verifier performs transactional database reads/writes.

## Commands actually executed by this verifier

All DB tests ran from candidate cwd using normal approved escalation and this exact prefix:

```bash
env PATH=/opt/miniconda3/bin:/usr/bin:/bin:/usr/sbin:/sbin PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service:/opt/miniconda3/lib/python3.12/site-packages:/opt/homebrew/lib/python3.12/site-packages /opt/miniconda3/bin/python -m pytest -p no:cacheprovider -q
```

| Target / command | Fresh actual result | Exit |
| --- | --- | --- |
| new R1 oracle absolute path, -rs | 58 passed in47.53s | 0 |
| preserved old supplemental absolute path, -rs | 15 failed,43 passed in53.32s; exact diagnosed failure classes | 1, expected verifier RED |
| Five fixed /tmp verifier files + tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py, -rs | 105 passed,2 HTTP422 deprecation warnings in85.81s; no skips | 0 |
| /opt/miniconda3/bin/ruff check --no-cache, three business files and new oracle | All checks passed | 0 |
| /opt/miniconda3/bin/ruff format --check --no-cache, same four files | 4 files already formatted | 0 |
| MYPYPATH=. /opt/miniconda3/bin/mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c03a-oracle-independent-mypy, three business files | No issues in3 source files; existing unused-section note | 0 |
| PYTHONPYCACHEPREFIX=/tmp/tg-r1c03a-oracle-independent-pycache /opt/miniconda3/bin/python -m compileall -q, four files | No errors | 0 |
| /opt/miniconda3/bin/alembic -c migrations/alembic.ini heads | 000000000004(head); metadata inspection, not business migration | 0 |
| git status/log/rev-parse/diff-check; actual file SHA recomputation | Fixed baseline and clean candidate preserved | 0 |
| JSON/AST read-only evidence validation |82 protected/48 indexed/37 command log hashes match;58 scenarios equal;232 raw proof records equal manifest | 0 |

The five originals are test_wp04_02_r1c_02_independent_20260915.py, test_wp04_02_r1c_01_independent_20260915.py, test_wp04_02_r1b_r1_wiring_20260915.py, test_wp04_02_r1b_reverify.py and test_wp04_02_r1a_verifier.py. Together they contribute70 cases; the regression contributes35. Full service239 and focused142 were **not re-executed in this independent turn**; their complete fresh executor-run logs/argv/exits were independently checked on the same unchanged candidate. They are not relabeled as this verifier's fresh runs.

## Persistence / counterexamples

Verified original raw proof counts:57 setup commits,45 no-residue baselines,61 production calls,45 domain-rejection/caller-commit/fresh-session full-nine-table equalities,8 ordinary history/no-inheritance results,4 replay/trusted-rejection equalities,12 exact audit checks. All232 parsed records equal the proof manifest. Every before/fresh hash pair matches; assertions also compare actual full rows, not just hashes.

High-risk counterexamples addressed: initial exact support without predecessor; nine types/values of illegal rules across five routes; explicit None versus omitted ordinary; automatic identity change without exact cycle; distinct audit actor/time across append/create; ordinary replay versus new trusted request using same key. UNKNOWN_OUTCOME/full concurrent reconciliation remain R1D and are not inferred from these tests.

Fresh DB tests use the existing local127.0.0.1:15432 disposable fixture; environment oracle checks all three diagnostic/admin redirect variables absent. Fixtures create/migrate/drop only their own random temporary databases. No fresh setup/teardown/cleanup exception occurred. No replacement instance, manual SQL or broad cleanup was performed. Executor's hash-checked infrastructure logs identify PostgreSQL17.11/original container/volume; this verifier did not separately enumerate the cluster or re-run container inspection.

## Findings, repair and next action

- BLOCKING findings: NONE within this task.
- NON-BLOCKING: two existing HTTP422 deprecation warnings and existing mypy configuration note.
- Historical source-reported R1C-03A business RED is not recertified as a fresh chronological business RED here. The fresh RED is explicitly old-oracle RED, and current route correctness is independently exercised against frozen admission requirements.
- Repair Required: NO. VF-01/VF-02 are resolved and prior successful R1A/R1B/R1C01/02 behavior is preserved.

Next selected task: TASK-WP04-02-R1C-03B-RULE-CONTRACT-R1, docs-only definition of a reviewable named deterministic correction rule. Why: production approval remains empty and frozen requirements specify semantic validation but no directly approved rule predicate. Do not enable an arbitrary parser string or let a developer create authorization. Initial-import and ordinary-correction qualifications remain separate tasks; this selection does not combine them with registry implementation. Rule approval and later implementation require separate user dispatch.

Whole R1C, R1D, final TASK-WP04-02-REVERIFY, WP04-03/04, Git integration, Sector Crowding and Capability Runtime remain outside this PASS.
