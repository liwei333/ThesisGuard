# TASK-WP04-02-R1C-05C-01-R5-RESOURCE-LIFECYCLE-REPAIR-R1 Independent Acceptance R1

## Verdict

**PASS**

The exact R5 residual was removed within the separately confirmed one-database authorization, the fixture repair remains fail closed, and a fresh independent real PostgreSQL lifecycle run completed with exact resource closure. This verdict is limited to the resource-lifecycle repair. It does not change the original 41-scenario R5 verdict, authorize that suite to be rerun, or authorize integration, push, later work packages, or any production/trading behavior.

## Review identity and fixed scope

- Independent verifier: Codex session separate from the repair executor session.
- Repair branch: `codex/wp04-02-r5-resource-lifecycle-repair-r1`.
- Repair worktree: `/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-r5-resource-lifecycle-repair-r1`.
- Baseline and repair branch HEAD: `77abbe72decfe5437ffed90521b8101f1eae1153`.
- Parent: `cc55162341fd99653b4ac6cd8f81da043cf7484c`.
- `origin/main`: `77abbe72decfe5437ffed90521b8101f1eae1153` at review time.
- Candidate: `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`, clean at review time.
- Accepted tracked change scope:
  1. `tests/evidence_pg_fixture.py`
  2. `tests/test_evidence_pg_fixture_lifecycle.py`
- Accepted untracked delivery scope: the repair execution report and its sibling evidence directory.
- No commit, stage, merge, rebase, push, reset, clean, stash, worktree prune, or business-suite execution was performed by this acceptance.

## Independent acceptance matrix

| Requirement | Result | Independent evidence |
|---|---|---|
| TOP-AC-01 exact residual recovery | PASS | The retained recovery evidence binds the operation to name `tg_wp04_service_53ea9a765404436e8fc6a6ecf2f51187`, OID `9268698`, owner `thesisguard`, owner OID `10`, and zero client backends. The operation was ordinary non-FORCE `DROP DATABASE`; the immediate delta removed only that identity. A fresh read-only catalog query found the exact name absent. |
| TOP-AC-02 demonstrated root cause and TDD | PASS | The retained R5 timestamps show the former fixture made its single connection check about 19 ms after `engine_disposed`. The repair delivery includes a red run for deterministic `[1, 0]` followed by a green run after implementation. Baseline source hashes independently matched `6639a612...27e3` and `f6fe68de...7c13`. |
| TOP-AC-03 bounded, exact, fail-closed cleanup | PASS | Source review confirmed a monotonic 1.0-second drain deadline, 0.05-second recheck interval, exact OID/owner/owner_oid checks before every count and again after zero, ordinary exact-name DROP only, and structured failure on persistent clients, query failure, or identity drift. No `pg_terminate_backend` or `WITH (FORCE)` path exists. |
| TOP-AC-04 deterministic lifecycle coverage | PASS | Fresh independent command selected 43 non-real cases: `43 passed, 4 deselected`, exit 0. Coverage includes transient drain, persistent connection, query failure, post-zero OID/owner/owner_oid drift, primary-exception preservation, initial zero, internal backend exclusion, create uncertainty, and cleanup failures. |
| TOP-AC-05 focused real PostgreSQL lifecycle | PASS | Fresh independent run ID `r5repair-independent-r1-20260922` selected only four lifecycle cases: `4 passed, 43 deselected`, exit 0. Ledger: 66 rows; create sent/created/drop sent/dropped = `4/4/4/4`; cleanup/create failures = 0; all created/dropped run ID, attempt ID, node, name, OID, owner and owner OID pairs matched. |
| Catalog restoration and historical protection | PASS | Fresh post-run catalog: 49 databases, 45 `tg_wp04_service_*` historical UNKNOWN databases, zero task-prefix client backends, and zero rows for the original R5 residual name. The current 45 name/OID/owner triples and the frozen cleanup plan independently produced the same SHA-256 `4be3542bc44953b8880993e9d43c744286cf9ad4ee6f733d3c04cdc6a7498432`. |
| Scope, Git and protected inputs | PASS | Only the two allowed tracked files differ. Index is empty. Main/candidate/harness HEADs match the delivery record. Original R5 acceptance and manifest hashes independently matched `7a76be1f...d75` and `a10316c1...014`. |
| Evidence completeness | PASS | The repair evidence manifest registers 18 non-manifest files. Independent recursive reconstruction found 18 actual eligible files; every byte count and SHA-256 matched. All JSON evidence parsed. |
| Credential safety | PASS | Independent scan of the repair report and evidence found no credential-bearing PostgreSQL URL, known development password literal, password assignment, or token assignment. No `.env` or complete environment was read for this acceptance. |

