# TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1 execution report

Status: **BLOCKED**. Executor: Codex / TEST_INFRASTRUCTURE_REPAIR, not business repair or final acceptance. Date: 2026-09-16 / Asia/Shanghai.

The fixture implementation and bounded tests were completed before the final preservation gate. That gate detected an unexpected tracked modification of main `AGENTS.md`, plus two new unrelated untracked documents. The dispatch explicitly requires stopping on identity/scope/hash mismatch. No further tests, migrations or database operations ran after detection. No restoration, reset, checkout, rebaseline or Git write was performed. The actor/source of these observed changes is not inferred. This task's recorded writes do not target those files.

## Authorized baseline and observed final identity

| Repository | Branch | HEAD | Parent |
| --- | --- | --- | --- |
| main | main | `d3acc1c6f4a2e5ce1fe4b973d7855409c0db1da5` | `438738c543e4cae3e805d31324b068c1cd5c7059` |
| candidate | codex/wp04-02-evidence-domain-service | `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8` | `0cef44fd2ffd929b40e849e607af0bd4c44d14d2` |

Both final branch/HEAD/parent values remain the authorized baseline. Baseline candidate was clean; main tracked/index was empty and its 19 existing untracked file paths were retained. Baseline SHA-256 for errors/services/tests exactly matched dispatch.

BASELINE_CHANGED_FILES: candidate `[]`; main existing untracked paths are enumerated in manifest baseline.status; no tracked/staged changes.

FINAL_CHANGED_FILES attributable to this task:
- candidate `M tests/test_evidence_services.py`, new `tests/evidence_pg_fixture.py`, new `tests/test_evidence_pg_fixture_lifecycle.py`;
- main this new execution report and evidence directory containing only execution.log, resources.jsonl, manifest.json (execution.log is ignored by Git but exists).

Unexpected final main changes: `M AGENTS.md`; new `docs/ZCODE_CAPABILITY_EVALUATION_2026-09-16.md` and `docs/prompts/ZCODE_CAPABILITY_BENCHMARK_2026-09-16.md`. These are retained; this task did not create/edit them. Main index remains empty. Candidate index remains empty; no additional candidate path changed.

AGENTS SHA-256: baseline `5244bc97ebe7939cc8fe15a49f060b8046b6d32b896c27dc631b7b59594bf476`; final observed `6680af6b8223096ac48c5188fb452ab9d43b7a2674fa27a94ea3044bd6dba789`. The appended agent-routing section is recorded as an observed diff in execution.log. Scope preservation is therefore BLOCKED, even though runtime tests passed.

## Implementation and scope

Existing fixture remains function-scoped and returns `AsyncIterator[async_sessionmaker[AsyncSession]]`. Only its body/request wiring and required imports changed (+11/-53 lines). It delegates to an Evidence-only helper. Factory configuration remains pool_pre_ping=True, expire_on_commit=False, autoflush=False; `db` fixture transaction semantics are unchanged.

The helper requires explicit absolute command-local `TG_EVIDENCE_PG_LEDGER`. Missing/relative/unwritable ledger fails before a DB connection/CREATE; no shell profile change. Optional `TG_EVIDENCE_PG_RUN_ID` groups attempts; unique attempt UUID and pytest node identify each target. Before CREATE, append/flush/fsync record exact run/node/name/endpoint, tools/child/heads, actual connected admin role/database and exact-name absence. CREATE acknowledgement and immediate exact OID/owner/owner_oid confirmation establish provenance. Prefix, count, age and catalog differences do not establish ownership.

Protection covers CREATE, confirmation, migration, engine/sessionmaker and yield. It closes owned admin/engine resources, checks the same exact OID/owner and zero target connections, then sends exact DROP without IF EXISTS/FORCE/termination. No unknown/unacknowledged target is adopted. Cleanup failures raise explicitly on normal exit; when a primary exists it is re-raised with cleanup notes. GeneratorExit from normal aclose is not treated as a primary failure. CREATE-rejection logging failures preserve the CREATE exception. Lost replies, shutdown-class or missing SQLSTATE are conservatively INDETERMINATE/UNKNOWN; no DROP.

Connection/query and close bounds are 10 seconds; subprocess tools 10 seconds and migration 60 seconds. This does not guarantee finalizers on SIGKILL, power loss or all interrupts. Caller-owned sessions retain normal async context management; outstanding connections prohibit DROP rather than being terminated. Ledger enables later separately authorized exact disposition.

Complete scoped unified diff for all three files is retained in execution.log; new-file git diff --no-index exit 1 means a diff exists. No new universal platform, business change, unrelated fixture fix or policy was implemented.

