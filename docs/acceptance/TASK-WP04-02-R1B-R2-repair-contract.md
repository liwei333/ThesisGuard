# TASK-WP04-02-R1B-R2 Repair Contract

Status: `READY_FOR_DISPATCH`

## A. Execution Core

- Task ID / Repair ID: `TASK-WP04-02-R1B-R2` (second R1B repair candidate).
- Original task: `TASK-WP04-02-R1B`; failed repair: `TASK-WP04-02-R1B-R1`.
- Source acceptance: `TASK-WP04-02-R1B-R1-acceptance.md` in this directory.
- Objective: wire the already-correct exact-version self/cycle validator into actual DERIVED version creation, replacement and append writes, using the actual new exact ID before persistence.
- Why now: R1 removed series-level overblocking but the graph-defense branch is invoked only in tests, violating its production-wiring AC.
- Task type / size: REPAIR / SMALL; one failure boundary, two files.
- Required acceptance: L1_STATIC_REVIEWED, L2_BUILD_VERIFIED, L3_CONTRACT_VERIFIED, L4_DB_VERIFIED.
- Evidence matrix: Full.

### Preflight / Baseline

Candidate worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`.

Branch: `codex/wp04-02-evidence-domain-service`.

HEAD must remain `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`, parent `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`.

Inspect AGENTS.md, frozen Evidence contract derivation constraints, R1 execution contract, this contract and source acceptance, production create/replacement/append paths and all R1B tests. Confirm initial status contains only services.py and test_evidence_services.py modifications, and hashes:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
2659bc4d06bd60c242a389365e96e60e4cc9bef0f31d5d924ef43e1e23da8331  backend/evidence/services.py
16784fc35abb8db4a41f7ed90307f3710edf52df98594a39b3cf707371e83681  tests/test_evidence_services.py
```

Preserve the existing candidate and main's untracked governance files. The accepted baseline is not changed by this repair.

### Top Blocking AC

1. **Production-wired exact target:** every fresh DERIVED version write, including create, replacement and existing append paths with copied derivation children, runs target-aware validation using the ID that the new version will actually persist. Assign it before new version/derivation children are flushed. Neither omitted/None target nor old exact/series ID is an acceptable substitute. No test-only branch or helper-only implementation.
2. **Actual reachability defense:** the production validator performs exact self checks and traverses exact supporting-version edges against that target within the caller-owned transaction. Negative helper self/multi-hop cycle coverage remains real-DB and green. Public future-ID unrepresentability is documented, not used to skip production wiring. Preserve deterministic rejection/no-residue behavior.
3. **Preserve R1 gains:** both legal public replacement chains remain allowed with correct v1/new-series/predecessor/CORRECTION tuple/fresh immutable children. Same-support metadata-only N+1 preserves identity/children; old versions/links unchanged. Keep R1A, all non-defective R1B identity/provenance/nullable-clear/no-residue behavior and stable errors.
4. **Verification and scope:** three verifier-owned wiring nodes, original R1B/R1A verifiers, full service/regression/static matrix are green; errors.py byte-identical, allowed two-file modifications only, Git HEAD/branch unchanged.

### Allowed / Forbidden Scope

Allowed edits only:

- `backend/evidence/services.py`
- `tests/test_evidence_services.py`

Keep errors.py unchanged; no fourth candidate file. No models/repositories/schema/migration/public API change is authorized. ID allocation must remain a service-level implementation detail and must not become a caller-controlled parameter, lineage input or request-hash field. Preserve existing idempotency/replay semantics; no R1D redesign.

No commit, merge, rebase, reset, checkout, push, branch movement, main mutation, docs/contract edits, edits to verifier-owned `/tmp` files, unrelated refactors/dependency upgrades/formatting churn. No R1C lifecycle/current-valid/trusted-rule work or R1D UNKNOWN_OUTCOME/atomicity redesign. No API/OpenAPI/Research/frontend/worker/storage/parser/embedding/RAG/Thesis/Agent/Capability Runtime work.

### Must Fix / Execution Strategy

First reproduce `/tmp/test_wp04_02_r1b_r1_wiring_20260915.py` failures. Its verifier-owned SHA-256 is `909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786`; do not edit it. Add minimal production-wiring regressions and repair at the existing service write boundary. Reuse the current exact-target validator/traversal; do not reintroduce the series prohibition or refactor the whole domain service.

Prevalidation of role/existence/duplicates may remain separate from final target-aware validation, but it must not substitute for that final check. Ensure the persisted new ID matches the validated target and validation precedes persistence of new version/derivation rows. Do not commit inside the service, mutate old links, or insert a provisional EvidenceVersion just to obtain an ID.

Use observer instrumentation only to measure genuine production calls; do not stub validators or fake DB results. Add candidate tests proving actual target equality and pre-write timing for create, same-series revision, replacement, and an existing DERIVED status-append path using its currently supported transition. This last test is wiring coverage only: do not modify lifecycle rules.

### Required Verification

Run from the candidate worktree with real migrated isolated PostgreSQL. Use the existing local test environment; do not reset the shared DB or expose credentials. All R1 Required Verification remains binding, plus the new production-wiring verifier:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_r1_wiring_20260915.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs
pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1b -rs
pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1b-r2-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1b-r2-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
git diff --check
git status --short --branch --untracked-files=all
git rev-parse HEAD
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

Alembic uses the existing local test DATABASE_URL; head remains `000000000004`. New tests may increase counts, but no deletion/skip/xfail/weakening is allowed. Verifier instrumentation forwards to the real existing validator/helper; it is not permission to build test-specific production behavior.

### Stop Conditions / Expected Evidence

Report BLOCKED for changed initial baseline/hashes/scope, missing verifier or real DB, or need for forbidden changes/new authority. Do not silently substitute a different task, reconstruct an external verifier or weaken AC.

Report before/after status and hashes, TOP-AC -> production locations -> real DB/test result, actual ID validation/persistence equality and timing evidence, exact commands/exits/results, achieved/missing acceptance levels and remaining limitations. Keep candidate uncommitted for independent acceptance.

## B. Governance Appendix

Preserve R1A and now-green R1B behavior; acceptance uses the frozen contract and source R1 acceptance, not executor claims. This is a focused continuation of the existing graph-defense repair, not a new business feature. Executor cannot change contracts/tests to manufacture green results or self-approve.

Executor final status only `IMPLEMENTATION_COMPLETE` or `BLOCKED`. Independent acceptance must close R2 and R1B before R1C. Original WP04-02 remains FAIL until the ordered R1C/R1D repairs and original full REVERIFY complete. This document's READY status does not authorize Git integration.
