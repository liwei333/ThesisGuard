# TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R3

## A. Execution Core

- Target: **Codex**, independent business/DB verifier; not the business implementation executor.
- Objective: Obtain fresh real-PostgreSQL evidence for the existing four 05C-01 focused nodes, 41 parameterized scenarios, on the independently accepted fixture bytes.
- Task type / size: `DB_PERSISTENCE_VERIFICATION / SMALL`; one focused boundary, Full Evidence Matrix.
- Required acceptance: `L1_STATIC_REVIEWED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED` for this focused scope only.
- Dispatch authorization: By forwarding this prompt for execution, the user authorizes the stated local metadata reads and at most 41 CREATE attempts for new disposable fixture databases, with normal identity-checked release. This does not authorize historical DB cleanup, shared DB/schema mutation, candidate repair or Git changes.
- R3 replaces R2's execution baseline precondition for this new run only. R2 remains historical BLOCKED; its contract/report/evidence are not edited. The original full 05C-01 acceptance matrix is not weakened or replaced.

### 1. Read the Necessary Context

Main repository: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard`.

Candidate: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`.

Read both AGENTS.md files and the following related sources, not the whole project indiscriminately:

- Original `TASK-WP04-02-R1C-05C-01-task-contract.md`, dispatch, acceptance and execution report.
- `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md` and `docs/WP04_EVIDENCE_CORRECTION_POLICY_ADDENDUM_2026-09-16.md`, specifically admission, correction, commit and replay clauses.
- `docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY-acceptance.md` and its evidence manifest/ledger. Use only its fixed-byte fixture acceptance; do not repeat its four CREATE scenarios.
- R2 acceptance/evidence and `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R2-FEEDBACK-REVIEW-acceptance.md`.
- Historical exact list: `docs/acceptance/TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-evidence/phase-a-20260916-exact-cleanup-plan.json`.
- Candidate fixture, db/sessionmaker wiring, four selected tests and their service/snapshot helpers. Inspect module loading for DB side effects before invoking collection.

### 2. Baseline: Exact Candidate, Semantic Main Gate

Candidate branch must be `codex/wp04-02-evidence-domain-service`, HEAD `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`, parent `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`, with clean worktree and empty index. Verify again before the real invocation and after execution. Any candidate drift blocks this run; do not rebase, reset, stash or repair.

