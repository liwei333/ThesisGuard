# TASK-WP04-02-R1C-05A-R1 — Initial VERIFIED Audit-Tuple Replay Repair

- Original task: `TASK-WP04-02-R1C-05A`.
- Source acceptance: `docs/acceptance/TASK-WP04-02-R1C-05A-acceptance.md`.
- Verdict: `FAIL`.
- Failed AC: Top AC 3 — a changed lifecycle audit tuple must not borrow a historical initial-VERIFIED exact replay.
- Failed gates: G2 Contract, G3 Architecture, G4 Test and DB Persistence.
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Evidence matrix: Full.
- Role / type / size: EXECUTOR / REPAIR / SMALL.

## A. Execution Core

### Objective

Make a same-key historical `create_evidence_series_version` replay conflict when any one of `status_changed_at`, `status_changed_by_actor`, `status_change_kind` or `status_reason` differs from the committed exact response, while preserving byte-compatible historical request hashes, exact matching replay and every already-passed R1C-05A behavior.

### Fixed repair baseline

```text
candidate: /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service
branch: codex/wp04-02-evidence-domain-service
HEAD: 0cef44fd2ffd929b40e849e607af0bd4c44d14d2
parent: bdd70edc153b6ed5def65ed99c41f325df45f066
status:
 M backend/evidence/services.py
 M tests/test_evidence_services.py
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
cd4fd5a32a6cebe123e76e0a668cafc6f19e4455863af1a954c7f06bff511207  backend/evidence/services.py
f8c36c6e2efdc549f0d36da5cb7575cf60892b188c4926350fa658bbcb8f1386  tests/test_evidence_services.py
```

Main must remain at `438738c543e4cae3e805d31324b068c1cd5c7059` with empty tracked/index diff. Read main `AGENTS.md`, the original R1C-05A contract, its FAIL acceptance, this Repair Contract and the frozen lifecycle/idempotency sections before editing.

Fixed independent verifier:

```text
/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c05a_audit_tuple_replay_r1_20260916.py
SHA-256: be68779f161c5983fce265bafe0b8237ae881feea7900a446c07ff03433ffb60
```

Do not modify that verifier.

### Root evidence

- `backend/evidence/services.py:667-679` hashes `verification_status` but not the four status audit fields.
- `services.py:681-694` returns a historical exact response without comparing those fields.
- `tests/test_evidence_services.py:4732-4738` changes `verification_status` together with the tuple, so it does not isolate the missing behavior.
- The fixed verifier changes exactly one tuple member while keeping the same key, status and all hash-covered fields. Current result is `4 failed`, each `DID NOT RAISE EvidenceIdempotencyConflict`.

### Top Blocking AC

1. The unchanged repair baseline must reproduce the fixed verifier RED as exactly four missing idempotency conflicts; permission/setup/cleanup failure is not valid RED.
2. At GREEN, independently changing any one of the four audit fields under the same historical key must raise `EvidenceIdempotencyConflict` before returning the old response and without any durable writes or key mutation.
3. An exact match of the historical operation/key/hash and all four audit fields must still return the same exact EvidenceVersion ID read-only. Do not invalidate old stored request hashes or require a data migration.
4. Preserve all already-passed R1C-05A behavior: new unqualified initial VERIFIED denial, new-key denial, display/source/locator/status-enum conflicts, ordinary UNREVIEWED→review→verify, disclosed test-only seed, no-residue and stable error details.
5. Only the two candidate files may change; fixed verifier/oracle/history artifacts remain byte-identical. Full regression and static checks must pass at final hashes.

### Allowed changes

- `backend/evidence/services.py`.
- `tests/test_evidence_services.py`.

### Must fix

- Add candidate-owned isolated tests for each tuple member, not one vector that also changes `verification_status`.
- On the `create_evidence_series_version` committed replay path, compare the requested initial-verification audit tuple with the persisted exact response before returning it. Any mismatch must raise the existing `EvidenceIdempotencyConflict` with stable field/mismatch details if supported by the existing error style.
- Keep the original request hash and historical idempotency record compatible. This repair is a narrow post-replay compatibility check; it must not broaden into the complete R1D request-hash redesign.
- For each mismatch: caller commit must succeed; a distinct fresh session must prove all rows/all columns in the nine relevant tables, exact history, children, current and idempotency record are unchanged.

### Preserve

- The initial VERIFIED fail-closed guard at its current post-replay/pre-write boundary.
- Exact matching historical replay.
- R1C-04A display-text rules and all 87 focused cases.
- R1C-03A oracle, R1C-02, R1C-01, R1B and R1A verifier behavior.
- Caller-owned outer transaction; service never commits.
- Append-only history, immutable children and production approved trusted rule set remaining empty.
- Public function signatures, schema, models, repositories, migration and Alembic head.

### Forbidden

- No change to the fixed verifier, old verifiers, oracle, frozen contract, old reports/logs/manifests or `errors.py`.
- No global expansion/reversion of every idempotency hash field, hash-version migration, UNKNOWN_OUTCOME, concurrency or replacement atomicity work; those remain R1D.
- No positive initial-import validator, trusted rule, parser/MinIO/source-byte feature or test-only production branch.
- No weakening of the candidate's current tests; add isolated coverage instead.
- No commit, merge, rebase, reset, checkout, push, branch movement or main tracked mutation.

### Required verification

Use only the existing `127.0.0.1:15432` disposable PostgreSQL fixture through normal permissions. Do not set the three diagnostic/admin variables or change the database route.

```bash
# First reproduce RED on unchanged repair baseline.
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q \
  /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c05a_audit_tuple_replay_r1_20260916.py -rs

# Then obtain GREEN on the same fixed verifier and candidate focused suites.
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q \
  /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c05a_audit_tuple_replay_r1_20260916.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1c05a -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1c04a -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q \
  /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q \
  /tmp/test_wp04_02_r1c_02_independent_20260915.py \
  /tmp/test_wp04_02_r1c_01_independent_20260915.py \
  /tmp/test_wp04_02_r1b_r1_wiring_20260915.py \
  /tmp/test_wp04_02_r1b_reverify.py \
  /tmp/test_wp04_02_r1a_verifier.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q \
  tests/test_evidence_persistence.py tests/test_migrations.py \
  tests/test_evidence_migrations.py tests/test_research_api.py \
  tests/test_research_persistence.py -rs
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports \
  --cache-dir=/tmp/tg-r1c05a-r1-mypy \
  backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1c05a-r1-pycache python -m compileall -q \
  backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
git diff --check
git status --short --branch --untracked-files=all
git rev-parse HEAD HEAD^
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

### Stop conditions

Stop and report `BLOCKED` if the fixed baseline/verifier hash differs; the four-case verifier does not reproduce RED before edits; the repair would require changing request-hash history/schema/API/errors/old verifiers; database permission/fixture/cleanup is unavailable; or any third candidate file is required.

### Evidence and executor response

Report only `IMPLEMENTATION_COMPLETE` or `BLOCKED`. Include baseline/final hashes, fixed verifier RED→GREEN, exact replay comparison code location, four isolated candidate tests, caller-commit/fresh-session no-residue proof, exact matching replay preservation, every regression command/result and remaining R1C/R1D boundaries. The executor cannot self-approve.

## B. Governance Appendix

Apply `systematic-debugging`, `test-driven-development` and `verification-before-completion`. This repair closes only the failed audit-tuple replay condition. It does not complete positive initial import, positive trusted correction, full R1C policy qualification, R1D, WP04-02 re-verification or Git integration.
