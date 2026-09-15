# TASK-WP04-02-R1A-R1 Acceptance Report

**OVERALL: FAIL — REPAIR_REQUIRED**

## Metadata

- Task ID: `TASK-WP04-02-R1A-R1`
- Date: `2026-09-15`
- Verifier: Codex independent verifier
- Report Path: `docs/acceptance/TASK-WP04-02-R1A-R1-acceptance.md`
- Candidate worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`
- Candidate branch: `codex/wp04-02-evidence-domain-service`
- Baseline and candidate HEAD: `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`
- Implementation Status: three untracked candidate files; no candidate commit; local `main` unchanged
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`
- Missing Acceptance: `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Repair Required: `YES`
- Next Repair ID: `TASK-WP04-02-R1A-R2`

## Changed Files Snapshot

- `BASELINE_CHANGED_FILES`: the R1A candidate already contained three untracked files; before R1A-R1 their hashes were recorded in the source acceptance.
- `FINAL_CHANGED_FILES`:
  - `?? backend/evidence/errors.py`
  - `?? backend/evidence/services.py`
  - `?? tests/test_evidence_services.py`
- R1A-R1-attributable changes: `services.py` and `test_evidence_services.py`; `errors.py` remained byte-identical.
- Attribution: `CERTAIN`

Final candidate SHA-256:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
66d332f27d9f1926fc8ac62a83e999334cb3dd3d750cd0ad336d6491280c75ba  backend/evidence/services.py
79997fb4ca3a408151206175c27964f006e508381b6796b9812d6665513235f4  tests/test_evidence_services.py
```

## Classification

- Task Type: `REPAIR`, `DOMAIN_SERVICE`, `DB_PERSISTENCE`
- Risk Type: source locator validation, fail-before-write, audit/idempotency residue
- Touched Layers: Evidence service and real-PostgreSQL service tests
- Task Size: `SMALL`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, DB Persistence, G5 Regression, G6 Evidence
- Not Applicable Gates: API/OpenAPI, frontend/browser, schema/migration modification

## Top Blocking AC Results

| Top Blocking AC | Result | Independent evidence |
|---|---|---|
| TOP-AC-01 WEB_ANCHOR canonical URL and optional selector semantics | `FAIL` | Original canonical-url-only case passes, but whitespace-only canonical_url is accepted although the Repair requires a nonempty value |
| TOP-AC-02 TABLE optional coordinate validation and bounds | `PASS` | Independent original verifier and candidate PostgreSQL cases pass |
| TOP-AC-03 TABLE_CELL cell-ref or complete numeric representation | `FAIL` | cell_ref plus only one numeric coordinate is accepted; numeric representation is not required to remain complete when cell_ref is present |
| TOP-AC-04 Stable exact locator errors and fail-before-write | `FAIL` | Original five failures are repaired, but both new malformed payloads are misclassified as valid and enter the persistence path |
| TOP-AC-05 Preserve all previously passed R1A behavior | `PASS` | Fresh service suite `83 passed`; affected regression suite `35 passed`; static gates pass |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | `PASS` | Correct branch/worktree; HEAD/main remain exact `3eb494e...` |
| G1 Scope | `PASS` | Exactly the same three authorized untracked files; only service/test hashes changed for R1A-R1 |
| G2 Contract | `FAIL` | Two explicit Repair requirements remain unsatisfied: nonempty canonical URL and complete numeric TABLE_CELL coordinates |
| G3 Architecture | `FAIL` | The public service validation boundary accepts malformed decision-critical locator payloads and proceeds toward durable mutation |
| G4 Test | `FAIL` | Candidate suite is green but omits the two combination/boundary counterexamples |
| DB Persistence | `FAIL` | Expanded public-path verifier uses real PostgreSQL and both malformed inputs fail to raise before persistence |
| G5 Regression | `PASS` | Fresh `83 passed` service suite and `35 passed` WP04-01/migration/WP03 regression suite |
| G6 Evidence | `FAIL` | Original verifier is `10 passed`; expanded independent verifier is `2 failed, 10 passed` |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary/Negative Evidence | Verdict |
|---|---|---|---|---|---|
| AC-01 [BLOCKING] | canonical_url-only WEB_ANCHOR succeeds | `services.py:1740-1749` | Original independent verifier passes | No selector fields required | `PASS` |
| AC-02 [BLOCKING] | WEB_ANCHOR canonical_url is a nonempty string | `services.py:1741` checks truthiness without trimming | Expanded real-PostgreSQL verifier fails | `canonical_url='   '` is accepted and writes Evidence | `FAIL` |
| AC-03 [BLOCKING] | WEB optional selectors validate when supplied | `services.py:1747-1748,1831-1847` | Candidate invalid-selector tests and original verifier pass | Empty/wrong-type optional fields reject with exact paths | `PASS` |
| AC-04 [BLOCKING] | TABLE validates optional coordinates and parser bounds | `services.py:1674-1700,1907-1929` | Candidate and original independent verifier pass | Out-of-range row/column reject; table-level/cell_ref forms pass | `PASS` |
| AC-05 [BLOCKING] | TABLE_CELL accepts cell_ref or a complete numeric pair | `services.py:1701-1738` | Basic cell_ref-only and complete numeric cases pass | cell_ref + row-only is accepted instead of reporting missing column | `FAIL` |
| AC-06 [BLOCKING] | Missing locator and raw/short fields return exact details | `services.py:1600-1605,1627-1638` | Candidate and original independent verifier pass | source version ID and exact path are present | `PASS` |
| AC-07 [BLOCKING] | Invalid locator commands leave no mutable Evidence residue | Validation occurs before mutation | Covered invalid tests compare five table counts | The two newly discovered malformed cases are not rejected and therefore bypass the no-residue contract | `FAIL` |
| AC-08 [BLOCKING] | Previous R1A matrix/fingerprint/dedup/lifecycle/concurrency behavior remains green | unchanged corresponding implementation | Fresh complete service suite: `83 passed, 2 warnings` | No regression found in covered behavior | `PASS` |
| AC-09 [BLOCKING] | WP04-01/migration/WP03 regression remains green | no changes outside candidate | Fresh combined run: `35 passed, 4 warnings` | Alembic remains `000000000004` | `PASS` |
| AC-10 [BLOCKING] | Required static/type/build gates pass | three candidate files | Ruff, format, mypy, compile all exit 0 | No skip/mock/TODO drift found | `PASS` |

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| Git branch/HEAD/main/status/hash/line-count checks | exact branch and `3eb494e...`; exactly three untracked candidate files; hashes match execution feedback | Baseline, scope and attribution |
| Original `/tmp/test_wp04_02_r1a_verifier.py` | `10 passed in 5.58s` | Reproduce executor's independent-verifier claim |
| Expanded independent verifier with two additional public-path cases | `2 failed, 10 passed in 6.67s` | Boundary/combination verification |
| `pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs` outside sandbox | `83 passed, 2 warnings in 60.09s` | Full candidate service suite |
| Combined WP04-01/migration/WP03 pytest outside sandbox | `35 passed, 4 warnings in 25.55s` | Required regression |
| Ruff check and format check | `All checks passed`; `3 files already formatted` | Static quality |
| Fresh mypy | `Success: no issues found in 3 source files` | Type gate |
| Compileall | exit 0 | Compilation |
| Alembic heads | `000000000004 (head)` | Migration graph |
| Git diff/status and anti-drift scan | no diff hygiene error; exact three files; no TODO/FIXME/skip/xfail/mock markers | Scope/evidence hygiene |

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| canonical-url-only WEB locator wrongly rejected | Yes | Original verifier now passes | `PASS` |
| whitespace-only canonical URL wrongly accepted | Yes | Public service command does not raise | `FAIL` |
| TABLE optional coordinate bypasses bounds | Yes | Original verifier now passes | `PASS` |
| TABLE_CELL cell_ref-only rejected | Yes | Original verifier now passes | `PASS` |
| TABLE_CELL cell_ref masks an incomplete numeric pair | Yes | cell_ref + row-only public command does not raise | `FAIL` |
| Missing locator/error path details | Yes | Original verifier now passes | `PASS` |
| Previously accepted service and persistence behavior regresses | Yes | Fresh 83- and 35-test runs | Not found |

