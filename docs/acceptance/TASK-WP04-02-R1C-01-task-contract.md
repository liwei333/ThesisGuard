# TASK-WP04-02-R1C-01 Development Contract

Status: `READY_FOR_DISPATCH_AFTER_USER_AUTHORIZATION`

## A. Execution Core

- Task ID: `TASK-WP04-02-R1C-01`.
- Parent repair program: `TASK-WP04-02-R1C` from `docs/acceptance/TASK-WP04-02-R1-repair-contract.md`.
- Role: business repair implementer for one minimal R1C slice.
- Objective: fix latest-first lifecycle eligibility for current-valid Evidence reads.
- Candidate worktree: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`.
- Candidate branch: `codex/wp04-02-evidence-domain-service`.
- Required starting HEAD: `bdd70edc153b6ed5def65ed99c41f325df45f066`.
- Required parent: `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`.
- Type / size: `REPAIR / SMALL`.
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Evidence matrix: `Full`.

## B. Required Reading

Before editing, read:

- Main `AGENTS.md`.
- `docs/acceptance/TASK-WP04-02-R1C-BASELINE-CONFIRM-R1-acceptance.md`.
- `docs/acceptance/TASK-WP04-02-R1C-BASELINE-CONFIRM-R1-task-contract.md`.
- `docs/acceptance/TASK-WP04-02-R1B-R2-INDEPENDENT-REVERIFY-acceptance.md`.
- `docs/acceptance/TASK-WP04-02-R1B-R2-REVERIFY-FEEDBACK-REVIEW-acceptance.md`.
- `docs/acceptance/TASK-WP04-02-R1-repair-contract.md`.
- `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`, especially sections 8, 12, 13, 22, examples 23 through 26, example 41, and D-06/D-07/D-15.
- Candidate `backend/evidence/services.py`.
- Candidate `tests/test_evidence_services.py`.

## C. Baseline Gate

Stop with `BLOCKED` before any edit unless all are true:

- `git branch --show-current` is `codex/wp04-02-evidence-domain-service`.
- `git rev-parse HEAD` is `bdd70edc153b6ed5def65ed99c41f325df45f066`.
- `git rev-parse HEAD^` is `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`.
- `git status --short --branch --untracked-files=all` shows a clean candidate worktree.
- Fixed hashes match:

```text
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
2f90167c131cf91c715fc7fb19ead5af9745fab3259c7af0c875474bb0ce444f  backend/evidence/services.py
a8b5e8e814230b21d732f2e973a62cdd0b69d00455ea29130b1750994d8bed2a  tests/test_evidence_services.py
909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786  /tmp/test_wp04_02_r1b_r1_wiring_20260915.py
0f7cea4d14735bd165b75d756444259a64483a97e6a338227bc09af806490cc9  /tmp/test_wp04_02_r1b_reverify.py
66be45f354d1df34370eedd9811b3bc68cf29852d45027ea576a67975b18ddfe  /tmp/test_wp04_02_r1a_verifier.py
```

If the baseline differs, do not silently rebaseline, do not checkout/reset/rebase, and do not create R3.

## D. In Scope

Only repair the latest-first lifecycle eligibility slice:

- `get_current_valid_evidence` must first read the highest EvidenceVersion for the series.
- For downstream current-valid eligibility, latest `VERIFIED` is eligible unless blocked by existing source lifecycle checks.
- Latest `UNREVIEWED`, `PENDING_REVIEW`, `DISPUTED`, `REJECTED`, `INVALIDATED`, or `RETRACTED` must make the series currently unavailable for that role.
- The query must never scan backward or return an older `VERIFIED` version when the latest version is ineligible.
- Exact historical reads and history listing must continue to return older versions, including older `VERIFIED` rows.
- Ordinary same-series correction and ordinary replacement rows that become `UNREVIEWED` must not inherit current-valid eligibility from the prior exact version.
- Existing R1A behavior, R1B exact-target wiring, immutable child rows, legal historical support links, and no-residue guarantees must remain intact.

Expected minimal code surface:

- `backend/evidence/services.py`
- `tests/test_evidence_services.py`

`backend/evidence/errors.py` must remain byte-identical. Do not add a fourth business file unless a verifier or dispatcher issues a separate contract.

## E. Out of Scope

Do not implement or claim completion for:

- Full lifecycle state-transition table repair beyond what is required to create legitimate latest-first counterexamples.
- Trusted deterministic correction registry or trusted-rule validation.
- R1D idempotency, replacement atomicity, concurrency reconciliation, or final repair closure.
- WP04-03 API/OpenAPI/client work.
- WP04-04 Research exact Evidence references.
- Thesis, worker, MinIO write, parser/extractor, embedding, RAG, Agent runtime, Capability runtime, UI, or Sector Crowding work.

Do not edit:

- Frozen contracts.
- Existing acceptance reports.
- Verifier files under `/tmp`.
- Migrations or database schema.
- `main` history.

Do not commit, merge, rebase, reset, checkout, push, skip tests, xfail tests, weaken old tests, or change verifier contracts.

## F. Red-To-Green Requirement

Before implementing the fix, add focused failing tests in `tests/test_evidence_services.py` that prove the baseline defect against real PostgreSQL.

The initial RED must be an assertion failure or contract failure reaching the real service behavior, not a permission error, fixture setup failure, modified verifier, or synthetic mock-only proof. If the baseline unexpectedly passes the new focused tests, stop and report `BLOCKED_UNEXPECTED_GREEN_BASELINE` with the observed evidence.

Minimum real PostgreSQL counterexamples:

- Version 1 is `VERIFIED`, latest version is `DISPUTED`: current-valid returns unavailable and does not return version 1.
- Version 1 is `VERIFIED`, latest version is `INVALIDATED`: current-valid returns unavailable and exact read/history still expose version 1.
- Version 1 is `VERIFIED`, latest version is `RETRACTED`: current-valid returns unavailable and exact read/history still expose version 1.
- Latest version is `UNREVIEWED` after ordinary same-series correction: current-valid returns unavailable and does not return the prior `VERIFIED`.
- Latest version is `UNREVIEWED` after ordinary identity-changing replacement: the replacement series is not current-valid merely because the prior exact version was `VERIFIED`.
- Latest version is `PENDING_REVIEW`: current-valid returns unavailable.
- Latest version is `REJECTED`: current-valid returns unavailable.
- Latest version is `VERIFIED`: current-valid returns the latest `VERIFIED` version.
- Missing series still returns `None` without side effects.

Use public service commands to create these states wherever possible. If a status is not representable by an existing public command because that command itself belongs to a later R1C state-table repair, document the gap and keep the test construction inside the existing fixture/service boundary without weakening the contract.

## G. Implementation Rule

Implement the smallest service change that makes the focused tests pass while preserving R1A/R1B behavior.

Do not solve this by introducing broad role policy, hardcoding unrelated downstream systems, changing persisted statuses, mutating old rows, or using source-grade/F-grade Thesis eligibility as a substitute for current-valid lifecycle eligibility.

The likely repair is to narrow current-valid eligibility so `VERIFIED` is the only status accepted by this generic current-valid helper, while preserving the existing source lifecycle retraction check.

## H. Required Verification

Run through the normal permission mechanism. The database tests use the existing project fixture and local disposable PostgreSQL databases; do not change host, port, fixture route, Docker setup, proxy, or environment to bypass permissions.

Required focused red/green:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -k "r1c or current_valid or lifecycle" -rs
```