## Business and historical preservation

Final read-only comparison: all 87 original named definitions except pg_sessionmaker match their baseline AST hashes; all other non-import/non-fixture top-level AST statements match Git HEAD. The entire byte suffix from `db` fixture to file end matches SHA-256 `790b7748ba89e58f9481a6c4e69f4e2dd2ad4dda1205e60ada35b80d4449e8d8`. Definitions, assertions, decorators/parameters and helpers are unchanged.

Candidate 183 protected existing files excluding the permitted fixture file match baseline SHA. Main 388 of 389 protected existing files match, with AGENTS.md the sole existing-file mismatch. Old verifiers, reports, manifests, logs, proposed three-document rebaseline material and all existing untracked evidence remain unchanged. No full business suite/verifier/regression was collected or executed; importing the fixture module does not run its business tests.

## RED/GREEN and fault boundary

1. Original fixture, unmodified: one deterministic migration nonzero test failed the resource assertion: acknowledged fake CREATE=1, exact DROP=0. Exit 1. No real DB connection; not a permission/import/missing-tool RED.
2. Initial implemented deterministic run: 13 passed, one cleanup-on-aclose assertion failed; corrected GeneratorExit handling. Next run 25 passed / 4 real deselected.
3. Durable pre-CREATE/ledger-negative tests: 29 passed / 4 real deselected.
4. Four real scenarios: 4 passed / 29 deterministic deselected, no skips, exit 0, 15.71 seconds.
5. Final review added deterministic shutdown/unclassified CREATE and failed-ledger tests. Expected REDs: shutdown wrongly NOT_CREATED; ledger OSError masked server rejection. Corrected only CREATE-exception classification/recording.
6. Final deterministic GREEN: **32 passed / 4 real deselected, zero skips, exit 0**. Final collection lists all 36 exact nodes in manifest/execution.log. Existing dependency deprecation warnings (Starlette/httpx and anyio alias) were disclosed; no dependency installation or fixture changes to suppress them.

Mock/fault injection is infrastructure-only. Migration-fault uses declared CalledProcessError(returncode=19) after real CREATE instead of a real upgrade; it is not an Alembic business defect. Engine-fault occurs after real existing migration. Normal/body-fault execute actual migration and session SELECT 1/rollback/close. Real test nodes manually drive the actual pg_sessionmaker.__wrapped__(request) generator, preserving node identity, without registering/collecting the full business suite.

## Command-local environment and actual discovery

```text
PATH=/opt/miniconda3/bin:/opt/homebrew/bin:/opt/homebrew/opt/postgresql@16/bin:/usr/bin:/bin:/usr/sbin:/sbin
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service:/opt/homebrew/lib/python3.12/site-packages
Python=/opt/homebrew/bin/python3.12
pytest=/opt/homebrew/bin/pytest
TG_EVIDENCE_PG_LEDGER=/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-evidence/resources.jsonl
TG_EVIDENCE_PG_RUN_ID=b2404b6ba2f348dbb962fb822177bc42
```

TG_TEST_ADMIN_DATABASE_URL, TG_R1C_REPLAY_BASELINE, TG_R1C02_REPLAY_PRIOR were originally UNSET in the initial shell and each command runner, including the normally approved real environment. No silent unset. Cache/bytecode under `/private/tmp/tg-fixture-r1-o961p3mp`; log/evidence in this task directory.

Actual versions: Python 3.12.9; pytest 9.1.1; Alembic 1.18.5; Ruff 0.16.1; mypy 2.3.0; psql 16.13. Actual child which('alembic')=/opt/miniconda3/bin/alembic; heads=000000000004 (head). Bare pytest resolves to Conda; every pytest command used explicit Homebrew path. All four real attempts repeated actual tool/child/heads checks in the same inherited environment before CREATE. Tool prechecks do not count as migration/business PASS.

Final Ruff check, Ruff format --check, mypy, compileall and git diff --check all exit 0 for the three scoped files. mypy unused override note is non-blocking. Exact argv/cwd/start/end/exit values and raw output (redacted) are in execution.log/manifest. Two independent static runs used parallel orchestration; manifest records were rebuilt from the complete append-only COMMAND lines to retain both results.

Test selection commands:
```text
/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py -k 'not real_postgres' -rs -x
TG_RUN_PG_FIXTURE_LIFECYCLE_REAL=1 /opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py -k real_postgres -rs -x
```

## Real provenance, release and preserved UNKNOWN