Five fixed candidate SHA256 values:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec backend/evidence/errors.py
7ce76b02928019347625048e7d0acb523d74168cd6bbbdf03184163ac277f959 backend/evidence/services.py
c54e2306b7ec9625f0498faeebd8a23ceb55c6366769ac0d944f228e2aa84851 tests/test_evidence_services.py
bb84518f354f2f7752881fb529dcd6df31b58085bf32d6728c2ccf6998c3e9db tests/evidence_pg_fixture.py
3887a89945a770ed22bac5839ff6a61e5daf47cb05a8b0105d1cfce8f3c12fc7 tests/test_evidence_pg_fixture_lifecycle.py
```

Main anchor is `554a87dce995c98d41021f6ae99c2173f4221c09`. Main HEAD equality is **not** a blanket stop condition in R3. Require this anchor to remain an ancestor of actual main HEAD, record actual HEAD/status/index, and classify every committed, staged, unstaged and untracked change relative to the anchor:

- `NON_BLOCKING_EXTERNAL_CHANGE`: this run's new report/evidence, retained incoming R2 artifacts, new unrelated governance/acceptance/prompt documents, and zcode capability evaluation documents. Existing unrelated zcode evaluation documents may change only without changing this task's privileges or relevant product/domain requirements.
- AGENTS.md may differ only in its coding-agent evaluation/routing section, with unchanged preceding product/architecture/rules and no changed DB authorization, frozen-rule meaning or this task's verifier/acceptance requirements. Otherwise stop.
- Any changes to runtime source, apps, tests, migrations, infrastructure, dependency/tool configuration, frozen/canonical domain or product decisions, the original 05C-01 contract/dispatch, the accepted fixture report/evidence, historical UNKNOWN plan, or old R1/R2 reports/evidence are blocking. New unrelated acceptance artifacts are not permission to modify historical protected evidence.
- Unclassified or ambiguous changes block; never infer that all changes under `docs/` are harmless. Save the changed-file list and content-level classification. Preserve all unrelated changes without restoring or committing them.
- Repeat semantic/candidate checks immediately before real pytest and after execution. An unrelated main documentation commit during this run is recorded, not an automatic failure. Relevant drift prevents PASS; if already running, preserve safe fixture finalization rather than abruptly killing it or creating further resources.

Additional pinned main inputs:

```text
b179ecc6ea60ffed75f7179a2d36e47ad2b55153f6d4fa62b8be7e4926fd1288 docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md
af345e2604497171dc2d2ef13489ec3cffa1528caa5175c2ccf245b6a987a955 docs/WP04_EVIDENCE_CORRECTION_POLICY_ADDENDUM_2026-09-16.md
daf2779bda9602a7397ffc01398b940b704091a3529015475542d5e7ad66de89 docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY-acceptance.md
635ba4aad0468c15b4360733c784d52f4430f03477a14ef8a271a1e32bada360 docs/acceptance/TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-evidence/phase-a-20260916-exact-cleanup-plan.json
```

Do non-DB baseline validation first. Do not connect to PostgreSQL just to discover a baseline mismatch.

### 3. Top Blocking Acceptance Criteria

1. Candidate identity/cleanliness/five pins and main semantic gate match. No source, assertions, fixture, frozen contract, old evidence or Git state is modified.
2. Real parent/child tools, target and single Alembic head are validated before CREATE; a unique new run ID and fresh empty ledger are used; collection yields exactly the intended 41 nodes and zero CREATE. Total `create_sent` attempts never exceed 41, with one real focused invocation and no business retries.
3. All 41 scenarios run on actual PostgreSQL with no skip, xfail, xpass, setup/teardown error or altered assertion: 20 forbidden, 16 allowed, 3 ordinary COMMITTED replay, 2 disclosed legacy COMMITTED replay.
4. Existing assertions prove commit/fresh-session nine-table full-column equality, no rejection residue in internal/external idempotency/history, allowed replacement routing/children/audit, read-only committed replay, and independently forbidden fresh writes. Historical seed/replay is not proof of new-write admission.
5. Every new resource has exact name/OID/owner/owner_oid and ledger/node attribution, normal zero-connection release and post-DROP ABSENT evidence. Full admin catalog identities before/after match; the 45 historical UNKNOWN resources remain untouched. Actual commands, coverage, outcomes and acceptance gaps are reproducible from redacted retained evidence.

### 4. Environment, Collection and One Real Invocation

Use the fixture's accepted command-local environment. Do not change profiles, global environment or dependencies:

```text
PATH=/opt/miniconda3/bin:/opt/homebrew/bin:/opt/homebrew/opt/postgresql@16/bin:/usr/bin:/bin:/usr/sbin:/sbin
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=<candidate>:/opt/homebrew/lib/python3.12/site-packages
Python=/opt/homebrew/bin/python3.12
pytest=/opt/homebrew/bin/pytest
Alembic=/opt/miniconda3/bin/alembic
```

Test cwd is candidate. Verify actual Python/pytest identities and the actual test-child environment's `shutil.which('alembic')`, not just the parent shell. `alembic -c migrations/alembic.ini heads` must yield the single head `000000000004`. Record and assert these preflight results rather than merely printing paths.

Require `TG_TEST_ADMIN_DATABASE_URL`, `TG_R1C_REPLAY_BASELINE`, `TG_R1C02_REPLAY_PRIOR` unset; check other diagnostic variables relevant to these tests. Do not silently clear contamination. Configure only the new `TG_EVIDENCE_PG_LEDGER` absolute path and unique `TG_EVIDENCE_PG_RUN_ID` plus the documented command-local environment.

Only the previously verified local `postgresql+asyncpg` admin target `127.0.0.1:15432/postgres` is authorized. Obtain existing credentials through local configuration without printing or embedding them in helpers/evidence. Missing credentials/tool/service means BLOCKED, not dependency installation or target substitution. Sandbox denial may use the standard tool approval flow for these already scoped local operations; do not bypass it. No shared `migrate`, `db-reset`, Docker restart, FORCE DROP or connection termination.

Allocate a new unique run ID and a new empty JSONL ledger, distinct from R2 `r2_44b108eb48744559910a43d1511678a7`. Never reuse, truncate or overwrite old paths. The new ledger is empty before collection. Confirm imports/collect-only cannot invoke fixtures or perform DB writes.

Capture the full `pg_database` name/OID/owner/owner_oid identity array via the authorized admin connection, not a prefix-filtered approximation. Admin metadata may inspect relevant connection counts, but do not connect individually to historical UNKNOWN databases. Keep their exact 45-name list and identities from before to after. Existing external resources are never cleanup targets.

Collect only these four exact nodes with cacheprovider disabled; save all parameter node IDs and confirm exactly 41 with the 20/16/3/2 distribution and zero ledger CREATE events:

```text
tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue
tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit
tests/test_evidence_services.py::test_r1c05c01_committed_exact_replay_read_only
tests/test_evidence_services.py::test_r1c05c01_legacy_forbidden_prior_committed_replay
```

After gates pass, run those exact nodes **once**, using `-p no:cacheprovider -x -vv -s --tb=short`. Do not run a broader test target or repeat a failed node. Preserve collection and the full redacted real stdout/stderr/exit code. A collect invocation is not the real invocation and must create zero databases.

Count budget by every `create_sent` attempt, including failed/uncertain attempts, not just successful DBs. Confirm the accepted function-scoped fixture provides at most one attempt per selected parameter node. If source/preflight cannot establish the maximum, stop before CREATE rather than modifying fixture code or relying on a retrospective count. Do not repeat the accepted lifecycle scenarios or add a DB probe that creates resources.

On first assertion/setup/teardown/cleanup error, `-x` prevents subsequent nodes. Let current fixture finalization proceed normally. Do not impose a blind outer subprocess timeout that kills active pytest/finalizers. Use existing fixture timeouts; if interruption/hang or uncertain release occurs, preserve exact state and report it. Never force cleanup to obtain a green result. Capture final candidate/main status, ledger summary and authorized admin metadata even on an error when access remains available.

### 5. Resource and Result Judgment

- Only this run's ledger-proven new resources may undergo the accepted normal precise release. Identity/CREATE acknowledgement ambiguity, identity mismatch or another connection triggers fail closed; retain UNKNOWN and stop, not a guessed DROP.
- For each completed node, map its parameter ID to resource/ledger events and verdict. Verify all 41 success results rather than trusting pytest's aggregate exit code alone.
- On a successful full focused run, require ledger budget compliance, all new resources released, zero residual connections and complete catalog identity equality. Any catalog discrepancy prevents PASS; classify external activity separately without deleting unrelated databases.
- Business assertion failure is FAIL. Missing/invalid baseline, environment or authorization before meaningful business execution is BLOCKED. Fixture safety/cleanup contract violation is FAIL; a genuinely unavailable external observation needed for judgment is BLOCKED. Preserve the original cause and any secondary cleanup error; do not relabel an assertion failure as environmental BLOCKED.
- No new source repair is allowed. If FAIL, recommend only one minimal subsequent repair contract and leave implementation untouched.

### 6. Deliverables and Closure Boundary

Only add to main:

```text
docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R3-acceptance.md
docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R3-evidence/
```

If either output path already exists, do not overwrite it or start the real run; request a newly dispatched ID. Temporary helper/cache files use a fresh `/private/tmp/` directory; no helper is written into candidate. Do not modify R2 helper/artifacts or simply edit its baseline constant.

Evidence directory must contain `before.json`, `after.json`, `execution.log`, `resources.jsonl`, `manifest.json`, collected node IDs and raw redacted preflight/collect/real outputs. Record actual argv/cwd, UTC start/end, exit code, relevant redacted local environment, actual main/candidate identities/status, changed-file classification, pins, full catalogs, node/ledger mapping, attempt counts and release/UNKNOWN outcomes.

Manifest lists byte sizes and SHA256 of retained non-manifest artifacts. Exclude its own self-hash to avoid recursion. Retain helper SHA256 and safe source: new helper must not embed credentials; old credential-bearing source is not copied verbatim, only referenced by hash with a redacted representation if needed. Validate JSON/JSONL and manifest hashes after final writes.

Report a Full Evidence Matrix for the five blocking AC with Required/Achieved/Missing acceptance. As independent verifier, conclude exactly PASS / FAIL / BLOCKED for this focused task. Report real test count, CREATE attempts out of 41, precise new-resource release/residual state, preservation of historical UNKNOWN, and remaining full-matrix debt.

Do not run full service, seven business verifiers, Research/persistence/migration regression suites or other CREATE-bearing tests. This focused result is the first fresh slice of the original complete 05C-01 matrix, not its replacement. Even focused PASS does **not** close 05C-01, R1C or WP-04-02; it does not authorize 05C-02/R1D, API or Git integration.

## B. Governance Appendix

Use `ai-task-governor`: core invariants, anti-drift, evidence-based acceptance, baseline/scope/contract/test/evidence gates and conditional DB Persistence Gate. Executor self-reports are leads, not acceptance. This role is independent verifier, hence may produce the final focused verdict; it may not self-approve any new implementation.

Deferred: candidate business changes, full WP-04-02 closure, Git integration, Evidence API/OpenAPI, Research/Thesis/Agent, worker/MinIO pipeline, Capability Runtime, Sector Crowding, new financial rules and historical UNKNOWN cleanup. R3's semantic main gate solves unrelated-doc baseline churn without weakening the fixed implementation, database safety or business assertions.
