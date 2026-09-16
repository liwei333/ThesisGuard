# TASK-WP04-02-R1C-03A-ORACLE-R1 execution report

STATUS: IMPLEMENTATION_COMPLETE

Role: verifier-only repair executor. This report supplies repair and reverify evidence for a later independent acceptance; it does not declare PASS or R1C/WP04-02 completion. User explicitly adopted the new baseline in the dispatch message. No Git integration or business change was performed.

## Baseline and preservation

Candidate branch codex/wp04-02-evidence-domain-service, HEAD0cef44fd2ffd929b40e849e607af0bd4c44d14d2, parentbdd70edc153b6ed5def65ed99c41f325df45f066, status clean before and after. HEAD commit scope is exactly services.py and tests/test_evidence_services.py; this pre-existing commit was adopted, not created by this task.

Main HEAD438738c543e4cae3e805d31324b068c1cd5c7059, parent7d3734bc8346c16f9bbf7f7d9806309949c996de, branch main; tracked/index diff empty. Initial untracked acceptance and repair-contract documents preserved. All later project additions are the allowed new oracle and task-specific logs/manifests/report.

Three business SHA-256 values unchanged:

- errors.py: 3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec
- services.py: 43b548232df4267f377c5e144222c9278c3cc478f6800720240c4618b689ebe3
- tests/test_evidence_services.py: 47ff645c0f782af67e9f6ee64520105febdb28c6547a43bf89b435bead6c5108

Five original /tmp files and five durable copies match fixed contract hashes. All66 old evidence entries, old supplemental6d3592f86d13ca5e66988a5522542d52cf630ab3ebc0a51121bd786e401b0b89, old failed log030b6fba4e6e7d12ddbaee183f45f5be108c1effe333e05b9f2acb93ac9e95d0, old manifest15e57d836f05cfefaf59508f50d79db7aaa8cee591d138d28ce2062c66e033e2, governing documents and recovery manifest were hash-compared before every recorded command and after execution. No missing artifact restoration was needed. See before-manifest.json, after-manifest.json and final-hashes.log. Old snapshots/reports remain historical; the new clean commits do not rewrite their chronology.

## Verifier repair and scope

Only new oracle: docs/acceptance/verifiers/test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py. SHA-256 0ae19f9103b328afc3f7b5b017390569ead2a5239f18765d8c82f369d8818b0b.

VF-01: prepare() builds alternate eligible exact support with production ordinary correction → request_review → verify_or_reject VERIFIED. It retains initial/corrected/pending/verified exact IDs, asserts four distinct IDs/versions and exact predecessor chain, confirms initial v1 legitimately has no predecessor, checks initial exact snapshot unchanged, new support is eligible source-backed leaf, proposed support differs from prior/old support, DERIVED origin changes, and all persisted derivation edges are acyclic. Setup commits and leaves no transaction before durable_rows baseline. Automatic command uses the returned verified exact ID; negative commands do no setup writes. Nine automatic negatives reach production revise and reject; both ordinary automatic routes produce distinct identity/new seriesv1 without exact self/cycle.

VF-02: strict route map from repair contract: same → EVIDENCE_CORRECTION; automatic/direct/underlying replacement → EVIDENCE_VERSION_CREATED. Every success checks exactly one exact-version aggregate event, aggregate_type EvidenceVersion, exact result ID, specified event, ownership actor/time, dictionary payload with command-specific expected values. Status actor USER/time2026-09-16 differ deliberately from create ownership: automatic legacy IMPORTER/time2026-09-16, direct explicit SYSTEM/time2026-09-16, underlying explicit ADMIN_SCRIPT/time2026-09-17. Initial replay setup also uses ADMIN_SCRIPT/time2026-09-17. Append events follow status command; creation events follow explicit created_by_actor/created_at. Assertions compare known input values and persisted row, not merely row/event agreement. All correction row fields remain status_changed_at/by_actor/kind/reason=(2026-09-16,USER,CORRECTION,known reason), exact supersedes and immutable history/children retained.

Shared candidate helpers are only pg_sessionmaker, db and constraint-legal legacy seed, disclosed in source. Public command wrapper, all-nine-table full row oracle, exact/history comparisons, DERIVED origin, cycle and audit ownership expectations are independently owned. No candidate command/count/oracle expectation helper, production monkeypatch or positive trusted rule injection.

Old and new collection logs contain identical58 logical scenarios, including every old test/parameter name:1 environment/empty allowlist,45 negative,8 ordinary,4 replay. No deletion or skip. First aggregation helper exited1 because project -v collection output is Coroutine tree rather than ::nodeids; both pytest collection commands themselves exited0. A corrected read-only parser consumed preserved output; no test/expectation changed. scenario-preservation-manifest.json records all58 matching names.

## Fresh RED/GREEN and complete matrix