Run ID `b2404b6ba2f348dbb962fb822177bc42`; endpoint only 127.0.0.1:15432. Normal approved escalation; no alternative endpoint/container/proxy/instance. Task-wide real create_sent=4, confirmed=4, dropped-confirmed=4, cleanup_failed=0. Budget is exhausted; no repeat/new DB authorized by this delivery.

| Scenario | Exact new name | OID | Owner / owner OID | Connections before DROP | Release |
| --- | --- | --- | --- | --- | --- |
| normal | `tg_wp04_service_c014108206a84be18b3eef20bb238d19` | 8325423 | thesisguard / 10 | 0 | CONFIRMED → ABSENT |
| migration_fault | `tg_wp04_service_b9725319f4194a9bb13a29983c90ba57` | 8326123 | thesisguard / 10 | 0 | CONFIRMED → ABSENT |
| engine_fault | `tg_wp04_service_99981375cf3f44fdbcfa4a107acd50de` | 8326124 | thesisguard / 10 | 0 | CONFIRMED → ABSENT |
| body_fault | `tg_wp04_service_120283d9ce8b4861bf9386617acad778` | 8326824 | thesisguard / 10 | 0 | CONFIRMED → ABSENT |

Each row has fsynced attempt, tools_checked, target_checked/ABSENT, create_sent, created/CONFIRMED, resources-close, cleanup_checked, drop_sent, dropped/ABSENT and cleanup_admin_closed events. Three primary_error events correspond only to the declared faults. Each post catalog verifies its exact target absent.

Eight actual pre/post admin catalogs are identical, each 49 names. All Phase A 45 UNKNOWN exact names/OIDs/owners match their saved plan in each catalog. They were never connected to, marked, migrated, renamed, terminated or dropped. The other four postgres/template0/template1/thesisguard entries remain. No historical ownership inference or historical cleanup approval is claimed. SQL catalog reads are not a claim of physically unchanged bytes/cache/time.

## Version-bound evidence and remaining acceptance

Four real scenarios ran before the final narrow CREATE-error hardening. Their source hashes are:
- `tests/test_evidence_services.py`: `c54e2306b7ec9625f0498faeebd8a23ceb55c6366769ac0d944f228e2aa84851`
- `tests/evidence_pg_fixture.py`: `2a5eeda1edcce7905fdc85ba7d4429aeb2b56d1d22a83573d1bc65b26318bd14`
- `tests/test_evidence_pg_fixture_lifecycle.py`: `029c9c24176d43cee22d8b82f715e14c6c9b45b8dbc7802e52fccd4fa122e618`

The existing fixture file hash is unchanged since that real run. The helper subsequently changed only the CREATE-exception branch; three deterministic tests were added. Final byte versions received deterministic/static checks; **do not label the recorded real run as a fresh run of all final bytes**. No additional real resources were created beyond four. Full final-byte independent acceptance is not delivered; a later verifier must assess this narrow impact and any required separately authorized resource budget.

| AC / level | Evidence and limit | Delivery state |
| --- | --- | --- |
| AC-01 | Missing tool/child/heads/target zero-create deterministic paths; repeated real tools/target checks | Implemented and exercised |
| AC-02 | Migration/engine/sessionmaker/body faults; primary and cleanup handling; exact real release | Implemented and exercised; final error-only hardening deterministic |
| AC-03 | Durable pre-attempt; ack+exact OID/owner; unknown CREATE no-drop, ledger failure primary preservation | Implemented; real confirmed provenance plus final deterministic uncertainty tests |
| AC-04 | Exact target only, resource close, zero sessions and identity guards; explicit cleanup-failure faults | Implemented and exercised; no termination/FORCE |
| AC-05 | Candidate business AST/suffix and old evidence preserved; protected main AGENTS changed | **BLOCKED final preservation gate** |
| L1_STATIC_REVIEWED | Scoped source/diff and preserved definitions inspected | Executor evidence obtained; overall scope blocked |
| L2_BUILD_VERIFIED | Scoped Ruff/format/mypy/compileall/diff-check exit 0 | Executor evidence obtained |
| L3_CONTRACT_VERIFIED | 32 final deterministic infrastructure tests | Executor evidence obtained, not business acceptance |
| L4_DB_VERIFIED | Four exact real lifecycle scenarios at recorded hashes | Bounded executor evidence obtained; final-byte/independent acceptance not claimed |

Required final preservation/independent acceptance not achieved. Main tracked scope drift must be resolved by the dispatcher under explicit instructions; do not restore/rebaseline silently. Historical residual ownership remains unresolved. Other persistence fixtures have similar late-finally/termination risks and remain deferred, unmodified.

