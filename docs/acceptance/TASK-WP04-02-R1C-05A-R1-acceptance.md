# TASK-WP04-02-R1C-05A-R1 — Independent Repair Acceptance

**OVERALL: PASS**

## Metadata

- Task ID: `TASK-WP04-02-R1C-05A-R1`.
- Original task: `TASK-WP04-02-R1C-05A`.
- Date: 2026-09-16, Asia/Shanghai.
- Verifier: Codex, independent verifier role using `ai-task-governor`.
- Report path: `docs/acceptance/TASK-WP04-02-R1C-05A-R1-acceptance.md`.
- Implementation status received: `IMPLEMENTATION_COMPLETE`; treated as evidence input, not approval.
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Achieved acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Missing acceptance for this repair: none.
- Repair required: NO.
- Next task: `TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1`.

This PASS closes only the R1 repair of the historical initial-VERIFIED audit-tuple replay defect. It does not approve a positive initial-import validator, a positive trusted correction rule, all ordinary-correction qualification policy, R1D, whole R1C, whole WP04-02, Git integration, WP04-03 or WP04-04.

## Changed Files Snapshot

The fixed repair baseline was already dirty in exactly two candidate files. The independently observed final candidate is:

```text
candidate: /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service
branch: codex/wp04-02-evidence-domain-service
HEAD: 0cef44fd2ffd929b40e849e607af0bd4c44d14d2
parent: bdd70edc153b6ed5def65ed99c41f325df45f066
status:
 M backend/evidence/services.py
 M tests/test_evidence_services.py
```

