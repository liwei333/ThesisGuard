# TASK-WP04-02-R1B-R2 Independent Reverify Acceptance

**OVERALL: PASS**

## Metadata

- Task ID: `TASK-WP04-02-R1B-R2-INDEPENDENT-REVERIFY`.
- Date: 2026-09-15, Asia/Shanghai.
- Role: independent VERIFIER; no business code edits, no verifier edits, no R3, no R1C/R1D implementation.
- Report path: `docs/acceptance/TASK-WP04-02-R1B-R2-INDEPENDENT-REVERIFY-acceptance.md`.
- Candidate worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`.
- Candidate branch: `codex/wp04-02-evidence-domain-service`.
- Candidate HEAD: `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`.
- Candidate parent: `3eb494e6613cf3952ffbaaf4166b8cf3ea801555`.
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Achieved acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Scope decision: this PASS closes the R1B-R2/R1B exact-target repair boundary only. It does not close all of original WP04-02, does not authorize Git integration, and does not implement or accept R1C/R1D.

## Authorization / Permission Result

User approval basis:

- Earlier in this conversation, the user explicitly approved the original R2 six pytest commands and their existing fixture subprocesses / temporary PostgreSQL database operations after disclosure that tests connect to local `127.0.0.1:15432`, create random temporary databases, run migrations/tests inside them, normally clean their own temporary databases, consume local resources, and may leave residue on failure.
- The current user request explicitly directed `TASK-WP04-02-R1B-R2-INDEPENDENT-REVERIFY`, required confirmation of the disclosed local temporary PostgreSQL operation approval, and required using the normal permission mechanism.

Normal permission outcome:

- All six required pytest commands that use local disposable PostgreSQL fixtures were executed through `require_escalated`.
- No permission rejection occurred.
- No alternate host, alternate port, proxy, Docker workaround, arbitrary SQL, shared/production DB reset, or broad cleanup was used.
- `TG_TEST_ADMIN_DATABASE_URL=UNSET`; fixture defaults therefore target local loopback `127.0.0.1:15432/postgres`. Passwords were not printed.
- No fixture setup or cleanup error was observed in command outputs. No broad residue scan or prefix cleanup was performed; no known temporary database residue was reported by pytest.

## Baseline / Scope

Fresh candidate status before and after verification:

```text
## codex/wp04-02-evidence-domain-service...origin/codex/wp04-02-evidence-domain-service
 M backend/evidence/services.py
 M tests/test_evidence_services.py
```

Fresh final hashes:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
2f90167c131cf91c715fc7fb19ead5af9745fab3259c7af0c875474bb0ce444f  backend/evidence/services.py
a8b5e8e814230b21d732f2e973a62cdd0b69d00455ea29130b1750994d8bed2a  tests/test_evidence_services.py
909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786  /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
```

Additional verifier hashes:

```text
0f7cea4d14735bd165b75d756444259a64483a97e6a338227bc09af806490cc9  /tmp/test_wp04_02_r1b_reverify.py
66be45f354d1df34370eedd9811b3bc68cf29852d45027ea576a67975b18ddfe  /tmp/test_wp04_02_r1a_verifier.py
```

Scope evidence:

- `backend/evidence/errors.py` remains byte-identical to the required hash.
- Candidate HEAD and parent remain unchanged.
- Candidate still has only the two allowed modified business files.
- Cumulative candidate diff relative to HEAD remains:

```text
backend/evidence/services.py    |  564 +++++++++++++++++---
tests/test_evidence_services.py | 1102 +++++++++++++++++++++++++++++++++++++++
2 files changed, 1599 insertions(+), 67 deletions(-)
```

This is cumulative candidate diff, including earlier R1B/R1 work; this verifier does not attribute all lines to R2.

Main worktree note:

- Main already had unrelated modified/untracked governance files before this report, including `AGENTS.md`, `docs/ARCHITECTURE_REFERENCES.md`, Sector Crowding governance, and WP04 acceptance/contract records.
- This verifier added only this independent reverify acceptance report.

## Evidence Matrix