## DB Persistence Result

- Schema constraints: unchanged; Alembic has the single head `000000000004`.
- Locator positive paths: original canonical-url-only, table-level, table coordinates, cell_ref-only and complete numeric cases pass.
- Locator negative paths: original five failures are repaired; whitespace canonical URL and mixed cell_ref/partial-numeric payloads still fail closed incorrectly by being accepted.
- Transaction boundary: covered invalid cases prove no residue, but the two malformed cases enter the normal mutation path because validation does not reject them.
- Version/snapshot/history: no regression found in the fresh complete service suite.
- Real persistence vs InMemory/Fake/Mock: the expanded verifier and both regression suites used disposable real PostgreSQL databases.

## Blocking Findings

### BF-01 — Whitespace-only WEB canonical URL is accepted

`backend/evidence/services.py:1741` uses `not payload['canonical_url']`, which rejects the empty string but accepts whitespace. The Repair Contract requires a nonempty canonical URL, and the adjacent optional string helper already uses `.strip()`. The expanded public-path verifier shows that `canonical_url='   '` creates Evidence rather than returning `EVIDENCE_INVALID_SOURCE_LOCATOR` with `locator_payload.canonical_url`.

### BF-02 — cell_ref masks an incomplete numeric coordinate representation

`backend/evidence/services.py:1717-1729` checks row/column completeness only when `cell_ref is None`. If a cell_ref is present together with only `row_index` or only `column_index`, the malformed numeric representation is accepted. The Repair Contract requires numeric coordinates, when used, to be complete; cell_ref is an alternative representation, not permission to retain contradictory partial coordinate metadata.

## Non-Blocking Findings

- None. R1B/R1C/R1D remain explicit deferrals and were not evaluated as part of this Repair verdict.

## Regression Result

- Result: `PASS` for required preserved behavior.
- Preserved behavior: full candidate service suite `83 passed`; combined WP04-01/migration/WP03 suite `35 passed`; Ruff/mypy/compile/Alembic pass.
- Regression gaps: original WP04-02 remains FAIL and WP04-03 remains blocked.

## Repair Required

- `YES`
- Repair ID: `TASK-WP04-02-R1A-R2`
- Failed AC/Gate: AC-02, AC-05, AC-07; G2 Contract, G3 Architecture, G4 Test, DB Persistence, G6 Evidence.
- Must preserve: all ten original verifier cases, 83 candidate tests, 35 affected regressions, exact scope and static gates.

## Final Decision Rationale

`FAIL`。R1A-R1 correctly repairs all five originally documented failures, and the executor's `10 passed`, `83 passed` and `35 passed` claims are independently reproducible. However, two directly implied boundary cases from the immutable Repair Contract still fail on the real public PostgreSQL service path. Because both are SourceLocator Top Blocking behavior and permit malformed durable evidence inputs, R1A-R1 cannot receive PASS.

## Next Action

Execute only the two-case `TASK-WP04-02-R1A-R2` repair in the same isolated worktree. Do not enter R1B, commit the candidate, or begin WP04-03 until R1A-R2 receives independent PASS.
