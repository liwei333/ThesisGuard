# TASK-WP04-02-R1A-R2 Acceptance Report

**OVERALL: PASS**

## Metadata

- Task ID: `TASK-WP04-02-R1A-R2`
- Date: `2026-09-15`
- Verifier: Codex independent verifier
- Report Path: `docs/acceptance/TASK-WP04-02-R1A-R2-acceptance.md`
- Candidate worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`
- Candidate branch: `codex/wp04-02-evidence-domain-service`
- Baseline and candidate HEAD: `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`
- Implementation Status: three untracked candidate files; no candidate commit; local `main` unchanged
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`
- Missing Acceptance: none
- Repair Required: `NO`
- Next Action: close the R1A repair chain and dispatch only `TASK-WP04-02-R1B`

## Changed Files Snapshot

- `BASELINE_CHANGED_FILES`: the R1A candidate already contained three untracked files. Before R1A-R2 their SHA-256 values were:
  - `errors.py`: `3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec`
  - `services.py`: `66d332f27d9f1926fc8ac62a83e999334cb3dd3d750cd0ad336d6491280c75ba`
  - `test_evidence_services.py`: `79997fb4ca3a408151206175c27964f006e508381b6796b9812d6665513235f4`
- `FINAL_CHANGED_FILES`:
  - `?? backend/evidence/errors.py`
  - `?? backend/evidence/services.py`
  - `?? tests/test_evidence_services.py`
- Task-attributable Changes: R1A-R2 modified only `services.py` and `test_evidence_services.py`; `errors.py` remained byte-identical.
- Attribution: `CERTAIN`

