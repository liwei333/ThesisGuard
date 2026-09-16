# TASK-WP04-02-R1C-05C-01-REBASELINE-DISPOSITION-CONTRACT-R1

Status: PROPOSED / NOT_DISPATCHED. This file is not user approval.

## A. Execution core

- Role: baseline/disposition contract compiler, not business executor or runtime verifier.
- Objective: record explicit user approval of the new exact baseline and retaining UNKNOWN databases; compile one unambiguous successor independent-verification contract.
- Why now: Phase A safely stopped; the old fixed identities and cleanup-before-tests prerequisite cannot be silently changed.
- Task type/size: DOCUMENTATION / SMALL, one verification-precondition closure.
- Required acceptance: L1_STATIC_REVIEWED. No runtime or DB acceptance claimed.
- Evidence matrix: Compact; successor verifier must use Full.

### Approval precondition

Locate an actual user message explicitly authorizing BOTH:

1. Adopt main `d3acc1c6f4a2e5ce1fe4b973d7855409c0db1da5` and candidate `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`, with the parents/scope/hashes below, after static equivalence checks. This is verification rebaseline only, not retroactive authorization of Git operations or acceptance of business behavior.
2. Preserve all 45 names in the Phase A exact-cleanup-plan as UNKNOWN, with no deletion, rename, connection termination, content modification or catalog marking. Compile a successor route permitting later independently dispatched tests in newly created disposable fixture DBs without first deleting those historical UNKNOWN databases. Historical residue remains unresolved and must remain disclosed.

The user must separately dispatch actual tests later. Approval of this docs-only task does not approve DB operations. Do not interpret this proposed file, an acceptance report or generic task dispatch as approval of those decisions. If actual approval is absent/partial/conflicting, stop without writing files: BLOCKED_POLICY_APPROVAL_REQUIRED.

### Read first

Main repository: `/Users/qianduoduo/Desktop/AI_app/ThesisGuard`.
Candidate: `/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service`.

Read AGENTS.md in both roots, and the following main-root files completely:

- `docs/acceptance/TASK-WP04-02-R1C-05C-01-PHASE-A-FEEDBACK-REVIEW-acceptance.md`.
- `docs/acceptance/TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-task-contract.md`.
- `docs/acceptance/TASK-WP04-02-R1C-05C-01-acceptance.md`.
- `docs/acceptance/TASK-WP04-02-R1C-05C-01-task-contract.md` and `TASK-WP04-02-R1C-05C-01-dispatch.md` in that directory.
- `docs/acceptance/TASK-WP04-02-R1C-05C-01-execution-report.md` and its artifact/command/protection manifests.
- `docs/WP04_EVIDENCE_CORRECTION_POLICY_ADDENDUM_2026-09-16.md` and `docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md`.
- Phase A independent report, exact cleanup plan, effective environment, evidence and before/after manifests in `docs/acceptance/TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-evidence`.

Inspect the original candidate PostgreSQL fixtures and seven protected verifier sources; do not execute them.

### Fixed proposed baseline

```text
main branch main
main HEAD d3acc1c6f4a2e5ce1fe4b973d7855409c0db1da5
main parent 438738c543e4cae3e805d31324b068c1cd5c7059
main tracked/index empty; existing untracked files retained
candidate branch codex/wp04-02-evidence-domain-service
candidate HEAD af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8
candidate parent 0cef44fd2ffd929b40e849e607af0bd4c44d14d2
candidate clean
candidate HEAD commit scope: services.py and tests/test_evidence_services.py only
3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec  backend/evidence/errors.py
7ce76b02928019347625048e7d0acb523d74168cd6bbbdf03184163ac277f959  backend/evidence/services.py
b5bfcdeb2db6753c71fd146b935dd26229daae0d73da5bda68af437db137b950  tests/test_evidence_services.py
```

### Top blocking AC

1. Actual explicit user approval is preserved with source/date/quote; the decision scope does not authorize cleanup, business policy expansion, tests or Git operations.
2. Exact identities, clean candidate and two-file commit scope match; committed blobs and working files are byte-equivalent to the 05C-01 final hashes. Main commit is docs-only. Existing evidence/verifiers/frozen contract are protected.
3. All 45 exact UNKNOWN names/OIDs are referenced from the existing plan and retained. Confirmed cleanup and proposed historical mutations remain empty. The original BLOCKED reports remain unchanged.
4. Successor verifier contract explicitly replaces only baseline identity and the historical-cleanup precondition, retains every original business AC/test/assertion/fixture, and differentiates historical unresolved residue from new-run no-residue proof.
5. Only the three specified documents are newly written. No DB connection, test, fixture, SQL, migration, container/dependency operation, candidate edit or Git write. Successor is PROPOSED / NOT_DISPATCHED; no 05C-01 PASS declared.