| AC | Requirement | Fresh Evidence | Verdict |
|---|---|---|---|
| AC-01 | Fresh DERIVED create/replacement/append/status writes use actual new exact ID before new version/children persistence. | Source review: `create_evidence_series_version` constructs `EvidenceVersion(id=uuid_str())` at `services.py:713-765`, calls `_validate_derivation_links(... proposed_derived_evidence_version_id=version.id)` before `db.add` / `db.flush` at `services.py:766-770`. Append/status path constructs `EvidenceVersion(id=uuid_str())` at `services.py:1396-1450`, validates before `db.add` / `db.flush` at `services.py:1451-1454`. Replacement delegates through `create_evidence_series_version` with replacement children at `services.py:1159-1201`. Candidate timing test asserts `(result.id, False)` in validation and traversal observations and then confirms persisted row ID equals `result.id` at `tests/test_evidence_services.py:1446-1593`. | PASS |
| AC-02 | wiring verifier three nodes and four-path timing tests pass against real PostgreSQL. | `/tmp/test_wp04_02_r1b_r1_wiring_20260915.py`: `3 passed in 5.17s`. `tests/test_evidence_services.py -k r1b`: `9 passed`; includes four-path timing test for create, same-series revision, replacement, status append. | PASS |
| AC-03 | exact self/cycle defense, legal historical support replacement, immutable children, and no-residue behavior preserved. | `/tmp/test_wp04_02_r1b_reverify.py`: `4 passed`. `/tmp/test_wp04_02_r1a_verifier.py`: `12 passed`. Focused R1B suite: `9 passed`. Full service suite: `100 passed`. Source review confirms exact helper tests at `tests/test_evidence_services.py:1345-1443`, legal replacement/no-residue coverage at `tests/test_evidence_services.py:1052-1342`, and replacement/child immutability coverage at `tests/test_evidence_services.py:1596+`. | PASS |
| AC-04 | Original full pytest and static matrix pass; candidate hash/HEAD/status unchanged. | Six pytest commands all exit 0. Ruff, format, mypy, compileall, Alembic heads, diff check all exit 0. Final status/HEAD/hashes match required values. | PASS |
| AC-05 | No verifier edits, no business code edits by verifier, no R1C/R1D, no Git history mutation. | Candidate status before/final unchanged with only two modified business files. No commit/merge/rebase/push/checkout/reset run. No business file write occurred. This report is the only new project file. | PASS |

## Commands Executed

All commands below were executed from the candidate worktree unless noted otherwise.

### Required Pytest Matrix

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_r1_wiring_20260915.py -rs
```

Result: exit 0, `3 passed in 5.17s`.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs
```

Result: exit 0, `4 passed in 5.05s`.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs
```

Result: exit 0, `12 passed in 9.25s`.

```bash
pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1b -rs
```

Result: exit 0, `9 passed, 91 deselected, 2 warnings in 8.00s`.

```bash
pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
```

Result: exit 0, `100 passed, 2 warnings in 70.71s`.

```bash
pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
```

Result: exit 0, `35 passed, 4 warnings in 23.77s`.

Warnings:

- Existing FastAPI/Starlette/httpx deprecation warning.
- Existing anyio `BlockingPortal` deprecation warning.
- Existing Starlette `HTTP_422_UNPROCESSABLE_ENTITY` deprecation warning in `tests/test_research_api.py::test_read_and_request_validation_errors`.

### Static / Build / Git Matrix

```bash
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

Result: exit 0, `All checks passed!`.

```bash
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

Result: exit 0, `3 files already formatted`.

```bash
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1b-r2-independent-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

Result: exit 0, `Success: no issues found in 3 source files`; advisory note only: unused mypy config sections for `boto3.*`, `botocore.*`, `dramatiq.*`.

```bash
PYTHONPYCACHEPREFIX=/tmp/tg-r1b-r2-independent-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

Result: exit 0, no output.

```bash
alembic -c migrations/alembic.ini heads
```

Result: exit 0, `000000000004 (head)`.

```bash
git diff --check
```

Result: exit 0, no output.

```bash
git status --short --branch --untracked-files=all
git rev-parse HEAD HEAD^
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
```

Result: exit 0; final status, HEAD/parent, and hashes are recorded in the Baseline / Scope section above.

## Source Review Notes

- The target-aware validation branch is not helper-only anymore. Production create and append paths pass `version.id` into `_validate_derivation_links`.
- The target ID is service-generated by `uuid_str()` before persistence. It is not caller-controlled, not a series ID, not the prior exact ID, and not `None`.
- The target-aware validation call happens before the new version is added/flushed, so cycle/self checks run before the new EvidenceVersion and its children are persisted.
- The four-path timing test observes real `_validate_derivation_links`, real `_support_graph_reaches_exact_version`, and real `AsyncSession.flush`; it records timing only and forwards behavior.
- Public future-ID unrepresentability remains a structural limit, but it no longer excuses production wiring: the service now creates the future exact ID internally before write.

## Acceptance Decision

`PASS`.

Rationale:

- The independent verifier ran the original R2 full required matrix against the actual candidate and local disposable PostgreSQL fixtures.
- The verifier-owned wiring test that previously failed with missing targets is now green.
- Candidate tests independently prove create, replacement, same-series append, and status append validate the real new exact ID before flush and that the persisted row ID matches the validated target.
- R1A verifier, R1B verifier, focused R1B tests, full service tests, and persistence/migration/research regressions are green.
- Static/build checks are green.
- HEAD, scope, errors.py hash, verifier hash, and allowed two-file candidate state are preserved.

This PASS authorizes the dispatcher to close the R1B-R2/R1B repair boundary and select the next repair-program task, expected to be R1C Lifecycle/current-valid/trusted verification, under a separate development contract. It does not close all WP04-02, does not authorize R1C implementation in this verifier turn, and does not authorize Git integration.
