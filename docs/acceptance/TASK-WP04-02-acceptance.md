# TASK-WP04-02 Evidence Domain Service 验收报告

**OVERALL: FAIL — REPAIR_REQUIRED**

## Metadata

- Task ID: `TASK-WP04-02`
- Date: `2026-09-15`
- Verifier: Codex independent verifier
- Report Path: `docs/acceptance/TASK-WP04-02-acceptance.md`
- Candidate branch: `codex/wp04-02-evidence-domain-service`
- Candidate worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`
- Baseline and candidate HEAD: `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`
- Implementation Status: three untracked candidate files; no candidate commit; local `main` unchanged
- Required Acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`, `L5_REGRESSION_VERIFIED`
- Achieved Acceptance: `L1_STATIC_REVIEWED`
- Missing Acceptance: `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`, `L5_REGRESSION_VERIFIED`
- Repair Required: `YES`
- Repair ID: `TASK-WP04-02-R1`

## Changed Files Snapshot

- `BASELINE_CHANGED_FILES`: candidate worktree was clean at exact baseline before executor changes according to the dispatched task; verifier independently confirmed its current HEAD and branch.
- `FINAL_CHANGED_FILES` in candidate worktree:
  - `?? backend/evidence/errors.py`
  - `?? backend/evidence/services.py`
  - `?? tests/test_evidence_services.py`
- Task-attributable Changes: exactly the three untracked files above.
- Attribution: `CERTAIN`
- Main worktree verifier artifacts remain separate and were not included in the candidate.

