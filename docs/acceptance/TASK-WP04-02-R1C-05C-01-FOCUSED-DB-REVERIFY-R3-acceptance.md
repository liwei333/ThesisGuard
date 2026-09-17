# TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R3 Independent Acceptance

Verdict: **BLOCKED**, limited to this focused task. Independent verifier: Codex. Evidence date: 2026-09-17. This is a verifier execution/evidence failure before meaningful business execution, not a demonstrated business assertion failure or an external PostgreSQL outage.

## Cause and Stop Decision

Run ID: `r3_e933fa17680041018f0e8d2284f5f1d6`. Preflight started at `2026-09-17T00:27:56.204497+00:00`; collect-only ended at `2026-09-17T00:27:58.277055+00:00`. Evidence closure time is retained in `after.json` and is not a test execution time.

The original verifier helper expected flat pytest node ID lines. Pytest emitted a tree containing `<Coroutine ...>` entries. Collection itself exited 0 and reported 41 items, but the helper parsed zero and exited 1 with `collect-only mismatch: count=0 dist={'forbidden': 0, 'allowed': 0, 'ordinary_replay': 0, 'legacy_replay': 0}`. This exit/error is known from the execution continuity record; the original helper's outer stdout/stderr was not retained in the evidence directory. Its child command output is retained.

Following the dispatch's first-unexpected-error stop rule, no real focused pytest was started and no retry was performed. Post-stop extraction of the existing collect output confirms exactly 41 unique node IDs, distributed 20 forbidden / 16 allowed / 3 ordinary replay / 2 legacy replay. This extraction does not retroactively complete the failed preflight or grant business acceptance.

## Baseline and Commands

Candidate branch is `codex/wp04-02-evidence-domain-service`, HEAD `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`, parent `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`. Retained initial and closure checks show clean candidate/index and matching five candidate SHA256 pins. Main HEAD remains `554a87dce995c98d41021f6ae99c2173f4221c09`; anchor ancestry holds. Main committed/staged/unstaged tracked diffs are empty, and all four main SHA256 pins match.

The changed-file list in `before.json` and `after.json` contains retained incoming R2 acceptance/feedback/evidence, the new R3 prompt and this run's evidence. They are classified `NON_BLOCKING_EXTERNAL_CHANGE` under R3; this report is also a permitted new R3 artifact. No unrelated main documentation commit advanced HEAD. The retained initial classification is path-level and does not provide complete content-hash proof that every incoming old artifact remained unchanged throughout; this is an evidence limitation, not a reason to assert PASS.

`execution.log` retains actual argv/cwd, command-local environment, UTC start/end, exit codes and stdout/stderr for four commands, all exit 0:

1. `tool-preflight`: Python 3.12.9, pytest 9.1.1, parent/child Alembic `/opt/miniconda3/bin/alembic`.
2. `/opt/miniconda3/bin/alembic -c migrations/alembic.ini heads`: single `000000000004 (head)`.
3. `module-import-no-db-side-effect`: child output `import-ok`. This alone does not prove full catalog equality.
4. `/opt/homebrew/bin/pytest -p no:cacheprovider --collect-only -q` followed by the four R3 exact node selectors: 41 collected, deprecation warnings only.

The three forbidden environment variables are recorded unset in `before.json`; the documented PATH/PYTHONPATH, `PYTHONDONTWRITEBYTECODE`, fresh ledger path and run ID are in each child execution record. The intended real `-x -vv -s --tb=short` command was **not executed**. There is no real-output file because no real process existed.

## Full Evidence Matrix

| AC | Required | Achieved / Evidence | Missing / Judgment |
|---|---|---|---|
| 1. Baseline and scope | L1 static review; exact candidate, pins, main semantic gate; no protected edits | `before.json`, `after.json`: identity/pins match, candidate clean, main anchor unchanged and tracked diffs empty | Complete content-level historical-artifact preservation proof is absent; static review cannot establish DB behavior |
| 2. Preflight and budget | Valid tools/target/head, fresh empty ledger, exact 41 nodes, at most one real invocation and 41 CREATE attempts | `execution.log`, raw stream files, `collected-nodeids.json`: tools/head and 41 distribution confirmed; ledger empty; 0 real invocations, 0/41 attempts | Original helper parser failed; full admin target/catalog observations and original safe helper source were not retained |
| 3. Actual scenario execution | L3/L4: 41 real PostgreSQL scenarios, no skips or errors | Collection only: 20/16/3/2 | 0 real tests; all 41 business outcomes UNPROVEN |
| 4. Business guarantees | Commit/fresh-session equality, no residue, routing/history/audit, read-only replay, independently forbidden writes | Selected scenario identities retained | No fresh DB assertion evidence; all specified guarantees remain unverified in R3 |
| 5. Resource safety and evidence | Exact attribution/release, zero residual connections, full catalogs equal, 45 historical UNKNOWN preserved, reproducible evidence | `resources.jsonl` is 0 bytes; no new resource/name/OID or release exists; retained artifacts have validated manifest hashes | Full before/after catalogs and historical 45 identity mapping absent; cannot claim catalog equality or independently prove complete historical preservation |

Required acceptance: `L1_STATIC_REVIEWED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED` for the focused scope. Achieved: baseline/hash/tool and collection observations only, with the limitations above. Missing: completed acceptance at all required levels, real business execution and complete DB/evidence safety observations. No required level is promoted to a complete PASS.

## Resources and Evidence Integrity

Real invocation count: **0**. Real executed/passed/failed business test count: **0/0/0**. CREATE attempts: **0 / 41**. DROP events: **0**. New disposable resources: none recorded; release/ABSENT and residual-connection checks are not applicable to new resources. There were no per-historical-DB connection/termination/rename/DROP operations in retained command records. No historical cleanup was performed, but absent full catalog evidence prevents an identity-preservation claim for all 45 UNKNOWN DBs.

The original helper path `/private/tmp/tg_wp04_02_r1c_05c_01_focused_db_reverify_r3_runner.py` is unavailable at closure. `before.json` records its SHA256 `88a8335cba23cdc29a36cfaae65fa72f809db32190b1711a0d7fc622185fd4c8`; that hash cannot now be independently revalidated. No source was reconstructed or presented as the original. Missing catalog snapshots were not fabricated.

`close-evidence.py` is retained safe closure source. It performs only Git/hash reads and extraction from existing records, with no pytest or DB call. It adds `after.json`, collected IDs, separate raw redacted preflight/collect stdout/stderr files and `manifest.json`, preserving the original three evidence files. All JSON/JSONL parses, retained stdout/stderr SHA256 values, and all manifest artifact byte sizes/SHA256 values were validated after writes. Manifest excludes its own hash and covers evidence-directory artifacts, not this sibling report.

## Remaining Work and Boundary

A subsequent newly dispatched focused ID should retain safe verifier source and full catalog metadata before any gate may fail, parse the actual collection format, and preserve the same one-real-run/41-attempt limits. This is a verifier harness/evidence correction recommendation; it requires no candidate business, assertion or fixture repair. The existing R3 output paths are occupied and must not be reused for another real run.

R2 report/evidence remains historical and is not modified or ratified. The original full 05C-01 matrix remains outstanding, including full service/seven business verifier/Research/persistence/migration regression debt as applicable to its original contract. This focused BLOCKED does not close 05C-01, R1C or WP-04-02 and does not authorize 05C-02/R1D, API or Git integration.