| Target | Actual summary | Exit |
|---|---|---|
| old-oracle-red | 15 failed, 43 passed in 44.95s | 1 |
| new-oracle-green | 58 passed in 48.89s | 0 |
| focused | 142 passed, 97 deselected in 113.61s (0:01:53) | 0 |
| r1c02 | 43 passed in 32.97s | 0 |
| r1c01 | 8 passed in 6.41s | 0 |
| r1b-wiring | 3 passed in 2.66s | 0 |
| r1b-reverify | 4 passed in 3.18s | 0 |
| r1a | 12 passed in 5.96s | 0 |
| full-services | 239 passed in 173.61s (0:02:53) | 0 |
| regression | 35 passed, 2 warnings in 21.28s | 0 |

Old RED reproduced from unchanged old supplemental after new-baseline authorization. Its11 constructor/pre-service failures and4 universal audit literal failures match diagnosed verifier defects. This is verification-tool RED, not business bugfix RED. New oracle GREEN executed all58 cases with no skips/setup/cleanup failures. pytest --capture=tee-sys additionally preserves exact IDs and proof records; assertion outcomes remain unfiltered.

Full original matrix ran freshly from candidate cwd: focused; five originals; full service; Evidence persistence/migrations plus Research API/persistence. All assertions succeeded and no Research skips. Regression warnings are two existing HTTP422 deprecations, not failures. No business semantic failure observed.

Ruff check/format check, original three-file mypy, compileall: exit0. Mypy has only existing unused-module configuration note. Alembic heads:000000000004(head), exit0. New oracle separately Ruff check, format check and compileall:exit0. Final diff-check/status/HEAD/hash:exit0. Complete argv/cwd/relevant environment/start/end/exit/log SHA in commands-manifest.json, complete logs retained; results-manifest.json summarizes outcomes.

## PostgreSQL/runtime/permissions

Existing local PostgreSQL127.0.0.1:15432 used through original disposable fixture. Container6684af51cd5a403090647d495967c019f50b5ae33898da24f89ad143d46f2a2f, thesisguard-postgres, pgvector/pgvector:pg17, existing thesisguard-postgres-data at /var/lib/postgresql/data, host15432/container5432, PostgreSQL17.11; ready throughout. No instance startup/substitution, proxy, alternate host/port, dependency install/upgrade, business migration or arbitrary SQL/broad cleanup. Normal require_escalated approved preflight reads and DB pytest fixture actions; no approval rejection.

Existing Miniconda Python3.12.9 primary runtime, pytest9.1.1, Ruff0.16.1, mypy2.3.0, Alembic1.18.5. PATH starts /opt/miniconda3/bin. PYTHONPATH candidate + existing Miniconda3.12 site-packages + existing Homebrew3.12 fallback; PYTHONDONTWRITEBYTECODE=1. boto3/botocore/s3transfer resolve from existing fallback, primary SQLAlchemy2.0.48/asyncpg0.31.0/FastAPI0.135.1/Pydantic2.12.5 unchanged. Module source/version evidence in runtime-resolution.log. pytest and Alembic fixture subprocess use same primary runtime. TG_TEST_ADMIN_DATABASE_URL, TG_R1C_REPLAY_BASELINE, TG_R1C02_REPLAY_PRIOR unset, checked in runner and environment test; no inherited DATABASE_URL override used for fixture admin route.

Fixtures created/migrated/dropped their own random disposable databases through existing normal mechanisms. Every test call returned after finalizers. No fixture setup/teardown/cleanup error in old RED/new GREEN or required matrix, no extra cleanup performed. This is observed fixture-success evidence; no claim of inspecting unrelated cluster databases.

## Persistence and acceptance handoff

persistence-proof-manifest.json retains57 setup-commit records,45 baseline/actual domain rejection/commit/fresh-session all-nine-table equality records,8 ordinary fresh-history/no-inheritance/routing records,4 read-only replay or new-trusted-request rejection/full-row equality records,12 exact audit records. Fresh readers are distinct sessions. Negative checks include stable validation code/path/raw rule/type/reason and no pending ORM new/dirty rows. Ordinary checks preserve every old row in all9 tables, legacy exact/status/rule/children, supersedes, N+1 versus replacementv1, complete CORRECTION tuple, disjoint child IDs and no current-valid eligibility. Replay preserves all durable rows including audit/idempotency exactly once.

AC1 baseline/old-byte preservation, AC2 public committed automatic setup, AC3 strict route audit ownership, AC4 old RED/new GREEN/full matrix, AC5 durable truthful evidence all supplied. Required L1/L2/L3/L4 evidence is ready for separate independent acceptance; this executor does not assign independent PASS. evidence-manifest.json enumerates all new project artifacts and their SHA/size. New untracked source/JSON/report whitespace and hashes checked explicitly, since git diff omits them.

Production approved trusted correction rules remain empty. Positive trusted registry/semantic validators, initial-import qualification, full ordinary-correction qualification, R1D, final WP04-02 independent full acceptance and Git integration remain unfinished/deferred. No R1C-03B/API/Agent/Sector Crowding/Capability Runtime work; no entire R1C or WP04-02 completion claimed. Await independent acceptance.