## Verification commands and results

### Static and deterministic checks

Executed from the repair worktree against the delivered, uncommitted source state:

```text
ruff check tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py
PASS — All checks passed

ruff format --check tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py
PASS — 2 files already formatted

python3.12 -m compileall -q tests/evidence_pg_fixture.py tests/test_evidence_pg_fixture_lifecycle.py
PASS — exit 0, bytecode redirected under /private/tmp

git diff --check
PASS — exit 0

pytest -p no:cacheprovider tests/test_evidence_pg_fixture_lifecycle.py -k 'not real_postgres' -q
PASS — 43 passed, 4 deselected, 2 pre-existing deprecation warnings
```

The delivered source hashes independently matched:

- `tests/evidence_pg_fixture.py`: `894630daace9489e19534cdff9b8b4f95b5c33e31bdce7452512ff76a584b42b`
- `tests/test_evidence_pg_fixture_lifecycle.py`: `5c8e4ed5a9cfdadb00ebde21fa3057a2687b05aa34b0f9bba54160c57a10de36`
- Complete two-file diff: `8ee1f97635eecca7452b46b90062e7f70152e54b395b3f5ba2a28cc4edffa127`

### Fresh independent PostgreSQL lifecycle check

Preflight read-only observations:

- container `thesisguard-postgres`: healthy;
- `pg_isready`: accepting connections;
- catalog count: 49;
- task-prefix client backends: 0;
- exact original R5 residual count: 0.

Executed exactly once by this verifier:

```text
TG_RUN_PG_FIXTURE_LIFECYCLE_REAL=1
TG_EVIDENCE_PG_RUN_ID=r5repair-independent-r1-20260922
pytest -p no:cacheprovider tests/test_evidence_pg_fixture_lifecycle.py -k real_postgres -q
```

Result: `4 passed, 43 deselected`, exit 0. The four selected scenarios were `normal`, `migration_fault`, `engine_fault`, and `body_fault`. No business test node was selected. The fresh ledger was `/private/tmp/tg-r5-repair-review-r1.7uiBbi/resources.XXXXXX.jsonl` and contained 66 rows bound to the single run ID.

Post-run read-only observations:

- catalog count: 49;
- `tg_wp04_service_*` catalog count: 45;
- task-prefix client backends: 0;
- exact original R5 residual count: 0;
- current 45 historical identities equal the frozen plan: true.

## Findings and residual risks

No acceptance-blocking defect was found in the repair scope.

The following limits remain explicit:

1. The independent real run observed the direct zero-connection cleanup path. The transient `1 → 0` path is demonstrated by deterministic fault injection, not by a deliberately held real client connection.
2. The fixture's logical drain deadline is one second, while individual asyncpg commands retain the pre-existing ten-second command timeout. This does not permit an unsafe DROP—the path remains fail closed—but a stalled metadata query can extend wall-clock teardown beyond the logical drain interval. This is a bounded-latency hardening opportunity, not a blocker for the demonstrated R5 failure mode.
3. The original 41-scenario R5 run remains `FAIL_DB_RESOURCE_LIFECYCLE`. Its nine completed business assertions are not promoted into a full-suite PASS, and its 31 unexecuted scenarios remain unverified.
4. The repair is still uncommitted and not integrated. Main continues to contain the baseline fixture until a separately authorized Git integration task completes.

## Acceptance levels

- `L1_STATIC_REVIEWED`: PASS for the two-file repair.
- `L2_BUILD_VERIFIED`: PASS for Ruff, format, compile, and diff hygiene in scope.
- `L3_CONTRACT_VERIFIED`: PASS for the 43 deterministic lifecycle cases and fail-closed counterexamples.
- Focused `L4_DB_VERIFIED`: PASS only for the four-case fixture resource-lifecycle slice.
- Original 41-scenario R5 focused DB reverify: NOT RERUN; prior FAIL remains authoritative.
- Product, strategy, profitability, broker, migration-wide, worker, MinIO, WP-04-03, 05C-02/R1D and later work: NOT VERIFIED / NOT AUTHORIZED.

## Closure decision

The repair may proceed to a separate, controlled Git integration task. After integration is independently accepted, a new Codex session—not the repair executor, this repair verifier, the PostgreSQL restore executor, or the failed R5 verifier—may receive a new one-shot contract to rerun the original 41-scenario focused PostgreSQL verification.

