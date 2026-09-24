# TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R5 Independent Acceptance

**OVERALL: FAIL_DB_RESOURCE_LIFECYCLE**

## Metadata and independent-session decision

- Task ID: `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R5`
- Date: 2026-09-22, Asia/Shanghai
- Executor / verifier: new Codex independent DB verifier task/session
- Session independence: PASS. This session did not execute the local PostgreSQL restore, implement the WP-04-02 candidate, implement or repair the R5 harness, integrate either branch, or author the predecessor execution reports.
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, focused `L4_DB_VERIFIED`
- Final verdict: `FAIL_DB_RESOURCE_LIFECYCLE`
- Report: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R5-acceptance.md`
- Evidence: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R5-evidence/`

The preflight, immutable baselines, structured collection and sustained catalog-quiescence gate all passed. The one authorized real PostgreSQL pytest invocation then collected all 41 scenarios. Nine forbidden-state scenarios passed their business assertions. During teardown of the ninth node, the fixture found one connection to its exact task-created temporary database and correctly refused to DROP it. Pytest stopped under `-x` with `EvidencePGCleanupError`. The ledger therefore contains one `cleanup_failed` event and one exact current-run residual database. This is a resource-lifecycle failure, not a business assertion failure and not a reason to rerun or repair in this session.

## Immutable baselines

Main used **Shape A**:

- `R5_START_MAIN_HEAD`: `77abbe72decfe5437ffed90521b8101f1eae1153`
- parent: `cc55162341fd99653b4ac6cd8f81da043cf7484c`
- tracked diff and index: empty
- initial untracked paths: only `docs/workbench.html` and the allowed wrong-session feedback review
- wrong-session feedback review SHA-256: `c2c4c6c551c0dbfe0b021a070d11e8e84ea40fb028476f93c2aae66ce23c801d`

Candidate:

- branch: `codex/wp04-02-evidence-domain-service`
- HEAD: `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`
- parent: `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`
- clean, index empty, all five fixed SHA-256 pins matched

Harness:

- branch: `codex/wp04-02-verifier-harness-r5-repair`
- HEAD: `f9a41ea045d3ab8ad18db32d65a8484d6c96ec25`
- parent: `df836cb39a1234aae967553b3783a67df9ad6672`
- clean, index empty, all three fixed SHA-256 pins matched

The candidate and harness commits were both ancestors of `R5_START_MAIN_HEAD`. A task-owned detached worktree was created at exact historical main `675217c3a15c0f416aa4462ca6edc491bf99f9f6`; it was detached, clean and matched all four historical SHA pins. It was removed cleanly at closure without pruning or touching any older worktree metadata.

## Tool and PostgreSQL preflight

- Python: `/opt/homebrew/bin/python3.12`, version `3.12.9`
- pytest: `/opt/homebrew/bin/pytest`, version `9.1.1`
- child Alembic: `/opt/miniconda3/bin/alembic`
- Alembic heads: exactly `000000000004 (head)`
- inherited `TG_TEST_ADMIN_DATABASE_URL`, `TG_R1C_REPLAY_BASELINE`, `TG_R1C02_REPLAY_PRIOR`: all absent
- Docker daemon: `docker-desktop`
- container: `thesisguard-postgres`, running and healthy
- image: `pgvector/pgvector:pg17`
- image ID: `sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f`
- named volume: `thesisguard-postgres-data`, mounted at `/var/lib/postgresql/data`
- restart policy: `unless-stopped`
- port: host `15432` to container `5432/tcp`
- `pg_isready`: accepting connections
- read-only SQL identity: database `postgres`, current user `thesisguard`, server `17.11 (Debian 17.11-1.pgdg12+2)`

The verifier's first SQL helper attempt failed at Python parse time before opening a socket. It was replaced with a no-credential-literal read-only helper and succeeded. This tool-side syntax error did not consume the pytest or CREATE budget.

## Collect-only and sustained quiescence

The accepted harness was run from clean `f9a41ea`, against clean candidate `e942cbcc`, with the detached `675217c3` historical main root, a fresh evidence leaf, a fresh invocation nonce and an independent fail-closed socket guard.

- runner exit: 0
- pytest return code: 0
- `valid=true`, `verdict=PASS`
- unique node IDs: 41
- distribution: 20 forbidden / 16 allowed / 3 ordinary COMMITTED replay / 2 disclosed legacy COMMITTED replay
- missing / extra / duplicates / unclassified: all empty
- test body calls: 0
- socket attempts: 0
- fixture ledger: absent
- CREATE: 0
- invocation nonce: fresh and matched
- inner manifest reconstruction: 10 actual = 10 listed, exact paths/bytes/SHA-256

The complete preflight catalog contained 49 databases and had canonical SHA-256 `8b74281638af2471d514f38c77ae08391deb8491cba6af12f0be9cb48c8a7b04`. The fixed historical set matched 45/45 exact name/OID/owner/owner_oid identities.

