# R2 Focused DB Reverify Feedback Review

## Decision and Scope

- Review ID: `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R2-FEEDBACK-REVIEW`
- Date: 2026-09-16
- Independent reviewer: Codex; skill: `ai-task-governor`
- Feedback-review result: **PASS**, limited to accepting the reported stop and selecting the next dispatch.
- Reviewed execution task: `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R2` remains **BLOCKED**.
- Required / achieved acceptance for this review: `L1_STATIC_REVIEWED`.
- Missing acceptance for the business verification: `L3_CONTRACT_VERIFIED`, `L4_DB_VERIFIED`.
- No collect-only, pytest, database connection, CREATE, DROP or other database operation was performed by this feedback reviewer. Database statements below are observations from the retained execution artifacts, not fresh database verification.

The stopped execution does not establish a business failure or a business PASS. Candidate repair is not justified by this feedback. The dispatcher must revise the execution precondition, rather than reset the shared checkout or silently amend the historical task.

## Independently Checked Evidence

| Check | Result | Evidence and limit |
|---|---|---|
| Main identity and drift contents | PASS | Current main is `554a87dce995c98d41021f6ae99c2173f4221c09`. `git diff --name-status 0dc2c5fd016af63f4836debf6ffa9d36b41a7703 554a87dce995c98d41021f6ae99c2173f4221c09` contains only AGENTS routing, zcode evaluation and documentation/acceptance/prompt artifacts. The AGENTS diff is confined to coding-agent evaluation/routing. No runtime source, tests, migrations, dependency/configuration files or frozen product rules changed in that interval. |
| Candidate identity and scope | PASS | Candidate branch `codex/wp04-02-evidence-domain-service`, HEAD `e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4`, parent `af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8`; clean worktree/index. Five fixed candidate SHA256 values match R2. |
| Stop evidence | PASS for the BLOCKED decision | Read R2 acceptance, before/after JSON, manifest and execution log. JSON evidence parses; retained artifacts consistently identify the baseline mismatch before collect/real pytest. Runner source control flow and its manifest SHA256 were checked. |
| New resource attempts | PASS for the reported stopped run | `resources.jsonl` is 0 bytes; after/manifest record zero collection and zero `create_sent`. No new-resource run took place in the retained evidence. An empty ledger alone is not universal proof that arbitrary unlogged DB operations never occurred. |
| Historical UNKNOWN preservation | Sufficient for this limited review | Retained before metadata and source inspection support preservation of the 45 historical UNKNOWN entries. This reviewer did not connect to or independently inventory the live databases. |
| Business tests and persistence semantics | NOT VERIFIED | All 41 focused scenarios remain outstanding. No fresh claim about transaction equality, admission, replay, routing, audit or release is accepted. |

The retained R2 runner hash is `1f06d6684ebd72bfd3610524e4cec9ed117816ace3f55f69b777323cd026b826`. The historical exact-plan hash is `635ba4aad0468c15b4360733c784d52f4430f03477a14ef8a271a1e32bada360`.

## Findings

1. **Execution blocker, not candidate defect:** stopping was consistent with the old exact-main-baseline contract. The candidate's bytes did not drift. The main change was unrelated documentation, so an exact shared-main HEAD lock caused avoidable dispatch churn. R3 will explicitly permit narrowly classified unrelated documentation changes, while protecting the candidate and relevant semantic inputs.
2. **Evidence qualification:** R2 `after.json` explicitly records the post-test catalog comparison as `NOT_RUN`; therefore no full before/after catalog equality is accepted. The runner's filtered catalog snapshot is not a complete cluster catalog. Its two summary log records and path-only artifact manifest suffice for understanding this stop, not for a future successful runtime acceptance.
3. **Successor runner requirements:** do not reuse the old helper unchanged or merely replace its HEAD constant. Validate relevant baseline before DB access; verify actual child tools; retain raw redacted command results; inspect the full catalog; independently enforce node coverage, attempt budget, ownership and release. Pytest exit 0 alone cannot satisfy all focused AC.
4. **Secret handling:** do not copy credential-bearing temporary helper source into public evidence. Preserve its hash and a redacted review representation if needed. New helper source must obtain credentials from existing local configuration without embedding or logging secrets.

## Next Dispatch

- Owner: **Codex**, independent DB verifier. Zcode's currently accepted restricted pure-logic/UI scope does not establish real PostgreSQL/fixture-lifecycle verification capability.
- Next task: `TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R3`.
- Same candidate and five byte pins; main anchor `554a87dce995c98d41021f6ae99c2173f4221c09`, with explicit semantic drift classification.
- Fresh run ID and empty ledger; at most 41 new CREATE attempts, one real focused invocation. R2 used zero attempts, but its run ID/ledger are never reused.
- Historical 45 UNKNOWN remain untouched. No source repair, old evidence edits, Git restoration/integration or shared-schema mutation.
- Focused PASS, if obtained, remains only the first slice of the original full 05C-01 matrix. It does not close 05C-01, R1C or WP-04-02 or authorize 05C-02/API.

## Persistence and Routing

Only this new review and the R3 prompt are added by the feedback reviewer; the incoming untracked R2 report/evidence are retained. AGENTS.md is not changed: a correct stop caused by dispatch-baseline drift supplies no new evidence for changing coding-agent capability or granting broader implementation privileges.

Sources: `docs/prompts/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R2.md`, its acceptance/evidence directory, fixed candidate files, the retained temporary runner, and independently inspected Git identity/status/diffs. Historical execution artifacts are preserved rather than retroactively relabeled.
