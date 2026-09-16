# TASK-WP04-02-R1C-05A — Initial VERIFIED Import Fail-Closed Admission

Status: READY_FOR_USER_DISPATCH. This contract authorizes only the bounded candidate repair below; it does not authorize Git integration or a positive trusted-import capability.

## A. Execution Core

- Task ID: `TASK-WP04-02-R1C-05A`.
- Objective: make every new no-predecessor direct `VERIFIED` Evidence import fail closed until a separately approved deterministic import rule and byte-bound semantic validator exist, while preserving ordinary creation, historical exact replay and all accepted lifecycle behavior.
- Why now: R1C-04A passed. The frozen contract allows initial direct `VERIFIED` only after source, locator, schema and semantic checks in one transaction, but the current public `create_evidence_series_version` accepts a caller-supplied `verification_status="VERIFIED"` plus audit tuple without an approved validator. Existing synthetic fixture hashes and labels do not prove that qualification.
- Role / Type / Size: EXECUTOR / REPAIR / MEDIUM. One production admission boundary plus transparent fixture separation is expected; at least three high-risk counterexamples are mandatory.
- Required acceptance: `L1_STATIC_REVIEWED`, `L2_BUILD_VERIFIED`, `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- Evidence matrix: Full, because this affects eligibility, DB writes, idempotency, audit and historical replay.

### Fixed baseline

```text
main: /Users/qianduoduo/Desktop/AI_app/ThesisGuard
main HEAD: 438738c543e4cae3e805d31324b068c1cd5c7059
main parent: 7d3734bc8346c16f9bbf7f7d9806309949c996de
candidate: /Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service
branch: codex/wp04-02-evidence-domain-service
candidate HEAD: 0cef44fd2ffd929b40e849e607af0bd4c44d14d2
candidate parent: bdd70edc153b6ed5def65ed99c41f325df45f066
candidate status at dispatch:
 M backend/evidence/services.py
 M tests/test_evidence_services.py
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
94bb12823690a07ef323323cffacbd756081f23b2edd7de04fc25884e5e612a6  backend/evidence/services.py
3c7da5f9405990ca047957b46a25ff0d8cde736152ec7d472c5535b2ed0d67d0  tests/test_evidence_services.py
```

The two modified candidate files are the accepted R1C-04A baseline, not unexplained drift. Verify exact branch/HEAD/status/hashes before editing. Read main `AGENTS.md`, this contract, `TASK-WP04-02-R1C-04A-acceptance.md`, R1C-03A oracle acceptance, R1C-03B rule draft/acceptance, the original R1 repair program, frozen Evidence contract sections 12, 13, 21 and 22, and actual candidate service/models/tests/fixtures. Any baseline mismatch, fixed verifier mismatch or main tracked/index change is `BLOCKED`.

### Top Blocking AC

1. Before service edits, add focused real-PostgreSQL tests and prove genuine RED: a new no-predecessor call with `verification_status="VERIFIED"`, complete `INITIAL_VERIFICATION` tuple and structurally valid synthetic source/locator currently persists an eligible version even though no approved deterministic initial-import validator exists. The RED must be a failed fail-closed assertion, not a permission/setup/cleanup failure.
2. On GREEN, every new no-predecessor direct `VERIFIED` request is rejected by a stable existing domain validation error before series/version/children/idempotency/audit writes. Use explicit details such as `validation_path=verification_status` and `reason=unqualified_initial_verified_import`. Do not silently downgrade an initial request to UNREVIEWED, and do not add a caller-controlled boolean/string that pretends semantic proof.
3. Preserve exact read-only replay of a historically committed initial `VERIFIED` response with the same operation/key/hash. A different payload or new key must not borrow that history. Place the new admission check so a legitimate committed replay remains read-only but a new request leaves no durable residue or key consumption.
4. Ordinary no-predecessor `UNREVIEWED` creation, ordinary correction/review/verify, R1C-04A display-text rules, replacement routing, latest-first eligibility, exact history, audit and immutable children remain unchanged. Fixed R1 oracle and five original verifiers must remain byte-identical and green.
5. Existing tests that need a version-1 historical `VERIFIED` starting point must not keep using the now-forbidden public creation path. Separate fixture state from production behavior transparently: a disclosed constraint-legal append-only historical seed is allowed only in tests, with no production branch, monkeypatch, fake validator or claim that the seed proves initial-import capability. Preserve external fixture names/signatures where fixed verifiers import them. Only the two candidate files may change.

### In scope

- `backend/evidence/services.py`: one fail-closed new-request admission check at the correct replay/write boundary.
- `tests/test_evidence_services.py`: focused `r1c05a` RED/GREEN, no-residue/history/replay tests, and the minimum transparent fixture adjustment required to keep accepted lifecycle tests modeling historical state rather than exercising a forbidden production command.

### Out of scope

- No positive initial-import registry, rule ID, validator, parser/MinIO/object-byte fetch, semantic extraction, new schema/column/model/repository/migration/API or frozen-contract change.
- No positive trusted correction rule, title rule activation, ordinary correction policy expansion, R1D hash/replay/concurrency repair, WP04-03/04, Research/Thesis/Agent/Sector work.
- No edits to `errors.py`, models, repositories, old verifiers, oracle, prior reports/manifests/logs, main tracked files or Git history.

### Required behavior and examples

- Given a lawful source/version/locator and no predecessor, when a new caller requests initial `VERIFIED` with a complete-looking audit tuple but no approved deterministic import validator exists, then reject with `EVIDENCE_VALIDATION_ERROR`, explicit path/reason, caller commit succeeds, and a fresh session proves all relevant durable rows unchanged.
- Given the same request uses `UNREVIEWED` with the initial all-null lifecycle tuple, then create version 1 normally and preserve R1C-04A text bytes.
- Given a disclosed historical initial-`VERIFIED` row and committed matching idempotency record already exist, when the exact request is replayed, then return the same exact ID with no writes. With a changed payload or new key, reject; do not create a second row or consume a key.
- Given lifecycle/current-valid tests need a `VERIFIED` version 1, fixture setup may seed an append-only constraint-valid historical row and children directly through ORM. The helper must clearly state that this is historical test setup, must not be callable from production code, and must not be presented as semantic import verification.
- Given an initial request asks for `VERIFIED` with malformed/partial audit data, the existing more-specific lifecycle validation may reject first. The task must still prove a fully formed but semantically unqualified request reaches the new fail-closed reason.

### High-risk counterexamples

1. A caller supplies plausible SHA strings, parser names, source grade S and PAGE locator; these declarations still do not constitute byte-bound semantic verification and must not make a new direct import eligible.
2. A historical committed response is replayed with the same key but changed display text/source/locator/status tuple; it must not return the old response or bypass the new denial.
3. Test fixtures remain green by secretly monkeypatching production admission or adding a test-only service branch; this is forbidden even if all assertions pass.
4. Rejection occurs after a series or child row is attached/flushed, leaving residue after caller commit; fresh-session all-column equality must catch it.
5. The new check accidentally rejects legal ordinary UNREVIEWED creation or status versions that copy an existing VERIFIED body's text; accepted suites must catch this regression.

### Implementation strategy

1. Capture baseline scope/hashes and fixed verifier/oracle hashes.
2. Add only focused `r1c05a` tests first. Run unchanged service code and retain genuine RED.
3. Implement the smallest fail-closed check after exact committed replay handling but before construction/attachment/flush/idempotency/audit for a new no-predecessor initial `VERIFIED` request.
4. Adjust only the shared test fixture path required by fixed lifecycle/oracle tests. Prefer an explicit historical seed helper; preserve old imported helper signature and document why it is not production evidence. Do not relax any lifecycle assertions.
5. Run focused and full regression matrices at final hashes. Do not commit inside services or use rollback as no-residue proof.

### Required verification

Use the existing approved `127.0.0.1:15432` disposable PostgreSQL fixture and candidate-first `PYTHONPATH`. Do not set `TG_TEST_ADMIN_DATABASE_URL`, `TG_R1C_REPLAY_BASELINE` or `TG_R1C02_REPLAY_PRIOR`; do not change host/port, start a replacement DB, run broad cleanup or install dependencies.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1c05a -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -k r1c04a -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/verifiers/test_wp04_02_r1c03a_boundary_oracle_r1_20260916.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q /tmp/test_wp04_02_r1c_02_independent_20260915.py /tmp/test_wp04_02_r1c_01_independent_20260915.py /tmp/test_wp04_02_r1b_r1_wiring_20260915.py /tmp/test_wp04_02_r1b_reverify.py /tmp/test_wp04_02_r1a_verifier.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_services.py -rs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" pytest -p no:cacheprovider -q tests/test_evidence_persistence.py tests/test_migrations.py tests/test_evidence_migrations.py tests/test_research_api.py tests/test_research_persistence.py -rs
ruff check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
ruff format --check --no-cache backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c05a-mypy backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
PYTHONPYCACHEPREFIX=/tmp/tg-r1c05a-pycache python -m compileall -q backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
alembic -c migrations/alembic.ini heads
git diff --check
git status --short --branch --untracked-files=all
git rev-parse HEAD HEAD^
shasum -a 256 backend/evidence/errors.py backend/evidence/services.py tests/test_evidence_services.py
```