Required original verifier matrix:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_r1_wiring_20260915.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1b_reverify.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1a_verifier.py -rs
```

Required service/regression matrix:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
```

Required static/build checks:

```bash
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c-01-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1c-01-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
git diff --check
git status --short --branch --untracked-files=all
git rev-parse HEAD HEAD^
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py /tmp/test_wp04_02_r1b_r1_wiring_20260915.py /tmp/test_wp04_02_r1b_reverify.py /tmp/test_wp04_02_r1a_verifier.py
```

Expected Alembic head remains:

```text
000000000004 (head)
```

## I. Stop Conditions

Report `BLOCKED` and stop if:

- Candidate HEAD, parent, branch, cleanliness, or fixed baseline hashes differ.
- Normal permission mechanism refuses required local PostgreSQL verification.
- Database fixture setup fails before reaching business assertions.
- The focused RED cannot be produced on the unmodified baseline.
- Passing the slice requires changing frozen contracts, verifiers, migrations, schema, old reports, or a fourth business file.
- The repair requires implementing state-transition table, trusted registry, R1D, API/OpenAPI, Research typed links, or adjacent systems.
- Any temporary database residue is known after failure; report the specific residue and do not perform broad prefix cleanup.

## J. Deliverables

Final implementation report must include:

- `IMPLEMENTATION_COMPLETE` or `BLOCKED` only.
- Baseline HEAD/parent/status evidence.
- The focused RED result and the final GREEN result.
- Exact explanation of why current-valid now uses the true latest EvidenceVersion and does not return old eligible rows.
- Evidence that exact historical reads/history remain intact.
- Full command results from the required matrix.
- Final file list and final SHA-256 hashes.
- Statement that `errors.py`, verifiers, frozen contracts, migrations, and Git history were not modified.
- Clear remaining-task boundary: state-transition table, trusted correction registry, R1D, and full `TASK-WP04-02-REVERIFY` remain open.

