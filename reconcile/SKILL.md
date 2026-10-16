---
name: reconcile
description: "Close a session by reconciling three sources of truth (git, the tracker, the transcript's own claims) into a discrepancy table, acting only on confirmation, and ending with the next piece of work. Use when the user says close out, wrap up, end the session, or we are done, or when a session is ending with uncommitted work, unpushed branches, worktrees, stashes, or tickets whose state was changed in conversation. Not for mid-task status updates; those are a handoff."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Reconcile

A session ends when three records agree on what happened: **git** (branches, worktrees, commits, pushes, stashes), the **tracker** (issue and PR state, or the local ticket files), and the **transcript** (what was decided and claimed in this conversation). Each is read fresh from its own source, in that order, and every pair is compared. The unit of output is a **discrepancy**: two sources that disagree. Every line of the report is quoted from a command run in this session, and a claim in the transcript stays a claim until git or the tracker confirms it.

## 1. Snapshot git and the tracker

Run `scripts/snapshot.sh` from the repository root (`--help` in the header). It prints a `## git` block (`git status --porcelain`, `git branch -vv`, `git worktree list`, commits ahead of upstream per branch, `git stash list`) and a `## tracker` block (every local ticket under `.scratch/*/issues/` as `id | title | state | path`, plus `gh` issues and PRs for the current branch when `gh` is signed in). Paste both blocks, redacted. Where the tracker is something else, add its rows to the `## tracker` block by hand, each from a command's output. Exit code 1 means there is state to reconcile.

**Done when** both blocks are pasted and every tracker item this session touched has a row.

## 2. Extract the transcript's claims

List every statement in this conversation of the form "done", "committed", "pushed", "closed", "decided X", "will do Y next". Each becomes a line `<claim> | <where it should show up: git | tracker | file>`.

**Done when** the list is exhausted; a session that made no claims and whose snapshot exited 0 ends here with `nothing to reconcile`.

## 3. Reconcile

Compare every pair. A discrepancy is any of:

- A transcript claim with no matching evidence in git or the tracker (said "committed", `git status` shows changes; said "closed #12", tracker shows open).
- A git fact with no transcript or tracker counterpart (a branch, stash or worktree nothing mentions; commits ahead of upstream with no PR).
- A tracker state that git contradicts (a PR marked merged whose branch is still ahead; a ticket closed with no commit referencing it).
- A decision in the transcript recorded nowhere durable (no commit message, ticket comment, ADR or ledger line carries it).

Write each as one row: `<source A> says | <source B> says | proposed action`.

**Done when** every pair of sources has been compared and the table is complete, or reads `0 discrepancies`.

## 4. Confirm, then act

Show the table and wait. Act only on the rows the user confirms, one command per row, pasting each command's output beneath its row. If the user is away, act on nothing: the table is the deliverable.

**Done when** every confirmed row shows its output, and every unconfirmed row is marked `left as is`.

## 5. Point at the next session

End with one line naming the next piece of work and the skill to start it with, taken from the frontier the tracker shows (an open ticket whose blockers are closed) or from the one discrepancy the user chose to leave.

**Done when** the last line of the report is `next: <work> (<skill>)`.