For every rejection, perform lawful setup and commit before the baseline; after the domain error, prove no pending ORM mutation, let the caller commit, then compare all rows/all columns in a distinct fresh session for the nine Evidence/source/idempotency/audit tables and any corroboration rows used. Exact replay must be tested after a real commit. Retain actual argv/cwd/environment/start/end/exit/full-log hashes and final file/verifier hashes.

### Stop conditions

Stop and report `BLOCKED` if:

- baseline, candidate hashes, fixed verifier/oracle hashes or main tracked/index state differ;
- unchanged service does not exhibit the expected fail-open RED;
- preserving fixed accepted lifecycle/oracle behavior would require editing old verifiers, weakening assertions, a production test-only branch, or an invented semantic validator;
- normal disposable PostgreSQL permission/runtime/fixture is unavailable or cleanup fails;
- the repair requires schema/API/contract/R1D changes or any file outside the two authorized candidate files.

### Expected evidence and final response

Report only `IMPLEMENTATION_COMPLETE` or `BLOCKED`; the executor cannot self-approve. Include baseline and final hashes/status, genuine RED, exact implementation location/order, new-request rejection details, historical replay proof, fixture-separation explanation, caller-commit/fresh-session no-residue proof, full command results and remaining boundaries. Explicitly state that positive initial deterministic import and positive trusted correction remain unimplemented and require separately approved byte-bound semantic evidence.

## B. Governance Appendix

Apply `systematic-debugging`, `test-driven-development` and `verification-before-completion`; obey `ai-task-governor` core invariants and anti-drift rules. Do not reinterpret this default-deny safety repair as permission to weaken the frozen contract or declare R1C/WP04-02 complete.

Standard deferrals remain: R1D idempotency/atomicity/concurrency, final `TASK-WP04-02-REVERIFY`, WP04-03 API/OpenAPI, WP04-04 Research exact references, worker/MinIO/parser/embedding/RAG/Thesis/Agent, Capability Runtime and Sector Crowding. No commit/merge/rebase/reset/checkout/push or main mutation is authorized.