No commit/merge/rebase/reset/checkout/push, full Evidence service, old verifier, persistence/Research regression, CI, 05C-02/R1D, API/Thesis/Agent or deferred product scope was executed. Original 05C-01 remains BLOCKED. This delivery does not close R1C/R1D/WP04-02, approve integration, or resolve historical residue.

## Final SHA-256 and minimal artifacts

| Candidate file | Final SHA-256 |
| --- | --- |
| `backend/evidence/errors.py` | `3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec` |
| `backend/evidence/services.py` | `7ce76b02928019347625048e7d0acb523d74168cd6bbbdf03184163ac277f959` |
| `tests/test_evidence_services.py` | `c54e2306b7ec9625f0498faeebd8a23ceb55c6366769ac0d944f228e2aa84851` |
| `tests/evidence_pg_fixture.py` | `bb84518f354f2f7752881fb529dcd6df31b58085bf32d6728c2ccf6998c3e9db` |
| `tests/test_evidence_pg_fixture_lifecycle.py` | `3887a89945a770ed22bac5839ff6a61e5daf47cb05a8b0105d1cfce8f3c12fc7` |

| Evidence artifact | Final SHA-256 |
| --- | --- |
| `execution.log` | `338a5202c20c58e8cf7c94f2ed3ebfbdcc303c2135252e40c9dfccf51782bcb6` |
| `resources.jsonl` | `7cc9359e2ca8676bb4c25b23e66fa95a026b4aab4ec522a6237772c0217b2ef7` |

The execution-report SHA-256 is recorded in manifest.json after writing this report. Manifest cannot embed its own hash; final handoff provides that SHA externally. No old output was overwritten. Temporary scripts and caches are task-local under the reported /private/tmp path, not candidate code/evidence.

## Actual command index

Long python -c diagnostic bodies are abbreviated here; exact literals are retained in manifest argv and execution.log.

| # | Command | Exit |
| --- | --- | --- |
| 1 | `/opt/homebrew/bin/python3.12 -c <full script retained in manifest/execution.log>` | 0 |
| 2 | `/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py -rs -x` | 1 |
| 3 | `/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py -k not real_postgres -rs -x` | 1 |
| 4 | `/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py -k not real_postgres -rs -x` | 0 |
| 5 | `/opt/miniconda3/bin/ruff check tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 1 |
| 6 | `/opt/miniconda3/bin/ruff check tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 0 |
| 7 | `/opt/miniconda3/bin/mypy --cache-dir /private/tmp/tg-fixture-r1-o961p3mp/mypy tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 1 |
| 8 | `/opt/miniconda3/bin/mypy --cache-dir /private/tmp/tg-fixture-r1-o961p3mp/mypy tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 0 |
| 9 | `/opt/miniconda3/bin/ruff format --check tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 0 |
| 10 | `/opt/homebrew/bin/python3.12 -m compileall -q tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 0 |
| 11 | `git diff --check` | 0 |
| 12 | `/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py -k not real_postgres -rs -x` | 0 |
| 13 | `/opt/miniconda3/bin/ruff check tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 1 |
| 14 | `/opt/miniconda3/bin/ruff format --check tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 0 |
| 15 | `/opt/miniconda3/bin/mypy --cache-dir /private/tmp/tg-fixture-r1-o961p3mp/mypy tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 0 |
| 16 | `/opt/miniconda3/bin/ruff check tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 0 |
| 17 | `/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py --collect-only -rs -x` | 0 |
| 18 | `/opt/homebrew/bin/python3.12 -c <full script retained in manifest/execution.log>` | 0 |
| 19 | `/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py -k real_postgres -rs -x` | 0 |
| 20 | `/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py -k shutdown_or_unclassified or create_error_is_preserved -rs -x` | 1 |
| 21 | `/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py -k create_error_is_preserved -rs -x` | 1 |
| 22 | `/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py -k not real_postgres -rs -x` | 0 |
| 23 | `/opt/miniconda3/bin/ruff check tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 0 |
| 24 | `/opt/miniconda3/bin/ruff format --check tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 0 |
| 25 | `/opt/miniconda3/bin/mypy --cache-dir /private/tmp/tg-fixture-r1-o961p3mp/mypy tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 0 |
| 26 | `/opt/homebrew/bin/python3.12 -m compileall -q tests/test_evidence_services.py tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py` | 0 |
| 27 | `git diff --check` | 0 |
| 28 | `/opt/homebrew/bin/pytest -p no:cacheprovider -q tests/test_evidence_pg_fixture_lifecycle.py --collect-only -o addopts= -rs -x` | 0 |
| 29 | `/opt/homebrew/bin/python3.12 -c <full script retained in manifest/execution.log>` | 1 |
