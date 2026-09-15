# TASK-WP04-02-R1B-R1 Execution Contract

Status: `READY_FOR_DISPATCH`

## Execution Core

- Task ID: `TASK-WP04-02-R1B-R1`.
- Type / size: Bug Fix / SMALL.
- Required acceptance: L1, L2, L3, L4_DB; Full evidence matrix.
- Goal: repair derivation validation on exact EvidenceVersion IDs, permitting acyclic historical-version supports without weakening true exact self-link/cycle defense.
- Sources: frozen `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`; existing `TASK-WP04-02-R1B-R1-repair-contract.md`, reverify acceptance and dispatch confirmation in this directory.
- This dispatcher-authored companion clarifies the original repair contract's phrase "existing direct/indirect cycle tests": only genuine exact-version cycles must remain rejected. Both existing series-based negative expectations must be corrected. It does not change the frozen contract or authorize broader work. The executor must not edit either contract.

Work only in `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`, branch `codex/wp04-02-evidence-domain-service`, accepted HEAD `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`, parent `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`.

Preflight: inspect AGENTS.md, related contract/source/tests, Git status, existing verifier fixtures/environment; confirm current SHA-256:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
f1c4a9b85505cb152273a246525a4b3214eaaff0847c328f1d2ed2b350fadf0c  backend/evidence/services.py
454f95d269b7521764409b952ba26055c473d62c93c75313b16fa2e4fa66a0ce  tests/test_evidence_services.py
```

Expected pre-existing candidate changes: only services.py and test_evidence_services.py modified. Preserve these changes and all main-worktree untracked governance records.

## Scope / Must Not

Allowed edits only: `backend/evidence/services.py` and `tests/test_evidence_services.py`. Keep errors.py byte-identical; add no fourth candidate file.

No commit, merge, rebase, reset, checkout, push, branch movement or main mutation. Do not edit docs/contracts, external `/tmp` verifiers, models, repositories, migrations/schema, API/OpenAPI, Research, frontend, worker, storage/parser/embedding/RAG, Thesis/Agent/Capability Runtime. No R1C lifecycle/current-valid/trusted-rule work or R1D replay/UNKNOWN_OUTCOME/atomicity redesign. Do not disable graph checks, tests or independent verifiers; no mock-only acceptance or unrelated formatting/refactors.

## Top Blocking Acceptance Criteria

1. **Exact graph semantics:** both direct validation and graph traversal use the proposed/new exact EvidenceVersion as the self/cycle target. Neither prior series identity nor a set of prior series versions is a proxy. Creation/replacement/append write paths retain the appropriate production validation. Acyclic prior-version chains are allowed, genuine exact self-links and return paths rejected.
2. **Legal public replacements:** (a) changed supports `{old derived exact, existing source exact}`; (b) `new B replacement -> old A -> old B -> source`. Both succeed without an exact cycle. Verify replacement v1, distinct series, predecessor exact ID, complete CORRECTION tuple, fresh children, unchanged old versions/links.
3. **True defense:** add real-PostgreSQL exact-target self-link and multi-hop return-path coverage via production validator/helper if the public API cannot represent a new version ID. Also test acyclic multi-hop reachability and traversal termination. Document structural limits; do not mutate old production links or substitute a series cycle. Tests must exercise production code, not a copied algorithm.
4. **Preserve green behavior:** R1A verifier, non-defective R1B identities/routing/nullable clear/metadata-only N+1 child copy, stable error codes and focused regressions remain green. Missing/duplicate supports still fail with no residual rows in the seven relevant tables. Do not broaden atomicity work.
5. **Evidence and scope:** all required verifications below executed against actual candidate; no skips or verifier edits, errors.py unchanged, allowed two-file scope only. Any blocking failure prevents acceptance.

## Execution Strategy

Reproduce the verifier-owned failing node before edits; add minimal red regressions, then implement the smallest fix. Inspect `_validate_derivation_links`, `_support_graph_reaches_series`, `_resolve_revision_children` and replacement/append routing together. Merely deleting the direct same-series guard or removing validation on replacement is insufficient. Correct both misleading negative test blocks in `test_r1b_derived_identity_links_validation_and_cycle_defense`, preserving valid negative assertions separately.

## Required Verification

Run from the candidate worktree using the existing test PostgreSQL environment. Use no bytecode writes into protected verifiers; local cache paths may be under `/tmp`. Do not reset the shared DB. Missing verifier files require BLOCKED, not reconstruction or skipping.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs
pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1b -rs
pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1b-r1-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1b-r1-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
git diff --check
git status --short --branch --untracked-files=all
git rev-parse HEAD
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

Alembic uses the existing local test DATABASE_URL; expected head `000000000004`. Request necessary local DB access through the product permission mechanism; do not bypass denied authorization.

## Stop Conditions and Deliverables

Report `BLOCKED` for changed baseline/hashes/scope, unavailable real DB/verifier, or need for frozen-contract, schema/repository, R1C/R1D or other forbidden changes. Explain evidence and missing authority; do not silently adapt the task.

Executor final status only `IMPLEMENTATION_COMPLETE` or `BLOCKED`, not an acceptance PASS. Report before/after changed-file snapshots and hashes, exact commands/exit codes/results, TOP-AC -> production location -> test/DB evidence, actual achieved/missing acceptance levels, public-cycle representability limits, and remaining risks. Keep code uncommitted for independent acceptance. This repair does not close original WP04-02 or authorize R1C automatically.