Final candidate SHA-256:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
f980f2fcbb789b08dd25982f6af2e548def71a3cba8851d79ae0155748736981  backend/evidence/services.py
619324318d25bc25a45941e69d0e10a1539ec9eed4d302a817d3e278e9719396  tests/test_evidence_services.py
```

## Classification

- Task Type: `REPAIR`, `DOMAIN_SERVICE`, `DB_PERSISTENCE`
- Risk Type: source-locator validation, fail-before-write, audit/idempotency residue
- Touched Layers: Evidence service and real-PostgreSQL service tests
- Task Size: `SMALL`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, DB Persistence, G5 Regression, G6 Evidence
- Not Applicable Gates: API/OpenAPI, frontend/browser, schema/migration modification

## Top Blocking AC Results

| Top Blocking AC | Result | Independent evidence |
|---|---|---|
| TOP-AC-01 WEB_ANCHOR rejects missing, empty, whitespace-only and non-string canonical URLs with exact details | `PASS` | `services.py:1752-1759`; verifier and candidate PostgreSQL tests pass |
| TOP-AC-02 TABLE_CELL enforces a complete numeric pair independently of cell_ref | `PASS` | `services.py:1701-1750`; symmetric row-only/column-only and positive combinations pass |
| TOP-AC-03 Invalid public commands leave five mutable Evidence tables unchanged | `PASS` | Real-PostgreSQL candidate tests and independent verifier compare exact before/after counts |
| TOP-AC-04 Preserve the ten previously passing R1A verifier cases and all prior R1A behavior | `PASS` | Independent verifier `12 passed`; service suite `91 passed`; affected regression `35 passed` |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | `PASS` | Correct worktree/branch; `HEAD` and local `main` remain exact `3eb494e...` |
| G1 Scope | `PASS` | Exactly the same three authorized untracked files; only the two R2-authorized files changed |
| G2 Contract | `PASS` | Both remaining frozen SourceLocator boundary cases now match the R2 Repair Contract |
| G3 Architecture | `PASS` | Validation remains ahead of EvidenceSeries/EvidenceVersion construction and persistence |
| G4 Test | `PASS` | Independent verifier, full service suite and static/type/build checks pass with no skips |
| DB Persistence | `PASS` | Invalid public-path commands run against real PostgreSQL and prove exact five-table no-residue behavior |
| G5 Regression | `PASS` | Fresh `91 passed` service suite and `35 passed` WP04-01/migration/WP03 regression suite |
| G6 Evidence | `PASS` | Executor claims were independently reproduced; independent read-only reviewer found no issue |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary/Negative Evidence | Verdict |
|---|---|---|---|---|---|
| AC-01 [BLOCKING] | WEB_ANCHOR canonical URL is a nonblank string | `services.py:1752-1759` uses string type plus `strip()` nonblank validation | Independent verifier `12 passed`; service tests `91 passed` | Missing, `''`, spaces, tab/newline and integer reject at `locator_payload.canonical_url` | `PASS` |
| AC-02 [BLOCKING] | WEB_ANCHOR positive forms remain valid | `services.py:1760-1762` keeps selector fields optional but validated when supplied | Candidate positive URL-only and selector tests pass | No URL normalization, fetch or rewrite was added to this repair | `PASS` |
| AC-03 [BLOCKING] | TABLE_CELL numeric coordinates are absent together or present together | `services.py:1711-1728` validates pair completeness before the cell_ref fallback | Independent verifier and candidate symmetric tests pass | cell_ref + row-only and cell_ref + column-only reject at the exact missing path | `PASS` |
| AC-04 [BLOCKING] | Valid cell_ref-only and complete numeric forms remain valid | `services.py:1729-1750` accepts cell_ref fallback and validates complete pairs | Three positive representations pass | Complete pairs still run page/table/table-shape bounds even when cell_ref is present | `PASS` |
| AC-05 [BLOCKING] | Invalid locator commands fail before durable Evidence mutation | `create_evidence_series_version` validates provenance/locators before constructing and adding rows | Candidate and verifier tests use real PostgreSQL | EvidenceSeries, EvidenceVersion, SourceLocator, IdempotencyRecord and AuditEvent counts remain unchanged | `PASS` |
| AC-06 [BLOCKING] | Prior R1A source matrix/fingerprint/dedup/locator behavior does not regress | R1A implementation remains in the same files | Full service suite `91 passed, 2 warnings` | Original ten verifier cases remain part of the green 12-case run | `PASS` |
| AC-07 [BLOCKING] | WP04-01/migration/WP03 behavior does not regress | No changes outside the candidate service/test files | Combined regression `35 passed, 4 warnings` | Alembic remains single head `000000000004` | `PASS` |
| AC-08 [BLOCKING] | Static/type/build and anti-drift gates pass | Three candidate files | Ruff, format, mypy, compileall and diff checks exit 0 | No TODO/FIXME/skip/xfail/mock markers; no fourth candidate file | `PASS` |

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| Candidate branch/HEAD/main/status/hash/line-count checks | exact branch and `3eb494e...`; three untracked files; hashes match execution report | Baseline, scope and attribution |
| `PYTHONPATH=<candidate> pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs` | `12 passed in 7.51s` | Independent R1A/R2 contract verifier |
| `pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs` | `91 passed, 2 warnings in 60.73s` | Full Evidence service suite |
| Combined WP04-01/migration/WP03 pytest command | `35 passed, 4 warnings in 23.40s` | Required regression |
| Ruff check | `All checks passed!` | Static lint |
| Ruff format check | `3 files already formatted` | Formatting |
| Fresh mypy with isolated cache | `Success: no issues found in 3 source files` | Type gate |
| Compileall with isolated pycache | exit 0 | Compilation |
| Alembic heads | `000000000004 (head)` | Migration graph |
| Git diff/status and marker scan | clean checks; exact three files; no prohibited markers | Scope/evidence hygiene |

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| Whitespace-only canonical URL bypasses required validation | Yes | Independent public-path verifier now raises exact error | `PASS` |
| Non-string canonical URL bypasses validation | Yes | Candidate parameterized PostgreSQL case passes | `PASS` |
| cell_ref masks row-only numeric coordinates | Yes | Independent verifier now raises missing column path | `PASS` |
| cell_ref masks column-only numeric coordinates | Yes | Candidate symmetric test raises missing row path | `PASS` |
| Complete numeric coordinates skip bounds when cell_ref exists | Yes | cell_ref + complete out-of-range pair rejects at exact coordinate | `PASS` |
| Repair breaks URL-only or cell_ref-only positive paths | Yes | Both positive forms pass | `PASS` |
| Invalid request leaves idempotency/audit or Evidence residue | Yes | Exact five-table counts remain unchanged | `PASS` |

## DB Persistence Result

- Schema constraints: unchanged; Alembic remains the single head `000000000004`.
- Read semantics: the exact created locator payload remains queryable on positive cases.
- Transaction boundary: invalid locator commands fail before Evidence mutation; exact five-table no-residue assertions pass on real PostgreSQL.
- Version/history: unchanged by this narrow locator repair.
- Real persistence vs InMemory/Fake/Mock: all runtime evidence uses the real PostgreSQL fixture; no fake persistence is used.

## Blocking Findings

None.

## Non-Blocking Findings

None. The independent reviewer specifically found no Critical, Important or Minor item for this repair.

## Regression Result

- Result: `PASS`
- Preserved behavior: original ten verifier cases, all prior R1A source policy/fingerprint/dedup/locator tests, WP04-01 persistence/migrations and WP03 Research tests.
- Regression gaps: R1B/R1C/R1D behavior remains intentionally deferred and is not claimed by this report.

## Repair Required

- `NO`
- Repair ID: none
- Failed AC/Gate: none

## Final Decision Rationale

`PASS`. Both blocking locator boundary defects reproduced by the R1A-R1 verifier now pass through the real PostgreSQL public service path. Exact error details, fail-before-write, five-table no-residue, positive forms, parser bounds, prior R1A behavior, affected regressions and static/type/build gates all have fresh independent evidence. The implementation stayed within the two R2-authorized files and did not weaken tests or enter a later repair leaf.

This PASS closes `TASK-WP04-02-R1A-R2` and the R1A repair chain only. Historical FAIL reports remain historical evidence and are not overwritten. The original `TASK-WP04-02` remains `FAIL — REPAIR_REQUIRED` until R1B, R1C, R1D and `TASK-WP04-02-REVERIFY` pass.

## Next Action

Dispatch only `TASK-WP04-02-R1B` in the same isolated worktree. Do not commit, merge, push, mutate `main`, enter R1C/R1D, or begin WP04-03.