## K. Copyable Development Prompt

```text
You are maintaining ThesisGuard.

Execute TASK-WP04-02-R1C-01.

Use the candidate worktree:
/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service

Candidate branch:
codex/wp04-02-evidence-domain-service

Required starting HEAD:
bdd70edc153b6ed5def65ed99c41f325df45f066

Required parent:
f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af

Read main AGENTS.md and:
docs/acceptance/TASK-WP04-02-R1C-01-task-contract.md
docs/acceptance/TASK-WP04-02-R1C-BASELINE-CONFIRM-R1-acceptance.md
docs/acceptance/TASK-WP04-02-R1C-BASELINE-CONFIRM-R1-task-contract.md
docs/acceptance/TASK-WP04-02-R1B-R2-INDEPENDENT-REVERIFY-acceptance.md
docs/acceptance/TASK-WP04-02-R1B-R2-REVERIFY-FEEDBACK-REVIEW-acceptance.md
docs/acceptance/TASK-WP04-02-R1-repair-contract.md
docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md

Only modify:
backend/evidence/services.py
tests/test_evidence_services.py

Do not modify errors.py, frozen contracts, old reports, verifiers, migrations, schema, main, or Git history. Do not commit, merge, rebase, reset, checkout, or push.

First confirm branch, HEAD, parent, clean status, and fixed hashes from the task contract. If any mismatch, report BLOCKED.

Implement only the latest-first lifecycle eligibility slice:
get_current_valid_evidence must read the latest EvidenceVersion first and return an eligible result only when the latest version is eligible for current-valid use. It must not return an older VERIFIED row when the latest version is UNREVIEWED, PENDING_REVIEW, DISPUTED, REJECTED, INVALIDATED, or RETRACTED. Exact historical reads and history listing must remain intact. Preserve all R1A/R1B behavior, immutable children, legal historical support replacement, and no-residue guarantees.

Use red-to-green development. Add focused real PostgreSQL tests proving that the unmodified baseline incorrectly treats latest UNREVIEWED/PENDING_REVIEW/DISPUTED as current-valid or otherwise fails latest-first eligibility. Cover latest VERIFIED, latest DISPUTED, latest INVALIDATED, latest RETRACTED, latest UNREVIEWED same-series correction, latest UNREVIEWED replacement, latest PENDING_REVIEW, latest REJECTED, missing series, and exact historical reads. If the unmodified baseline unexpectedly passes these tests, stop and report BLOCKED_UNEXPECTED_GREEN_BASELINE.

Run the full required verification matrix from the task contract through the normal permission mechanism: focused R1C tests, original R1B wiring verifier, R1B reverify, R1A verifier, full service tests, persistence/migration/research regressions, ruff, format check, mypy, compileall, Alembic heads, diff check, final status/HEAD/hash checks. Use the existing local temporary PostgreSQL fixture route only; do not change host/port, use Docker/proxy/workarounds, run arbitrary SQL, or perform broad DB cleanup.

Final result must be IMPLEMENTATION_COMPLETE or BLOCKED only. Include baseline evidence, red reproduction, green verification, exact current-valid timing/semantics evidence, command results, final file list/hashes, and the remaining boundary: state-transition table, trusted correction registry, R1D, and full TASK-WP04-02-REVERIFY remain open.
```
