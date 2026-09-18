# Branch and Merge Workflow

This document defines the branch, development, and merge workflow for
ThesisGuard engineering tasks.  It applies to all task branches unless a
specific task contract overrides a clause.

## Core Principles

1. **Never develop on `main`.**  Business code, tests, verification scripts,
   task documents, acceptance reports, and evidence files are all developed on
   task branches.  `main` receives only integrated, reviewed, and confirmed
   deliverables.
2. **Complete stages, not individual tasks, are the unit of merge.**  A small
   task PASS does not justify merging its branch into `main`.  The relevant
   work package (WP) stage must be complete, independently verified, and
   confirmed by the user before a PR merges.
3. **Evidence belongs on the task branch.**  Acceptance reports, execution
   logs, and evidence directories are delivered on the task branch.  Do not
   commit acceptance materials to `main` directly.

## Branch Creation

```text
git fetch origin --prune
git branch <task-branch> origin/main
git worktree add ../<task-dir> <task-branch>
```

- Branch names follow `codex/<task-id>` convention.
- Verify the branch points at the expected `origin/main` commit.
- If a branch or worktree directory already exists, check ownership before
  proceeding.

## Development

- Develop and self-test on the task branch.
- Verify candidate/main baselines before any non-trivial operation.
- Keep the candidate branch untouched; never modify, rebase, or reset it.

## Independent Verification

- After self-test, a separate independent session verifies the deliverables.
- The independent verifier checks source, diff, test results, and evidence.
- The developer session does not self-sign the final PASS.

## Merge into `main`

Only when ALL of the following hold:

- The full WP stage is complete (not just the current task).
- Independent verification has issued a PASS.
- All evidence and acceptance materials are on the task branch.
- The user has explicitly confirmed.

```text
git checkout main
git merge --no-ff <task-branch>
git push origin main
```

## Failure Handling

- Developer gets one controlled fix attempt.
- If the fix fails, the task escalates to a more capable executor.
- On failure, report the exact state; do not fabricate evidence or
  self-certify PASS.
