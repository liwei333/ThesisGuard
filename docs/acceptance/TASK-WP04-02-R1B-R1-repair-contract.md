# TASK-WP04-02-R1B-R1 Repair Contract

## Status

`READY_FOR_DISPATCH`

## Source

- Failed verification: `TASK-WP04-02-R1B-REBASELINE-REVERIFY-R1`
- Source report: `docs/acceptance/TASK-WP04-02-R1B-REBASELINE-REVERIFY-R1-acceptance.md`
- Candidate worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`
- Candidate branch: `codex/wp04-02-evidence-domain-service`
- Candidate HEAD baseline: `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`
- Current candidate hashes at failure:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
f1c4a9b85505cb152273a246525a4b3214eaaff0847c328f1d2ed2b350fadf0c  backend/evidence/services.py
454f95d269b7521764409b952ba26055c473d62c93c75313b16fa2e4fa66a0ce  tests/test_evidence_services.py
```

## Objective

Repair only the R1B derivation cycle validation defect: exact derivation support validation must operate on exact `EvidenceVersion` graph semantics and must not reject all historical exact supports from the same `EvidenceSeries`.

## Blocking Finding to Close

`_validate_derivation_links()` currently rejects:

```python
if support.evidence_series_id == derived_evidence_series_id:
    raise EvidenceInvalidDerivationLink(...)
```

This broad same-series prohibition blocks valid replacement routing where a new DERIVED replacement version supports an older exact version from the previous series lineage and no exact graph cycle exists.

## Allowed Files

Only:

- `backend/evidence/services.py`
- `tests/test_evidence_services.py`

`backend/evidence/errors.py` may remain unchanged. Do not add a fourth candidate file.

## Required Behavior

1. Preserve rejection of true exact self-reference where representable by current public commands.
2. Preserve rejection of indirect exact `EvidenceVersion` derivation cycles by graph traversal.
3. Allow a changed support set to include an older exact `EvidenceVersion` from the same prior series when that exact-version graph does not cycle.
4. Ensure that this allowed case routes to replacement EvidenceSeries v1, with:
   - `version == 1`;
   - `evidence_series_id` distinct from the old series;
   - `supersedes_evidence_version_id` pointing to the replaced exact version;
   - complete CORRECTION audit tuple;
   - fresh immutable `EvidenceDerivationLink` rows for the replacement version.
5. Preserve no-residue behavior for invalid derivation links.
6. Do not change source policy, locator validation, lifecycle/current-valid/trusted-rule behavior, R1D idempotency/replacement atomicity, schema, repositories, migrations, API/OpenAPI, Research typed links, frontend, worker, MinIO/parser/embedding/RAG, Thesis, Agent or Capability Runtime.

## Required Tests

Add or adjust focused PostgreSQL tests proving:

1. A DERIVED revision with changed support set `{old_exact_version, existing_support}` creates replacement v1 when the exact graph has no cycle.
2. Existing direct/indirect cycle tests still reject with `EVIDENCE_INVALID_DERIVATION_LINK`.
3. Duplicate and missing support failure paths still leave `EvidenceSeries`, `EvidenceVersion`, `EvidenceDerivationLink`, `EvidenceInstrumentLink`, `EvidenceSourceLocator`, `EvidenceIdempotencyRecord`, and `EvidenceAuditEvent` counts unchanged.
4. Existing R1B tests still pass.

The old candidate test that labels an older exact version from the same series as “self support” must be corrected to match exact-version semantics. Do not weaken real self/cycle checks.

## Required Verification

Run from the candidate worktree with real PostgreSQL:

```bash
pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1b -rs
pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
PYTHONPATH=/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service \
  pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs
PYTHONPATH=/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service \
  pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs
pytest -p no:cacheprovider -q \
  tests/test_evidence_persistence.py \
  tests/test_migrations.py \
  tests/test_evidence_migrations.py \
  tests/test_research_api.py \
  tests/test_research_persistence.py -rs
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports \
  --cache-dir=/tmp/tg-r1b-r1-mypy \
  backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1b-r1-pycache \
  python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
DATABASE_URL=postgresql+asyncpg://thesisguard:thesisguard_dev_password@127.0.0.1:15432/thesisguard \
  alembic -c migrations/alembic.ini heads
git diff --check
git status --short --branch --untracked-files=all
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

## Stop Conditions

Stop and report `BLOCKED` if:

- correcting exact-version cycle semantics requires model/repository/schema/migration changes;
- passing requires changing frozen contract semantics;
- passing requires entering R1C/R1D;
- real PostgreSQL is unavailable;
- candidate baseline or allowed file scope changes unexpectedly.

## Acceptance

This repair can only close `TASK-WP04-02-R1B-R1`. It does not close all of WP04-02 and does not authorize R1C until an independent verifier accepts the repair.