### Allowed new files (main root only)

- `docs/acceptance/TASK-WP04-02-R1C-05C-01-REBASELINE-DISPOSITION-R1-decision.md`.
- `docs/acceptance/TASK-WP04-02-R1C-05C-01-REBASELINE-DISPOSITION-CONTRACT-R1-execution-report.md`.
- `docs/acceptance/TASK-WP04-02-R1C-05C-01-REBASELINED-INDEPENDENT-REVERIFY-R1-task-contract.md`.

Use exclusive new paths; if any already exists, stop rather than overwrite. Do not change this task contract, canonical AGENTS/PRD/TAD, historical acceptance or fixtures.

### Successor verifier specification to compile, not execute

Required acceptance: L1_STATIC_REVIEWED, L2_BUILD_VERIFIED, L3_CONTRACT_VERIFIED, L4_DB_VERIFIED; Full matrix. One unchanged-candidate verification boundary; no new business repair or RED requested.

Require an exact effective-environment preflight before any CREATE, using recorded command-local PATH:

```text
PATH=/opt/miniconda3/bin:/opt/homebrew/bin:/opt/homebrew/opt/postgresql@16/bin:/usr/bin:/bin:/usr/sbin:/sbin
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service:/opt/homebrew/lib/python3.12/site-packages
python=/opt/homebrew/bin/python3.12
pytest=/opt/homebrew/bin/pytest
```

Check all three diagnostic variables absent without silently unsetting them; child `shutil.which('alembic')` resolves `/opt/miniconda3/bin/alembic`; heads is exactly `000000000004`. Bare pytest is forbidden. Record absolute tools, cwd, effective child environment and versions, not shell assumptions. No profile edits/installations or approval workarounds.

Only original disposable fixtures at `127.0.0.1:15432` may be used after separate test dispatch. For each test command require actual pre/post DB-name inventories, a run ID, exact new DB name/OID and node/run mapping, CREATE/teardown evidence, and preservation of the 45 historical names. Catalog set differences alone are insufficient run provenance if concurrent users exist. Specify a read-only observation method before running; if exact mapping cannot be captured without editing fixtures, overriding UUIDs/connections/cleanup, or changing assertions, stop and request a separate bounded instrumentation contract. Do not claim an observer has been implemented in this docs task.

No new-run residue or fixture setup/teardown errors may be ignored. On any such failure stop subsequent DB commands, preserve exact evidence and request name-specific direction; no broad retry/cleanup. Normal original fixture teardown applies only to its newly created DBs. Never drop or terminate connections in the 45 historical names or the four system/business databases.

Compile actual executable commands from the executor command manifest, preserving focused 05C-01, 05A/04A preservation, audit-tuple/replay verifier, fixed 58-scene oracle, five original verifiers, full service and persistence/migration/Research regressions; Ruff/format/mypy/compileall/heads and final protected hashes. No skip or replacement of tests; 41/11/87/4/58/70/378/35 are historical expected collection/results, not new execution proof. Preserve caller commit/fresh-session nine-table full equality, exact routing, children/history/audit and COMMITTED replay evidence. If fresh behavior fails, return FAIL for independent acceptance and issue a later repair, not repair in this verifier task.

A future PASS may close only the 05C-01 state-admission boundary at the new baseline with disclosed historical residue. It must not describe the whole database environment as residue-free or close R1C/WP04-02. 05C-02 requires that independent PASS and separate dispatch.

### Required verification for this docs-only task

Use read-only git rev-parse/status/diff-tree/diff --check, git show blobs, SHA-256 comparisons and manifest integrity/link/UTF-8/LF/whitespace checks. Check before/after repository status and existing file hashes; include untracked additions in scope verification. For new untracked documents use no-index whitespace checks with documented exit-code semantics. Do not run any DB command or pytest, even collection.

Stop on missing approval, identity/hash/scope drift, existing output paths, conflicting contract or unsafe/unverifiable proposed runtime plan. Output only IMPLEMENTATION_COMPLETE or BLOCKED, with the three artifact paths/hashes, actual static checks, approval provenance and deferred runtime boundary.

## B. Governance appendix

Use ai-task-governor and ai-task-prompt-architect. IMPLEMENTATION_COMPLETE is not acceptance. Use verification-before-completion for any static claim. Preserve immutable historical evidence; no production policy change beyond the existing approved addendum. Standard deferrals: 05C-02, remaining qualifications, R1D, full WP04-02 acceptance, Git integration, API/OpenAPI, Research/Thesis/Agent, trusted success rules, Capability Runtime and Sector Crowding.