Candidate SHA-256 at verification:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
ee2d9cf6faf44cc8f51bb357d2745dc29a6623860e86195dc72363a262117924  backend/evidence/services.py
8e11668a8efcb6b8b5503d203cd3a29f9dd8bfab01cb1a3b245bc724a9c2e94d  tests/test_evidence_services.py
```

## Classification

- Task Type: `DOMAIN_SERVICE`, `DB_PERSISTENCE`, `VERSIONED_WRITE`, `IDEMPOTENCY`, `AUDIT`
- Risk Type: financial-evidence eligibility, immutable history, provenance, optimistic concurrency, idempotency, transaction atomicity, audit integrity
- Touched Layers: Evidence service, internal errors, real-PostgreSQL contract tests
- Task Size: `LARGE`
- Evidence Matrix Type: `Full`
- Selected Gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, DB Persistence, G5 Regression, G6 Evidence
- Not Applicable Gates: API/OpenAPI, frontend/browser, migration/schema modification

## Top Blocking AC Results

| Top Blocking AC | Result | Independent evidence |
|---|---|---|
| TOP-AC-01 Source identity/versioning, grade matrix and locator must match the frozen contract | `FAIL` | Exact matrix differs; fingerprint uses the wrong field set; same-byte grade correction is rejected; contract-valid `page_number` locator is rejected |
| TOP-AC-02 Eligibility, lifecycle and trusted verification must fail closed | `FAIL` | UNREVIEWED is returned as current-valid; illegal PENDING_REVIEW→DISPUTED and UNREVIEWED→INVALIDATED succeed; arbitrary non-empty trusted rule produces VERIFIED |
| TOP-AC-03 MANUAL/DERIVED/CROSS_INSTRUMENT identity, provenance and immutable children must be service-derived and preserved | `FAIL` | Caller-provided origin/scope identities are trusted; zero-support DERIVED commits; cycle traversal is absent; N+1 child copy drops derivation links |
| TOP-AC-04 Idempotency, replay, concurrency and replacement must be aggregate-scoped and atomic | `FAIL` | Scope is operation-only; hashes omit semantic fields; correction checks expected_version before replay; replacement uses two savepoints and two idempotency records |
| TOP-AC-05 Required contract tests and static verification must prove the blocking behaviors | `FAIL` | Candidate has only 8 service tests and encodes wrong semantics; verifier's 10 targeted PostgreSQL counterexamples all fail; mypy reports 4 task-related errors |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | `PASS` | Branch, worktree and exact baseline `3eb494e...` independently confirmed; candidate attribution is exact |
| G1 Scope | `PASS` | Only the three authorized new files exist; no model, migration, API, OpenAPI, Research, frontend, worker or runtime change |
| G2 Contract | `FAIL` | Multiple frozen-contract rules and Given/When/Then examples are contradicted by implementation and candidate tests |
| G3 Architecture | `FAIL` | Fail-closed eligibility, provenance-derived identity, immutable derivation lineage and atomic command/idempotency boundaries are violated |
| G4 Test | `FAIL` | Required negative/contract coverage is absent; verifier counterexamples are `10 failed`; mypy fails |
| DB Persistence | `FAIL` | Real PostgreSQL demonstrates wrong eligibility, dedup, lifecycle, provenance and idempotency behavior; replacement/child-copy atomicity is not proven and static code exposes partial-write risk |
| G5 Regression | `FAIL` | WP04-01 and WP03 focused regressions pass, but required full regression was not used to override already-proven blocking failures; original task cannot achieve L5 while core contract behavior fails |
| G6 Evidence | `FAIL` | Executor's 26-pass result covers only its reduced test set; Full Evidence Matrix requirements and numerous mandatory counterexamples are missing |

## Full Evidence Matrix

| AC | Requirement | Implementation Evidence | Verification Evidence | Boundary/Negative Evidence | Verdict |
|---|---|---|---|---|---|
| AC-01 [BLOCKING] | Exact SourceType/SourceGrade closed matrix | `services.py:84-100` | Verifier matrix equality test fails | Candidate helper uses forbidden `COMPANY_ANNOUNCEMENT + A` at test line 109 | `FAIL` |
| AC-02 [BLOCKING] | Source fingerprint uses exactly the contract fields | `services.py:347-382` hashes command payload | Static comparison with contract §8 | Includes operation/storage fields, omits document language, and conflates request hash with version identity | `FAIL` |
| AC-03 [BLOCKING] | Same bytes may create grade/metadata/status revision; identical fingerprint re-observes | `services.py:383-405` | PostgreSQL grade-reclassification verifier test fails | Content-hash duplicate check rejects a legal new fingerprint; new-key identical fingerprint raises instead of replay/re-observation | `FAIL` |
| AC-04 [BLOCKING] | Locator schema and coordinates follow §15 | `services.py:1464-1477` | Contract-valid `page_number` test fails | Code expects `page`; paragraph/table/cell/web/time validators are absent | `FAIL` |
| AC-05 [BLOCKING] | Current-valid is latest-first and fail-closed | `services.py:83,1055-1068` | PostgreSQL UNREVIEWED-current test fails | UNREVIEWED, PENDING_REVIEW and DISPUTED are declared eligible | `FAIL` |
| AC-06 [BLOCKING] | Lifecycle allowlist exactly matches §12 | `services.py:790-870` | PENDING_REVIEW→DISPUTED and UNREVIEWED→INVALIDATED verifier tests both fail | Legal UNREVIEWED→REJECTED is absent; dispute resolution uses wrong audit kind | `FAIL` |
| AC-07 [BLOCKING] | Trusted initial/correction verification is rule-controlled | `services.py:514-519,742,984` | Unknown-rule verifier test fails | Any truthy string elevates to VERIFIED; no registry or rule-specific validator exists | `FAIL` |
| AC-08 [BLOCKING] | DERIVED requires exact support and cycle-free lineage | `services.py:1400-1514` | Zero-support THESIS_INFERENCE verifier test fails | No required nonempty support, self/cycle graph traversal, or origin-key derivation | `FAIL` |
| AC-09 [BLOCKING] | CROSS_INSTRUMENT/MANUAL/DERIVED identities are service-derived | `services.py:479-552` | Static contract review | Caller supplies scope_key/origin_key; no cross-instrument sorted-set or manual/derived canonical derivation | `FAIL` |
| AC-10 [BLOCKING] | N+1 lifecycle/correction/tombstone copies mandatory immutable children | `services.py:1176-1236` | Static contract review | Locators/instrument links are copied, but derivation links are always passed as empty; revision cannot replace source/locator/link inputs | `FAIL` |
| AC-11 [BLOCKING] | Idempotency scope is operation + target aggregate | operation-only scopes throughout service | Two-series shared-key PostgreSQL verifier test fails | Different EvidenceSeries incorrectly conflict on the same client key | `FAIL` |
| AC-12 [BLOCKING] | Request hash covers complete canonical semantic payload | `services.py:553-565,725-735,934-942` | Static field-by-field review | Multiple value/unit/effective/link/manual/extractor/status/trusted fields are omitted | `FAIL` |
| AC-13 [BLOCKING] | Same-key/same-hash replay precedes expected-version check | `services.py:721-724` | PostgreSQL correction-replay test fails with version conflict | A successful prior correction cannot replay after current advances | `FAIL` |
| AC-14 [BLOCKING] | UNKNOWN_OUTCOME is reconciled, not treated as COMMITTED | `services.py:1611-1627` | Static review | Record status is ignored; a null/unconfirmed response reference is treated as replay | `FAIL` |
| AC-15 [BLOCKING] | Replacement mutation and idempotency/audit are one atomic boundary | `services.py:958-1009` | Static transaction review | Inner create commits a savepoint and `:inner` idempotency before a second outer savepoint; caller may catch failure and commit partial replacement | `FAIL` |
| AC-16 [BLOCKING] | Nullable corrections can explicitly clear a field | `services.py:1272-1273` | Static review | `None` always means “keep fallback”; no unset sentinel exists | `FAIL` |
| AC-17 [BLOCKING] | Automatic extraction records required extractor provenance | `services.py:1400-1461` | Static review | Validator does not receive actor/extractor metadata and accepts automatic source-backed Evidence without it | `FAIL` |
| AC-18 [BLOCKING] | Errors are stable and carry required contract details | `errors.py:8-85`; service validators | Static review | Several validation paths fall through to generic persistence conflict; locator/link/persistence details are incomplete | `FAIL` |
| AC-19 [BLOCKING] | Mandatory PostgreSQL examples/rollback tests exist | `tests/test_evidence_services.py` has 8 tests | Candidate suite 8/8 passes; verifier suite 0/10 passes | Missing most §24 scenarios; existing tests encode wrong grade, eligibility and trusted-rule semantics | `FAIL` |
| AC-20 [BLOCKING] | Required static/type gate passes | three candidate files | Ruff and compile pass; mypy reports 4 errors | Required `L2_BUILD_VERIFIED` not achieved | `FAIL` |
| AC-21 | Candidate stays within authorized file boundary | Git status/file inventory | Exact three untracked authorized files | No adjacent module changes | `PASS` |
| AC-22 | Previously accepted WP04-01 persistence/migration remains green | unchanged WP04-01 code/tests | Combined Evidence suite includes 17 persistence + 1 migration passing | Passing baseline cannot compensate for service-contract failure | `PASS` |
| AC-23 | WP03 Research remains green | unchanged Research code/tests | `16 passed, 4 warnings` | No Research typed-link or API work was introduced | `PASS` |

## Blocking Findings

### BF-01 — Frozen SourceGrade policy is broadened

`backend/evidence/services.py:84-100` permits many contract-forbidden grade/type combinations. The test helper at `tests/test_evidence_services.py:109-111` uses `COMPANY_ANNOUNCEMENT + A`, although the frozen matrix permits only `S`. This is a contract and test-standard failure.

### BF-02 — Source version identity and dedup are wrong

The fingerprint is computed from a generic command payload containing storage/operation fields and omitting required contract fields. A second check treats same `content_hash + media_type` as duplicate, which makes grade reclassification, metadata correction and retraction notice with unchanged bytes impossible. Real PostgreSQL reproduced the failure.

### BF-03 — Eligibility and lifecycle fail open

Initial UNREVIEWED Evidence is returned as current-valid. Illegal lifecycle transitions are accepted, a legal UNREVIEWED rejection path is missing, and arbitrary trusted-rule strings elevate corrected Evidence directly to VERIFIED.

### BF-04 — Provenance-derived identities and lineage are incomplete

MANUAL/DERIVED origin keys and CROSS_INSTRUMENT scope keys are accepted from callers rather than computed from canonical inputs. DERIVED Evidence can commit without supporting links; cycle checking is absent; N+1 status/tombstone construction drops derivation children.

### BF-05 — Idempotency and replacement atomicity are unsafe

Idempotency records are scoped only by operation, hashes omit semantic fields, correction replay happens after version checking, and UNKNOWN_OUTCOME is ignored. Replacement creates an inner mutation/idempotency savepoint and later writes a second idempotency record, so an outer failure can be reported while the earlier replacement remains committable in the caller transaction.

### BF-06 — Test evidence is materially insufficient and partially inverted

The new suite has only eight test functions and omits most mandatory examples and rollback checks. It explicitly asserts that initial UNREVIEWED is current-valid and uses an invalid grade pair and arbitrary trusted rules as successful fixtures. The verifier's ten targeted counterexamples all fail against real PostgreSQL.

### BF-07 — Required mypy gate fails

Fresh command against the two service files reports four task-related errors:

```text
backend/evidence/services.py:169: Name "normalized" already defined on line 162 [no-redef]
backend/evidence/services.py:172: Unsupported target for indexed assignment ("datetime") [index]
backend/evidence/services.py:174: Unsupported target for indexed assignment ("datetime") [index]
backend/evidence/services.py:1378: Argument 2 to "EvidenceDomainError" has incompatible type "**dict[str, str]"; expected "int | None" [arg-type]
```

## Commands Actually Executed

| Command | Result | Purpose |
|---|---|---|
| Git branch/HEAD/main/origin/status/log checks | exact branch and `3eb494e...` baseline; exactly 3 untracked candidate files | Baseline and scope |
| `pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs` | `8 passed, 2 warnings in 6.13s` | Reproduce candidate focused claim |
| `pytest ... test_evidence_services.py test_evidence_persistence.py test_evidence_migrations.py -rs` | `26 passed, 2 warnings in 22.22s` | Reproduce executor's Evidence suite |
| `PYTHONPATH=<candidate> pytest -p no:cacheprovider -q /tmp/test_wp04_02_verifier.py -rs` | `10 failed, 1 warning in 8.31s` | Independent PostgreSQL counterexamples |
| `pytest ... test_research_api.py test_research_persistence.py -rs` | `16 passed, 4 warnings in 11.90s` | WP03 regression |
| `ruff check --no-cache <3 candidate files>` | `All checks passed!` | Static lint |
| `ruff format --check --no-cache <3 candidate files>` | `3 files already formatted` | Format gate |
| `mypy --cache-dir=/tmp/... --show-traceback --explicit-package-bases backend/evidence/errors.py backend/evidence/services.py --ignore-missing-imports` | `4 errors in 1 file` | Type gate |
| `PYTHONPYCACHEPREFIX=/tmp/... python -m compileall -q backend apps migrations tests` | exit 0 | Compilation |
| `alembic -c migrations/alembic.ini heads` | `000000000004 (head)` | Migration graph unchanged |
| `git diff --no-index --check /dev/null <each candidate file>` | no whitespace errors | Diff hygiene for untracked files |

The first verifier-test invocation had a `/tmp` import/async configuration issue and did not constitute contract evidence. It was corrected by explicitly setting the candidate `PYTHONPATH` and asyncio mark; the final collected run executed all ten tests against real PostgreSQL and produced the failures above.

## Counterexample / Negative Verification

| Risk | Checked? | Evidence | Verdict |
|---|---|---|---|
| Contract matrix differs from implementation | Yes | Exact 15-entry equality assertion | `FAIL` |
| UNREVIEWED leaks into current-valid | Yes | Real PostgreSQL query returns the row instead of `None` | `FAIL` |
| Same bytes cannot receive grade reclassification | Yes | Real PostgreSQL command raises duplicate-source-version | `FAIL` |
| Contract-valid locator is rejected | Yes | `{page_number: 12}` raises invalid locator | `FAIL` |
| Source-less THESIS_INFERENCE commits without support | Yes | Command completes instead of raising | `FAIL` |
| Illegal lifecycle transitions mutate history | Yes | Both tested illegal transitions complete instead of raising | `FAIL` |
| Arbitrary trusted string promotes Evidence | Yes | Command completes instead of rejecting | `FAIL` |
| Same client key on different aggregates conflicts | Yes | Second series raises idempotency conflict | `FAIL` |
| Successful correction cannot replay after current advances | Yes | Retry raises stale-version conflict | `FAIL` |
| Existing persistence/migration behavior regressed | Yes | 18/18 existing WP04-01 tests remain green | Not found |
| WP03 Research behavior regressed | Yes | 16/16 focused Research tests remain green | Not found |

## DB Persistence Result

- Schema constraints: existing revision `000000000004` remains the sole Alembic head and prior persistence/migration tests pass.
- Read semantics: `FAIL`; current-valid returns ineligible statuses.
- Replace semantics: `FAIL`; identity derivation and replacement transaction atomicity are incomplete.
- Active/inactive/deleted/status: `FAIL`; lifecycle allowlist permits forbidden transitions.
- Transaction boundary: `FAIL`; replacement has nested two-stage idempotency/mutation scope and required rollback counterexamples are absent.
- Version/snapshot/history: append mechanics exist, but DERIVED N+1 loses mandatory support children and replay/version ordering is wrong.
- Real persistence vs InMemory/Fake/Mock: verifier used real PostgreSQL; no mock was used for the ten final counterexamples.

## Non-Blocking Findings

1. `list_evidence_by_instrument` performs an N+1 current-version query and should be reduced to one database query during repair if it can be done without scope expansion.
2. The service imports repository-private `_evidence_version_load_options`; a public repository helper would make ownership clearer, but this is secondary to correctness.
3. URL canonicalization always removes fragments. The frozen contract reserves a stable web-anchor case; document identity and locator-anchor handling should be made explicit during locator repair.

## Regression Result

- Result: `PARTIAL PASS EVIDENCE`, but overall G5 remains `FAIL` because the required task cannot pass while core contract behavior is wrong.
- Preserved behavior:
  - WP04-01 persistence/migration: `18 passed` within the combined Evidence run.
  - WP03 Research API/persistence: `16 passed`.
  - Alembic remains `000000000004 (head)`.
- Regression gaps: the full repository suite and known OpenAPI comparison were not run after the verifier had already proved multiple blocking contract failures; they cannot change the FAIL verdict and must be rerun after repair.

## Repair Required

- `YES`
- Repair ID: `TASK-WP04-02-R1`
- Failed AC/Gate: AC-01 through AC-20; G2 Contract, G3 Architecture, G4 Test, DB Persistence, G5 Regression, G6 Evidence.
- Passed items that repair must preserve: exact three-file scope unless explicitly narrowed, asynchronous SQLAlchemy style, no service commit, append-only historical rows, WP04-01 tests, WP03 tests, migration head, no API/OpenAPI/Research/frontend/runtime expansion.

## Final Decision Rationale

`FAIL`。候选的 26 项自有/既有测试可独立复现为通过，但它们只证明了一个缩小且部分错误的实现表面。冻结合同的关键 fail-closed 行为由代码静态证据和十个真实 PostgreSQL 反例共同证明不满足。尤其是错误的 SourceGrade 矩阵、UNREVIEWED current-valid、任意 trusted string 直升 VERIFIED、无支持 DERIVED 落库、非法生命周期、错误幂等 scope/replay 和非原子 replacement，会破坏 Evidence durable-truth、审计和不可变历史边界。

该候选不得提交、合并或进入 WP04-03。必须先完成 `TASK-WP04-02-R1`，然后重新执行完整独立验收。

## Next Action

按 `TASK-WP04-02-R1` 修复计划拆分执行，当前只派发同一隔离 worktree 上的 `TASK-WP04-02-R1A`。R1A 只允许更正现有三个候选文件中的 Source policy、SourceDocumentVersion identity/dedup/re-observation、SourceLocator 及对应测试；禁止提前进入 R1B/R1C/R1D、WP04-03、API/OpenAPI、WP04-04、schema/migration、worker/MinIO/parser/embedding/RAG/Thesis/Agent/Capability Runtime。