The one permitted sustained quiescence window produced 25 samples over 120.016 seconds, at five-second intervals. First and last catalog count were both 49 and every sample had the same canonical SHA-256. External active client count and external sessions connected to any `tg_wp04_service_*` database were zero in every sample. No pytest or CREATE occurred before this gate passed.

## Exactly one real PostgreSQL invocation

The only real pytest command used `/opt/homebrew/bin/pytest` with `-p no:cacheprovider -x -vv -s --tb=short`, the four exact selectors, and the exact candidate worktree as cwd. The child environment was a fixed allowlist plus only the fresh absolute ledger path and fresh run ID. No historical diagnostic variable was inherited or set; no credential URL was placed in argv or retained metadata.

- real invocation count: **1**
- run ID: `2fbae112c2c0e6829ff3ff77efd03e28`
- collected: 41
- passed: 9
- failed business assertions: 0
- errors: 1
- skipped / xfailed / xpassed: 0 / 0 / 0
- not executed after `-x`: 31
- failure node: `tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[REJECTED-same]`
- failure type: `EvidencePGCleanupError`

The first nine test bodies reached their expected assertions. The ninth test printed its durable nine-table equality and was reported `PASSED` before teardown failed. The fixture ledger then recorded `connections=1` for its exact temporary database and, as designed, issued no `drop_sent` for that resource.

## Resource ledger and catalog result

- attempt: 9
- create_sent: 9
- confirmed created: 9
- drop_sent: 8
- confirmed dropped: 8
- cleanup_failed: 1
- create_failed: 0
- current-run UNKNOWN: 0
- current-run exact residual: 1
- CREATE budget: 9/41, within limit

Exact residual identity:

- name: `tg_wp04_service_53ea9a765404436e8fc6a6ecf2f51187`
- OID: `9268698`
- owner: `thesisguard`
- owner OID: `10`
- node: `tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[REJECTED-same]`

The immediate after catalog contained 50 databases and canonical SHA-256 `bd2665dffc6987907a5f02616ded90fe7e57d45d94eeea96ce954d7e33ac3a90`. It differed from before only by the exact ledger-attributed residual. A subsequent 30.010-second post-run window produced seven samples; all seven remained at the same 50-database after hash and therefore did not restore before/after equality. No manual DROP or connection termination was attempted.

The fixed 45 historical UNKNOWN databases remained 45/45 exact before and after. This verifier never connected to any of them individually, never reclassified ownership by prefix/count/age and never tried to clean, rename, alter or terminate a connection for them.

The runtime observer recorded nine complete catalog samples. Four short-lived task-created identities were observed and matched exact run-id ledger identities. It found no unknown external catalog addition and no missing or changed pre-existing identity. The one teardown connection that caused cleanup refusal was no longer present at the later after-catalog capture, but the exact database remained. The recorded `cleanup_failed` and residual are independently sufficient for the resource-lifecycle FAIL verdict.

## Verdict and acceptance boundary

| Gate | Result | Basis |
|---|---|---|
| Session / immutable baseline | PASS | New verifier; Shape A; exact candidate/harness/detached identities and hashes |
| Collect-only | PASS | Fresh 41/20/16/3/2; body/socket/ledger/CREATE zero |
| PostgreSQL preflight | PASS | Exact tool, service, target, user and server identities |
| 120-second quiescence | PASS | 25 identical samples; external activity counts zero |
| Business assertions reached | PARTIAL | Nine nodes passed before fixture teardown error; remaining 31 not executed |
| Resource lifecycle | **FAIL** | 1 cleanup_failed; 1 confirmed-created exact residual; before/after catalog unequal |
| focused L4 DB | **NOT ACHIEVED** | Complete 41-node PASS and exact catalog restoration were not achieved |

The verdict is `FAIL_DB_RESOURCE_LIFECYCLE`. It is not changed to `BLOCKED_CONCURRENT_DB_ACTIVITY` because the task has an independent, explicit fixture cleanup failure and exact task-owned residual. It is not a business-service FAIL because no domain assertion failed in the executed nodes.

## Scope, Git and prohibited-action closure

Final Git identities remain:

- main: `main@77abbe72decfe5437ffed90521b8101f1eae1153`, tracked diff and index empty
- candidate: `codex/wp04-02-evidence-domain-service@e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`, clean and index empty
- harness: `codex/wp04-02-verifier-harness-r5-repair@f9a41ea045d3ab8ad18db32d65a8484d6c96ec25`, clean and index empty

Only the authorized R5 report and evidence directory were added by this task. No source, test, fixture, harness, frozen contract, addendum, migration, compose file or `.env` was modified. No second real pytest was run. No source repair, database manual cleanup, `pg_terminate_backend`, commit, stage, merge, rebase, push, reset, clean or stash was performed.

This FAIL does not authorize 05C-02, R1D, Git integration or push, WP-04-03/API/OpenAPI, WP-04-04, Research, Thesis, Agent, worker, MinIO, parser, embedding, RAG, Capability Runtime or Sector Crowding. A separate Codex session must create a minimal repair/operations contract for the exact residual and fixture teardown failure; zcode must not perform the DB cleanup, real PostgreSQL repair, independent DB acceptance or Git integration.