Final candidate hashes:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
6e5c1c1c8cd83603a73c71c77993f76883f780fa773910fe3d026797e611aa69  backend/evidence/services.py
dce8c3644441399ef443d54073c3121e8f59ebcd330c6955458c5db703056308  tests/test_evidence_services.py
```

The independent verifier remains byte-identical:

```text
be68779f161c5983fce265bafe0b8237ae881feea7900a446c07ff03433ffb60  docs/acceptance/verifiers/test_wp04_02_r1c05a_audit_tuple_replay_r1_20260916.py
```

Main remained on `438738c543e4cae3e805d31324b068c1cd5c7059`, parent `7d3734bc8346c16f9bbf7f7d9806309949c996de`, with empty tracked/index diff. Existing untracked governance evidence was preserved. Attribution is CERTAIN from the fixed input hashes, final hashes, two-file candidate status and task-specific implementation locations.

## Classification

- Task type: REPAIR / backend domain service.
- Risk types: idempotency, lifecycle audit identity, historical compatibility, DB persistence and no-residue semantics.
- Touched layers: service and PostgreSQL tests.
- Task size: SMALL.
- Evidence matrix: Full because the repair changes audit/idempotent replay semantics on a persistent command path.
- Selected gates: G0 Baseline, G1 Scope, G2 Contract, G3 Architecture, G4 Test, DB Persistence, G5 Regression and G6 Evidence.

## Top Blocking AC Results

| Top AC | Result | Independent evidence |
|---|---|---|
| Fixed verifier originally represents the four missing conflicts | PASS | Previous acceptance and immutable verifier preserve the four isolated counterexamples. Executor supplied RED logs; current verifier bytes match the fixed hash. This acceptance does not relabel executor RED as a fresh pre-edit run. |
| Any one changed audit-tuple field conflicts before replay return | PASS | Fresh real-PostgreSQL fixed verifier: `4 passed in 3.94s`; code compares time, actor, kind and reason before returning the historical exact response. |
| Exact matching historical replay remains read-only and hash-compatible | PASS | Fresh candidate `-k r1c05a`: `11 passed`; matching replay, new-key denial, isolated conflicts and fresh-session no-residue assertions all passed. Request hash payload and existing idempotency rows were not redesigned. |
| Previously passed R1C/R1B/R1A behavior remains green | PASS | Fresh R1C-04A `87 passed`; R1C-03A oracle `58 passed`; five fixed verifiers `70 passed`; full Evidence service `337 passed`; persistence/migration/Research `35 passed`. |
| Scope and protected artifacts remain exact | PASS | Exactly two authorized candidate files remain modified; `errors.py`, verifier hash, HEAD/parent, Alembic head and main tracked/index state are unchanged. |

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| G0 Baseline | PASS | Original FAIL acceptance, R1 Repair Contract, execution feedback, fixed verifier, candidate identity/status and before/final hashes are available and attributable. |
| G1 Scope | PASS | Only `services.py` and `tests/test_evidence_services.py` are modified in the candidate. No request-hash migration, schema/API/error/frozen-contract/verifier/Git-history change occurred. |
| G2 Contract | PASS | All four isolated tuple changes raise the required conflict; exact matching replay and prior R1C-05A admission behavior remain intact. |
| G3 Architecture | PASS | The repair is a narrow post-replay compatibility check against the persisted exact response. It preserves historical request hashes and does not create a caller-controlled validator or positive trusted rule. |
| G4 Test | PASS | Fixed verifier, focused suites, full service suite, regression suite, Ruff, format, mypy and compileall passed freshly. |
| DB Persistence | PASS | Real PostgreSQL disposable fixtures exercised the production service. Candidate tests commit after rejection and compare nine tables from a distinct fresh session; no pending ORM mutation, key mutation or durable residue is accepted. |
| G5 Regression | PASS | Previously accepted R1C-04A, R1C-03A, R1C-02, R1C-01, R1B and R1A paths, plus persistence/migration/Research, are green. |
| G6 Evidence | PASS | Fresh command evidence, code locations, fixed verifier hash and boundary review are sufficient for every Blocking AC. Executor narrative was used only as a clue. |

## Full Evidence Matrix

| AC | Requirement | Implementation evidence | Verification evidence | Boundary/negative evidence | Verdict |
|---|---|---|---|---|---|
| AC-01 | A changed `status_changed_at` cannot borrow an old replay | Replay comparison in `backend/evidence/services.py` before trusted-rule replay return | Fixed verifier and candidate isolated parameter both pass | One-second time-only delta, same key/status/hash-covered fields | PASS |
| AC-02 | A changed actor cannot borrow an old replay | Same comparison loop; stable `mismatch_field` details | Fixed verifier and candidate isolated parameter both pass | Actor-only delta; caller commit and fresh-session equality | PASS |
| AC-03 | A changed kind cannot borrow an old replay | Same comparison loop; existing `EvidenceIdempotencyConflict` | Fixed verifier and candidate isolated parameter both pass | Kind-only delta; no version/idempotency/audit mutation | PASS |
| AC-04 | A changed reason cannot borrow an old replay | Same comparison loop; `reason=audit_tuple_mismatch` | Fixed verifier and candidate isolated parameter both pass | Reason-only delta; exact/current/history preserved | PASS |
| AC-05 | Exact historical replay remains compatible | Comparison is limited to persisted initial VERIFIED exact responses and leaves the original request hash unchanged | Candidate `r1c05a` focused `11 passed` | Same tuple returns same exact ID; new key still fails closed | PASS |
| AC-06 | Passed repair boundaries do not regress | No change to errors/schema/API/models/repositories/verifiers | Fresh `87 + 58 + 70 + 337 + 35` successful tests | Positive trusted/import/R1D behavior remains absent, not faked | PASS |

## Commands Actually Executed

The first two attempts exposed local command-resolution issues (`alembic` absent from one pytest PATH; `boto3` absent from the Conda pytest environment). They failed during collection/setup and were not treated as business results. No dependency was installed or upgraded. The final commands used the existing Homebrew Python 3.12 pytest with the existing Conda Alembic executable added to PATH.

| Command | Actual result | Purpose |
|---|---|---|
| Fixed audit-tuple verifier | `4 passed in 3.94s` | Directly close the previous four-case Blocking defect |
| Candidate `tests/test_evidence_services.py -k r1c05a` | `11 passed, 326 deselected` | Matching replay, default denial, four isolated conflicts and no-residue behavior |
| Candidate `-k r1c04a` | `87 passed, 250 deselected` | Preserve display-text admission/history behavior |
| R1C-03A boundary oracle | `58 passed` | Preserve trusted default-deny, route, audit and history behavior |
| Five fixed R1C-02/R1C-01/R1B/R1A verifiers | `70 passed` | Preserve accepted repair leaves |
| Full Evidence service suite | `337 passed, 2 warnings` | Full affected-domain regression |
| Evidence persistence/migrations plus Research regression | `35 passed, 4 warnings` | Cross-module persistence and Research regression |
| Ruff check / format | `All checks passed`; `3 files already formatted` | Static/style verification |
| mypy | `Success: no issues found in 3 source files` | Type verification |
| compileall | exit 0 | Syntax/bytecode verification |
| Alembic heads | `000000000004 (head)` | Migration-head preservation |
| `git diff --check`, status, HEAD/parent and SHA-256 | expected scope and hashes | Baseline/scope/integrity verification |

Warnings are the existing Starlette/TestClient, AnyIO alias and HTTP 422 deprecation warnings; they are not task failures.

## Counterexamples and Persistence Result

- Four audit-tuple members were changed one at a time with the same operation, idempotency key, verification status and all originally hash-covered fields. All four now reject.
- Exact tuple replay returns the same historical exact version read-only.
- New-key initial VERIFIED remains default-denied.
- Display/source/locator/status-enum payload changes still conflict through the existing request hash.
- Candidate tests assert no `new`, `dirty` or `deleted` ORM state after rejection, permit caller commit, then compare all rows/all columns in a distinct session across the nine Evidence/source/idempotency/audit tables.
- No schema, constraint, migration or stored request hash changed. Existing data compatibility is preserved without backfill.

## Findings and Final Decision

Blocking findings: NONE within this Repair.

Non-blocking/open program boundaries:

- Production approved trusted correction rules remain empty.
- Positive initial deterministic import and positive trusted correction remain unimplemented and unapproved.
- The complete ordinary-correction `from-status`, source-state and validity-window policy is unresolved.
- R1D aggregate-complete hashes, replay ordering, `UNKNOWN_OUTCOME`, replacement atomicity and concurrent reconciliation remain unimplemented.
- Whole `TASK-WP04-02-REVERIFY`, WP04-03, WP04-04 and Git integration remain unauthorized.

The former Blocking defect is now directly disproved by the immutable four-case verifier on real PostgreSQL, and the complete affected regression surface is green. Therefore the only valid verdict for `TASK-WP04-02-R1C-05A-R1` is `PASS`.

## Next Action

Dispatch `TASK-WP04-02-R1C-05B-QUALIFICATION-CONTRACT-R1`. It is a docs-only policy-contract task because the frozen lifecycle table and already accepted verifier behavior do not currently yield one unambiguous ordinary-correction `from-status` rule. It must produce an approval-ready matrix before any business-code enforcement. Do not enter R1D or enable a positive trusted/import rule yet.
